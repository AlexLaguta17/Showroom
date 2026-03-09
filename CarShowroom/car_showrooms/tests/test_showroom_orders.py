"""Tests for showroom order API access control."""

import pytest
from django.urls import reverse
from rest_framework import status

from services.choices import UserType
from users.tests.factories import UserFactory

pytest_plugins = [
    "users.tests.fixtures",
    "car_showrooms.tests.fixtures",
    "dealers.tests.fixtures",
]


def order_list_url(showroom_pk):
    """Return the URL for listing orders of a showroom."""
    return reverse("showroom-order-list", kwargs={"showroom_pk": showroom_pk})


def order_detail_url(showroom_pk, pk):
    """Return the URL for a single showroom order detail."""
    return reverse("showroom-order-detail", kwargs={"showroom_pk": showroom_pk, "pk": pk})


def order_create_url(showroom_pk):
    """Return the URL for creating an order with a showroom."""
    return reverse("showroom-order-create", kwargs={"showroom_pk": showroom_pk})


@pytest.mark.django_db
class TestShowroomOrderAccess:
    """Tests for showroom order access rules.

    Access rules:
    - List/Detail: showroom owner sees all orders for their showroom;
                   customer sees only their own orders; providers are blocked entirely.
    - Create: only customers (type=CUSTOMER) can create orders.
    """

    @pytest.mark.parametrize(
        "auth_role_client, is_showroom_owner, expected_status",
        [
            ("showroom_user", True, status.HTTP_200_OK),
            ("user", False, status.HTTP_200_OK),
            ("provider_user", False, status.HTTP_403_FORBIDDEN),
            (None, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_list_permissions(self, auth_role_client, is_showroom_owner, showroom, expected_status):
        """Allow showroom owners and customers to list orders; block providers and anonymous users."""
        force_user = getattr(auth_role_client.handler, "_force_user", None)
        my_showroom = showroom(owner_user=force_user) if is_showroom_owner else showroom()

        response = auth_role_client.get(order_list_url(my_showroom.id))

        assert response.status_code == expected_status

    def test_showroom_owner(self, client, showroom, showroom_order, showroom_user):
        """Verify that a showroom owner cannot read another showroom's orders."""
        showroom_b_owner = UserFactory(type=UserType.SHOWROOM)
        showroom_a = showroom(owner_user=showroom_user)
        showroom_b = showroom(owner_user=showroom_b_owner)

        showroom_order(showroom=showroom_a)
        showroom_order(showroom=showroom_b)

        client.force_authenticate(user=showroom_user)

        response_b = client.get(order_list_url(showroom_b.id))
        assert response_b.status_code == status.HTTP_200_OK
        assert len(response_b.data) == 0

        response_a = client.get(order_list_url(showroom_a.id))
        assert response_a.status_code == status.HTTP_200_OK
        assert len(response_a.data) == 1

    def test_customer_sees_only_own_orders(self, client, showroom, showroom_order):
        """Verify that a customer only sees their own orders, not other customers' orders."""
        customer_a = UserFactory(type=UserType.CUSTOMER)
        customer_b = UserFactory(type=UserType.CUSTOMER)
        my_showroom = showroom()

        order_a = showroom_order(showroom=my_showroom, car_buyer=customer_a)
        showroom_order(showroom=my_showroom, car_buyer=customer_b)

        client.force_authenticate(user=customer_a)
        response = client.get(order_list_url(my_showroom.id))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == order_a.id

    @pytest.mark.parametrize(
        "auth_role_client, is_showroom_owner, is_customer_buyer, expected_status",
        [
            ("showroom_user", True, False, status.HTTP_200_OK),
            ("showroom_user", False, False, status.HTTP_404_NOT_FOUND),
            ("user", False, True, status.HTTP_200_OK),
            ("user", False, False, status.HTTP_404_NOT_FOUND),
            ("provider_user", False, False, status.HTTP_403_FORBIDDEN),
            (None, False, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_detail_permissions(
        self, auth_role_client, is_showroom_owner, is_customer_buyer, showroom, showroom_order, expected_status
    ):
        """Allow showroom owners and order buyers to access detail; block providers and anonymous."""
        force_user = getattr(auth_role_client.handler, "_force_user", None)
        order_showroom = showroom(owner_user=force_user) if is_showroom_owner else showroom()
        order = (
            showroom_order(showroom=order_showroom, car_buyer=force_user)
            if is_customer_buyer
            else showroom_order(showroom=order_showroom)
        )

        response = auth_role_client.get(order_detail_url(order_showroom.id, order.id))

        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "auth_role_client, needs_showroom_car, expected_status",
        [
            ("user", True, status.HTTP_201_CREATED),
            ("showroom_user", False, status.HTTP_403_FORBIDDEN),
            ("provider_user", False, status.HTTP_403_FORBIDDEN),
            (None, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_create_permissions(self, auth_role_client, needs_showroom_car, showroom, showroom_car, expected_status):
        """Allow only customers to create showroom orders; block all other roles."""
        my_showroom = showroom()
        payload = {}
        if needs_showroom_car:
            my_car = showroom_car(showroom=my_showroom)
            payload = {"car": my_car.id}

        response = auth_role_client.post(order_create_url(my_showroom.id), payload)

        assert response.status_code == expected_status

    def test_create_sets_fields(self, client, showroom, showroom_car, user):
        """Verify that car_buyer and showroom are set automatically on order creation."""
        from car_showrooms.models import CarShowroomOrder

        my_showroom = showroom()
        my_car = showroom_car(showroom=my_showroom)

        client.force_authenticate(user=user)
        response = client.post(order_create_url(my_showroom.id), {"car": my_car.id})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["car_buyer"] == user.id

        order = CarShowroomOrder.objects.get(id=response.data["id"])
        assert order.showroom_id == my_showroom.id
        assert order.car_buyer_id == user.id

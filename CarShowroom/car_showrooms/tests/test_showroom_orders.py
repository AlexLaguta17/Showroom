"""Tests for showroom order API access control."""

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from users.tests.factories import UserFactory
from services.choices import UserType, OrderStatus
from car_showrooms.tests.factories import CarShowroomOrderFactory

pytest_plugins = [
    "users.tests.fixtures",
    "car_showrooms.tests.fixtures",
    "dealers.tests.fixtures",
]


def order_list_url(showroom_pk):
    """Return the URL for listing orders of a showroom."""
    return reverse("showroom-order-list-create", kwargs={"showroom_pk": showroom_pk})


def order_detail_url(showroom_pk, pk):
    """Return the URL for a single showroom order detail."""
    return reverse("showroom-order-detail", kwargs={"showroom_pk": showroom_pk, "pk": pk})


def order_create_url(showroom_pk):
    """Return the URL for creating an order with a showroom."""
    return reverse("showroom-order-list-create", kwargs={"showroom_pk": showroom_pk})


def order_confirm_url(showroom_pk, pk):
    """Return the URL for confirming a showroom order."""
    return reverse("showroom-order-confirm", kwargs={"showroom_pk": showroom_pk, "pk": pk})


def order_reject_url(showroom_pk, pk):
    """Return the URL for rejecting a showroom order."""
    return reverse("showroom-order-reject", kwargs={"showroom_pk": showroom_pk, "pk": pk})


def order_cancel_url(showroom_pk, pk):
    """Return the URL for cancelling a showroom order."""
    return reverse("showroom-order-cancel", kwargs={"showroom_pk": showroom_pk, "pk": pk})


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


@pytest.mark.django_db
class TestShowroomOrderActions:
    """Tests for showroom order action endpoints: confirm, reject, cancel.

    Access rules:
    - confirm/reject: only the showroom owner (SHOWROOM user who owns the showroom in the URL).
    - cancel: only the customer who placed the order (the car_buyer).
    All actions require PENDING status.
    """

    @pytest.mark.parametrize("get_action_url", [order_confirm_url, order_reject_url])
    @pytest.mark.parametrize(
        "auth_role_client, is_showroom_owner, expected_status",
        [
            ("showroom_user", True, status.HTTP_200_OK),
            ("showroom_user", False, status.HTTP_403_FORBIDDEN),
            ("user", False, status.HTTP_403_FORBIDDEN),
            ("provider_user", False, status.HTTP_403_FORBIDDEN),
            (None, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_confirm_reject_permissions(
        self,
        auth_role_client,
        is_showroom_owner,
        get_action_url,
        showroom,
        showroom_car,
        showroom_order,
        expected_status,
    ):
        """Allow only the showroom owner to confirm or reject orders; block all others."""
        force_user = getattr(auth_role_client.handler, "_force_user", None)
        my_showroom = showroom(owner_user=force_user) if is_showroom_owner and force_user else showroom()
        my_car = showroom_car(showroom=my_showroom, car_quantity=5)
        buyer = UserFactory(type=UserType.CUSTOMER, balance=Decimal("50000.00"))
        order = showroom_order(showroom=my_showroom, car=my_car, car_buyer=buyer, price=Decimal("100.00"))

        response = auth_role_client.post(get_action_url(my_showroom.id, order.id))
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "auth_role_client, is_car_buyer, expected_status",
        [
            ("user", True, status.HTTP_200_OK),
            ("user", False, status.HTTP_404_NOT_FOUND),
            ("showroom_user", False, status.HTTP_403_FORBIDDEN),
            ("provider_user", False, status.HTTP_403_FORBIDDEN),
            (None, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_cancel_permissions(
        self,
        auth_role_client,
        is_car_buyer,
        showroom,
        showroom_car,
        showroom_order,
        expected_status,
    ):
        """Allow only the order's car buyer to cancel; block other customers (404) and other roles."""
        force_user = getattr(auth_role_client.handler, "_force_user", None)
        my_showroom = showroom()
        my_car = showroom_car(showroom=my_showroom)
        order = (
            showroom_order(showroom=my_showroom, car=my_car, car_buyer=force_user)
            if is_car_buyer and force_user
            else showroom_order(showroom=my_showroom, car=my_car)
        )

        response = auth_role_client.post(order_cancel_url(my_showroom.id, order.id))
        assert response.status_code == expected_status

    def test_confirm_transfers_balance(self, client, showroom, showroom_car, showroom_order, showroom_user):
        """Confirm deducts customer balance, credits showroom owner, decrements car_quantity, sets COMPLETED."""
        order_price = Decimal("30000.00")
        customer = UserFactory(type=UserType.CUSTOMER, balance=Decimal("50000.00"))
        my_showroom = showroom(owner_user=showroom_user)
        my_car = showroom_car(showroom=my_showroom, car_quantity=5, price=order_price)
        order = showroom_order(showroom=my_showroom, car=my_car, car_buyer=customer, price=order_price)

        initial_owner_balance = showroom_user.balance
        client.force_authenticate(user=showroom_user)
        response = client.post(order_confirm_url(my_showroom.id, order.id))

        assert response.status_code == status.HTTP_200_OK

        customer.refresh_from_db()
        showroom_user.refresh_from_db()
        my_car.refresh_from_db()
        order.refresh_from_db()

        assert customer.balance == Decimal("50000.00") - order_price
        assert showroom_user.balance == initial_owner_balance + order_price
        assert my_car.car_quantity == 4
        assert order.status == OrderStatus.COMPLETED

    def test_confirm_insufficient_balance(self, client, showroom, showroom_car, showroom_order, showroom_user):
        """Return 400 when the customer's balance is less than the order price."""
        order_price = Decimal("30000.00")
        customer = UserFactory(type=UserType.CUSTOMER, balance=Decimal("0.00"))
        my_showroom = showroom(owner_user=showroom_user)
        my_car = showroom_car(showroom=my_showroom, car_quantity=5, price=order_price)
        order = showroom_order(showroom=my_showroom, car=my_car, car_buyer=customer, price=order_price)

        client.force_authenticate(user=showroom_user)
        response = client.post(order_confirm_url(my_showroom.id, order.id))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_out_of_stock(self, client, showroom, showroom_car, showroom_order, showroom_user):
        """Return 400 when the showroom car has no stock at confirm time."""
        order_price = Decimal("30000.00")
        customer = UserFactory(type=UserType.CUSTOMER, balance=Decimal("50000.00"))
        my_showroom = showroom(owner_user=showroom_user)
        my_car = showroom_car(showroom=my_showroom, car_quantity=1, price=order_price)
        order = showroom_order(showroom=my_showroom, car=my_car, car_buyer=customer, price=order_price)

        my_car.car_quantity = 0
        my_car.save()

        client.force_authenticate(user=showroom_user)
        response = client.post(order_confirm_url(my_showroom.id, order.id))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reject_sets_status(self, client, showroom, showroom_car, showroom_order, showroom_user):
        """Verify that rejecting an order sets its status to REJECTED."""
        my_showroom = showroom(owner_user=showroom_user)
        my_car = showroom_car(showroom=my_showroom)
        order = showroom_order(showroom=my_showroom, car=my_car)

        client.force_authenticate(user=showroom_user)
        response = client.post(order_reject_url(my_showroom.id, order.id))

        assert response.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.status == OrderStatus.REJECTED

    def test_cancel_sets_status(self, client, showroom, showroom_car, showroom_order, user):
        """Verify that cancelling an order sets its status to CANCELLED."""
        my_showroom = showroom()
        my_car = showroom_car(showroom=my_showroom)
        order = showroom_order(showroom=my_showroom, car=my_car, car_buyer=user)

        client.force_authenticate(user=user)
        response = client.post(order_cancel_url(my_showroom.id, order.id))

        assert response.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED

    @pytest.mark.parametrize(
        "initial_order_status", [OrderStatus.COMPLETED, OrderStatus.REJECTED, OrderStatus.CANCELLED]
    )
    @pytest.mark.parametrize(
        "get_action_url, user_fixture",
        [
            (order_confirm_url, "showroom_user"),
            (order_reject_url, "showroom_user"),
            (order_cancel_url, "user"),
        ],
    )
    def test_action_requires_pending_status(
        self,
        client,
        get_action_url,
        user_fixture,
        initial_order_status,
        showroom,
        showroom_car,
        showroom_order,
        request,
    ):
        """Reject confirm/reject/cancel actions on non-PENDING orders."""
        auth_user = request.getfixturevalue(user_fixture)

        if user_fixture == "showroom_user":
            my_showroom = showroom(owner_user=auth_user)
            order_buyer = UserFactory(type=UserType.CUSTOMER)
        else:
            my_showroom = showroom()
            order_buyer = auth_user

        my_car = showroom_car(showroom=my_showroom)
        order = CarShowroomOrderFactory(
            showroom=my_showroom, car=my_car, car_buyer=order_buyer, status=initial_order_status
        )

        client.force_authenticate(user=auth_user)
        response = client.post(get_action_url(my_showroom.id, order.id))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

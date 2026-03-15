"""Tests for provider order API permissions and business logic."""

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from users.tests.factories import UserFactory
from services.choices import UserType, OrderStatus

pytest_plugins = [
    "users.tests.fixtures",
    "car_showrooms.tests.fixtures",
    "dealers.tests.fixtures",
]


def order_list_url(provider_pk):
    """Return the URL for listing orders of a provider."""
    return reverse("provider-order-list-create", kwargs={"provider_pk": provider_pk})


def order_detail_url(provider_pk, pk):
    """Return the URL for a single provider order detail."""
    return reverse("provider-order-detail", kwargs={"provider_pk": provider_pk, "pk": pk})


def order_create_url(provider_pk):
    """Return the URL for creating an order with a provider."""
    return reverse("provider-order-list-create", kwargs={"provider_pk": provider_pk})


def order_confirm_url(provider_pk, pk):
    """Return the URL for confirming a provider order."""
    return reverse("provider-order-confirm", kwargs={"provider_pk": provider_pk, "pk": pk})


def order_reject_url(provider_pk, pk):
    """Return the URL for rejecting a provider order."""
    return reverse("provider-order-reject", kwargs={"provider_pk": provider_pk, "pk": pk})


def order_cancel_url(provider_pk, pk):
    """Return the URL for cancelling a provider order."""
    return reverse("provider-order-cancel", kwargs={"provider_pk": provider_pk, "pk": pk})


@pytest.mark.django_db
class TestProviderOrder:
    """Tests for provider order access rules and business logic.

    Access rules:
    - Create: only showroom owners (type=SHOWROOM with an associated CarShowroom row)
    - List/Detail: provider owner sees all orders addressed to them;
                   showroom sees only its own orders; customers are blocked entirely.
    """

    @pytest.mark.parametrize(
        "auth_role_client, needs_showroom, expected_status",
        [
            ("showroom_user", True, status.HTTP_201_CREATED),
            ("provider_user", False, status.HTTP_403_FORBIDDEN),
            ("user", False, status.HTTP_403_FORBIDDEN),
            (None, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_create_permissions(
        self,
        auth_role_client,
        needs_showroom,
        showroom,
        provider,
        provider_car,
        expected_status,
    ):
        """Allow only showroom owners to create orders; block providers, customers, and anonymous."""
        my_provider = provider()
        my_car = provider_car(provider=my_provider, car_quantity=10)

        force_user = getattr(auth_role_client.handler, "_force_user", None)
        if needs_showroom and force_user:
            showroom(owner_user=force_user)

        response = auth_role_client.post(order_create_url(my_provider.id), {"car": my_car.id, "car_quantity": 1})
        assert response.status_code == expected_status

    def test_create_sets_provider_showroom_and_price(self, client, provider, showroom, provider_car, showroom_user):
        """Verify that provider, showroom, and total_price are set automatically on creation."""
        my_provider = provider()
        my_showroom = showroom(owner_user=showroom_user)
        my_car = provider_car(provider=my_provider, car_quantity=10, price=Decimal("30000.00"))

        client.force_authenticate(user=showroom_user)
        response = client.post(order_create_url(my_provider.id), {"car": my_car.id, "car_quantity": 2})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["provider"] == my_provider.id
        assert response.data["showroom"] == my_showroom.id
        assert Decimal(response.data["total_price"]) == Decimal("60000.00")

    @pytest.mark.parametrize(
        "quantity_in_stock, quantity_ordered, wrong_provider",
        [
            (10, 1, True),
            (3, 10, False),
        ],
    )
    def test_create_rejects_invalid_order(
        self,
        client,
        provider,
        showroom,
        provider_car,
        showroom_user,
        quantity_in_stock,
        quantity_ordered,
        wrong_provider,
    ):
        """Reject orders where the car belongs to a different provider or stock is insufficient."""
        provider_a = provider()
        showroom(owner_user=showroom_user)
        car_provider = provider() if wrong_provider else provider_a
        my_car = provider_car(provider=car_provider, car_quantity=quantity_in_stock)

        client.force_authenticate(user=showroom_user)
        response = client.post(
            order_create_url(provider_a.id),
            {"car": my_car.id, "car_quantity": quantity_ordered},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "auth_role_client, is_provider_owner, needs_showroom, expected_status",
        [
            ("provider_user", True, False, status.HTTP_200_OK),
            ("provider_user", False, False, status.HTTP_403_FORBIDDEN),
            ("showroom_user", False, True, status.HTTP_200_OK),
            ("showroom_user", False, False, status.HTTP_403_FORBIDDEN),
            ("user", False, False, status.HTTP_403_FORBIDDEN),
            (None, False, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_list_permissions(
        self,
        auth_role_client,
        is_provider_owner,
        needs_showroom,
        provider,
        showroom,
        expected_status,
    ):
        """Allow provider owners and their showroom clients to list orders; block others."""
        force_user = getattr(auth_role_client.handler, "_force_user", None)
        my_provider = provider(owner_user=force_user) if is_provider_owner else provider()

        if needs_showroom and force_user:
            showroom(owner_user=force_user)

        response = auth_role_client.get(order_list_url(my_provider.id))
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "auth_role_client, sees_both",
        [
            ("showroom_user", False),
            ("provider_user", True),
        ],
        indirect=["auth_role_client"],
    )
    def test_list_queryset_isolation(
        self,
        auth_role_client,
        provider,
        showroom,
        showroom_user,
        provider_user,
        provider_order,
        sees_both,
    ):
        """Verify that showrooms see only their own orders while providers see all."""
        my_provider = provider(owner_user=provider_user)
        showroom_b_user = UserFactory(type=UserType.SHOWROOM)

        showroom_a = showroom(owner_user=showroom_user)
        showroom_b = showroom(owner_user=showroom_b_user)

        order_a = provider_order(provider=my_provider, showroom=showroom_a)
        order_b = provider_order(provider=my_provider, showroom=showroom_b)

        response = auth_role_client.get(order_list_url(my_provider.id))

        assert response.status_code == status.HTTP_200_OK
        returned_ids = {o["id"] for o in response.data}
        assert order_a.id in returned_ids
        assert (order_b.id in returned_ids) == sees_both

    @pytest.mark.parametrize(
        "auth_role_client, is_provider_owner, needs_showroom, is_order_owner, expected_status",
        [
            ("provider_user", True, False, False, status.HTTP_200_OK),
            ("showroom_user", False, True, True, status.HTTP_200_OK),
            ("showroom_user", False, True, False, status.HTTP_404_NOT_FOUND),
            ("user", False, False, False, status.HTTP_403_FORBIDDEN),
            (None, False, False, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_detail_permissions(
        self,
        auth_role_client,
        is_provider_owner,
        needs_showroom,
        is_order_owner,
        provider,
        showroom,
        provider_order,
        expected_status,
    ):
        """Allow provider owners and order-owning showrooms to see the detail; block others."""
        force_user = getattr(auth_role_client.handler, "_force_user", None)
        my_provider = provider(owner_user=force_user) if is_provider_owner else provider()

        auth_showroom = showroom(owner_user=force_user) if needs_showroom and force_user else None
        order_showroom = auth_showroom if is_order_owner and auth_showroom else showroom()

        order = provider_order(provider=my_provider, showroom=order_showroom)
        response = auth_role_client.get(order_detail_url(my_provider.id, order.id))
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "auth_role_client, needs_showroom, is_order_owner, expected_status",
        [
            ("showroom_user", True, True, status.HTTP_200_OK),
            ("showroom_user", True, False, status.HTTP_404_NOT_FOUND),
            ("provider_user", False, False, status.HTTP_403_FORBIDDEN),
            ("user", False, False, status.HTTP_403_FORBIDDEN),
            (None, False, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_update_permissions(
        self,
        auth_role_client,
        needs_showroom,
        is_order_owner,
        provider,
        showroom,
        provider_car,
        provider_order,
        expected_status,
    ):
        """Allow only the order-owning showroom to update the order."""
        my_provider = provider()
        my_car = provider_car(provider=my_provider, car_quantity=10)

        force_user = getattr(auth_role_client.handler, "_force_user", None)
        auth_showroom = showroom(owner_user=force_user) if needs_showroom and force_user else None
        order_showroom = auth_showroom if is_order_owner and auth_showroom else showroom()

        order = provider_order(provider=my_provider, showroom=order_showroom, car=my_car)

        response = auth_role_client.patch(order_detail_url(my_provider.id, order.id), {"car_quantity": 1})
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "discount_percent, quantity, expected_total",
        [
            pytest.param(None, 2, Decimal("60000.00"), id="no_discount"),
            pytest.param(Decimal("10.00"), 2, Decimal("54000.00"), id="with_10pct_discount"),
        ],
    )
    def test_update_price_calculation(
        self,
        client,
        provider,
        showroom,
        provider_car,
        provider_order,
        discount,
        showroom_user,
        discount_percent,
        quantity,
        expected_total,
    ):
        """Verify that updating car_quantity correctly recalculates total_price with discount."""
        my_provider = provider()
        my_showroom = showroom(owner_user=showroom_user)

        applied_discount = discount(owner_user=showroom_user, percent=discount_percent) if discount_percent else None
        my_car = provider_car(
            provider=my_provider,
            car_quantity=10,
            price=Decimal("30000.00"),
            discount=applied_discount,
        )
        order = provider_order(provider=my_provider, showroom=my_showroom, car=my_car)

        client.force_authenticate(user=showroom_user)
        response = client.patch(order_detail_url(my_provider.id, order.id), {"car_quantity": quantity})

        assert response.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.total_price == expected_total

    @pytest.mark.parametrize(
        "quantity_in_stock, quantity_ordered, wrong_provider",
        [
            (10, 1, True),
            (3, 10, False),
        ],
    )
    def test_update_rejects_invalid_order(
        self,
        client,
        provider,
        showroom,
        provider_car,
        provider_order,
        showroom_user,
        quantity_in_stock,
        quantity_ordered,
        wrong_provider,
    ):
        """Reject order updates where car belongs to wrong provider or stock is insufficient."""
        my_provider = provider()
        my_showroom = showroom(owner_user=showroom_user)
        original_car = provider_car(provider=my_provider, car_quantity=10)
        order = provider_order(provider=my_provider, showroom=my_showroom, car=original_car)

        car_provider = provider() if wrong_provider else my_provider
        new_car = provider_car(provider=car_provider, car_quantity=quantity_in_stock)

        client.force_authenticate(user=showroom_user)
        response = client.patch(
            order_detail_url(my_provider.id, order.id),
            {"car": new_car.id, "car_quantity": quantity_ordered},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "order_status, expected_status",
        [
            (OrderStatus.PENDING, status.HTTP_200_OK),
            (OrderStatus.COMPLETED, status.HTTP_400_BAD_REQUEST),
            (OrderStatus.REJECTED, status.HTTP_400_BAD_REQUEST),
        ],
    )
    def test_update_rejects_non_pending_order(
        self,
        client,
        provider,
        showroom,
        provider_car,
        provider_order,
        showroom_user,
        order_status,
        expected_status,
    ):
        """Allow updates only for PENDING orders; reject COMPLETED and REJECTED."""
        my_provider = provider()
        my_showroom = showroom(owner_user=showroom_user)
        my_car = provider_car(provider=my_provider, car_quantity=10)
        order = provider_order(provider=my_provider, showroom=my_showroom, car=my_car, status=order_status)

        client.force_authenticate(user=showroom_user)
        response = client.patch(order_detail_url(my_provider.id, order.id), {"car_quantity": 1})
        assert response.status_code == expected_status

    @pytest.mark.parametrize("get_action_url", [order_confirm_url, order_reject_url])
    @pytest.mark.parametrize(
        "auth_role_client, is_provider_owner, needs_showroom, expected_status",
        [
            ("provider_user", True, False, status.HTTP_200_OK),
            ("provider_user", False, False, status.HTTP_403_FORBIDDEN),
            ("showroom_user", False, True, status.HTTP_403_FORBIDDEN),
            ("user", False, False, status.HTTP_403_FORBIDDEN),
            (None, False, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_provider_action_permissions(
        self,
        auth_role_client,
        is_provider_owner,
        needs_showroom,
        get_action_url,
        provider,
        showroom,
        provider_car,
        provider_order,
        expected_status,
    ):
        """Allow only the provider owner to confirm or reject orders."""
        force_user = getattr(auth_role_client.handler, "_force_user", None)
        my_provider = provider(owner_user=force_user) if is_provider_owner else provider()

        if needs_showroom and force_user:
            showroom(owner_user=force_user)

        order_showroom_user = UserFactory(type=UserType.SHOWROOM, balance=Decimal("50000.00"))
        order_showroom = showroom(owner_user=order_showroom_user)
        my_car = provider_car(provider=my_provider, car_quantity=5, price=Decimal("100.00"))
        order = provider_order(
            provider=my_provider, showroom=order_showroom, car=my_car, car_quantity=1, total_price=Decimal("100.00")
        )

        response = auth_role_client.post(get_action_url(my_provider.id, order.id))
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "auth_role_client, needs_showroom, is_order_owner, expected_status",
        [
            ("showroom_user", True, True, status.HTTP_200_OK),
            ("showroom_user", True, False, status.HTTP_404_NOT_FOUND),
            ("provider_user", False, False, status.HTTP_403_FORBIDDEN),
            ("user", False, False, status.HTTP_403_FORBIDDEN),
            (None, False, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_cancel_permissions(
        self,
        auth_role_client,
        needs_showroom,
        is_order_owner,
        provider,
        showroom,
        provider_car,
        provider_order,
        expected_status,
    ):
        """Allow only the order-owning showroom to cancel; block providers and others."""
        force_user = getattr(auth_role_client.handler, "_force_user", None)
        my_provider = provider()
        my_car = provider_car(provider=my_provider, car_quantity=10)

        auth_showroom = showroom(owner_user=force_user) if needs_showroom and force_user else None
        order_showroom = auth_showroom if is_order_owner and auth_showroom else showroom()

        order = provider_order(provider=my_provider, showroom=order_showroom, car=my_car)

        response = auth_role_client.post(order_cancel_url(my_provider.id, order.id))
        assert response.status_code == expected_status

    def test_confirm_completes_order(
        self,
        client,
        provider,
        showroom,
        provider_car,
        provider_order,
        provider_user,
    ):
        """Verify that confirming an order transfers balances, adjusts stock, and creates ShowroomCar."""
        from car_showrooms.models import ShowroomCar

        my_provider = provider(owner_user=provider_user)
        total_price = Decimal("30000.00")
        initial_provider_balance = provider_user.balance

        showroom_owner = UserFactory(type=UserType.SHOWROOM, balance=Decimal("50000.00"))
        my_showroom = showroom(owner_user=showroom_owner)
        my_car = provider_car(provider=my_provider, car_quantity=5, price=Decimal("30000.00"))
        order = provider_order(
            provider=my_provider, showroom=my_showroom, car=my_car, car_quantity=1, total_price=total_price
        )

        client.force_authenticate(user=provider_user)
        response = client.post(order_confirm_url(my_provider.id, order.id))

        assert response.status_code == status.HTTP_200_OK

        showroom_owner.refresh_from_db()
        provider_user.refresh_from_db()
        my_car.refresh_from_db()
        order.refresh_from_db()

        assert showroom_owner.balance == Decimal("50000.00") - total_price
        assert provider_user.balance == initial_provider_balance + total_price
        assert my_car.car_quantity == 4  # 5 - 1
        assert ShowroomCar.objects.filter(showroom=my_showroom).exists()
        showroom_car = ShowroomCar.objects.get(showroom=my_showroom)
        assert showroom_car.car_quantity == 1
        assert showroom_car.car == my_car.car  # guards the order.car.car FK fix
        assert order.status == OrderStatus.COMPLETED

    @staticmethod
    def _setup_action_order(user_fixture, request, provider, showroom, provider_car, provider_order, **order_kwargs):
        """Create a PENDING order with correct provider/showroom ownership for the given user fixture.

        provider_user → owns the provider, a separate showroom is created for the order.
        showroom_user → owns the order's showroom, a separate provider is created.

        Returns (auth_user, my_provider, order).
        """
        auth_user = request.getfixturevalue(user_fixture)
        if user_fixture == "provider_user":
            my_provider = provider(owner_user=auth_user)
            order_showroom = showroom()
        else:
            my_provider = provider()
            order_showroom = showroom(owner_user=auth_user)
        my_car = provider_car(provider=my_provider, car_quantity=10)
        order = provider_order(provider=my_provider, showroom=order_showroom, car=my_car, **order_kwargs)
        return auth_user, my_provider, order

    @pytest.mark.parametrize(
        "get_action_url, user_fixture, expected_order_status",
        [
            (order_reject_url, "provider_user", OrderStatus.REJECTED),
            (order_cancel_url, "showroom_user", OrderStatus.CANCELLED),
        ],
    )
    def test_status_change_on_action(
        self,
        client,
        get_action_url,
        user_fixture,
        expected_order_status,
        provider,
        showroom,
        provider_car,
        provider_order,
        request,
    ):
        """Verify that reject sets REJECTED and cancel sets CANCELLED status."""
        auth_user, my_provider, order = self._setup_action_order(
            user_fixture, request, provider, showroom, provider_car, provider_order
        )

        client.force_authenticate(user=auth_user)
        response = client.post(get_action_url(my_provider.id, order.id))

        assert response.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.status == expected_order_status

    @pytest.mark.parametrize(
        "initial_order_status",
        [OrderStatus.COMPLETED, OrderStatus.REJECTED, OrderStatus.CANCELLED],
    )
    @pytest.mark.parametrize(
        "get_action_url, user_fixture",
        [
            (order_confirm_url, "provider_user"),
            (order_reject_url, "provider_user"),
            (order_cancel_url, "showroom_user"),
        ],
    )
    def test_actions_require_pending_status(
        self,
        client,
        get_action_url,
        user_fixture,
        initial_order_status,
        provider,
        showroom,
        provider_car,
        provider_order,
        request,
    ):
        """Reject confirm/reject/cancel actions on non-PENDING orders."""
        auth_user, my_provider, order = self._setup_action_order(
            user_fixture, request, provider, showroom, provider_car, provider_order, status=initial_order_status
        )

        client.force_authenticate(user=auth_user)
        response = client.post(get_action_url(my_provider.id, order.id))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

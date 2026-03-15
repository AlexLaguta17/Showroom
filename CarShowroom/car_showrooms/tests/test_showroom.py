"""Tests for car showroom API permissions and business rules."""

import pytest
from django.urls import reverse
from rest_framework import status

pytest_plugins = [
    "users.tests.fixtures",
    "car_showrooms.tests.fixtures",
    "dealers.tests.fixtures",
]


@pytest.mark.django_db
class TestCarShowroomPermissions:
    """Tests for showroom creation and update permissions.

    1. Creation rule (type=SHOWROOM + only one showroom)
    2. Update only by owner_user
    """

    @pytest.mark.parametrize(
        "user_fixture, has_existing_showroom, expected_status",
        [
            ("showroom_user", False, status.HTTP_201_CREATED),
            ("showroom_user", True, status.HTTP_400_BAD_REQUEST),
            ("user", False, status.HTTP_403_FORBIDDEN),
            ("provider_user", False, status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_showroom_rules(
        self,
        request,
        client,
        showroom,
        user_fixture,
        has_existing_showroom,
        expected_status,
    ):
        """Allow SHOWROOM users to create exactly one showroom; block duplicates and other roles."""
        user = request.getfixturevalue(user_fixture)

        if has_existing_showroom:
            showroom(owner_user=user)
        client.force_authenticate(user=user)

        response = client.post(reverse("showroom-list"), {"name": "New Showroom"})

        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.data["owner_user_id"] == user.id

    @pytest.mark.parametrize(
        "role, expected_status",
        [
            ("owner", status.HTTP_200_OK),
            ("stranger", status.HTTP_403_FORBIDDEN),
            ("anonymous", status.HTTP_401_UNAUTHORIZED),
        ],
    )
    def test_update_showroom_permissions(self, client, showroom, showroom_user, another_user, role, expected_status):
        """Allow only the showroom owner to update; block strangers and anonymous users."""
        obj = showroom(owner_user=showroom_user, name="Old Name")

        if role == "owner":
            client.force_authenticate(user=showroom_user)
        elif role == "stranger":
            client.force_authenticate(user=another_user)

        response = client.patch(reverse("showroom-detail", args=[obj.id]), {"name": "Updated Name"})

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            obj.refresh_from_db()
            assert obj.name == "Updated Name"


@pytest.mark.django_db
class TestShowroomCarPermissions:
    """Tests for showroom car update and list filtering permissions."""

    @pytest.mark.parametrize(
        "role, expected_status",
        [
            ("owner", status.HTTP_200_OK),
            ("stranger", status.HTTP_403_FORBIDDEN),
            ("anonymous", status.HTTP_401_UNAUTHORIZED),
        ],
    )
    def test_update_showroom_car_permissions(
        self,
        client,
        showroom,
        showroom_car,
        showroom_user,
        another_user,
        role,
        expected_status,
    ):
        """Allow only the showroom owner to update car entries."""
        my_showroom = showroom(owner_user=showroom_user)
        car_entry = showroom_car(showroom=my_showroom)

        if role == "owner":
            client.force_authenticate(user=showroom_user)
        elif role == "stranger":
            client.force_authenticate(user=another_user)

        response = client.patch(
            reverse("showroom-car-detail", args=[my_showroom.id, car_entry.id]),
            {"price": "15000.00"},
        )

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            car_entry.refresh_from_db()
            assert str(car_entry.price) == "15000.00"

    @pytest.mark.parametrize(
        "role, expected_count",
        [
            ("public", 1),
            ("owner", 4),
        ],
    )
    def test_showroom_car_queryset_filtering(self, client, showroom, showroom_car, showroom_user, role, expected_count):
        """Return only published, in-stock, priced cars to the public; return all to the owner."""
        my_showroom = showroom(owner_user=showroom_user)

        showroom_car(
            showroom=my_showroom,
            price=20000,
            car_quantity=1,
            is_published=True,
        )

        showroom_car(showroom=my_showroom, price=0)
        showroom_car(showroom=my_showroom, car_quantity=0)
        showroom_car(showroom=my_showroom, is_published=False)

        if role == "owner":
            client.force_authenticate(user=showroom_user)

        response = client.get(reverse("showroom-car-list", args=[my_showroom.id]))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == expected_count


@pytest.mark.django_db
class TestShowroomDiscountPermissions:
    """Tests for showroom discount create and update permissions."""

    @pytest.mark.parametrize(
        "role, expected_status",
        [
            ("owner", status.HTTP_201_CREATED),
            ("stranger", status.HTTP_403_FORBIDDEN),
            ("anonymous", status.HTTP_401_UNAUTHORIZED),
        ],
    )
    def test_create_discount_permissions(
        self,
        client,
        showroom,
        another_user,
        role,
        expected_status,
    ):
        """Allow only the showroom owner to create discounts."""
        my_showroom = showroom()

        payload = {
            "name": "Summer Sale",
            "percent": "15.00",
        }

        if role == "owner":
            client.force_authenticate(user=my_showroom.owner_user)
        elif role == "stranger":
            client.force_authenticate(user=another_user)

        response = client.post(reverse("showroom-discount-list", args=[my_showroom.id]), payload)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.data["owner_user_id"] == my_showroom.owner_user.id

    @pytest.mark.parametrize(
        "role, expected_status",
        [
            ("owner", status.HTTP_200_OK),
            ("stranger", status.HTTP_403_FORBIDDEN),
            ("anonymous", status.HTTP_401_UNAUTHORIZED),
        ],
    )
    def test_update_discount_permissions(
        self,
        client,
        showroom,
        discount,
        showroom_user,
        another_user,
        role,
        expected_status,
    ):
        """Allow only the discount owner to update; block strangers and anonymous users."""
        my_showroom = showroom(owner_user=showroom_user)
        my_discount = discount(owner_user=showroom_user)

        if role == "owner":
            client.force_authenticate(user=showroom_user)
        elif role == "stranger":
            client.force_authenticate(user=another_user)

        response = client.patch(
            reverse("showroom-discount-detail", args=[my_showroom.id, my_discount.id]),
            {"percent": "30.00"},
        )

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            my_discount.refresh_from_db()
            assert str(my_discount.percent) == "30.00"

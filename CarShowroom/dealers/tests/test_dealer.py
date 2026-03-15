"""Tests for dealer API permissions and business rules."""

import pytest
from django.urls import reverse
from rest_framework import status

from services.choices import BodyType, EngineType, TransmissionType

pytest_plugins = [
    "users.tests.fixtures",
    "car_showrooms.tests.fixtures",
    "dealers.tests.fixtures",
]


@pytest.mark.django_db
class TestCarPermissions:
    """Tests for car list and create endpoint permissions."""

    @pytest.mark.parametrize(
        "auth_role_client, expected_status",
        [
            ("provider_user", status.HTTP_200_OK),
            ("showroom_user", status.HTTP_200_OK),
            ("user", status.HTTP_403_FORBIDDEN),
            (None, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_car_list_permissions(self, auth_role_client, car, expected_status):
        """Allow providers and showrooms to list cars; block customers and anonymous users."""
        car()
        response = auth_role_client.get(reverse("car-list"))
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "auth_role_client, expected_status",
        [
            ("provider_user", status.HTTP_201_CREATED),
            ("showroom_user", status.HTTP_403_FORBIDDEN),
            ("user", status.HTTP_403_FORBIDDEN),
            (None, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_car_create_permissions(self, auth_role_client, expected_status):
        """Allow only providers to create cars; block all other roles."""
        payload = {
            "engine_type": EngineType.GASOLINE,
            "transmission_type": TransmissionType.MANUAL,
            "body_type": BodyType.SEDAN,
            "engine_volume": "2.0",
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "year": 2020,
        }

        response = auth_role_client.post(reverse("car-list"), payload)
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestProviderPermissions:
    """Tests for provider create and update endpoint permissions."""

    @pytest.mark.parametrize(
        "auth_role_client, has_provider, expected_status",
        [
            ("provider_user", False, status.HTTP_201_CREATED),
            ("provider_user", True, status.HTTP_400_BAD_REQUEST),
            ("showroom_user", False, status.HTTP_403_FORBIDDEN),
            ("user", False, status.HTTP_403_FORBIDDEN),
            (None, False, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_create_provider_rules(
        self,
        auth_role_client,
        provider,
        has_provider,
        expected_status,
    ):
        """Allow providers without an existing provider to create one; block duplicates."""
        user = getattr(auth_role_client.handler._force_user, "pk", None)

        if has_provider and user:
            provider(owner_user_id=user)

        response = auth_role_client.post(
            reverse("provider-list"),
            {"name": "New Provider", "year_founded": 2000},
        )

        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "auth_role_client, owner_fixture, expected_status",
        [
            ("provider_user", "provider_user", status.HTTP_200_OK),
            ("another_user", "provider_user", status.HTTP_403_FORBIDDEN),
            ("showroom_user", "provider_user", status.HTTP_403_FORBIDDEN),
        ],
        indirect=["auth_role_client"],
    )
    def test_update_provider_permissions(
        self,
        auth_role_client,
        provider,
        request,
        owner_fixture,
        expected_status,
    ):
        """Allow only the provider owner to update provider details."""
        owner = request.getfixturevalue(owner_fixture)
        obj = provider(owner_user=owner)

        response = auth_role_client.patch(reverse("provider-detail", args=[obj.id]), {"name": "Updated"})

        assert response.status_code == expected_status


@pytest.mark.django_db
class TestProviderCarPermissions:
    """Tests for provider car create endpoint permissions."""

    @pytest.mark.parametrize(
        "auth_role_client, expected_status",
        [
            ("provider_user", status.HTTP_201_CREATED),
            ("another_user", status.HTTP_403_FORBIDDEN),
            ("showroom_user", status.HTTP_403_FORBIDDEN),
            (None, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_create_provider_car_permissions(
        self,
        auth_role_client,
        provider,
        car,
        provider_user,
        expected_status,
    ):
        """Allow only the provider owner to add cars to their inventory."""
        my_provider = provider(owner_user=provider_user)
        new_car = car()

        payload = {
            "car": new_car.id,
            "car_quantity": 10,
            "price": "25000.00",
        }

        response = auth_role_client.post(reverse("provider-car-list", args=[my_provider.id]), payload)
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestProviderDiscountPermissions:
    """Tests for provider discount create endpoint permissions."""

    @pytest.mark.parametrize(
        "auth_role_client, expected_status",
        [
            ("provider_user", status.HTTP_201_CREATED),
            ("another_user", status.HTTP_403_FORBIDDEN),
            ("showroom_user", status.HTTP_403_FORBIDDEN),
            (None, status.HTTP_401_UNAUTHORIZED),
        ],
        indirect=["auth_role_client"],
    )
    def test_create_provider_discount_permissions(
        self,
        auth_role_client,
        provider,
        provider_user,
        expected_status,
    ):
        """Allow only the provider owner to create discounts."""
        my_provider = provider(owner_user=provider_user)

        payload = {"name": "Summer", "percent": "10.00"}

        response = auth_role_client.post(reverse("provider-discount-list", args=[my_provider.id]), payload)
        assert response.status_code == expected_status

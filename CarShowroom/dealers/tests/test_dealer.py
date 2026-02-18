import pytest

from rest_framework import status

from services.choices import EngineType, TransmissionType, BodyType

pytest_plugins = [
    "users.tests.fixtures",
    "car_showrooms.tests.fixtures",
    "dealers.tests.fixtures",
]

BASE_URL = "/api/v1/dealers/"
CARS_URL = f"{BASE_URL}cars/"


@pytest.mark.django_db
class TestCarPermissions:

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
        car()
        response = auth_role_client.get(CARS_URL)
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

        response = auth_role_client.post(CARS_URL, payload)
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestProviderPermissions:

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
        user = getattr(auth_role_client.handler._force_user, "pk", None)

        if has_provider and user:
            provider(owner_user_id=user)

        response = auth_role_client.post(
            BASE_URL,
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
        owner = request.getfixturevalue(owner_fixture)
        obj = provider(owner_user=owner)

        url = f"{BASE_URL}{obj.id}/"
        response = auth_role_client.patch(url, {"name": "Updated"})

        assert response.status_code == expected_status


@pytest.mark.django_db
class TestProviderCarPermissions:

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
        my_provider = provider(owner_user=provider_user)
        new_car = car()

        url = f"{BASE_URL}{my_provider.id}/cars/"
        payload = {
            "car": new_car.id,
            "car_quantity": 10,
            "price": "25000.00",
        }

        response = auth_role_client.post(url, payload)
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestProviderDiscountPermissions:

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
        my_provider = provider(owner_user=provider_user)

        url = f"{BASE_URL}{my_provider.id}/discounts/"
        payload = {"name": "Summer", "percent": "10.00"}

        response = auth_role_client.post(url, payload)
        assert response.status_code == expected_status

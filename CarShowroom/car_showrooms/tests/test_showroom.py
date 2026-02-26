import pytest
from rest_framework import status

pytest_plugins = [
    "users.tests.fixtures",
    "car_showrooms.tests.fixtures",
    "dealers.tests.fixtures",
]

BASE_URL = "/api/v1/showrooms/"


def showroom_detail_url(showroom_id):
    return f"{BASE_URL}{showroom_id}/"


def showroom_cars_url(showroom_id):
    return f"{BASE_URL}{showroom_id}/cars/"


def showroom_car_detail_url(showroom_id, car_id):
    return f"{BASE_URL}{showroom_id}/cars/{car_id}/"


def showroom_discounts_url(showroom_id):
    return f"{BASE_URL}{showroom_id}/discounts/"


def showroom_discount_detail_url(showroom_id, discount_id):
    return f"{BASE_URL}{showroom_id}/discounts/{discount_id}/"


@pytest.mark.django_db
class TestCarShowroomPermissions:
    """
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
        user = request.getfixturevalue(user_fixture)

        if has_existing_showroom:
            showroom(owner_user=user)
        client.force_authenticate(user=user)

        response = client.post(BASE_URL, {"name": "New Showroom"})

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
        obj = showroom(owner_user=showroom_user, name="Old Name")
        url = showroom_detail_url(obj.id)

        if role == "owner":
            client.force_authenticate(user=showroom_user)
        elif role == "stranger":
            client.force_authenticate(user=another_user)

        response = client.patch(url, {"name": "Updated Name"})

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            obj.refresh_from_db()
            assert obj.name == "Updated Name"


@pytest.mark.django_db
class TestShowroomCarPermissions:
    """Only owner_user can update ShowroomCar"""

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
        my_showroom = showroom(owner_user=showroom_user)
        car_entry = showroom_car(showroom=my_showroom)

        url = showroom_car_detail_url(my_showroom.id, car_entry.id)

        if role == "owner":
            client.force_authenticate(user=showroom_user)
        elif role == "stranger":
            client.force_authenticate(user=another_user)

        response = client.patch(url, {"price": "15000.00"})

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

        url = showroom_cars_url(my_showroom.id)

        if role == "owner":
            client.force_authenticate(user=showroom_user)

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == expected_count


@pytest.mark.django_db
class TestShowroomDiscountPermissions:
    """Only owner_user can create & update discounts"""

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
        my_showroom = showroom()
        url = showroom_discounts_url(my_showroom.id)

        payload = {
            "name": "Summer Sale",
            "percent": "15.00",
        }

        if role == "owner":
            client.force_authenticate(user=my_showroom.owner_user)
        elif role == "stranger":
            client.force_authenticate(user=another_user)

        response = client.post(url, payload)

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
        my_showroom = showroom(owner_user=showroom_user)
        my_discount = discount(owner_user=showroom_user)

        url = showroom_discount_detail_url(my_showroom.id, my_discount.id)

        if role == "owner":
            client.force_authenticate(user=showroom_user)
        elif role == "stranger":
            client.force_authenticate(user=another_user)

        response = client.patch(url, {"percent": "30.00"})

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            my_discount.refresh_from_db()
            assert str(my_discount.percent) == "30.00"

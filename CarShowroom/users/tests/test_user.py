import pytest
from rest_framework import status
from django.contrib.auth import get_user_model

pytest_plugins = ["users.tests.fixtures"]

User = get_user_model()

USERS_URL = "/api/v1/users/"


def detail_url(user_id):
    return f"{USERS_URL}{user_id}/"


@pytest.mark.django_db
class TestUserAPI:

    @pytest.mark.parametrize(
        "client_fixture, expected_status",
        [
            ("client", status.HTTP_201_CREATED),
            ("auth_client", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_user_permissions(
        self, request, client_fixture, expected_status, user_payload
    ):
        client = request.getfixturevalue(client_fixture)
        response = client.post(USERS_URL, user_payload)

        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "target_fixture, expected_status, should_update",
        [
            ("user", status.HTTP_200_OK, True),
            ("another_user", status.HTTP_403_FORBIDDEN, False),
        ],
    )
    def test_update_profile_permissions(
        self, auth_client, request, target_fixture, expected_status, should_update, user
    ):
        target_user = request.getfixturevalue(target_fixture)
        payload = {"first_name": "Updated"}
        response = auth_client.patch(detail_url(target_user.id), payload)

        assert response.status_code == expected_status
        user.refresh_from_db()

        if should_update:
            assert user.first_name == "Updated"
        else:
            assert user.first_name != "Updated"

    def test_soft_delete_user(self, auth_client, user, another_user):
        """
        User owner can delete profile and his is_active flag will be False. Users with is_active=False not in queryset.
        """

        response = auth_client.delete(detail_url(user.id))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.is_active is False
        assert User.objects.filter(id=user.id).exists()

        response = auth_client.get(USERS_URL)

        assert response.status_code == status.HTTP_200_OK
        ids = [u["id"] for u in response.data]
        assert user.id not in ids
        assert another_user.id in ids

"""Tests for user API permissions and business rules."""

import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

pytest_plugins = ["users.tests.fixtures"]

User = get_user_model()


@pytest.mark.django_db
class TestUserAPI:
    """Tests for user registration, profile updates, and soft deletion."""

    @pytest.mark.parametrize(
        "client_fixture, expected_status",
        [
            ("client", status.HTTP_201_CREATED),
            ("auth_client", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_user_permissions(self, request, client_fixture, expected_status, user_payload):
        """Allow anonymous users to register; block authenticated users."""
        client = request.getfixturevalue(client_fixture)
        response = client.post(reverse("user-list"), user_payload)

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
        """Allow users to update their own profile; block updates to other profiles."""
        target_user = request.getfixturevalue(target_fixture)
        payload = {"first_name": "Updated"}
        response = auth_client.patch(reverse("user-detail", args=[target_user.id]), payload)

        assert response.status_code == expected_status
        user.refresh_from_db()

        if should_update:
            assert user.first_name == "Updated"
        else:
            assert user.first_name != "Updated"

    def test_soft_delete_user(self, auth_client, user, another_user):
        """Set is_active=False on delete; exclude the user from subsequent list results."""
        response = auth_client.delete(reverse("user-detail", args=[user.id]))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.is_active is False
        assert User.objects.filter(id=user.id).exists()

        response = auth_client.get(reverse("user-list"))

        assert response.status_code == status.HTTP_200_OK
        ids = [u["id"] for u in response.data]
        assert user.id not in ids
        assert another_user.id in ids

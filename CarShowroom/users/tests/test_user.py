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

    def test_create_user_anonymous(self, client, user_payload):
        """Anonymous users can create a new user and password does not return in response.data"""
        response = client.post(USERS_URL, user_payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=user_payload["username"]).exists()
        assert "password" not in response.data

    def test_create_user_authenticated_forbidden(self, auth_client, user_payload):
        """Authorized users can't create a new user"""
        response = auth_client.post(USERS_URL, user_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_own_profile(self, auth_client, user):
        """Only owner can update their own profile"""
        payload = {"first_name": "Updated Name"}

        response = auth_client.patch(detail_url(user.id), payload)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "Updated Name"

    def test_update_other_profile_forbidden(self, auth_client, user, another_user):
        """User cannot update not his own profile"""
        payload = {"first_name": "Hacked"}

        response = auth_client.patch(detail_url(another_user.id), payload)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not user.first_name == "Hacked"

    def test_soft_delete_user(self, auth_client, user):
        """User owner can delete profile and his is_active flag will be False"""

        response = auth_client.delete(detail_url(user.id))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.is_active is False

    def test_soft_deleted_user_not_in_queryset(self, client, user, another_user):
        """Deleted user is not in queryset"""
        user.is_active = False
        user.save()
        response = client.get(USERS_URL)

        assert response.status_code == status.HTTP_200_OK
        ids = [u["id"] for u in response.data]
        assert user.id not in ids
        assert another_user.id in ids

    @pytest.mark.parametrize("method", ["get", "head", "options"])
    def test_safe_methods_allowed(self, client, user, method):
        client_method = getattr(client, method)
        response = client_method(detail_url(user.id))
        assert response.status_code == 200

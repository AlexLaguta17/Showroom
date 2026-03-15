"""Tests for JWT token authentication endpoints."""

import pytest
from django.urls import reverse

from users.tests.factories import UserFactory

pytest_plugins = ["users.tests.fixtures"]


class TestJWT:
    """Tests for JWT obtain, refresh, and verify endpoints."""

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "username,password,expected_status",
        [
            ("valid_user", "correctpass", 200),
            ("valid_user", "wrongpass", 401),
            ("wrong_user", "correctpass", 401),
        ],
    )
    def test_jwt_login_parametrized(self, client, username, password, expected_status):
        """Return 200 for valid credentials and 401 for invalid username or password."""
        user = UserFactory(username="valid_user")
        user.set_password("correctpass")
        user.save()

        response = client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": password},
        )

        assert response.status_code == expected_status

    @pytest.mark.django_db
    def test_refresh_token(self, client, user):
        """Return a new access token when a valid refresh token is provided."""
        user.set_password("testpass123")
        token_response = client.post(
            reverse("token_obtain_pair"),
            {"username": user.username, "password": "testpass123"},
        )

        refresh_token = token_response.data["refresh"]

        response = client.post(
            reverse("token_refresh"),
            {"refresh": refresh_token},
        )

        assert response.status_code == 200
        assert "access" in response.data

    @pytest.mark.django_db
    def test_verify_token(self, client, user):
        """Return 200 when a valid access token is submitted to the verify endpoint."""
        user.set_password("testpass123")

        token_response = client.post(
            reverse("token_obtain_pair"),
            {"username": user.username, "password": "testpass123"},
        )

        access_token = token_response.data["access"]

        response = client.post(
            reverse("token_verify"),
            {"token": access_token},
        )

        assert response.status_code == 200

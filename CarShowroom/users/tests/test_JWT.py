import pytest

from users.tests.factories import UserFactory

pytest_plugins = ["users.tests.fixtures"]

TOKEN_URL = "/api/v1/token/"
REFRESH_URL = "/api/v1/token/refresh/"
VERIFY_URL = "/api/v1/token/verify/"


class TestJWT:

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
        user = UserFactory(username="valid_user")
        user.set_password("correctpass")
        user.save()

        response = client.post(
            "/api/v1/token/",
            {"username": username, "password": password},
        )

        assert response.status_code == expected_status

    @pytest.mark.django_db
    def test_refresh_token(self, client, user):
        user.set_password("testpass123")
        token_response = client.post(
            TOKEN_URL,
            {"username": user.username, "password": "testpass123"},
        )

        refresh_token = token_response.data["refresh"]

        response = client.post(
            REFRESH_URL,
            {"refresh": refresh_token},
        )

        assert response.status_code == 200
        assert "access" in response.data

    @pytest.mark.django_db
    def test_verify_token(self, client, user):
        user.set_password("testpass123")

        token_response = client.post(
            TOKEN_URL,
            {"username": user.username, "password": "testpass123"},
        )

        access_token = token_response.data["access"]

        response = client.post(
            VERIFY_URL,
            {"token": access_token},
        )

        assert response.status_code == 200

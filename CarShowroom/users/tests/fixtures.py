import pytest
from rest_framework.test import APIClient

from .factories import UserFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user, client):
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def another_user():
    return UserFactory()


@pytest.fixture
def user_payload():
    return {
        "username": "new_user",
        "password": "strong_password_123",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "age": 25,
        "phone_number": "+12345678901",
        "country": "US",
        "type": "customer",
    }

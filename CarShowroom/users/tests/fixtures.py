"""Pytest fixtures for the users app."""

import pytest
from rest_framework.test import APIClient

from services.choices import UserType

from .factories import UserFactory


@pytest.fixture
def client():
    """Return an unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def auth_client(user, client):
    """Return an API client authenticated as the default user."""
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def auth_role_client(client, request):
    """Return an authenticated or anonymous client depending on the param value."""
    user_fixture = getattr(request, "param", None)

    if user_fixture:
        user = request.getfixturevalue(user_fixture)
        client.force_authenticate(user=user)

    return client


@pytest.fixture
def user():
    """Return a default customer user."""
    return UserFactory()


@pytest.fixture
def another_user():
    """Return a second customer user distinct from the default user."""
    return UserFactory()


@pytest.fixture
def provider_user():
    """Return a user with the PROVIDER role."""
    return UserFactory(type=UserType.PROVIDER)


@pytest.fixture
def showroom_user():
    """Return a user with the SHOWROOM role."""
    return UserFactory(type=UserType.SHOWROOM)


@pytest.fixture
def user_payload():
    """Return a valid payload dict for creating a new user via the API."""
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

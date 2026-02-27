"""Tests for the User model behaviour."""

import pytest
from django.contrib.auth import get_user_model

pytest_plugins = [
    "users.tests.fixtures",
]

User = get_user_model()


@pytest.mark.django_db
def test_password_is_hashed():
    """Verify that saving a User with a plain-text password auto-hashes it."""
    user = User.objects.create(
        username="user",
        password="password",
    )

    assert user.password != "password"
    assert user.check_password("password")

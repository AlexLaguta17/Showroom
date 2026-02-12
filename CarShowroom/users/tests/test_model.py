import pytest
from django.contrib.auth import get_user_model

pytest_plugins = [
    "users.tests.fixtures",
]

User = get_user_model()


@pytest.mark.django_db
def test_password_is_hashed():

    user = User.objects.create(
        username="user",
        password="password",
    )

    assert user.password != "password"
    assert user.check_password("password")

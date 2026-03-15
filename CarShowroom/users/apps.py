"""App configuration for the users Django app."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Django app configuration for users."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

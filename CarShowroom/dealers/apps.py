"""App configuration for the dealers Django app."""

from django.apps import AppConfig


class DealersConfig(AppConfig):
    """Django app configuration for dealers."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dealers"

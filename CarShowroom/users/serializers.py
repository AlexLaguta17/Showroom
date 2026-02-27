"""Serializers for the users app."""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django_countries.serializers import CountryFieldMixin


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    """Serializer for the User model; password is write-only."""

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        """User serializer metadata."""

        model = get_user_model()
        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "type",
            "phone_number",
            "age",
            "country",
        )

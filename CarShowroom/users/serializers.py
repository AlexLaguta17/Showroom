from rest_framework import serializers
from django.contrib.auth import get_user_model
from django_countries.serializers import CountryFieldMixin


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = "__all__"

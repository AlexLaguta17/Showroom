from rest_framework import serializers

from dealers.models import (
    Car,
    Provider,
    ProviderCar,
    ProviderOrder,
)


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = "__all__"


class ProviderCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderCar
        fields = "__all__"


class ProviderOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderOrder
        fields = "__all__"

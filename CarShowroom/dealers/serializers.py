from rest_framework import serializers

from dealers.models import (
    Car,
    Provider,
    ProviderCars,
    ProviderSalesHistory,
    ProviderDiscount,
)


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = "__all__"


class ProviderCarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderCars
        fields = "__all__"


class ProviderSalesHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderSalesHistory
        fields = "__all__"


class ProviderDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderDiscount
        fields = "__all__"

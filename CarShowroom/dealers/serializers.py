from rest_framework import serializers

from services.order_service import validate_order_creation
from dealers.models import (
    Car,
    Provider,
    ProviderCar,
    ProviderOrder,
)


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = (
            "id",
            "engine_type",
            "transmission_type",
            "body_type",
            "engine_volume",
            "brand",
            "model",
            "color",
            "year",
        )


class ProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Provider
        fields = "id", "name", "year_founded", "owner_user_id", "cars"
        read_only_fields = ("owner_user_id", "cars")

    def validate(self, attrs):
        user = self.context["request"].user

        if self.instance is None and Provider.objects.filter(owner_user_id=user.id).exists():
            raise serializers.ValidationError({"detail": "User already has one."})

        return attrs


class ProviderCarSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProviderCar
        fields = "id", "car_quantity", "price", "discount", "car"


class UpdateProviderCarSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProviderCar
        fields = "id", "car_quantity", "price", "discount"


class ProviderOrderSerializer(serializers.ModelSerializer):
    """Serializer for reading provider order data."""

    class Meta:
        model = ProviderOrder
        fields = (
            "id",
            "provider",
            "showroom",
            "car",
            "car_quantity",
            "status",
            "sale_date",
            "total_price",
        )
        read_only_fields = "status", "total_price", "sale_date", "showroom", "provider"
        extra_kwargs = {
            "car_quantity": {
                "required": True,
            }
        }

    def validate(self, attrs):
        provider = self.context["view"].provider
        provider_car = attrs["car"]
        car_quantity = attrs["car_quantity"]

        total_price = validate_order_creation(provider_car, car_quantity, provider)

        attrs["total_price"] = total_price
        return attrs


class ProviderOrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a provider order.
    Allows updating only car and car_quantity fields.
    """

    class Meta:
        model = ProviderOrder
        fields = (
            "id",
            "provider",
            "showroom",
            "car",
            "car_quantity",
            "status",
            "sale_date",
            "total_price",
        )
        read_only_fields = "status", "total_price", "sale_date", "showroom", "provider"
        extra_kwargs = {
            "car": {"required": False},
            "car_quantity": {"required": False},
        }

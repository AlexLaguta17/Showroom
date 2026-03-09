"""Serializers for the dealer's app."""

from rest_framework import serializers

from services.order_service import validate_provider_order_creation
from dealers.models import Car, Provider, ProviderCar, ProviderOrder


class CarSerializer(serializers.ModelSerializer):
    """Serializer for the Car model."""

    class Meta:
        """Car serializer metadata."""

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
    """Serializer for the Provider model."""

    class Meta:
        """Provider serializer metadata."""

        model = Provider
        fields = "id", "name", "year_founded", "owner_user_id", "cars"
        read_only_fields = ("owner_user_id", "cars")

    def validate(self, attrs):
        """Prevent a user from owning more than one provider."""
        user = self.context["request"].user

        if self.instance is None and Provider.objects.filter(owner_user_id=user.id).exists():
            raise serializers.ValidationError({"detail": "User already has one."})

        return attrs


class ProviderCarSerializer(serializers.ModelSerializer):
    """Serializer for creating and reading ProviderCar entries."""

    class Meta:
        """ProviderCar serializer metadata."""

        model = ProviderCar
        fields = "id", "car_quantity", "price", "discount", "car"


class UpdateProviderCarSerializer(serializers.ModelSerializer):
    """Serializer for updating ProviderCar price, discount, and quantity."""

    class Meta:
        """UpdateProviderCar serializer metadata."""

        model = ProviderCar
        fields = "id", "car_quantity", "price", "discount"


class ProviderOrderSerializer(serializers.ModelSerializer):
    """Serializer for reading provider order data."""

    class Meta:
        """ProviderOrder serializer metadata."""

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
        """Validate order creation and compute total price."""
        provider = self.context["view"].provider
        provider_car = attrs["car"]
        car_quantity = attrs["car_quantity"]

        total_price = validate_provider_order_creation(provider_car, car_quantity, provider)

        attrs["total_price"] = total_price
        return attrs


class ProviderOrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a provider order.

    Allows updating only car and car_quantity fields.
    """

    class Meta:
        """ProviderOrderUpdate serializer metadata."""

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

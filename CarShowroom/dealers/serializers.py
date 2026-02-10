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

        if self.instance is None:
            if Provider.objects.filter(owner_user_id=user.id).exists():
                raise serializers.ValidationError({"detail": "User already has one."})

        return attrs


class ProviderCarSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProviderCar
        fields = "id", "car_quantity", "price", "discount", "car"


class UpdateProviderCarSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProviderCar
        fields = (
            "id",
            "car_quantity",
            "price",
            "discount",
        )


# TODO redo everything below
class ProviderOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new provider order."""

    provider_id = serializers.IntegerField(write_only=True)
    car_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProviderOrder
        fields = ["provider_id", "car_id", "car_quantity"]


class ProviderOrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a provider order.
    Allows updating only car and car_quantity fields.
    """

    class Meta:
        model = ProviderOrder
        fields = ["car", "car_quantity"]
        extra_kwargs = {
            "car": {"required": False},
            "car_quantity": {"required": False},
        }


class ProviderOrderSerializer(serializers.ModelSerializer):
    """Serializer for reading provider order data."""

    class Meta:
        model = ProviderOrder
        fields = "__all__"
        read_only_fields = ["status", "total_price", "sale_date"]


class ProviderOrderActionSerializer(serializers.Serializer):
    """Serializer for reject or approve an order."""

    action = serializers.ChoiceField(choices=["reject", "approve"])

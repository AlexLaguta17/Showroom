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


class CarWithPriceSerializer(serializers.ModelSerializer):
    """Serializer for car information with providers and their prices."""

    providers = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = "__all__"

    @staticmethod
    def get_providers(obj):
        """Get all providers that have this car with their prices."""
        provider_cars = obj.providercar_set.all()
        providers_data = []
        for provider_car in provider_cars:
            providers_data.append(
                {
                    "id": provider_car.provider.id,
                    "name": provider_car.provider.name,
                    "price": provider_car.price,
                    "car_quantity": provider_car.car_quantity,
                    "discount": (
                        provider_car.discount.percent if provider_car.discount else None
                    ),
                }
            )
        return providers_data


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = "__all__"


class ProviderCarSerializer(serializers.ModelSerializer):
    car = CarSerializer()

    class Meta:
        model = ProviderCar
        fields = "__all__"


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

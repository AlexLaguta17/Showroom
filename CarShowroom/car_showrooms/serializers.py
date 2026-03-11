"""Serializers for the car_showrooms app."""

from rest_framework import serializers

from services.order_service import validate_showroom_order_creation
from car_showrooms.models import Discount, CarShowroom, ShowroomCar, CarShowroomOrder


class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for the Discount model."""

    class Meta:
        """Discount serializer metadata."""

        model = Discount
        fields = (
            "id",
            "owner_user_id",
            "name",
            "description",
            "date_start",
            "date_end",
            "percent",
        )


class CarShowroomSerializer(serializers.ModelSerializer):
    """Serializer for the CarShowroom model."""

    class Meta:
        """CarShowroom serializer metadata."""

        model = CarShowroom
        fields = "id", "name", "cars", "owner_user_id"
        read_only_fields = "cars", "owner_user_id"

    def validate(self, attrs):
        """Prevent a user from owning more than one showroom."""
        user = self.context["request"].user

        if self.instance is None and CarShowroom.objects.filter(owner_user_id=user.id).exists():
            raise serializers.ValidationError({"detail": "User already has showroom."})

        return attrs


class ShowroomCarSerializer(serializers.ModelSerializer):
    """Serializer for ShowroomCar entries; allows the owner to toggle is_published."""

    class Meta:
        """ShowroomCar serializer metadata."""

        model = ShowroomCar
        fields = "id", "car_quantity", "price", "discount", "car", "is_published"
        read_only_fields = "car", "car_quantity"


class ShowroomOrderSerializer(serializers.ModelSerializer):
    """Serializer for reading CarShowroomOrder data."""

    class Meta:
        """ShowroomOrder read serializer metadata."""

        model = CarShowroomOrder
        fields = "id", "car", "car_buyer", "status", "price", "sale_date"
        read_only_fields = "car_buyer", "status", "price", "sale_date"

    def validate(self, attrs):
        """Validate order creation: car quantity, car price, calculate order price with discount."""
        showroom = self.context["view"].showroom
        showroom_car = attrs["car"]

        price = validate_showroom_order_creation(showroom, showroom_car)
        attrs["price"] = price
        return attrs

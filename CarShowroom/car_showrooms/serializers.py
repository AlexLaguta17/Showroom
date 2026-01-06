from rest_framework import serializers

from car_showrooms.models import (
    Discount,
    CarShowroom,
    ShowroomCar,
    CarShowroomOrder,
)


class CarShowroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarShowroom
        fields = "__all__"


class ShowroomCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowroomCar
        fields = "__all__"


class CarShowroomOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarShowroomOrder
        fields = "__all__"


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = "__all__"


class ProviderOrderCancelSerializer(serializers.Serializer):
    cancel_order = serializers.BooleanField()

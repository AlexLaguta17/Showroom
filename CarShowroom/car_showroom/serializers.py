from rest_framework import serializers

from car_showroom.models import (
    CarShowroom,
    ShowroomCars,
    CarShowroomSalesHistory,
    CarShowroomDiscount,
)


class CarShowroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarShowroom
        fields = "__all__"


class ShowroomCarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowroomCars
        fields = "__all__"


class CarShowroomSalesHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CarShowroomSalesHistory
        fields = "__all__"


class CarShowroomDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarShowroomDiscount
        fields = "__all__"


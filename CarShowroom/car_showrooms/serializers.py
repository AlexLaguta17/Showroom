from rest_framework import serializers

from car_showrooms.models import (
    Discount,
    CarShowroom,
    ShowroomCar,
    CarShowroomOrder,
)


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
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

    class Meta:
        model = CarShowroom
        fields = "id", "name", "cars", "owner_user_id"
        read_only_fields = "cars", "owner_user_id"

    def validate(self, attrs):
        user = self.context["request"].user

        if self.instance is None:
            if CarShowroom.objects.filter(owner_user_id=user.id).exists():
                raise serializers.ValidationError(
                    {"detail": "User already has showroom."}
                )

        return attrs


class ShowroomCarSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShowroomCar
        fields = "id", "car_quantity", "price", "discount", "car"
        read_only_fields = "car", "car_quantity"


class ShowroomOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = CarShowroomOrder
        fields = "id", "car", "car_buyer", "status", "price", "sale_date"


class ShowroomOrderWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = CarShowroomOrder
        fields = "id", "car"


class ProviderOrderCancelSerializer(serializers.Serializer):
    cancel_order = serializers.BooleanField()

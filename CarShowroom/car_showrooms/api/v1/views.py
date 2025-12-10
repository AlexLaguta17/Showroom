from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from car_showrooms.models import Discount, CarShowroom, ShowroomCar, CarShowroomOrder
from car_showrooms.serializers import (
    DiscountSerializer,
    CarShowroomSerializer,
    ShowroomCarSerializer,
    CarShowroomOrderSerializer,
)


class ShowroomViewSet(viewsets.ModelViewSet):
    queryset = CarShowroom.objects.all()
    serializer_class = CarShowroomSerializer

    def get_object(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        return get_object_or_404(self.get_queryset(), pk=showroom_pk)


class ShowroomCarViewSet(viewsets.ModelViewSet):
    serializer_class = ShowroomCarSerializer

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        if showroom_pk is None:
            return ShowroomCar.objects.none()
        return ShowroomCar.objects.filter(showroom_id=showroom_pk)

    def get_object(self):
        car_pk = self.kwargs.get("car_pk")
        return get_object_or_404(self.get_queryset(), pk=car_pk)

    def perform_create(self, serializer):
        showroom_pk = self.kwargs.get("showroom_pk")
        serializer.save(showroom_id=showroom_pk)


class ShowroomDiscountViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountSerializer

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        if showroom_pk is None:
            return Discount.objects.none()
        return Discount.objects.filter(showroomcar__showroom_id=showroom_pk)

    def get_object(self):
        discount_pk = self.kwargs.get("discount_pk")
        return get_object_or_404(self.get_queryset(), pk=discount_pk)

    def perform_create(self, serializer):
        serializer.save()


class CarShowroomOrderViewSet(viewsets.ModelViewSet):
    serializer_class = CarShowroomOrderSerializer

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        if showroom_pk is None:
            return CarShowroomOrder.objects.none()
        return CarShowroomOrder.objects.filter(showroom_id=showroom_pk)

    def get_object(self):
        order_pk = self.kwargs.get("order_pk")
        return get_object_or_404(self.get_queryset(), pk=order_pk)

    def perform_create(self, serializer):
        showroom_pk = self.kwargs.get("showroom_pk")
        serializer.save(showroom_id=showroom_pk)

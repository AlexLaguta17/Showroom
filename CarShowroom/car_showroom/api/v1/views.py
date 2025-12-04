from rest_framework import viewsets

from car_showroom.serializers import (
    CarShowroomSerializer,
    ShowroomCarsSerializer,
    CarShowroomSalesHistorySerializer,
    CarShowroomDiscountSerializer,
)
from car_showroom.models import (
    CarShowroom,
    ShowroomCars,
    CarShowroomSalesHistory,
    CarShowroomDiscount,
)


class CarShowroomViewSet(viewsets.ModelViewSet):
    queryset = CarShowroom.objects.all()
    serializer_class = CarShowroomSerializer


class ShowroomCarsViewSet(viewsets.ModelViewSet):
    queryset = ShowroomCars.objects.all()
    serializer_class = ShowroomCarsSerializer


class CarShowroomSalesHistoryViewSet(viewsets.ModelViewSet):
    queryset = CarShowroomSalesHistory.objects.all()
    serializer_class = CarShowroomSalesHistorySerializer


class CarShowroomDiscountViewSet(viewsets.ModelViewSet):
    queryset = CarShowroomDiscount.objects.all()
    serializer_class = CarShowroomDiscountSerializer

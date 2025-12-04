from rest_framework import viewsets

from dealers.serializers import (
    CarSerializer,
    ProviderSerializer,
    ProviderCarsSerializer,
    ProviderSalesHistorySerializer,
    ProviderDiscountSerializer,
)
from dealers.models import (
    Car,
    Provider,
    ProviderCars,
    ProviderSalesHistory,
    ProviderDiscount,
)


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class ProviderCarsViewSet(viewsets.ModelViewSet):
    queryset = ProviderCars.objects.all()
    serializer_class = ProviderCarsSerializer


class ProviderSalesHistoryViewSet(viewsets.ModelViewSet):
    queryset = ProviderSalesHistory.objects.all()
    serializer_class = ProviderSalesHistorySerializer


class ProviderDiscountViewSet(viewsets.ModelViewSet):
    queryset = ProviderDiscount.objects.all()
    serializer_class = ProviderDiscountSerializer

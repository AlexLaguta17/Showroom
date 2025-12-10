from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from car_showrooms.models import Discount
from car_showrooms.serializers import DiscountSerializer
from dealers.models import Car, Provider, ProviderCar, ProviderOrder
from dealers.serializers import (
    CarSerializer,
    ProviderSerializer,
    ProviderCarSerializer,
    ProviderOrderSerializer,
)


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

    def get_object(self):
        provider_pk = self.kwargs.get("provider_pk")
        return get_object_or_404(self.get_queryset(), pk=provider_pk)


class ProviderCarViewSet(viewsets.ModelViewSet):
    serializer_class = ProviderCarSerializer

    def get_queryset(self):
        provider_pk = self.kwargs.get("provider_pk")
        if provider_pk is None:
            return ProviderCar.objects.none()
        return ProviderCar.objects.filter(provider_id=provider_pk)

    def get_object(self):
        car_pk = self.kwargs.get("car_pk")
        return get_object_or_404(self.get_queryset(), pk=car_pk)

    def perform_create(self, serializer):
        provider_pk = self.kwargs.get("provider_pk")
        serializer.save(provider_id=provider_pk)


class ProviderOrderViewSet(viewsets.ModelViewSet):
    serializer_class = ProviderOrderSerializer

    def get_queryset(self):
        provider_pk = self.kwargs.get("provider_pk")
        if provider_pk is None:
            return ProviderOrder.objects.none()
        return ProviderOrder.objects.filter(provider_id=provider_pk)

    def get_object(self):
        order_pk = self.kwargs.get("order_pk")
        return get_object_or_404(self.get_queryset(), pk=order_pk)

    def perform_create(self, serializer):
        provider_pk = self.kwargs.get("provider_pk")
        serializer.save(provider_id=provider_pk)


class ProviderDiscountViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountSerializer

    def get_queryset(self):
        provider_pk = self.kwargs.get("provider_pk")
        if provider_pk is None:
            return Discount.objects.none()
        return Discount.objects.filter(providercar__provider_id=provider_pk)

    def get_object(self):
        discount_pk = self.kwargs.get("discount_pk")
        return get_object_or_404(self.get_queryset(), pk=discount_pk)

    def perform_create(self, serializer):
        serializer.save()

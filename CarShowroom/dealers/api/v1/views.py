from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, viewsets

from car_showrooms.models import Discount
from dealers.permissions import IsProviderOwner
from car_showrooms.serializers import DiscountSerializer
from dealers.models import Car, Provider, ProviderCar, ProviderOrder
from services.order_service import (
    _reject_order,
    _approve_order,
)
from dealers.serializers import (
    ProviderSerializer,
    ProviderCarSerializer,
    CarWithPriceSerializer,
    ProviderOrderSerializer,
    ProviderOrderActionSerializer,
)


class CarListCreateAPIView(generics.GenericAPIView):
    """API view for managing cars."""

    serializer_class = CarWithPriceSerializer

    def get_queryset(self):
        """Get queryset with prefetched provider data for better performance."""
        return Car.objects.prefetch_related(
            "providercar_set__provider", "providercar_set__discount"
        ).all()

    def get(self, request, *args, **kwargs):
        """List all cars."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Handle POST request to create a new car."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CarDetailAPIView(generics.RetrieveAPIView):
    """API view for managing cars."""

    serializer_class = CarWithPriceSerializer

    def get_queryset(self):
        """Get queryset with prefetched provider data for better performance."""
        return Car.objects.prefetch_related("providercar_set__provider", "providercar_set__discount").all()

    def get_object(self):
        """Retrieve a specific car instance."""
        pk = self.kwargs.get("pk")
        return get_object_or_404(self.get_queryset(), pk=pk)

    def get(self, request, *args, **kwargs):
        """Retrieve detailed information about a specific car."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """Handle PUT request to update a car."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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


class ProviderOrderAPIView(generics.GenericAPIView):
    """List all orders for a provider or retrieve detailed information about a specific provider order."""

    serializer_class = ProviderOrderSerializer
    permission_classes = [IsProviderOwner]

    def get_queryset(self):
        provider_pk = self.kwargs.get("provider_pk")

        if provider_pk is None:
            return ProviderOrder.objects.none()
        return ProviderOrder.objects.filter(provider_id=provider_pk)

    def get_object(self):
        order_pk = self.kwargs.get("pk")
        return get_object_or_404(self.get_queryset(), pk=order_pk)

    def list(self, request, *args, **kwargs):
        """List all orders for a provider."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve detailed information about a specific provider order."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        """Handle GET request - list orders if no pk, retrieve order if pk is provided."""
        pk = kwargs.get("pk")
        if pk is not None:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)


class ProviderOrderActionAPIView(generics.GenericAPIView):
    """Approve or reject a provider order."""

    serializer_class = ProviderOrderActionSerializer
    permission_classes = [IsProviderOwner]

    def get_queryset(self):
        provider_pk = self.kwargs.get("provider_pk")
        if provider_pk is None:
            return ProviderOrder.objects.none()
        return ProviderOrder.objects.filter(provider_id=provider_pk)

    def get_object(self):
        order_pk = self.kwargs.get("order_pk")
        order = get_object_or_404(self.get_queryset(), pk=order_pk)
        self.check_object_permissions(self.request, order)
        return order

    def post(self, request, provider_pk, order_pk):
        """Handle POST request to approve or reject an order."""
        order = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]

        if action == "approve":
            return _approve_order(order)
        elif action == "reject":
            return _reject_order(order)

        return Response(
            {"error": "Invalid action."},
            status=status.HTTP_400_BAD_REQUEST,
        )

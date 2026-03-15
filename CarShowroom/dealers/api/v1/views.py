"""API views for the dealers app."""

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics, permissions

from car_showrooms.models import Discount
from dealers.models import Car, Provider, ProviderCar
from car_showrooms.serializers import DiscountSerializer
from dealers.mixins import ProviderContextMixin, BaseProviderOrderMixin
from services.order_service import (
    cancel_order,
    reject_order,
    complete_order,
    update_provider_order,
)
from dealers.permissions import (
    IsProviderOwner,
    IsShowroomOwnerUser,
    IsOrderShowroomOwner,
    IsProviderOrShowroom,
    IsProviderOwnerOrShowroom,
    IsProviderCarOwnerOrShowroom,
)
from dealers.serializers import (
    CarSerializer,
    ProviderSerializer,
    ProviderCarSerializer,
    ProviderOrderSerializer,
    UpdateProviderCarSerializer,
    ProviderOrderUpdateSerializer,
)


class CarListCreateAPIView(generics.ListCreateAPIView):
    """API view for managing cars."""

    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = (IsAuthenticated, IsProviderOrShowroom)


class CarDetailAPIView(generics.RetrieveUpdateAPIView):
    """API view for managing cars."""

    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = (IsAuthenticated, IsProviderOrShowroom)


class ProviderListCreateAPIView(generics.ListCreateAPIView):
    """List all providers or create a new one."""

    queryset = Provider.objects.all().prefetch_related("cars")
    serializer_class = ProviderSerializer
    permission_classes = (IsAuthenticated, IsProviderOrShowroom)

    def perform_create(self, serializer):
        """Save the provider with the requesting user as owner."""
        serializer.save(owner_user_id=self.request.user.id)


class ProviderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single provider."""

    queryset = Provider.objects.prefetch_related("cars").select_related("owner_user")
    serializer_class = ProviderSerializer
    permission_classes = (
        IsAuthenticated,
        IsProviderOrShowroom,
        IsProviderOwnerOrShowroom,
    )


class ProviderCarListCreateAPIView(ProviderContextMixin, generics.ListCreateAPIView):
    """List a provider's cars or add a new car to the provider's inventory."""

    serializer_class = ProviderCarSerializer

    def get_queryset(self):
        """Return cars belonging to the current provider."""
        return ProviderCar.objects.filter(provider_id=self.provider.id).select_related("car", "discount")

    def get_permissions(self):
        """Return read permissions for safe methods; require provider ownership for mutations."""
        if self.request.method in permissions.SAFE_METHODS:
            return [IsAuthenticated(), IsProviderOrShowroom()]
        else:
            return [IsAuthenticated(), IsProviderOwner()]

    def perform_create(self, serializer):
        """Save the new provider car entry linked to the current provider."""
        serializer.save(provider_id=self.provider.id)


class ProviderCarDetailAPIView(ProviderContextMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single provider car entry."""

    permission_classes = (
        IsAuthenticated,
        IsProviderOrShowroom,
        IsProviderCarOwnerOrShowroom,
    )

    def get_queryset(self):
        """Return cars belonging to the current provider."""
        return ProviderCar.objects.filter(provider_id=self.provider.id).select_related("car", "discount")

    def get_serializer_class(self):
        """Return UpdateProviderCarSerializer for PUT/PATCH; ProviderCarSerializer otherwise."""
        if self.request.method in ("PUT", "PATCH"):
            return UpdateProviderCarSerializer
        return ProviderCarSerializer


class ProviderDiscountListCreateAPIView(ProviderContextMixin, generics.ListCreateAPIView):
    """List a provider's discounts or create a new one."""

    serializer_class = DiscountSerializer
    permission_classes = (IsAuthenticated, IsProviderOrShowroom, IsProviderOwner)

    def get_queryset(self):
        """Return discounts owned by the provider's owner user."""
        return Discount.objects.filter(owner_user_id=self.provider.owner_user_id)

    def perform_create(self, serializer):
        """Save the discount with the requesting user as owner."""
        serializer.save(owner_user_id=self.request.user.id)


class ProviderDiscountDetailAPIView(ProviderContextMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single provider discount."""

    serializer_class = DiscountSerializer
    permission_classes = (
        IsAuthenticated,
        IsProviderOrShowroom,
        IsProviderOwnerOrShowroom,
    )

    def get_queryset(self):
        """Return discounts owned by the provider's owner user."""
        return Discount.objects.filter(owner_user_id=self.provider.owner_user_id)


class ProviderOrderListCreateAPIView(BaseProviderOrderMixin, generics.ListCreateAPIView):
    """List all orders for a provider or create a new one."""

    def get_permissions(self):
        """Require showroom ownership for POST; use base permissions otherwise."""
        if self.request.method == "POST":
            return [IsAuthenticated(), IsShowroomOwnerUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Save the order linked to the current provider and the requesting showroom."""
        serializer.save(
            provider_id=self.provider.id,
            showroom=self.request.user.carshowroom,
        )


class ProviderOrderDetailAPIView(BaseProviderOrderMixin, generics.RetrieveUpdateAPIView):
    """Retrieve or update a single provider order."""

    def get_serializer_class(self):
        """Return ProviderOrderUpdateSerializer for PUT/PATCH; default serializer otherwise."""
        if self.request.method in ("PUT", "PATCH"):
            return ProviderOrderUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """Require showroom ownership for PUT/PATCH; use base permissions otherwise."""
        if self.request.method in ("PUT", "PATCH"):
            return [IsAuthenticated(), IsOrderShowroomOwner()]
        return super().get_permissions()

    def perform_update(self, serializer):
        """Delegate the update to the order service to recalculate price."""
        order = serializer.instance
        provider_car = serializer.validated_data.get("car", order.car)
        car_quantity = serializer.validated_data.get("car_quantity", order.car_quantity)
        update_provider_order(order, provider_car, car_quantity)


class ProviderOrderConfirmAPIView(BaseProviderOrderMixin, generics.GenericAPIView):
    """Provider confirms and completes an order."""

    permission_classes = (IsAuthenticated, IsProviderOwner)

    def post(self, request, *args, **kwargs):
        """Complete the order by transferring funds and updating stock."""
        order = self.get_object()
        complete_order(order)
        return Response({"detail": "Order confirmed successfully."}, status=status.HTTP_200_OK)


class ProviderOrderRejectAPIView(BaseProviderOrderMixin, generics.GenericAPIView):
    """Provider rejects an order."""

    permission_classes = (IsAuthenticated, IsProviderOwner)

    def post(self, request, *args, **kwargs):
        """Mark the order as rejected."""
        order = self.get_object()
        reject_order(order)
        return Response({"detail": "Order rejected successfully."}, status=status.HTTP_200_OK)


class ProviderOrderCancelAPIView(BaseProviderOrderMixin, generics.GenericAPIView):
    """Allow a showroom to cancel their own pending order."""

    permission_classes = (IsAuthenticated, IsOrderShowroomOwner)

    def post(self, request, *args, **kwargs):
        """Mark the order as cancelled."""
        order = self.get_object()
        cancel_order(order)
        return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)

from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated

from car_showrooms.models import Discount
from dealers.mixins import ProviderContextMixin, BaseProviderOrderMixin
from car_showrooms.serializers import DiscountSerializer
from dealers.models import Car, Provider, ProviderCar, ProviderOrder
from services.order_service import (
    _reject_order,
    _approve_order,
)
from dealers.permissions import (
    IsProviderOwner,
    IsProviderOrShowroom,
    IsProviderOwnerOrShowroom,
    IsProviderCarOwnerOrShowroom, IsShowroomOwnerUser, IsProviderOrShowroomOwner,
)
from dealers.serializers import (
    CarSerializer,
    ProviderSerializer,
    ProviderCarSerializer,
    ProviderOrderSerializer,
    UpdateProviderCarSerializer,
    ProviderOrderActionSerializer,
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
    queryset = Provider.objects.all().prefetch_related("cars")
    serializer_class = ProviderSerializer
    permission_classes = (IsAuthenticated, IsProviderOrShowroom)

    def perform_create(self, serializer):
        serializer.save(owner_user_id=self.request.user.id)


class ProviderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Provider.objects.prefetch_related("cars").select_related("owner_user")
    serializer_class = ProviderSerializer
    permission_classes = (
        IsAuthenticated,
        IsProviderOrShowroom,
        IsProviderOwnerOrShowroom,
    )


class ProviderCarListCreateAPIView(ProviderContextMixin, generics.ListCreateAPIView):
    serializer_class = ProviderCarSerializer

    def get_queryset(self):
        return ProviderCar.objects.filter(provider_id=self.provider.id).select_related(
            "car", "discount"
        )

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [IsAuthenticated(), IsProviderOrShowroom()]
        else:
            return [IsAuthenticated(), IsProviderOwner()]

    def perform_create(self, serializer):
        serializer.save(provider_id=self.request.user.provider.id)


class ProviderCarDetailAPIView(
    ProviderContextMixin, generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = (
        IsAuthenticated,
        IsProviderOrShowroom,
        IsProviderCarOwnerOrShowroom,
    )

    def get_queryset(self):
        return ProviderCar.objects.filter(provider_id=self.provider.id).select_related(
            "car", "discount"
        )

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UpdateProviderCarSerializer
        return ProviderCarSerializer


class ProviderDiscountListCreateAPIView(
    ProviderContextMixin, generics.ListCreateAPIView
):
    serializer_class = DiscountSerializer
    permission_classes = (IsAuthenticated, IsProviderOrShowroom, IsProviderOwner)

    def get_queryset(self):
        return Discount.objects.filter(owner_user_id=self.provider.owner_user_id)

    def perform_create(self, serializer):
        serializer.save(owner_user_id=self.request.user.id)


class ProviderDiscountDetailAPIView(
    ProviderContextMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = DiscountSerializer
    permission_classes = (
        IsAuthenticated,
        IsProviderOrShowroom,
        IsProviderOwnerOrShowroom,
    )

    def get_queryset(self):
        return Discount.objects.filter(owner_user_id=self.provider.owner_user_id)


class ProviderOrderListAPIView(BaseProviderOrderMixin, generics.ListAPIView):
    pass


class ProviderOrderDetailAPIView(BaseProviderOrderMixin, generics.RetrieveAPIView):
    pass


class ProviderOrderCreateAPIView(ProviderContextMixin, generics.CreateAPIView):
    queryset = ProviderOrder.objects.all()
    serializer_class = ProviderOrderSerializer
    permission_classes = (IsAuthenticated, IsShowroomOwnerUser)

    def perform_create(self, serializer):
        serializer.save(
            provider_id=self.provider.id,
            showroom=self.request.user.carshowroom,
        )


class ProviderOrderActionAPIView(
    generics.GenericAPIView
):  # TODO: Divide into 2 endpoints: ...order/approve and .../order/reject
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

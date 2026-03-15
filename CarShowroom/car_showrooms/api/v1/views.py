"""API views for the car_showrooms app."""

from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated

from car_showrooms.models import Discount, CarShowroom, ShowroomCar
from car_showrooms.mixins import BaseShowroomOrderMixin, CarShowroomContextMixin
from services.order_service import cancel_order, reject_order, confirm_showroom_order
from car_showrooms.serializers import (
    DiscountSerializer,
    CarShowroomSerializer,
    ShowroomCarSerializer,
    ShowroomOrderSerializer,
)
from car_showrooms.permissions import (
    IsCustomer,
    IsOrderViewer,
    IsDiscountOwner,
    IsOrderCarBuyer,
    IsShowroomOwner,
    IsCarShowroomOwner,
    IsShowroomCarOwner,
)


class ShowroomViewSet(viewsets.ModelViewSet):
    """CRUD operations for car showrooms."""

    queryset = CarShowroom.objects.prefetch_related("cars")
    serializer_class = CarShowroomSerializer
    permission_classes = (IsCarShowroomOwner,)

    def perform_create(self, serializer):
        """Save the showroom with the requesting user as owner."""
        serializer.save(owner_user_id=self.request.user.id)


class ShowroomCarViewSet(CarShowroomContextMixin, viewsets.ModelViewSet):
    """CRUD operations for cars belonging to a showroom."""

    serializer_class = ShowroomCarSerializer
    permission_classes = (IsShowroomCarOwner,)

    def get_queryset(self):
        """Return all cars for the owner; return only published cars with stock for public."""
        queryset = ShowroomCar.objects.filter(showroom_id=self.showroom.id).select_related(
            "car", "discount", "showroom__owner_user"
        )
        user = self.request.user
        if user.is_authenticated and self.showroom.owner_user_id == user.id:
            return queryset
        return queryset.filter(price__gt=0, car_quantity__gt=0, is_published=True)


class ShowroomDiscountViewSet(CarShowroomContextMixin, viewsets.ModelViewSet):
    """CRUD operations for discounts belonging to a showroom."""

    serializer_class = DiscountSerializer
    permission_classes = (IsDiscountOwner,)

    def get_queryset(self):
        """Return discounts owned by the showroom's owner user."""
        return Discount.objects.filter(owner_user_id=self.showroom.owner_user_id)

    def perform_create(self, serializer):
        """Save the discount with the requesting user as owner."""
        serializer.save(owner_user_id=self.request.user.id)


class ShowroomOrderListCreateAPIView(BaseShowroomOrderMixin, generics.ListCreateAPIView):
    """API for listing and creating showroom orders."""

    def get_permissions(self):
        """Allow only customers to create orders; showroom owners and customers can list."""
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomer()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Save the showroom order with the requesting user as car buyer."""
        serializer.save(showroom_id=self.showroom.id, car_buyer_id=self.request.user.id)


class ShowroomOrderDetailAPIView(BaseShowroomOrderMixin, generics.RetrieveAPIView):
    """API for showroom detail orders."""


class ShowroomOrderConfirmAPIView(BaseShowroomOrderMixin, generics.GenericAPIView):
    """Showroom owner confirms and completes a customer order."""

    permission_classes = (IsAuthenticated, IsShowroomOwner)

    def post(self, request, *args, **kwargs):
        """Complete the order by transferring funds and updating stock."""
        order = self.get_object()
        confirm_showroom_order(order)
        return Response({"detail": "Order confirmed successfully."}, status=status.HTTP_200_OK)


class ShowroomOrderRejectAPIView(BaseShowroomOrderMixin, generics.GenericAPIView):
    """Showroom owner rejects a customer order."""

    permission_classes = (IsAuthenticated, IsShowroomOwner)

    def post(self, request, *args, **kwargs):
        """Mark the order as rejected."""
        order = self.get_object()
        reject_order(order)
        return Response({"detail": "Order rejected successfully."}, status=status.HTTP_200_OK)


class ShowroomOrderCancelAPIView(BaseShowroomOrderMixin, generics.GenericAPIView):
    """Allow a customer to cancel their own pending showroom order."""

    permission_classes = (IsAuthenticated, IsOrderCarBuyer)

    def post(self, request, *args, **kwargs):
        """Mark the order as cancelled."""
        order = self.get_object()
        cancel_order(order)
        return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)

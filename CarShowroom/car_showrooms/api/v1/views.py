"""API views for the car_showrooms app."""

from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from car_showrooms.models import Discount, CarShowroom, ShowroomCar
from car_showrooms.mixins import BaseShowroomOrderMixin, CarShowroomContextMixin
from car_showrooms.permissions import (
    IsCustomer,
    IsDiscountOwner,
    IsCarShowroomOwner,
    IsShowroomCarOwner,
)
from car_showrooms.serializers import (
    DiscountSerializer,
    CarShowroomSerializer,
    ShowroomCarSerializer,
    ShowroomOrderSerializer,
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


class ShowroomOrderListAPIView(BaseShowroomOrderMixin, generics.ListAPIView):
    """API for showroom list orders."""


class ShowroomOrderDetailAPIView(BaseShowroomOrderMixin, generics.RetrieveAPIView):
    """API for showroom detail orders."""


class ShowroomOrderCreateAPIView(CarShowroomContextMixin, generics.CreateAPIView):
    """API for creating showroom orders. Only UserType.CUSTOMER can create orders."""

    serializer_class = ShowroomOrderSerializer
    permission_classes = (IsAuthenticated, IsCustomer)

    def perform_create(self, serializer):
        """Save the showroom order with the requesting user as car buyer."""
        serializer.save(showroom_id=self.showroom.id, car_buyer_id=self.request.user.id)

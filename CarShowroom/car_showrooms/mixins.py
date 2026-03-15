"""Mixins for the car_showrooms app views."""

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from services.choices import UserType
from car_showrooms.permissions import IsOrderViewer
from car_showrooms.serializers import ShowroomOrderSerializer
from car_showrooms.models import CarShowroom, CarShowroomOrder


class CarShowroomContextMixin:
    """Resolve and cache the CarShowroom instance from the URL keyword argument."""

    @property
    def showroom(self):
        """Return the CarShowroom identified by ``showroom_pk`` in the URL kwargs."""
        if not hasattr(self, "_showroom"):
            self._showroom = get_object_or_404(CarShowroom, pk=self.kwargs["showroom_pk"])
        return self._showroom


class BaseShowroomOrderMixin(CarShowroomContextMixin):
    """Base mixin for showroom order views: queryset, serializer, and permissions."""

    serializer_class = ShowroomOrderSerializer
    permission_classes = (IsAuthenticated, IsOrderViewer)

    def get_queryset(self):
        """Return orders for the current showroom; scope to the requesting customer's own orders if applicable."""
        queryset = CarShowroomOrder.objects.filter(showroom_id=self.showroom.id).select_related(
            "car_buyer", "showroom", "car"
        )

        user = self.request.user
        if user.type == UserType.CUSTOMER:
            queryset = queryset.filter(car_buyer_id=user.id)
        elif self.showroom.owner_user_id != user.id:
            return queryset.none()

        return queryset

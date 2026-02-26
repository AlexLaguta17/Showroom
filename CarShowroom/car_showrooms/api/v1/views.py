from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework import status, generics, viewsets
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError

from dealers.models import Provider, ProviderOrder
from services.choices import UserType, OrderStatus
from car_showrooms.mixins import CarShowroomContextMixin
from car_showrooms.models import Discount, CarShowroom, ShowroomCar, CarShowroomOrder
from car_showrooms.permissions import (
    IsOrderViewer,
    IsDiscountOwner,
    IsCarShowroomOwner,
    IsShowroomCarOwner,
)
from car_showrooms.serializers import (
    DiscountSerializer,
    CarShowroomSerializer,
    ShowroomCarSerializer,
    ShowroomOrderSerializer,
    ShowroomOrderWriteSerializer,
    ProviderOrderCancelSerializer,
)


class ShowroomViewSet(viewsets.ModelViewSet):
    queryset = CarShowroom.objects.prefetch_related("cars")
    serializer_class = CarShowroomSerializer
    permission_classes = (IsCarShowroomOwner,)

    def perform_create(self, serializer):
        serializer.save(owner_user_id=self.request.user.id)


class ShowroomCarViewSet(CarShowroomContextMixin, viewsets.ModelViewSet):
    serializer_class = ShowroomCarSerializer
    permission_classes = (IsShowroomCarOwner,)

    def get_queryset(self):
        queryset = ShowroomCar.objects.filter(showroom_id=self.showroom.id).select_related(
            "car", "discount", "showroom__owner_user"
        )
        user = self.request.user
        if user.is_authenticated and self.showroom.owner_user.id == user.id:
            return queryset
        return queryset.filter(price__gt=0, car_quantity__gt=0, is_published=True)


class ShowroomDiscountViewSet(CarShowroomContextMixin, viewsets.ModelViewSet):
    serializer_class = DiscountSerializer
    permission_classes = (IsDiscountOwner,)

    def get_queryset(self):
        return Discount.objects.filter(owner_user_id=self.showroom.owner_user.id)

    def perform_create(self, serializer):
        serializer.save(owner_user_id=self.request.user.id)


class CarShowroomOrderViewSet(viewsets.ModelViewSet):  # TODO Rewrite
    permission_classes = (IsAuthenticated, IsOrderViewer)

    def get_serializer_class(self):
        if self.action == "create":
            return ShowroomOrderWriteSerializer
        return ShowroomOrderSerializer

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        user = self.request.user
        qs = CarShowroomOrder.objects.filter(showroom_id=showroom_pk).select_related("car")

        if user.type == UserType.CUSTOMER:
            return qs.filter(car_buyer_id=user.id)

        if user.type == UserType.SHOWROOM:
            return qs.filter(showroom__owner_user_id=user.id)
        return CarShowroomOrder.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.type != UserType.CUSTOMER:
            raise PermissionDenied("Only customers can create orders")
        # TODO calculate price with discount and check car's owner (May be in other View with business logic)
        serializer.save(
            showroom_id=self.kwargs["showroom_pk"],
            price=1500,
            car_buyer_id=user.id,
            status=OrderStatus.PENDING,
        )

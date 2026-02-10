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
from services.order_service import (
    update_provider_order,
    validate_order_status,
    validate_order_creation,
)
from car_showrooms.permissions import (
    IsOrderViewer,
    IsDiscountOwner,
    IsCarShowroomOwner,
    IsShowroomCarOwner,
)
from dealers.serializers import (
    ProviderOrderSerializer,
    ProviderOrderCreateSerializer,
    ProviderOrderUpdateSerializer,
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
        queryset = ShowroomCar.objects.filter(
            showroom_id=self.showroom.id
        ).select_related("car", "discount", "showroom__owner_user")
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
        qs = CarShowroomOrder.objects.filter(showroom_id=showroom_pk).select_related(
            "car"
        )

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


class ShowroomProviderOrderDetailAPIView(generics.GenericAPIView):  # TODO Rewrite
    """Retrieve or update a specific provider order for a showroom."""

    permission_classes = [IsCarShowroomOwner]
    serializer_class = ProviderOrderSerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == "PUT":
            return ProviderOrderUpdateSerializer
        return ProviderOrderSerializer

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        if showroom_pk is None:
            return ProviderOrder.objects.none()
        return ProviderOrder.objects.filter(showroom_id=showroom_pk)

    def get_object(self):
        order_pk = self.kwargs.get("order_pk")
        order = get_object_or_404(self.get_queryset(), pk=order_pk)
        self.check_object_permissions(self.request, order)
        return order

    def get(self, request, *args, **kwargs):
        """Retrieve detailed information about a specific provider order."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """Update a provider order.
        Showroom can change only car_quantity or/and car.
        """
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        car = serializer.validated_data.get("car", instance.car)
        car_quantity = serializer.validated_data.get(
            "car_quantity", instance.car_quantity
        )

        try:
            update_provider_order(instance, car, car_quantity)
        except ValidationError as e:
            raise DRFValidationError({"error": str(e)})

        instance.refresh_from_db()

        return Response(
            {
                "car": instance.car.id,
                "order_status": instance.status,
                "quantity": instance.car_quantity,
                "total_price": instance.total_price,
                "provider": instance.provider.id,
                "message": "Order updated successfully",
            },
            status=status.HTTP_200_OK,
        )


class ShowroomProviderOrderListCreateAPIView(generics.GenericAPIView):
    """List all provider orders for a showroom or create a new provider order."""

    permission_classes = [IsCarShowroomOwner]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProviderOrderCreateSerializer
        return ProviderOrderSerializer

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        if showroom_pk is None:
            return ProviderOrder.objects.none()
        return ProviderOrder.objects.filter(showroom_id=showroom_pk)

    def get_showroom(self):
        """Get showroom object and check permissions."""
        showroom_pk = self.kwargs.get("showroom_pk")
        showroom = get_object_or_404(CarShowroom, pk=showroom_pk)
        self.check_object_permissions(self.request, showroom)
        return showroom

    def get(self, request, *args, **kwargs):
        """List all provider orders for a showroom."""
        self.get_showroom()

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Handle POST request to create a new provider order."""
        showroom = self.get_showroom()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider_id = serializer.validated_data["provider_id"]
        car_id = serializer.validated_data["car_id"]
        car_quantity = serializer.validated_data["car_quantity"]

        provider = get_object_or_404(Provider, pk=provider_id)

        try:
            total_price = validate_order_creation(
                provider=provider, car_id=car_id, car_quantity=car_quantity
            )
        except ValidationError as e:
            raise DRFValidationError({"error": str(e)})

        order = serializer.save(
            provider=provider,
            showroom=showroom,
            car_id=car_id,
            total_price=total_price,
            order_status="Pending",
        )

        response_serializer = ProviderOrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ShowroomProviderOrderCancelAPIView(generics.GenericAPIView):
    """Cancel a showroom provider order."""

    serializer_class = ProviderOrderCancelSerializer
    permission_classes = [IsCarShowroomOwner]

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        if showroom_pk is None:
            return ProviderOrder.objects.none()
        return ProviderOrder.objects.filter(showroom_id=showroom_pk)

    def get_object(self):
        order_pk = self.kwargs.get("order_pk")
        order = get_object_or_404(self.get_queryset(), pk=order_pk)
        self.check_object_permissions(self.request, order)
        return order

    def post(self, request, showroom_pk, order_pk):
        """Handle POST request to cancel an order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["cancel_order"]:
            order = self.get_object()

            try:
                validate_order_status(order, "Pending")
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            order.status = "Cancelled"
            order.save()

            return Response(
                {
                    "id": order.id,
                    "order_status": order.status,
                    "message": "Order cancelled successfully",
                },
                status=status.HTTP_200_OK,
            )

        return redirect(
            "showroom-provider-order-detail", showroom_pk=showroom_pk, order_pk=order_pk
        )

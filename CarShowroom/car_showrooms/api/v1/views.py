from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.core.serializers import get_serializer
from rest_framework import status, generics, viewsets
from django.shortcuts import redirect, get_object_or_404
from rest_framework.exceptions import ValidationError as DRFValidationError

from dealers.models import Provider, ProviderOrder
from car_showrooms.permissions import IsShowroomOwner
from car_showrooms.models import Discount, CarShowroom, ShowroomCar, CarShowroomOrder
from services.order_service import (
    update_provider_order,
    validate_order_status,
    validate_order_creation,
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
    CarShowroomOrderSerializer,
    ProviderOrderCancelSerializer,
)


class ShowroomViewSet(viewsets.ModelViewSet):
    queryset = CarShowroom.objects.all()
    serializer_class = CarShowroomSerializer

    def get_object(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        return get_object_or_404(self.get_queryset(), pk=showroom_pk)


class ShowroomCarViewSet(viewsets.ModelViewSet):
    serializer_class = ShowroomCarSerializer

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        if showroom_pk is None:
            return ShowroomCar.objects.none()
        return ShowroomCar.objects.filter(showroom_id=showroom_pk)

    def get_object(self):
        car_pk = self.kwargs.get("car_pk")
        return get_object_or_404(self.get_queryset(), pk=car_pk)

    def perform_create(self, serializer):
        showroom_pk = self.kwargs.get("showroom_pk")
        serializer.save(showroom_id=showroom_pk)


class ShowroomDiscountViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountSerializer

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        if showroom_pk is None:
            return Discount.objects.none()
        return Discount.objects.filter(showroomcar__showroom_id=showroom_pk)

    def get_object(self):
        discount_pk = self.kwargs.get("discount_pk")
        return get_object_or_404(self.get_queryset(), pk=discount_pk)

    def perform_create(self, serializer):
        serializer.save()


class CarShowroomOrderViewSet(viewsets.ModelViewSet):
    serializer_class = CarShowroomOrderSerializer

    def get_queryset(self):
        showroom_pk = self.kwargs.get("showroom_pk")
        if showroom_pk is None:
            return CarShowroomOrder.objects.none()
        return CarShowroomOrder.objects.filter(showroom_id=showroom_pk)

    def get_object(self):
        order_pk = self.kwargs.get("order_pk")
        return get_object_or_404(self.get_queryset(), pk=order_pk)

    def perform_create(self, serializer):
        showroom_pk = self.kwargs.get("showroom_pk")
        serializer.save(showroom_id=showroom_pk)


class ShowroomProviderOrderDetailAPIView(generics.GenericAPIView):
    """Retrieve or update a specific provider order for a showroom."""

    permission_classes = [IsShowroomOwner]
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

    permission_classes = [IsShowroomOwner]

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
    permission_classes = [IsShowroomOwner]

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

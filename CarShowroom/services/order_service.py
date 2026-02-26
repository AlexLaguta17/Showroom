"""
Business logic for order processing.

This module contains all business logic related to provider orders,
including price calculation, order validation, and order completion.
"""

from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError

from users.models import User
from services.choices import OrderStatus
from car_showrooms.models import CarShowroom, ShowroomCar
from dealers.models import Provider, ProviderCar, ProviderOrder


def calculate_order_price(provider_car: ProviderCar, car_quantity: int) -> Decimal:
    """Calculate total order price with discount applied."""
    if provider_car.price is None:
        raise DRFValidationError("ProviderCar price must be set")

    unit_price = provider_car.price
    discount_percent = Decimal("0")

    if provider_car.discount:
        discount_percent = provider_car.discount.percent

    discounted_unit_price = unit_price * (1 - discount_percent / Decimal("100"))
    total_price = discounted_unit_price * car_quantity

    return total_price.quantize(Decimal("0.01"))


def validate_car_quantity(provider_car: ProviderCar, order_car_quantity: int) -> None:
    """Validate that provider has sufficient quantity of cars."""
    if provider_car.car_quantity < order_car_quantity:
        raise DRFValidationError({"detail": "Provider doesn't have sufficient quantity of cars"})


def validate_balance(user: User, total_price: Decimal) -> None:
    """Validate that user has sufficient balance."""
    if user.balance < total_price:
        raise DRFValidationError({"detail": "You don't have enough balance to order"})


def validate_car_provider(provider_car: ProviderCar, provider: Provider) -> None:
    """Validate that provider actually has this provider_car"""
    if provider_car.provider.id != provider.id:
        raise DRFValidationError(
            {
                "detail": f"Car {provider_car.car.brand} {provider_car.car.model} "
                f"does not belong to the provider {provider.name}"
            }
        )


def validate_order_status(order: ProviderOrder, expected_status: OrderStatus) -> None:
    """Validate that order has the expected status."""
    if order.status != expected_status:
        raise DRFValidationError(f"Order is not in {expected_status} status")


def validate_order_creation(provider_car: ProviderCar, car_quantity: int, provider: Provider) -> Decimal:
    """Validate order creation requirements and calculate total price."""

    validate_car_provider(provider_car, provider)
    validate_car_quantity(provider_car, car_quantity)
    total_price = calculate_order_price(provider_car, car_quantity)

    return total_price


def complete_order(order: ProviderOrder) -> None:
    """Complete an order: transfer money, update inventories, change status."""
    from django.db import transaction

    validate_order_status(order, OrderStatus.PENDING)

    provider = order.provider
    showroom = order.showroom
    provider_car = order.car

    validate_car_quantity(provider_car, order.car_quantity)
    validate_balance(showroom.owner_user, order.total_price)

    with transaction.atomic():
        showroom.owner_user.balance -= order.total_price
        showroom.owner_user.save()

        provider.owner_user.balance += order.total_price
        provider.owner_user.save()

        provider_car.car_quantity -= order.car_quantity
        provider_car.save()

        showroom_car, created = ShowroomCar.objects.get_or_create(
            showroom=showroom, car=order.car, defaults={"car_quantity": 0, "price": 0}
        )
        showroom_car.car_quantity += order.car_quantity
        showroom_car.save()

        order.status = OrderStatus.COMPLETED
        order.save()


def approve_order(order: ProviderOrder) -> Response:  # TODO: Rename
    """Approve and complete an order."""
    try:
        complete_order(order)

        return Response(  # TODO rewrite without Response
            {
                "id": order.id,
                "order_status": order.status,
                "message": "Order approved and completed successfully",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def reject_order(order: ProviderOrder) -> Response:  # TODO Rename
    """Reject an order."""
    try:
        validate_order_status(order, OrderStatus.PENDING)
    except DRFValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  # TODO rewrite without Response

    order.status = OrderStatus.REJECTED
    order.save()

    return Response(
        {
            "id": order.id,
            "order_status": order.status,
            "message": "Order rejected successfully",
        },
        status=status.HTTP_200_OK,
    )


def update_provider_order(order: ProviderOrder, provider_car: ProviderCar, car_quantity: int) -> None:
    """Update a provider order with new car and/or quantity."""
    validate_order_status(order, OrderStatus.PENDING)

    if provider_car != order.car or car_quantity != order.car_quantity:
        total_price = validate_order_creation(
            provider_car,
            car_quantity,
            order.provider,
        )

        order.car = provider_car
        order.car_quantity = car_quantity
        order.total_price = total_price
        order.save()

"""
Business logic for order processing.

This module contains all business logic related to provider orders,
including price calculation, order validation, and order completion.
"""

from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from car_showrooms.models import CarShowroom, ShowroomCar
from dealers.models import Provider, ProviderCar, ProviderOrder


def calculate_order_price(provider_car: ProviderCar, car_quantity: int) -> Decimal:
    """Calculate total order price with discount applied."""
    if provider_car.price is None:
        raise ValidationError("ProviderCar price must be set")

    unit_price = provider_car.price
    discount_percent = Decimal("0")

    if provider_car.discount:
        discount_percent = provider_car.discount.percent

    discounted_unit_price = unit_price * (1 - discount_percent / Decimal("100"))
    total_price = discounted_unit_price * car_quantity

    return total_price.quantize(Decimal("0.01"))


def validate_car_quantity(provider_car: ProviderCar, car_quantity: int) -> None:
    """Validate that provider has sufficient quantity of cars."""
    if provider_car.car_quantity < car_quantity:
        raise ValidationError("Insufficient car quantity")


def validate_balance(user_balance: Decimal, required_amount: Decimal) -> None:
    """Validate that user has sufficient balance."""
    if user_balance < required_amount:
        raise ValidationError("Insufficient balance")


def validate_order_status(order: ProviderOrder, expected_status: str = "Pending") -> None:
    """Validate that order has the expected status."""
    if order.status != expected_status:
        raise ValidationError(f"Order is not in {expected_status} status")


def validate_order_creation(provider: Provider, car_id: int, car_quantity: int) -> Decimal:
    """Validate order creation requirements and calculate total price."""
    from django.shortcuts import get_object_or_404

    provider_car = get_object_or_404(ProviderCar, provider=provider, car_id=car_id)

    validate_car_quantity(provider_car, car_quantity)

    if provider_car.price is None:
        raise ValidationError("ProviderCar price must be set")

    total_price = calculate_order_price(provider_car, car_quantity)

    return total_price


def complete_order(order: ProviderOrder) -> None:
    """Complete an order: transfer money, update inventories, change status."""
    from django.db import transaction
    from django.shortcuts import get_object_or_404

    validate_order_status(order, "Pending")

    provider = order.provider
    showroom = order.showroom

    provider_car = get_object_or_404(ProviderCar, provider=provider, car=order.car)

    validate_car_quantity(provider_car, order.car_quantity)
    validate_balance(showroom.owner_user.balance, order.total_price)

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

        order.status = "Completed"
        order.save()


def _approve_order(order: ProviderOrder) -> Response:
    """Approve and complete an order."""
    try:
        complete_order(order)

        return Response(
            {
                "id": order.id,
                "order_status": order.status,
                "message": "Order approved and completed successfully",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def _reject_order(order: ProviderOrder) -> Response:
    """Reject an order."""
    try:
        validate_order_status(order, "Pending")
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    order.status = "Rejected"
    order.save()

    return Response(
        {
            "id": order.id,
            "order_status": order.status,
            "message": "Order rejected successfully",
        },
        status=status.HTTP_200_OK,
    )


def update_provider_order(order: ProviderOrder, car, car_quantity: int) -> None:
    """Update a provider order with new car and/or quantity."""
    validate_order_status(order, "Pending")

    if car != order.car or car_quantity != order.car_quantity:
        total_price = validate_order_creation(
            provider=order.provider,
            car_id=car.id,
            car_quantity=car_quantity,
        )

        order.car = car
        order.car_quantity = car_quantity
        order.total_price = total_price
        order.save()

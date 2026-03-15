"""
Business logic for order processing.

This module contains all business logic related to provider orders,
including price calculation, order validation, and order completion.
"""

from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError as DRFValidationError

from users.models import User
from services.choices import OrderStatus
from car_showrooms.models import ShowroomCar
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
    """Validate that provider actually has this provider_car."""
    if provider_car.provider.id != provider.id:
        raise DRFValidationError(
            {
                "detail": f"Car {provider_car.car.brand} {provider_car.car.model} "
                f"does not belong to the provider {provider.name}"
            }
        )


def validate_order_status(order: ProviderOrder, *expected_statuses: OrderStatus) -> None:
    """Validate that order has the expected status."""
    if order.status not in expected_statuses:
        allowed = ", ".join(str(expected_status) for expected_status in expected_statuses)
        raise DRFValidationError(f"Order status must be: {allowed}")


def validate_order_creation(provider_car: ProviderCar, car_quantity: int, provider: Provider) -> Decimal:
    """Validate order creation requirements and calculate total price."""
    validate_car_provider(provider_car, provider)
    validate_car_quantity(provider_car, car_quantity)
    total_price = calculate_order_price(provider_car, car_quantity)

    return total_price


def complete_order(order: ProviderOrder) -> None:
    """Complete an order: transfer money, update inventories, change status."""
    validate_order_status(order, OrderStatus.PENDING)

    with transaction.atomic():
        order = ProviderOrder.objects.select_for_update().get(pk=order.pk)
        validate_order_status(order, OrderStatus.PENDING)

        provider = order.provider
        showroom = order.showroom
        provider_car = ProviderCar.objects.select_for_update().get(pk=order.car_id)
        showroom_owner = User.objects.select_for_update().get(pk=showroom.owner_user_id)
        provider_owner = User.objects.select_for_update().get(pk=provider.owner_user_id)

        validate_car_quantity(provider_car, order.car_quantity)
        validate_balance(showroom_owner, order.total_price)

        showroom_owner.balance -= order.total_price
        showroom_owner.save()

        provider_owner.balance += order.total_price
        provider_owner.save()

        provider_car.car_quantity -= order.car_quantity
        provider_car.save()

        showroom_car, created = ShowroomCar.objects.get_or_create(
            showroom=showroom, car=provider_car.car, defaults={"car_quantity": 0, "price": 0}
        )
        showroom_car.car_quantity += order.car_quantity
        showroom_car.save()

        order.status = OrderStatus.COMPLETED
        order.save()


def reject_order(order: ProviderOrder) -> None:
    """Reject an order (provider action)."""
    with transaction.atomic():
        order = ProviderOrder.objects.select_for_update().get(pk=order.pk)
        validate_order_status(order, OrderStatus.PENDING)
        order.status = OrderStatus.REJECTED
        order.save()


def cancel_order(order: ProviderOrder) -> None:
    """Cancel an order (showroom action)."""
    with transaction.atomic():
        order = ProviderOrder.objects.select_for_update().get(pk=order.pk)
        validate_order_status(order, OrderStatus.PENDING)
        order.status = OrderStatus.CANCELLED
        order.save()


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

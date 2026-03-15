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
from dealers.models import Provider, ProviderCar, ProviderOrder
from car_showrooms.models import CarShowroom, ShowroomCar, CarShowroomOrder


def check_car_order_price(car: ProviderCar | ShowroomCar) -> None:
    """Check if car order price is correct."""
    if car.price == Decimal("0.0"):
        raise DRFValidationError({"detail": "This car is not for sale yet"})


def calculate_order_price(provider_car: ProviderCar, car_quantity: int) -> Decimal:
    """Calculate total provider order price with discount applied."""
    check_car_order_price(provider_car)

    unit_price = provider_car.price
    discount_percent = Decimal("0")

    if provider_car.discount:
        discount_percent = provider_car.discount.percent

    discounted_unit_price = unit_price * (1 - discount_percent / Decimal("100"))
    total_price = discounted_unit_price * car_quantity

    return total_price.quantize(Decimal("0.01"))


def calculate_price_with_discount(showroom_car: ShowroomCar) -> Decimal:
    """Calculate total showroom order price with discount applied."""
    check_car_order_price(showroom_car)

    discount_percent = Decimal("0")

    if showroom_car.discount:
        discount_percent = showroom_car.discount.percent

    price_with_discount = showroom_car.price * (1 - discount_percent / Decimal("100"))

    return price_with_discount.quantize(Decimal("0.01"))


def validate_car_quantity(provider_car: ProviderCar, order_car_quantity: int) -> None:
    """Validate that provider has sufficient quantity of cars."""
    if provider_car.car_quantity < order_car_quantity:
        raise DRFValidationError({"detail": "Provider doesn't have sufficient quantity of cars"})


def validate_balance(user: User, total_price: Decimal) -> None:
    """Validate that user has sufficient balance."""
    if user.balance < total_price:
        raise DRFValidationError({"detail": "Car buyer doesn't have sufficient balance"})


def validate_car_provider(provider_car: ProviderCar, provider: Provider) -> None:
    """Validate that provider actually has this provider_car."""
    if provider_car.provider.id != provider.id:
        raise DRFValidationError(
            {
                "detail": f"Car {provider_car.car.brand} {provider_car.car.model} "
                f"does not belong to the provider {provider.name}"
            }
        )


def validate_car_showroom(showroom_car: ShowroomCar, showroom: CarShowroom) -> None:
    """Validate that showroom actually has this showroom_car."""
    if not showroom_car.is_published or showroom_car.car_quantity < 1:
        raise DRFValidationError({"detail": "This car is not for sale"})

    if showroom_car.showroom.id != showroom.id:
        raise DRFValidationError(
            {
                "detail": f"Car {showroom_car.car.brand} {showroom_car.car.model} "
                f"does not belong to the car showroom {showroom.name}"
            }
        )

    if showroom_car.car_quantity < 1:
        raise DRFValidationError({"detail": "Showroom doesn't have sufficient quantity of cars"})


def validate_order_status(order: ProviderOrder | CarShowroomOrder, *expected_statuses: OrderStatus) -> None:
    """Validate that order has the expected status."""
    if order.status not in expected_statuses:
        allowed = ", ".join(str(expected_status) for expected_status in expected_statuses)
        raise DRFValidationError({"detail": f"Order status must be: {allowed}"})


def validate_provider_order_creation(provider_car: ProviderCar, car_quantity: int, provider: Provider) -> Decimal:
    """Validate order creation requirements and calculate total price."""
    validate_car_provider(provider_car, provider)
    validate_car_quantity(provider_car, car_quantity)
    total_price = calculate_order_price(provider_car, car_quantity)

    return total_price


def validate_showroom_order_creation(showroom: CarShowroom, showroom_car: ShowroomCar) -> Decimal:
    """Validate order creation requirements and calculate price with discount."""
    validate_car_showroom(showroom_car, showroom)
    price_with_discount = calculate_price_with_discount(showroom_car)

    return price_with_discount


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


def change_order_status(order: CarShowroomOrder | ProviderOrder, new_status: OrderStatus) -> None:
    """Service function for changing order status."""
    with transaction.atomic():
        order = order.__class__.objects.select_for_update().get(pk=order.pk)
        validate_order_status(order, OrderStatus.PENDING)
        order.status = new_status
        order.save(update_fields=["status"])


def reject_order(order: ProviderOrder | CarShowroomOrder) -> None:
    """Reject an order (provider action)."""
    change_order_status(order, OrderStatus.REJECTED)


def cancel_order(order: ProviderOrder | CarShowroomOrder) -> None:
    """Cancel an order (showroom action)."""
    change_order_status(order, OrderStatus.CANCELLED)


def confirm_showroom_order(order: CarShowroomOrder) -> None:
    """Confirm a showroom order: transfer funds, decrement inventory, set status COMPLETED."""
    with transaction.atomic():
        order = CarShowroomOrder.objects.select_for_update().get(pk=order.pk)
        validate_order_status(order, OrderStatus.PENDING)

        showroom = order.showroom
        showroom_car = ShowroomCar.objects.select_for_update().get(pk=order.car_id)
        customer = User.objects.select_for_update().get(pk=order.car_buyer_id)
        showroom_owner = User.objects.select_for_update().get(pk=showroom.owner_user_id)

        validate_car_showroom(showroom_car, showroom)
        validate_balance(customer, order.price)

        customer.balance -= order.price
        customer.save()
        showroom_owner.balance += order.price
        showroom_owner.save()
        showroom_car.car_quantity -= 1
        showroom_car.save()
        order.status = OrderStatus.COMPLETED
        order.save(update_fields=["status"])


def update_provider_order(order: ProviderOrder, provider_car: ProviderCar, car_quantity: int) -> None:
    """Update a provider order with new car and/or quantity."""
    validate_order_status(order, OrderStatus.PENDING)

    if provider_car != order.car or car_quantity != order.car_quantity:
        total_price = validate_provider_order_creation(
            provider_car,
            car_quantity,
            order.provider,
        )

        order.car = provider_car
        order.car_quantity = car_quantity
        order.total_price = total_price
        order.save()

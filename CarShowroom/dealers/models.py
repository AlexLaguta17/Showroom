"""Models for the dealers app: Car, Provider, ProviderCar, ProviderOrder."""

from datetime import date

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from services.choices import (
    BodyType,
    UserType,
    EngineType,
    OrderStatus,
    TransmissionType,
)


class Car(models.Model):
    """Model describing a car with its technical characteristics."""

    engine_type = models.CharField(choices=EngineType.choices, max_length=8, default=EngineType.GASOLINE)
    transmission_type = models.CharField(choices=TransmissionType.choices, max_length=9, default=TransmissionType.MANUAL)
    body_type = models.CharField(choices=BodyType.choices, max_length=9, default=BodyType.SEDAN)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(date.today().year),
        ]
    )
    color = models.CharField(null=True, max_length=30)
    engine_volume = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0)], default=0)

    def __str__(self):
        """Return a string identifying the car by brand and model."""
        return f"{self.brand}-{self.model}"


class Provider(models.Model):
    """Model representing a car provider."""

    name = models.CharField(max_length=100)
    year_founded = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1800),
            MaxValueValidator(date.today().year),
        ],
        null=True,
        blank=True,
    )
    cars = models.ManyToManyField("Car", through="ProviderCar")
    owner_user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        limit_choices_to={"type": UserType.PROVIDER},
    )

    def __str__(self):
        """Return the provider name."""
        return self.name


class ProviderCar(models.Model):
    """Model of a provider's cars available for selling."""

    car = models.ForeignKey("Car", on_delete=models.CASCADE)
    provider = models.ForeignKey("Provider", on_delete=models.CASCADE)
    discount = models.ForeignKey("car_showrooms.Discount", on_delete=models.SET_NULL, blank=True, null=True)
    car_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
    )

    def __str__(self):
        """Return a string identifying this provider car entry."""
        return f"{self.provider}'s car: {self.car}"


class ProviderOrder(models.Model):
    """Model of showroom orders addressed to providers."""

    provider = models.ForeignKey("Provider", on_delete=models.CASCADE)
    showroom = models.ForeignKey("car_showrooms.CarShowroom", on_delete=models.CASCADE)
    car = models.ForeignKey("dealers.ProviderCar", on_delete=models.CASCADE)
    status = models.CharField(choices=OrderStatus.choices, max_length=9, default=OrderStatus.PENDING)
    car_quantity = models.PositiveIntegerField(default=1)
    sale_date = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        """Return a string describing the order's showroom, car, quantity and status."""
        return f"{self.showroom} order: {self.car}, quantity: {self.car_quantity}, status: {self.status}"

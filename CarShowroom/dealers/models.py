from datetime import date

from django.db import models
from djmoney.models.fields import MoneyField
from django_countries.fields import CountryField
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User
from services.choices import (
    BodyType,
    UserType,
    EngineType,
    OrderStatus,
    TransmissionType,
)


class Car(models.Model):
    """Model for description car"""

    engine_type = models.CharField(
        choices=EngineType.choices, max_length=8, default=EngineType.GASOLINE
    )
    transmission_type = models.CharField(
        choices=TransmissionType.choices, max_length=9, default=TransmissionType.MANUAL
    )
    body_type = models.CharField(
        choices=BodyType.choices, max_length=9, default=BodyType.SEDAN
    )
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(date.today().year),
        ]
    )
    color = models.CharField(null=True, max_length=30)
    engine_volume = models.DecimalField(
        max_digits=3, decimal_places=1, validators=[MinValueValidator(0.0)], default=0.0
    )

    def __str__(self):
        return f"{self.brand}-{self.model}"


class Provider(models.Model):
    """Provider model"""

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
        return f"{self.name}"


class ProviderCar(models.Model):
    """Model of provider's cars for selling"""

    car = models.ForeignKey("Car", on_delete=models.CASCADE)
    provider = models.ForeignKey("Provider", on_delete=models.CASCADE)
    discount = models.ForeignKey(
        "car_showrooms.Discount", on_delete=models.SET_NULL, blank=True, null=True
    )
    car_quantity = models.IntegerField(default=0)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.provider}'s car: {self.car}"


class ProviderOrder(models.Model):
    """Model of orders to showrooms"""

    provider = models.ForeignKey("Provider", on_delete=models.CASCADE)
    showroom = models.ForeignKey("car_showrooms.CarShowroom", on_delete=models.CASCADE)
    car = models.ForeignKey("dealers.Car", on_delete=models.CASCADE)
    status = models.CharField(
        choices=OrderStatus.choices, max_length=9, default=OrderStatus.PENDING
    )
    car_quantity = models.PositiveIntegerField(default=1)
    sale_date = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
    )

    def __str__(self):
        return f"{self.showroom} order: {self.car}, quantity: {self.car_quantity}, status: {self.status}"

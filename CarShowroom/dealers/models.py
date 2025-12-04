from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField
from datetime import date

from services.choices import EngineType, UserType, BodyType, TransmissionType

from users.models import User


class Car(models.Model):
    """Model for description car"""

    engine_type = models.CharField(
        choices=EngineType.choices, max_length=8, default=EngineType.GASOLINE
    )
    transmission_type = models.CharField(
        choices=TransmissionType.choices, max_length=9, default=TransmissionType.MANUAL
    )
    body_type = models.CharField(
        choices=BodyType.choices, max_length=20
    )
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2026),
        ]
    )
    color = models.CharField(null=True, max_length=20)
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
            MaxValueValidator(2026),
        ],
        null=True,
        blank=True,
    )
    cars = models.ManyToManyField("Car", through="ProviderCars")
    country = CountryField(null=True, blank_label="(select country)")
    balance = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        validators=[MinValueValidator(0.00)],
        default=0.0,
    )
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, limit_choices_to={"user_type": UserType.PROVIDER}
    )

    def __str__(self):
        return f"{self.name}"

    def soft_delete(self):
        """Soft delete the object"""
        self.user.is_active = False
        self.save()


class ProviderCars(models.Model):
    """Cars for sale from Providers to Showrooms"""

    car = models.ForeignKey("Car", on_delete=models.CASCADE)
    provider = models.ForeignKey("Provider", on_delete=models.CASCADE)
    discount = models.ForeignKey("ProviderDiscount", on_delete=models.CASCADE)
    price = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        validators=[MinValueValidator(0.00)],
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.provider}'s car: {self.car}"


class ProviderSalesHistory(models.Model):
    """Sales history between Providers and Showrooms"""

    provider = models.ForeignKey("Provider", on_delete=models.CASCADE)
    showroom = models.ForeignKey("car_showroom.CarShowroom", on_delete=models.CASCADE)
    car = models.ForeignKey("dealers.Car", on_delete=models.CASCADE)
    car_amount = models.PositiveIntegerField(default=1)
    sale_date = models.DateField(auto_now_add=True)
    total_price = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        validators=[MinValueValidator(0.00)],
    )

class ProviderDiscount(models.Model):
    """Providers discount for showrooms"""

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date_start = models.DateField(default=date.today)
    date_end = models.DateField(blank=True, null=True)
    percent = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        default=0.0,
    )

    def __str__(self):
        return f"{self.name}"

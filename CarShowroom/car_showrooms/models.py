from datetime import date

from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User
from dealers.models import Car
from services.choices import UserType, OrderStatus


class Discount(models.Model):
    """Model for description discount"""

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


class CarShowroom(models.Model):
    """Model of car showroom"""

    name = models.CharField(max_length=100)
    cars = models.ManyToManyField("dealers.Car", through="ShowroomCar")
    owner_user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        limit_choices_to={"type": UserType.SHOWROOM},
    )

    def __str__(self):
        return f"{self.name}"


class ShowroomCar(models.Model):
    """Model of showroom's cars for selling"""

    car = models.ForeignKey("dealers.Car", on_delete=models.CASCADE)
    showroom = models.ForeignKey("CarShowroom", on_delete=models.CASCADE)
    discount = models.ForeignKey(
        "Discount", on_delete=models.SET_NULL, blank=True, null=True
    )
    car_quantity = models.IntegerField(default=0)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        default=0.0,
    )

    def __str__(self):
        return f"{self.showroom}'s car: {self.car}"


class CarShowroomOrder(models.Model):
    """Model of orders to customers"""

    showroom = models.ForeignKey("CarShowroom", on_delete=models.CASCADE)
    car_buyer = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        limit_choices_to={"type": UserType.SHOWROOM},
    )
    car = models.ForeignKey("dealers.Car", on_delete=models.CASCADE)
    status = models.CharField(
        choices=OrderStatus.choices, max_length=9, default=OrderStatus.PENDING
    )
    sale_date = models.DateField(auto_now_add=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
    )

    def __str__(self):
        return f"{self.car_buyer} order: {self.car}, status: {self.status}"

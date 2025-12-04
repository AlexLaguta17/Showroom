from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField
from django.utils import timezone
from datetime import date

from dealers.models import Car
from users.models import User
from customers.models import Customer


# Create your models here.
class CarShowroom(models.Model):
    """Model of car showrooms selling cars to customers"""

    name = models.CharField(max_length=100)
    country = CountryField(null=True)
    balance = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        validators=[MinValueValidator(0.00)],
        default=0.0,
    )
    cars = models.ManyToManyField("dealers.Car", through="ShowroomCars")
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    def soft_delete(self):
        """Soft delete the object"""
        self.user.is_active = False
        self.save()


class ShowroomCars(models.Model):
    """Model of showrooms selling cars to customers"""

    car = models.ForeignKey("dealers.Car", on_delete=models.CASCADE)
    showroom = models.ForeignKey("CarShowroom", on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    discount = models.ForeignKey("CarShowroomDiscount", on_delete=models.CASCADE)
    price = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        validators=[MinValueValidator(0.00)],
        default=0.0,
    )


class CarShowroomSalesHistory(models.Model):
    """Model of showrooms selling history cars to customers"""

    showroom = models.ForeignKey("CarShowroom", on_delete=models.CASCADE)
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE)
    car = models.ForeignKey("dealers.Car", on_delete=models.CASCADE)
    sale_date = models.DateField(auto_now_add=True)
    total_price = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        validators=[MinValueValidator(0.00)],
    )



class CarShowroomDiscount(models.Model):
    """Model of showrooms selling discount cars to customers"""

    showroom = models.ForeignKey("CarShowroom", on_delete=models.CASCADE)
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

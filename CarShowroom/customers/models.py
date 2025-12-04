from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField
from phonenumber_field.modelfields import PhoneNumberField

from services.choices import Gender, UserType

from users.models import User


class Customer(models.Model):
    """The car buyer model at CarShowrooms"""

    sex = models.CharField(choices=Gender.choices, max_length=6)
    phone_number = PhoneNumberField(null=True, unique=True)
    balance = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        validators=[MinValueValidator(0.00)],
        default=0.0,
    )
    age = models.IntegerField(null=True, validators=[MinValueValidator(18)])
    country = CountryField(null=True)
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"

    def soft_delete(self):
        """Soft delete the object"""
        self.user.is_active = False
        self.save()

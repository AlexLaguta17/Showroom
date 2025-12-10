from django.db import models
from djmoney.models.fields import MoneyField
from django_countries.fields import CountryField
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

from services.choices import UserType


class User(AbstractUser):
    """Extended AbstractUser for realize roles of UserType.choices"""

    user_type = models.CharField(
        choices=UserType.choices, max_length=8, default=UserType.CUSTOMER
    )
    phone_number = PhoneNumberField(null=True, unique=True)
    age = models.IntegerField(null=True, validators=[MinValueValidator(18)])
    country = CountryField(null=True, blank_label="(select country)")
    balance = models.DecimalField(
        default=0.0,
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
    )

    def __str__(self):
        return f"{self.user_type}: {self.first_name} {self.last_name}"

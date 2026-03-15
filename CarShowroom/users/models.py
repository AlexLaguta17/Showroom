"""Models for the users app: custom User extending AbstractUser."""

from django.db import models
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator
from django.contrib.auth.hashers import identify_hasher
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import UserManager, AbstractUser

from services.choices import UserType


class User(AbstractUser):
    """Extended AbstractUser that adds a role, balance, and contact details."""

    type = models.CharField(choices=UserType.choices, max_length=8, default=UserType.CUSTOMER)
    phone_number = PhoneNumberField(null=True, unique=True)
    age = models.IntegerField(null=True, validators=[MinValueValidator(18)])
    country = CountryField(null=True, blank_label="(select country)")
    balance = models.DecimalField(
        default=0.0,
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def save(self, *args, **kwargs):
        """Hash the password before saving if it is stored in plain text."""
        if self.password:
            try:
                identify_hasher(self.password)
            except ValueError:
                self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string showing the user type and full name."""
        return f"{self.type}: {self.first_name} {self.last_name}"

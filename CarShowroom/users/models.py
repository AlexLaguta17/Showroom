from django.contrib.auth.models import AbstractUser
from django.db import models
from services.choices import UserType


class User(AbstractUser):
    """Extended AbstractUser for realize roles of UserType.choices"""

    user_type = models.CharField(
        choices=UserType.choices, max_length=8, default=UserType.NONE
    )

    def __str__(self):
        return self.username

from decimal import Decimal

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    type = "customer"
    phone_number = factory.Sequence(lambda n: f"+479000000{n}")
    age = 25
    country = "NO"
    balance = Decimal("0.00")
    password = factory.LazyFunction(lambda: make_password("testpass123"))

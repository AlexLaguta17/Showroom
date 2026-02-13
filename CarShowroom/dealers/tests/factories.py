from datetime import date

import factory
import factory.fuzzy
from factory.django import DjangoModelFactory

from users.tests.factories import UserFactory
from dealers.models import Car, Provider, ProviderCar
from services.choices import BodyType, UserType, EngineType, TransmissionType


class CarFactory(DjangoModelFactory):
    class Meta:
        model = Car

    engine_type = factory.fuzzy.FuzzyChoice(EngineType.values)
    transmission_type = factory.fuzzy.FuzzyChoice(TransmissionType.values)
    body_type = factory.fuzzy.FuzzyChoice(BodyType.values)
    brand = factory.Iterator(
        ["Toyota", "BMW", "Audi", "Mercedes", "Ford", "Honda", "Hyundai"]
    )
    model = factory.Sequence(lambda n: f"Model-{n}")

    year = factory.Faker("random_int", min=1990, max=date.today().year)

    color = factory.Faker("color_name")
    engine_volume = factory.Faker(
        "pydecimal",
        left_digits=1,
        right_digits=1,
        positive=True,
        min_value=1,
        max_value=6,
    )


class ProviderFactory(DjangoModelFactory):
    class Meta:
        model = Provider

    name = factory.Faker("company")
    year_founded = factory.Faker("random_int", min=1800, max=date.today().year)

    owner_user = factory.SubFactory(UserFactory, type=UserType.PROVIDER)


class ProviderCarFactory(DjangoModelFactory):
    """Фабрика для промежуточной модели ProviderCar"""

    class Meta:
        model = ProviderCar

    car = factory.SubFactory(CarFactory)
    provider = factory.SubFactory(ProviderFactory)
    discount = None
    car_quantity = factory.Faker("random_int", min=0, max=100)
    price = factory.Faker(
        "pydecimal",
        left_digits=7,
        right_digits=2,
        positive=True,
        min_value=5000,
        max_value=1000000,
    )

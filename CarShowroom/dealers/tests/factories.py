from datetime import date
from decimal import Decimal

import factory
import factory.fuzzy
from factory.django import DjangoModelFactory

from users.tests.factories import UserFactory
from dealers.models import Car, Provider, ProviderCar, ProviderOrder
from services.choices import (
    BodyType,
    UserType,
    EngineType,
    OrderStatus,
    TransmissionType,
)


class CarFactory(DjangoModelFactory):
    class Meta:
        model = Car

    engine_type = factory.fuzzy.FuzzyChoice(EngineType.values)
    transmission_type = factory.fuzzy.FuzzyChoice(TransmissionType.values)
    body_type = factory.fuzzy.FuzzyChoice(BodyType.values)
    brand = factory.Iterator(["Toyota", "BMW", "Audi", "Mercedes", "Ford", "Honda", "Hyundai"])
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


class ProviderOrderFactory(DjangoModelFactory):
    class Meta:
        model = ProviderOrder

    provider = factory.SubFactory(ProviderFactory)
    showroom = factory.SubFactory("car_showrooms.tests.factories.CarShowroomFactory")
    car = factory.SubFactory(ProviderCarFactory, provider=factory.SelfAttribute("..provider"))
    status = OrderStatus.PENDING
    car_quantity = 1
    total_price = Decimal("25000.00")

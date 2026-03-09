"""Factory classes for car_showrooms app models used in tests."""

import random
import datetime

import factory
from factory.django import DjangoModelFactory

from users.tests.factories import UserFactory
from dealers.tests.factories import CarFactory
from services.choices import UserType, OrderStatus
from car_showrooms.models import Discount, CarShowroom, ShowroomCar, CarShowroomOrder


class DiscountFactory(DjangoModelFactory):
    """Factory for the Discount model."""

    class Meta:
        """Factory metadata."""

        model = Discount

    name = factory.Sequence(lambda n: f"Discount Offer {n}")
    description = factory.Faker("text", max_nb_chars=200)
    percent = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        positive=True,
        min_value=5,
        max_value=50,
    )

    date_start = factory.Faker("date_between", start_date="-30d", end_date="today")
    date_end = factory.LazyAttribute(lambda o: o.date_start + datetime.timedelta(days=random.randint(1, 30)))
    owner_user = factory.SubFactory(UserFactory, type=UserType.SHOWROOM)

    class Params:
        """Factory traits."""

        is_expired = factory.Trait(
            date_start=factory.Faker("date_between", start_date="-60d", end_date="-31d"),
            date_end=factory.LazyAttribute(lambda o: o.date_start + datetime.timedelta(days=10)),
        )


class CarShowroomFactory(DjangoModelFactory):
    """Factory for the CarShowroom model."""

    class Meta:
        """Factory metadata."""

        model = CarShowroom

    name = factory.Sequence(lambda n: f"Best Cars Showroom {n}")
    owner_user = factory.SubFactory(UserFactory, type=UserType.SHOWROOM)


class ShowroomCarFactory(DjangoModelFactory):
    """Factory for the ShowroomCar through-model."""

    class Meta:
        """Factory metadata."""

        model = ShowroomCar

    car = factory.SubFactory(CarFactory)
    showroom = factory.SubFactory(CarShowroomFactory)
    discount = None
    car_quantity = factory.Faker("random_int", min=1, max=10)
    price = factory.Faker(
        "pydecimal",
        left_digits=5,
        right_digits=2,
        positive=True,
        min_value=10000,
        max_value=90000,
    )
    is_published = True

    class Params:
        """Factory traits."""

        with_discount = factory.Trait(discount=factory.SubFactory(DiscountFactory))


class CarShowroomOrderFactory(DjangoModelFactory):
    """Factory for the CarShowroomOrder model."""

    class Meta:
        """Factory metadata."""

        model = CarShowroomOrder

    showroom = factory.SubFactory(CarShowroomFactory)
    car_buyer = factory.SubFactory(UserFactory, type=UserType.CUSTOMER)
    car = factory.SubFactory(ShowroomCarFactory, showroom=factory.SelfAttribute("..showroom"))
    status = OrderStatus.PENDING
    price = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True, min_value=10000, max_value=90000)

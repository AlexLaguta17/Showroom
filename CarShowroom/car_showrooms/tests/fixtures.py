"""Pytest fixtures for the car_showrooms app."""

import pytest

from car_showrooms.tests.factories import (
    DiscountFactory,
    CarShowroomFactory,
    ShowroomCarFactory,
)

pytest_plugins = ["users.tests.fixtures", "dealers.tests.fixtures"]


@pytest.fixture
def discount():
    """Return a factory function for creating Discount instances."""

    def _create_discount(**kwargs):
        """Create and return a Discount instance."""
        return DiscountFactory(**kwargs)

    return _create_discount


@pytest.fixture
def showroom():
    """Return a factory function for creating CarShowroom instances."""

    def _create_showroom(**kwargs):
        """Create and return a CarShowroom instance."""
        return CarShowroomFactory(**kwargs)

    return _create_showroom


@pytest.fixture
def showroom_car():
    """Return a factory function for creating ShowroomCar instances."""

    def _create_showroom_car(**kwargs):
        """Create and return a ShowroomCar instance."""
        return ShowroomCarFactory(**kwargs)

    return _create_showroom_car

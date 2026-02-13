import pytest

from car_showrooms.tests.factories import (
    DiscountFactory,
    CarShowroomFactory,
    ShowroomCarFactory,
)

pytest_plugins = ["users.tests.fixtures", "dealers.tests.fixtures"]


@pytest.fixture
def discount():
    def _create_discount(**kwargs):
        return DiscountFactory(**kwargs)

    return _create_discount


@pytest.fixture
def showroom():
    def _create_showroom(**kwargs):
        return CarShowroomFactory(**kwargs)

    return _create_showroom


@pytest.fixture
def showroom_car():
    def _create_showroom_car(**kwargs):
        return ShowroomCarFactory(**kwargs)

    return _create_showroom_car

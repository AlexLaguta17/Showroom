import pytest

from dealers.tests.factories import CarFactory, ProviderFactory, ProviderCarFactory, ProviderOrderFactory


@pytest.fixture
def car():
    def _create_car(**kwargs):
        return CarFactory(**kwargs)

    return _create_car


@pytest.fixture
def provider():
    def _create_provider(**kwargs):
        return ProviderFactory(**kwargs)

    return _create_provider


@pytest.fixture
def provider_car():
    def _create_provider_car(**kwargs):
        return ProviderCarFactory(**kwargs)

    return _create_provider_car


@pytest.fixture
def provider_order():
    def _create_provider_order(**kwargs):
        return ProviderOrderFactory(**kwargs)

    return _create_provider_order

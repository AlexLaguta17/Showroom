"""Pytest fixtures for the dealers app."""

import pytest

from dealers.tests.factories import (
    CarFactory,
    ProviderFactory,
    ProviderCarFactory,
    ProviderOrderFactory,
)


@pytest.fixture
def car():
    """Return a factory function for creating Car instances."""

    def _create_car(**kwargs):
        """Create and return a Car instance."""
        return CarFactory(**kwargs)

    return _create_car


@pytest.fixture
def provider():
    """Return a factory function for creating Provider instances."""

    def _create_provider(**kwargs):
        """Create and return a Provider instance."""
        return ProviderFactory(**kwargs)

    return _create_provider


@pytest.fixture
def provider_car():
    """Return a factory function for creating ProviderCar instances."""

    def _create_provider_car(**kwargs):
        """Create and return a ProviderCar instance."""
        return ProviderCarFactory(**kwargs)

    return _create_provider_car


@pytest.fixture
def provider_order():
    """Return a factory function for creating ProviderOrder instances."""

    def _create_provider_order(**kwargs):
        """Create and return a ProviderOrder instance."""
        return ProviderOrderFactory(**kwargs)

    return _create_provider_order

"""TextChoices enums shared across all apps."""

from django.db import models


class UserType(models.TextChoices):
    """Roles a user account can hold in the system."""

    CUSTOMER = "customer"
    SHOWROOM = "showroom"
    PROVIDER = "provider"


class EngineType(models.TextChoices):
    """Fuel/power source types for a car engine."""

    GASOLINE = "Gasoline"
    DIESEL = "Diesel"
    HYBRID = "Hybrid"
    ELECTRIC = "Electric"


class BodyType(models.TextChoices):
    """Car body style variants."""

    SEDAN = "Sedan"
    WAGON = "Wagon"
    COUPE = "Coupe"
    HATCHBACK = "Hatchback"


class TransmissionType(models.TextChoices):
    """Gearbox transmission types."""

    AUTOMATIC = "Automatic"
    MANUAL = "Manual"


class OrderStatus(models.TextChoices):
    """Lifecycle statuses for provider and showroom orders."""

    PENDING = "Pending"
    COMPLETED = "Completed"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"
    SOLD = "Sold"
    BOOKED = "Booked"

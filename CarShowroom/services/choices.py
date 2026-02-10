from django.db import models


class UserType(models.TextChoices):
    CUSTOMER = "customer"
    SHOWROOM = "showroom"
    PROVIDER = "provider"


class EngineType(models.TextChoices):
    GASOLINE = "Gasoline"
    DIESEL = "Diesel"
    HYBRID = "Hybrid"
    ELECTRIC = "Electric"


class BodyType(models.TextChoices):
    SEDAN = "Sedan"
    WAGON = "Wagon"
    COUPE = "Coupe"
    HATCHBACK = "Hatchback"


class TransmissionType(models.TextChoices):
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"


class OrderStatus(models.TextChoices):
    PENDING = "Pending"
    COMPLETED = "Completed"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"
    SOLD = "Sold"
    BOOKED = "Booked"

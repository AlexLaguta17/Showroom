from django.db import models


class UserType(models.TextChoices):
    NONE = "none"
    CUSTOMER = "customer"
    SHOWROOM = "showroom"
    PROVIDER = "provider"


class EngineType(models.TextChoices):
    GASOLINE = "Gasoline"
    DIESEL = "Diesel"
    HYBRID = "Hybrid"
    ELECTRIC = "Electric"


class Gender(models.TextChoices):
    M = "Male"
    F = "Female"


class BodyType(models.TextChoices):
    SEDAN = "Sedan"
    WAGON = "Wagon"
    COUPE = "Coupe"
    HATCHBACK = "Hatchback"


class TransmissionType(models.TextChoices):
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"

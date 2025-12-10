from django.contrib import admin

from dealers.models import (
    Car,
    Provider,
    ProviderCar,
    ProviderOrder,
)

admin.site.register(Car)
admin.site.register(Provider)
admin.site.register(ProviderCar)
admin.site.register(ProviderOrder)

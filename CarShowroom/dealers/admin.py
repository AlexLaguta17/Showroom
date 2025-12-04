from django.contrib import admin

from dealers.models import (
    Car,
    Provider,
    ProviderCars,
    ProviderDiscount,
    ProviderSalesHistory,
)


# Register your models here.
admin.site.register(Car)
admin.site.register(Provider)
admin.site.register(ProviderCars)
admin.site.register(ProviderDiscount)
admin.site.register(ProviderSalesHistory)

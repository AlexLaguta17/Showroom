from django.contrib import admin

from car_showroom.models import (
    CarShowroom,
    CarShowroomDiscount,
    CarShowroomSalesHistory,
    ShowroomCars,
)

# Register your models here.
admin.site.register(CarShowroom)
admin.site.register(ShowroomCars)
admin.site.register(CarShowroomDiscount)
admin.site.register(CarShowroomSalesHistory)

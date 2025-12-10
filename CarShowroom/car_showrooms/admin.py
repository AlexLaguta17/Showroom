from django.contrib import admin

from car_showrooms.models import (
    Discount,
    CarShowroom,
    ShowroomCar,
    CarShowroomOrder,
)

admin.site.register(Discount)
admin.site.register(CarShowroom)
admin.site.register(ShowroomCar)
admin.site.register(CarShowroomOrder)

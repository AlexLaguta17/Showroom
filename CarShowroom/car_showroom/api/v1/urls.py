from django.urls import path, include
from rest_framework import routers

from car_showroom.api.v1.views import (
    CarShowroomViewSet,
    ShowroomCarsViewSet,
    CarShowroomSalesHistoryViewSet,
    CarShowroomDiscountViewSet,
)


car_showroom_router = routers.SimpleRouter()
car_showroom_router.register("showrooms", CarShowroomViewSet)
car_showroom_router.register("showroom-cars", ShowroomCarsViewSet)
car_showroom_router.register("showroom-sales-history", CarShowroomSalesHistoryViewSet)
car_showroom_router.register("showroom-discounts", CarShowroomDiscountViewSet)

urlpatterns = [
    path("", include(car_showroom_router.urls)),
]

from django.urls import path, include
from rest_framework import routers

from dealers.api.v1.views import (
    CarViewSet,
    ProviderViewSet,
    ProviderCarsViewSet,
    ProviderSalesHistoryViewSet,
    ProviderDiscountViewSet,
)


dealers_router = routers.SimpleRouter()
dealers_router.register("cars", CarViewSet)
dealers_router.register("providers", ProviderViewSet)
dealers_router.register("provider-cars", ProviderCarsViewSet)
dealers_router.register("provider-sales-history", ProviderSalesHistoryViewSet)
dealers_router.register("provider-discounts", ProviderDiscountViewSet)

urlpatterns = [
    path("", include(dealers_router.urls)),
]

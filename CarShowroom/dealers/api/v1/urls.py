from django.urls import path

from dealers.api.v1.views import (
    CarViewSet,
    ProviderViewSet,
    ProviderCarViewSet,
    ProviderOrderViewSet,
    ProviderDiscountViewSet,
)

CR_methods = {"get": "list", "post": "create"}
RUD_methods = {"get": "retrieve", "put": "update", "delete": "destroy"}

urlpatterns = [
    path("cars/", CarViewSet.as_view(CR_methods)),
    path("cars/<int:pk>/", CarViewSet.as_view(RUD_methods)),
    path("", ProviderViewSet.as_view(CR_methods)),
    path("<int:provider_pk>/", ProviderViewSet.as_view(RUD_methods)),
    path("<int:provider_pk>/cars/", ProviderCarViewSet.as_view(CR_methods)),
    path(
        "<int:provider_pk>/cars/<int:car_pk>/", ProviderCarViewSet.as_view(RUD_methods)
    ),
    path("<int:provider_pk>/orders/", ProviderOrderViewSet.as_view(CR_methods)),
    path(
        "<int:provider_pk>/orders/<int:order_pk>/",
        ProviderOrderViewSet.as_view(RUD_methods),
    ),
    path("<int:provider_pk>/discounts/", ProviderDiscountViewSet.as_view(CR_methods)),
    path(
        "<int:provider_pk>/discounts/<int:discount_pk>/",
        ProviderDiscountViewSet.as_view(RUD_methods),
    ),
]

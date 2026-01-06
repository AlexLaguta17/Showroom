from django.urls import path

from dealers.api.v1.views import (
    ProviderViewSet,
    CarDetailAPIView,
    ProviderCarViewSet,
    CarListCreateAPIView,
    ProviderOrderAPIView,
    ProviderDiscountViewSet,
    ProviderOrderActionAPIView,
)

CR_methods = {"get": "list", "post": "create"}
RUD_methods = {"get": "retrieve", "put": "update", "delete": "destroy"}

urlpatterns = [
    path("cars/", CarListCreateAPIView.as_view()),
    path("cars/<int:pk>/", CarDetailAPIView.as_view()),
    path("", ProviderViewSet.as_view(CR_methods)),
    path("<int:provider_pk>/", ProviderViewSet.as_view(RUD_methods)),
    path("<int:provider_pk>/cars/", ProviderCarViewSet.as_view(CR_methods)),
    path("<int:provider_pk>/cars/<int:car_pk>/", ProviderCarViewSet.as_view(RUD_methods)),
    path("<int:provider_pk>/discounts/", ProviderDiscountViewSet.as_view(CR_methods)),
    path("<int:provider_pk>/discounts/<int:discount_pk>/", ProviderDiscountViewSet.as_view(RUD_methods)),
    path(
        "<int:provider_pk>/orders/",
        ProviderOrderAPIView.as_view(),
        name="provider-order-list",
    ),
    path(
        "<int:provider_pk>/orders/<int:pk>/",
        ProviderOrderAPIView.as_view(),
        name="provider-order-detail",
    ),
    path(
        "<int:provider_pk>/orders/<int:order_pk>/action/",
        ProviderOrderActionAPIView.as_view(),
        name="provider-order-action-list",
    ),
]

"""URL configuration for the dealers API v1."""

from django.urls import path

from dealers.api.v1.views import (
    CarDetailAPIView,
    CarListCreateAPIView,
    ProviderDetailAPIView,
    ProviderCarDetailAPIView,
    ProviderListCreateAPIView,
    ProviderOrderCancelAPIView,
    ProviderOrderDetailAPIView,
    ProviderOrderRejectAPIView,
    ProviderOrderConfirmAPIView,
    ProviderCarListCreateAPIView,
    ProviderDiscountDetailAPIView,
    ProviderOrderListCreateAPIView,
    ProviderDiscountListCreateAPIView,
)

urlpatterns = [
    path("", ProviderListCreateAPIView.as_view(), name="provider-list"),
    path("<int:pk>/", ProviderDetailAPIView.as_view(), name="provider-detail"),
    path("cars/", CarListCreateAPIView.as_view(), name="car-list"),
    path("cars/<int:pk>/", CarDetailAPIView.as_view(), name="car-detail"),
    path("<int:provider_pk>/cars/", ProviderCarListCreateAPIView.as_view(), name="provider-car-list"),
    path("<int:provider_pk>/cars/<int:pk>/", ProviderCarDetailAPIView.as_view(), name="provider-car-detail"),
    path("<int:provider_pk>/discounts/", ProviderDiscountListCreateAPIView.as_view(), name="provider-discount-list"),
    path(
        "<int:provider_pk>/discounts/<int:pk>/",
        ProviderDiscountDetailAPIView.as_view(),
        name="provider-discount-detail",
    ),
    path(
        "<int:provider_pk>/orders/",
        ProviderOrderListCreateAPIView.as_view(),
        name="provider-order-list-create",
    ),
    path(
        "<int:provider_pk>/orders/<int:pk>/",
        ProviderOrderDetailAPIView.as_view(),
        name="provider-order-detail",
    ),
    path(
        "<int:provider_pk>/orders/<int:pk>/confirm/",
        ProviderOrderConfirmAPIView.as_view(),
        name="provider-order-confirm",
    ),
    path(
        "<int:provider_pk>/orders/<int:pk>/reject/",
        ProviderOrderRejectAPIView.as_view(),
        name="provider-order-reject",
    ),
    path(
        "<int:provider_pk>/orders/<int:pk>/cancel/",
        ProviderOrderCancelAPIView.as_view(),
        name="provider-order-cancel",
    ),
]

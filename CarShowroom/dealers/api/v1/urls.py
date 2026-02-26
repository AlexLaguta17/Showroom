from django.urls import path

from dealers.api.v1.views import (
    CarDetailAPIView,
    CarListCreateAPIView,
    ProviderDetailAPIView,
    ProviderCarDetailAPIView,
    ProviderOrderListAPIView,
    ProviderListCreateAPIView,
    ProviderOrderCancelAPIView,
    ProviderOrderCreateAPIView,
    ProviderOrderDetailAPIView,
    ProviderOrderRejectAPIView,
    ProviderOrderConfirmAPIView,
    ProviderCarListCreateAPIView,
    ProviderDiscountDetailAPIView,
    ProviderDiscountListCreateAPIView,
)

urlpatterns = [
    path("", ProviderListCreateAPIView.as_view()),
    path("<int:pk>/", ProviderDetailAPIView.as_view()),
    path("cars/", CarListCreateAPIView.as_view()),
    path("cars/<int:pk>/", CarDetailAPIView.as_view()),
    path("<int:provider_pk>/cars/", ProviderCarListCreateAPIView.as_view()),
    path("<int:provider_pk>/cars/<int:pk>/", ProviderCarDetailAPIView.as_view()),
    path("<int:provider_pk>/discounts/", ProviderDiscountListCreateAPIView.as_view()),
    path(
        "<int:provider_pk>/discounts/<int:pk>/",
        ProviderDiscountDetailAPIView.as_view(),
    ),
    path(
        "<int:provider_pk>/orders/",
        ProviderOrderListAPIView.as_view(),
        name="provider-order-list",
    ),
    path(
        "<int:provider_pk>/orders/<int:pk>/",
        ProviderOrderDetailAPIView.as_view(),
        name="provider-order-detail",
    ),
    path(
        "<int:provider_pk>/create-orders/",
        ProviderOrderCreateAPIView.as_view(),
        name="provider-order-create",
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

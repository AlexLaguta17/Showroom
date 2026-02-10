from django.urls import path

from dealers.api.v1.views import (
    CarDetailAPIView,
    CarListCreateAPIView,
    ProviderOrderAPIView,
    ProviderDetailAPIView,
    ProviderCarDetailAPIView,
    ProviderListCreateAPIView,
    ProviderOrderActionAPIView,
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

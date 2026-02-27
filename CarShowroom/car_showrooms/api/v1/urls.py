"""URL configuration for the car_showrooms API v1."""

from django.urls import path

from car_showrooms.api.v1.views import (
    ShowroomViewSet,
    ShowroomCarViewSet,
    ShowroomDiscountViewSet,
)

LIST_CREATE_ACTIONS = {"get": "list", "post": "create"}
RETRIEVE_UPDATE_DESTROY_ACTIONS = {
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
}

urlpatterns = [
    path("", ShowroomViewSet.as_view(LIST_CREATE_ACTIONS), name="showroom-list"),
    path("<int:pk>/", ShowroomViewSet.as_view(RETRIEVE_UPDATE_DESTROY_ACTIONS), name="showroom-detail"),
    path("<int:showroom_pk>/cars/", ShowroomCarViewSet.as_view({"get": "list"}), name="showroom-car-list"),
    path(
        "<int:showroom_pk>/cars/<int:pk>/",
        ShowroomCarViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update"}),
        name="showroom-car-detail",
    ),
    path(
        "<int:showroom_pk>/discounts/",
        ShowroomDiscountViewSet.as_view(LIST_CREATE_ACTIONS),
        name="showroom-discount-list",
    ),
    path(
        "<int:showroom_pk>/discounts/<int:pk>/",
        ShowroomDiscountViewSet.as_view(RETRIEVE_UPDATE_DESTROY_ACTIONS),
        name="showroom-discount-detail",
    ),
]

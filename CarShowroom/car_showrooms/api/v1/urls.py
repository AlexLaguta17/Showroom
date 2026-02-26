from django.urls import path

from car_showrooms.api.v1.views import (
    ShowroomViewSet,
    ShowroomCarViewSet,
    CarShowroomOrderViewSet,
    ShowroomDiscountViewSet,
)

CR_methods = {"get": "list", "post": "create"}
RUD_methods = {
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
}

urlpatterns = [
    path("", ShowroomViewSet.as_view(CR_methods)),
    path("<int:pk>/", ShowroomViewSet.as_view(RUD_methods)),
    path("<int:showroom_pk>/cars/", ShowroomCarViewSet.as_view({"get": "list"})),
    path(
        "<int:showroom_pk>/cars/<int:pk>/",
        ShowroomCarViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update"}),
    ),
    path(
        "<int:showroom_pk>/orders/",
        CarShowroomOrderViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "<int:showroom_pk>/orders/<int:pk>/",
        CarShowroomOrderViewSet.as_view({"get": "retrieve"}),
    ),
    # path("discounts/", AllShowroomDiscountViewSet.as_view(CR_methods)),
    path("<int:showroom_pk>/discounts/", ShowroomDiscountViewSet.as_view(CR_methods)),
    path(
        "<int:showroom_pk>/discounts/<int:pk>/",
        ShowroomDiscountViewSet.as_view(RUD_methods),
    ),
]

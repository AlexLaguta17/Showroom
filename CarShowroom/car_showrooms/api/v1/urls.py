from django.urls import path

from car_showrooms.api.v1.views import (
    ShowroomViewSet,
    ShowroomCarViewSet,
    CarShowroomOrderViewSet,
    ShowroomDiscountViewSet,
    ShowroomProviderOrderCancelAPIView,
    ShowroomProviderOrderDetailAPIView,
    ShowroomProviderOrderListCreateAPIView,
)

CR_methods = {"get": "list", "post": "create"}
RUD_methods = {"get": "retrieve", "put": "update", "delete": "destroy"}

urlpatterns = [
    path("", ShowroomViewSet.as_view(CR_methods)),
    path("<int:showroom_pk>/", ShowroomViewSet.as_view(RUD_methods)),
    path("<int:showroom_pk>/cars/", ShowroomCarViewSet.as_view(CR_methods)),
    path("<int:showroom_pk>/cars/<int:car_pk>/", ShowroomCarViewSet.as_view(RUD_methods)),
    path("<int:showroom_pk>/orders/", CarShowroomOrderViewSet.as_view(CR_methods)),
    path("<int:showroom_pk>/orders/<int:order_pk>/", CarShowroomOrderViewSet.as_view(RUD_methods)),
    path("<int:showroom_pk>/discounts/", ShowroomDiscountViewSet.as_view(CR_methods)),
    path("<int:showroom_pk>/discounts/<int:discount_pk>/", ShowroomDiscountViewSet.as_view(RUD_methods),
    ),
    path(
        "<int:showroom_pk>/provider-orders/",
        ShowroomProviderOrderListCreateAPIView.as_view(),
        name="showroom-provider-order-list-create",
    ),
    path(
        "<int:showroom_pk>/provider-orders/<int:order_pk>/",
        ShowroomProviderOrderDetailAPIView.as_view(),
        name="showroom-provider-order-detail",
    ),
    path(
        "<int:showroom_pk>/provider-orders/<int:order_pk>/cancel/",
        ShowroomProviderOrderCancelAPIView.as_view(),
        name="showroom-provider-order-cancel",
    ),
]

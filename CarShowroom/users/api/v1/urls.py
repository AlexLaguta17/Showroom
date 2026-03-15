"""URL configuration for the users API v1."""

from django.urls import path

from users.api.v1.views import UserViewSet

LIST_CREATE_ACTIONS = {"get": "list", "post": "create"}
RETRIEVE_UPDATE_DESTROY_ACTIONS = {
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
}

urlpatterns = [
    path("", UserViewSet.as_view(LIST_CREATE_ACTIONS), name="user-list"),
    path("<int:pk>/", UserViewSet.as_view(RETRIEVE_UPDATE_DESTROY_ACTIONS), name="user-detail"),
]

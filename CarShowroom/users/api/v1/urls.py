from django.urls import path

from users.api.v1.views import UserViewSet

CR_methods = {"get": "list", "post": "create"}
RUD_methods = {"get": "retrieve", "put": "update", "delete": "destroy"}

urlpatterns = [
    path("", UserViewSet.as_view(CR_methods)),
    path("<int:user_pk>/", UserViewSet.as_view(RUD_methods)),
]

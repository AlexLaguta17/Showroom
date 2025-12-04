from django.urls import path, include
from rest_framework import routers

from users.api.v1.views import UserViewSet, LoginUser, LogoutUser

user_router = routers.SimpleRouter()
user_router.register("", UserViewSet)

urlpatterns = [
    path("", include(user_router.urls)),
    path("login/", LoginUser.as_view(), name='login'),
    path("logout/", LogoutUser.as_view(), name='logout'),
]

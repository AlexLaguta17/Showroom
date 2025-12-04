from django.urls import path, include
from rest_framework import routers

from customers.api.v1.views import CustomerViewSet


customer_router = routers.SimpleRouter()
customer_router.register("", CustomerViewSet)
urlpatterns = [
    path("", include(customer_router.urls)),
]

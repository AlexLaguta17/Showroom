from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.views import APIView

from customers.serializers import CustomerSerializer
from customers.models import Customer


# Create your views here.
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

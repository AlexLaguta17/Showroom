from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserSerializer
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginUser(LoginView):
    form_class = AuthenticationForm


class LogoutUser(LogoutView):
    pass

#
# class UserLoginAPIView(APIView):
#     def post(self, request):
#         return Response("<h1> Login </h1>", status=status.HTTP_200_OK)
#
#
# class UserLogoutAPIView(APIView):
#     def post(self, request):
#         return Response('logout', status=status.HTTP_200_OK)
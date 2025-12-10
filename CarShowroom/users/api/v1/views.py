from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from users.models import User
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        user_pk = self.kwargs.get("user_pk")
        return get_object_or_404(self.get_queryset(), pk=user_pk)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

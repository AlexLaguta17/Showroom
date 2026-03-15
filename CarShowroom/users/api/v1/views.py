"""API views for the users app."""

from rest_framework import status, viewsets
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer
from users.permissions import IsOwnerOrReadOnly, IsAnonymousForCreate


class UserViewSet(viewsets.ModelViewSet):
    """CRUD operations for users; destroy performs a soft delete."""

    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrReadOnly, IsAnonymousForCreate)

    def destroy(self, request, *args, **kwargs):
        """Soft-delete the user by setting is_active to False."""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

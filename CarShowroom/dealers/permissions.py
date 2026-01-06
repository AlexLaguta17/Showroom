from rest_framework import permissions

from dealers.models import Provider


class IsProviderOwner(permissions.BasePermission):
    """Check if user is the owner of a Provider."""

    def has_permission(self, request, view):
        """Check permissions at request level."""
        if not request.user.is_authenticated:
            return False
        return request.user.type == "provider"

    def has_object_permission(self, request, view, obj):
        """Check permissions at object level."""
        if isinstance(obj, Provider):
            return obj.owner_user == request.user

        elif hasattr(obj, "provider"):
            return obj.provider.owner_user == request.user

        return False

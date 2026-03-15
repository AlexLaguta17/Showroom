"""Permission classes for the users app."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAnonymousForCreate(BasePermission):
    """Allow only unauthenticated users to create (register) accounts."""

    def has_permission(self, request, view):
        """Block authenticated users from calling the create action."""
        if view.action == "create":
            return not request.user.is_authenticated

        return True


class IsOwnerOrReadOnly(BasePermission):
    """Allow read-only access to anyone; restrict writes to the object owner."""

    def has_object_permission(self, request, view, obj):
        """Allow safe methods; restrict mutations to the object owner."""
        if request.method in SAFE_METHODS:
            return True

        return obj == request.user

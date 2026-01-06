from rest_framework import permissions

from car_showrooms.models import CarShowroom


class IsShowroomOwner(permissions.BasePermission):
    """Check if user is the owner of a CarShowroom."""

    def has_permission(self, request, view):
        """Check permissions at request level."""
        if not request.user.is_authenticated:
            return False
        return request.user.type == "showroom"

    def has_object_permission(self, request, view, obj):
        """Check permissions at object level."""

        if isinstance(obj, CarShowroom):
            return obj.owner_user == request.user

        elif hasattr(obj, "showroom"):
            return obj.showroom.owner_user == request.user

        return False

"""Permission classes for the dealers app."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from services.choices import UserType


class IsProviderOrShowroom(BasePermission):
    """Check if user type is provider or showroom."""

    def has_permission(self, request, view):
        """Allow safe methods for providers and showrooms; restrict mutations to providers."""
        if request.method == "GET":
            return request.user.type in (UserType.PROVIDER, UserType.SHOWROOM)

        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return request.user.type == UserType.PROVIDER

        return True


class IsProviderOwner(BasePermission):
    """Check if user is Provider owner."""

    def has_permission(self, request, view):
        """Allow HEAD/OPTIONS unconditionally; require the user to own the provider."""
        if request.method in ("HEAD", "OPTIONS"):
            return True

        return view.provider.owner_user_id == request.user.id


class IsProviderOwnerOrShowroom(BasePermission):
    """Check if user is provider owner or showroom read only."""

    def has_object_permission(self, request, view, obj):
        """Allow safe methods for all; restrict mutations to the object owner."""
        if request.method in SAFE_METHODS:
            return True

        return request.user.id == obj.owner_user.id


class IsProviderOrShowroomOwner(BasePermission):
    """Allow provider owner full access; allow showroom users read-only access."""

    def has_permission(self, request, view):
        """Allow HEAD/OPTIONS unconditionally; allow provider owner or any showroom owner."""
        if request.method in ("HEAD", "OPTIONS"):
            return True
        return view.provider.owner_user_id == request.user.id or hasattr(request.user, "carshowroom")


class IsProviderCarOwnerOrShowroom(BasePermission):
    """Check if user is provider car owner or showroom read only."""

    def has_object_permission(self, request, view, obj):
        """Allow safe methods for all; restrict mutations to the provider car owner."""
        if request.method in SAFE_METHODS:
            return True

        return request.user.id == obj.provider.owner_user.id


class IsShowroomOwnerUser(BasePermission):
    """Check if user is showroom owner user."""

    def has_permission(self, request, view):
        """Allow HEAD/OPTIONS unconditionally; require an authenticated showroom owner."""
        if request.method in ("HEAD", "OPTIONS"):
            return True

        return request.user.type == UserType.SHOWROOM and hasattr(request.user, "carshowroom")


class IsOrderShowroomOwner(BasePermission):
    """Ensure only the showroom that created the order can modify it."""

    def has_permission(self, request, view):
        """Allow HEAD/OPTIONS unconditionally; require SHOWROOM user type."""
        if request.method in ("HEAD", "OPTIONS"):
            return True
        return request.user.type == UserType.SHOWROOM

    def has_object_permission(self, request, view, obj):
        """Allow safe methods; restrict mutations to the order's showroom owner."""
        if request.method in SAFE_METHODS:
            return True
        return hasattr(request.user, "carshowroom") and obj.showroom.owner_user_id == request.user.id

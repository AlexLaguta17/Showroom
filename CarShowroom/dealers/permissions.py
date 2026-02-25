from rest_framework.permissions import SAFE_METHODS, BasePermission

from car_showrooms.models import CarShowroom
from services.choices import UserType


class IsProviderOrShowroom(BasePermission):
    """Check if user type is provider or showroom."""

    def has_permission(self, request, view):
        if request.method == "GET":
            return request.user.type in (UserType.PROVIDER, UserType.SHOWROOM)

        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return request.user.type == UserType.PROVIDER

        return True


class IsProviderOwner(BasePermission):
    """Check if user is Provider owner."""

    def has_permission(self, request, view):
        if request.method in ("HEAD", "OPTIONS"):
            return True

        return view.provider.owner_user_id == request.user.id


class IsProviderOwnerOrShowroom(BasePermission):
    """Check if user is provider owner or showroom read only"""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.id == obj.owner_user.id


class IsProviderOrShowroomOwner(BasePermission):

    def has_permission(self, request, view):
        if request.method in ("HEAD", "OPTIONS"):
            return True
        return view.provider.owner_user_id == request.user.id or hasattr(request.user, "carshowroom")



class IsProviderCarOwnerOrShowroom(BasePermission):
    """Check if user is provider car owner or showroom read only"""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.id == obj.provider.owner_user.id


class IsShowroomOwnerUser(BasePermission):
    """Check if user is showroom owner user."""

    def has_permission(self, request, view):
        if request.method in ("HEAD", "OPTIONS"):
            return True

        return request.user.type == UserType.SHOWROOM and CarShowroom.objects.filter(owner_user_id=request.user.id).exists()

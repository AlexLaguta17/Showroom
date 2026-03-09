"""Permission classes for the car_showrooms app."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from services.choices import UserType
from car_showrooms.models import ShowroomCar


class IsCarShowroomOwner(BasePermission):
    """Allow read access to anyone; restrict writes to showroom owners."""

    def has_permission(self, request, view):
        """Allow safe methods; require SHOWROOM type for mutations."""
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.type == UserType.SHOWROOM

    def has_object_permission(self, request, view, obj):
        """Allow safe methods; restrict mutations to the object's owner."""
        if request.method in SAFE_METHODS:
            return True

        return obj.owner_user.id == request.user.id


class IsShowroomCarOwner(BasePermission):
    """Allow read access to anyone; restrict mutations to the showroom owner."""

    def has_object_permission(self, request, view, obj):
        """Allow safe methods; restrict mutations to the car's showroom owner."""
        if request.method in SAFE_METHODS:
            return True

        if isinstance(obj, ShowroomCar):
            return obj.showroom.owner_user.id == request.user.id

        return False


class IsDiscountOwner(BasePermission):
    """Allow read access to anyone; restrict mutations to the discount owner."""

    def has_permission(self, request, view):
        """Allow safe methods; restrict mutations to the showroom owner."""
        if request.method in SAFE_METHODS:
            return True

        return view.showroom.owner_user.id == request.user.id

    def has_object_permission(self, request, view, obj):
        """Allow safe methods; restrict mutations to the discount owner."""
        if request.method in SAFE_METHODS:
            return True

        return obj.owner_user.id == request.user.id


class IsOrderViewer(BasePermission):
    """Control order visibility."""

    def has_permission(self, request, view):
        """Block providers from accessing showroom orders entirely."""
        if request.method in ("HEAD", "OPTIONS"):
            return True

        return request.user.type in (UserType.SHOWROOM, UserType.CUSTOMER)


class IsCustomer(BasePermission):
    """Allow only to UserType.CUSTOMER."""

    def has_permission(self, request, view):
        """Allow customer access."""
        if request.method in SAFE_METHODS:
            return True

        return request.user.type == UserType.CUSTOMER

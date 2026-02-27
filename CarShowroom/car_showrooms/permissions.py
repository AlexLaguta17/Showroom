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
    """Control order visibility.

    GET access:
    - Showroom owner: orders of his showroom
    - Customer: only his orders
    """

    def has_permission(self, request, view):
        """Block providers from accessing showroom orders entirely."""
        if request.user.type == UserType.PROVIDER:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """Restrict order detail access to the relevant showroom owner or customer."""
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if user.type == UserType.SHOWROOM:
            return obj.showroom.owner_user.id == user.id

        if user.type == UserType.CUSTOMER:
            return obj.car_buyer.id == user.id

        return False

from rest_framework.permissions import SAFE_METHODS, BasePermission

from services.choices import UserType
from car_showrooms.models import ShowroomCar


class IsCarShowroomOwner(BasePermission):
    """Check Car Showroom Owner permission"""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.type == UserType.SHOWROOM

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.owner_user.id == request.user.id


class IsShowroomCarOwner(BasePermission):
    """Check Showroom Car Owner permission"""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if isinstance(obj, ShowroomCar):
            return obj.showroom.owner_user.id == request.user.id

        return False


class IsDiscountOwner(BasePermission):
    """Check Discount Owner permission"""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return view.showroom.owner_user.id == request.user.id

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.owner_user.id == request.user.id


class IsOrderViewer(BasePermission):
    """
    GET access:
    - Showroom owner: orders of his showroom
    - Customer: only his orders
    """

    def has_permission(self, request, view):
        if request.user.type == UserType.PROVIDER:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if user.type == UserType.SHOWROOM:
            return obj.showroom.owner_user.id == user.id

        if user.type == UserType.CUSTOMER:
            return obj.car_buyer.id == user.id

        return False

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAnonymousForCreate(BasePermission):

    def has_permission(self, request, view):
        if view.action == "create":
            return not request.user.is_authenticated

        return True


class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj == request.user

from rest_framework.permissions import BasePermission


class IsGuestUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "guest")


class IsRegisteredUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "registered")

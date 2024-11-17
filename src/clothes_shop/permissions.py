from rest_framework.permissions import BasePermission


class IsGuest(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "guest")


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "customer")


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "admin")

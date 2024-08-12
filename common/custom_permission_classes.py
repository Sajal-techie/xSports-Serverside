from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsAcademy(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_academy


class IsPlayer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and not request.user.is_academy and not request.user.is_staff
        )


#  permission for both player and academy
class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and not request.user.is_staff

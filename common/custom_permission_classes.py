from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Custom permission to grant access only to admin users.

    Admin users are identified by the `is_staff` attribute on the user.

    Methods:
    - has_permission: Returns True if the user is authenticated and is an admin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsAcademy(BasePermission):
    """
    Custom permission to grant access only to academy users.

    Academy users are identified by the `is_academy` attribute on the user.

    Methods:
    - has_permission: Returns True if the user is authenticated and is an academy.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_academy


class IsPlayer(BasePermission):
    """
    Custom permission to grant access only to player users.

    Player users are identified by the absence of both 'is_academy' and 'is_staff' attributes.

    Methods:
    - has_permission: Returns True if the user is authenticated, not an academy, and not an admin.
    """
    def has_permission(self, request, view):
        return (
            request.user and not request.user.is_academy and not request.user.is_staff
        )


class IsUser(BasePermission):
    """
    Custom permission to grant access to both players and academy users, but not admins.

    Methods:
    - has_permission: Returns True if the user is authenticated and not an admin.
    """
    def has_permission(self, request, view):
        return request.user and not request.user.is_staff

from rest_framework.permissions import BasePermission


class IsPlatformAdmin(BasePermission):
    """Django staff members and users with the admin role."""

    message = "Administrator access required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or getattr(user, "role", None) == "admin")
        )

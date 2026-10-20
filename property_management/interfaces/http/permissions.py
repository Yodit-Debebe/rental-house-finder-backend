from rest_framework.permissions import BasePermission


class IsLandlord(BasePermission):
    """Only users whose role is 'landlord' may manage properties."""

    message = "Only landlords can manage properties."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == "landlord"
        )

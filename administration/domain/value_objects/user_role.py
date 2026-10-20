from enum import Enum


class AdminUserRole(str, Enum):
    """Roles an administrator may assign to a user."""

    TENANT = "tenant"
    LANDLORD = "landlord"
    ADMIN = "admin"

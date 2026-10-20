from dataclasses import dataclass

from administration.domain.value_objects import AdminUserRole


@dataclass
class ManagedUser:
    """The admin-facing view of a user account."""

    email: str
    full_name: str
    role: AdminUserRole
    is_active: bool
    is_staff: bool
    id: int | None = None

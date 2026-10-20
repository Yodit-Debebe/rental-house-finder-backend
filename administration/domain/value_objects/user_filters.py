from dataclasses import dataclass


@dataclass(frozen=True)
class UserFilters:
    """Criteria for narrowing the user list."""

    role: str | None = None
    is_active: bool | None = None
    search: str | None = None

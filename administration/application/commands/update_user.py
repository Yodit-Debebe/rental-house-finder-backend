from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateUserCommand:
    """Only the provided fields are changed; None means "keep the current value"."""

    user_id: int
    actor_id: int
    role: str | None = None
    is_active: bool | None = None

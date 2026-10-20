from dataclasses import dataclass

from identity.domain.value_objects import Email, Role


@dataclass
class User:
    """A registered user of the platform. Knows nothing about Django or a database."""

    email: Email
    full_name: str
    role: Role
    password_hash: str
    id: int | None = None

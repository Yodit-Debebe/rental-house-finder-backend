from dataclasses import dataclass

from identity.domain.value_objects import Role


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    full_name: str
    password: str
    role: str = Role.TENANT.value

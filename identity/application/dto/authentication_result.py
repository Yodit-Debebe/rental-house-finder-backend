from dataclasses import dataclass

from identity.domain.entities import User


@dataclass(frozen=True)
class AuthenticationResult:
    user: User
    token: str

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticateUserCommand:
    email: str
    password: str

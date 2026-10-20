from dataclasses import dataclass

from identity.application.exceptions import EmailAlreadyRegistered
from identity.application.ports import PasswordHasher, UserRepository
from identity.domain.entities import User
from identity.domain.value_objects import Email, Role


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    full_name: str
    password: str
    role: str = Role.TENANT.value


class RegisterUserUseCase:
    def __init__(self, repository: UserRepository, hasher: PasswordHasher):
        self._repository = repository
        self._hasher = hasher

    def execute(self, command: RegisterUserCommand) -> User:
        email = Email(command.email)

        if self._repository.get_by_email(email) is not None:
            raise EmailAlreadyRegistered(str(email))

        user = User(
            email=email,
            full_name=command.full_name.strip(),
            role=Role(command.role),
            password_hash=self._hasher.hash(command.password),
        )
        return self._repository.add(user)

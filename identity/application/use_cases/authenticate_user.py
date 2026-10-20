from dataclasses import dataclass

from identity.application.exceptions import InvalidCredentials
from identity.application.ports import PasswordHasher, TokenIssuer, UserRepository
from identity.domain.entities import User
from identity.domain.exceptions import InvalidEmail
from identity.domain.value_objects import Email


@dataclass(frozen=True)
class AuthenticateUserCommand:
    email: str
    password: str


@dataclass(frozen=True)
class AuthenticationResult:
    user: User
    token: str


class AuthenticateUserUseCase:
    def __init__(
        self,
        repository: UserRepository,
        hasher: PasswordHasher,
        token_issuer: TokenIssuer,
    ):
        self._repository = repository
        self._hasher = hasher
        self._token_issuer = token_issuer

    def execute(self, command: AuthenticateUserCommand) -> AuthenticationResult:
        try:
            email = Email(command.email)
        except InvalidEmail:
            # Do not leak why authentication failed.
            raise InvalidCredentials from None

        user = self._repository.get_by_email(email)
        if user is None or not self._hasher.verify(command.password, user.password_hash):
            raise InvalidCredentials

        return AuthenticationResult(user=user, token=self._token_issuer.issue(user))

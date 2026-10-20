from identity.application.commands import AuthenticateUserCommand
from identity.application.dto import AuthenticationResult
from identity.application.exceptions import InvalidCredentials
from identity.application.ports import PasswordHasher, TokenIssuer
from identity.domain.exceptions import InvalidEmail
from identity.domain.repositories import UserRepository
from identity.domain.value_objects import Email


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

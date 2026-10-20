from unittest import TestCase

from identity.application.exceptions import (
    EmailAlreadyRegistered,
    InvalidCredentials,
)
from identity.application.commands import (
    AuthenticateUserCommand,
    RegisterUserCommand,
)
from identity.application.ports import PasswordHasher, TokenIssuer
from identity.application.use_cases.authenticate_user import AuthenticateUserUseCase
from identity.application.use_cases.register_user import RegisterUserUseCase
from identity.domain.entities import User
from identity.domain.exceptions import InvalidEmail
from identity.domain.repositories import UserRepository
from identity.domain.value_objects import Email, Role


class InMemoryUserRepository(UserRepository):
    """Test double: behaves like a database, but lives in a dictionary."""

    def __init__(self):
        self._users: dict[str, User] = {}
        self._next_id = 1

    def get_by_email(self, email: Email) -> User | None:
        return self._users.get(email.value)

    def add(self, user: User) -> User:
        user.id = self._next_id
        self._users[user.email.value] = user
        self._next_id += 1
        return user


class FakePasswordHasher(PasswordHasher):
    def hash(self, raw_password: str) -> str:
        return f"hashed:{raw_password}"

    def verify(self, raw_password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{raw_password}"


class FakeTokenIssuer(TokenIssuer):
    def issue(self, user: User) -> str:
        return f"token-for-{user.email}"


def register_user(
    repository: UserRepository,
    hasher: PasswordHasher,
    email: str = "user@example.com",
    password: str = "secret-pass",
    role: str = Role.TENANT.value,
) -> User:
    return RegisterUserUseCase(repository, hasher).execute(
        RegisterUserCommand(
            email=email,
            full_name="Test User",
            password=password,
            role=role,
        )
    )


class RegisterUserUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryUserRepository()
        self.hasher = FakePasswordHasher()
        self.use_case = RegisterUserUseCase(self.repository, self.hasher)

    def test_registers_user_with_hashed_password(self):
        user = self.use_case.execute(
            RegisterUserCommand(
                email="user@example.com",
                full_name="Test User",
                password="secret-pass",
            )
        )

        self.assertEqual(user.password_hash, "hashed:secret-pass")
        self.assertNotEqual(user.password_hash, "secret-pass")

    def test_assigns_an_id(self):
        user = register_user(self.repository, self.hasher)

        self.assertEqual(user.id, 1)

    def test_normalizes_email(self):
        user = register_user(self.repository, self.hasher, email="  User@Example.COM ")

        self.assertEqual(user.email.value, "user@example.com")

    def test_rejects_duplicate_email_regardless_of_case(self):
        register_user(self.repository, self.hasher, email="user@example.com")

        with self.assertRaises(EmailAlreadyRegistered):
            register_user(self.repository, self.hasher, email="USER@example.com")

    def test_rejects_invalid_email(self):
        with self.assertRaises(InvalidEmail):
            register_user(self.repository, self.hasher, email="not-an-email")

    def test_parses_role(self):
        user = register_user(
            self.repository, self.hasher, role=Role.LANDLORD.value
        )

        self.assertEqual(user.role, Role.LANDLORD)


class AuthenticateUserUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryUserRepository()
        self.hasher = FakePasswordHasher()
        self.token_issuer = FakeTokenIssuer()
        self.use_case = AuthenticateUserUseCase(
            self.repository, self.hasher, self.token_issuer
        )
        register_user(self.repository, self.hasher, password="secret-pass")

    def authenticate(self, email="user@example.com", password="secret-pass"):
        return self.use_case.execute(
            AuthenticateUserCommand(email=email, password=password)
        )

    def test_returns_user_and_token_for_valid_credentials(self):
        result = self.authenticate()

        self.assertEqual(result.user.email.value, "user@example.com")
        self.assertEqual(result.token, "token-for-user@example.com")

    def test_rejects_wrong_password(self):
        with self.assertRaises(InvalidCredentials):
            self.authenticate(password="wrong-password")

    def test_rejects_unknown_email(self):
        with self.assertRaises(InvalidCredentials):
            self.authenticate(email="nobody@example.com")

    def test_invalid_email_format_does_not_leak_validation_error(self):
        with self.assertRaises(InvalidCredentials):
            self.authenticate(email="not-an-email")

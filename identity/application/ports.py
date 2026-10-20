from abc import ABC, abstractmethod

from identity.domain.entities import User
from identity.domain.value_objects import Email


class UserRepository(ABC):
    """Outbound port: persistence for users, provided by infrastructure."""

    @abstractmethod
    def get_by_email(self, email: Email) -> User | None:
        ...

    @abstractmethod
    def add(self, user: User) -> User:
        ...


class PasswordHasher(ABC):
    """Outbound port: password hashing, provided by infrastructure."""

    @abstractmethod
    def hash(self, raw_password: str) -> str:
        ...

    @abstractmethod
    def verify(self, raw_password: str, password_hash: str) -> bool:
        ...


class TokenIssuer(ABC):
    """Outbound port: issues an authentication token for a user.

    Today this is implemented with DRF tokens; a Keycloak adapter can replace
    it later without changing the use cases.
    """

    @abstractmethod
    def issue(self, user: User) -> str:
        ...

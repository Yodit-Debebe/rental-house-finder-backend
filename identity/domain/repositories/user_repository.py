from abc import ABC, abstractmethod

from identity.domain.entities import User
from identity.domain.value_objects import Email


class UserRepository(ABC):
    """Outbound port: persistence for users, implemented by infrastructure."""

    @abstractmethod
    def get_by_email(self, email: Email) -> User | None:
        ...

    @abstractmethod
    def add(self, user: User) -> User:
        ...

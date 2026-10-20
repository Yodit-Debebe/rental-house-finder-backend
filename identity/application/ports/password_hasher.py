from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Outbound port: password hashing, provided by infrastructure."""

    @abstractmethod
    def hash(self, raw_password: str) -> str:
        ...

    @abstractmethod
    def verify(self, raw_password: str, password_hash: str) -> bool:
        ...

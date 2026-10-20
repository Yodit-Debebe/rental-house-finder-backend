from abc import ABC, abstractmethod

from administration.domain.entities import ManagedUser
from administration.domain.value_objects import UserFilters


class UserAdminRepository(ABC):
    """Outbound port: admin access to user accounts."""

    @abstractmethod
    def list(self, filters: UserFilters) -> list[ManagedUser]:
        ...

    @abstractmethod
    def get(self, user_id: int) -> ManagedUser | None:
        ...

    @abstractmethod
    def save(self, user: ManagedUser) -> ManagedUser:
        ...

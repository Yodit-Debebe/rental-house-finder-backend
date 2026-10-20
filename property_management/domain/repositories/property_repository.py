from abc import ABC, abstractmethod

from property_management.domain.entities import Property


class PropertyRepository(ABC):
    """Outbound port: persistence for properties, implemented by infrastructure."""

    @abstractmethod
    def get(self, property_id: int) -> Property | None:
        ...

    @abstractmethod
    def list_by_landlord(self, landlord_id: int) -> list[Property]:
        ...

    @abstractmethod
    def add(self, property: Property) -> Property:
        ...

    @abstractmethod
    def save(self, property: Property) -> Property:
        ...

    @abstractmethod
    def delete(self, property_id: int) -> None:
        ...

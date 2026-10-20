from abc import ABC, abstractmethod

from property_management.domain.entities import Amenity


class AmenityRepository(ABC):
    """Outbound port: read access to the amenity catalog."""

    @abstractmethod
    def list_all(self) -> list[Amenity]:
        ...

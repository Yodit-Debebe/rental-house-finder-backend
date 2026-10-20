from abc import ABC, abstractmethod

from property_management.domain.entities import PropertyImage


class PropertyImageRepository(ABC):
    """Outbound port: image storage for properties."""

    @abstractmethod
    def list_by_property(self, property_id: int) -> list[PropertyImage]:
        ...

    @abstractmethod
    def get(self, image_id: int) -> PropertyImage | None:
        ...

    @abstractmethod
    def add(
        self,
        property_id: int,
        file_name: str,
        content: bytes,
        caption: str,
        is_cover: bool,
    ) -> PropertyImage:
        ...

    @abstractmethod
    def delete(self, image_id: int) -> None:
        ...

from property_management.domain.entities import Amenity
from property_management.domain.repositories import AmenityRepository


class ListAmenitiesUseCase:
    def __init__(self, repository: AmenityRepository):
        self._repository = repository

    def execute(self) -> list[Amenity]:
        return self._repository.list_all()

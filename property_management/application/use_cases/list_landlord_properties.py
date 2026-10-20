from property_management.application.queries import ListLandlordPropertiesQuery
from property_management.domain.entities import Property
from property_management.domain.repositories import PropertyRepository


class ListLandlordPropertiesUseCase:
    def __init__(self, repository: PropertyRepository):
        self._repository = repository

    def execute(self, query: ListLandlordPropertiesQuery) -> list[Property]:
        return self._repository.list_by_landlord(query.landlord_id)

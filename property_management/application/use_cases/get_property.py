from property_management.application.queries import GetPropertyQuery
from property_management.domain.entities import Property
from property_management.domain.exceptions import (
    NotPropertyOwner,
    PropertyNotFound,
)
from property_management.domain.repositories import PropertyRepository


class GetPropertyUseCase:
    def __init__(self, repository: PropertyRepository):
        self._repository = repository

    def execute(self, query: GetPropertyQuery) -> Property:
        property = self._repository.get(query.property_id)
        if property is None:
            raise PropertyNotFound(f"Property {query.property_id} was not found")
        if property.landlord_id != query.landlord_id:
            raise NotPropertyOwner("You do not own this property")
        return property

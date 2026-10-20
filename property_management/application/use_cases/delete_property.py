from property_management.application.commands import DeletePropertyCommand
from property_management.domain.exceptions import (
    NotPropertyOwner,
    PropertyNotFound,
)
from property_management.domain.repositories import PropertyRepository


class DeletePropertyUseCase:
    def __init__(self, repository: PropertyRepository):
        self._repository = repository

    def execute(self, command: DeletePropertyCommand) -> None:
        existing = self._repository.get(command.property_id)
        if existing is None:
            raise PropertyNotFound(f"Property {command.property_id} was not found")
        if existing.landlord_id != command.landlord_id:
            raise NotPropertyOwner("You do not own this property")

        self._repository.delete(command.property_id)

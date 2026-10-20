from property_management.application.commands import UpdatePropertyCommand
from property_management.domain.entities import Property
from property_management.domain.exceptions import (
    NotPropertyOwner,
    PropertyNotFound,
)
from property_management.domain.repositories import PropertyRepository
from property_management.domain.value_objects import Address


class UpdatePropertyUseCase:
    def __init__(self, repository: PropertyRepository):
        self._repository = repository

    def execute(self, command: UpdatePropertyCommand) -> Property:
        existing = self._repository.get(command.property_id)
        if existing is None:
            raise PropertyNotFound(f"Property {command.property_id} was not found")
        if existing.landlord_id != command.landlord_id:
            raise NotPropertyOwner("You do not own this property")

        updated = Property(
            id=existing.id,
            landlord_id=existing.landlord_id,
            title=command.title if command.title is not None else existing.title,
            description=(
                command.description
                if command.description is not None
                else existing.description
            ),
            address=Address(
                command.address if command.address is not None else existing.address.street,
                command.city if command.city is not None else existing.address.city,
            ),
            price=command.price if command.price is not None else existing.price,
            bedrooms=(
                command.bedrooms if command.bedrooms is not None else existing.bedrooms
            ),
            bathrooms=(
                command.bathrooms
                if command.bathrooms is not None
                else existing.bathrooms
            ),
            is_available=(
                command.is_available
                if command.is_available is not None
                else existing.is_available
            ),
            amenity_ids=(
                command.amenity_ids
                if command.amenity_ids is not None
                else existing.amenity_ids
            ),
        )
        return self._repository.save(updated)

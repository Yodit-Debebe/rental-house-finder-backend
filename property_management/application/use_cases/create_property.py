from property_management.application.commands import CreatePropertyCommand
from property_management.domain.entities import Property
from property_management.domain.repositories import PropertyRepository
from property_management.domain.value_objects import Address


class CreatePropertyUseCase:
    def __init__(self, repository: PropertyRepository):
        self._repository = repository

    def execute(self, command: CreatePropertyCommand) -> Property:
        property = Property(
            landlord_id=command.landlord_id,
            title=command.title,
            description=command.description,
            address=Address(command.address, command.city),
            price=command.price,
            bedrooms=command.bedrooms,
            bathrooms=command.bathrooms,
            is_available=command.is_available,
        )
        return self._repository.add(property)

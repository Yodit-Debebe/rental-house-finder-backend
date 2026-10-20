from property_management.application.commands import DeletePropertyImageCommand
from property_management.domain.exceptions import (
    NotPropertyOwner,
    PropertyImageNotFound,
    PropertyNotFound,
)
from property_management.domain.repositories import (
    PropertyImageRepository,
    PropertyRepository,
)


class DeletePropertyImageUseCase:
    def __init__(
        self,
        property_repository: PropertyRepository,
        image_repository: PropertyImageRepository,
    ):
        self._property_repository = property_repository
        self._image_repository = image_repository

    def execute(self, command: DeletePropertyImageCommand) -> None:
        property = self._property_repository.get(command.property_id)
        if property is None:
            raise PropertyNotFound(f"Property {command.property_id} was not found")
        if property.landlord_id != command.landlord_id:
            raise NotPropertyOwner("You do not own this property")

        image = self._image_repository.get(command.image_id)
        if image is None or image.property_id != command.property_id:
            raise PropertyImageNotFound(
                f"Image {command.image_id} was not found on this property"
            )

        self._image_repository.delete(command.image_id)

from property_management.application.commands import UploadPropertyImageCommand
from property_management.domain.entities import PropertyImage
from property_management.domain.exceptions import (
    NotPropertyOwner,
    PropertyNotFound,
)
from property_management.domain.repositories import (
    PropertyImageRepository,
    PropertyRepository,
)


class UploadPropertyImageUseCase:
    def __init__(
        self,
        property_repository: PropertyRepository,
        image_repository: PropertyImageRepository,
    ):
        self._property_repository = property_repository
        self._image_repository = image_repository

    def execute(self, command: UploadPropertyImageCommand) -> PropertyImage:
        property = self._property_repository.get(command.property_id)
        if property is None:
            raise PropertyNotFound(f"Property {command.property_id} was not found")
        if property.landlord_id != command.landlord_id:
            raise NotPropertyOwner("You do not own this property")

        return self._image_repository.add(
            property_id=property.id,
            file_name=command.file_name,
            content=command.content,
            caption=command.caption,
            is_cover=command.is_cover,
        )

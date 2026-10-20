from property_management.domain.entities import Amenity
from property_management.domain.repositories import AmenityRepository
from property_management.models import Amenity as AmenityModel


class DjangoAmenityRepository(AmenityRepository):
    """Implements the AmenityRepository port with the Django ORM."""

    def list_all(self) -> list[Amenity]:
        return [
            Amenity(id=row.pk, name=row.name)
            for row in AmenityModel.objects.all()
        ]

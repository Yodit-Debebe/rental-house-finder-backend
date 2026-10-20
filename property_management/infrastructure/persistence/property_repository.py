from property_management.domain.entities import Property
from property_management.domain.repositories import PropertyRepository
from property_management.domain.value_objects import Address
from property_management.models import Property as PropertyModel


class DjangoPropertyRepository(PropertyRepository):
    """Implements the PropertyRepository port with the Django ORM."""

    def get(self, property_id: int) -> Property | None:
        row = PropertyModel.objects.filter(pk=property_id).first()
        return self._to_domain(row) if row is not None else None

    def list_by_landlord(self, landlord_id: int) -> list[Property]:
        rows = PropertyModel.objects.filter(landlord_id=landlord_id)
        return [self._to_domain(row) for row in rows]

    def add(self, property: Property) -> Property:
        row = PropertyModel.objects.create(
            landlord_id=property.landlord_id,
            title=property.title,
            description=property.description,
            address=property.address.street,
            city=property.address.city,
            price=property.price,
            bedrooms=property.bedrooms,
            bathrooms=property.bathrooms,
            is_available=property.is_available,
        )
        return self._to_domain(row)

    def save(self, property: Property) -> Property:
        if property.id is None:
            raise ValueError("Cannot save a property without an id")

        PropertyModel.objects.filter(pk=property.id).update(
            title=property.title,
            description=property.description,
            address=property.address.street,
            city=property.address.city,
            price=property.price,
            bedrooms=property.bedrooms,
            bathrooms=property.bathrooms,
            is_available=property.is_available,
        )
        return self.get(property.id)

    def delete(self, property_id: int) -> None:
        PropertyModel.objects.filter(pk=property_id).delete()

    @staticmethod
    def _to_domain(row: PropertyModel) -> Property:
        return Property(
            id=row.pk,
            landlord_id=row.landlord_id,
            title=row.title,
            description=row.description,
            address=Address(row.address, row.city),
            price=row.price,
            bedrooms=row.bedrooms,
            bathrooms=row.bathrooms,
            is_available=row.is_available,
        )

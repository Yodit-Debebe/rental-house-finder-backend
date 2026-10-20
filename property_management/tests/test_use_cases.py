from decimal import Decimal
from unittest import TestCase

from property_management.application.commands import (
    CreatePropertyCommand,
    DeletePropertyCommand,
    UpdatePropertyCommand,
)
from property_management.application.queries import (
    GetPropertyQuery,
    ListLandlordPropertiesQuery,
)
from property_management.application.use_cases import (
    CreatePropertyUseCase,
    DeletePropertyUseCase,
    GetPropertyUseCase,
    ListLandlordPropertiesUseCase,
    UpdatePropertyUseCase,
)
from property_management.domain.entities import Property
from property_management.domain.exceptions import (
    NotPropertyOwner,
    PropertyNotFound,
)
from property_management.domain.repositories import PropertyRepository


class InMemoryPropertyRepository(PropertyRepository):
    """Test double: behaves like a database, but lives in a dictionary."""

    def __init__(self):
        self._properties: dict[int, Property] = {}
        self._next_id = 1

    def get(self, property_id: int) -> Property | None:
        return self._properties.get(property_id)

    def list_by_landlord(self, landlord_id: int) -> list[Property]:
        return [
            item
            for item in self._properties.values()
            if item.landlord_id == landlord_id
        ]

    def add(self, property: Property) -> Property:
        property.id = self._next_id
        self._properties[property.id] = property
        self._next_id += 1
        return property

    def save(self, property: Property) -> Property:
        self._properties[property.id] = property
        return property

    def delete(self, property_id: int) -> None:
        del self._properties[property_id]


def create_property(
    repository: PropertyRepository,
    landlord_id: int = 1,
    **overrides,
) -> Property:
    values = {
        "landlord_id": landlord_id,
        "title": "2-bedroom apartment",
        "description": "Near the market",
        "address": "Bole Road 12",
        "city": "Addis Ababa",
        "price": Decimal("15000.00"),
        "bedrooms": 2,
        "bathrooms": 1,
    }
    values.update(overrides)
    return CreatePropertyUseCase(repository).execute(
        CreatePropertyCommand(**values)
    )


class CreatePropertyUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryPropertyRepository()
        self.use_case = CreatePropertyUseCase(self.repository)

    def test_persists_and_assigns_an_id(self):
        property = create_property(self.repository)

        self.assertEqual(property.id, 1)
        self.assertEqual(self.repository.get(1), property)

    def test_builds_address_from_command(self):
        property = create_property(self.repository, city="Bahir Dar")

        self.assertEqual(property.address.street, "Bole Road 12")
        self.assertEqual(property.address.city, "Bahir Dar")


class UpdatePropertyUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryPropertyRepository()
        self.property = create_property(self.repository)
        self.use_case = UpdatePropertyUseCase(self.repository)

    def test_changes_only_provided_fields(self):
        updated = self.use_case.execute(
            UpdatePropertyCommand(
                property_id=self.property.id,
                landlord_id=1,
                title="Renovated apartment",
            )
        )

        self.assertEqual(updated.title, "Renovated apartment")
        self.assertEqual(updated.price, Decimal("15000.00"))
        self.assertEqual(updated.bedrooms, 2)
        self.assertEqual(updated.address.city, "Addis Ababa")

    def test_can_change_availability(self):
        updated = self.use_case.execute(
            UpdatePropertyCommand(
                property_id=self.property.id,
                landlord_id=1,
                is_available=False,
            )
        )

        self.assertFalse(updated.is_available)

    def test_missing_property_raises(self):
        with self.assertRaises(PropertyNotFound):
            self.use_case.execute(
                UpdatePropertyCommand(property_id=999, landlord_id=1, title="x")
            )

    def test_other_landlord_cannot_update(self):
        with self.assertRaises(NotPropertyOwner):
            self.use_case.execute(
                UpdatePropertyCommand(
                    property_id=self.property.id, landlord_id=2, title="Hijacked"
                )
            )


class DeletePropertyUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryPropertyRepository()
        self.property = create_property(self.repository)
        self.use_case = DeletePropertyUseCase(self.repository)

    def test_deletes_own_property(self):
        self.use_case.execute(
            DeletePropertyCommand(property_id=self.property.id, landlord_id=1)
        )

        self.assertIsNone(self.repository.get(self.property.id))

    def test_missing_property_raises(self):
        with self.assertRaises(PropertyNotFound):
            self.use_case.execute(
                DeletePropertyCommand(property_id=999, landlord_id=1)
            )

    def test_other_landlord_cannot_delete(self):
        with self.assertRaises(NotPropertyOwner):
            self.use_case.execute(
                DeletePropertyCommand(property_id=self.property.id, landlord_id=2)
            )
        self.assertIsNotNone(self.repository.get(self.property.id))


class ListLandlordPropertiesUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryPropertyRepository()
        create_property(self.repository, landlord_id=1, title="First")
        create_property(self.repository, landlord_id=1, title="Second")
        create_property(self.repository, landlord_id=2, title="Not mine")
        self.use_case = ListLandlordPropertiesUseCase(self.repository)

    def test_returns_only_properties_of_the_landlord(self):
        properties = self.use_case.execute(
            ListLandlordPropertiesQuery(landlord_id=1)
        )

        self.assertEqual([item.title for item in properties], ["First", "Second"])


class GetPropertyUseCaseTests(TestCase):
    def setUp(self):
        self.repository = InMemoryPropertyRepository()
        self.property = create_property(self.repository, landlord_id=1)
        self.use_case = GetPropertyUseCase(self.repository)

    def test_returns_own_property(self):
        found = self.use_case.execute(
            GetPropertyQuery(property_id=self.property.id, landlord_id=1)
        )

        self.assertEqual(found, self.property)

    def test_missing_property_raises(self):
        with self.assertRaises(PropertyNotFound):
            self.use_case.execute(GetPropertyQuery(property_id=999, landlord_id=1))

    def test_other_landlord_cannot_read(self):
        with self.assertRaises(NotPropertyOwner):
            self.use_case.execute(
                GetPropertyQuery(property_id=self.property.id, landlord_id=2)
            )

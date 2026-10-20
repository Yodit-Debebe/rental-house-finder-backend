from decimal import Decimal
from unittest import TestCase

from property_management.application.commands import (
    CreatePropertyCommand,
    DeletePropertyCommand,
    DeletePropertyImageCommand,
    UpdatePropertyCommand,
    UploadPropertyImageCommand,
)
from property_management.application.queries import (
    GetPropertyQuery,
    ListLandlordPropertiesQuery,
)
from property_management.application.use_cases import (
    CreatePropertyUseCase,
    DeletePropertyImageUseCase,
    DeletePropertyUseCase,
    GetPropertyUseCase,
    ListAmenitiesUseCase,
    ListLandlordPropertiesUseCase,
    UpdatePropertyUseCase,
    UploadPropertyImageUseCase,
)
from property_management.domain.entities import (
    Amenity,
    Property,
    PropertyImage,
)
from property_management.domain.exceptions import (
    NotPropertyOwner,
    PropertyImageNotFound,
    PropertyNotFound,
)
from property_management.domain.repositories import (
    AmenityRepository,
    PropertyImageRepository,
    PropertyRepository,
)


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


class FakeAmenityRepository(AmenityRepository):
    def list_all(self):
        return [Amenity(id=1, name="Parking"), Amenity(id=2, name="WiFi")]


class InMemoryPropertyImageRepository(PropertyImageRepository):
    def __init__(self):
        self._images: dict[int, PropertyImage] = {}
        self._next_id = 1

    def list_by_property(self, property_id: int) -> list[PropertyImage]:
        return [
            image
            for image in self._images.values()
            if image.property_id == property_id
        ]

    def get(self, image_id: int) -> PropertyImage | None:
        return self._images.get(image_id)

    def add(
        self,
        property_id: int,
        file_name: str,
        content: bytes,
        caption: str,
        is_cover: bool,
    ) -> PropertyImage:
        image = PropertyImage(
            id=self._next_id,
            property_id=property_id,
            url=f"/media/{file_name}",
            caption=caption.strip(),
            is_cover=is_cover,
        )
        self._images[image.id] = image
        self._next_id += 1
        return image

    def delete(self, image_id: int) -> None:
        del self._images[image_id]


class ListAmenitiesUseCaseTests(TestCase):
    def test_returns_catalog(self):
        amenities = ListAmenitiesUseCase(FakeAmenityRepository()).execute()

        self.assertEqual([item.name for item in amenities], ["Parking", "WiFi"])


class CreatePropertyWithAmenitiesTests(TestCase):
    def test_passes_amenity_ids_to_the_property(self):
        repository = InMemoryPropertyRepository()

        property = create_property(repository, amenity_ids=[2, 1])

        self.assertEqual(property.amenity_ids, [1, 2])
        self.assertEqual(repository.get(property.id).amenity_ids, [1, 2])


class UploadPropertyImageUseCaseTests(TestCase):
    def setUp(self):
        self.properties = InMemoryPropertyRepository()
        self.images = InMemoryPropertyImageRepository()
        self.property = create_property(self.properties)
        self.use_case = UploadPropertyImageUseCase(self.properties, self.images)

    def execute(self, **overrides):
        values = {
            "property_id": self.property.id,
            "landlord_id": 1,
            "file_name": "cover.png",
            "content": b"fake-image-bytes",
            "caption": "Living room",
            "is_cover": True,
        }
        values.update(overrides)
        return self.use_case.execute(UploadPropertyImageCommand(**values))

    def test_uploads_image_to_own_property(self):
        image = self.execute()

        self.assertEqual(image.property_id, self.property.id)
        self.assertEqual(image.url, "/media/cover.png")
        self.assertTrue(image.is_cover)

    def test_strips_caption(self):
        image = self.execute(caption="  Living room  ")

        self.assertEqual(image.caption, "Living room")

    def test_missing_property_raises(self):
        with self.assertRaises(PropertyNotFound):
            self.execute(property_id=999)

    def test_other_landlord_cannot_upload(self):
        with self.assertRaises(NotPropertyOwner):
            self.execute(landlord_id=2)

        self.assertEqual(self.images.list_by_property(self.property.id), [])


class DeletePropertyImageUseCaseTests(TestCase):
    def setUp(self):
        self.properties = InMemoryPropertyRepository()
        self.images = InMemoryPropertyImageRepository()
        self.property = create_property(self.properties)
        self.image = UploadPropertyImageUseCase(
            self.properties, self.images
        ).execute(
            UploadPropertyImageCommand(
                property_id=self.property.id,
                landlord_id=1,
                file_name="cover.png",
                content=b"fake-image-bytes",
            )
        )
        self.use_case = DeletePropertyImageUseCase(self.properties, self.images)

    def test_deletes_own_image(self):
        self.use_case.execute(
            DeletePropertyImageCommand(
                property_id=self.property.id,
                image_id=self.image.id,
                landlord_id=1,
            )
        )

        self.assertIsNone(self.images.get(self.image.id))

    def test_other_landlord_cannot_delete(self):
        with self.assertRaises(NotPropertyOwner):
            self.use_case.execute(
                DeletePropertyImageCommand(
                    property_id=self.property.id,
                    image_id=self.image.id,
                    landlord_id=2,
                )
            )
        self.assertIsNotNone(self.images.get(self.image.id))

    def test_image_must_belong_to_the_property(self):
        other_property = create_property(self.properties, title="Other")

        with self.assertRaises(PropertyImageNotFound):
            self.use_case.execute(
                DeletePropertyImageCommand(
                    property_id=other_property.id,
                    image_id=self.image.id,
                    landlord_id=1,
                )
            )

import io
import os
import shutil
import tempfile
from decimal import Decimal

from django.core.files.storage import default_storage, storages
from django.test import TestCase, override_settings
from django.utils.functional import empty
from PIL import Image

from identity.models import User
from property_management.domain.entities import Property
from property_management.domain.exceptions import InvalidAmenity
from property_management.domain.value_objects import Address
from property_management.infrastructure.persistence import (
    DjangoAmenityRepository,
    DjangoPropertyImageRepository,
    DjangoPropertyRepository,
)
from property_management.models import Amenity as AmenityModel
from property_management.models import Property as PropertyModel
from property_management.models import PropertyImage as PropertyImageModel

FAST_HASHING = override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]
)


class TempMediaMixin:
    """Point file storage at a throwaway directory for each test."""

    def setUp(self):
        super().setUp()
        self._media_root = tempfile.mkdtemp()
        self._media_override = override_settings(MEDIA_ROOT=self._media_root)
        self._media_override.enable()
        storages._storages = {}
        default_storage._wrapped = empty

    def tearDown(self):
        self._media_override.disable()
        storages._storages = {}
        default_storage._wrapped = empty
        shutil.rmtree(self._media_root, ignore_errors=True)
        super().tearDown()


def png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "red").save(buffer, format="PNG")
    return buffer.getvalue()


@FAST_HASHING
class DjangoPropertyRepositoryTests(TestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(
            email="landlord@example.com",
            password="secret-pass",
            full_name="Landlord",
            role="landlord",
        )
        self.other_landlord = User.objects.create_user(
            email="other@example.com",
            password="secret-pass",
            full_name="Other Landlord",
            role="landlord",
        )
        self.repository = DjangoPropertyRepository()

    def make_property(self, landlord_id=None, **overrides) -> Property:
        values = {
            "landlord_id": landlord_id or self.landlord.id,
            "title": "2-bedroom apartment",
            "description": "Near the market",
            "address": Address("Bole Road 12", "Addis Ababa"),
            "price": Decimal("15000.00"),
            "bedrooms": 2,
            "bathrooms": 1,
        }
        values.update(overrides)
        return Property(**values)

    def test_add_persists_and_returns_property_with_id(self):
        saved = self.repository.add(self.make_property())

        self.assertIsNotNone(saved.id)
        self.assertEqual(saved.landlord_id, self.landlord.id)

    def test_get_returns_domain_property(self):
        saved = self.repository.add(self.make_property())

        found = self.repository.get(saved.id)

        self.assertEqual(found.title, "2-bedroom apartment")
        self.assertEqual(found.address, Address("Bole Road 12", "Addis Ababa"))
        self.assertEqual(found.price, Decimal("15000.00"))

    def test_get_returns_none_when_missing(self):
        self.assertIsNone(self.repository.get(999))

    def test_list_by_landlord_filters_ownership(self):
        self.repository.add(self.make_property(title="Mine"))
        self.repository.add(
            self.make_property(landlord_id=self.other_landlord.id, title="Not mine")
        )

        properties = self.repository.list_by_landlord(self.landlord.id)

        self.assertEqual([item.title for item in properties], ["Mine"])

    def test_save_updates_fields(self):
        saved = self.repository.add(self.make_property())
        saved.title = "Renovated"
        saved.is_available = False

        self.repository.save(saved)

        found = self.repository.get(saved.id)
        self.assertEqual(found.title, "Renovated")
        self.assertFalse(found.is_available)

    def test_delete_removes_property(self):
        saved = self.repository.add(self.make_property())

        self.repository.delete(saved.id)

        self.assertIsNone(self.repository.get(saved.id))


class DjangoAmenityRepositoryTests(TestCase):
    def test_lists_amenities_ordered_by_name(self):
        AmenityModel.objects.create(name="WiFi")
        AmenityModel.objects.create(name="Parking")

        amenities = DjangoAmenityRepository().list_all()

        self.assertEqual([item.name for item in amenities], ["Parking", "WiFi"])


@FAST_HASHING
class PropertyAmenityPersistenceTests(TestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(
            email="landlord@example.com",
            password="secret-pass",
            full_name="Landlord",
            role="landlord",
        )
        self.parking = AmenityModel.objects.create(name="Parking")
        self.wifi = AmenityModel.objects.create(name="WiFi")
        self.repository = DjangoPropertyRepository()

    def make_property(self, amenity_ids=None) -> Property:
        return Property(
            landlord_id=self.landlord.id,
            title="Apartment",
            description="Nice",
            address=Address("Bole Road 12", "Addis Ababa"),
            price=Decimal("15000.00"),
            bedrooms=2,
            bathrooms=1,
            amenity_ids=amenity_ids or [],
        )

    def test_add_stores_amenities(self):
        saved = self.repository.add(
            self.make_property([self.parking.id, self.wifi.id])
        )

        self.assertEqual(
            saved.amenity_ids, sorted([self.parking.id, self.wifi.id])
        )

    def test_save_replaces_amenities(self):
        saved = self.repository.add(self.make_property([self.parking.id]))
        saved.amenity_ids = [self.wifi.id]

        updated = self.repository.save(saved)

        self.assertEqual(updated.amenity_ids, [self.wifi.id])

    def test_unknown_amenity_raises(self):
        with self.assertRaises(InvalidAmenity):
            self.repository.add(self.make_property([999]))


@FAST_HASHING
class DjangoPropertyImageRepositoryTests(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.landlord = User.objects.create_user(
            email="landlord@example.com",
            password="secret-pass",
            full_name="Landlord",
            role="landlord",
        )
        self.property = PropertyModel.objects.create(
            landlord=self.landlord,
            title="Apartment",
            address="Bole Road 12",
            city="Addis Ababa",
            price=Decimal("15000.00"),
            bedrooms=2,
            bathrooms=1,
        )
        self.repository = DjangoPropertyImageRepository()

    def add_image(self, name="cover.png", is_cover=False):
        return self.repository.add(
            self.property.id, name, png_bytes(), "  Living room  ", is_cover
        )

    def test_add_persists_image_and_strips_caption(self):
        image = self.add_image()

        self.assertIsNotNone(image.id)
        self.assertEqual(image.caption, "Living room")
        self.assertTrue(image.url.endswith("cover.png"))

    def test_first_image_becomes_cover(self):
        image = self.add_image()

        self.assertTrue(image.is_cover)

    def test_explicit_cover_replaces_previous_cover(self):
        first = self.add_image("first.png")
        second = self.add_image("second.png", is_cover=True)

        self.assertFalse(self.repository.get(first.id).is_cover)
        self.assertTrue(self.repository.get(second.id).is_cover)

    def test_list_returns_cover_first(self):
        self.add_image("first.png")
        self.add_image("second.png", is_cover=True)

        images = self.repository.list_by_property(self.property.id)

        self.assertEqual(len(images), 2)
        self.assertTrue(images[0].is_cover)

    def test_delete_removes_row_and_file(self):
        image = self.add_image()
        row = PropertyImageModel.objects.get(pk=image.id)
        file_path = row.image.path

        self.repository.delete(image.id)

        self.assertIsNone(self.repository.get(image.id))
        self.assertFalse(PropertyImageModel.objects.filter(pk=image.id).exists())
        self.assertFalse(os.path.exists(file_path))

    def test_get_returns_none_when_missing(self):
        self.assertIsNone(self.repository.get(999))

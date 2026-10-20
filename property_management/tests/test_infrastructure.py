from decimal import Decimal

from django.test import TestCase, override_settings

from identity.models import User
from property_management.domain.entities import Property
from property_management.domain.value_objects import Address
from property_management.infrastructure.persistence import DjangoPropertyRepository

FAST_HASHING = override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]
)


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

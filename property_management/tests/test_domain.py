from decimal import Decimal
from unittest import TestCase

from property_management.domain.entities import Property
from property_management.domain.exceptions import InvalidProperty
from property_management.domain.value_objects import Address


def make_property(**overrides) -> Property:
    values = {
        "landlord_id": 1,
        "title": "2-bedroom apartment",
        "description": "Near the market",
        "address": Address("Bole Road 12", "Addis Ababa"),
        "price": Decimal("15000.00"),
        "bedrooms": 2,
        "bathrooms": 1,
    }
    values.update(overrides)
    return Property(**values)


class AddressTests(TestCase):
    def test_strips_whitespace(self):
        address = Address("  Bole Road 12  ", "  Addis Ababa  ")

        self.assertEqual(address.street, "Bole Road 12")
        self.assertEqual(address.city, "Addis Ababa")

    def test_rejects_blank_street(self):
        with self.assertRaises(InvalidProperty):
            Address("   ", "Addis Ababa")

    def test_rejects_blank_city(self):
        with self.assertRaises(InvalidProperty):
            Address("Bole Road 12", "   ")


class PropertyTests(TestCase):
    def test_strips_text_fields(self):
        property = make_property(title="  Apartment  ", description="  Nice  ")

        self.assertEqual(property.title, "Apartment")
        self.assertEqual(property.description, "Nice")

    def test_rejects_blank_title(self):
        with self.assertRaises(InvalidProperty):
            make_property(title="   ")

    def test_rejects_negative_price(self):
        with self.assertRaises(InvalidProperty):
            make_property(price=Decimal("-1.00"))

    def test_rejects_negative_bedrooms(self):
        with self.assertRaises(InvalidProperty):
            make_property(bedrooms=-1)

    def test_rejects_negative_bathrooms(self):
        with self.assertRaises(InvalidProperty):
            make_property(bathrooms=-1)

    def test_coerces_price_to_decimal(self):
        property = make_property(price="15000.50")

        self.assertEqual(property.price, Decimal("15000.50"))

    def test_is_available_defaults_to_true(self):
        self.assertTrue(make_property().is_available)

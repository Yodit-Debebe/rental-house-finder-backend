from dataclasses import FrozenInstanceError
from unittest import TestCase

from identity.domain.entities import User
from identity.domain.exceptions import InvalidEmail
from identity.domain.value_objects import Email, Role


class EmailTests(TestCase):
    def test_normalizes_whitespace_and_case(self):
        email = Email("  User@Example.COM  ")

        self.assertEqual(email.value, "user@example.com")

    def test_rejects_invalid_addresses(self):
        invalid_values = [
            "",
            "plain-text",
            "user@example",
            "user@@example.com",
            "user name@example.com",
        ]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(InvalidEmail):
                    Email(value)

    def test_is_immutable(self):
        email = Email("user@example.com")

        with self.assertRaises(FrozenInstanceError):
            email.value = "other@example.com"

    def test_equality_uses_normalized_value(self):
        self.assertEqual(Email("User@Example.com"), Email("user@example.com"))


class RoleTests(TestCase):
    def test_lookup_by_value(self):
        self.assertEqual(Role("tenant"), Role.TENANT)

    def test_values(self):
        self.assertEqual(Role.LANDLORD.value, "landlord")


class UserTests(TestCase):
    def test_id_defaults_to_none(self):
        user = User(
            email=Email("user@example.com"),
            full_name="Test User",
            role=Role.TENANT,
            password_hash="hashed",
        )

        self.assertIsNone(user.id)

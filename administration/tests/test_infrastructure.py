from django.test import TestCase, override_settings

from administration.domain.entities import ManagedUser
from administration.domain.value_objects import AdminUserRole, UserFilters
from administration.infrastructure.persistence import DjangoUserAdminRepository
from identity.models import User

FAST_HASHING = override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]
)


@FAST_HASHING
class DjangoUserAdminRepositoryTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            email="alice@example.com",
            password="secret-pass",
            full_name="Alice Landlord",
            role="landlord",
        )
        self.bob = User.objects.create_user(
            email="bob@example.com",
            password="secret-pass",
            full_name="Bob Tenant",
            role="tenant",
        )
        self.carol = User.objects.create_user(
            email="carol@example.com",
            password="secret-pass",
            full_name="Carol Tenant",
            role="tenant",
            is_active=False,
        )
        self.repository = DjangoUserAdminRepository()

    def test_lists_all_users(self):
        self.assertEqual(len(self.repository.list(UserFilters())), 3)

    def test_filters_by_role(self):
        users = self.repository.list(UserFilters(role="tenant"))

        self.assertEqual(
            [user.email for user in users],
            ["bob@example.com", "carol@example.com"],
        )

    def test_filters_by_active_status(self):
        users = self.repository.list(UserFilters(is_active=False))

        self.assertEqual([user.email for user in users], ["carol@example.com"])

    def test_searches_email_and_full_name(self):
        by_name = self.repository.list(UserFilters(search="alice"))
        by_email = self.repository.list(UserFilters(search="bob@"))

        self.assertEqual([user.full_name for user in by_name], ["Alice Landlord"])
        self.assertEqual([user.full_name for user in by_email], ["Bob Tenant"])

    def test_get_returns_managed_user(self):
        user = self.repository.get(self.alice.id)

        self.assertEqual(user.email, "alice@example.com")
        self.assertEqual(user.role, AdminUserRole.LANDLORD)

    def test_get_returns_none_when_missing(self):
        self.assertIsNone(self.repository.get(999))

    def test_save_updates_role_and_status(self):
        user = self.repository.get(self.bob.id)
        user.role = AdminUserRole.ADMIN
        user.is_active = False

        self.repository.save(user)

        saved = self.repository.get(self.bob.id)
        self.assertEqual(saved.role, AdminUserRole.ADMIN)
        self.assertFalse(saved.is_active)
        self.assertFalse(User.objects.get(pk=self.bob.id).is_active)

    def test_save_requires_id(self):
        with self.assertRaises(ValueError):
            self.repository.save(
                ManagedUser(
                    email="new@example.com",
                    full_name="New",
                    role=AdminUserRole.TENANT,
                    is_active=True,
                    is_staff=False,
                )
            )

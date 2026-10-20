from django.test import TestCase, override_settings

from identity.application.exceptions import EmailAlreadyRegistered
from identity.domain.entities import User
from identity.domain.value_objects import Email, Role
from identity.infrastructure.persistence import DjangoUserRepository
from identity.infrastructure.security import DRFTokenIssuer, DjangoPasswordHasher
from identity.models import User as UserModel

# Production-strength hashing is deliberately slow; tests do not need it.
FAST_HASHING = override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]
)


@FAST_HASHING
class DjangoUserRepositoryTests(TestCase):
    def setUp(self):
        self.repository = DjangoUserRepository()
        self.hasher = DjangoPasswordHasher()

    def make_user(self, email="user@example.com", role=Role.TENANT) -> User:
        return User(
            email=Email(email),
            full_name="Test User",
            role=role,
            password_hash=self.hasher.hash("secret-pass"),
        )

    def test_add_persists_and_returns_user_with_id(self):
        saved = self.repository.add(self.make_user())

        self.assertIsNotNone(saved.id)
        self.assertTrue(UserModel.objects.filter(pk=saved.id).exists())

    def test_get_by_email_returns_domain_user(self):
        self.repository.add(self.make_user())

        found = self.repository.get_by_email(Email("user@example.com"))

        self.assertIsNotNone(found)
        self.assertEqual(found.email, Email("user@example.com"))
        self.assertEqual(found.full_name, "Test User")
        self.assertEqual(found.role, Role.TENANT)

    def test_get_by_email_returns_none_when_missing(self):
        self.assertIsNone(self.repository.get_by_email(Email("nobody@example.com")))

    def test_duplicate_email_raises(self):
        self.repository.add(self.make_user())

        with self.assertRaises(EmailAlreadyRegistered):
            self.repository.add(self.make_user(email="USER@example.com"))

    def test_password_hash_is_stored_unchanged(self):
        user = self.make_user()

        saved = self.repository.add(user)

        row = UserModel.objects.get(pk=saved.id)
        self.assertEqual(row.password, user.password_hash)

    def test_round_trips_role(self):
        saved = self.repository.add(self.make_user(role=Role.LANDLORD))

        found = self.repository.get_by_email(saved.email)

        self.assertEqual(found.role, Role.LANDLORD)


@FAST_HASHING
class DjangoPasswordHasherTests(TestCase):
    def setUp(self):
        self.hasher = DjangoPasswordHasher()

    def test_hash_is_verifiable(self):
        hashed = self.hasher.hash("secret-pass")

        self.assertTrue(self.hasher.verify("secret-pass", hashed))
        self.assertFalse(self.hasher.verify("wrong-password", hashed))

    def test_hash_is_not_plaintext(self):
        self.assertNotEqual(self.hasher.hash("secret-pass"), "secret-pass")

    def test_hash_is_salted(self):
        self.assertNotEqual(
            self.hasher.hash("secret-pass"), self.hasher.hash("secret-pass")
        )


@FAST_HASHING
class DRFTokenIssuerTests(TestCase):
    def setUp(self):
        self.repository = DjangoUserRepository()
        self.hasher = DjangoPasswordHasher()
        self.issuer = DRFTokenIssuer()
        self.user = self.repository.add(
            User(
                email=Email("token@example.com"),
                full_name="Token User",
                role=Role.TENANT,
                password_hash=self.hasher.hash("secret-pass"),
            )
        )

    def test_issues_a_token(self):
        self.assertTrue(self.issuer.issue(self.user))

    def test_returns_same_token_on_reissue(self):
        first = self.issuer.issue(self.user)
        second = self.issuer.issue(self.user)

        self.assertEqual(first, second)

from django.test import override_settings
from rest_framework.test import APITestCase

from identity.models import User as UserModel

FAST_HASHING = override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]
)

REGISTER_URL = "/api/identity/register/"
LOGIN_URL = "/api/identity/login/"
ME_URL = "/api/identity/me/"


@FAST_HASHING
class IdentityApiTests(APITestCase):
    def register(self, **overrides):
        payload = {
            "email": "user@example.com",
            "full_name": "Test User",
            "password": "secret-pass",
            "role": "tenant",
        }
        payload.update(overrides)
        return self.client.post(REGISTER_URL, payload, format="json")

    def login(self, email="user@example.com", password="secret-pass"):
        return self.client.post(
            LOGIN_URL, {"email": email, "password": password}, format="json"
        )

    def use_token(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_register_creates_user(self):
        response = self.register()

        self.assertEqual(response.status_code, 201)
        saved = UserModel.objects.get(email="user@example.com")
        self.assertTrue(saved.check_password("secret-pass"))

    def test_register_returns_public_fields_only(self):
        response = self.register()

        self.assertEqual(
            set(response.data.keys()), {"id", "email", "full_name", "role"}
        )

    def test_register_normalizes_email(self):
        self.register(email="USER@Example.COM")

        self.assertTrue(UserModel.objects.filter(email="user@example.com").exists())

    def test_register_rejects_duplicate_email(self):
        self.register()

        response = self.register(email="USER@example.com")

        self.assertEqual(response.status_code, 409)

    def test_register_rejects_invalid_email(self):
        response = self.register(email="not-an-email")

        self.assertEqual(response.status_code, 400)

    def test_register_rejects_short_password(self):
        response = self.register(password="short")

        self.assertEqual(response.status_code, 400)

    def test_register_accepts_role(self):
        response = self.register(role="landlord")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["role"], "landlord")

    def test_register_rejects_admin_role(self):
        response = self.register(role="admin")

        self.assertEqual(response.status_code, 400)

    def test_login_returns_token_and_user(self):
        self.register()

        response = self.login()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["token"])
        self.assertEqual(response.data["user"]["email"], "user@example.com")

    def test_login_rejects_wrong_password(self):
        self.register()

        response = self.login(password="wrong-password")

        self.assertEqual(response.status_code, 401)

    def test_login_rejects_unknown_email(self):
        response = self.login(email="nobody@example.com")

        self.assertEqual(response.status_code, 401)

    def test_me_requires_authentication(self):
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 401)

    def test_me_returns_current_user_with_token(self):
        self.register()
        token = self.login().data["token"]

        self.use_token(token)
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "user@example.com")

    def test_me_rejects_invalid_token(self):
        self.use_token("not-a-real-token")

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 401)

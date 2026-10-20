from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from identity.models import User

FAST_HASHING = override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]
)


@FAST_HASHING
class AdministrationApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="secret-pass",
            full_name="Admin User",
            role="admin",
        )
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="secret-pass",
            full_name="Staff User",
            is_staff=True,
        )
        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="secret-pass",
            full_name="Tenant User",
            role="tenant",
        )
        self.landlord = User.objects.create_user(
            email="landlord@example.com",
            password="secret-pass",
            full_name="Landlord User",
            role="landlord",
        )
        self.list_url = reverse("administration:user-list")

    def authenticate(self, user):
        token, _created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def detail_url(self, user_id):
        return reverse("administration:user-detail", args=[user_id])

    def test_unauthenticated_requests_are_rejected(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 401)

    def test_tenants_cannot_access_administration(self):
        self.authenticate(self.tenant)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)

    def test_landlords_cannot_access_administration(self):
        self.authenticate(self.landlord)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_role_can_list_users(self):
        self.authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

    def test_staff_can_list_users(self):
        self.authenticate(self.staff)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)

    def test_filter_users_by_role(self):
        self.authenticate(self.admin)

        response = self.client.get(self.list_url, {"role": "landlord"})

        self.assertEqual(
            [user["email"] for user in response.data],
            ["landlord@example.com"],
        )

    def test_filter_users_by_active_status(self):
        self.tenant.is_active = False
        self.tenant.save(update_fields=["is_active"])
        self.authenticate(self.admin)

        response = self.client.get(self.list_url, {"is_active": "false"})

        self.assertEqual(
            [user["email"] for user in response.data], ["tenant@example.com"]
        )

    def test_invalid_active_filter_is_rejected(self):
        self.authenticate(self.admin)

        response = self.client.get(self.list_url, {"is_active": "maybe"})

        self.assertEqual(response.status_code, 400)

    def test_search_users(self):
        self.authenticate(self.admin)

        response = self.client.get(self.list_url, {"search": "landlord"})

        self.assertEqual(
            [user["email"] for user in response.data],
            ["landlord@example.com"],
        )

    def test_get_user_detail(self):
        self.authenticate(self.admin)

        response = self.client.get(self.detail_url(self.tenant.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "tenant@example.com")

    def test_missing_user_returns_404(self):
        self.authenticate(self.admin)

        response = self.client.get(self.detail_url(999))

        self.assertEqual(response.status_code, 404)

    def test_admin_can_change_role(self):
        self.authenticate(self.admin)

        response = self.client.patch(
            self.detail_url(self.tenant.id), {"role": "landlord"}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["role"], "landlord")
        self.assertEqual(User.objects.get(pk=self.tenant.id).role, "landlord")

    def test_admin_can_deactivate_user(self):
        self.authenticate(self.admin)

        response = self.client.patch(
            self.detail_url(self.tenant.id), {"is_active": False}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_active"])

    def test_deactivated_user_token_stops_working(self):
        tenant_token, _created = Token.objects.get_or_create(user=self.tenant)
        self.authenticate(self.admin)
        self.client.patch(
            self.detail_url(self.tenant.id), {"is_active": False}, format="json"
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {tenant_token.key}")
        response = self.client.get(reverse("identity:me"))

        self.assertEqual(response.status_code, 401)

    def test_admin_cannot_modify_their_own_account(self):
        self.authenticate(self.admin)

        response = self.client.patch(
            self.detail_url(self.admin.id), {"is_active": False}, format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertTrue(User.objects.get(pk=self.admin.id).is_active)

    def test_invalid_role_is_rejected(self):
        self.authenticate(self.admin)

        response = self.client.patch(
            self.detail_url(self.tenant.id), {"role": "superhero"}, format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_empty_update_is_rejected(self):
        self.authenticate(self.admin)

        response = self.client.patch(
            self.detail_url(self.tenant.id), {}, format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_update_missing_user_returns_404(self):
        self.authenticate(self.admin)

        response = self.client.patch(
            self.detail_url(999), {"is_active": False}, format="json"
        )

        self.assertEqual(response.status_code, 404)

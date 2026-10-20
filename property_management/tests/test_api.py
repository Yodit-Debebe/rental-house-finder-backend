from decimal import Decimal

from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from identity.models import User
from property_management.models import Property

FAST_HASHING = override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]
)


@FAST_HASHING
class PropertyApiTests(APITestCase):
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
        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="secret-pass",
            full_name="Tenant",
            role="tenant",
        )

        self.list_url = reverse("property_management:list-create")
        self.property = Property.objects.create(
            landlord=self.landlord,
            title="2-bedroom apartment",
            description="Near the market",
            address="Bole Road 12",
            city="Addis Ababa",
            price=Decimal("15000.00"),
            bedrooms=2,
            bathrooms=1,
        )
        self.detail_url = reverse(
            "property_management:detail", args=[self.property.id]
        )

    def authenticate(self, user):
        token, _created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def payload(self, **overrides):
        values = {
            "title": "3-bedroom house",
            "description": "With a garden",
            "address": "Sarbet 5",
            "city": "Addis Ababa",
            "price": "25000.00",
            "bedrooms": 3,
            "bathrooms": 2,
        }
        values.update(overrides)
        return values

    def test_unauthenticated_requests_are_rejected(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 401)

    def test_tenants_cannot_manage_properties(self):
        self.authenticate(self.tenant)

        response = self.client.post(self.list_url, self.payload(), format="json")

        self.assertEqual(response.status_code, 403)

    def test_landlord_can_create_property(self):
        self.authenticate(self.landlord)

        response = self.client.post(self.list_url, self.payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "3-bedroom house")
        self.assertEqual(response.data["price"], "25000.00")
        created = Property.objects.get(pk=response.data["id"])
        self.assertEqual(created.landlord, self.landlord)

    def test_description_is_optional(self):
        self.authenticate(self.landlord)
        payload = self.payload()
        payload.pop("description")

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["description"], "")

    def test_invalid_payload_is_rejected(self):
        self.authenticate(self.landlord)

        response = self.client.post(
            self.list_url, self.payload(title="   "), format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_negative_price_is_rejected(self):
        self.authenticate(self.landlord)

        response = self.client.post(
            self.list_url, self.payload(price="-1.00"), format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_list_returns_only_own_properties(self):
        Property.objects.create(
            landlord=self.other_landlord,
            title="Not mine",
            address="Unknown",
            city="Addis Ababa",
            price=Decimal("9000.00"),
            bedrooms=1,
            bathrooms=1,
        )
        self.authenticate(self.landlord)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["title"] for item in response.data], ["2-bedroom apartment"])

    def test_landlord_can_read_own_property(self):
        self.authenticate(self.landlord)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.property.id)

    def test_landlord_can_update_own_property(self):
        self.authenticate(self.landlord)

        response = self.client.patch(
            self.detail_url, {"title": "Renovated", "is_available": False}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Renovated")
        self.assertEqual(response.data["price"], "15000.00")
        self.assertFalse(response.data["is_available"])

    def test_landlord_can_delete_own_property(self):
        self.authenticate(self.landlord)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Property.objects.filter(pk=self.property.id).exists())

    def test_other_landlord_cannot_read_property(self):
        self.authenticate(self.other_landlord)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 403)

    def test_other_landlord_cannot_update_property(self):
        self.authenticate(self.other_landlord)

        response = self.client.patch(
            self.detail_url, {"title": "Hijacked"}, format="json"
        )

        self.assertEqual(response.status_code, 403)

    def test_other_landlord_cannot_delete_property(self):
        self.authenticate(self.other_landlord)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Property.objects.filter(pk=self.property.id).exists())

    def test_missing_property_returns_404(self):
        self.authenticate(self.landlord)

        response = self.client.get(
            reverse("property_management:detail", args=[999])
        )

        self.assertEqual(response.status_code, 404)

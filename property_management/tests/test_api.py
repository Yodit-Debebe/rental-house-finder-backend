import io
import shutil
import tempfile
from decimal import Decimal

from django.core.files.storage import default_storage, storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils.functional import empty
from PIL import Image
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from identity.models import User
from property_management.models import Amenity as AmenityModel
from property_management.models import Property

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


def png_upload(name: str = "cover.png") -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "red").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


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


@FAST_HASHING
class PropertyMediaApiTests(TempMediaMixin, APITestCase):
    def setUp(self):
        super().setUp()
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
        self.property = Property.objects.create(
            landlord=self.landlord,
            title="2-bedroom apartment",
            address="Bole Road 12",
            city="Addis Ababa",
            price=Decimal("15000.00"),
            bedrooms=2,
            bathrooms=1,
        )
        self.detail_url = reverse(
            "property_management:detail", args=[self.property.id]
        )
        self.upload_url = reverse(
            "property_management:image-upload", args=[self.property.id]
        )

    def authenticate(self, user):
        token, _created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def upload(self, is_cover=False, name="cover.png"):
        payload = {"image": png_upload(name), "caption": "  Living room  "}
        if is_cover:
            payload["is_cover"] = True
        return self.client.post(self.upload_url, payload, format="multipart")

    def test_amenities_endpoint_lists_catalog(self):
        AmenityModel.objects.create(name="WiFi")
        AmenityModel.objects.create(name="Parking")
        self.authenticate(self.landlord)

        response = self.client.get(reverse("property_management:amenities"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["name"] for item in response.data], ["Parking", "WiFi"]
        )

    def test_tenants_cannot_read_amenities(self):
        self.authenticate(self.tenant)

        response = self.client.get(reverse("property_management:amenities"))

        self.assertEqual(response.status_code, 403)

    def test_create_property_with_amenities(self):
        parking = AmenityModel.objects.create(name="Parking")
        self.authenticate(self.landlord)

        response = self.client.post(
            reverse("property_management:list-create"),
            {
                "title": "3-bedroom house",
                "address": "Sarbet 5",
                "city": "Addis Ababa",
                "price": "25000.00",
                "bedrooms": 3,
                "bathrooms": 2,
                "amenity_ids": [parking.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["amenities"], [{"id": parking.id, "name": "Parking"}]
        )

    def test_unknown_amenity_is_rejected(self):
        self.authenticate(self.landlord)

        response = self.client.post(
            reverse("property_management:list-create"),
            {
                "title": "3-bedroom house",
                "address": "Sarbet 5",
                "city": "Addis Ababa",
                "price": "25000.00",
                "bedrooms": 3,
                "bathrooms": 2,
                "amenity_ids": [999],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_upload_returns_image_and_first_becomes_cover(self):
        self.authenticate(self.landlord)

        response = self.upload(name="living-room.png")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["is_cover"])
        self.assertTrue(response.data["url"].endswith("living-room.png"))
        self.assertEqual(response.data["caption"], "Living room")

    def test_detail_includes_images(self):
        self.authenticate(self.landlord)
        self.upload()

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["images"]), 1)
        self.assertTrue(response.data["images"][0]["is_cover"])

    def test_second_image_is_not_cover_unless_requested(self):
        self.authenticate(self.landlord)
        self.upload(name="first.png")

        response = self.upload(name="second.png")

        self.assertFalse(response.data["is_cover"])

    def test_upload_can_set_cover(self):
        self.authenticate(self.landlord)
        first = self.upload(name="first.png")
        second = self.upload(name="second.png", is_cover=True)

        response = self.client.get(self.detail_url)

        images = {item["id"]: item for item in response.data["images"]}
        self.assertFalse(images[first.data["id"]]["is_cover"])
        self.assertTrue(images[second.data["id"]]["is_cover"])

    def test_delete_image(self):
        self.authenticate(self.landlord)
        uploaded = self.upload()

        response = self.client.delete(
            reverse(
                "property_management:image-delete",
                args=[self.property.id, uploaded.data["id"]],
            )
        )

        self.assertEqual(response.status_code, 204)
        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.data["images"], [])

    def test_tenants_cannot_upload_images(self):
        self.authenticate(self.tenant)

        response = self.upload()

        self.assertEqual(response.status_code, 403)

    def test_other_landlord_cannot_upload_images(self):
        self.authenticate(self.other_landlord)

        response = self.upload()

        self.assertEqual(response.status_code, 403)

    def test_other_landlord_cannot_delete_images(self):
        self.authenticate(self.landlord)
        uploaded = self.upload()
        self.authenticate(self.other_landlord)

        response = self.client.delete(
            reverse(
                "property_management:image-delete",
                args=[self.property.id, uploaded.data["id"]],
            )
        )

        self.assertEqual(response.status_code, 403)

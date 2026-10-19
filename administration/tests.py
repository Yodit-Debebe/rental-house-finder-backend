from django.test import TestCase
from django.urls import reverse


class AdminSiteSmokeTests(TestCase):
    """Smoke tests: prove the request pipeline (URL -> view -> response) works."""

    def test_admin_login_page_loads(self):
        response = self.client.get(reverse("admin:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django administration")

    def test_admin_index_redirects_anonymous_users_to_login(self):
        response = self.client.get(reverse("admin:index"))
        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next=/admin/",
        )

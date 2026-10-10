
from django.test import TestCase
from django.urls import reverse, resolve
from django.conf import settings


class DjangoConfigurationTests(TestCase):
    """Kiểm tra cấu hình cơ bản của dự án."""

    def test_debug_setting_exists(self):
        self.assertIsInstance(settings.DEBUG, bool)

    def test_root_url_is_configured(self):
        # Kiểm tra URL trang chủ "/"
        match = resolve("/")
        self.assertIsNotNone(match)


class PageTests(TestCase):
    """Kiểm tra các trang web cơ bản."""

    def test_homepage_returns_success(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
import frappe
from frappe.tests.utils import FrappeTestCase

from galaxy_ui.galaxy_ui.doctype.ui_app_config.ui_app_config import _normalize_url


class TestUIAppConfig(FrappeTestCase):
    def test_doctype_exists(self):
        self.assertTrue(frappe.db.exists("DocType", "UI App Config"))

    def test_normalize_url(self):
        self.assertEqual(_normalize_url("https://example.com/api"), "https://example.com/api")
        self.assertEqual(_normalize_url("/api"), "/api")

    def test_normalize_url_rejects_invalid(self):
        with self.assertRaises(frappe.ValidationError):
            _normalize_url("ftp://example.com")

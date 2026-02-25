import frappe
from frappe.tests.utils import FrappeTestCase

from galaxy_ui.api.registry import _response_envelope


class TestUIAPIRegistry(FrappeTestCase):
    def test_doctype_exists(self):
        self.assertTrue(frappe.db.exists("DocType", "UI API Registry"))

    def test_response_envelope(self):
        result = {"rows": [], "total": 0}
        wrapped = _response_envelope("sales.orders", "list", result)
        self.assertEqual(wrapped.get("ok"), 1)
        self.assertEqual(wrapped.get("mode"), "list")
        self.assertEqual(wrapped.get("key"), "sales.orders")
        self.assertEqual(wrapped.get("result"), result)

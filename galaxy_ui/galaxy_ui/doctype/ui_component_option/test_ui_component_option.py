import frappe
from frappe.tests.utils import FrappeTestCase


class TestUIComponentOption(FrappeTestCase):
    def test_doctype_exists(self):
        self.assertTrue(frappe.db.exists("DocType", "UI Component Option"))

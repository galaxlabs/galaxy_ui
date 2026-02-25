import frappe
from frappe.tests.utils import FrappeTestCase


class TestUIViewTemplate(FrappeTestCase):
    def test_doctype_exists(self):
        self.assertTrue(frappe.db.exists("DocType", "UI View Template"))

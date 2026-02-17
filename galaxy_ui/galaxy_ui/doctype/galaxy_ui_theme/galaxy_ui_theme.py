# Copyright (c) 2026, Galaxy Labs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GalaxyUITheme(Document):
    def validate(self):
        # allow only one active
        if self.is_active:
            frappe.db.sql(
                """UPDATE `tabGalaxy UI Theme` SET is_active=0 WHERE name!=%s""",
                (self.name,),
            )

        # clean tokens (advanced overrides)
        # clean tokens (advanced overrides)
        if getattr(self, "tokens", None):
            for r in self.tokens:
                # trim
                r.token = (r.token or "").strip()
                r.light_value = (r.light_value or "").strip()
                r.dark_value = (r.dark_value or "").strip()

                # auto-disable fully empty rows
                if not r.token and not r.light_value and not r.dark_value:
                    r.enabled = 0

                # if enabled and token exists, enforce format
                if r.enabled and r.token and not r.token.startswith("--"):
                    frappe.throw(f"Token must start with -- : {r.token}")

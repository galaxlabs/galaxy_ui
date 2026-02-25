# Copyright (c) 2026, Galaxy Labs and contributors
# For license information, please see license.txt

from __future__ import annotations

import json

import frappe
from frappe.model.document import Document


class UIPanelDashboard(Document):
    def validate(self):
        self.title = (self.title or self.name or "").strip()
        if not self.title:
            frappe.throw("Title is required")

        raw = (self.dashboard_json or "").strip()
        if not raw:
            frappe.throw("dashboard_json is required")

        try:
            parsed = json.loads(raw)
        except Exception as e:
            frappe.throw(f"dashboard_json is not valid JSON: {e}")

        if not isinstance(parsed, dict):
            frappe.throw("dashboard_json root must be an object")
        if not isinstance(parsed.get("sections") or [], list):
            frappe.throw("dashboard_json.sections must be a list")

    def on_update(self):
        if self.is_default:
            frappe.db.sql(
                """
                update `tabUI Panel Dashboard`
                set is_default = 0
                where name != %s and ifnull(is_default, 0) = 1
                """,
                (self.name,),
            )

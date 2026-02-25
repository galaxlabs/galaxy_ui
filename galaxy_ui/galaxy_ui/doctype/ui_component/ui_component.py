from __future__ import annotations

import re

import frappe
from frappe.model.document import Document


class UIComponent(Document):
    def validate(self):
        self.component_name = (self.component_name or "").strip().lower()
        if not self.component_name:
            frappe.throw("component_name is required")

        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,120}", self.component_name):
            frappe.throw("component_name must be lowercase and may include dot/underscore/dash")

        self.title = (self.title or self.component_name).strip()
        if not self.title:
            frappe.throw("title is required")

        self.applies_to = (self.applies_to or "panel").strip().lower()
        if self.applies_to not in {"all", "panel", "dashboard", "web", "desk"}:
            frappe.throw("applies_to must be one of: all, panel, dashboard, web, desk")

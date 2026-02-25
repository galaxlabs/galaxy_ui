from __future__ import annotations

import json
import re

import frappe
from frappe.model.document import Document


class UIAPIRegistry(Document):
    def validate(self):
        self.key = (self.key or "").strip().lower()
        if not self.key:
            frappe.throw("Key is required")
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,140}", self.key):
            frappe.throw("Key must be lowercase and may include dot/underscore/dash")

        self.source_type = (self.source_type or "Doctype").strip()
        if self.source_type not in {"Doctype", "Report", "Custom Query"}:
            frappe.throw("Invalid source_type")

        if self.source_type == "Doctype" and not self.source_doctype:
            frappe.throw("source_doctype is required when source_type is Doctype")
        if self.source_type == "Report" and not self.report:
            frappe.throw("report is required when source_type is Report")

        self.allowed_fields_json = _normalize_json(self.allowed_fields_json, "allowed_fields_json", list)
        self.filters_allowed_json = _normalize_json(self.filters_allowed_json, "filters_allowed_json", list)
        self.order_by_allowed_json = _normalize_json(self.order_by_allowed_json, "order_by_allowed_json", list)
        self.limit_rules_json = _normalize_json(self.limit_rules_json, "limit_rules_json", dict)
        self.allowed_roles_json = _normalize_json(self.allowed_roles_json, "allowed_roles_json", list)


def _normalize_json(raw, fieldname: str, expected):
    text = (raw or "").strip()
    if not text:
        if expected is dict:
            return "{}"
        return "[]"

    try:
        parsed = json.loads(text)
    except Exception as exc:
        frappe.throw(f"{fieldname} must be valid JSON: {exc}")

    if not isinstance(parsed, expected):
        frappe.throw(f"{fieldname} must be {expected.__name__}")

    return json.dumps(parsed, separators=(",", ":"))

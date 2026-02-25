from __future__ import annotations

import json

import frappe
from frappe.model.document import Document


class UIViewTemplate(Document):
    def validate(self):
        self.title = (self.title or "").strip()
        if not self.title:
            frappe.throw("title is required")

        self.template_type = (self.template_type or "list").strip().lower()
        if self.template_type not in {"dashboard", "list", "form"}:
            frappe.throw("template_type must be one of: dashboard, list, form")

        self.source_doctype = (self.source_doctype or "").strip()
        if self.source_doctype and not frappe.db.exists("DocType", self.source_doctype):
            frappe.throw(f"Invalid source_doctype: {self.source_doctype}")

        self.target_section = (self.target_section or "").strip()

        self.config_json = _normalize_config(self.config_json, self.template_type, self.source_doctype)
        self.generated_route = _suggest_route(self.template_type, self.source_doctype, self.name)


def _normalize_config(raw, template_type: str, source_doctype: str | None) -> str:
    text = (raw or "").strip()
    if not text:
        parsed = _default_config(template_type, source_doctype)
    else:
        try:
            parsed = json.loads(text)
        except Exception as exc:
            frappe.throw(f"config_json must be valid JSON: {exc}")

    if not isinstance(parsed, dict):
        frappe.throw("config_json must be a JSON object")

    if template_type == "dashboard":
        parsed.setdefault("title", "Dashboard")
        parsed.setdefault("sections", [])
        if not isinstance(parsed.get("sections"), list):
            frappe.throw("dashboard config_json.sections must be a list")

    if template_type == "list":
        parsed.setdefault("doctype", source_doctype or "")
        parsed.setdefault("fields", ["name", "modified", "owner"])
        parsed.setdefault("filters", {})
        if not isinstance(parsed.get("fields"), list):
            frappe.throw("list config_json.fields must be a list")
        if not isinstance(parsed.get("filters"), (dict, list)):
            frappe.throw("list config_json.filters must be object or array")

    if template_type == "form":
        parsed.setdefault("doctype", source_doctype or "")
        parsed.setdefault("field_groups", [])
        if not isinstance(parsed.get("field_groups"), list):
            frappe.throw("form config_json.field_groups must be a list")

    return json.dumps(parsed, separators=(",", ":"))


def _default_config(template_type: str, source_doctype: str | None) -> dict:
    if template_type == "dashboard":
        return {"title": "Dashboard", "sections": []}
    if template_type == "form":
        return {"doctype": source_doctype or "", "field_groups": []}
    return {"doctype": source_doctype or "", "fields": ["name", "modified", "owner"], "filters": {}}


def _suggest_route(template_type: str, source_doctype: str | None, name: str | None) -> str:
    if template_type == "dashboard":
        return "/app/ui_panel"
    if template_type == "list" and source_doctype:
        return f"/app/{frappe.scrub(source_doctype)}"
    if template_type == "form" and source_doctype:
        return f"/app/{frappe.scrub(source_doctype)}"
    return f"/app/ui-view-template/{frappe.scrub(name or '')}"

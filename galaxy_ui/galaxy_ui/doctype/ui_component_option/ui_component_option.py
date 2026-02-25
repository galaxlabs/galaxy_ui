from __future__ import annotations

import json
import re

import frappe
from frappe.model.document import Document


class UIComponentOption(Document):
    def validate(self):
        self.option_name = _normalize_option_name(self.option_name)
        if not self.option_name:
            frappe.throw("option_name is required")

        if not self.component:
            frappe.throw("component is required")

        if not frappe.db.exists("UI Component", self.component):
            frappe.throw(f"UI Component not found: {self.component}")

        self.title = (self.title or self.option_name).strip()

        self.css_vars_json = _normalize_css_vars(self.css_vars_json)
        self.classes_json = _normalize_classes(self.classes_json)

    def autoname(self):
        component = frappe.scrub(self.component or "")
        option = frappe.scrub(self.option_name or "")
        if not component or not option:
            frappe.throw("component and option_name are required for naming")
        self.name = f"{component}-{option}"

    def on_update(self):
        if self.is_default and self.component:
            frappe.db.sql(
                """
                update `tabUI Component Option`
                set is_default = 0
                where component = %s and name != %s and ifnull(is_default, 0) = 1
                """,
                (self.component, self.name),
            )


def _normalize_option_name(value: str | None) -> str:
    text = (value or "").strip().lower().replace(" ", "_")
    if text and not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,120}", text):
        frappe.throw("option_name must be lowercase and may include dot/underscore/dash")
    return text


def _normalize_css_vars(raw) -> str:
    text = (raw or "").strip()
    if not text:
        return "{}"

    try:
        parsed = json.loads(text)
    except Exception as exc:
        frappe.throw(f"css_vars_json must be valid JSON: {exc}")

    if not isinstance(parsed, dict):
        frappe.throw("css_vars_json must be a JSON object")

    clean = {}
    for key, value in parsed.items():
        token = (str(key) if key is not None else "").strip()
        if not token.startswith("--"):
            frappe.throw(f"CSS variable must start with -- : {token}")
        clean[token] = "" if value is None else str(value).strip()

    return json.dumps(clean, separators=(",", ":"))


def _normalize_classes(raw) -> str:
    text = (raw or "").strip()
    if not text:
        return "{}"

    try:
        parsed = json.loads(text)
    except Exception as exc:
        frappe.throw(f"classes_json must be valid JSON: {exc}")

    if isinstance(parsed, list):
        if not all(isinstance(x, str) for x in parsed):
            frappe.throw("classes_json list entries must be strings")
        parsed = {"shell": [x.strip() for x in parsed if (x or "").strip()]}
    elif not isinstance(parsed, dict):
        frappe.throw("classes_json must be a JSON object or array of strings")

    clean = {}
    for scope, value in parsed.items():
        scope_key = (str(scope) if scope is not None else "").strip() or "shell"
        if isinstance(value, str):
            classes = [value.strip()] if value.strip() else []
        elif isinstance(value, list):
            classes = [str(v).strip() for v in value if str(v).strip()]
        else:
            frappe.throw(f"classes_json.{scope_key} must be string or list of strings")

        clean[scope_key] = classes

    return json.dumps(clean, separators=(",", ":"))

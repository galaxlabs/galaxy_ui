# Copyright (c) 2026, Galaxy Labs and contributors
# For license information, please see license.txt

from __future__ import annotations

import json

import frappe
from jsonschema import Draft202012Validator
from frappe.model.document import Document

from galaxy_ui.core.bundle import bundle_hash

try:
    from galaxy_ui.core.schemas import UI_PANEL_NAVIGATION_SCHEMA_V1
except Exception:
    UI_PANEL_NAVIGATION_SCHEMA_V1 = {
        "type": "object",
        "required": ["sections", "topbar"],
        "properties": {
            "sections": {"type": "array"},
            "topbar": {"type": "array"},
        },
        "additionalProperties": True,
    }


def _validate_navigation(data: dict) -> None:
    try:
        from galaxy_ui.core.bundle import validate_ui_panel_navigation_v1 as validator  # type: ignore

        validator(data)
        return
    except Exception:
        pass

    errors = sorted(Draft202012Validator(UI_PANEL_NAVIGATION_SCHEMA_V1).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        msg = "; ".join([(f"{'.'.join([str(p) for p in e.path]) or '(root)'}: {e.message}") for e in errors[:5]])
        frappe.throw(f"Invalid UI Panel Navigation: {msg}")


class UIPanelNavigation(Document):
    def validate(self):
        # Governance: Draft records cannot be active
        if (self.status or "Draft") != "Published":
            self.is_active = 0
            self.published_on = None
            self.published_by = None

        # If active, force publish + set metadata
        if self.is_active:
            self.status = "Published"
            if not self.published_on:
                self.published_on = frappe.utils.now_datetime()
            if not self.published_by:
                self.published_by = frappe.session.user

        self.title = (self.title or self.name or "").strip()
        if not self.title:
            frappe.throw("Title is required")

        raw = (self.navigation_json or "").strip()
        if not raw:
            frappe.throw("navigation_json is required")

        try:
            parsed = json.loads(raw)
        except Exception as e:
            frappe.throw(f"navigation_json is not valid JSON: {e}")

        _validate_navigation(parsed)
        self.nav_hash = bundle_hash(raw)

    def on_update(self):
        if self.is_active:
            frappe.db.sql(
                """
                update `tabUI Panel Navigation`
                set is_active = 0
                where name != %s and ifnull(is_active, 0) = 1
                """,
                (self.name,),
            )
        if self.is_default:
            frappe.db.sql(
                """
                update `tabUI Panel Navigation`
                set is_default = 0
                where name != %s and ifnull(is_default, 0) = 1
                """,
                (self.name,),
            )

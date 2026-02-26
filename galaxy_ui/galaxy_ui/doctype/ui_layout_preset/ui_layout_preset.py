from __future__ import annotations

import json

import frappe
from frappe.model.document import Document
from frappe.utils import cint

from galaxy_ui.core.bundle import bundle_hash, validate_ui_layout_preset


class UILayoutPreset(Document):
    def validate(self):
        self.title = (self.title or self.name or "").strip()
        if not self.title:
            frappe.throw("Title is required")

        targets = _json_obj(self.targets_json, "targets_json", list, default=["panel"])
        component_options = _json_obj(self.component_options_json, "component_options_json", dict, default={})
        component_css_vars = _json_obj(self.component_css_vars_json, "component_css_vars_json", dict, default={})
        effects = _json_obj(self.effects_json, "effects_json", dict, default={})
        self.apply_scope = (self.apply_scope or "UI Panel").strip()
        if self.apply_scope not in {"UI Panel", "Desk", "Both"}:
            frappe.throw("apply_scope must be one of: UI Panel, Desk, Both")

        payload = {
            "name": self.title,
            "enabled": bool(cint(self.enabled or 0)),
            "targets": targets,
            "shell_style": (self.shell_style or "admin").strip().lower(),
            "component_options": component_options,
            "effects": effects,
        }

        validate_ui_layout_preset(payload)
        self.layout_hash = bundle_hash(frappe.as_json(payload, indent=None))
        self.targets_json = json.dumps(targets, separators=(",", ":"))
        self.component_options_json = json.dumps(component_options, separators=(",", ":"))
        self.component_css_vars_json = json.dumps(component_css_vars, separators=(",", ":"))
        self.component_classes = " ".join(
            [part.strip() for part in (self.component_classes or "").split() if part.strip()]
        )
        self.effects_json = json.dumps(effects, separators=(",", ":"))

    def on_update(self):
        if cint(self.is_default):
            frappe.db.sql(
                """
                update `tabUI Layout Preset`
                set is_default = 0
                where name != %s and ifnull(is_default, 0) = 1
                """,
                (self.name,),
            )


def _json_obj(raw, fieldname: str, expected_type, default):
    txt = (raw or "").strip()
    if not txt:
        return default

    try:
        parsed = json.loads(txt)
    except Exception as exc:
        frappe.throw(f"{fieldname} must be valid JSON: {exc}")

    if not isinstance(parsed, expected_type):
        frappe.throw(f"{fieldname} must be {expected_type.__name__}")
    return parsed

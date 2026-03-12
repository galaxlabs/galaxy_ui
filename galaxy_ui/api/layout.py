from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint

from galaxy_ui.core.bundle import validate_ui_layout_preset
from galaxy_ui.core.component_runtime import resolve_layout_preset_runtime_doc
from galaxy_ui.api.theme import get_active_theme_bundle


def _ensure_system_user() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Login required"))
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw(_("Galaxy UI layout center is for System Users only"))


def _ensure_manager() -> None:
    _ensure_system_user()
    roles = set(frappe.get_roles(frappe.session.user) or [])
    if "System Manager" not in roles:
        frappe.throw(_("Only System Manager can modify layout presets"))


def _json_or_default(raw, default):
    txt = (raw or "").strip()
    if not txt:
        return default
    try:
        parsed = json.loads(txt)
    except Exception:
        return default
    return parsed if isinstance(parsed, type(default)) else default


def _preset_payload(doc) -> dict:
    payload = {
        "name": doc.title,
        "enabled": bool(cint(doc.enabled or 0)),
        "targets": _json_or_default(doc.targets_json, ["panel"]),
        "shell_style": (doc.shell_style or "admin").strip().lower(),
        "component_options": _json_or_default(doc.component_options_json, {}),
        "effects": _json_or_default(doc.effects_json, {}),
    }
    validate_ui_layout_preset(payload)
    return payload


@frappe.whitelist(allow_guest=False)
def list_layout_presets():
    _ensure_system_user()
    if not frappe.db.exists("DocType", "UI Layout Preset"):
        return []

    return frappe.get_all(
        "UI Layout Preset",
        fields=[
            "name",
            "title",
            "enabled",
            "is_default",
            "shell_style",
            "apply_scope",
            "layout_hash",
            "last_resolved_on",
            "modified",
        ],
        filters={"enabled": 1},
        order_by="is_default desc, modified desc",
        limit_page_length=200,
    )


@frappe.whitelist(allow_guest=False)
def get_layout_preset(name: str):
    _ensure_system_user()
    if not name:
        frappe.throw(_("name is required"))
    if not frappe.db.exists("UI Layout Preset", name):
        frappe.throw(_("UI Layout Preset not found: {0}").format(name))

    doc = frappe.get_doc("UI Layout Preset", name)
    return {
        "name": doc.name,
        "title": doc.title,
        "enabled": cint(doc.enabled or 0),
        "is_default": cint(doc.is_default or 0),
        "apply_scope": (doc.apply_scope or "UI Panel"),
        "layout": _preset_payload(doc),
        "component_css_vars_json": _json_or_default(getattr(doc, "component_css_vars_json", ""), {}),
        "component_classes": (getattr(doc, "component_classes", "") or "").strip(),
        "last_resolved_on": str(getattr(doc, "last_resolved_on", "") or ""),
    }


@frappe.whitelist(allow_guest=False)
def apply_layout_preset(preset_name: str, theme_name: str | None = None):
    _ensure_system_user()

    if not preset_name:
        frappe.throw(_("preset_name is required"))
    if not frappe.db.exists("UI Layout Preset", preset_name):
        frappe.throw(_("UI Layout Preset not found: {0}").format(preset_name))

    preset = frappe.get_doc("UI Layout Preset", preset_name)
    layout = _preset_payload(preset)

    if theme_name:
        if not frappe.db.exists("UI Theme", theme_name):
            frappe.throw(_("UI Theme not found: {0}").format(theme_name))
        target_theme = theme_name
    else:
        names = frappe.get_all("UI Theme", filters={"is_active": 1}, pluck="name", limit=1)
        if not names:
            names = frappe.get_all("UI Theme", pluck="name", order_by="modified desc", limit=1)
        if not names:
            frappe.throw(_("No UI Theme exists to apply layout"))
        target_theme = names[0]

    # Set selected theme active (single active)
    if frappe.db.has_column("UI Theme", "is_active"):
        frappe.db.sql("update `tabUI Theme` set is_active = 0")
        frappe.db.set_value("UI Theme", target_theme, "is_active", 1)

    theme_doc = frappe.get_doc("UI Theme", target_theme)
    theme_doc.layout_json = frappe.as_json(layout)
    theme_doc.save(ignore_permissions=True)

    if cint(preset.is_default or 0):
        frappe.db.sql("update `tabUI Layout Preset` set is_default = 0 where name != %s", (preset.name,))
        frappe.db.set_value("UI Layout Preset", preset.name, "is_default", 1)

    frappe.db.commit()

    return {
        "ok": 1,
        "preset": preset.name,
        "theme": target_theme,
        "layout_name": layout.get("name"),
    }


@frappe.whitelist(allow_guest=False)
def resolve_layout_preset_runtime(preset_name: str, save_cache: int = 0):
    _ensure_system_user()
    if not preset_name:
        frappe.throw(_("preset_name is required"))
    if not frappe.db.exists("UI Layout Preset", preset_name):
        frappe.throw(_("UI Layout Preset not found: {0}").format(preset_name))

    doc = frappe.get_doc("UI Layout Preset", preset_name)
    runtime = resolve_layout_preset_runtime_doc(doc, target_scope="UI Panel")

    save_cache = cint(save_cache or 0)
    if save_cache:
        _ensure_manager()
        doc.component_css_vars_json = frappe.as_json(runtime.get("css_vars") or {})
        doc.component_classes = " ".join(runtime.get("classes") or [])
        doc.last_resolved_on = frappe.utils.now_datetime()
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    return {
        "preset_name": doc.name,
        "apply_scope": runtime.get("apply_scope"),
        "active_for_scope": runtime.get("active_for_scope"),
        "css_vars": runtime.get("css_vars") or {},
        "classes": runtime.get("classes") or [],
        "warnings": runtime.get("warnings") or [],
        "matched": runtime.get("matched") or [],
        "unmatched": runtime.get("unmatched") or [],
        "saved_cache": 1 if save_cache else 0,
    }


def _activate_theme(theme_name: str) -> str:
    if not theme_name:
        frappe.throw(_("theme_name is required"))
    if not frappe.db.exists("UI Theme", theme_name):
        frappe.throw(_("UI Theme not found: {0}").format(theme_name))

    if frappe.db.has_column("UI Theme", "is_active"):
        frappe.db.sql("update `tabUI Theme` set is_active = 0")
        frappe.db.set_value("UI Theme", theme_name, "is_active", 1)
    return theme_name


@frappe.whitelist(allow_guest=False)
def get_appearance_options():
    _ensure_system_user()

    presets = list_layout_presets()
    themes = frappe.get_all(
        "UI Theme",
        fields=["name", "theme_name", "is_active", "modified"],
        order_by="is_active desc, modified desc",
        limit_page_length=300,
    )

    default_preset = next((p for p in presets if cint(p.get("is_default") or 0)), None)
    active_theme = next((t for t in themes if cint(t.get("is_active") or 0)), None)

    return {
        "presets": presets,
        "themes": themes,
        "current": {
            "preset": default_preset.get("name") if default_preset else (presets[0].get("name") if presets else None),
            "theme": active_theme.get("name") if active_theme else (themes[0].get("name") if themes else None),
        },
    }


@frappe.whitelist(allow_guest=False)
def apply_panel_appearance(preset_name: str | None = None, theme_name: str | None = None):
    _ensure_system_user()
    if not preset_name and not theme_name:
        frappe.throw(_("At least one of preset_name or theme_name is required"))

    result = {}
    if preset_name:
        result = apply_layout_preset(preset_name=preset_name, theme_name=theme_name)
    elif theme_name:
        activated_theme = _activate_theme(theme_name)
        frappe.db.commit()
        result = {"ok": 1, "preset": None, "theme": activated_theme, "layout_name": None}

    bundle = get_active_theme_bundle()
    return {
        "ok": 1,
        "applied": result,
        "theme_bundle": bundle,
    }

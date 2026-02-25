from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint


def _ensure_system_user() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Login required"))
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw(_("Galaxy UI component library is available to System Users only"))


def _parse_json(raw, default):
    if raw in (None, "", []):
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        parsed = json.loads(raw)
    except Exception:
        return default
    return parsed if isinstance(parsed, type(default)) else default


def _component_exists(name: str) -> bool:
    return bool(name and frappe.db.exists("UI Component", name))


def _ensure_manager() -> None:
    _ensure_system_user()
    if "System Manager" not in set(frappe.get_roles(frappe.session.user) or []):
        frappe.throw(_("Only System Manager can seed component library"))


def _get_option_doc(component_name: str, option_name: str):
    names = frappe.get_all(
        "UI Component Option",
        filters={"component": component_name, "option_name": option_name, "enabled": 1},
        pluck="name",
        limit=1,
    )
    if names:
        return frappe.get_doc("UI Component Option", names[0])
    return None


@frappe.whitelist(allow_guest=False)
def list_components():
    _ensure_system_user()
    if not frappe.db.exists("DocType", "UI Component"):
        return []

    components = frappe.get_all(
        "UI Component",
        fields=["name", "component_name", "title", "applies_to", "enabled", "modified"],
        filters={"enabled": 1},
        order_by="modified desc",
        limit_page_length=300,
    )

    out = []
    for comp in components:
        count = frappe.db.count("UI Component Option", filters={"component": comp.get("name"), "enabled": 1})
        out.append(
            {
                "name": comp.get("name"),
                "component_name": comp.get("component_name"),
                "title": comp.get("title"),
                "applies_to": comp.get("applies_to"),
                "enabled": cint(comp.get("enabled") or 0),
                "option_count": cint(count or 0),
            }
        )
    return out


@frappe.whitelist(allow_guest=False)
def list_component_options(component_name: str):
    _ensure_system_user()
    if not component_name:
        frappe.throw(_("component_name is required"))
    if not _component_exists(component_name):
        frappe.throw(_("UI Component not found: {0}").format(component_name))

    rows = frappe.get_all(
        "UI Component Option",
        fields=["name", "component", "option_name", "title", "is_default", "enabled", "modified"],
        filters={"component": component_name},
        order_by="is_default desc, modified desc",
        limit_page_length=500,
    )

    options = []
    for row in rows:
        options.append(
            {
                "name": row.get("name"),
                "component": row.get("component"),
                "option_name": row.get("option_name"),
                "title": row.get("title"),
                "is_default": cint(row.get("is_default") or 0),
                "enabled": cint(row.get("enabled") or 0),
            }
        )
    return options


@frappe.whitelist(allow_guest=False)
def resolve_component_options(component_options=None):
    _ensure_system_user()
    mapping = _parse_json(component_options, {})
    if not isinstance(mapping, dict):
        frappe.throw(_("component_options must be a JSON object"))

    resolved = {}
    css_vars = {}
    classes = {"shell": []}
    missing = []

    for component_name, option_name in mapping.items():
        comp = (component_name or "").strip()
        opt = (option_name or "").strip()
        if not comp or not opt:
            continue

        if not _component_exists(comp):
            missing.append({"component": comp, "option": opt, "reason": "component_not_found"})
            continue

        doc = _get_option_doc(comp, opt)
        if not doc:
            missing.append({"component": comp, "option": opt, "reason": "option_not_found"})
            continue

        option_css = _parse_json(doc.css_vars_json, {})
        option_classes = _parse_json(doc.classes_json, {})

        if isinstance(option_css, dict):
            css_vars.update(option_css)

        if isinstance(option_classes, dict):
            for scope, values in option_classes.items():
                scope_key = (scope or "").strip() or "shell"
                if scope_key not in classes:
                    classes[scope_key] = []
                if isinstance(values, str):
                    if values.strip():
                        classes[scope_key].append(values.strip())
                elif isinstance(values, list):
                    classes[scope_key].extend([str(v).strip() for v in values if str(v).strip()])

        resolved[comp] = {
            "option": doc.option_name,
            "option_doc": doc.name,
            "title": doc.title or doc.option_name,
        }

    # Deduplicate class lists while preserving order.
    for scope, values in list(classes.items()):
        seen = set()
        uniq = []
        for cls in values:
            if cls in seen:
                continue
            seen.add(cls)
            uniq.append(cls)
        classes[scope] = uniq

    return {
        "mapping": mapping,
        "resolved": resolved,
        "css_vars": css_vars,
        "classes": classes,
        "missing": missing,
    }


@frappe.whitelist(allow_guest=False)
def seed_default_components():
    _ensure_manager()

    defaults = {
        "card": {
            "title": "Card",
            "applies_to": "panel",
            "options": {
                "soft_shadow": {
                    "title": "Soft Shadow",
                    "is_default": 1,
                    "css_vars": {"--guip-shadow": "0 8px 20px rgba(15, 23, 42, 0.08)"},
                    "classes": {"shell": ["guip-card-soft"]},
                }
            },
        },
        "button": {
            "title": "Button",
            "applies_to": "panel",
            "options": {
                "rounded_primary": {
                    "title": "Rounded Primary",
                    "is_default": 1,
                    "css_vars": {"--guip-radius": "12px"},
                    "classes": {"shell": ["guip-btn-rounded"]},
                }
            },
        },
        "list_row": {
            "title": "List Row",
            "applies_to": "panel",
            "options": {
                "hover_glow": {
                    "title": "Hover Glow",
                    "is_default": 1,
                    "css_vars": {"--guip-row-hover": "rgba(37,99,235,.12)"},
                    "classes": {"shell": ["guip-row-glow"]},
                }
            },
        },
        "sidebar": {
            "title": "Sidebar",
            "applies_to": "panel",
            "options": {
                "compact_dark": {
                    "title": "Compact Dark",
                    "is_default": 1,
                    "css_vars": {"--guip-sidebar-width": "280px"},
                    "classes": {"shell": ["guip-sidebar-compact"]},
                }
            },
        },
        "navbar": {"title": "Navbar", "applies_to": "panel", "options": {}},
        "table": {"title": "Table", "applies_to": "panel", "options": {}},
        "page_shell": {"title": "Page Shell", "applies_to": "panel", "options": {}},
        "dashboard_tile": {"title": "Dashboard Tile", "applies_to": "dashboard", "options": {}},
    }

    created_components = 0
    created_options = 0

    for component_name, cfg in defaults.items():
        if not frappe.db.exists("UI Component", component_name):
            doc = frappe.get_doc(
                {
                    "doctype": "UI Component",
                    "component_name": component_name,
                    "title": cfg.get("title") or component_name,
                    "applies_to": cfg.get("applies_to") or "panel",
                    "enabled": 1,
                }
            )
            doc.insert(ignore_permissions=True)
            created_components += 1

        for option_name, option_cfg in (cfg.get("options") or {}).items():
            existing = frappe.get_all(
                "UI Component Option",
                filters={"component": component_name, "option_name": option_name},
                pluck="name",
                limit=1,
            )
            if existing:
                continue

            option_doc = frappe.get_doc(
                {
                    "doctype": "UI Component Option",
                    "enabled": 1,
                    "component": component_name,
                    "option_name": option_name,
                    "title": option_cfg.get("title") or option_name,
                    "is_default": cint(option_cfg.get("is_default") or 0),
                    "css_vars_json": frappe.as_json(option_cfg.get("css_vars") or {}),
                    "classes_json": frappe.as_json(option_cfg.get("classes") or {}),
                }
            )
            option_doc.insert(ignore_permissions=True)
            created_options += 1

    frappe.db.commit()
    return {"ok": 1, "created_components": created_components, "created_options": created_options}

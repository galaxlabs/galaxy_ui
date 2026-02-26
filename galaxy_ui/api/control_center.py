from __future__ import annotations

import json
from datetime import datetime

import frappe
from frappe import _
from frappe.utils import cint

from galaxy_ui.api import component as component_api
from galaxy_ui.api import layout as layout_api
from galaxy_ui.api import panel as panel_api
from galaxy_ui.api.theme import get_active_theme_bundle


REQUIRED_DOCTYPES = [
    "UI Theme",
    "UI Token",
    "UI Panel Navigation",
    "UI App Config",
    "UI API Registry",
    "UI Component",
    "UI Component Option",
    "UI View Template",
]

DEFAULT_FEATURE_FLAGS = {
    "bridge": 1,
    "registry": 1,
    "builder": 1,
}


def _require_admin() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Login required"))
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw(_("Galaxy UI Control Center is available to System Users only"))
    roles = set(frappe.get_roles(frappe.session.user) or [])
    if "System Manager" not in roles:
        frappe.throw(_("Only System Manager can access Galaxy UI Control Center"))


def _bool01(value, default: int = 0) -> int:
    if value in (None, ""):
        return cint(default or 0)
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return 1 if cint(value) else 0
    return 1 if str(value).strip().lower() in {"1", "true", "yes", "on", "y"} else 0


def _feature_flags() -> dict:
    flags = dict(DEFAULT_FEATURE_FLAGS)
    raw = frappe.conf.get("galaxy_ui_features")
    override = {}
    if isinstance(raw, str):
        try:
            override = frappe.parse_json(raw) or {}
        except Exception:
            override = {}
    elif isinstance(raw, dict):
        override = raw

    if isinstance(override, dict):
        for key in flags:
            if key in override:
                flags[key] = _bool01(override.get(key), flags[key])
    return flags


def _dt_exists(doctype_name: str) -> bool:
    return bool(doctype_name and frappe.db.exists("DocType", doctype_name))


def _safe_count(doctype_name: str) -> int:
    if not _dt_exists(doctype_name):
        return 0
    try:
        return cint(frappe.db.count(doctype_name) or 0)
    except Exception:
        return 0


def _safe_json(value, default):
    if value in (None, "", []):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        parsed = json.loads(value)
    except Exception:
        return default
    return parsed if isinstance(parsed, type(default)) else default


def _active_theme_doc():
    if not _dt_exists("UI Theme"):
        return None
    names = frappe.get_all("UI Theme", filters={"is_active": 1}, pluck="name", order_by="modified desc", limit=1)
    if not names:
        names = frappe.get_all("UI Theme", pluck="name", order_by="modified desc", limit=1)
    return frappe.get_doc("UI Theme", names[0]) if names else None


def _active_layout_doc():
    if not _dt_exists("UI Layout Preset"):
        return None
    names = frappe.get_all(
        "UI Layout Preset",
        filters={"enabled": 1},
        pluck="name",
        order_by="is_default desc, modified desc",
        limit=1,
    )
    return frappe.get_doc("UI Layout Preset", names[0]) if names else None


def _active_nav_doc():
    if not _dt_exists("UI Panel Navigation"):
        return None
    names = frappe.get_all(
        "UI Panel Navigation",
        filters={"is_active": 1},
        pluck="name",
        order_by="is_default desc, modified desc",
        limit=1,
    )
    if not names:
        names = frappe.get_all(
            "UI Panel Navigation",
            filters={"is_default": 1},
            pluck="name",
            order_by="modified desc",
            limit=1,
        )
    if not names:
        names = frappe.get_all("UI Panel Navigation", pluck="name", order_by="modified desc", limit=1)
    return frappe.get_doc("UI Panel Navigation", names[0]) if names else None


def _nav_item_count(nav_doc) -> int:
    if not nav_doc:
        return 0
    parsed = _safe_json(nav_doc.navigation_json, {})
    sections = parsed.get("sections") if isinstance(parsed, dict) else []
    topbar = parsed.get("topbar") if isinstance(parsed, dict) else []
    section_items = 0
    for sec in (sections or []):
        if isinstance(sec, dict):
            section_items += len(sec.get("items") or [])
    return cint(section_items + len(topbar or []))


def _find_target_name(doctype_name: str, requested_name: str | None, fallback_filters: dict | None = None):
    if not _dt_exists(doctype_name):
        frappe.throw(_("{0} DocType not found").format(doctype_name))

    req = (requested_name or "").strip()
    if req:
        if not frappe.db.exists(doctype_name, req):
            frappe.throw(_("{0} not found: {1}").format(doctype_name, req))
        return req

    filters = dict(fallback_filters or {})
    names = frappe.get_all(doctype_name, filters=filters, pluck="name", order_by="modified desc", limit=1)
    if names:
        return names[0]

    names = frappe.get_all(doctype_name, pluck="name", order_by="modified desc", limit=1)
    if names:
        return names[0]

    frappe.throw(_("No records found for {0}").format(doctype_name))
    return None


def _status_payload() -> dict:
    theme_doc = _active_theme_doc()
    layout_doc = _active_layout_doc()
    nav_doc = _active_nav_doc()
    flags = _feature_flags()

    status = {
        "active_theme": {
            "name": theme_doc.name if theme_doc else None,
            "status": (theme_doc.status if theme_doc else None) or "N/A",
            "is_active": cint(theme_doc.is_active or 0) if theme_doc else 0,
            "published_on": str(theme_doc.published_on) if theme_doc and theme_doc.published_on else None,
        },
        "active_layout_preset": {
            "name": layout_doc.name if layout_doc else None,
            "title": layout_doc.title if layout_doc else None,
            "enabled": cint(layout_doc.enabled or 0) if layout_doc else 0,
            "is_default": cint(layout_doc.is_default or 0) if layout_doc else 0,
        },
        "active_navigation_profile": {
            "name": nav_doc.name if nav_doc else None,
            "title": nav_doc.title if nav_doc else None,
            "status": (nav_doc.status if nav_doc else None) or "N/A",
            "is_active": cint(nav_doc.is_active or 0) if nav_doc else 0,
            "item_count": _nav_item_count(nav_doc),
        },
        "feature_flags": {
            "bridge": flags.get("bridge", "N/A"),
            "registry": flags.get("registry", "N/A"),
            "builder": flags.get("builder", "N/A"),
        },
        "counts": {
            "themes": _safe_count("UI Theme"),
            "layout_presets": _safe_count("UI Layout Preset"),
            "navigation_profiles": _safe_count("UI Panel Navigation"),
            "app_configs": _safe_count("UI App Config"),
            "registry_keys": _safe_count("UI API Registry"),
            "components": _safe_count("UI Component"),
            "component_options": _safe_count("UI Component Option"),
            "view_templates": _safe_count("UI View Template"),
        },
    }
    return status


def _check(status_value: str, key: str, title: str, hint: str, details: str | None = None) -> dict:
    row = {"key": key, "title": title, "status": status_value, "hint": hint}
    if details:
        row["details"] = details
    return row


@frappe.whitelist(allow_guest=False)
def get_status():
    _require_admin()
    return _status_payload()


@frappe.whitelist(allow_guest=False)
def run_health_checks():
    _require_admin()

    checks = []
    for dt in REQUIRED_DOCTYPES:
        if _dt_exists(dt):
            checks.append(_check("PASS", f"doctype_{frappe.scrub(dt)}", f"{dt} exists", "OK"))
        else:
            checks.append(
                _check(
                    "FAIL",
                    f"doctype_{frappe.scrub(dt)}",
                    f"{dt} exists",
                    "Run bench migrate and ensure the app is installed on this site.",
                )
            )

    if _dt_exists("UI Layout Preset") or _dt_exists("UI Preset"):
        checks.append(_check("PASS", "doctype_layout_preset", "Layout Preset DocType exists", "OK"))
    else:
        checks.append(
            _check(
                "FAIL",
                "doctype_layout_preset",
                "Layout Preset DocType exists",
                "Create/migrate UI Layout Preset (or legacy UI Preset) DocType.",
            )
        )

    theme_doc = _active_theme_doc()
    if theme_doc:
        checks.append(_check("PASS", "active_theme", "Active theme exists", "OK", details=theme_doc.name))
        if (theme_doc.status or "").strip().lower() == "published":
            checks.append(_check("PASS", "theme_published", "Active theme is published", "OK"))
        else:
            checks.append(
                _check(
                    "WARN",
                    "theme_published",
                    "Active theme is published",
                    "Publish or activate a theme from UI Theme.",
                )
            )
    else:
        checks.append(_check("FAIL", "active_theme", "Active theme exists", "Run Seed Defaults to create a theme."))
        checks.append(_check("FAIL", "theme_published", "Active theme is published", "Activate and publish a theme."))

    bundle_ok = 1
    bundle_hint = "OK"
    bundle_details = None
    try:
        _ = get_active_theme_bundle()
        published_on = theme_doc.published_on if theme_doc else None
        if not published_on:
            bundle_ok = 0
            bundle_hint = "Bundle API is reachable, but no published timestamp on active theme."
        else:
            if isinstance(published_on, datetime):
                bundle_details = published_on.isoformat()
            else:
                bundle_details = str(published_on)
    except Exception:
        bundle_ok = 0
        bundle_hint = "Theme bundle endpoint failed; check logs and theme config."

    checks.append(
        _check(
            "PASS" if bundle_ok and theme_doc else "WARN",
            "loader_bundle",
            "Loader/token bundle best-effort check",
            bundle_hint,
            details=bundle_details,
        )
    )

    nav_doc = _active_nav_doc()
    if nav_doc:
        item_count = _nav_item_count(nav_doc)
        if item_count > 0:
            checks.append(
                _check(
                    "PASS",
                    "active_nav",
                    "Active navigation profile exists with items",
                    "OK",
                    details=f"{nav_doc.name} ({item_count} items)",
                )
            )
        else:
            checks.append(
                _check(
                    "WARN",
                    "active_nav",
                    "Active navigation profile exists with items",
                    "Profile has zero items. Update navigation_json.",
                    details=nav_doc.name,
                )
            )
    else:
        checks.append(
            _check(
                "FAIL",
                "active_nav",
                "Active navigation profile exists with items",
                "Run Seed Defaults or set an active UI Panel Navigation profile.",
            )
        )

    preset_count = _safe_count("UI Layout Preset")
    if preset_count > 0:
        checks.append(_check("PASS", "layout_preset_count", "At least one layout preset exists", "OK"))
    else:
        checks.append(
            _check(
                "FAIL",
                "layout_preset_count",
                "At least one layout preset exists",
                "Run Seed Defaults to create a baseline UI Layout Preset.",
            )
        )

    flags = _feature_flags()
    if _bool01(flags.get("registry", 1), 1):
        published_registry_keys = 0
        if _dt_exists("UI API Registry"):
            published_registry_keys = cint(frappe.db.count("UI API Registry", filters={"enabled": 1}) or 0)
        if published_registry_keys > 0:
            checks.append(_check("PASS", "registry_enabled_keys", "API Registry has at least one published key", "OK"))
        else:
            checks.append(
                _check(
                    "WARN",
                    "registry_enabled_keys",
                    "API Registry has at least one published key",
                    "Create a UI API Registry key and publish it.",
                )
            )
    else:
        checks.append(_check("WARN", "registry_enabled_keys", "API Registry is enabled", "Registry feature flag is disabled."))

    if _bool01(flags.get("bridge", 1), 1):
        bridge_count = 0
        if _dt_exists("UI App Config"):
            bridge_count = cint(frappe.db.count("UI App Config", filters={"enabled": 1}) or 0)
        if bridge_count > 0:
            checks.append(_check("PASS", "bridge_config", "Bridge config exists", "OK"))
        else:
            checks.append(
                _check(
                    "WARN",
                    "bridge_config",
                    "Bridge config exists",
                    "Create an enabled UI App Config record.",
                )
            )
    else:
        checks.append(_check("WARN", "bridge_config", "Bridge feature is enabled", "Bridge feature flag is disabled."))

    return {"checks": checks}


@frappe.whitelist(allow_guest=False)
def seed_defaults():
    _require_admin()
    summary = []

    theme_doc = _active_theme_doc()
    if not theme_doc:
        theme_name = "Galaxy Default Theme"
        if not frappe.db.exists("UI Theme", theme_name):
            theme_doc = frappe.get_doc(
                {
                    "doctype": "UI Theme",
                    "theme_name": theme_name,
                    "status": "Published",
                    "is_active": 1,
                    "mode": "Auto",
                    "primary_color": "#2563eb",
                    "accent_color": "#0ea5e9",
                    "success_color": "#16a34a",
                    "warning_color": "#f59e0b",
                    "danger_color": "#dc2626",
                    "background_color": "#f8fafc",
                    "background_color_dark": "#0f172a",
                    "border_color": "#e2e8f0",
                    "card_color": "#ffffff",
                    "panel_color": "#f8fafc",
                    "text_primary": "#111827",
                    "text_muted": "#6b7280",
                    "sidebar_bg": "#eef2ff",
                    "sidebar_text": "#1f2937",
                    "sidebar_icon": "#334155",
                    "navbar_bg": "#ffffff",
                    "navbar_text": "#0f172a",
                    "navbar_icon": "#334155",
                }
            )
            theme_doc.insert(ignore_permissions=True)
            summary.append({"action": "create_theme", "status": "created", "name": theme_doc.name})
        else:
            theme_doc = frappe.get_doc("UI Theme", theme_name)
            theme_doc.status = "Published"
            theme_doc.is_active = 1
            theme_doc.save(ignore_permissions=True)
            summary.append({"action": "create_theme", "status": "updated", "name": theme_doc.name})
    else:
        summary.append({"action": "create_theme", "status": "skipped", "name": theme_doc.name})

    if _safe_count("UI Layout Preset") == 0:
        layout_doc = frappe.get_doc(
            {
                "doctype": "UI Layout Preset",
                "title": "Galaxy Default Layout",
                "enabled": 1,
                "is_default": 1,
                "shell_style": "admin",
                "targets_json": frappe.as_json(["panel", "dashboard"]),
                "component_options_json": frappe.as_json(
                    {"card": "soft_shadow", "button": "rounded_primary", "sidebar": "compact_dark"}
                ),
                "effects_json": frappe.as_json({"density": "compact", "radius_level": 3, "shadow_level": 2}),
            }
        )
        layout_doc.insert(ignore_permissions=True)
        summary.append({"action": "create_layout", "status": "created", "name": layout_doc.name})
    else:
        layout_doc = _active_layout_doc()
        summary.append({"action": "create_layout", "status": "skipped", "name": layout_doc.name if layout_doc else None})

    if _safe_count("UI Panel Navigation") == 0:
        nav_json = {
            "sections": [
                {
                    "label": "Galaxy UI",
                    "items": [
                        {"type": "route", "ref": "/app/ui_panel", "label": "Dashboard", "icon": "dashboard"},
                        {"type": "route", "ref": "#/control-center", "label": "Control Center", "icon": "settings"},
                    ],
                },
                {
                    "label": "System",
                    "items": [
                        {"type": "doctype", "ref": "User", "label": "Users", "icon": "users"},
                        {"type": "doctype", "ref": "Role", "label": "Roles", "icon": "shield"},
                        {"type": "doctype", "ref": "UI Theme", "label": "UI Themes", "icon": "palette"},
                        {"type": "doctype", "ref": "UI Layout Preset", "label": "UI Presets", "icon": "sliders-h"},
                    ],
                },
            ],
            "topbar": [],
        }
        nav_doc = frappe.get_doc(
            {
                "doctype": "UI Panel Navigation",
                "title": "Default Navigation",
                "status": "Published",
                "is_active": 1,
                "is_default": 1,
                "navigation_json": frappe.as_json(nav_json),
            }
        )
        nav_doc.insert(ignore_permissions=True)
        summary.append({"action": "create_navigation", "status": "created", "name": nav_doc.name})
    else:
        nav_doc = _active_nav_doc()
        summary.append({"action": "create_navigation", "status": "skipped", "name": nav_doc.name if nav_doc else None})

    if _safe_count("UI Component") == 0 or _safe_count("UI Component Option") == 0:
        seeded = component_api.seed_default_components()
        summary.append({"action": "seed_components", "status": "updated", "details": seeded})
    else:
        summary.append({"action": "seed_components", "status": "skipped"})

    frappe.db.commit()
    return {"ok": 1, "summary": summary}


@frappe.whitelist(allow_guest=False)
def apply_active_theme(theme_name: str | None = None):
    _require_admin()
    target_name = _find_target_name("UI Theme", theme_name, {"is_active": 1})
    doc = frappe.get_doc("UI Theme", target_name)
    doc.status = "Published"
    doc.is_active = 1
    doc.save(ignore_permissions=True)
    bundle = get_active_theme_bundle()
    frappe.db.commit()
    return {"ok": 1, "theme": doc.name, "status": doc.status, "bundle_hash": bundle.get("hash")}


@frappe.whitelist(allow_guest=False)
def apply_active_layout(preset_name: str | None = None):
    _require_admin()
    target_preset = _find_target_name("UI Layout Preset", preset_name, {"enabled": 1, "is_default": 1})
    target_theme = _find_target_name("UI Theme", None, {"is_active": 1})
    applied = layout_api.apply_layout_preset(preset_name=target_preset, theme_name=target_theme)
    return {"ok": 1, "applied": applied}


@frappe.whitelist(allow_guest=False)
def set_active_navigation(profile_name: str | None = None):
    _require_admin()
    target_name = _find_target_name("UI Panel Navigation", profile_name, {"is_active": 1})
    doc = frappe.get_doc("UI Panel Navigation", target_name)
    doc.status = "Published"
    doc.is_active = 1
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    active_bundle = panel_api.get_active_navigation()
    return {"ok": 1, "profile": doc.name, "status": doc.status, "hash": active_bundle.get("hash")}

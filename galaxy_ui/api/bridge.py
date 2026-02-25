from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint

from galaxy_ui.api import panel as panel_api
from galaxy_ui.api.theme import get_active_theme_bundle
from galaxy_ui.core.bundle import bundle_hash


SAFE_APP_CONFIG_FIELDS = {
    "name",
    "app_id",
    "enabled",
    "auth_mode",
    "api_base",
    "assets_base",
    "default_layout",
    "default_layout_preset",
    "default_theme",
    "navigation_profile",
    "base_urls",
    "feature_flags",
    "branding",
    "allowed_origins",
}


def _ensure_system_user() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Login required"))
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw(_("Galaxy UI bridge is available to System Users only"))


def _json_or_default(value, default):
    if value in (None, "", []):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        parsed = json.loads(value)
    except Exception:
        return default
    if isinstance(default, dict) and not isinstance(parsed, dict):
        return default
    if isinstance(default, list) and not isinstance(parsed, list):
        return default
    return parsed


def _get_app_config_doc(app_id: str | None):
    if not frappe.db.exists("DocType", "UI App Config"):
        return None

    filters = {"enabled": 1}
    if app_id:
        filters["app_id"] = app_id.strip().lower()

    names = frappe.get_all("UI App Config", filters=filters, pluck="name", order_by="modified desc", limit=1)
    if names:
        return frappe.get_doc("UI App Config", names[0])

    if app_id:
        return None

    names = frappe.get_all("UI App Config", filters={"enabled": 1}, pluck="name", order_by="modified desc", limit=1)
    if names:
        return frappe.get_doc("UI App Config", names[0])

    return None


def _sanitize_app_config(doc) -> dict:
    if not doc:
        return {}

    data = {}
    raw = doc.as_dict()
    for key in SAFE_APP_CONFIG_FIELDS:
        if key in raw:
            data[key] = raw.get(key)

    data["enabled"] = cint(data.get("enabled") or 0)
    data["api_base"] = (data.get("api_base") or "").strip()
    data["assets_base"] = (data.get("assets_base") or "").strip()
    data["default_layout"] = (data.get("default_layout") or "").strip()
    data["default_layout_preset"] = (data.get("default_layout_preset") or "").strip()
    data["default_theme"] = (data.get("default_theme") or "").strip()
    data["navigation_profile"] = (data.get("navigation_profile") or "").strip()
    data["base_urls"] = _json_or_default(data.get("base_urls"), {})
    data["feature_flags"] = _json_or_default(data.get("feature_flags"), {})
    data["branding"] = _json_or_default(data.get("branding"), {})
    data["allowed_origins"] = _json_or_default(data.get("allowed_origins"), [])
    return data


def _resolve_base_urls(app_config: dict) -> dict:
    urls = dict(app_config.get("base_urls") or {})
    if app_config.get("api_base") and not urls.get("api_base"):
        urls["api_base"] = app_config.get("api_base")
    if app_config.get("assets_base") and not urls.get("assets_base"):
        urls["assets_base"] = app_config.get("assets_base")
    return urls


def _get_navigation_for_profile(profile_name: str | None) -> dict:
    if not profile_name:
        return panel_api.get_active_navigation()

    if not frappe.db.exists("UI Panel Navigation", profile_name):
        return panel_api.get_active_navigation()

    doc = frappe.get_doc("UI Panel Navigation", profile_name)
    raw = (doc.navigation_json or "").strip()
    if not raw:
        return panel_api.get_active_navigation()

    try:
        parsed = panel_api._parse_navigation(raw)
        normalized = panel_api._normalize_navigation(parsed)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Galaxy UI Bridge Navigation Parse Failed")
        return panel_api.get_active_navigation()

    return {
        "name": doc.name,
        "title": doc.title or doc.name,
        "is_active": cint(doc.is_active or 0),
        "is_default": cint(doc.is_default or 0),
        "navigation": normalized,
        "navigation_json": raw,
        "hash": doc.nav_hash or bundle_hash(raw),
        "source": "ui_panel_navigation",
    }


@frappe.whitelist(allow_guest=False)
def get_ui_app_config(app_id: str):
    _ensure_system_user()
    if not app_id:
        frappe.throw(_("app_id is required"))

    doc = _get_app_config_doc(app_id)
    if not doc:
        return {"app_id": app_id, "enabled": 0}
    payload = _sanitize_app_config(doc)
    payload["base_urls"] = _resolve_base_urls(payload)
    return payload


@frappe.whitelist(allow_guest=False)
def get_ui_nav(app_id: str | None = None):
    _ensure_system_user()
    clean_app_id = (app_id or "").strip().lower() or None
    app_doc = _get_app_config_doc(clean_app_id) if clean_app_id else None
    app_config = _sanitize_app_config(app_doc) if app_doc else {}
    nav = _get_navigation_for_profile(app_config.get("navigation_profile"))
    return {
        "app_id": clean_app_id,
        "name": nav.get("name"),
        "title": nav.get("title"),
        "hash": nav.get("hash"),
        "navigation": nav.get("navigation"),
        "source": nav.get("source"),
        "profile": app_config.get("navigation_profile") or nav.get("name"),
    }


@frappe.whitelist(allow_guest=False)
def get_ui_bundle(app_id: str):
    _ensure_system_user()
    if not app_id:
        frappe.throw(_("app_id is required"))

    app_doc = _get_app_config_doc(app_id)
    app_config = _sanitize_app_config(app_doc)
    app_config["base_urls"] = _resolve_base_urls(app_config)

    theme = get_active_theme_bundle()
    nav = get_ui_nav(app_id)

    merged_flags = dict(theme.get("flags") or {})
    merged_flags.update(app_config.get("feature_flags") or {})

    merged_layout = dict(theme.get("layout") or {})
    if app_config.get("default_layout") and "name" not in merged_layout:
        merged_layout["name"] = app_config.get("default_layout")
    if app_config.get("default_layout_preset") and "preset" not in merged_layout:
        merged_layout["preset"] = app_config.get("default_layout_preset")

    payload_hash = bundle_hash(
        str(theme.get("hash") or ""),
        str(nav.get("hash") or ""),
        frappe.as_json(app_config),
    )

    return {
        "app_id": app_id.strip().lower(),
        "hash": payload_hash,
        "theme": {
            "mode": theme.get("mode"),
            "css_tokens": theme.get("css_tokens"),
            "hash": theme.get("hash"),
        },
        "flags": merged_flags,
        "layout": merged_layout,
        "navigation": nav,
        "app_config": app_config,
        "env": {
            "site": frappe.local.site,
            "user": frappe.session.user,
            "is_system_user": 1,
        },
    }

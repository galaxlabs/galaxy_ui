from __future__ import annotations

import json
import re

import frappe
from frappe import _
from frappe.utils import cint
from jsonschema import Draft202012Validator

from galaxy_ui.api.theme import get_active_theme_bundle
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


DEFAULT_NAVIGATION_V1 = {
    "sections": [
        {
            "label": "Core",
            "items": [
                {"type": "doctype", "ref": "User", "label": "Users", "icon": "users"},
                {"type": "doctype", "ref": "Role", "label": "Roles", "icon": "shield"},
            ],
        }
    ],
    "topbar": [{"type": "route", "ref": "ui-panel", "label": "Panel Home", "icon": "home"}],
}

DEFAULT_DASHBOARD_JSON = {
    "title": "Panel Dashboard",
    "sections": [
        {
            "label": "Overview",
            "widgets": [
                {
                    "type": "kpi_count",
                    "label": "Users",
                    "doctype": "User",
                    "filters": {"enabled": 1},
                },
                {"type": "link", "label": "Open Customers", "route": "#/doctype/Customer/list"},
            ],
        }
    ],
}

DEFAULT_PANEL_FEATURES = {
    "appearance": 1,
    "builder": 1,
    "components": 1,
    "dashboard": 1,
    "navigation": 1,
    "registry": 1,
    "bridge": 1,
}


def _ensure_system_user() -> None:
    if frappe.session.user == "Guest":
        frappe.throw("Login required")
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw("Galaxy UI Panel is available to System Users only")


def _as_feature_bool(value, default: int = 0) -> int:
    if value in (None, ""):
        return cint(default or 0)
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return 1 if cint(value) else 0
    return 1 if str(value).strip().lower() in {"1", "true", "yes", "on", "y"} else 0


def _panel_feature_flags(theme_bundle: dict | None = None) -> dict:
    features = dict(DEFAULT_PANEL_FEATURES)

    # Site-level override from site_config.json:
    # "galaxy_ui_features": {"builder": 0, "appearance": 1, ...}
    raw_override = frappe.conf.get("galaxy_ui_features")
    override = {}
    if isinstance(raw_override, str):
        try:
            override = frappe.parse_json(raw_override) or {}
        except Exception:
            override = {}
    elif isinstance(raw_override, dict):
        override = raw_override

    if isinstance(override, dict):
        for key in features:
            if key in override:
                features[key] = _as_feature_bool(override.get(key), features[key])

    return features


def _parse_navigation(raw_json: str) -> dict:
    text = (raw_json or "").strip()
    if not text:
        return DEFAULT_NAVIGATION_V1
    data = json.loads(text)
    _validate_navigation(data)
    return data


def _validate_navigation(data: dict) -> None:
    """
    Validate nav JSON with best-effort compatibility.
    If runtime still has older bundle.py loaded (without validate_ui_panel_navigation_v1),
    fall back to local schema validation here so panel APIs don't crash.
    """
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


def _get_active_navigation_doc() -> dict | None:
    if not frappe.db.exists("DocType", "UI Panel Navigation"):
        return None

    active_names = frappe.get_all(
        "UI Panel Navigation",
        filters={"is_active": 1},
        pluck="name",
        order_by="is_default desc, modified desc",
        limit=1,
    )
    if active_names:
        return frappe.get_doc("UI Panel Navigation", active_names[0]).as_dict()

    default_names = frappe.get_all(
        "UI Panel Navigation",
        filters={"is_default": 1},
        pluck="name",
        order_by="modified desc",
        limit=1,
    )
    if default_names:
        return frappe.get_doc("UI Panel Navigation", default_names[0]).as_dict()

    any_names = frappe.get_all("UI Panel Navigation", pluck="name", order_by="modified desc", limit=1)
    if any_names:
        return frappe.get_doc("UI Panel Navigation", any_names[0]).as_dict()

    return None


def _doctype_route(doctype_name: str) -> str:
    if not doctype_name:
        return ""
    return f"/app/{frappe.scrub(doctype_name)}"


def _report_route(report_name: str) -> str:
    if not report_name:
        return ""
    return f"/app/query-report/{frappe.scrub(report_name)}"


def _page_route(page_name: str) -> str:
    if not page_name:
        return ""
    return f"/app/{frappe.scrub(page_name)}"


def _workspace_route(workspace_name: str) -> str:
    if not workspace_name:
        return ""
    return f"/app/{frappe.scrub(workspace_name)}"


def _normalize_nav_item(item: dict) -> dict:
    item_type = (item.get("type") or "").strip().lower()
    ref = (item.get("ref") or "").strip()
    label = (item.get("label") or ref or "Item").strip()
    icon = (item.get("icon") or "").strip()
    route = (item.get("route") or "").strip()
    params = item.get("params") if isinstance(item.get("params"), dict) else {}
    badge_rule = (item.get("badge_rule") or "").strip()

    if not route:
        if item_type == "doctype":
            route = _doctype_route(ref)
        elif item_type == "report":
            route = _report_route(ref)
        elif item_type == "page":
            route = _page_route(ref)
        elif item_type == "workspace":
            route = _workspace_route(ref)
        elif item_type == "url":
            route = ref
        elif item_type == "route":
            route = ref if ref.startswith("/") else f"/app/{frappe.scrub(ref)}"

    return {
        "type": item_type,
        "ref": ref,
        "label": label,
        "icon": icon,
        "route": route,
        "params": params,
        "badge_rule": badge_rule,
    }


def _normalize_navigation(nav: dict) -> dict:
    sections = []
    for section in nav.get("sections", []):
        items = [_normalize_nav_item(i) for i in (section.get("items") or []) if isinstance(i, dict)]
        sections.append({"label": (section.get("label") or "Section").strip(), "items": items})

    topbar = [_normalize_nav_item(i) for i in nav.get("topbar", []) if isinstance(i, dict)]
    return {"sections": sections, "topbar": topbar}


def _parse_json_arg(value, default):
    if value in (None, "", []):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return frappe.parse_json(value)
    except Exception:
        return default


def _safe_order_by(order_by: str, default: str = "modified desc") -> str:
    raw = (order_by or "").strip() or default
    if not re.fullmatch(r"[a-zA-Z0-9_`,.\s]+", raw):
        return default
    return raw


def _safe_list_fields(doctype: str, fields: list[str]) -> list[str]:
    meta = frappe.get_meta(doctype)
    allowed_fieldnames = {df.fieldname for df in meta.fields}
    allowed_fieldnames.update({"name", "owner", "modified", "creation", "docstatus"})

    safe_fields = []
    for f in fields or []:
        field = (f or "").strip()
        if field in allowed_fieldnames:
            safe_fields.append(field)

    if "name" not in safe_fields:
        safe_fields.insert(0, "name")
    return safe_fields[:8]


def _parse_dashboard_json(raw: str) -> dict:
    text = (raw or "").strip()
    if not text:
        return DEFAULT_DASHBOARD_JSON
    try:
        parsed = json.loads(text)
    except Exception:
        return DEFAULT_DASHBOARD_JSON
    if not isinstance(parsed, dict):
        return DEFAULT_DASHBOARD_JSON
    if "sections" not in parsed or not isinstance(parsed.get("sections"), list):
        return DEFAULT_DASHBOARD_JSON
    return parsed


@frappe.whitelist(allow_guest=False)
def get_active_navigation():
    _ensure_system_user()

    doc = _get_active_navigation_doc()
    if not doc:
        normalized = _normalize_navigation(DEFAULT_NAVIGATION_V1)
        raw = frappe.as_json(DEFAULT_NAVIGATION_V1)
        return {
            "name": None,
            "title": "Default Navigation",
            "is_active": 1,
            "is_default": 1,
            "navigation": normalized,
            "navigation_json": raw,
            "hash": bundle_hash(raw),
            "source": "fallback",
        }

    raw = doc.get("navigation_json") or doc.get("nav_json") or ""
    try:
        navigation = _parse_navigation(raw)
        source = "ui_panel_navigation"
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Galaxy UI Panel Navigation Parse Failed")
        navigation = DEFAULT_NAVIGATION_V1
        source = "fallback"

    normalized = _normalize_navigation(navigation)
    return {
        "name": doc.get("name"),
        "title": doc.get("title") or doc.get("name"),
        "is_active": int(doc.get("is_active") or 0),
        "is_default": int(doc.get("is_default") or 0),
        "navigation": normalized,
        "navigation_json": raw or frappe.as_json(navigation),
        "hash": doc.get("nav_hash") or bundle_hash(raw or frappe.as_json(navigation)),
        "source": source,
    }


@frappe.whitelist(allow_guest=False)
def list_available_resources():
    _ensure_system_user()

    doctypes = []
    for dt in frappe.get_all(
        "DocType",
        fields=["name", "module", "title_field"],
        filters={"istable": 0, "issingle": 0, "custom": 0},
        order_by="name asc",
        limit_page_length=1000,
    ):
        dt_name = dt.get("name")
        if not dt_name:
            continue
        if not frappe.has_permission(doctype=dt_name, ptype="read"):
            continue
        doctypes.append(
            {
                "name": dt_name,
                "label": frappe.unscrub(dt_name),
                "route": _doctype_route(dt_name),
                "module": dt.get("module"),
            }
        )

    reports = []
    if frappe.db.exists("DocType", "Report"):
        for report in frappe.get_all(
            "Report",
            fields=["name", "module"],
            order_by="name asc",
            limit_page_length=1000,
        ):
            report_name = report.get("name")
            if not report_name:
                continue
            if not frappe.has_permission(doctype="Report", ptype="read", doc=report_name):
                continue
            reports.append(
                {
                    "name": report_name,
                    "label": report_name,
                    "route": _report_route(report_name),
                    "module": report.get("module"),
                }
            )

    pages = []
    for page in frappe.get_all(
        "Page",
        fields=["name", "module"],
        order_by="name asc",
        limit_page_length=500,
    ):
        page_name = page.get("name")
        if not page_name:
            continue
        if not frappe.has_permission(doctype="Page", ptype="read", doc=page_name):
            continue
        pages.append(
            {
                "name": page_name,
                "label": frappe.unscrub(page_name),
                "route": _page_route(page_name),
                "module": page.get("module"),
            }
        )

    return {"doctypes": doctypes, "reports": reports, "pages": pages}


@frappe.whitelist(allow_guest=False)
def get_panel_bundle():
    _ensure_system_user()

    theme_bundle = get_active_theme_bundle()
    navigation_bundle = get_active_navigation()
    features = _panel_feature_flags(theme_bundle)

    return {
        "theme": theme_bundle,
        "navigation": navigation_bundle,
        "features": features,
        "env": {
            "site": frappe.local.site,
            "user": frappe.session.user,
            "is_system_user": 1,
            "panel_route": "/app/ui_panel",
        },
    }


@frappe.whitelist(allow_guest=False)
def get_doctype_meta(doctype: str):
    _ensure_system_user()

    if not doctype:
        frappe.throw(_("doctype is required"))
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Invalid DocType: {0}").format(doctype))
    if not frappe.has_permission(doctype=doctype, ptype="read"):
        frappe.throw(_("Not permitted for DocType: {0}").format(doctype))

    meta = frappe.get_meta(doctype)
    safe_fields = []
    default_fields = []

    for df in meta.fields:
        if df.fieldtype in {
            "Section Break",
            "Column Break",
            "Tab Break",
            "HTML",
            "Button",
            "Table",
            "Table MultiSelect",
            "Fold",
        }:
            continue
        safe_fields.append(
            {
                "fieldname": df.fieldname,
                "label": df.label,
                "fieldtype": df.fieldtype,
                "options": df.options,
                "in_list_view": cint(df.in_list_view or 0),
            }
        )
        if cint(df.in_list_view):
            default_fields.append(df.fieldname)

    title_field = meta.title_field or "name"
    if title_field not in default_fields:
        default_fields = [title_field] + default_fields
    for fallback in ("name", "status", "modified"):
        if fallback not in default_fields:
            default_fields.append(fallback)

    return {
        "doctype": doctype,
        "title_field": title_field,
        "fields": safe_fields,
        "default_fields": default_fields[:6],
        "is_submittable": cint(meta.is_submittable or 0),
    }


@frappe.whitelist(allow_guest=False)
def get_list_data(
    doctype: str,
    fields=None,
    filters=None,
    order_by: str | None = None,
    start: int = 0,
    page_length: int = 20,
):
    _ensure_system_user()

    if not doctype:
        frappe.throw(_("doctype is required"))
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Invalid DocType: {0}").format(doctype))
    if not frappe.has_permission(doctype=doctype, ptype="read"):
        frappe.throw(_("Not permitted for DocType: {0}").format(doctype))

    parsed_fields = _parse_json_arg(fields, [])
    parsed_filters = _parse_json_arg(filters, [])
    safe_fields = _safe_list_fields(doctype, parsed_fields)
    safe_order_by = _safe_order_by(order_by or "modified desc")

    page_length = min(max(cint(page_length or 20), 5), 50)
    start = max(cint(start or 0), 0)

    rows = frappe.get_list(
        doctype,
        fields=safe_fields,
        filters=parsed_filters,
        order_by=safe_order_by,
        start=start,
        page_length=page_length,
    )

    total = None
    try:
        total_row = frappe.get_list(
            doctype,
            fields=["count(name) as total"],
            filters=parsed_filters,
            page_length=1,
        )
        if total_row:
            total = cint(total_row[0].get("total") or 0)
    except Exception:
        total = None

    return {
        "doctype": doctype,
        "fields": safe_fields,
        "rows": rows,
        "start": start,
        "page_length": page_length,
        "total": total,
        "has_more": len(rows) == page_length if total is None else (start + len(rows) < total),
    }


@frappe.whitelist(allow_guest=False)
def get_report_data(report_name: str, filters=None):
    _ensure_system_user()

    if not report_name:
        frappe.throw(_("report_name is required"))
    if not frappe.db.exists("Report", report_name):
        frappe.throw(_("Report not found: {0}").format(report_name))
    if not frappe.has_permission(doctype="Report", ptype="read", doc=report_name):
        frappe.throw(_("Not permitted for Report: {0}").format(report_name))

    report_doc = frappe.get_doc("Report", report_name)
    if report_doc.report_type != "Query Report":
        frappe.throw(_("Only Query Report is supported in Phase 2 MVP"))

    parsed_filters = _parse_json_arg(filters, {})
    from frappe.desk.query_report import run

    data = run(report_name, filters=parsed_filters, ignore_prepared_report=True)
    return {
        "report_name": report_name,
        "columns": data.get("columns") or [],
        "rows": data.get("result") or [],
        "chart": data.get("chart"),
        "message": data.get("message"),
    }


@frappe.whitelist(allow_guest=False)
def get_dashboard(name: str):
    _ensure_system_user()

    if not name:
        frappe.throw(_("Dashboard name is required"))
    if not frappe.db.exists("UI Panel Dashboard", name):
        frappe.throw(_("UI Panel Dashboard not found: {0}").format(name))

    doc = frappe.get_doc("UI Panel Dashboard", name)
    payload = _parse_dashboard_json(doc.dashboard_json or "")
    payload.setdefault("title", doc.title or doc.name)
    return {
        "name": doc.name,
        "title": doc.title,
        "is_default": cint(doc.is_default or 0),
        "dashboard": payload,
    }


@frappe.whitelist(allow_guest=False)
def get_default_dashboard():
    _ensure_system_user()

    if not frappe.db.exists("DocType", "UI Panel Dashboard"):
        return {"name": None, "title": "Panel Dashboard", "is_default": 1, "dashboard": DEFAULT_DASHBOARD_JSON}

    names = frappe.get_all(
        "UI Panel Dashboard",
        filters={"is_default": 1},
        pluck="name",
        order_by="modified desc",
        limit=1,
    )
    if not names:
        names = frappe.get_all("UI Panel Dashboard", pluck="name", order_by="modified desc", limit=1)
    if names:
        return get_dashboard(names[0])

    return {"name": None, "title": "Panel Dashboard", "is_default": 1, "dashboard": DEFAULT_DASHBOARD_JSON}


@frappe.whitelist(allow_guest=False)
def get_kpi(doctype: str, filters=None):
    _ensure_system_user()

    if not doctype:
        frappe.throw(_("doctype is required"))
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Invalid DocType: {0}").format(doctype))
    if not frappe.has_permission(doctype=doctype, ptype="read"):
        frappe.throw(_("Not permitted for DocType: {0}").format(doctype))

    parsed_filters = _parse_json_arg(filters, {})
    total = frappe.db.count(doctype, filters=parsed_filters)
    return {"doctype": doctype, "count": cint(total or 0)}


@frappe.whitelist(allow_guest=False)
def list_navigation_profiles():
    _ensure_system_user()
    if not frappe.db.exists("DocType", "UI Panel Navigation"):
        return []
    return frappe.get_all(
        "UI Panel Navigation",
        fields=["name", "title", "is_active", "is_default", "modified"],
        order_by="is_default desc, modified desc",
        limit_page_length=200,
    )


@frappe.whitelist(allow_guest=False)
def save_navigation_profile(
    title: str,
    navigation_json,
    name: str | None = None,
    is_active: int = 1,
    is_default: int = 0,
):
    _ensure_system_user()
    if not frappe.has_permission("UI Panel Navigation", ptype="write"):
        frappe.throw(_("Not permitted to manage UI Panel Navigation"))

    if not title:
        frappe.throw(_("Title is required"))

    parsed_nav = _parse_json_arg(navigation_json, None)
    if not isinstance(parsed_nav, dict):
        frappe.throw(_("navigation_json must be a JSON object"))
    _validate_navigation(parsed_nav)

    payload = {
        "title": title.strip(),
        "navigation_json": frappe.as_json(parsed_nav),
        "is_active": cint(is_active or 0),
        "is_default": cint(is_default or 0),
    }

    if name:
        if not frappe.db.exists("UI Panel Navigation", name):
            frappe.throw(_("UI Panel Navigation not found: {0}").format(name))
        doc = frappe.get_doc("UI Panel Navigation", name)
        doc.update(payload)
        doc.save()
    else:
        doc = frappe.get_doc({"doctype": "UI Panel Navigation", **payload})
        doc.insert()

    return {
        "name": doc.name,
        "title": doc.title,
        "is_active": cint(doc.is_active or 0),
        "is_default": cint(doc.is_default or 0),
        "hash": doc.nav_hash,
    }

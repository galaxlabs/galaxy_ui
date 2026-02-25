from __future__ import annotations

import json

import frappe

DEFAULT_NAV = {
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


def _normalize_item(item: dict) -> dict:
    item = item or {}
    label = item.get("label") or item.get("ref") or item.get("route") or "Item"
    route = (item.get("route") or "").strip()
    item_type = (item.get("type") or "").strip().lower()
    ref = (item.get("ref") or "").strip()

    if not item_type:
        if route:
            item_type = "route"
            ref = ref or route
        else:
            item_type = "doctype"
            ref = ref or label

    if not ref:
        ref = route or label

    return {
        "type": item_type,
        "ref": ref,
        "label": label,
        "icon": (item.get("icon") or "").strip(),
    }


def _to_v1_navigation(raw: str) -> dict:
    text = (raw or "").strip()
    if not text:
        return DEFAULT_NAV

    try:
        parsed = json.loads(text)
    except Exception:
        return DEFAULT_NAV

    if isinstance(parsed, dict) and "sections" in parsed and "topbar" in parsed:
        return parsed

    if isinstance(parsed, dict) and isinstance(parsed.get("sidebar"), list):
        sections = []
        for sec in parsed.get("sidebar") or []:
            items = [_normalize_item(i) for i in (sec.get("items") or [])]
            sections.append({"label": sec.get("label") or "Section", "items": items})
        topbar = [_normalize_item(i) for i in (parsed.get("topbar") or [])]
        return {"sections": sections, "topbar": topbar}

    return DEFAULT_NAV


def execute():
    if not frappe.db.exists("DocType", "UI Panel Navigation"):
        return

    if frappe.db.exists("UI Panel Navigation", {"is_default": 1}):
        return

    old_single_rows = frappe.db.sql(
        """
        select field, value
        from tabSingles
        where doctype = %s
        """,
        ("UI Panel Navigation",),
        as_dict=True,
    )
    old_single = {r.field: r.value for r in old_single_rows}

    if not old_single:
        navigation_json = json.dumps(DEFAULT_NAV)
        enabled = 1
        notes = ""
    else:
        navigation_json = old_single.get("navigation_json") or old_single.get("nav_json") or ""
        enabled = int(old_single.get("is_active") or old_single.get("enabled") or 1)
        notes = old_single.get("notes") or ""
        navigation_json = json.dumps(_to_v1_navigation(navigation_json))

    title = "Default Navigation"
    doc = frappe.get_doc(
        {
            "doctype": "UI Panel Navigation",
            "title": title,
            "is_active": enabled,
            "is_default": 1,
            "navigation_json": navigation_json,
            "notes": notes,
        }
    )
    doc.insert(ignore_permissions=True)

from __future__ import annotations

import json

import frappe


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
                {"type": "link", "label": "Customers", "route": "#/doctype/Customer/list"},
                {"type": "link", "label": "Sales Invoice", "route": "#/doctype/Sales Invoice/list"},
            ],
        }
    ],
}


def execute():
    if not frappe.db.exists("DocType", "UI Panel Dashboard"):
        return

    if frappe.db.exists("UI Panel Dashboard", {"is_default": 1}):
        return

    doc = frappe.get_doc(
        {
            "doctype": "UI Panel Dashboard",
            "title": "Default Dashboard",
            "is_default": 1,
            "dashboard_json": json.dumps(DEFAULT_DASHBOARD_JSON),
            "notes": "Auto-seeded by Galaxy UI Phase 2 patch",
        }
    )
    doc.insert(ignore_permissions=True)

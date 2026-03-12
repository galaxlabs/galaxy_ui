from __future__ import annotations

import frappe


def execute():
    if not frappe.db.exists("DocType", "UI Layout Preset"):
        return

    if frappe.db.has_column("UI Layout Preset", "apply_scope"):
        frappe.db.sql(
            """
            update `tabUI Layout Preset`
            set apply_scope = 'UI Panel'
            where ifnull(apply_scope, '') = ''
            """
        )

    if frappe.db.has_column("UI Layout Preset", "component_css_vars_json"):
        frappe.db.sql(
            """
            update `tabUI Layout Preset`
            set component_css_vars_json = '{}'
            where ifnull(component_css_vars_json, '') = ''
            """
        )

    if frappe.db.has_column("UI Layout Preset", "component_classes"):
        frappe.db.sql(
            """
            update `tabUI Layout Preset`
            set component_classes = ''
            where component_classes is null
            """
        )

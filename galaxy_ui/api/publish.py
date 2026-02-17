from __future__ import annotations

import frappe
from frappe.utils import now_datetime


@frappe.whitelist()
def publish_theme(name: str):
    """
    Publish a UI Theme and enforce single-active theme per site.

    Effects:
    - status = "Published"
    - is_active = 1
    - published_on = now
    - published_by = current user
    - all other themes is_active = 0
    """
    frappe.only_for("System Manager")

    if not name:
        frappe.throw("Theme name is required")

    dt = "UI Theme"
    if not frappe.db.exists(dt, name):
        frappe.throw(f"UI Theme not found: {name}")

    # Deactivate any currently active theme(s) except this one
    frappe.db.sql(
        f"""
        UPDATE `tab{dt}`
        SET is_active = 0
        WHERE IFNULL(is_active, 0) = 1
          AND name != %s
        """,
        (name,),
    )

    # Activate + publish this theme
    theme = frappe.get_doc(dt, name)
    theme.status = "Published"
    theme.is_active = 1
    theme.published_on = now_datetime()
    theme.published_by = frappe.session.user

    theme.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "ok": True,
        "theme": theme.name,
        "status": theme.status,
        "is_active": theme.is_active,
        "published_on": str(theme.published_on) if theme.published_on else None,
        "published_by": theme.published_by,
    }

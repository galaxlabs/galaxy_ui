import frappe
from galaxy_ui.api.panel import get_active_navigation


@frappe.whitelist(allow_guest=False)
def get_ui_panel_navigation():
    """
    Backward-compatible wrapper around panel.get_active_navigation().
    """
    payload = get_active_navigation()
    return {
        "enabled": int(payload.get("is_active") or 0),
        "nav": payload.get("navigation"),
        "nav_json": payload.get("navigation_json"),
        "hash": payload.get("hash"),
        "source": payload.get("source"),
        "error": None,
    }

import json
import hashlib
import frappe


def _safe_json_loads(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return None, "nav_json is empty"
    try:
        return json.loads(raw), None
    except Exception as e:
        return None, str(e)


def _sha1(s: str) -> str:
    return hashlib.sha1((s or "").encode("utf-8")).hexdigest()


@frappe.whitelist(allow_guest=False)
def get_ui_panel_navigation():
    """
    Returns the current UI Panel sidebar navigation.

    Response:
      {
        "enabled": 1|0,
        "nav": <dict/list> | null,
        "nav_json": "<raw json string>",
        "hash": "<sha1>",
        "source": "ui_panel_navigation" | "fallback",
        "error": "<string or null>"
      }
    """
    # Single DocType
    doc = frappe.get_single("UI Panel Navigation")

    enabled = int(doc.enabled or 0)
    raw = doc.nav_json or ""
    nav, err = _safe_json_loads(raw)

    # Prefer stored hash if present, else compute from raw
    h = (doc.nav_hash or "").strip() or _sha1(raw)

    # If disabled, UI should fall back to built-in defaults
    if not enabled:
        return {
            "enabled": 0,
            "nav": None,
            "nav_json": raw,
            "hash": h,
            "source": "fallback",
            "error": err,
        }

    return {
        "enabled": 1,
        "nav": nav,
        "nav_json": raw,
        "hash": h,
        "source": "ui_panel_navigation",
        "error": err,
    }
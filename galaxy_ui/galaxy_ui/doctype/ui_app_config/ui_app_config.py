from __future__ import annotations

import json
import re
from urllib.parse import urlparse

import frappe
from frappe.model.document import Document


class UIAppConfig(Document):
    def validate(self):
        self.app_id = (self.app_id or "").strip().lower()
        if not self.app_id:
            frappe.throw("App ID is required")
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,120}", self.app_id):
            frappe.throw("App ID may contain lowercase letters, digits, dot, underscore and dash")

        self.api_base = _normalize_url(self.api_base)
        self.assets_base = _normalize_url(self.assets_base)
        self.base_urls = _normalize_json(self.base_urls, fieldname="base_urls", expected=dict)
        self.feature_flags = _normalize_json(self.feature_flags, fieldname="feature_flags", expected=dict)
        self.branding = _normalize_json(self.branding, fieldname="branding", expected=dict)
        self.allowed_origins = _normalize_json(self.allowed_origins, fieldname="allowed_origins", expected=list)


def _normalize_json(raw, fieldname: str, expected):
    text = (raw or "").strip()
    if not text:
        if expected is dict:
            return "{}"
        return "[]"

    try:
        parsed = json.loads(text)
    except Exception as exc:
        frappe.throw(f"{fieldname} must be valid JSON: {exc}")

    if not isinstance(parsed, expected):
        if isinstance(expected, tuple):
            names = ", ".join(t.__name__ for t in expected)
            frappe.throw(f"{fieldname} must be one of: {names}")
        frappe.throw(f"{fieldname} must be {expected.__name__}")

    return json.dumps(parsed, separators=(",", ":"))


def _normalize_url(value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        return ""

    # Allow relative paths for proxied setups, otherwise require http/https.
    if text.startswith("/"):
        return text.rstrip("/")

    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        frappe.throw("URL fields must be absolute http(s) URLs or begin with '/'")

    return text.rstrip("/")

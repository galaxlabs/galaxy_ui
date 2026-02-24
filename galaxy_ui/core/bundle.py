"""
Bundle helpers: compute hash/version and assemble payload for the runtime loader.
"""
from __future__ import annotations
import hashlib


def bundle_hash(*parts: str) -> str:
    raw = "\n".join([p or "" for p in parts]).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]

# ------------------------------
# JSON Schema Validation
# ------------------------------

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from galaxy_ui.core.schemas import UI_LAYOUT_PRESET_SCHEMA


def validate_ui_layout_preset(data: dict) -> None:
    """
    Validates UI Layout Preset JSON against schema.
    Raises frappe.ValidationError with readable messages when invalid.
    """
    import frappe

    try:
        validator = Draft202012Validator(UI_LAYOUT_PRESET_SCHEMA)
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            msgs = []
            for e in errors[:8]:
                path = ".".join([str(p) for p in e.path]) or "(root)"
                msgs.append(f"{path}: {e.message}")
            frappe.throw("Invalid UI Layout Preset:\n" + "\n".join(msgs))
    except ValidationError as e:
        frappe.throw(f"Invalid UI Layout Preset: {e.message}")
from __future__ import annotations

import json
import re

import frappe
from frappe import _
from frappe.utils import cint


ALLOWED_FIELDTYPES = {
    "Data",
    "Link",
    "Select",
    "Int",
    "Float",
    "Currency",
    "Date",
    "Datetime",
    "Check",
    "Small Text",
}
ALLOWED_FORM_FIELDTYPES = {
    "Data",
    "Link",
    "Select",
    "Int",
    "Float",
    "Currency",
    "Date",
    "Datetime",
    "Check",
    "Small Text",
}
ALLOWED_OPERATORS = {"=", "!=", "<", "<=", ">", ">=", "like", "in", "not in", "between"}
DISALLOWED_DOCTYPES = {"DocType"}


def _ensure_system_user() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Login required"))
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw(_("Galaxy UI Panel is available to System Users only"))


def _parse_json(raw, default):
    if raw in (None, "", []):
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return default


def _safe_order_by(order_by: str, allowed_fields: set[str]) -> str:
    raw = (order_by or "").strip()
    if not raw:
        return "modified desc"
    if not re.fullmatch(r"[a-zA-Z0-9_`,.\s]+", raw):
        return "modified desc"
    first = raw.split()[0].replace("`", "").replace(",", "").strip()
    if first not in allowed_fields:
        return "modified desc"
    return raw


def _allowed_fieldnames(meta) -> tuple[set[str], list[str]]:
    allowed = {"name", "modified", "owner", "docstatus"}
    preferred = []

    for df in meta.fields:
        if not df.fieldname:
            continue
        if df.fieldtype not in ALLOWED_FIELDTYPES:
            continue
        allowed.add(df.fieldname)
        if cint(df.in_list_view or 0):
            preferred.append(df.fieldname)

    title_field = (meta.title_field or "").strip()
    if title_field and title_field in allowed and title_field not in preferred:
        preferred.insert(0, title_field)

    for fallback in ("name", "docstatus", "modified"):
        if fallback in allowed and fallback not in preferred:
            preferred.append(fallback)

    return allowed, preferred


def _sanitize_fields(meta, requested_fields) -> list[str]:
    allowed, preferred = _allowed_fieldnames(meta)
    requested = [str(f or "").strip() for f in (requested_fields or []) if str(f or "").strip()]
    if requested:
        fields = [f for f in requested if f in allowed]
    else:
        fields = preferred

    if "name" not in fields:
        fields.insert(0, "name")
    fields = fields[:10]
    return fields


def _sanitize_filters(doctype: str, raw_filters, meta) -> list:
    allowed, _ = _allowed_fieldnames(meta)
    if not raw_filters:
        return []

    out = []
    if isinstance(raw_filters, dict):
        for fieldname, value in raw_filters.items():
            field = str(fieldname or "").strip()
            if field in allowed:
                out.append([doctype, field, "=", value])
        return out

    if isinstance(raw_filters, list):
        for cond in raw_filters:
            if not isinstance(cond, list):
                continue
            if len(cond) == 3:
                field, op, value = cond
                dt = doctype
            elif len(cond) == 4:
                dt, field, op, value = cond
            else:
                continue
            if dt != doctype:
                continue
            field = str(field or "").strip()
            op_norm = str(op or "").strip().lower()
            if field not in allowed:
                continue
            if op_norm not in ALLOWED_OPERATORS:
                continue
            out.append([doctype, field, op_norm, value])

    return out


def _column_payload(meta, fields: list[str]) -> list[dict]:
    title_field = (meta.title_field or "").strip()
    cols = []
    for fieldname in fields:
        if fieldname in {"name", "modified", "owner", "docstatus"}:
            ftype = "Data" if fieldname != "docstatus" else "Int"
            label = fieldname.title()
        else:
            df = meta.get_field(fieldname)
            if not df:
                continue
            ftype = df.fieldtype
            label = df.label or fieldname
        width = 220 if fieldname == title_field else 160
        cols.append({"fieldname": fieldname, "label": label, "fieldtype": ftype, "width": width})
    return cols


def _safe_form_fields(meta) -> list[dict]:
    fields = []
    for df in meta.fields:
        if not df.fieldname:
            continue
        if df.fieldtype not in ALLOWED_FORM_FIELDTYPES:
            continue
        fields.append(
            {
                "fieldname": df.fieldname,
                "label": df.label or df.fieldname,
                "fieldtype": df.fieldtype,
                "options": df.options or "",
                "read_only": cint(df.read_only or 0),
                "reqd": cint(df.reqd or 0),
                "hidden": cint(df.hidden or 0),
            }
        )
    return fields[:40]


def _sanitize_form_values(values, meta) -> dict:
    raw = _parse_json(values, {})
    if not isinstance(raw, dict):
        return {}

    allowed = {}
    for df in _safe_form_fields(meta):
        if cint(df.get("read_only") or 0) or cint(df.get("hidden") or 0):
            continue
        allowed[df["fieldname"]] = df

    out = {}
    for key, value in raw.items():
        fieldname = str(key or "").strip()
        if fieldname not in allowed:
            continue
        out[fieldname] = value
    return out


@frappe.whitelist(allow_guest=False)
def get_doctype_meta(doctype: str):
    _ensure_system_user()
    doctype = (doctype or "").strip()
    if not doctype:
        frappe.throw(_("doctype is required"))
    if doctype in DISALLOWED_DOCTYPES:
        frappe.throw(_("DocType is not allowed in panel content engine: {0}").format(doctype))
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Invalid DocType: {0}").format(doctype))
    if not frappe.has_permission(doctype=doctype, ptype="read"):
        frappe.throw(_("Not permitted for DocType: {0}").format(doctype))

    meta = frappe.get_meta(doctype)
    allowed, preferred = _allowed_fieldnames(meta)

    status_field = ""
    for candidate in ("status", "workflow_state"):
        if candidate in allowed:
            status_field = candidate
            break

    return {
        "doctype": doctype,
        "label": meta.get("title") or doctype,
        "title_field": meta.title_field or "name",
        "image_field": (meta.image_field or "").strip(),
        "status_field": status_field,
        "default_fields": preferred[:8],
    }


@frappe.whitelist(allow_guest=False)
def get_doctype_list(
    doctype: str,
    filters=None,
    fields=None,
    order_by: str | None = None,
    limit_start: int = 0,
    limit_page_length: int = 20,
    search: str | None = None,
):
    _ensure_system_user()
    doctype = (doctype or "").strip()
    if not doctype:
        frappe.throw(_("doctype is required"))
    if doctype in DISALLOWED_DOCTYPES:
        frappe.throw(_("DocType is not allowed in panel content engine: {0}").format(doctype))
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Invalid DocType: {0}").format(doctype))
    if not frappe.has_permission(doctype=doctype, ptype="read"):
        frappe.throw(_("Not permitted for DocType: {0}").format(doctype))

    meta = frappe.get_meta(doctype)
    requested_fields = _parse_json(fields, [])
    safe_fields = _sanitize_fields(meta, requested_fields)

    requested_filters = _parse_json(filters, [])
    safe_filters = _sanitize_filters(doctype, requested_filters, meta)

    search_value = (search or "").strip()
    title_field = (meta.title_field or "").strip()
    if search_value:
        pattern = f"%{search_value}%"
        if title_field and title_field in safe_fields:
            safe_filters.append([doctype, title_field, "like", pattern])
        else:
            safe_filters.append([doctype, "name", "like", pattern])

    safe_order = _safe_order_by(order_by or "", set(safe_fields))
    page_len = min(max(cint(limit_page_length or 20), 5), 100)
    start = max(cint(limit_start or 0), 0)

    rows = frappe.get_all(
        doctype,
        fields=safe_fields,
        filters=safe_filters,
        order_by=safe_order,
        start=start,
        limit_page_length=page_len,
    )
    total_count = cint(frappe.db.count(doctype, filters=safe_filters) or 0)

    return {
        "doctype": doctype,
        "columns": _column_payload(meta, safe_fields),
        "rows": rows,
        "total_count": total_count,
        "limit_start": start,
        "limit_page_length": page_len,
        "has_more": (start + len(rows)) < total_count,
    }


@frappe.whitelist(allow_guest=False)
def get_doctype_doc(doctype: str, name: str):
    _ensure_system_user()
    doctype = (doctype or "").strip()
    name = (name or "").strip()
    if not doctype or not name:
        frappe.throw(_("doctype and name are required"))
    if doctype in DISALLOWED_DOCTYPES:
        frappe.throw(_("DocType is not allowed in panel content engine: {0}").format(doctype))
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Invalid DocType: {0}").format(doctype))
    if not frappe.has_permission(doctype=doctype, ptype="read"):
        frappe.throw(_("Not permitted for DocType: {0}").format(doctype))
    if not frappe.db.exists(doctype, name):
        frappe.throw(_("Document not found: {0}/{1}").format(doctype, name))

    doc = frappe.get_doc(doctype, name)
    if not doc.has_permission("read"):
        frappe.throw(_("Not permitted to read this document"))

    meta = frappe.get_meta(doctype)
    form_fields = _safe_form_fields(meta)
    values = {}
    for f in form_fields:
        fieldname = f["fieldname"]
        values[fieldname] = doc.get(fieldname)

    # Safety: keep submittable transactional docs read-only in panel form.
    is_submittable = cint(meta.is_submittable or 0) == 1
    can_write = (doc.has_permission("write") and not is_submittable)

    return {
        "doctype": doctype,
        "name": doc.name,
        "title": doc.get(meta.title_field) if meta.title_field else doc.name,
        "title_field": meta.title_field or "name",
        "fields": form_fields,
        "values": values,
        "docstatus": cint(doc.docstatus or 0),
        "can_write": 1 if can_write else 0,
        "is_submittable": 1 if is_submittable else 0,
    }


@frappe.whitelist(allow_guest=False)
def save_doctype_doc(doctype: str, name: str, values=None):
    _ensure_system_user()
    doctype = (doctype or "").strip()
    name = (name or "").strip()
    if not doctype or not name:
        frappe.throw(_("doctype and name are required"))
    if doctype in DISALLOWED_DOCTYPES:
        frappe.throw(_("DocType is not allowed in panel content engine: {0}").format(doctype))
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Invalid DocType: {0}").format(doctype))
    if not frappe.has_permission(doctype=doctype, ptype="write"):
        frappe.throw(_("Not permitted to write DocType: {0}").format(doctype))
    if not frappe.db.exists(doctype, name):
        frappe.throw(_("Document not found: {0}/{1}").format(doctype, name))

    doc = frappe.get_doc(doctype, name)
    if not doc.has_permission("write"):
        frappe.throw(_("Not permitted to write this document"))

    meta = frappe.get_meta(doctype)
    if cint(meta.is_submittable or 0) == 1:
        frappe.throw(_("In-panel editing is disabled for submittable DocTypes like {0}. Open in Desk for controlled actions.").format(doctype))
    updates = _sanitize_form_values(values, meta)
    if not updates:
        return {"ok": 1, "doctype": doctype, "name": name, "updated_fields": [], "modified": str(doc.modified)}

    for fieldname, value in updates.items():
        doc.set(fieldname, value)

    doc.save(ignore_permissions=False)
    frappe.db.commit()
    return {
        "ok": 1,
        "doctype": doctype,
        "name": doc.name,
        "updated_fields": sorted(updates.keys()),
        "modified": str(doc.modified),
    }

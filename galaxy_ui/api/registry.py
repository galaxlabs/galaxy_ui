from __future__ import annotations

import json
import re

import frappe
from frappe import _
from frappe.utils import cint


ALLOWED_OPERATORS = {"=", "!=", "<", "<=", ">", ">=", "like", "in", "not in", "between"}


def _ensure_system_user() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Login required"))
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw(_("Galaxy UI registry is available to System Users only"))


def _parse_json(value, default):
    if value in (None, "", []):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


def _load_registry(key: str):
    if not key:
        frappe.throw(_("key is required"))
    doc = frappe.get_doc("UI API Registry", key)
    if not cint(doc.enabled):
        frappe.throw(_("Registry key is disabled: {0}").format(key))
    return doc


def _current_user_roles() -> set[str]:
    return set(frappe.get_roles(frappe.session.user) or [])


def _check_registry_permission(doc) -> None:
    allowed_roles = _parse_json(doc.allowed_roles_json, [])
    if allowed_roles:
        user_roles = _current_user_roles()
        if not any(role in user_roles for role in allowed_roles):
            frappe.throw(_("Not permitted for registry key: {0}").format(doc.key))


def _safe_fields(doctype: str, requested_fields: list[str], allowed_fields: list[str]) -> list[str]:
    meta = frappe.get_meta(doctype)
    valid = {df.fieldname for df in meta.fields}
    valid.update({"name", "owner", "creation", "modified", "docstatus"})

    allowed = [f for f in (allowed_fields or []) if f in valid]
    if not allowed:
        allowed = ["name", "modified"]

    picked = [f for f in (requested_fields or []) if f in allowed]
    if not picked:
        picked = allowed[:6]

    if "name" not in picked:
        picked.insert(0, "name")

    return picked[:20]


def _safe_order_by(order_by: str, allowed_order_by: list[str], default: str = "modified desc") -> str:
    cleaned = (order_by or "").strip()
    if cleaned and cleaned in (allowed_order_by or []):
        return cleaned

    if default in (allowed_order_by or []):
        return default

    if allowed_order_by:
        return allowed_order_by[0]

    if re.fullmatch(r"[a-zA-Z0-9_`,.\s]+", default):
        return default

    return "modified desc"


def _sanitize_filters(doctype: str, raw_filters, allowed_filter_fields: list[str]) -> list:
    if not raw_filters:
        return []

    out = []
    allowed = set(allowed_filter_fields or [])

    if isinstance(raw_filters, dict):
        for fieldname, value in raw_filters.items():
            if fieldname not in allowed:
                continue
            out.append([doctype, fieldname, "=", value])
        return out

    if isinstance(raw_filters, list):
        for cond in raw_filters:
            if not isinstance(cond, list):
                continue

            if len(cond) == 3:
                fieldname, op, value = cond
                dt = doctype
            elif len(cond) == 4:
                dt, fieldname, op, value = cond
            else:
                continue

            if dt != doctype:
                continue

            op_norm = str(op or "").strip().lower()
            if op_norm not in ALLOWED_OPERATORS:
                continue
            if fieldname not in allowed:
                continue

            out.append([doctype, fieldname, op_norm, value])

    return out


def _apply_scope_filters(doc, target_doctype: str, filters: list) -> list:
    scoped = list(filters or [])

    if cint(doc.allow_owner_only):
        scoped.append([target_doctype, "owner", "=", frappe.session.user])

    company_scope_field = (doc.company_scope_field or "").strip()
    if company_scope_field:
        default_company = frappe.defaults.get_user_default("Company")
        if default_company:
            scoped.append([target_doctype, company_scope_field, "=", default_company])

    return scoped


def _registry_to_config(doc) -> dict:
    return {
        "key": doc.key,
        "title": doc.title,
        "source_type": doc.source_type,
        "doctype": doc.source_doctype,
        "report": doc.report,
        "allow_list": cint(doc.allow_list or 0),
        "allow_get": cint(doc.allow_get or 0),
        "allowed_fields": _parse_json(doc.allowed_fields_json, []),
        "filters_allowed": _parse_json(doc.filters_allowed_json, []),
        "order_by_allowed": _parse_json(doc.order_by_allowed_json, []),
        "limit_rules": _parse_json(doc.limit_rules_json, {}),
    }


def _doc_to_subset(document, fields: list[str]) -> dict:
    out = {}
    for field in fields:
        out[field] = document.get(field)
    return out


def _response_envelope(key: str, mode: str, result: dict) -> dict:
    payload = {"ok": 1, "error": None, "key": key, "mode": mode, "result": result}
    # Backward-compatible top-level mirror for early clients.
    payload.update(result)
    return payload


def _ensure_registry_manager() -> None:
    _ensure_system_user()
    if "System Manager" not in _current_user_roles():
        frappe.throw(_("Only System Manager can publish or test API registry keys"))


@frappe.whitelist(allow_guest=False)
def call(key: str, params=None):
    _ensure_system_user()
    doc = _load_registry(key)
    _check_registry_permission(doc)

    cfg = _registry_to_config(doc)
    payload = _parse_json(params, {})
    mode = (payload.get("mode") or "list").strip().lower()

    if cfg["source_type"] != "Doctype":
        frappe.throw(_("Only source_type=Doctype is enabled in MVP"))

    dt = cfg["doctype"]
    if not frappe.db.exists("DocType", dt):
        frappe.throw(_("Invalid DocType in registry: {0}").format(dt))
    if not frappe.has_permission(doctype=dt, ptype="read"):
        frappe.throw(_("Not permitted for DocType: {0}").format(dt))

    requested_fields = payload.get("fields") if isinstance(payload.get("fields"), list) else []
    fields = _safe_fields(dt, requested_fields, cfg["allowed_fields"])

    if mode == "list":
        if not cfg["allow_list"]:
            frappe.throw(_("LIST not allowed for key: {0}").format(key))

        filters = _sanitize_filters(dt, payload.get("filters"), cfg["filters_allowed"])
        filters = _apply_scope_filters(doc, dt, filters)

        limit_rules = cfg["limit_rules"] if isinstance(cfg["limit_rules"], dict) else {}
        default_page_length = cint(limit_rules.get("default_page_length") or 20)
        max_page_length = cint(limit_rules.get("max_page_length") or 100)
        page_length = cint(payload.get("page_length") or default_page_length or 20)
        page_length = min(max(page_length, 1), max(max_page_length, 1))
        start = max(cint(payload.get("start") or 0), 0)

        order_by = _safe_order_by(payload.get("order_by") or "", cfg["order_by_allowed"], default="modified desc")

        rows = frappe.get_all(
            dt,
            fields=fields,
            filters=filters,
            order_by=order_by,
            start=start,
            limit_page_length=page_length,
        )

        total = None
        try:
            total = cint(frappe.db.count(dt, filters=filters))
        except Exception:
            total = None

        result = {
            "key": key,
            "mode": "list",
            "doctype": dt,
            "fields": fields,
            "rows": rows,
            "start": start,
            "page_length": page_length,
            "total": total,
            "has_more": len(rows) == page_length if total is None else (start + len(rows) < total),
        }
        return _response_envelope(key, "list", result)

    if mode == "get":
        if not cfg["allow_get"]:
            frappe.throw(_("GET not allowed for key: {0}").format(key))

        name = (payload.get("name") or "").strip()
        if not name:
            frappe.throw(_("params.name is required for mode=get"))

        if not frappe.db.exists(dt, name):
            frappe.throw(_("Document not found: {0}").format(name))

        record = frappe.get_doc(dt, name)
        if not record.has_permission("read"):
            frappe.throw(_("Not permitted to read document: {0}").format(name))

        if cint(doc.allow_owner_only) and record.get("owner") != frappe.session.user:
            frappe.throw(_("Owner-only access denied"))

        company_scope_field = (doc.company_scope_field or "").strip()
        if company_scope_field:
            default_company = frappe.defaults.get_user_default("Company")
            if default_company and record.get(company_scope_field) != default_company:
                frappe.throw(_("Company scope access denied"))

        result = {
            "key": key,
            "mode": "get",
            "doctype": dt,
            "name": name,
            "doc": _doc_to_subset(record, fields),
        }
        return _response_envelope(key, "get", result)

    frappe.throw(_("Unsupported mode: {0}").format(mode))


def _to_pascal(value: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", value or "")
    return "".join([p[:1].upper() + p[1:] for p in parts if p]) or "Registry"


def _fieldtype_to_ts(fieldtype: str) -> str:
    ft = (fieldtype or "").strip()
    if ft in {"Int", "Float", "Currency", "Percent", "Rating", "Duration"}:
        return "number"
    if ft in {"Check"}:
        return "0 | 1"
    if ft in {"Date", "Datetime", "Time"}:
        return "string"
    if ft in {"JSON", "Code", "Text", "Small Text", "Long Text", "Data", "Link", "Select", "Dynamic Link"}:
        return "string"
    return "string"


def _emit_ts_for_registry(doc) -> str:
    cfg = _registry_to_config(doc)
    if cfg["source_type"] != "Doctype":
        return f"// {doc.key}: source_type {cfg['source_type']} is not emitted in MVP"

    dt = cfg["doctype"]
    if not frappe.db.exists("DocType", dt):
        return f"// {doc.key}: invalid doctype {dt}"

    meta = frappe.get_meta(dt)
    field_types = {df.fieldname: _fieldtype_to_ts(df.fieldtype) for df in meta.fields}
    field_types.update({"name": "string", "owner": "string", "creation": "string", "modified": "string", "docstatus": "0 | 1 | 2"})

    fields = cfg["allowed_fields"] or ["name", "modified"]
    safe_fields = [f for f in fields if f in field_types]
    if "name" not in safe_fields:
        safe_fields.insert(0, "name")

    pascal = _to_pascal(doc.key)
    lines = []
    lines.append(f"export interface {pascal}Row {{")
    for f in safe_fields:
        lines.append(f"  {f}?: {field_types.get(f, 'string')};")
    lines.append("}")
    lines.append("")
    lines.append(f"export interface {pascal}ListParams {{")
    lines.append("  mode?: \"list\";")
    lines.append("  fields?: string[];")
    lines.append("  filters?: Record<string, unknown> | unknown[];")
    lines.append("  order_by?: string;")
    lines.append("  start?: number;")
    lines.append("  page_length?: number;")
    lines.append("}")
    lines.append("")
    lines.append(f"export interface {pascal}GetParams {{")
    lines.append("  mode: \"get\";")
    lines.append("  name: string;")
    lines.append("  fields?: string[];")
    lines.append("}")
    lines.append("")
    lines.append(f"export interface {pascal}ListResponse {{")
    lines.append("  key: string;")
    lines.append("  mode: \"list\";")
    lines.append("  rows: Array<" + pascal + "Row>;")
    lines.append("  total?: number | null;")
    lines.append("  has_more: boolean;")
    lines.append("}")
    lines.append("")
    lines.append(f"export interface {pascal}GetResponse {{")
    lines.append("  key: string;")
    lines.append("  mode: \"get\";")
    lines.append("  doc: " + pascal + "Row;")
    lines.append("}")
    return "\n".join(lines)


@frappe.whitelist(allow_guest=False)
def types(app_id: str | None = None, key: str | None = None):
    _ensure_system_user()

    filters = {"enabled": 1}
    if key:
        filters["name"] = key
    if app_id:
        filters["target_app"] = app_id

    names = frappe.get_all("UI API Registry", filters=filters, pluck="name", order_by="modified desc", limit_page_length=500)
    docs = [frappe.get_doc("UI API Registry", name) for name in names]

    items = []
    for doc in docs:
        ts = _emit_ts_for_registry(doc)
        items.append({"key": doc.key, "title": doc.title, "typescript": ts})

    combined = "\n\n".join([i["typescript"] for i in items if i.get("typescript")])
    return {
        "generated_at": frappe.utils.now_datetime().isoformat(),
        "count": len(items),
        "items": items,
        "typescript": combined,
    }


@frappe.whitelist(allow_guest=False)
def publish_key(key: str, enabled: int = 1):
    _ensure_registry_manager()
    doc = frappe.get_doc("UI API Registry", key)
    doc.enabled = cint(enabled or 0)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"ok": 1, "key": doc.key, "enabled": cint(doc.enabled or 0)}


@frappe.whitelist(allow_guest=False)
def test_call(key: str, params=None):
    _ensure_registry_manager()
    return call(key=key, params=params)

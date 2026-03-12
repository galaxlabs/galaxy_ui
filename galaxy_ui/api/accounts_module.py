from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _
from frappe.utils import cint, flt


ACCOUNTS_DOCTYPE_CANDIDATES = [
    "Account",
    "GL Entry",
    "Journal Entry",
    "Payment Entry",
    "Payment Ledger Entry",
    "Sales Invoice",
    "Purchase Invoice",
    "Sales Invoice Payment",
    "Mode of Payment",
    "Cost Center",
    "Bank Account",
    "Fiscal Year",
    "Payment Reconciliation",
]

SAFE_LIST_FIELDS = {
    "name",
    "owner",
    "creation",
    "modified",
    "modified_by",
    "docstatus",
    "company",
    "posting_date",
    "account",
    "party_type",
    "party",
    "debit",
    "credit",
    "debit_in_account_currency",
    "credit_in_account_currency",
    "account_currency",
    "voucher_type",
    "voucher_no",
    "against_voucher_type",
    "against_voucher",
    "cost_center",
    "remarks",
    "grand_total",
    "base_grand_total",
    "outstanding_amount",
    "paid_amount",
    "status",
    "posting_time",
    "due_date",
    "currency",
    "naming_series",
}


def _ensure_system_user() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Login required"))
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw(_("Accounts module is available to System Users only"))


def _json(value: Any, default: Any):
    if value in (None, "", []):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        parsed = json.loads(value)
    except Exception:
        return default
    return parsed


def _has_dt(doctype: str) -> bool:
    return bool(doctype and frappe.db.exists("DocType", doctype))


def _is_allowed_accounts_doctype(doctype: str) -> bool:
    if doctype in ACCOUNTS_DOCTYPE_CANDIDATES and _has_dt(doctype):
        return True
    if not _has_dt(doctype):
        return False
    module_name = frappe.db.get_value("DocType", doctype, "module")
    if str(module_name or "").strip().lower() == "accounts":
        return True
    return False


def _validate_doctype(doctype: str) -> str:
    clean = str(doctype or "").strip()
    if not clean:
        frappe.throw(_("doctype is required"))
    if not _is_allowed_accounts_doctype(clean):
        frappe.throw(_("DocType is not allowed for Accounts module: {0}").format(clean))
    return clean


def _get_permissions(doctype: str) -> dict[str, int]:
    return {
        "read": cint(frappe.has_permission(doctype=doctype, ptype="read")),
        "create": cint(frappe.has_permission(doctype=doctype, ptype="create")),
        "write": cint(frappe.has_permission(doctype=doctype, ptype="write")),
        "delete": cint(frappe.has_permission(doctype=doctype, ptype="delete")),
        "print": cint(frappe.has_permission(doctype=doctype, ptype="print")),
    }


def _default_fields_for_doctype(doctype: str) -> list[str]:
    meta = frappe.get_meta(doctype)
    fields = ["name", "modified"]
    for candidate in ("posting_date", "company", "status", "docstatus"):
        if meta.has_field(candidate):
            fields.append(candidate)
    return fields


def _safe_fields(doctype: str, requested: Any) -> list[str]:
    if not requested:
        return _default_fields_for_doctype(doctype)
    parsed = _json(requested, [])
    if not isinstance(parsed, list):
        return _default_fields_for_doctype(doctype)
    clean = []
    for field in parsed:
        f = str(field or "").strip()
        if not f:
            continue
        if f in SAFE_LIST_FIELDS or f == "name":
            clean.append(f)
    return clean or _default_fields_for_doctype(doctype)


@frappe.whitelist(allow_guest=False)
def get_accounts_doctypes():
    _ensure_system_user()
    results = []
    for doctype in ACCOUNTS_DOCTYPE_CANDIDATES:
        if not _has_dt(doctype):
            continue
        perms = _get_permissions(doctype)
        if not perms["read"]:
            continue
        meta = frappe.get_meta(doctype)
        fields = [
            {"fieldname": f.fieldname, "label": f.label, "fieldtype": f.fieldtype, "reqd": cint(f.reqd or 0)}
            for f in meta.fields
            if f.fieldtype in ("Data", "Select", "Link", "Date", "Datetime", "Currency", "Float", "Int", "Small Text", "Text")
            and not f.hidden
            and not f.read_only
        ][:30]
        results.append(
            {
                "doctype": doctype,
                "label": meta.name,
                "permissions": perms,
                "default_fields": _default_fields_for_doctype(doctype),
                "editable_fields": fields,
            }
        )
    return {"doctypes": results}


@frappe.whitelist(allow_guest=False)
def accounts_list(
    doctype: str,
    fields: str | list[str] | None = None,
    filters: str | list | dict | None = None,
    order_by: str | None = None,
    start: int | None = 0,
    page_length: int | None = 20,
):
    _ensure_system_user()
    dt = _validate_doctype(doctype)
    if not frappe.has_permission(doctype=dt, ptype="read"):
        frappe.throw(_("No read permission for {0}").format(dt))

    resolved_filters = _json(filters, {})
    if not isinstance(resolved_filters, (list, dict)):
        resolved_filters = {}

    list_fields = _safe_fields(dt, fields)
    sort_order = (order_by or "modified desc").strip()
    page = max(1, min(cint(page_length or 20), 200))
    row_start = max(0, cint(start or 0))

    rows = frappe.get_all(
        dt,
        fields=list_fields,
        filters=resolved_filters,
        order_by=sort_order,
        start=row_start,
        page_length=page,
    )
    total = cint(frappe.db.count(dt, filters=resolved_filters) or 0)
    return {"doctype": dt, "fields": list_fields, "rows": rows, "total": total, "start": row_start, "page_length": page}


@frappe.whitelist(allow_guest=False)
def accounts_get(doctype: str, name: str):
    _ensure_system_user()
    dt = _validate_doctype(doctype)
    if not frappe.has_permission(doctype=dt, ptype="read"):
        frappe.throw(_("No read permission for {0}").format(dt))
    doc = frappe.get_doc(dt, name)
    if not doc.has_permission("read"):
        frappe.throw(_("No read permission for {0} {1}").format(dt, name))
    return {"doc": doc.as_dict()}


@frappe.whitelist(allow_guest=False)
def accounts_save(doctype: str, doc: str | dict):
    _ensure_system_user()
    dt = _validate_doctype(doctype)
    payload = _json(doc, {})
    if not isinstance(payload, dict):
        frappe.throw(_("doc must be a JSON object"))

    payload["doctype"] = dt
    docname = str(payload.get("name") or "").strip()

    if docname and frappe.db.exists(dt, docname):
        if not frappe.has_permission(doctype=dt, ptype="write"):
            frappe.throw(_("No write permission for {0}").format(dt))
        existing = frappe.get_doc(dt, docname)
        if not existing.has_permission("write"):
            frappe.throw(_("No write permission for {0} {1}").format(dt, docname))
        for key, value in payload.items():
            if key in ("doctype", "name"):
                continue
            existing.set(key, value)
        existing.save()
        return {"name": existing.name, "doctype": dt, "action": "updated"}

    if not frappe.has_permission(doctype=dt, ptype="create"):
        frappe.throw(_("No create permission for {0}").format(dt))
    new_doc = frappe.get_doc(payload)
    new_doc.insert()
    return {"name": new_doc.name, "doctype": dt, "action": "created"}


@frappe.whitelist(allow_guest=False)
def accounts_delete(doctype: str, name: str):
    _ensure_system_user()
    dt = _validate_doctype(doctype)
    if not frappe.has_permission(doctype=dt, ptype="delete"):
        frappe.throw(_("No delete permission for {0}").format(dt))
    doc = frappe.get_doc(dt, name)
    if not doc.has_permission("delete"):
        frappe.throw(_("No delete permission for {0} {1}").format(dt, name))
    frappe.delete_doc(dt, name, ignore_permissions=False, force=0)
    return {"ok": 1, "doctype": dt, "name": name}


@frappe.whitelist(allow_guest=False)
def accounts_dashboard_report(company: str | None = None, from_date: str | None = None, to_date: str | None = None):
    _ensure_system_user()

    filters = ["docstatus = 1"]
    values: dict[str, Any] = {}
    if company:
        filters.append("company = %(company)s")
        values["company"] = company
    if from_date:
        filters.append("posting_date >= %(from_date)s")
        values["from_date"] = from_date
    if to_date:
        filters.append("posting_date <= %(to_date)s")
        values["to_date"] = to_date
    where = " AND ".join(filters)

    income_rows = frappe.db.sql(
        f"""
        SELECT DATE_FORMAT(posting_date, '%%Y-%%m') AS month_key, SUM(base_grand_total) AS amount
        FROM `tabSales Invoice`
        WHERE {where}
        GROUP BY DATE_FORMAT(posting_date, '%%Y-%%m')
        ORDER BY month_key ASC
        """,
        values=values,
        as_dict=True,
    )

    expense_rows = frappe.db.sql(
        f"""
        SELECT DATE_FORMAT(posting_date, '%%Y-%%m') AS month_key, SUM(base_grand_total) AS amount
        FROM `tabPurchase Invoice`
        WHERE {where}
        GROUP BY DATE_FORMAT(posting_date, '%%Y-%%m')
        ORDER BY month_key ASC
        """,
        values=values,
        as_dict=True,
    )

    months = sorted({r.month_key for r in income_rows}.union({r.month_key for r in expense_rows}))
    income_map = {r.month_key: flt(r.amount) for r in income_rows}
    expense_map = {r.month_key: flt(r.amount) for r in expense_rows}
    income = [income_map.get(m, 0.0) for m in months]
    expense = [expense_map.get(m, 0.0) for m in months]
    profit = [round(income[i] - expense[i], 2) for i in range(len(months))]

    totals = {
        "income": round(sum(income), 2),
        "expense": round(sum(expense), 2),
        "profit": round(sum(profit), 2),
    }

    return {
        "months": months,
        "series": [
            {"name": "Income", "data": income, "color": "#16a34a"},
            {"name": "Expense", "data": expense, "color": "#dc2626"},
            {"name": "Profit", "data": profit, "color": "#2563eb"},
        ],
        "totals": totals,
    }


@frappe.whitelist(allow_guest=False)
def accounts_print_formats(doctype: str):
    _ensure_system_user()
    dt = _validate_doctype(doctype)
    if not frappe.has_permission(doctype=dt, ptype="print"):
        frappe.throw(_("No print permission for {0}").format(dt))
    rows = frappe.get_all(
        "Print Format",
        filters={"doc_type": dt},
        fields=["name", "doc_type", "standard", "disabled", "print_format_type", "modified"],
        order_by="modified desc",
    )
    return {"doctype": dt, "print_formats": rows}


@frappe.whitelist(allow_guest=False)
def save_accounts_print_format(
    doctype: str,
    name: str | None = None,
    html: str | None = None,
    css: str | None = None,
    print_format_type: str | None = "Jinja",
):
    _ensure_system_user()
    dt = _validate_doctype(doctype)
    if frappe.session.user != "Administrator" and not frappe.has_permission("Print Format", "write"):
        frappe.throw(_("Insufficient permission to manage Print Formats"))

    format_name = (name or "").strip()
    if format_name and frappe.db.exists("Print Format", format_name):
        doc = frappe.get_doc("Print Format", format_name)
        if doc.doc_type != dt:
            frappe.throw(_("Print Format {0} does not belong to {1}").format(format_name, dt))
        doc.html = html or ""
        doc.css = css or ""
        doc.print_format_type = print_format_type or "Jinja"
        doc.save()
        return {"name": doc.name, "doctype": dt, "action": "updated"}

    new_doc = frappe.get_doc(
        {
            "doctype": "Print Format",
            "doc_type": dt,
            "name": format_name or None,
            "html": html or "",
            "css": css or "",
            "print_format_type": print_format_type or "Jinja",
            "disabled": 0,
        }
    )
    new_doc.insert()
    return {"name": new_doc.name, "doctype": dt, "action": "created"}

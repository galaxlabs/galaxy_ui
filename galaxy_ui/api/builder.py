from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint


def _ensure_system_user() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Login required"))
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw(_("Galaxy UI Builder is available to System Users only"))


def _ensure_manager() -> None:
    _ensure_system_user()
    if "System Manager" not in set(frappe.get_roles(frappe.session.user) or []):
        frappe.throw(_("Only System Manager can save or publish templates"))


def _parse_json(raw, default):
    if raw in (None, "", []):
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        parsed = json.loads(raw)
    except Exception:
        return default
    return parsed if isinstance(parsed, type(default)) else default


@frappe.whitelist(allow_guest=False)
def list_templates(template_type: str | None = None):
    _ensure_system_user()
    filters = {"enabled": 1}
    if template_type:
        filters["template_type"] = template_type.strip().lower()

    return frappe.get_all(
        "UI View Template",
        fields=["name", "title", "template_type", "source_doctype", "is_published", "generated_route", "modified"],
        filters=filters,
        order_by="is_published desc, modified desc",
        limit_page_length=500,
    )


@frappe.whitelist(allow_guest=False)
def get_template(name: str):
    _ensure_system_user()
    if not name:
        frappe.throw(_("name is required"))
    if not frappe.db.exists("UI View Template", name):
        frappe.throw(_("UI View Template not found: {0}").format(name))

    doc = frappe.get_doc("UI View Template", name)
    return {
        "name": doc.name,
        "title": doc.title,
        "template_type": doc.template_type,
        "source_doctype": doc.source_doctype,
        "target_section": doc.target_section,
        "is_published": cint(doc.is_published or 0),
        "config": _parse_json(doc.config_json, {}),
        "generated_route": doc.generated_route,
    }


@frappe.whitelist(allow_guest=False)
def generate_from_doctype(doctype: str, template_type: str = "list"):
    _ensure_system_user()
    if not doctype or not frappe.db.exists("DocType", doctype):
        frappe.throw(_("Invalid doctype"))

    tt = (template_type or "list").strip().lower()
    meta = frappe.get_meta(doctype)

    if tt == "dashboard":
        config = {
            "title": f"{doctype} Dashboard",
            "sections": [
                {
                    "label": "Overview",
                    "widgets": [
                        {"type": "kpi_count", "label": f"{doctype} Count", "doctype": doctype, "filters": {}},
                        {"type": "link", "label": f"Open {doctype}", "route": f"/app/{frappe.scrub(doctype)}"},
                    ],
                }
            ],
        }
    elif tt == "form":
        field_groups = []
        for df in meta.fields:
            if df.fieldtype in {"Section Break", "Column Break", "Tab Break", "HTML", "Table", "Table MultiSelect"}:
                continue
            field_groups.append({"fieldname": df.fieldname, "label": df.label, "fieldtype": df.fieldtype})
            if len(field_groups) >= 20:
                break
        config = {"doctype": doctype, "field_groups": field_groups}
    else:
        fields = ["name"]
        for df in meta.fields:
            if cint(df.in_list_view or 0):
                fields.append(df.fieldname)
            if len(fields) >= 8:
                break
        for fallback in ("modified", "owner"):
            if fallback not in fields:
                fields.append(fallback)
        config = {"doctype": doctype, "fields": fields[:10], "filters": {}}

    return {"doctype": doctype, "template_type": tt, "config": config}


@frappe.whitelist(allow_guest=False)
def save_template(
    title: str,
    template_type: str,
    source_doctype: str | None = None,
    config_json=None,
    name: str | None = None,
    publish: int = 0,
):
    _ensure_manager()

    if not title:
        frappe.throw(_("title is required"))

    payload = {
        "title": title.strip(),
        "template_type": (template_type or "list").strip().lower(),
        "source_doctype": (source_doctype or "").strip() or None,
        "config_json": frappe.as_json(_parse_json(config_json, {})),
        "enabled": 1,
        "is_published": cint(publish or 0),
    }

    if name:
        if not frappe.db.exists("UI View Template", name):
            frappe.throw(_("UI View Template not found: {0}").format(name))
        doc = frappe.get_doc("UI View Template", name)
        doc.update(payload)
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({"doctype": "UI View Template", **payload})
        doc.insert(ignore_permissions=True)

    out = {"ok": 1, "name": doc.name, "title": doc.title, "template_type": doc.template_type}

    if cint(publish or 0):
        out["publish"] = publish_template(doc.name)

    frappe.db.commit()
    return out


@frappe.whitelist(allow_guest=False)
def publish_template(name: str):
    _ensure_manager()
    if not name:
        frappe.throw(_("name is required"))
    if not frappe.db.exists("UI View Template", name):
        frappe.throw(_("UI View Template not found: {0}").format(name))

    doc = frappe.get_doc("UI View Template", name)
    config = _parse_json(doc.config_json, {})

    if doc.template_type == "dashboard":
        if not frappe.db.exists("DocType", "UI Panel Dashboard"):
            frappe.throw(_("UI Panel Dashboard DocType not found"))

        dash_name = f"tmpl-{frappe.scrub(doc.name)}"
        if frappe.db.exists("UI Panel Dashboard", dash_name):
            dash = frappe.get_doc("UI Panel Dashboard", dash_name)
            dash.title = doc.title
            dash.dashboard_json = frappe.as_json(config)
            dash.save(ignore_permissions=True)
        else:
            dash = frappe.get_doc(
                {
                    "doctype": "UI Panel Dashboard",
                    "name": dash_name,
                    "title": doc.title,
                    "is_default": 0,
                    "dashboard_json": frappe.as_json(config),
                }
            )
            dash.insert(ignore_permissions=True)

    doc.is_published = 1
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "ok": 1,
        "name": doc.name,
        "template_type": doc.template_type,
        "published": 1,
    }

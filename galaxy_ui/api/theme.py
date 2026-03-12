import frappe
from ..core.bundle import bundle_hash, validate_ui_layout_preset
from frappe import _
from frappe.utils import cint


def _require_system_manager() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Login required"))
    user_type = frappe.get_cached_value("User", frappe.session.user, "user_type")
    if user_type != "System User":
        frappe.throw(_("Galaxy UI theme tools are for System Users only"))
    roles = set(frappe.get_roles(frappe.session.user) or [])
    if "System Manager" not in roles:
        frappe.throw(_("Only System Manager can modify Galaxy UI themes"))


def _pick(d: dict, keys: list[str], default=None):
    for k in keys:
        if k in d and d.get(k) not in (None, ""):
            return d.get(k)
    return default


def _as_bool(v) -> int:
    return 1 if str(v).lower() in ("1", "true", "yes", "y", "on") else 0


def _safe_var_name(name: str) -> str:
    n = (name or "").strip()
    if not n:
        return ""
    # allow raw css var name
    if n.startswith("--"):
        return n
    # normalize to --ui-*
    n = n.replace(" ", "-").replace("_", "-").lower()
    return f"--ui-{n}"


def _css_vars_block(selector: str, kv: dict[str, str]) -> str:
    parts = []
    for k, v in kv.items():
        if not k or v in (None, ""):
            continue
        parts.append(f"{k}:{str(v).strip()};")
    return f"{selector}{{{''.join(parts)}}}"


def _get_active_theme_doc() -> dict | None:
    # Try common active flags without assuming exact field names
    for flag_field in ("is_active", "enabled", "active"):
        if frappe.db.has_column("UI Theme", flag_field):
            names = frappe.get_all(
                "UI Theme",
                filters={flag_field: 1},
                pluck="name",
                limit=1,
            )
            if names:
                return frappe.get_doc("UI Theme", names[0]).as_dict()

    # fallback: first theme
    names = frappe.get_all("UI Theme", pluck="name", limit=1)
    if names:
        return frappe.get_doc("UI Theme", names[0]).as_dict()

    return None


def _get_tokens(theme_name: str) -> list[dict]:
    # find link field name in UI Token
    meta = frappe.get_meta("UI Token")
    theme_link_field = None
    for df in meta.fields:
        if df.fieldtype == "Link" and df.options == "UI Theme":
            theme_link_field = df.fieldname
            break

    filters = {}
    if theme_link_field:
        filters[theme_link_field] = theme_name

    return frappe.get_all("UI Token", filters=filters, fields=["*"], limit_page_length=2000)


PANEL_THEME_VARIANTS = [
    {
        "theme_name": "Panel Aura Mint",
        "fields": {
            "mode": "Light",
            "status": "Draft",
            "applies_to": "Both",
            "enable_skin": 1,
            "enable_cards": 1,
            "enable_rules": 1,
            "enable_tailwind": 0,
            "primary_color": "#0f172a",
            "primary_color_dark": "#e5e7eb",
            "accent_color": "#f59e0b",
            "success_color": "#22c55e",
            "danger_color": "#ef4444",
            "warning_color": "#f59e0b",
            "background_color": "#f6f4fb",
            "background_color_dark": "#111827",
            "card_color": "#f8f8fb",
            "panel_color": "#ecebf3",
            "border_color": "#dfdfeb",
            "text_primary": "#111827",
            "text_muted": "#64748b",
            "navbar_bg": "#efe2d3",
            "navbar_text": "#111827",
            "navbar_icon": "#334155",
            "navbar_hover_bg": "#f5eadf",
            "navbar_active_bg": "#ffffff",
            "sidebar_bg": "#f4f1f7",
            "sidebar_text": "#111827",
            "sidebar_icon": "#334155",
            "sidebar_active_bg": "#ffffff",
            "sidebar_hover_bg": "#f5eef8",
            "hover_glow_color": "#f59e0b",
            "hover_glow_strength": "Low",
            "shadow_level": "Soft",
            "density": "Comfortable",
            "radius_base": 14,
            "font_preset": "Poppins",
        },
        "custom_tokens": {
            "--guip-shell-bg": "linear-gradient(120deg, #f9edcf 0%, #efe7f3 55%, #e8ecf9 100%)",
            "--ui-listrow-hover-bg": "rgba(15, 23, 42, 0.06)",
            "--ui-card-shadow": "0 10px 24px rgba(15, 23, 42, 0.08)",
        },
    },
    {
        "theme_name": "Panel Ocean Glass",
        "fields": {
            "mode": "Light",
            "status": "Draft",
            "applies_to": "Both",
            "enable_skin": 1,
            "enable_cards": 1,
            "enable_rules": 1,
            "enable_tailwind": 0,
            "primary_color": "#0c4a6e",
            "primary_color_dark": "#bae6fd",
            "accent_color": "#06b6d4",
            "success_color": "#16a34a",
            "danger_color": "#dc2626",
            "warning_color": "#d97706",
            "background_color": "#f2f7fb",
            "background_color_dark": "#0f172a",
            "card_color": "#ffffff",
            "panel_color": "#e9f1f8",
            "border_color": "#d4e2ee",
            "text_primary": "#0f172a",
            "text_muted": "#64748b",
            "navbar_bg": "#dff0f7",
            "navbar_text": "#0f172a",
            "navbar_icon": "#0c4a6e",
            "navbar_hover_bg": "#eaf6fb",
            "navbar_active_bg": "#ffffff",
            "sidebar_bg": "#eef5fb",
            "sidebar_text": "#0f172a",
            "sidebar_icon": "#0c4a6e",
            "sidebar_active_bg": "#ffffff",
            "sidebar_hover_bg": "#e3f1fa",
            "hover_glow_color": "#06b6d4",
            "hover_glow_strength": "Low",
            "shadow_level": "Soft",
            "density": "Comfortable",
            "radius_base": 12,
            "font_preset": "Inter",
        },
        "custom_tokens": {
            "--guip-shell-bg": "linear-gradient(135deg, #e8f7ff 0%, #f2f8ff 48%, #eef3f8 100%)",
            "--ui-listrow-hover-bg": "rgba(2, 132, 199, 0.09)",
            "--ui-card-shadow": "0 12px 28px rgba(12, 74, 110, 0.10)",
        },
    },
    {
        "theme_name": "Panel Ember Sand",
        "fields": {
            "mode": "Light",
            "status": "Draft",
            "applies_to": "Both",
            "enable_skin": 1,
            "enable_cards": 1,
            "enable_rules": 1,
            "enable_tailwind": 0,
            "primary_color": "#7c2d12",
            "primary_color_dark": "#fed7aa",
            "accent_color": "#ea580c",
            "success_color": "#16a34a",
            "danger_color": "#b91c1c",
            "warning_color": "#ca8a04",
            "background_color": "#fff8ef",
            "background_color_dark": "#111827",
            "card_color": "#fffdf8",
            "panel_color": "#f9f2e8",
            "border_color": "#f1dfca",
            "text_primary": "#292524",
            "text_muted": "#78716c",
            "navbar_bg": "#f7e8d5",
            "navbar_text": "#292524",
            "navbar_icon": "#9a3412",
            "navbar_hover_bg": "#fdf0e1",
            "navbar_active_bg": "#ffffff",
            "sidebar_bg": "#fbf3e8",
            "sidebar_text": "#292524",
            "sidebar_icon": "#9a3412",
            "sidebar_active_bg": "#ffffff",
            "sidebar_hover_bg": "#fff1df",
            "hover_glow_color": "#ea580c",
            "hover_glow_strength": "Med",
            "shadow_level": "Soft",
            "density": "Comfortable",
            "radius_base": 16,
            "font_preset": "Noto Sans",
        },
        "custom_tokens": {
            "--guip-shell-bg": "linear-gradient(140deg, #fff2de 0%, #ffe8d2 38%, #f2e7f2 100%)",
            "--ui-listrow-hover-bg": "rgba(234, 88, 12, 0.11)",
            "--ui-card-shadow": "0 12px 26px rgba(154, 52, 18, 0.10)",
        },
    },
]


def _upsert_custom_token_rows(doc, custom_tokens: dict[str, str]) -> None:
    if not custom_tokens:
        return
    existing = {}
    for row in doc.get("tokens") or []:
        if (row.get("source") or "System") == "Custom":
            existing[row.get("token")] = row

    for token, value in custom_tokens.items():
        token_name = _safe_var_name(token)
        if not token_name or value in (None, ""):
            continue
        row = existing.get(token_name)
        if row:
            row.enabled = 1
            row.type = "other"
            row.light_value = str(value).strip()
            row.dark_value = str(value).strip()
            row.source = "Custom"
        else:
            doc.append(
                "tokens",
                {
                    "enabled": 1,
                    "token": token_name,
                    "type": "other",
                    "light_value": str(value).strip(),
                    "dark_value": str(value).strip(),
                    "source": "Custom",
                },
            )


@frappe.whitelist(allow_guest=False)
def seed_panel_theme_variants(overwrite: int = 0):
    _require_system_manager()
    overwrite = cint(overwrite or 0)
    if not frappe.db.exists("DocType", "UI Theme"):
        frappe.throw(_("UI Theme DocType is missing"))

    summary = []
    for spec in PANEL_THEME_VARIANTS:
        theme_name = spec["theme_name"]
        exists = frappe.db.exists("UI Theme", theme_name)
        if exists and not overwrite:
            summary.append({"theme": theme_name, "action": "skipped", "reason": "already exists"})
            continue

        doc = frappe.get_doc("UI Theme", theme_name) if exists else frappe.new_doc("UI Theme")
        doc.theme_name = theme_name
        for fieldname, value in (spec.get("fields") or {}).items():
            if hasattr(doc, fieldname):
                doc.set(fieldname, value)

        if not exists:
            doc.is_active = 0

        _upsert_custom_token_rows(doc, spec.get("custom_tokens") or {})
        doc.save(ignore_permissions=True)
        summary.append({"theme": theme_name, "action": "updated" if exists else "created"})

    frappe.db.commit()
    return {
        "ok": 1,
        "overwrite": overwrite,
        "items": summary,
        "created": len([x for x in summary if x["action"] == "created"]),
        "updated": len([x for x in summary if x["action"] == "updated"]),
        "skipped": len([x for x in summary if x["action"] == "skipped"]),
    }

@frappe.whitelist()
def get_active_theme_bundle():
    """
    Contract for the client runtime loader.
    Return only data + CSS (no HTML).
    """
    theme = _get_active_theme_doc()

    # Defaults if no theme exists yet
    mode = "auto"
    flags = {"skin": 0, "cards": 0, "rules": 0, "tailwind": 0}
    css_tokens = ""
    layout = None

    if theme:
        # mode field (try multiple possibilities)
        mode = (_pick(theme, ["mode", "theme_mode", "color_mode"], "auto") or "auto").lower()

        # feature flags (try multiple possibilities)
        flags = {
            "skin": _as_bool(_pick(theme, ["enable_skin", "skin_enabled"], 0)),
            "cards": _as_bool(_pick(theme, ["enable_cards", "cards_enabled", "enable_card_view"], 0)),
            "rules": _as_bool(_pick(theme, ["enable_rules", "rules_enabled"], 0)),
            "tailwind": _as_bool(_pick(theme, ["enable_tailwind", "tailwind_enabled"], 0)),
        }

        # Build vars from tokens
        light_vars: dict[str, str] = {}
        dark_vars: dict[str, str] = {}

        tokens = _get_tokens(theme["name"])

        # Guess token fields
        for t in tokens:
            raw_name = _pick(t, ["css_variable", "variable", "token", "name", "key"])
            if not raw_name:
                continue

            var_name = _safe_var_name(raw_name)

            light_val = _pick(t, ["light_value", "light", "value_light", "value"])
            dark_val = _pick(t, ["dark_value", "dark", "value_dark", "value"])

            if light_val is not None and light_val != "":
                light_vars[var_name] = str(light_val).strip()
            if dark_val is not None and dark_val != "":
                dark_vars[var_name] = str(dark_val).strip()

        # If you want a guaranteed --ui-primary, map from common theme fields if missing
        if "--ui-primary" not in light_vars:
            primary = _pick(theme, ["primary", "primary_color", "brand_color"], "")
            if primary:
                light_vars["--ui-primary"] = str(primary).strip()
        if "--ui-primary" not in dark_vars:
            primary_dark = _pick(theme, ["primary_dark", "brand_color_dark"], "") or light_vars.get("--ui-primary", "")
            if primary_dark:
                dark_vars["--ui-primary"] = str(primary_dark).strip()

        css_tokens = _css_vars_block(":root", light_vars) + "\n" + _css_vars_block('html[data-ui-mode="dark"]', dark_vars)

    if theme and theme.get("layout_json"):
        import json
        try:
            layout = json.loads(theme.get("layout_json"))
            validate_ui_layout_preset(layout)
        except Exception:
            # Don't crash loader; just ignore invalid layout_json
            layout = None

    h = bundle_hash(mode, str(flags), css_tokens, str(layout))

    return {
        "mode": mode,
        "flags": flags,
        "css_tokens": css_tokens,
        "hash": h,
        "layout": layout,
    }
    
@frappe.whitelist()
def list_presets():
    """
    Return UI Presets for selector page (card grid).
    Uses the actual fieldnames of our UI Preset DocType.
    """
    if not frappe.db.exists("DocType", "UI Preset"):
        return []

    meta = frappe.get_meta("UI Preset")
    fieldnames = {df.fieldname for df in meta.fields}

    # always try these (if they exist)
    wanted = [
        "name",
        "preset_name",
        "preview_image",
        "short_description",
        "applies_to",
        "is_featured",
        "sort_order",
        "theme_ref",
    ]

    fields = ["name"] + [f for f in wanted if f != "name" and f in fieldnames]

    return frappe.get_all(
        "UI Preset",
        fields=fields,
        order_by="is_featured desc, sort_order asc, modified desc",
        limit_page_length=200,
    )


@frappe.whitelist()
def apply_preset(preset_name: str):
    """
    Activate preset's linked UI Theme.
    Only one theme will be active at a time.
    """
    _require_system_manager()
    if not preset_name:
        frappe.throw("Preset name is required")

    if not frappe.db.exists("UI Preset", preset_name):
        frappe.throw("Preset not found")

    preset = frappe.get_doc("UI Preset", preset_name)

    # detect linked theme field dynamically
    meta = frappe.get_meta("UI Preset")
    theme_link_field = None
    for df in meta.fields:
        if df.fieldtype == "Link" and df.options == "UI Theme":
            theme_link_field = df.fieldname
            break

    if not theme_link_field:
        frappe.throw("UI Preset is not linked to UI Theme")

    theme_name = preset.get(theme_link_field)

    if not theme_name:
        frappe.throw("This preset is not linked to any UI Theme")

    # deactivate all themes
    for flag_field in ("is_active", "enabled", "active"):
        if frappe.db.has_column("UI Theme", flag_field):
            frappe.db.sql(f"update `tabUI Theme` set `{flag_field}` = 0")

    # activate selected theme
    for flag_field in ("is_active", "enabled", "active"):
        if frappe.db.has_column("UI Theme", flag_field):
            frappe.db.set_value("UI Theme", theme_name, flag_field, 1)

    frappe.db.commit()

    return {
        "ok": 1,
        "theme": theme_name,
    }

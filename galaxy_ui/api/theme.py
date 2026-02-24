import frappe
from ..core.bundle import bundle_hash, validate_ui_layout_preset


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

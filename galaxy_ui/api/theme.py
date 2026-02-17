import frappe


FONT_PRESETS = {
    "System Default": 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji","Segoe UI Emoji"',
    "Inter": 'Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial',
    "Poppins": 'Poppins, system-ui, -apple-system, "Segoe UI", Roboto, Arial',
    "Roboto": 'Roboto, system-ui, -apple-system, "Segoe UI", Arial',
    "Noto Sans": '"Noto Sans", system-ui, -apple-system, "Segoe UI", Roboto, Arial',
}

SHADOWS = {
    "None": "none",
    "Soft": "0 6px 18px rgba(15, 23, 42, 0.08)",
    "Medium": "0 10px 28px rgba(15, 23, 42, 0.12)",
    "Strong": "0 16px 40px rgba(15, 23, 42, 0.18)",
}

# Optional density tokens (use later in CSS)
DENSITY = {
    "Compact": {"--pt-density": "compact", "--pt-pad": "8px"},
    "Comfortable": {"--pt-density": "comfortable", "--pt-pad": "12px"},
}


def _norm_mode(s: str) -> str:
    s = (s or "").strip().lower()
    return s if s in ("auto", "light", "dark") else "auto"


def _coalesce(*vals):
    for v in vals:
        if v is None:
            continue
        v = str(v).strip()
        if v:
            return v
    return ""


def _add(line_list, k, v):
    if v:
        line_list.append(f"{k}: {v};")


@frappe.whitelist()
def get_active_theme():
    """
    Returns:
      {
        mode: auto|light|dark,
        css: "..."
      }
    """
    theme = frappe.get_all(
        "Galaxy UI Theme",
        filters={"is_active": 1},
        fields=[
            "name", "mode",

            # Branding
            "primary_color", "accent_color", "success_color", "warning_color", "danger_color",

            # Surface + Text
            "background_color", "card_color", "panel_color", "border_color",
            "text_primary", "text_muted",

            # Style + Typography
            "radius_base", "shadow_level", "density",
            "font_preset", "font_family",

            # Navbar
            "navbar_bg", "navbar_text", "navbar_icon", "navbar_hover_bg", "navbar_active_bg",

            # Sidebar / Workspace
            "sidebar_bg", "sidebar_text", "sidebar_icon", "sidebar_hover_bg", "sidebar_active_bg",

            # Glow
            "hover_glow_color", "hover_glow_strength",
        ],

        order_by="modified desc",
        limit=1,
    )

    if not theme:
        return {"mode": "auto", "css": ""}

    t = theme[0]
    mode = _norm_mode(t.get("mode"))

    # -------------------------
    # 1) Build LIGHT tokens from builder fields
    # -------------------------
    light = []

    # Brand
    _add(light, "--pt-primary", _coalesce(t.get("primary_color"), "#2563eb"))
    _add(light, "--pt-accent", _coalesce(t.get("accent_color"), "#22c55e"))
    _add(light, "--pt-green", _coalesce(t.get("success_color"), "#22c55e"))
    _add(light, "--pt-amber", _coalesce(t.get("warning_color"), "#f59e0b"))
    _add(light, "--pt-red", _coalesce(t.get("danger_color"), "#ef4444"))
    _add(light, "--pt-blue", _coalesce(t.get("primary_color"), "#3b82f6"))
    _add(light, "--pt-gray", "#64748b")

    # Surface
    _add(light, "--pt-bg", _coalesce(t.get("background_color"), "#f7f7fb"))
    _add(light, "--pt-surface-1", _coalesce(t.get("card_color"), "#ffffff"))
    _add(light, "--pt-surface-2", _coalesce(t.get("panel_color"), "#f1f5f9"))
    _add(light, "--pt-border", _coalesce(t.get("border_color"), "rgba(15,23,42,0.12)"))

    # Text
    _add(light, "--pt-text-1", _coalesce(t.get("text_primary"), "#0f172a"))
    _add(light, "--pt-muted", _coalesce(t.get("text_muted"), "#64748b"))
    _add(light, "--pt-text-2", _coalesce(t.get("text_muted"), "#475569"))
    # ---------------------------------
    # Navbar / Sidebar / Icons / Glow
    # ---------------------------------
    _add(light, "--pt-navbar-bg", _coalesce(t.get("navbar_bg"), ""))  # fallback handled by CSS var()
    _add(light, "--pt-navbar-text", _coalesce(t.get("navbar_text"), ""))
    _add(light, "--pt-navbar-hover-bg", _coalesce(t.get("navbar_hover_bg"), ""))
    _add(light, "--pt-navbar-active-bg", _coalesce(t.get("navbar_active_bg"), ""))

    _add(light, "--pt-sidebar-bg", _coalesce(t.get("sidebar_bg"), ""))
    _add(light, "--pt-sidebar-text", _coalesce(t.get("sidebar_text"), ""))
    _add(light, "--pt-sidebar-hover-bg", _coalesce(t.get("sidebar_hover_bg"), ""))
    _add(light, "--pt-sidebar-active-bg", _coalesce(t.get("sidebar_active_bg"), ""))

    # Icon color: prefer explicit sidebar_icon, else navbar_icon, else muted
    _icon = _coalesce(t.get("sidebar_icon"), t.get("navbar_icon"), "")
    _add(light, "--pt-icon", _icon)

    # Glow: prefer hover_glow_color else accent_color
    glow_color = _coalesce(t.get("hover_glow_color"), t.get("accent_color"), "#22c55e")

    strength = (t.get("hover_glow_strength") or "Med").strip()
    alpha = {"Low": 0.18, "Med": 0.25, "High": 0.35}.get(strength, 0.25)

    # If glow_color is hex (#RRGGBB) convert to rgba; otherwise accept as-is
    def _hex_to_rgba(hx: str, a: float) -> str:
        hx = (hx or "").strip()
        if not hx.startswith("#") or len(hx) != 7:
            return hx
        r = int(hx[1:3], 16)
        g = int(hx[3:5], 16)
        b = int(hx[5:7], 16)
        return f"rgba({r},{g},{b},{a})"

    _add(light, "--pt-glow", _hex_to_rgba(glow_color, alpha))


    # Radius / Shadow
    radius = t.get("radius_base") if t.get("radius_base") is not None else 12
    try:
        radius = int(radius)
    except Exception:
        radius = 12
    radius = max(6, min(radius, 20))
    _add(light, "--pt-radius", f"{radius}px")

    shadow_level = (t.get("shadow_level") or "Soft").strip()
    _add(light, "--pt-shadow", SHADOWS.get(shadow_level, SHADOWS["Soft"]))

    # Typography
    preset = (t.get("font_preset") or "System Default").strip()
    font = _coalesce(t.get("font_family"), FONT_PRESETS.get(preset, FONT_PRESETS["System Default"]))
    _add(light, "--pt-font-family", font)

    # Density (optional)
    dens = (t.get("density") or "Comfortable").strip()
    for k, v in DENSITY.get(dens, DENSITY["Comfortable"]).items():
        _add(light, k, v)

    # -------------------------
    # 2) Build DARK tokens
    #    If you later add dark fields, plug them here.
    #    For now, use sensible defaults.
    # -------------------------
    dark = []
    _add(dark, "--pt-bg", "#0b1220")
    _add(dark, "--pt-surface-1", "#0f172a")
    _add(dark, "--pt-surface-2", "#111c33")
    _add(dark, "--pt-text-1", "#e5e7eb")
    _add(dark, "--pt-text-2", "#cbd5e1")
    _add(dark, "--pt-muted", "#94a3b8")
    _add(dark, "--pt-border", "rgba(148,163,184,0.18)")
    _add(dark, "--pt-shadow", "0 10px 28px rgba(0,0,0,0.45)")

    # keep same font/radius/colors in dark unless overridden
    _add(dark, "--pt-font-family", font)
    _add(dark, "--pt-radius", f"{radius}px")
    _add(dark, "--pt-primary", _coalesce(t.get("primary_color"), "#3b82f6"))
    _add(dark, "--pt-accent", _coalesce(t.get("accent_color"), "#22c55e"))
    _add(dark, "--pt-green", _coalesce(t.get("success_color"), "#22c55e"))
    _add(dark, "--pt-amber", _coalesce(t.get("warning_color"), "#f59e0b"))
    _add(dark, "--pt-red", _coalesce(t.get("danger_color"), "#ef4444"))
    _add(dark, "--pt-blue", _coalesce(t.get("primary_color"), "#3b82f6"))
    _add(dark, "--pt-gray", "#94a3b8")

    _add(dark, "--pt-navbar-bg", _coalesce(t.get("navbar_bg"), ""))
    _add(dark, "--pt-navbar-text", _coalesce(t.get("navbar_text"), ""))
    _add(dark, "--pt-navbar-hover-bg", _coalesce(t.get("navbar_hover_bg"), ""))
    _add(dark, "--pt-navbar-active-bg", _coalesce(t.get("navbar_active_bg"), ""))

    _add(dark, "--pt-sidebar-bg", _coalesce(t.get("sidebar_bg"), ""))
    _add(dark, "--pt-sidebar-text", _coalesce(t.get("sidebar_text"), ""))
    _add(dark, "--pt-sidebar-hover-bg", _coalesce(t.get("sidebar_hover_bg"), ""))
    _add(dark, "--pt-sidebar-active-bg", _coalesce(t.get("sidebar_active_bg"), ""))

    _add(dark, "--pt-icon", _icon)
    _add(dark, "--pt-glow", _hex_to_rgba(glow_color, alpha))


    for k, v in DENSITY.get(dens, DENSITY["Comfortable"]).items():
        _add(dark, k, v)

    # -------------------------
    # 3) Advanced override tokens table (optional)
    #    These override both light & dark if user added them.
    # -------------------------
    try:
        tokens = frappe.get_all(
            "Galaxy UI Token",
            filters={"parent": t["name"], "enabled": 1},
            fields=["token", "light_value", "dark_value"],
            order_by="idx asc",
        )
    except Exception:
        tokens = []

    if tokens:
        # use dict so overrides are clean
        light_map = {}
        dark_map = {}

        # load existing
        for line in light:
            k, v = line.split(":", 1)
            light_map[k.strip()] = v.strip().rstrip(";")
        for line in dark:
            k, v = line.split(":", 1)
            dark_map[k.strip()] = v.strip().rstrip(";")

        for row in tokens:
            token = (row.get("token") or "").strip()
            if not token.startswith("--"):
                continue
            lv = (row.get("light_value") or "").strip()
            dv = (row.get("dark_value") or "").strip()
            if lv:
                light_map[token] = lv
            if dv:
                dark_map[token] = dv

        light = [f"{k}: {v};" for k, v in light_map.items()]
        dark = [f"{k}: {v};" for k, v in dark_map.items()]

    css = (
        ":root{\n" + "\n".join(light) + "\n}\n"
        'html[data-pt-mode="dark"]{\n' + "\n".join(dark) + "\n}\n"
    )

    return {"mode": mode, "css": css, "theme": t["name"]}

# galaxy_ui/core/schemas.py
# Central place for JSON schemas used by Galaxy UI runtime bundles and governance.

UI_LAYOUT_PRESET_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://galaxylabs.online/schemas/ui-layout-preset.schema.json",
    "title": "UI Layout Preset",
    "type": "object",
    "additionalProperties": False,
    "required": ["name", "targets", "shell_style", "component_options"],
    "properties": {
        "name": {"type": "string", "minLength": 3, "maxLength": 140},

        "enabled": {"type": "boolean", "default": True},

        "targets": {
            "title": "MultiSelect Targets",
            "type": "array",
            "items": {"type": "string", "enum": ["desk", "panel", "dashboard", "web"]},
            "minItems": 1,
            "uniqueItems": True,
        },

        "route_prefix": {
            "type": "string",
            "minLength": 1,
            "maxLength": 140,
            "pattern": "^/[-a-zA-Z0-9_/]*$",
            "default": "/app/ui-panel",
        },

        "shell_style": {"type": "string", "enum": ["default", "admin", "minimal", "portal"]},

        "toggles": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "sidebar_enabled": {"type": "boolean", "default": True},
                "topbar_enabled": {"type": "boolean", "default": True},
                "footer_enabled": {"type": "boolean", "default": False},
                "breadcrumbs_enabled": {"type": "boolean", "default": True},
            },
            "default": {},
        },

        "default_theme": {
            "type": "string",
            "minLength": 1,
            "maxLength": 140,
            "description": "Link name of UI Theme",
        },

        "default_workspace": {
            "type": "string",
            "minLength": 0,
            "maxLength": 140,
            "description": "Link name of Portal Workspace (optional)",
        },

        "feature_flags": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "skin": {"type": "boolean", "default": True},
                "rules": {"type": "boolean", "default": True},
                "cards": {"type": "boolean", "default": True},
                "tailwind": {"type": "boolean", "default": False},
            },
            "default": {},
        },

        "component_options": {
            "title": "Component option mapping",
            "type": "object",
            "minProperties": 1,
            "additionalProperties": {"type": "string", "minLength": 1, "maxLength": 140},
            "description": "Map component_name -> option_name. Example: {\"card\":\"soft_shadow\"}",
        },

        "effects": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "shadow_level": {"type": "integer", "minimum": 0, "maximum": 6, "default": 2},
                "radius_level": {"type": "integer", "minimum": 0, "maximum": 6, "default": 3},
                "density": {"type": "string", "enum": ["comfortable", "compact", "dense"], "default": "comfortable"},
                "hover_effect": {"type": "string", "enum": ["none", "lift", "glow", "outline"], "default": "lift"},
                "transition_ms": {"type": "integer", "minimum": 0, "maximum": 800, "default": 160},
            },
            "default": {},
        },
    },
}

# Component Options Runtime (B1)

## Purpose

Layout presets can now drive runtime visual variants in `/app/ui_panel` using component options.

Source of truth:
- `UI Layout Preset.component_options_json`

Runtime output:
- CSS vars map
- root classes list
- warnings/debug summary

## JSON Shape (v1)

`component_options_json` supports two formats:

1. Structured map (recommended)

```json
{
  "Sidebar": {
    "variant": "compact",
    "density": "dense",
    "shadow": "soft"
  },
  "Topbar": {
    "variant": "solid"
  },
  "Card": {
    "radius": "md",
    "shadow": "soft"
  },
  "ListRow": {
    "hover": "tint"
  }
}
```

2. Legacy direct map

```json
{
  "card": "soft_shadow",
  "sidebar": "compact_dark"
}
```

## Resolver Behavior

- Unknown components/options do not crash runtime.
- Unknown entries are returned in `warnings` / `unmatched`.
- Matching uses normalized component aliases (`Topbar -> navbar`, `ListRow -> list_row`).
- Resolver is deterministic and does not use eval/dynamic execution.

## Bundle Contract

`galaxy_ui.api.panel.get_panel_bundle` includes:

- `active_layout_preset`
- `resolved_component_runtime`
  - `css_vars`
  - `classes`
  - `warnings`
  - `matched`
  - `unmatched`

## Runtime Apply

UI panel applies runtime via:

- style tag: `#galaxy-ui-component-runtime`
- root selector: `.ui-panel-root`
- class injection on panel root

Runtime vars/classes override base theme tokens only where keys overlap.

## Manual Resolve Endpoint

`galaxy_ui.api.layout.resolve_layout_preset_runtime(preset_name, save_cache=0|1)`

- `save_cache=1` writes:
  - `component_css_vars_json`
  - `component_classes`
  - `last_resolved_on`
- mutation requires `System Manager`.

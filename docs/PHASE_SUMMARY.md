# Galaxy UI Phase Summary (v1)

## Scope Baseline

- Platform: Frappe v15
- App: `galaxy_ui`
- Route policy: only `/app/ui_panel` (core page only)
- Target users: System Users only
- Core Desk untouched (alternative UI only)

## Phase Status

### Phase 1: Panel Shell + Navigation JSON Render

Status: Completed

Delivered:
- `ui_panel` shell (topbar, sidebar, content area)
- Navigation loading from active panel navigation profile
- Dashboard/list placeholders rendered inside panel
- Runtime token/style consumption

### Phase 2: Navigation Builder UI

Status: Completed

Delivered:
- `UI Panel Navigation` profile model
- Save/load active navigation profile
- Resource discovery (DocTypes/Reports/Pages)
- Panel API support for navigation profile management

### Phase 3: Layout Presets + Theme Selection

Status: Completed

Delivered:
- `UI Layout Preset` DocType
- Layout validation/hash generation
- Layout apply flow to selected/active `UI Theme`
- Appearance APIs for layout preset operations

### Phase 4: Bridge Config Hub

Status: Completed

Delivered:
- `UI App Config` DocType with bridge fields
- Bridge endpoints for external apps:
  - app config
  - nav
  - merged runtime bundle

### Phase 5: API Registry (list/get)

Status: Completed

Delivered:
- `UI API Registry` with strict field/filter allowlist
- Generic endpoint `galaxy_ui.api.registry.call`
- Permission/role checks + owner/company scope checks
- Publish/test APIs and form actions
- Standard response envelope

### Phase 6: Multi-layout Presets + Color Scheme Switch

Status: Completed

Delivered:
- In-panel `Appearance` switcher in `/app/ui_panel`
- Theme-only apply fallback when no layout preset exists
- Runtime apply + bundle reload

### Phase 7: Component Options Library

Status: Completed

Delivered:
- `UI Component` and `UI Component Option` DocTypes
- Component option resolver API (vars/classes merge)
- Runtime application of component options in panel shell
- Default component library seeding API

### Phase 8: UI Builder (dashboard/list/form templates)

Status: Completed (MVP)

Delivered:
- `UI View Template` DocType
- Builder APIs:
  - generate template config from DocType metadata
  - save template
  - publish template (dashboard sync)
  - list/get templates
- `Builder` action in `ui_panel` topbar
- Sample template retained for docs: `User List Template`

### Phase B1: Component Options Apply Runtime (Sidebar/Admin Variants)

Status: Completed (v1)

Delivered:
- Canonical runtime resolver in `core/component_runtime.py`
- Layout Preset runtime fields:
  - `component_options_json`
  - `component_css_vars_json` (cache)
  - `component_classes` (cache)
  - `apply_scope` (`UI Panel|Desk|Both`)
  - `last_resolved_on`
- New API: `galaxy_ui.api.layout.resolve_layout_preset_runtime`
- `get_panel_bundle` now returns:
  - `active_layout_preset`
  - `resolved_component_runtime` (`css_vars`, `classes`, `warnings`, debug summary)
- Panel runtime apply uses:
  - style tag `#galaxy-ui-component-runtime`
  - root classes on `.ui-panel-root`
- Backfill patch for existing preset records.

### Phase C1.1: Panel Theme Variant Pack (Color Presets)

Status: Completed (v1)

Delivered:
- New endpoint: `galaxy_ui.api.theme.seed_panel_theme_variants`
- System Manager-only, idempotent creation of panel-ready `UI Theme` variants
- Appearance dialog action: `Seed Theme Variants`
- New token-aware shell background support via `--guip-shell-bg`

## Current Data Model (Active)

- `UI Theme`
- `UI Token`
- `UI Panel Navigation`
- `UI Panel Dashboard`
- `UI Layout Preset`
- `UI App Config`
- `UI API Registry`
- `UI Component`
- `UI Component Option`
- `UI View Template`

## API Matrix

### Theme/Layout
- `galaxy_ui.api.theme.get_active_theme_bundle`
- `galaxy_ui.api.layout.list_layout_presets`
- `galaxy_ui.api.layout.get_layout_preset`
- `galaxy_ui.api.layout.apply_layout_preset`
- `galaxy_ui.api.layout.resolve_layout_preset_runtime`
- `galaxy_ui.api.layout.get_appearance_options`
- `galaxy_ui.api.layout.apply_panel_appearance`

### Panel/Navigation
- `galaxy_ui.api.panel.get_panel_bundle`
- `galaxy_ui.api.panel.get_active_navigation`
- `galaxy_ui.api.panel.list_navigation_profiles`
- `galaxy_ui.api.panel.save_navigation_profile`
- `galaxy_ui.api.panel.get_default_dashboard`
- `galaxy_ui.api.panel.get_dashboard`

### Bridge
- `galaxy_ui.api.bridge.get_ui_app_config`
- `galaxy_ui.api.bridge.get_ui_nav`
- `galaxy_ui.api.bridge.get_ui_bundle`

### Registry
- `galaxy_ui.api.registry.call`
- `galaxy_ui.api.registry.types`
- `galaxy_ui.api.registry.publish_key`
- `galaxy_ui.api.registry.test_call`

### Component Library
- `galaxy_ui.api.component.list_components`
- `galaxy_ui.api.component.list_component_options`
- `galaxy_ui.api.component.resolve_component_options`
- `galaxy_ui.api.component.seed_default_components`

### Builder
- `galaxy_ui.api.builder.list_templates`
- `galaxy_ui.api.builder.get_template`
- `galaxy_ui.api.builder.generate_from_doctype`
- `galaxy_ui.api.builder.save_template`
- `galaxy_ui.api.builder.publish_template`

## Canonical Routes

- Core panel: `/app/ui_panel`
- Core Desk fallback: `/app/home`

Notes:
- `ui-panel` alias intentionally removed from page records.
- Non-core Galaxy UI pages removed; `ui_panel` is the only page entry in module `Galaxy UI`.

## Documentation Example Records

Kept intentionally for docs/demo:
- UI View Template: `User List Template`

## UAT / Screenshot Checklist

### Panel Core
- [ ] Open `/app/ui_panel` with no JS errors
- [ ] Sidebar navigation renders and items open correctly
- [ ] Dashboard widgets and links load

### Appearance
- [ ] `Appearance` dialog opens
- [ ] Theme change applies instantly
- [ ] Layout preset apply works (when presets exist)

### Components
- [ ] `Components` action seeds defaults if missing
- [ ] `component_options_json` in preset resolves without hard failures (warnings allowed)
- [ ] Runtime class/var effects are visible in panel shell (sidebar/card/list variants)

### Registry
- [ ] Registry `list` endpoint respects allowed fields/filters
- [ ] Registry `get` endpoint enforces access checks
- [ ] Publish/unpublish and test actions work from form

### Builder
- [ ] `Builder` dialog generates config from selected DocType
- [ ] Save template creates `UI View Template` record
- [ ] Publish dashboard template syncs `UI Panel Dashboard`

## Operational Notes

- After code updates: run migrate, build app assets, clear site cache.
- Test environment has test runner disabled unless `allow_tests` is enabled.
- For production rollout, keep System Manager ownership on all governance DocTypes.

# Galaxy UI

Production-safe **UI Operating System** for Frappe v15 / ERPNext.

Galaxy UI provides a modern alternative admin panel, no-code UI governance, bridge APIs for external apps, and configurable runtime theming without modifying Frappe core files.

## What This Repo Delivers

- Alternative panel route for system users: `/app/ui_panel`
- Theme + token runtime bundle
- Layout presets and live appearance switching
- JSON-driven panel navigation
- Bridge config hub for external React/Next.js apps
- No-code registry APIs (`list/get`) with allowlists and role checks
- TypeScript type generation for registry endpoints
- Component options library (variant -> css vars/classes)
- Builder templates for dashboard/list/form MVP

## Core Principles

- No core file modification
- Upgrade-safe extension model
- DocType-driven configuration
- Runtime CSS variables and JSON schemas
- Desk remains available (`/app/home`)

## Current Canonical Route

- Panel: `/app/ui_panel`
- Desk: `/app/home`

Notes:
- Route aliases were removed intentionally.
- `ui_panel` is the only Galaxy UI page record in module `Galaxy UI`.

## Phase Coverage

Implemented phases:
1. Panel shell + navigation render
2. Navigation builder backend flow
3. Layout preset management
4. Bridge config hub
5. API registry (list/get) + publish/test
6. Appearance switcher (layout/theme)
7. Component options library + runtime resolver
8. Builder template MVP (dashboard/list/form)

See full phase ledger: [docs/PHASE_SUMMARY.md](docs/PHASE_SUMMARY.md)

## Repository Structure

```text
galaxy_ui/
  api/                        # whitelisted backend APIs (panel, layout, bridge, registry, builder, component)
  core/                       # shared schema/hash/validation helpers
  galaxy_ui/
    doctype/                  # governance/config models
    page/
      ui_panel/               # core panel page (only active page)
  public/
    ui/styles/                # runtime styles
    ui/runtime/               # runtime loaders/helpers
docs/
  APP_BRIEF.md
  GETTING_STARTED.md
  INTEGRATION_SDK.md
  PHASE_SUMMARY.md
  sdk/galaxy-ui-client.ts
```

## Key DocTypes

- `UI Theme`, `UI Token`
- `UI Panel Navigation`
- `UI Panel Dashboard`
- `UI Layout Preset`
- `UI App Config`
- `UI API Registry`
- `UI Component`, `UI Component Option`
- `UI View Template`

## Key API Endpoints

### Panel/Theme/Layout
- `galaxy_ui.api.panel.get_panel_bundle`
- `galaxy_ui.api.theme.get_active_theme_bundle`
- `galaxy_ui.api.layout.get_appearance_options`
- `galaxy_ui.api.layout.apply_panel_appearance`

### Panel Feature Flags
- `get_panel_bundle` now returns `features` for UI gating:
  - `appearance`, `builder`, `components`, `dashboard`, `navigation`, `registry`, `bridge`, `react_dashboard`
- Optional site-level override in `site_config.json`:

```json
{
  "galaxy_ui_features": {
    "builder": 0,
    "components": 1,
    "appearance": 1,
    "dashboard": 1
  }
}
```

### Bridge (External Apps)
- `galaxy_ui.api.bridge.get_ui_app_config`
- `galaxy_ui.api.bridge.get_ui_nav`
- `galaxy_ui.api.bridge.get_ui_bundle`
- `galaxy_ui.api.bridge.get_react_dashboard_runtime`

### Registry + Types
- `galaxy_ui.api.registry.call`
- `galaxy_ui.api.registry.types`
- `galaxy_ui.api.registry.publish_key`
- `galaxy_ui.api.registry.test_call`

### Components + Builder
- `galaxy_ui.api.component.resolve_component_options`
- `galaxy_ui.api.component.seed_default_components`
- `galaxy_ui.api.builder.generate_from_doctype`
- `galaxy_ui.api.builder.save_template`
- `galaxy_ui.api.builder.publish_template`

## Installation

From your bench directory:

```bash
bench get-app <repo_url> --branch develop
bench --site <site> install-app galaxy_ui
bench --site <site> migrate
bench build --app galaxy_ui
bench --site <site> clear-cache
```

## Upgrade / Deploy Steps

When updating this app:

```bash
bench --site <site> migrate
bench build --app galaxy_ui
bench --site <site> clear-cache
```

## First-Time Setup (System Manager)

1. Open `/app/ui_panel`
2. Click **Components** to seed default component library
3. Click **Appearance** to select theme / layout
4. Configure `UI Panel Navigation` and mark active
5. Configure `UI Panel Dashboard` default record
6. Create API keys in `UI API Registry` and test
7. Use **Builder** to generate/save templates (example: `User List Template`)

Detailed onboarding: [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)

## External App Integration (React/Next.js)

- SDK client: [docs/sdk/galaxy-ui-client.ts](docs/sdk/galaxy-ui-client.ts)
- Integration guide: [docs/INTEGRATION_SDK.md](docs/INTEGRATION_SDK.md)
- React dashboard switch + runtime config: [docs/REACT_DASHBOARD.md](docs/REACT_DASHBOARD.md)
- Accounts module phase guide: [docs/ACCOUNTS_MODULE.md](docs/ACCOUNTS_MODULE.md)

## Example Records Kept for Documentation

- `User List Template` (`UI View Template`)

## Troubleshooting Quick Checks

- Blank panel: verify user is System User and route is `/app/ui_panel`
- Missing methods after deploy: run migrate + clear-cache (restart workers if needed)
- Empty sidebar: check active `UI Panel Navigation`
- Appearance errors: ensure at least one active `UI Theme`
- Registry denied: verify `allowed_roles_json` and DocType permissions

## Development Quality

This repo uses `pre-commit` and lint tools.

```bash
cd apps/galaxy_ui
pre-commit install
```

Configured checks include:
- `ruff`
- `eslint`
- `prettier`
- `pyupgrade`

## License

MIT

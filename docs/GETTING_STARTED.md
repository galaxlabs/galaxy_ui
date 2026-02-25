# Galaxy UI Getting Started Guide

## Who this guide is for

This guide is for new System Users and System Managers using `galaxy_ui` on Frappe v15.

## What Galaxy UI is

`galaxy_ui` gives you an alternative admin experience inside Desk without replacing core Desk.

- Core panel route: `/app/ui_panel`
- Core Desk remains available: `/app/home`

## Access Requirements

- User must be logged in.
- User must be a **System User**.
- Configuration actions require **System Manager** role.

## First-Time Setup (System Manager)

### 1) Open the panel

Go to `/app/ui_panel`.

You should see:
- Topbar actions (Desk, Dashboard, Builder, Components, Appearance, Refresh)
- Sidebar navigation
- Main content area

### 2) Seed component defaults once

In panel topbar, click **Components**.

This seeds default component families/options if missing:
- `card -> soft_shadow`
- `button -> rounded_primary`
- `list_row -> hover_glow`
- `sidebar -> compact_dark`

Then it opens `UI Component Option` list where you can edit/create variants.

### 3) Confirm theme and appearance

Click **Appearance**.

- Select a color scheme (`UI Theme`)
- Optional: select layout preset (if presets exist)
- Click **Apply**

Changes apply instantly in panel runtime.

### 4) Confirm navigation

Ensure an active `UI Panel Navigation` profile exists.

If sidebar is empty:
- Create/update profile in `UI Panel Navigation`
- Set `is_active = 1`
- Add `navigation_json` sections/items

### 5) Verify dashboard source

Panel dashboard reads from `UI Panel Dashboard` default record.

If dashboard is empty:
- Create/update `UI Panel Dashboard`
- Set `is_default = 1`
- Define widgets in `dashboard_json`

## Daily Usage (All System Users)

### Open panel

Use `/app/ui_panel`.

### Navigate

Use sidebar items:
- `doctype` type: inline list render
- `report/page/url/route` types: opens corresponding route

### Quick actions

- **Desk**: jump to core desk (`/app/home`)
- **Dashboard**: reload default panel dashboard view
- **Refresh**: reload full panel bundle (theme + nav + runtime)

## Builder (No-Code Template Flow)

Use topbar **Builder** to generate templates from DocType metadata.

### Steps

1. Click **Builder**
2. Enter template title
3. Choose template type:
   - `dashboard`
   - `list`
   - `form`
4. Choose source DocType
5. Optional: check **Publish Now**
6. Click **Generate + Save**

This creates a `UI View Template` record.

Notes:
- Saved example template retained for documentation: `User List Template`
- Publishing `dashboard` templates syncs into `UI Panel Dashboard`

## API Bridge for External Apps

For React/Next.js or external admin clients:

- `galaxy_ui.api.bridge.get_ui_app_config(app_id)`
- `galaxy_ui.api.bridge.get_ui_bundle(app_id)`
- `galaxy_ui.api.bridge.get_ui_nav(app_id)`

SDK and examples:
- `docs/sdk/galaxy-ui-client.ts`
- `docs/INTEGRATION_SDK.md`

## API Registry (No-Code Data APIs)

Use `UI API Registry` to publish safe list/get APIs.

### Minimal flow

1. Create key in `UI API Registry`
2. Set `source_type = Doctype`
3. Set `source_doctype`
4. Define:
   - `allowed_fields_json`
   - `filters_allowed_json`
   - `order_by_allowed_json`
   - `limit_rules_json`
5. Set role constraints (`allowed_roles_json`)
6. Use form buttons:
   - **Publish API**
   - **Test API**
   - **Generate TS Types**

Runtime endpoint:
- `galaxy_ui.api.registry.call(key, params)`

## Component Options Library

### DocTypes

- `UI Component`: component families (sidebar, card, table, etc.)
- `UI Component Option`: per-family options with runtime JSON:
  - `css_vars_json`
  - `classes_json`

### How panel consumes this

Panel reads `layout.component_options` mapping, then resolves via:
- `galaxy_ui.api.component.resolve_component_options`

Resolved variables/classes are applied to panel shell at runtime.

## Canonical Records to Know

- Theme: `UI Theme`, `UI Token`
- Navigation: `UI Panel Navigation`
- Dashboard: `UI Panel Dashboard`
- Layout: `UI Layout Preset`
- Bridge: `UI App Config`
- Registry: `UI API Registry`
- Components: `UI Component`, `UI Component Option`
- Templates: `UI View Template`

## Troubleshooting

### Panel blank or stale UI

- Hard refresh browser (`Ctrl+Shift+R`)
- Verify route is `/app/ui_panel` (not alias)
- Confirm user is `System User`
- Ensure theme/nav records exist and are enabled

### Appearance button errors

- Confirm method exists:
  - `galaxy_ui.api.layout.get_appearance_options`
- Clear cache after updates

### Missing navigation/items

- Check active `UI Panel Navigation`
- Validate `navigation_json` schema

### Registry call denied

- Check `allowed_roles_json`
- Check source DocType read permission
- Check owner/company scope rules

### Builder save/publish fails

- Ensure user has System Manager role
- Ensure `config_json` valid for selected template type

## Recommended Onboarding Sequence (New Site)

1. Open `/app/ui_panel`
2. Seed components (Components button)
3. Select/apply theme (Appearance button)
4. Configure navigation profile
5. Configure default dashboard
6. Create first registry key and test it
7. Create first template with Builder (use `User` doctype)
8. Integrate external app using bridge bundle API

## Reference Docs

- `docs/PHASE_SUMMARY.md`
- `docs/INTEGRATION_SDK.md`
- `docs/sdk/galaxy-ui-client.ts`

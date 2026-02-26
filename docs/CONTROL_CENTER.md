# Galaxy UI Control Center

## What It Is

Control Center is an internal admin screen inside `/app/ui_panel#/control-center` for operating Galaxy UI safely.
It is designed for setup, health verification, and repeatable admin actions.

## Access

- Required user type: `System User`
- Required role: `System Manager`
- Backend endpoints enforce this role check for every action.

## Sections

### 1) Current Status

Read-only summary:

- Active Theme and publish status
- Active Layout Preset
- Active Navigation Profile and item count
- Feature flags (`bridge`, `registry`, `builder`)
- Core record counts

### 2) Setup Wizard

Actions:

- `Seed Defaults`: Creates baseline theme/layout/navigation/components only if missing.
- `Apply Active Theme`: Publishes/activates selected current theme and refreshes bundle.
- `Apply Active Layout`: Applies active/default layout preset to active theme.
- `Set Active Navigation`: Publishes/activates selected/default nav profile.
- `Run Health Checks`: Re-runs checklist and returns latest status.

All actions are idempotent and safe to run multiple times.

### 3) Health Checks

Checklist outputs `PASS`, `WARN`, or `FAIL` with hints.
Checks include DocType presence, active theme/navigation/layout state, bundle best-effort readiness, bridge config readiness, and registry publication readiness.

## Expected Outcomes

- Fresh site can become operational by running `Seed Defaults` once.
- Existing sites can use Apply actions to re-sync active settings.
- Health checks provide quick troubleshooting hints for missing setup pieces.

## Troubleshooting

- Permission error: ensure the user has `System Manager`.
- Theme not active: run `Apply Active Theme`.
- No layout preset: run `Seed Defaults`.
- Nav missing/empty: run `Seed Defaults` then edit `UI Panel Navigation`.
- Bridge check warning: create/enable at least one `UI App Config`.
- Registry check warning: create and publish at least one `UI API Registry` key.

## System Overview

- `UI Theme`: tokenized colors/mode and publish status for runtime bundle.
- `UI Token`: token rows attached to theme records.
- `UI Layout Preset`: shell + component option presets applied to active theme.
- `UI Panel Navigation`: sidebar/topbar profile JSON used by panel shell.
- `UI App Config`: bridge configuration for external React/Next.js apps.
- `UI API Registry`: no-code API exposure with allowlists and role constraints.
- `UI Component`: component registry (sidebar/card/button/etc).
- `UI Component Option`: style variants mapping to css vars/classes.
- `UI View Template`: UI Builder-generated templates for dashboard/list/form.
- `UI Panel Dashboard`: default dashboard widgets rendered in panel home.

## User Journeys

1. Setup from scratch
- Open `/app/ui_panel#/control-center`.
- Click `Seed Defaults`.
- Click `Apply Active Theme`, `Apply Active Layout`, and `Set Active Navigation`.
- Run `Run Health Checks` until critical checks pass.

2. Change theme/layout
- Update or create theme/preset records in their doctypes.
- Return to Control Center.
- Click `Apply Active Theme` and/or `Apply Active Layout`.
- Refresh panel and verify status reflects new active selections.

3. Update navigation
- Edit `UI Panel Navigation` profile JSON.
- Ensure it is published/default if needed.
- In Control Center click `Set Active Navigation`.
- Re-run `Run Health Checks` and confirm item count/active profile.

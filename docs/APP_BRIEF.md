# Galaxy UI App Brief

## App Name

`galaxy_ui`

## One-Line Summary

Galaxy UI is a production-safe, upgrade-safe alternative admin interface for Frappe/ERPNext that runs inside Desk and is driven by no-code configuration.

## Problem It Solves

Default Desk is powerful but not always optimized for:
- modern admin-shell UX patterns
- centralized UI governance (layout/theme/nav)
- external app configuration via a single bridge
- no-code API publishing and frontend type generation

Galaxy UI provides these capabilities without modifying core Frappe files.

## Core Vision

Build a "UI Operating System" on top of Frappe where System Managers can control:
- panel experience
- themes and presets
- navigation
- no-code APIs
- reusable component options
- template-driven dashboard/list/form experiences

## Target Users

Primary:
- System Users (panel consumers)

Administrative:
- System Managers (configuration, publishing, governance)

## Current Operating Mode

- Canonical route: `/app/ui_panel`
- Core Desk remains available at `/app/home`
- No core-file replacement, only additive extension patterns

## Feature Set

### 1) Alternative Admin Panel Shell

- Full-screen panel UI within Desk
- Topbar actions + sidebar navigation + content region
- Dashboard and list rendering inside panel
- Mobile-responsive layout behavior

### 2) Theme + Layout Runtime

- Runtime token bundle from active theme
- Layout preset application on active theme
- Instant appearance switching from panel (theme + optional preset)

### 3) Navigation Governance

- `UI Panel Navigation` as JSON-driven navigation model
- Active/default profile support
- Route-safe rendering in panel shell

### 4) Bridge Config Hub (External App Integration)

- `UI App Config` stores external app config (non-secret)
- Bridge APIs return app config, nav, and merged runtime bundle
- Enables React/Next.js clients to consume environment-like config from Frappe

### 5) No-Code API Registry

- `UI API Registry` defines list/get endpoints per key
- Strict field/filter/order/limit allowlists
- Role and scope enforcement
- Generic runtime endpoint:
  - `galaxy_ui.api.registry.call(key, params)`

### 6) TypeScript Type Generation

- Generates TS interfaces for registry endpoints
- Supports external client typing and integration consistency

### 7) Component Options Library

- `UI Component` and `UI Component Option`
- Variant-level CSS variable and class flags
- Resolver API merges selected options into runtime payload

### 8) Builder (Template MVP)

- `UI View Template` for no-code templates
- Builder flow can generate from DocType metadata
- Save/publish template from panel
- Dashboard template publishing can sync into `UI Panel Dashboard`

## Architecture Highlights

- Upgrade-safe: no core file edits
- Configuration via DocTypes
- Runtime APIs for bundle/config/navigation/registry/builder
- UI behavior driven by JSON schemas and allowlists

## Security Model (High-Level)

- System User gate on runtime APIs
- System Manager gate on publish/seed/save operations
- Allowlist-based registry execution
- Owner/company scope enforcement where configured

## Business Value

- Faster UI customization without custom fork maintenance
- Better governance for admin UX decisions
- Faster external app integration via bridge APIs
- Reduced frontend/backend drift via generated TS contracts

## Documentation References

- `docs/GETTING_STARTED.md`
- `docs/PHASE_SUMMARY.md`
- `docs/INTEGRATION_SDK.md`
- `docs/sdk/galaxy-ui-client.ts`

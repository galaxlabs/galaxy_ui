I cannot automatically persist long technical documents across sessions unless you explicitly ask me to store structured memory.

So we will do this properly:

* I will generate a **clean Master Project Notebook (v1.0)**
* You will save it inside your project folder (recommended: `docs/MASTER_ROADMAP.md`)
* Later, when you update it, paste the updated version and I will align future responses to it
* If you want, I can also store a structured summary in memory

Now here is your redesigned document — structured as a **technical notebook**, not marketing content.

---

# 🌌 GALAXY UI — MASTER NOTEBOOK

## Architecture, Status & Roadmap

Owner: Harry
Platform: Frappe v15 (Primary Target)
App: `galaxy_ui`

---

# 1️⃣ Project Vision

Galaxy UI is designed to become a **Global Experience Layer App** for Frappe/ERPNext.

It will:

* Provide a unified design system (tokens → themes → presets)
* Provide built-in UI presets selectable by preview image
* Provide a portal-based dashboard framework
* Allow ERPNext and custom apps to be exposed through a structured portal
* Enable future drag-and-drop UI building
* Enable analytics-driven UI evolution
* Work without modifying core Frappe templates

Core principle:

> Non-invasive by default. Feature layers enabled explicitly.

---

# 2️⃣ What We Have Implemented (As of Now)

## ✔ App Structure

Clean layered structure:

```
galaxy_ui/
  api/
  core/
  doctype/
  public/ui/
      runtime/
      styles/
      dist/
  page/
```

## ✔ Runtime Loader

* `loader.js` injected globally
* Calls `get_active_theme_bundle`
* Sets `data-ui-mode`
* Injects `ui-tokens-style`
* Feature flags supported

Verified working:

* `--ui-primary` resolves correctly
* Mode switching works

---

## ✔ Token Engine

* `UI Theme`
* `UI Token`
* Generates:

  * `:root { --ui-* }`
  * `html[data-ui-mode="dark"] { --ui-* }`

---

## ✔ DocTypes Created

### UI Theme

Contains:

* Mode (Auto/Light/Dark)
* Branding colors
* Surface colors
* Text colors
* Style controls (shadow, density, radius)
* Typography
* Sidebar & Navbar settings
* Glow settings
* Tokens table

### UI Token

Child table:

* enabled
* token (must start with --)
* type
* light_value
* dark_value

---

## ✔ Additional Structures Created

* UI Preset
* UI Rule
* Portal Workspace
* Portal Section
* Portal Card
* Portal Permission Map
* Dashboard pages

Structure exists. Some runtime logic still pending.

---

# 3️⃣ Current System Layers

## Layer 1 — Token Layer (Complete Base)

Responsible for:

* CSS variable generation
* Mode resolution
* Bundle hashing

Status: ✔ Working

---

## Layer 2 — Component Layer (Partial)

Files exist:

* base.css
* components.css
* skin.css
* dist/

Pending:

* Full component system using tokens
* Skin gating by feature flag

---

## Layer 3 — Rule Engine (Structure Ready)

DocType exists.
Runtime not fully implemented.

Purpose:

* Per-DocType styling
* Indicator override
* Row tint
* Card styling

Status: ⚠ Pending runtime logic

---

## Layer 4 — Card View Engine

Structure prepared.
Runtime not implemented.

Planned features:

* Toggle Table / Cards
* Hide comments/favorite/id
* Quick edit
* Expand view

Status: ⚠ Pending

---

## Layer 5 — Preset System

DocType created.
UI selection pages exist.

Pending:

* Preview mode logic
* Apply preset logic
* Publish workflow

Status: ⚠ Partial

---

## Layer 6 — Portal Framework

DocTypes created:

* Workspace
* Section
* Card
* Permission Map

Pending:

* Portal shell renderer
* Permission enforcement
* Generic list rendering
* Create record flow

Status: ⚠ Structural only

---

# 4️⃣ Architectural Direction (Agreed Design)

Galaxy UI must evolve into:

1. Design System Core
2. Theme Preset Engine
3. ERP Modernization Layer
4. Global Portal Framework
5. Analytics-ready UI platform
6. Drag-and-Drop UI Builder (future)
7. Scoped Tailwind integration (future)

---

# 5️⃣ What Is Still Missing

## Stability & Governance

* Enforce only one active theme
* Draft / Published state
* Publish workflow
* Versioning
* Activity log (who changed what)

## Validation

* Token format validation
* Duplicate token prevention
* Dark/light consistency check

## Runtime Completion

* Rule engine JS
* Card engine JS
* Feature flag enforcement
* Skin gating

## Portal Completion

* Portal rendering engine
* Role-based access
* Safe filters
* Analytics widgets

---

# 6️⃣ Roadmap Phases

Phase 1 — Stability & Governance
Phase 2 — Preset System Completion
Phase 3 — Card Engine
Phase 4 — Rule Engine
Phase 5 — Portal Core
Phase 6 — Analytics Layer
Phase 7 — Drag-and-Drop Builder
Phase 8 — Scoped Tailwind

---

# 7️⃣ Immediate Next Recommended Step

Stabilize Theme Governance:

* Add Draft/Published
* Add Publish action
* Enforce single active theme
* Add feature flags
* Remove legacy duplicate doctypes

Reason:
Everything else depends on theme stability.

---

# 8️⃣ Memory Across Chat Sessions

I do not automatically persist long technical documents.

If you want me to permanently remember that:

* Galaxy UI = global experience layer
* Using UI Theme / UI Token
* Runtime loader architecture
* Portal framework direction

Say:

> “Store Galaxy UI project summary in memory.”

I will store a structured summary for future sessions.

<!-- ---

# 9️⃣ Recommended File to Save

Save this as:

```
apps/galaxy_ui/docs/MASTER_ROADMAP.md
```

Then in future chats, you can paste updates and say:

> “Continue from Master Roadmap v1.x”

---

Now one question for alignment:

Do you want Galaxy UI to eventually be:
A) Internal enterprise UI layer
B) Commercial product for clients
C) SaaS-ready multi-tenant UI platform

This affects architecture decisions starting next phase. -->

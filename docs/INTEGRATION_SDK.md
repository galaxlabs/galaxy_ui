# Galaxy UI Integration SDK (React/Next.js)

This document defines a production-safe integration flow for external apps that consume `galaxy_ui` runtime config.

## 1) Server endpoints to consume

- `galaxy_ui.api.bridge.get_ui_app_config(app_id)`
- `galaxy_ui.api.bridge.get_ui_bundle(app_id)`
- `galaxy_ui.api.bridge.get_ui_nav(app_id)`
- `galaxy_ui.api.registry.call(key, params)`
- `galaxy_ui.api.registry.types(app_id|key)`
- `galaxy_ui.api.builder.list_templates(template_type)`

All endpoints require authenticated System User session.

## 2) SDK file

Use: `docs/sdk/galaxy-ui-client.ts`

Recommended placement in Next.js app:
- `src/lib/galaxy-ui-client.ts`

## 3) Next.js usage example

```ts
import { GalaxyUIClient } from "@/lib/galaxy-ui-client";

const client = new GalaxyUIClient({
  siteUrl: process.env.NEXT_PUBLIC_FRAPPE_URL!,
  // Optional server-side cookie forwarding for SSR
  cookie: undefined,
});

export async function loadBootBundle() {
  const bundle = await client.getUIBundle("external.portal");
  return bundle;
}
```

## 4) Apply runtime tokens in React

```ts
export function applyCSSTokens(cssTokens: string) {
  const id = "galaxy-ui-runtime-tokens";
  let node = document.getElementById(id) as HTMLStyleElement | null;
  if (!node) {
    node = document.createElement("style");
    node.id = id;
    document.head.appendChild(node);
  }
  node.textContent = cssTokens || "";
}
```

## 5) Call generated registry APIs

```ts
const result = await client.callRegistry("phase5.user.list", {
  mode: "list",
  page_length: 10,
  filters: { enabled: 1 },
});
```

## 6) Example template for docs

Saved sample template in site:
- `User List Template` (`template_type=list`, `source_doctype=User`)

Use it in docs/screenshots as the baseline no-code builder output.

## 7) Suggested SDK package layout

```text
src/lib/galaxy-ui/
  client.ts            // transport + method wrapper
  bridge.ts            // getUIBundle/getUIAppConfig wrappers
  registry.ts          // callRegistry + typed helpers
  templates.ts         // list/get template helpers
  tokens.ts            // css token applier
  types.ts             // generated API response interfaces
```

## 8) Security checklist for external app

- Never call with Guest session.
- Use allowlisted `UI API Registry` keys only.
- Do not expose privileged session cookies to browser logs.
- Cache `get_ui_bundle` by `hash`.
- Enforce role checks in Frappe (already in server endpoints).

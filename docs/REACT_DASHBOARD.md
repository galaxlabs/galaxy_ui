# React Dashboard Integration (Galaxy UI)

This enables Galaxy UI to open an external React admin dashboard (for example hosted on Vercel) from `/app/ui_panel`.

## 1) Configure `UI App Config`

Open **UI App Config** and set `base_urls` JSON with your React app URL:

```json
{
  "react_dashboard_url": "https://your-dashboard.vercel.app"
}
```

Optional feature flag:

```json
{
  "react_dashboard": 1
}
```

- `react_dashboard: 1` shows the **React Dashboard** buttons in Galaxy UI Panel.
- If missing, feature defaults to enabled.

## 2) Runtime Bridge API

Galaxy UI exposes:

- `galaxy_ui.api.bridge.get_react_dashboard_runtime(app_id?: str)`

Response includes:

- `react_dashboard_url`
- `base_urls`
- `feature_flags`
- `branding`
- `frappe.site`
- `frappe.base_url`
- `frappe.api_base`
- `frappe.user`

## 3) How opening works

From `/app/ui_panel`, clicking **React Dashboard** opens a new tab and appends query params:

- `frappe_site`
- `frappe_base`
- `app_id`

Your React app can use these values to call Frappe APIs and load app-specific settings.

## 4) Recommended auth for external frontend

- Use Frappe API keys/tokens for service-level access, or
- Use OAuth/JWT gateway for user-level access.

For public Vercel frontend, avoid exposing privileged secrets in client code.

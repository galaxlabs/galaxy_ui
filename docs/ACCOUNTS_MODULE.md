# Accounts Module (React + Frappe)

Phase-1 Accounts module is now available with:

- Account-related DocType discovery
- CRUD (permission-aware)
- Highcharts monthly income/expense/profit dashboard
- Print format list and save designer endpoint

## Backend APIs

- `galaxy_ui.api.accounts_module.get_accounts_doctypes`
- `galaxy_ui.api.accounts_module.accounts_list`
- `galaxy_ui.api.accounts_module.accounts_get`
- `galaxy_ui.api.accounts_module.accounts_save`
- `galaxy_ui.api.accounts_module.accounts_delete`
- `galaxy_ui.api.accounts_module.accounts_dashboard_report`
- `galaxy_ui.api.accounts_module.accounts_print_formats`
- `galaxy_ui.api.accounts_module.save_accounts_print_format`

All APIs require logged-in **System User**.

## Frontend module

React workspace file:

- `apps/galaxy_ui/react_dashboard/src/modules/AccountsWorkspace.tsx`

Features:

- Select account-related DocType
- List records using `frappe.get_all` backend API
- Create/Update/Delete actions based on user permission
- Highcharts reporting block
- Print format designer UI (HTML/CSS save)

## Deploy steps

From bench root:

```bash
bench --site <site> migrate
bench build --app galaxy_ui
bench --site <site> clear-cache
```

React dashboard:

```bash
cd apps/galaxy_ui/react_dashboard
npm install
npm run build
```

If npm registry is temporarily unreachable, retry `npm install` when connectivity is restored.

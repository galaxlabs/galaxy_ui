(function inject_ui_panel_css() {
  if (document.getElementById("guip-style")) return;
  const css = `
  .guip-page .layout-main-section-wrapper { max-width:none !important; }
  .guip-page .layout-main-section { padding: 0 !important; }
  .guip-shell {
    --guip-radius: 14px;
    --guip-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
    min-height: calc(100vh - 84px);
    width: 100%;
    background: var(--guip-shell-bg,
      radial-gradient(1200px 460px at -10% -20%, rgba(16, 185, 129, 0.16), transparent 50%),
      radial-gradient(1100px 420px at 110% -25%, rgba(99, 102, 241, 0.12), transparent 46%),
      var(--ui-bg, #f8fafc)
    );
    border: 1px solid var(--ui-border, #e5e7eb);
    border-radius: 0;
    overflow: hidden;
  }
  .guip-topbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    padding:10px 14px;
    border-bottom:1px solid var(--ui-border, #e5e7eb);
    background: color-mix(in srgb, var(--ui-navbar-bg, #f8fafc) 86%, #ffffff 14%);
    backdrop-filter: blur(6px);
  }
  .guip-actions { display:flex; gap:8px; flex-wrap:wrap; }
  .guip-body { display:grid; grid-template-columns:280px minmax(0,1fr) 320px; min-height: calc(100vh - 142px); }
  .guip-sidebar { padding:12px; background:color-mix(in srgb, var(--ui-sidebar-bg, #f8fafc) 90%, #ffffff 10%); border-right:1px solid var(--ui-border, #e5e7eb); overflow-y:auto; }
  .guip-content { padding:14px; overflow-y:auto; }
  .guip-right { padding:14px; border-left:1px solid var(--ui-border, #e5e7eb); background:rgba(255,255,255,0.55); overflow-y:auto; }
  .guip-box,.guip-card { border:1px solid var(--ui-border, #e5e7eb); border-radius: var(--guip-radius); background: var(--ui-card, #fff); box-shadow: var(--guip-shadow); padding:12px; margin-bottom:12px; }
  .guip-nav-title { font-size:12px; text-transform:uppercase; letter-spacing:.04em; margin:10px 6px 6px; color:var(--ui-text-muted,#6b7280); }
  .guip-nav-item { width:100%; text-align:left; border:0; background:transparent; border-radius:10px; padding:8px 10px; cursor:pointer; color:var(--ui-text,#111827); }
  .guip-nav-item:hover { background:rgba(0,0,0,.05); }
  .guip-nav-item.is-active { background:rgba(37,99,235,.15); }
  .guip-daily-wrap { margin-bottom:10px; }
  .guip-daily-item { width:100%; text-align:left; border:1px solid var(--ui-border,#e5e7eb); background:var(--ui-card,#fff); border-radius:10px; padding:7px 9px; margin-bottom:6px; cursor:pointer; }
  .guip-daily-item:hover { background:rgba(0,0,0,.03); }
  .guip-table-wrap { overflow:auto; border:1px solid var(--ui-border,#e5e7eb); border-radius:var(--guip-radius); }
  .guip-table { width:100%; border-collapse:separate; border-spacing:0; min-width:720px; }
  .guip-table th,.guip-table td { padding:10px; border-bottom:1px solid var(--ui-border,#e5e7eb); text-align:left; }
  .guip-form-frame-wrap { border:1px solid var(--ui-border,#e5e7eb); border-radius:var(--guip-radius); overflow:hidden; background:var(--ui-card,#fff); }
  .guip-form-frame { width:100%; min-height: calc(100vh - 240px); border:0; background:#fff; }
  .guip-toolbar-actions { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
  .guip-form-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
  .guip-form-field { border:1px solid var(--ui-border,#e5e7eb); border-radius:10px; padding:10px; background:var(--ui-card,#fff); }
  .guip-form-field label { display:block; font-size:12px; margin-bottom:6px; color:var(--ui-text-muted,#6b7280); }
  .guip-form-field textarea,.guip-form-field input,.guip-form-field select { width:100%; }
  .guip-form-field.is-full { grid-column:1 / -1; }
  .guip-kpi-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }
  .guip-kpi { border:1px solid var(--ui-border,#e5e7eb); border-radius:10px; padding:10px; }
  .guip-kpi .value { font-size:22px; font-weight:700; }
  .guip-links { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-top:10px; }
  .guip-link { border:1px solid var(--ui-border,#e5e7eb); border-radius:10px; padding:10px; cursor:pointer; background:var(--ui-card,#fff); }
  .guip-status-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
  .guip-status-item { border:1px solid var(--ui-border,#e5e7eb); border-radius:10px; padding:10px; }
  .guip-status-label { font-size:12px; color:var(--ui-text-muted,#6b7280); margin-bottom:4px; }
  .guip-status-value { font-weight:600; display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
  .guip-badge { display:inline-block; border-radius:999px; padding:2px 8px; font-size:11px; font-weight:700; }
  .guip-badge-pass { background:#dcfce7; color:#166534; }
  .guip-badge-fail { background:#fee2e2; color:#991b1b; }
  .guip-badge-warn { background:#fef3c7; color:#92400e; }
  .guip-badge-na { background:#e5e7eb; color:#374151; }
  .guip-wizard-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
  .guip-wizard-action { border:1px solid var(--ui-border,#e5e7eb); border-radius:10px; padding:10px; }
  .guip-wizard-action .btn { margin-bottom:6px; }
  .guip-checklist { display:flex; flex-direction:column; gap:8px; }
  .guip-check-item { border:1px solid var(--ui-border,#e5e7eb); border-radius:10px; padding:10px; }
  .guip-check-head { display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:6px; }
  .guip-right-stat { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; padding:8px 10px; border:1px solid var(--ui-border,#e5e7eb); border-radius:10px; background:var(--ui-card,#fff); }
  .guip-right h4 { margin:2px 0 10px 0; }
  .guip-row-glow .guip-table tbody tr:hover { background: var(--guip-row-hover, rgba(37,99,235,.12)); }
  .guip-sidebar-compact .guip-body { grid-template-columns: var(--guip-sidebar-width, 280px) 1fr; }
  .guip-btn-rounded .btn { border-radius: 999px; }
  @media (max-width: 900px) {
    .guip-body { grid-template-columns:1fr; }
    .guip-sidebar { border-right:0; border-bottom:1px solid var(--ui-border,#e5e7eb); }
    .guip-right { border-left:0; border-top:1px solid var(--ui-border,#e5e7eb); }
    .guip-kpi-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .guip-links { grid-template-columns:1fr; }
    .guip-status-grid, .guip-wizard-grid { grid-template-columns:1fr; }
    .guip-form-grid { grid-template-columns:1fr; }
  }
  `;
  const style = document.createElement("style");
  style.id = "guip-style";
  style.textContent = css;
  document.head.appendChild(style);
})();

function galaxy_ui_panel_on_page_load(wrapper) {
  const RUNTIME_STYLE_ID = "galaxy-ui-component-runtime";
  $(wrapper).addClass("guip-page");
  frappe.ui.make_app_page({
    parent: wrapper,
    title: "Galaxy UI Panel",
    single_column: true,
  });

  // hard reset any old hash-router state that caused guip chains
  if ((window.location.hash || "").includes("guip/")) {
    history.replaceState(null, "", window.location.pathname);
  }

  const state = {
    bundle: null,
    nav: { sections: [], topbar: [] },
    activeItemKey: "",
    appliedShellClasses: [],
    features: {},
    listView: {
      doctype: "",
      fields: [],
      start: 0,
      pageLength: 20,
      search: "",
      filters: [],
      orderBy: "modified desc",
    },
  };

  const $root = $(wrapper).find(".layout-main-section");
  $root.empty();

  const $shell = $(`
    <div class="guip-shell ui-panel-root">
      <div class="guip-topbar">
        <div><b>Galaxy UI</b></div>
        <div class="guip-actions">
          <button class="btn btn-default btn-sm guip-go-desk">Desk</button>
          <button class="btn btn-default btn-sm guip-go-home">Dashboard</button>
          <button class="btn btn-default btn-sm guip-react-dashboard">React Dashboard</button>
          <button class="btn btn-default btn-sm guip-navigation">Navigation</button>
          <button class="btn btn-default btn-sm guip-registry">Registry</button>
          <button class="btn btn-default btn-sm guip-bridge">Bridge</button>
          <button class="btn btn-default btn-sm guip-builder">Builder</button>
          <button class="btn btn-default btn-sm guip-daily-manager">Daily Use +</button>
          <button class="btn btn-default btn-sm guip-components">Components</button>
          <button class="btn btn-default btn-sm guip-runtime-resolve">Resolve Runtime</button>
          <button class="btn btn-default btn-sm guip-appearance">Appearance</button>
          <button class="btn btn-primary btn-sm guip-refresh">Refresh</button>
        </div>
      </div>
      <div class="guip-body">
        <aside class="guip-sidebar">
          <div class="guip-box">
            <div class="text-muted">Layout</div>
            <div class="guip-layout-name">-</div>
          </div>
          <div class="guip-box guip-nav-host">Loading navigation...</div>
        </aside>
        <main class="guip-content">
          <div class="guip-card">
            <h3 class="guip-title" style="margin-top:0">Loading...</h3>
            <div class="guip-body-host"></div>
          </div>
        </main>
        <aside class="guip-right">
          <div class="guip-card">
            <h4>Panel Status</h4>
            <div class="guip-right-stat"><span>User</span><b class="guip-r-user">-</b></div>
            <div class="guip-right-stat"><span>Theme</span><b class="guip-r-theme">-</b></div>
            <div class="guip-right-stat"><span>Layout</span><b class="guip-r-layout">-</b></div>
          </div>
          <div class="guip-card">
            <h4>Quick Actions</h4>
            <button class="btn btn-default btn-sm guip-go-home" style="width:100%;margin-bottom:8px">Open Dashboard</button>
            <button class="btn btn-default btn-sm guip-react-dashboard" style="width:100%;margin-bottom:8px">Open React Dashboard</button>
            <button class="btn btn-default btn-sm guip-daily-manager" style="width:100%;margin-bottom:8px">Manage Daily Use</button>
            <button class="btn btn-default btn-sm guip-appearance" style="width:100%;margin-bottom:8px">Change Appearance</button>
            <button class="btn btn-default btn-sm guip-runtime-resolve" style="width:100%">Resolve Runtime</button>
          </div>
        </aside>
      </div>
    </div>
  `);

  $root.append($shell);

  function esc(v) {
    return frappe.utils.escape_html(String(v == null ? "" : v));
  }

  function set_body(title, html) {
    $shell.find(".guip-title").html(title || "");
    $shell.find(".guip-body-host").html(html || "");
  }

  function is_feature_enabled(name) {
    const raw = (state.features && Object.prototype.hasOwnProperty.call(state.features, name))
      ? state.features[name]
      : 1;
    return String(raw) === "1" || raw === true;
  }

  function apply_feature_flags() {
    $shell.find(".guip-appearance").toggle(is_feature_enabled("appearance"));
    $shell.find(".guip-builder").toggle(is_feature_enabled("builder"));
    $shell.find(".guip-components").toggle(is_feature_enabled("components"));
    $shell.find(".guip-go-home").toggle(is_feature_enabled("dashboard"));
    $shell.find(".guip-navigation").toggle(is_feature_enabled("navigation"));
    $shell.find(".guip-registry").toggle(is_feature_enabled("registry"));
    $shell.find(".guip-bridge").toggle(is_feature_enabled("bridge"));
    $shell.find(".guip-react-dashboard").toggle(is_feature_enabled("react_dashboard"));
    $shell.find(".guip-runtime-resolve").toggle(is_feature_enabled("components"));
  }

  async function open_react_dashboard() {
    try {
      const appId = ((state.bundle || {}).app_config || {}).app_id || "";
      const r = await frappe.call("galaxy_ui.api.bridge.get_react_dashboard_runtime", { app_id: appId || undefined });
      const cfg = (r && r.message) || {};
      const target = String(cfg.react_dashboard_url || "").trim() || "/assets/galaxy_ui/react_dashboard/index.html";
      const u = new URL(target, window.location.origin);
      u.searchParams.set("frappe_site", String((cfg.frappe && cfg.frappe.site) || ""));
      u.searchParams.set("frappe_base", String((cfg.frappe && cfg.frappe.base_url) || ""));
      u.searchParams.set("app_id", String(cfg.app_id || ""));
      window.open(u.toString(), "_blank", "noopener,noreferrer");
    } catch (e) {
      frappe.msgprint(__("Failed to open React dashboard"));
    }
  }

  function apply_layout() {
    const layout = (state.bundle && state.bundle.theme && state.bundle.theme.layout) || null;
    $shell.find(".guip-layout-name").text(layout ? (layout.name || "Custom") : "Default");
    const user = (((state.bundle || {}).env || {}).user || "-");
    const themeMode = (((state.bundle || {}).theme || {}).mode || "-");
    const preset = (((state.bundle || {}).active_layout_preset || {}).title || ((state.bundle || {}).active_layout_preset || {}).name || "Default");
    $shell.find(".guip-r-user").text(user);
    $shell.find(".guip-r-theme").text(themeMode);
    $shell.find(".guip-r-layout").text(preset);
  }

  function apply_component_runtime(payload) {
    const runtime = payload || {};
    const cssVars = (runtime.css_vars && typeof runtime.css_vars === "object") ? runtime.css_vars : {};
    const nextShellClasses = Array.isArray(runtime.classes) ? runtime.classes : [];

    for (const cls of state.appliedShellClasses || []) {
      if (cls) $shell.removeClass(cls);
    }
    for (const cls of nextShellClasses) {
      if (cls) $shell.addClass(cls);
    }
    state.appliedShellClasses = nextShellClasses.slice();

    let styleEl = document.getElementById(RUNTIME_STYLE_ID);
    const varLines = [];
    for (const [k, v] of Object.entries(cssVars)) {
      if (String(k || "").startsWith("--") && String(v || "").trim()) {
        varLines.push(`${k}:${String(v).replace(/;/g, "")};`);
      }
    }

    if (!varLines.length) {
      if (styleEl) styleEl.remove();
      return;
    }

    if (!styleEl) {
      styleEl = document.createElement("style");
      styleEl.id = RUNTIME_STYLE_ID;
      document.head.appendChild(styleEl);
    }
    styleEl.textContent = `.ui-panel-root{${varLines.join("")}}`;
  }

  function item_key(item) {
    return `${item.type || "x"}:${item.ref || item.route || item.label || ""}`;
  }

  function normalize_item(item) {
    const it = item || {};
    const type = (it.type || "route").toLowerCase();
    const ref = (it.ref || "").trim();
    const route = (it.route || "").trim();
    const label = (it.label || ref || route || "Item").trim();
    return { type, ref, route, label, params: it.params || {} };
  }

  function daily_doctypes_key() {
    const site = (frappe.boot && frappe.boot.sitename) || "site";
    const user = (frappe.session && frappe.session.user) || "user";
    return `galaxy_ui.daily_doctypes:${site}:${user}`;
  }

  function get_daily_doctypes() {
    try {
      const raw = localStorage.getItem(daily_doctypes_key()) || "[]";
      const arr = JSON.parse(raw);
      return Array.isArray(arr) ? arr.filter(Boolean) : [];
    } catch (_e) {
      return [];
    }
  }

  function set_daily_doctypes(items) {
    const clean = Array.from(new Set((items || []).map((x) => String(x || "").trim()).filter(Boolean))).slice(0, 20);
    localStorage.setItem(daily_doctypes_key(), JSON.stringify(clean));
    return clean;
  }

  function is_daily_doctype(doctype) {
    return get_daily_doctypes().includes(String(doctype || "").trim());
  }

  function toggle_daily_doctype(doctype) {
    const dt = String(doctype || "").trim();
    if (!dt) return { exists: false, items: get_daily_doctypes() };
    const curr = get_daily_doctypes();
    if (curr.includes(dt)) {
      const next = curr.filter((x) => x !== dt);
      set_daily_doctypes(next);
      return { exists: false, items: next };
    }
    const next = set_daily_doctypes(curr.concat([dt]));
    return { exists: true, items: next };
  }

  function build_panel_nav() {
    const base = state.nav && Array.isArray(state.nav.sections)
      ? JSON.parse(JSON.stringify(state.nav))
      : { sections: [], topbar: [] };
    const hasControlCenter = (base.sections || []).some((section) => (
      (section.items || []).some((it) => String((it && (it.ref || it.route || "") || "")).includes("control-center"))
    ));
    if (!hasControlCenter) {
      base.sections = [{
        label: "Galaxy UI",
        items: [
          {
            type: "route",
            ref: "control-center",
            route: "#/control-center",
            label: "Control Center",
            icon: "settings",
          },
        ],
      }].concat(base.sections || []);
    }
    return base;
  }

  function render_nav() {
    const nav = build_panel_nav();
    const parts = [];
    const daily = get_daily_doctypes();
    if (daily.length) {
      parts.push('<div class="guip-box guip-daily-wrap"><div class="guip-nav-title" style="margin-top:0">Daily Use</div>');
      for (const dt of daily) {
        parts.push(`<button class="guip-daily-item guip-open-daily" data-doctype="${esc(dt)}">${esc(dt)}</button>`);
      }
      parts.push("</div>");
    }
    for (const section of (nav.sections || [])) {
      parts.push(`<div class="guip-nav-title">${esc(section.label || "Section")}</div>`);
      for (const rawItem of (section.items || [])) {
        const item = normalize_item(rawItem);
        const key = item_key(item);
        const active = state.activeItemKey === key ? "is-active" : "";
        parts.push(`<button class="guip-nav-item ${active}" data-item='${esc(JSON.stringify(item))}'>${esc(item.label)}</button>`);
      }
    }
    if (!parts.length) {
      parts.push('<div class="text-muted">No navigation configured.</div>');
    }
    $shell.find(".guip-nav-host").html(parts.join(""));
  }

  function badge_class(status) {
    const s = String(status || "").toUpperCase();
    if (s === "PASS") return "guip-badge guip-badge-pass";
    if (s === "FAIL") return "guip-badge guip-badge-fail";
    if (s === "WARN") return "guip-badge guip-badge-warn";
    return "guip-badge guip-badge-na";
  }

  async function render_control_center() {
    const [statusRes, checksRes] = await Promise.all([
      frappe.call("galaxy_ui.api.control_center.get_status"),
      frappe.call("galaxy_ui.api.control_center.run_health_checks"),
    ]);
    const status = statusRes.message || {};
    const checks = (checksRes.message && checksRes.message.checks) || [];

    const theme = status.active_theme || {};
    const layout = status.active_layout_preset || {};
    const nav = status.active_navigation_profile || {};
    const flags = status.feature_flags || {};

    const fmtFlag = (v) => (String(v) === "1" || v === 1 || v === true ? "Enabled" : (String(v) === "0" || v === 0 || v === false ? "Disabled" : "N/A"));

    const statusHtml = `
      <div class="guip-status-grid">
        <div class="guip-status-item"><div class="guip-status-label">Active Theme</div><div class="guip-status-value">${esc(theme.name || "-")} <span class="${badge_class(theme.status || "N/A")}">${esc(theme.status || "N/A")}</span></div></div>
        <div class="guip-status-item"><div class="guip-status-label">Active Layout Preset</div><div class="guip-status-value">${esc(layout.title || layout.name || "-")}</div></div>
        <div class="guip-status-item"><div class="guip-status-label">Active Navigation Profile</div><div class="guip-status-value">${esc(nav.title || nav.name || "-")} <span class="${badge_class(nav.status || "N/A")}">${esc(nav.status || "N/A")}</span></div></div>
        <div class="guip-status-item"><div class="guip-status-label">Theme Publish Status</div><div class="guip-status-value"><span class="${badge_class(theme.status || "N/A")}">${esc(theme.status || "N/A")}</span></div></div>
        <div class="guip-status-item"><div class="guip-status-label">Feature Flags</div><div class="guip-status-value">Bridge: ${esc(fmtFlag(flags.bridge))}</div></div>
        <div class="guip-status-item"><div class="guip-status-label">Feature Flags</div><div class="guip-status-value">Registry: ${esc(fmtFlag(flags.registry))}, Builder: ${esc(fmtFlag(flags.builder))}</div></div>
      </div>
    `;

    const wizardHtml = `
      <div class="guip-wizard-grid">
        <div class="guip-wizard-action"><button class="btn btn-sm btn-primary guip-cc-action" data-action="seed_defaults">Seed Defaults</button><div class="text-muted small">Create baseline theme/layout/navigation/components if missing.</div></div>
        <div class="guip-wizard-action"><button class="btn btn-sm btn-default guip-cc-action" data-action="apply_active_theme">Apply Active Theme</button><div class="text-muted small">Publishes and reapplies current active theme bundle.</div></div>
        <div class="guip-wizard-action"><button class="btn btn-sm btn-default guip-cc-action" data-action="apply_active_layout">Apply Active Layout</button><div class="text-muted small">Applies current default/active layout preset to active theme.</div></div>
        <div class="guip-wizard-action"><button class="btn btn-sm btn-default guip-cc-action" data-action="set_active_navigation">Set Active Navigation</button><div class="text-muted small">Marks selected/default navigation profile as active and published.</div></div>
        <div class="guip-wizard-action"><button class="btn btn-sm btn-default guip-cc-action" data-action="run_health_checks">Run Health Checks</button><div class="text-muted small">Re-evaluate environment readiness and show latest checklist.</div></div>
      </div>
    `;

    const checksHtml = (checks || []).map((row) => `
      <div class="guip-check-item">
        <div class="guip-check-head">
          <div><b>${esc(row.title || row.key || "Check")}</b></div>
          <span class="${badge_class(row.status)}">${esc(row.status || "N/A")}</span>
        </div>
        <div class="small text-muted">${esc(row.hint || "")}</div>
        ${row.details ? `<div class="small" style="margin-top:4px">${esc(row.details)}</div>` : ""}
      </div>
    `).join("") || '<div class="text-muted">No checks found.</div>';

    set_body("Control Center", `
      <div class="guip-card">
        <h4 style="margin-top:0">Current Status</h4>
        ${statusHtml}
      </div>
      <div class="guip-card">
        <h4 style="margin-top:0">Setup Wizard</h4>
        ${wizardHtml}
      </div>
      <div class="guip-card">
        <h4 style="margin-top:0">Health Checks</h4>
        <div class="guip-checklist">${checksHtml}</div>
      </div>
    `);
  }

  async function load_dashboard() {
    const listRes = await frappe.call("frappe.client.get_list", {
      doctype: "UI Panel Dashboard",
      fields: ["name", "title", "dashboard_json", "is_default", "modified"],
      filters: { is_default: 1 },
      order_by: "modified desc",
      limit_page_length: 1,
    });

    const row = (listRes.message || [])[0] || null;
    let dashboard = { title: "Panel Dashboard", sections: [] };
    if (row && row.dashboard_json) {
      try {
        dashboard = JSON.parse(row.dashboard_json);
      } catch (_e) {
        dashboard = { title: row.title || "Panel Dashboard", sections: [] };
      }
    }

    const chunks = [];
    for (const section of (dashboard.sections || [])) {
      const widgets = Array.isArray(section.widgets) ? section.widgets : [];
      const kpis = widgets.filter((w) => w.type === "kpi_count");
      const links = widgets.filter((w) => w.type === "link");

      const kpiBlocks = [];
      for (const k of kpis) {
        let val = "-";
        try {
          const c = await frappe.call("frappe.client.get_count", {
            doctype: k.doctype,
            filters: k.filters || {},
          });
          val = (c.message && c.message.count != null) ? c.message.count : "-";
        } catch (_e) {
          val = "!";
        }
        kpiBlocks.push(`<div class="guip-kpi"><div class="text-muted">${esc(k.label || k.doctype || "KPI")}</div><div class="value">${esc(val)}</div></div>`);
      }

      const linkBlocks = links
        .map((l) => `<div class="guip-link" data-route="${esc(l.route || "")}">${esc(l.label || "Open")}</div>`)
        .join("");

      chunks.push(`
        <div class="guip-card">
          <h4 style="margin-top:0">${esc(section.label || "Section")}</h4>
          ${kpiBlocks.length ? `<div class="guip-kpi-grid">${kpiBlocks.join("")}</div>` : ""}
          ${linkBlocks ? `<div class="guip-links">${linkBlocks}</div>` : ""}
        </div>
      `);
    }

    set_body("Dashboard", chunks.join("") || '<div class="text-muted">No widgets configured.</div>');
  }

  let listSearchTimer = null;
  function parse_hash_route() {
    const hash = String(window.location.hash || "").trim();
    if (!hash) return null;
    const dt = hash.match(/^#\/doctype\/([^?]+)/i);
    if (dt) {
      const doctype = decodeURIComponent(dt[1] || "").trim();
      if (doctype) {
        const query = hash.includes("?") ? hash.slice(hash.indexOf("?") + 1) : "";
        const qs = new URLSearchParams(query);
        let filters = [];
        const rawFilters = qs.get("filters");
        if (rawFilters) {
          try {
            const parsed = JSON.parse(decodeURIComponent(rawFilters));
            filters = Array.isArray(parsed) ? parsed : [];
          } catch (_e) {
            filters = [];
          }
        }
        const search = String(qs.get("search") || "").trim();
        const orderBy = String(qs.get("order_by") || "modified desc").trim();
        return { type: "doctype", doctype, filters, search, orderBy };
      }
    }
    const fm = hash.match(/^#\/form\/([^/]+)\/([^?]+)/i);
    if (fm) {
      const doctype = decodeURIComponent(fm[1] || "").trim();
      const name = decodeURIComponent(fm[2] || "").trim();
      if (doctype && name) return { type: "form", doctype, name };
    }
    if (hash === "#/control-center") return { type: "control-center" };
    return null;
  }

  function open_form_in_panel(doctype, name) {
    if (!doctype || !name) return;
    window.location.hash = `/form/${encodeURIComponent(doctype)}/${encodeURIComponent(name)}`;
  }

  function format_input_value(fieldtype, value) {
    if (value == null) return "";
    if (fieldtype === "Check") return String(value) === "1" || value === 1 || value === true ? "1" : "0";
    if (fieldtype === "Datetime") {
      const raw = String(value || "").trim();
      return raw ? raw.replace(" ", "T").slice(0, 16) : "";
    }
    return String(value);
  }

  function parse_input_value(fieldtype, raw) {
    if (fieldtype === "Check") return raw ? 1 : 0;
    if (fieldtype === "Int") return raw === "" ? null : Number.parseInt(raw, 10);
    if (fieldtype === "Float" || fieldtype === "Currency") return raw === "" ? null : Number.parseFloat(raw);
    if (fieldtype === "Datetime") return raw ? String(raw).replace("T", " ") + ":00" : "";
    return raw;
  }

  function render_native_form_input(f, value) {
    const fieldname = esc(f.fieldname || "");
    const fieldtype = String(f.fieldtype || "Data");
    const readonly = Number(f.read_only || 0) ? "disabled" : "";
    const v = value == null ? "" : value;
    if (fieldtype === "Small Text") {
      return `<textarea class="form-control input-xs guip-form-input" data-fieldname="${fieldname}" data-fieldtype="${esc(fieldtype)}" rows="3" ${readonly}>${esc(v)}</textarea>`;
    }
    if (fieldtype === "Check") {
      const checked = format_input_value(fieldtype, v) === "1" ? "checked" : "";
      return `<input type="checkbox" class="guip-form-input" data-fieldname="${fieldname}" data-fieldtype="${esc(fieldtype)}" ${checked} ${readonly}/>`;
    }
    if (fieldtype === "Select") {
      const options = String(f.options || "")
        .split("\n")
        .map((x) => String(x || "").trim())
        .filter(Boolean)
        .map((opt) => {
          const sel = String(v) === opt ? "selected" : "";
          return `<option value="${esc(opt)}" ${sel}>${esc(opt)}</option>`;
        })
        .join("");
      return `<select class="form-control input-xs guip-form-input" data-fieldname="${fieldname}" data-fieldtype="${esc(fieldtype)}" ${readonly}><option value=""></option>${options}</select>`;
    }
    const inputType = fieldtype === "Date"
      ? "date"
      : (fieldtype === "Datetime" ? "datetime-local" : ((fieldtype === "Int" || fieldtype === "Float" || fieldtype === "Currency") ? "number" : "text"));
    const step = (fieldtype === "Float" || fieldtype === "Currency") ? ' step="0.01"' : "";
    return `<input type="${inputType}" class="form-control input-xs guip-form-input" data-fieldname="${fieldname}" data-fieldtype="${esc(fieldtype)}" value="${esc(format_input_value(fieldtype, v))}" ${step} ${readonly}/>`;
  }

  async function render_doctype_form(doctype, name) {
    const title = `Form: ${esc(doctype)} / ${esc(name)}`;
    set_body(title, '<div class="text-muted">Loading form...</div>');
    const r = await frappe.call("galaxy_ui.api.panel_content.get_doctype_doc", { doctype, name });
    const payload = r.message || {};
    const fields = Array.isArray(payload.fields) ? payload.fields.filter((f) => !Number(f.hidden || 0)) : [];
    const values = payload.values || {};
    const canWrite = Number(payload.can_write || 0) === 1;
    const isSubmittable = Number(payload.is_submittable || 0) === 1;
    const route = `/app/${frappe.scrub(doctype)}/${encodeURIComponent(name)}`;

    const rows = fields.map((f) => {
      const full = String(f.fieldtype || "") === "Small Text" ? "is-full" : "";
      const req = Number(f.reqd || 0) ? " <span class='text-danger'>*</span>" : "";
      return `<div class="guip-form-field ${full}">
        <label>${esc(f.label || f.fieldname)}${req}</label>
        ${render_native_form_input(f, values[f.fieldname])}
      </div>`;
    }).join("");

    const html = `
      <div class="guip-box">
        <div style="display:flex;justify-content:space-between;gap:8px;align-items:center;flex-wrap:wrap">
          <div><b>${esc(doctype)}</b> <span class="text-muted small">${esc(name)}</span></div>
          <div class="guip-toolbar-actions">
            <button class="btn btn-default btn-sm guip-back-list" data-doctype="${esc(doctype)}">Back to List</button>
            ${canWrite ? `<button class="btn btn-primary btn-sm guip-save-form" data-doctype="${esc(doctype)}" data-name="${esc(name)}">Save</button>` : ""}
            <button class="btn btn-default btn-sm guip-open-native-form" data-route="${esc(route)}">Open in Desk</button>
          </div>
        </div>
      </div>
      ${isSubmittable ? `<div class="guip-box"><div class="text-warning small">Safety mode: in-panel editing is disabled for submittable DocTypes (example: Sales Invoice). Use "Open in Desk".</div></div>` : ""}
      <div class="guip-form-grid">${rows || '<div class="text-muted">No safe fields available for panel form rendering.</div>'}</div>
    `;
    set_body(title, html);
  }

  async function open_daily_use_dialog() {
    const current = get_daily_doctypes();
    const d = new frappe.ui.Dialog({
      title: __("Daily Use DocTypes"),
      fields: [
        {
          fieldname: "doctype_name",
          label: __("DocType"),
          fieldtype: "Link",
          options: "DocType",
          reqd: 1,
        },
      ],
      primary_action_label: __("Add"),
      primary_action: (values) => {
        const dt = String(values.doctype_name || "").trim();
        if (!dt) return;
        set_daily_doctypes(current.concat([dt]));
        frappe.show_alert({ message: __("Added to Daily Use: {0}", [dt]), indicator: "green" });
        render_nav();
        d.hide();
      },
      secondary_action_label: __("Remove"),
      secondary_action: (values) => {
        const dt = String(values.doctype_name || "").trim();
        if (!dt) return;
        set_daily_doctypes(current.filter((x) => x !== dt));
        frappe.show_alert({ message: __("Removed from Daily Use: {0}", [dt]), indicator: "green" });
        render_nav();
        d.hide();
      },
    });
    d.show();
  }

  async function render_doctype_list(doctype) {
    const lv = state.listView || {};
    lv.doctype = doctype;
    state.listView = lv;
    set_body(`List: ${esc(doctype)}`, '<div class="text-muted">Loading records...</div>');

    const metaRes = await frappe.call("galaxy_ui.api.panel_content.get_doctype_meta", { doctype });
    const meta = metaRes.message || {};

    const listRes = await frappe.call("galaxy_ui.api.panel_content.get_doctype_list", {
      doctype,
      fields: JSON.stringify(lv.fields || []),
      filters: JSON.stringify(lv.filters || []),
      limit_start: lv.start || 0,
      limit_page_length: lv.pageLength || 20,
      search: lv.search || "",
      order_by: lv.orderBy || "modified desc",
    });
    const payload = listRes.message || {};
    const columns = payload.columns || [];
    const rows = payload.rows || [];
    const total = Number(payload.total_count || 0);
    const start = Number(payload.limit_start || 0);
    const pageLength = Number(payload.limit_page_length || 20);
    const hasMore = !!payload.has_more;
    const hasPrev = start > 0;

    const head = columns.map((c) => `<th>${esc(c.label || c.fieldname)}</th>`).join("");
    const body = rows.map((row) => {
      const tds = columns.map((c) => `<td>${esc(row[c.fieldname])}</td>`).join("");
      return `<tr class="guip-open-doc" data-doctype="${esc(doctype)}" data-name="${esc(row.name)}">${tds}</tr>`;
    }).join("");

    const favLabel = is_daily_doctype(doctype) ? "Remove Daily Use" : "Add Daily Use";
    const toolbar = `
      <div class="guip-box ui-panel-list">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap">
          <div><b>${esc(meta.label || doctype)}</b> <span class="text-muted small">(${esc(total)})</span></div>
          <div class="guip-toolbar-actions">
            <input class="form-control input-xs guip-list-search" value="${esc(lv.search || "")}" placeholder="Search name/title..." style="min-width:220px" />
            <button class="btn btn-default btn-sm guip-toggle-daily" data-doctype="${esc(doctype)}">${esc(favLabel)}</button>
            <button class="btn btn-default btn-sm guip-list-refresh">Refresh</button>
          </div>
        </div>
      </div>
    `;
    const pager = `
      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:10px">
        <div class="text-muted small">Showing ${esc(start + 1)}-${esc(start + rows.length)} of ${esc(total)}</div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-default btn-sm guip-page-prev" ${hasPrev ? "" : "disabled"}>Prev</button>
          <button class="btn btn-default btn-sm guip-page-next" ${hasMore ? "" : "disabled"}>Next</button>
        </div>
      </div>
    `;

    set_body(
      `List: ${esc(doctype)}`,
      `${toolbar}<div class="guip-table-wrap ui-panel-list"><table class="guip-table"><thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${columns.length || 1}">No records</td></tr>`}</tbody></table></div>${pager}`
    );
  }

  function open_route(route) {
    const r = String(route || "").trim();
    if (!r) return;
    if (r.startsWith("#/")) {
      window.location.href = `/app/ui_panel${r}`;
      return;
    }
    if (r.startsWith("/")) {
      window.location.href = r;
      return;
    }
    if (/^https?:\/\//i.test(r)) {
      window.open(r, "_blank");
      return;
    }
    window.location.href = `/app/${frappe.scrub(r)}`;
  }

  async function activate_item(item) {
    const it = normalize_item(item);
    state.activeItemKey = item_key(it);
    render_nav();

    const refNorm = String(it.ref || "").trim().replace(/^#\//, "").replace(/^\/+/, "");
    const routeNorm = String(it.route || "").trim().replace(/^#\//, "").replace(/^\/+/, "");
    if (refNorm === "control-center" || routeNorm === "control-center") {
      await render_control_center();
      return;
    }

    if (it.type === "doctype" && it.ref) {
      const p = (it.params && typeof it.params === "object") ? it.params : {};
      const targetName = String(p.name || p.record_name || "").trim();
      if (targetName) {
        open_form_in_panel(it.ref, targetName);
        await render_doctype_form(it.ref, targetName);
        return;
      }
      const filters = Array.isArray(p.filters) ? p.filters : [];
      const search = String(p.search || "").trim();
      const orderBy = String(p.order_by || "modified desc").trim();
      const query = new URLSearchParams();
      if (filters.length) query.set("filters", encodeURIComponent(JSON.stringify(filters)));
      if (search) query.set("search", search);
      if (orderBy && orderBy !== "modified desc") query.set("order_by", orderBy);
      const q = query.toString();
      window.location.hash = `/doctype/${encodeURIComponent(it.ref)}${q ? `?${q}` : ""}`;
      state.listView = { doctype: it.ref, fields: [], start: 0, pageLength: 20, search, filters, orderBy };
      await render_doctype_list(it.ref);
      return;
    }

    if (it.type === "report") {
      open_route(it.route || `/app/query-report/${frappe.scrub(it.ref)}`);
      return;
    }

    if (it.type === "page" || it.type === "workspace" || it.type === "route" || it.type === "url") {
      open_route(it.route || it.ref);
      return;
    }

    set_body("Unsupported", `<div class="text-danger">Unsupported nav item type: ${esc(it.type)}</div>`);
  }

  async function open_appearance_dialog() {
    const r = await frappe.call("galaxy_ui.api.layout.get_appearance_options");
    const payload = r.message || {};
    const presets = payload.presets || [];
    const themes = payload.themes || [];
    const current = payload.current || {};

    if (!themes.length) {
      frappe.msgprint(__("No themes available. Configure UI Theme first."));
      return;
    }

    const fields = [];
    const keepLayoutOption = "Keep Current Layout";
    const presetOptions = [keepLayoutOption].concat(presets.map((p) => p.name)).join("\n");
    fields.push({
      fieldname: "preset_name",
      label: __("Layout Preset"),
      fieldtype: "Select",
      reqd: 1,
      options: presetOptions,
      default: current.preset || keepLayoutOption,
      description: __("Choose Keep Current Layout to switch only theme"),
    });
    fields.push({
      fieldname: "theme_name",
      label: __("Color Scheme (Theme)"),
      fieldtype: "Select",
      reqd: 1,
      options: themes.map((t) => t.name).join("\n"),
      default: current.theme || themes[0].name,
    });

    const d = new frappe.ui.Dialog({
      title: __("Panel Appearance"),
      fields,
      secondary_action_label: __("Seed Theme Variants"),
      secondary_action: async () => {
        const seedRes = await frappe.call("galaxy_ui.api.theme.seed_panel_theme_variants");
        const msg = seedRes.message || {};
        frappe.show_alert({
          message: __("Theme variants: {0} created, {1} updated, {2} skipped", [
            msg.created || 0,
            msg.updated || 0,
            msg.skipped || 0,
          ]),
          indicator: "green",
        });
        d.hide();
        await open_appearance_dialog();
      },
      primary_action_label: __("Apply"),
      primary_action: async (values) => {
        const presetName = values.preset_name === keepLayoutOption ? null : values.preset_name;
        await frappe.call("galaxy_ui.api.layout.apply_panel_appearance", {
          preset_name: presetName,
          theme_name: values.theme_name,
        });
        d.hide();
        await load_bundle();
        frappe.show_alert({ message: __("Appearance applied"), indicator: "green" });
      },
    });

    d.show();
  }

  async function open_builder_dialog() {
    const dtRes = await frappe.call("frappe.client.get_list", {
      doctype: "DocType",
      fields: ["name"],
      filters: { istable: 0 },
      order_by: "name asc",
      limit_page_length: 500,
    });
    const doctypes = (dtRes.message || []).map((x) => x.name).filter(Boolean);
    if (!doctypes.length) {
      frappe.msgprint(__("No DocTypes available"));
      return;
    }

    const d = new frappe.ui.Dialog({
      title: __("UI Builder"),
      fields: [
        {
          fieldname: "title",
          label: __("Template Title"),
          fieldtype: "Data",
          reqd: 1,
          default: "Untitled Template",
        },
        {
          fieldname: "template_type",
          label: __("Template Type"),
          fieldtype: "Select",
          options: "dashboard\nlist\nform",
          default: "list",
          reqd: 1,
        },
        {
          fieldname: "source_doctype",
          label: __("Source DocType"),
          fieldtype: "Select",
          options: doctypes.join("\n"),
          default: doctypes.includes("User") ? "User" : doctypes[0],
          reqd: 1,
        },
        {
          fieldname: "publish_now",
          label: __("Publish Now"),
          fieldtype: "Check",
          default: 0,
        },
      ],
      primary_action_label: __("Generate + Save"),
      primary_action: async (values) => {
        const draft = await frappe.call("galaxy_ui.api.builder.generate_from_doctype", {
          doctype: values.source_doctype,
          template_type: values.template_type,
        });

        const saveRes = await frappe.call("galaxy_ui.api.builder.save_template", {
          title: values.title,
          template_type: values.template_type,
          source_doctype: values.source_doctype,
          config_json: JSON.stringify((draft.message || {}).config || {}),
          publish: values.publish_now ? 1 : 0,
        });

        const saved = saveRes.message || {};
        d.hide();
        frappe.show_alert({ message: __("Template saved: {0}", [saved.name || values.title]), indicator: "green" });
        if (values.publish_now && values.template_type === "dashboard") {
          await load_dashboard();
        }
      },
    });
    d.show();
  }

  async function load_bundle() {
    const r = await frappe.call("galaxy_ui.api.panel.get_panel_bundle");
    state.bundle = r.message || {};
    state.nav = ((state.bundle.navigation || {}).navigation) || { sections: [], topbar: [] };
    state.features = (state.bundle.features && typeof state.bundle.features === "object")
      ? state.bundle.features
      : {};
    apply_feature_flags();
    apply_component_runtime(state.bundle.resolved_component_runtime || {});
    apply_layout();
    render_nav();
    const hashRoute = parse_hash_route();
    if (hashRoute && hashRoute.type === "doctype") {
      state.activeItemKey = "";
      state.listView = {
        doctype: hashRoute.doctype,
        fields: [],
        start: 0,
        pageLength: 20,
        search: hashRoute.search || "",
        filters: Array.isArray(hashRoute.filters) ? hashRoute.filters : [],
        orderBy: hashRoute.orderBy || "modified desc",
      };
      await render_doctype_list(hashRoute.doctype);
      return;
    }
    if (hashRoute && hashRoute.type === "form") {
      state.activeItemKey = "";
      await render_doctype_form(hashRoute.doctype, hashRoute.name);
      return;
    }
    if (hashRoute && hashRoute.type === "control-center") {
      await activate_item({ type: "route", ref: "control-center", route: "#/control-center", label: "Control Center" });
      return;
    }
    if (is_feature_enabled("dashboard")) {
      state.activeItemKey = "";
      await load_dashboard();
    } else {
      set_body("Dashboard Disabled", '<div class="text-muted">Panel dashboard is disabled by feature flag.</div>');
    }
  }

  $shell.on("click", ".guip-refresh", async function () {
    await load_bundle();
  });

  $shell.on("click", ".guip-go-home", async function () {
    if (!is_feature_enabled("dashboard")) {
      frappe.msgprint(__("Dashboard feature is disabled"));
      return;
    }
    if ((window.location.hash || "").trim()) {
      history.replaceState(null, "", window.location.pathname);
    }
    await load_dashboard();
  });

  $shell.on("click", ".guip-go-desk", function () {
    window.location.href = "/app/home";
  });

  $shell.on("click", ".guip-react-dashboard", async function () {
    await open_react_dashboard();
  });

  $shell.on("click", ".guip-appearance", async function () {
    if (!is_feature_enabled("appearance")) {
      frappe.msgprint(__("Appearance feature is disabled"));
      return;
    }
    await open_appearance_dialog();
  });

  $shell.on("click", ".guip-builder", async function () {
    if (!is_feature_enabled("builder")) {
      frappe.msgprint(__("Builder feature is disabled"));
      return;
    }
    await open_builder_dialog();
  });

  $shell.on("click", ".guip-daily-manager", async function () {
    await open_daily_use_dialog();
  });

  $shell.on("click", ".guip-navigation", function () {
    if (!is_feature_enabled("navigation")) {
      frappe.msgprint(__("Navigation feature is disabled"));
      return;
    }
    window.location.href = "/app/ui-panel-navigation";
  });

  $shell.on("click", ".guip-registry", function () {
    if (!is_feature_enabled("registry")) {
      frappe.msgprint(__("Registry feature is disabled"));
      return;
    }
    window.location.href = "/app/ui-api-registry";
  });

  $shell.on("click", ".guip-bridge", function () {
    if (!is_feature_enabled("bridge")) {
      frappe.msgprint(__("Bridge feature is disabled"));
      return;
    }
    window.location.href = "/app/ui-app-config";
  });

  $shell.on("click", ".guip-components", async function () {
    if (!is_feature_enabled("components")) {
      frappe.msgprint(__("Components feature is disabled"));
      return;
    }
    await frappe.confirm(
      __("Seed default component options if missing and open UI Component Option list?"),
      async () => {
        try {
          await frappe.call("galaxy_ui.api.component.seed_default_components");
        } catch (_e) {
          // Continue: user may not be System Manager; still allow opening list.
        }
        window.location.href = "/app/ui-component-option";
      }
    );
  });

  $shell.on("click", ".guip-runtime-resolve", async function () {
    if (!is_feature_enabled("components")) {
      frappe.msgprint(__("Components feature is disabled"));
      return;
    }
    const preset = (state.bundle && state.bundle.active_layout_preset) || {};
    if (!preset.name) {
      frappe.msgprint(__("No active layout preset found."));
      return;
    }
    await frappe.call("galaxy_ui.api.layout.resolve_layout_preset_runtime", {
      preset_name: preset.name,
      save_cache: 1,
    });
    frappe.show_alert({ message: __("Component runtime resolved"), indicator: "green" });
    await load_bundle();
  });

  $shell.on("click", ".guip-nav-item", async function () {
    let item = {};
    try {
      item = JSON.parse($(this).attr("data-item") || "{}");
    } catch (_e) {
      item = {};
    }
    await activate_item(item);
  });

  $shell.on("click", ".guip-open-doc", function () {
    const doctype = $(this).data("doctype");
    const name = $(this).data("name");
    if (doctype && name) {
      open_form_in_panel(doctype, name);
    }
  });

  $shell.on("click", ".guip-open-daily", async function () {
    const doctype = String($(this).data("doctype") || "").trim();
    if (!doctype) return;
    state.listView = { doctype, fields: [], start: 0, pageLength: 20, search: "", filters: [], orderBy: "modified desc" };
    window.location.hash = `/doctype/${encodeURIComponent(doctype)}`;
    await render_doctype_list(doctype);
  });

  $shell.on("click", ".guip-toggle-daily", function () {
    const doctype = String($(this).data("doctype") || "").trim();
    if (!doctype) return;
    const out = toggle_daily_doctype(doctype);
    render_nav();
    frappe.show_alert({
      message: out.exists ? __("Added to Daily Use: {0}", [doctype]) : __("Removed from Daily Use: {0}", [doctype]),
      indicator: "green",
    });
    $(this).text(out.exists ? "Remove Daily Use" : "Add Daily Use");
  });

  $shell.on("click", ".guip-back-list", async function () {
    const doctype = String($(this).data("doctype") || "").trim();
    if (!doctype) return;
    window.location.hash = `/doctype/${encodeURIComponent(doctype)}`;
    state.listView = { doctype, fields: [], start: 0, pageLength: 20, search: "", filters: [], orderBy: "modified desc" };
    await render_doctype_list(doctype);
  });

  $shell.on("click", ".guip-open-native-form", function () {
    const route = String($(this).data("route") || "").trim();
    if (!route) return;
    window.location.href = route;
  });

  $shell.on("click", ".guip-save-form", async function () {
    const doctype = String($(this).data("doctype") || "").trim();
    const name = String($(this).data("name") || "").trim();
    if (!doctype || !name) return;
    const values = {};
    $shell.find(".guip-form-input").each(function () {
      const $el = $(this);
      const fieldname = String($el.data("fieldname") || "").trim();
      const fieldtype = String($el.data("fieldtype") || "Data").trim();
      if (!fieldname) return;
      let raw;
      if ($el.attr("type") === "checkbox") {
        raw = $el.is(":checked");
      } else {
        raw = $el.val();
      }
      values[fieldname] = parse_input_value(fieldtype, raw);
    });
    await frappe.call("galaxy_ui.api.panel_content.save_doctype_doc", {
      doctype,
      name,
      values: JSON.stringify(values),
    });
    frappe.show_alert({ message: __("Saved {0}/{1}", [doctype, name]), indicator: "green" });
    await render_doctype_form(doctype, name);
  });

  $shell.on("click", ".guip-link", function () {
    open_route($(this).data("route"));
  });

  $shell.on("click", ".guip-cc-action", async function () {
    const action = String($(this).data("action") || "").trim();
    if (!action) return;
    try {
      await frappe.call(`galaxy_ui.api.control_center.${action}`);
      frappe.show_alert({ message: __("Control Center action completed"), indicator: "green" });
      await load_bundle();
    } catch (e) {
      frappe.msgprint(__(e.message || "Control Center action failed"));
    }
  });

  $shell.on("input", ".guip-list-search", function () {
    const doctype = (state.listView && state.listView.doctype) || "";
    if (!doctype) return;
    const value = $(this).val() || "";
    state.listView.search = String(value).trim();
    state.listView.start = 0;
    clearTimeout(listSearchTimer);
    listSearchTimer = setTimeout(() => {
      render_doctype_list(doctype).catch((e) => {
        set_body("Error", `<div class="text-danger">${esc(e.message || e)}</div>`);
      });
    }, 280);
  });

  $shell.on("click", ".guip-list-refresh", async function () {
    const doctype = (state.listView && state.listView.doctype) || "";
    if (!doctype) return;
    await render_doctype_list(doctype);
  });

  $shell.on("click", ".guip-page-prev", async function () {
    const doctype = (state.listView && state.listView.doctype) || "";
    if (!doctype) return;
    state.listView.start = Math.max(Number(state.listView.start || 0) - Number(state.listView.pageLength || 20), 0);
    await render_doctype_list(doctype);
  });

  $shell.on("click", ".guip-page-next", async function () {
    const doctype = (state.listView && state.listView.doctype) || "";
    if (!doctype) return;
    state.listView.start = Number(state.listView.start || 0) + Number(state.listView.pageLength || 20);
    await render_doctype_list(doctype);
  });

  load_bundle().catch((e) => {
    set_body("Error", `<div class="text-danger">${esc(e.message || e)}</div>`);
  });
}

["ui_panel"].forEach((pageKey) => {
  frappe.pages[pageKey] = frappe.pages[pageKey] || {};
  frappe.pages[pageKey].on_page_load = galaxy_ui_panel_on_page_load;
});

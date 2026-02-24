(function inject_ui_panel_css() {
  if (document.getElementById("guip-style")) return;

  const css = `
  /* Full page feel */
  .page-body .layout-main-section { padding: 0 !important; }
  .guip-shell { min-height: calc(100vh - 140px); }

  /* Galaxy UI Panel - scoped styles */
  .guip-shell {
    border: 1px solid var(--ui-border, #e5e7eb);
    border-radius: 12px;
    background: var(--ui-bg, #fff);
    overflow: hidden;
  }
  .guip-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 12px;
    background: var(--ui-navbar-bg, #f8fafc);
    border-bottom: 1px solid var(--ui-border, #e5e7eb);
  }
  .guip-brand { display: flex; align-items: center; gap: 10px; }
  .guip-switch .btn { margin-right: 6px; }

  /* Shell layout */
  .guip-body { display: grid; grid-template-columns: 320px 1fr; min-height: 520px; }
  .guip-sidebar {
    padding: 12px;
    background: var(--ui-sidebar-bg, #f8fafc);
    border-right: 1px solid var(--ui-border, #e5e7eb);
    overflow: auto;
  }
  .guip-content { padding: 12px; overflow: auto; }

  .guip-box, .guip-card {
    border: 1px solid var(--ui-border, #e5e7eb);
    border-radius: 12px;
    background: var(--ui-card, #fff);
    padding: 12px;
    margin-bottom: 12px;
  }
  .guip-layout-name { font-size: 16px; font-weight: 700; margin-top: 6px; color: var(--ui-text, #111827); }
  .guip-layout-meta { margin-top: 6px; }
  .guip-debug { background: rgba(0,0,0,0.03); border-radius: 10px; padding: 10px; }

  /* Sidebar nav */
  .guip-nav { margin-top: 10px; }
  .guip-nav-section { margin-bottom: 14px; }
  .guip-nav-title {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: .04em;
    color: var(--ui-text-muted, #6b7280);
    margin: 10px 6px 6px;
  }
  .guip-nav-item a{
    display:flex;
    align-items:center;
    gap:10px;
    padding: 8px 10px;
    border-radius: 10px;
    color: var(--ui-text, #111827);
    text-decoration:none;
  }
  .guip-nav-item a:hover{
    background: rgba(0,0,0,.04);
    text-decoration:none;
  }
  .guip-nav-item.is-active a{
    background: rgba(59,130,246,.12);
  }
  .guip-nav-icon{
    width:18px;
    text-align:center;
    opacity:.8;
  }

  /* Mobile: collapse sidebar to top stack */
  @media (max-width: 768px) {
    .guip-body { grid-template-columns: 1fr; }
    .guip-sidebar { border-right: 0; border-bottom: 1px solid var(--ui-border, #e5e7eb); }
  }
  `;

  const style = document.createElement("style");
  style.id = "guip-style";
  style.textContent = css;
  document.head.appendChild(style);
})();

frappe.pages["ui_panel"].on_page_load = function (wrapper) {
  frappe.ui.make_app_page({
    parent: wrapper,
    title: "Galaxy UI Panel",
    single_column: true,
  });

  const $root = $(wrapper).find(".layout-main-section");
  $root.empty();

  const $shell = $(`
    <div class="guip-shell">
      <div class="guip-topbar">
        <div class="guip-brand">
          <span class="indicator blue"></span>
          <b>Galaxy UI</b> <span class="text-muted">Admin Panel</span>
        </div>

        <div class="guip-switch">
          <button class="btn btn-default btn-sm" data-view="desk">Desk</button>
          <button class="btn btn-default btn-sm" data-view="panel">Panel</button>
          <button class="btn btn-default btn-sm" data-view="dashboard">Dashboard</button>
          <button class="btn btn-default btn-sm" data-view="web">Web</button>
        </div>

        <div class="guip-actions">
          <button class="btn btn-primary btn-sm guip-refresh">Refresh</button>
        </div>
      </div>

      <div class="guip-body">
        <div class="guip-sidebar">
          <div class="guip-box">
            <div class="text-muted">Layout</div>
            <div class="guip-layout-name">—</div>
            <div class="guip-layout-meta text-muted">—</div>
          </div>

          <div class="guip-box guip-nav-box">
            <div class="text-muted">Navigation</div>
            <div class="guip-nav text-muted">Loading…</div>
          </div>
        </div>

        <div class="guip-content">
          <div class="guip-card">
            <h4 style="margin-top:0">Preview Area</h4>
            <div class="text-muted">This will render the selected shell and components.</div>
            <hr>
            <pre class="guip-debug" style="white-space:pre-wrap"></pre>
          </div>
        </div>
      </div>
    </div>
  `);

  $root.append($shell);

  function render_bundle(bundle) {
    const layout = bundle && bundle.layout ? bundle.layout : null;

    $shell.find(".guip-layout-name").text(layout ? layout.name : "No layout_json on active theme");
    $shell
      .find(".guip-layout-meta")
      .text(layout ? `targets: ${layout.targets.join(", ")} | shell: ${layout.shell_style}` : "Set UI Theme → Layout JSON");

    $shell.find(".guip-debug").text(JSON.stringify(bundle, null, 2));
  }

  function icon_html(icon) {
    // minimal: show first letter if icon missing (later we map to lucide/fa)
    const t = (icon || "").trim();
    if (!t) return `<span class="guip-nav-icon">•</span>`;
    return `<span class="guip-nav-icon">${frappe.utils.escape_html(t.slice(0, 2))}</span>`;
  }

  function normalize_route(route) {
    const r = (route || "").trim();
    if (!r) return "";
    return r.startsWith("/") ? r : `/${r}`;
  }

  function current_route_path() {
    // location.pathname includes /app/... in desk
    return (window.location && window.location.pathname) ? window.location.pathname : "";
  }

  function render_nav(nav_payload) {
    const $nav = $shell.find(".guip-nav");

    const enabled = nav_payload && nav_payload.enabled ? 1 : 0;
    const nav = nav_payload && nav_payload.nav ? nav_payload.nav : null;

    if (!enabled) {
      $nav.html(`<div class="text-muted">Navigation is disabled. Using fallback.</div>`);
      return;
    }

    const sidebar = nav && nav.sidebar ? nav.sidebar : [];
    if (!Array.isArray(sidebar) || sidebar.length === 0) {
      $nav.html(`<div class="text-muted">No sidebar items found.</div>`);
      return;
    }

    const active_path = current_route_path();

    const parts = [];
    parts.push(`<div class="guip-nav">`);

    for (const section of sidebar) {
      const title = (section && section.label) ? section.label : "Section";
      const items = (section && Array.isArray(section.items)) ? section.items : [];

      parts.push(`<div class="guip-nav-section">`);
      parts.push(`<div class="guip-nav-title">${frappe.utils.escape_html(title)}</div>`);

      for (const item of items) {
        const label = (item && item.label) ? item.label : "Item";
        const route = normalize_route(item ? item.route : "");
        const icon = item ? item.icon : "";

        const is_active = route && active_path && active_path === route;
        parts.push(
          `<div class="guip-nav-item ${is_active ? "is-active" : ""}">
            <a href="${frappe.utils.escape_html(route || "#")}">
              ${icon_html(icon)}
              <span>${frappe.utils.escape_html(label)}</span>
            </a>
          </div>`
        );
      }

      parts.push(`</div>`);
    }

    parts.push(`</div>`);
    $nav.html(parts.join(""));
  }

  async function load_nav() {
    try {
      const res = await frappe.call("galaxy_ui.api.navigation.get_ui_panel_navigation");
      render_nav(res.message);
    } catch (e) {
      $shell.find(".guip-nav").html(`<div class="text-danger">Failed to load navigation</div>`);
      frappe.msgprint({
        title: "Galaxy UI",
        message: e.message || e,
        indicator: "red",
      });
    }
  }

  async function load_bundle() {
    try {
      const bundle = await frappe.call("galaxy_ui.api.theme.get_active_theme_bundle");
      render_bundle(bundle.message);
    } catch (e) {
      frappe.msgprint({
        title: "Galaxy UI",
        message: e.message || e,
        indicator: "red",
      });
    }
  }

  $shell.on("click", ".guip-refresh", function () {
    load_bundle();
    load_nav();
  });

  $shell.on("click", ".guip-switch .btn", function () {
    const view = $(this).data("view");
    frappe.show_alert({ message: `Switch requested: ${view}`, indicator: "blue" });
    // Phase 2: persist view selection in UI User Preference / UI Layout Preset
  });

  load_bundle();
  load_nav();
};

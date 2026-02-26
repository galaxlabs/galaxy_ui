(function inject_ui_panel_css() {
  if (document.getElementById("guip-style")) return;
  const css = `
  .page-body .layout-main-section { padding: 0 !important; }
  .guip-shell {
    --guip-radius: 12px;
    --guip-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
    min-height: calc(100vh - 120px);
    border: 1px solid var(--ui-border, #e5e7eb);
    border-radius: 14px;
    background: var(--ui-bg, #ffffff);
    overflow: hidden;
  }
  .guip-topbar { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:10px 12px; border-bottom:1px solid var(--ui-border, #e5e7eb); background:var(--ui-navbar-bg, #f8fafc); }
  .guip-actions { display:flex; gap:8px; flex-wrap:wrap; }
  .guip-body { display:grid; grid-template-columns:300px 1fr; min-height: calc(100vh - 200px); }
  .guip-sidebar { padding:12px; background:var(--ui-sidebar-bg, #f8fafc); border-right:1px solid var(--ui-border, #e5e7eb); overflow-y:auto; }
  .guip-content { padding:14px; overflow-y:auto; }
  .guip-box,.guip-card { border:1px solid var(--ui-border, #e5e7eb); border-radius: var(--guip-radius); background: var(--ui-card, #fff); box-shadow: var(--guip-shadow); padding:12px; margin-bottom:12px; }
  .guip-nav-title { font-size:12px; text-transform:uppercase; letter-spacing:.04em; margin:10px 6px 6px; color:var(--ui-text-muted,#6b7280); }
  .guip-nav-item { width:100%; text-align:left; border:0; background:transparent; border-radius:10px; padding:8px 10px; cursor:pointer; color:var(--ui-text,#111827); }
  .guip-nav-item:hover { background:rgba(0,0,0,.05); }
  .guip-nav-item.is-active { background:rgba(37,99,235,.15); }
  .guip-table-wrap { overflow:auto; border:1px solid var(--ui-border,#e5e7eb); border-radius:var(--guip-radius); }
  .guip-table { width:100%; border-collapse:separate; border-spacing:0; min-width:720px; }
  .guip-table th,.guip-table td { padding:10px; border-bottom:1px solid var(--ui-border,#e5e7eb); text-align:left; }
  .guip-kpi-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }
  .guip-kpi { border:1px solid var(--ui-border,#e5e7eb); border-radius:10px; padding:10px; }
  .guip-kpi .value { font-size:22px; font-weight:700; }
  .guip-links { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-top:10px; }
  .guip-link { border:1px solid var(--ui-border,#e5e7eb); border-radius:10px; padding:10px; cursor:pointer; background:var(--ui-card,#fff); }
  .guip-row-glow .guip-table tbody tr:hover { background: var(--guip-row-hover, rgba(37,99,235,.12)); }
  .guip-sidebar-compact .guip-body { grid-template-columns: var(--guip-sidebar-width, 280px) 1fr; }
  .guip-btn-rounded .btn { border-radius: 999px; }
  @media (max-width: 900px) {
    .guip-body { grid-template-columns:1fr; }
    .guip-sidebar { border-right:0; border-bottom:1px solid var(--ui-border,#e5e7eb); }
    .guip-kpi-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .guip-links { grid-template-columns:1fr; }
  }
  `;
  const style = document.createElement("style");
  style.id = "guip-style";
  style.textContent = css;
  document.head.appendChild(style);
})();

function galaxy_ui_panel_on_page_load(wrapper) {
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
  };

  const $root = $(wrapper).find(".layout-main-section");
  $root.empty();

  const $shell = $(`
    <div class="guip-shell">
      <div class="guip-topbar">
        <div><b>Galaxy UI</b></div>
        <div class="guip-actions">
          <button class="btn btn-default btn-sm guip-go-desk">Desk</button>
          <button class="btn btn-default btn-sm guip-go-home">Dashboard</button>
          <button class="btn btn-default btn-sm guip-navigation">Navigation</button>
          <button class="btn btn-default btn-sm guip-registry">Registry</button>
          <button class="btn btn-default btn-sm guip-bridge">Bridge</button>
          <button class="btn btn-default btn-sm guip-builder">Builder</button>
          <button class="btn btn-default btn-sm guip-components">Components</button>
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
  }

  function apply_layout() {
    const layout = (state.bundle && state.bundle.theme && state.bundle.theme.layout) || null;
    $shell.find(".guip-layout-name").text(layout ? (layout.name || "Custom") : "Default");
  }

  function apply_component_runtime(payload) {
    const runtime = payload || {};
    const cssVars = (runtime.css_vars && typeof runtime.css_vars === "object") ? runtime.css_vars : {};
    const classScopes = (runtime.classes && typeof runtime.classes === "object") ? runtime.classes : {};
    const nextShellClasses = Array.isArray(classScopes.shell) ? classScopes.shell : [];

    for (const cls of state.appliedShellClasses || []) {
      if (cls) $shell.removeClass(cls);
    }
    for (const cls of nextShellClasses) {
      if (cls) $shell.addClass(cls);
    }
    state.appliedShellClasses = nextShellClasses.slice();

    const shellEl = $shell.get(0);
    if (!shellEl || !shellEl.style) return;
    for (const [k, v] of Object.entries(cssVars)) {
      if (String(k || "").startsWith("--")) {
        shellEl.style.setProperty(k, String(v == null ? "" : v));
      }
    }
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

  function render_nav() {
    const parts = [];
    for (const section of (state.nav.sections || [])) {
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

  async function load_doctype_list(doctype) {
    let payload = null;
    try {
      const r = await frappe.call("galaxy_ui.api.panel.get_list_data", {
        doctype,
        fields: JSON.stringify(["name", "modified", "owner"]),
        filters: JSON.stringify([]),
        start: 0,
        page_length: 20,
        order_by: "modified desc",
      });
      payload = r.message || null;
    } catch (_e) {
      const r = await frappe.call("frappe.client.get_list", {
        doctype,
        fields: ["name", "modified", "owner"],
        order_by: "modified desc",
        limit_page_length: 20,
      });
      payload = { fields: ["name", "modified", "owner"], rows: r.message || [] };
    }

    const fields = payload.fields || ["name", "modified", "owner"];
    const rows = payload.rows || [];
    const head = fields.map((f) => `<th>${esc(f)}</th>`).join("");
    const body = rows.map((row) => {
      const tds = fields.map((f) => `<td>${esc(row[f])}</td>`).join("");
      return `<tr class="guip-open-doc" data-doctype="${esc(doctype)}" data-name="${esc(row.name)}">${tds}</tr>`;
    }).join("");

    set_body(
      `List: ${esc(doctype)}`,
      `<div class="guip-table-wrap"><table class="guip-table"><thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${fields.length}">No records</td></tr>`}</tbody></table></div>`
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

    if (it.type === "doctype" && it.ref) {
      await load_doctype_list(it.ref);
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
    try {
      const layout = (state.bundle.theme || {}).layout || {};
      const componentOptions = (layout && typeof layout === "object") ? (layout.component_options || {}) : {};
      const rr = await frappe.call("galaxy_ui.api.component.resolve_component_options", {
        component_options: JSON.stringify(componentOptions),
      });
      apply_component_runtime(rr.message || {});
    } catch (_e) {
      apply_component_runtime({});
    }
    apply_layout();
    render_nav();
    if (is_feature_enabled("dashboard")) {
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
    await load_dashboard();
  });

  $shell.on("click", ".guip-go-desk", function () {
    window.location.href = "/app/home";
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
      window.open(`/app/${frappe.scrub(doctype)}/${encodeURIComponent(name)}`, "_blank");
    }
  });

  $shell.on("click", ".guip-link", function () {
    open_route($(this).data("route"));
  });

  load_bundle().catch((e) => {
    set_body("Error", `<div class="text-danger">${esc(e.message || e)}</div>`);
  });
}

["ui_panel"].forEach((pageKey) => {
  frappe.pages[pageKey] = frappe.pages[pageKey] || {};
  frappe.pages[pageKey].on_page_load = galaxy_ui_panel_on_page_load;
});

frappe.pages["ui-dashboard"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "UI Dashboard",
    single_column: true,
  });

  $(wrapper).find(".layout-main-section").html(`
    <div class="ui" style="padding: 16px;">
      <div class="ui-card" style="padding: 16px; border: 1px solid var(--ui-border, #e5e7eb); border-radius: var(--ui-radius, 10px); background: var(--ui-card, #fff);">
        <h3 style="margin:0 0 8px 0;">UI Dashboard</h3>
        <p style="margin:0 0 12px 0; color: var(--ui-text-muted, #6b7280);">
          Page loaded. Next: preset grid + live preview + Apply/Customize actions.
        </p>
        <button class="btn btn-primary" id="ui-test-fetch">Test Theme Bundle API</button>
        <pre id="ui-test-out" style="margin-top:12px; padding:12px; background:#111827; color:#e5e7eb; border-radius:8px; overflow:auto;"></pre>
      </div>
    </div>
  `);

  $(wrapper).on("click", "#ui-test-fetch", () => {
    frappe.call("galaxy_ui.api.theme.get_active_theme_bundle").then((r) => {
      $("#ui-test-out").text(JSON.stringify(r.message || {}, null, 2));
      frappe.show_alert({ message: "Theme bundle loaded", indicator: "green" });
    });
  });
};

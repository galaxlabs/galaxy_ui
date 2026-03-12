frappe.ui.form.on("UI Layout Preset", {
  refresh(frm) {
    frm.set_intro(__("Defines panel layout behavior and component variants."), "blue");
    if (!frm.is_new()) {
      frm.add_custom_button(__("Resolve Component Runtime"), async () => {
        const r = await frappe.call("galaxy_ui.api.layout.resolve_layout_preset_runtime", {
          preset_name: frm.doc.name,
          save_cache: 1,
        });
        const msg = r.message || {};
        frappe.show_alert({
          message: __("Runtime resolved ({0} vars, {1} classes)", [
            Object.keys(msg.css_vars || {}).length,
            (msg.classes || []).length,
          ]),
          indicator: "green",
        });
        await frm.reload_doc();
      });
    }
  },
});

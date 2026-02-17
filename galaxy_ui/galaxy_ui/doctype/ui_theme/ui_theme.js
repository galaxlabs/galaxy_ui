// Copyright (c) 2026, Galaxy Labs and contributors
// For license information, please see license.txt
frappe.ui.form.on("UI Theme", {
  refresh(frm) {
    // Show Publish button only when not already published+active
    const is_published = frm.doc.status === "Published";
    const is_active = cint(frm.doc.is_active) === 1;

    if (!frm.is_new() && !(is_published && is_active)) {
      frm.add_custom_button(__("Publish"), () => {
        frappe.call({
          method: "galaxy_ui.api.publish.publish_theme",
          args: { name: frm.doc.name },
          freeze: true,
          freeze_message: __("Publishing theme..."),
          callback(r) {
            if (r && r.message && r.message.ok) {
              frappe.show_alert({ message: __("Theme published"), indicator: "green" });
              frm.reload_doc();
            }
          },
        });
      }).addClass("btn-primary");
    }
  },
});
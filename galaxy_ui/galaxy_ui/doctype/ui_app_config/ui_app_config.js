frappe.ui.form.on("UI App Config", {
  refresh(frm) {
    frm.set_intro(__("Stores non-secret bridge config for external UI apps."), "blue");
  },
});

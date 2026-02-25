frappe.ui.form.on("UI API Registry", {
  refresh(frm) {
    frm.set_intro(__("Register no-code list/get APIs with strict allowlists."), "blue");
    add_registry_actions(frm);
  },
});

function add_registry_actions(frm) {
  if (frm.is_new()) {
    return;
  }

  frm.add_custom_button(__("Publish API"), async () => {
    await frappe.call("galaxy_ui.api.registry.publish_key", {
      key: frm.doc.name,
      enabled: 1,
    });
    await frm.reload_doc();
    frappe.show_alert({ message: __("API key published"), indicator: "green" });
  });

  frm.add_custom_button(__("Unpublish API"), async () => {
    await frappe.call("galaxy_ui.api.registry.publish_key", {
      key: frm.doc.name,
      enabled: 0,
    });
    await frm.reload_doc();
    frappe.show_alert({ message: __("API key unpublished"), indicator: "orange" });
  });

  frm.add_custom_button(__("Test API"), () => open_test_dialog(frm));

  frm.add_custom_button(__("Generate TS Types"), async () => {
    const r = await frappe.call("galaxy_ui.api.registry.types", { key: frm.doc.name });
    const out = (r.message && r.message.typescript) || "";
    frappe.msgprint({
      title: __("Generated TypeScript"),
      message: `<pre style="max-height:360px;overflow:auto;white-space:pre-wrap;">${frappe.utils.escape_html(out || "// No types generated")}</pre>`,
      wide: true,
    });
  });
}

function open_test_dialog(frm) {
  const d = new frappe.ui.Dialog({
    title: __("Test Registry API"),
    fields: [
      {
        label: __("Mode"),
        fieldname: "mode",
        fieldtype: "Select",
        options: "list\nget",
        default: "list",
        reqd: 1,
      },
      {
        label: __("Name (for get)"),
        fieldname: "name",
        fieldtype: "Data",
      },
      {
        label: __("Filters JSON"),
        fieldname: "filters_json",
        fieldtype: "Small Text",
        default: "{}",
      },
      {
        label: __("Fields CSV"),
        fieldname: "fields_csv",
        fieldtype: "Data",
      },
      {
        label: __("Page Length"),
        fieldname: "page_length",
        fieldtype: "Int",
        default: 20,
      },
    ],
    primary_action_label: __("Run"),
    primary_action: async (values) => {
      let filters = {};
      try {
        filters = JSON.parse(values.filters_json || "{}");
      } catch (e) {
        frappe.msgprint(__("Filters JSON is invalid"));
        return;
      }

      const fields = (values.fields_csv || "")
        .split(",")
        .map((x) => x.trim())
        .filter(Boolean);

      const params = {
        mode: values.mode || "list",
        filters,
        fields,
        page_length: values.page_length || 20,
      };
      if (values.mode === "get") {
        params.name = (values.name || "").trim();
      }

      const res = await frappe.call("galaxy_ui.api.registry.test_call", {
        key: frm.doc.name,
        params: JSON.stringify(params),
      });

      const message = JSON.stringify(res.message || {}, null, 2);
      frappe.msgprint({
        title: __("API Test Result"),
        message: `<pre style="max-height:420px;overflow:auto;white-space:pre-wrap;">${frappe.utils.escape_html(message)}</pre>`,
        wide: true,
      });
      d.hide();
    },
  });

  d.show();
}

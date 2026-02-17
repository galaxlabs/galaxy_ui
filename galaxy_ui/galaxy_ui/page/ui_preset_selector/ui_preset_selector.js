frappe.pages["ui_preset_selector"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __("UI Presets"),
    single_column: true,
  });

  const $body = $(page.body);

  $body.html(`
    <div class="ui-preset-selector">
      <div class="ui-presets-grid row"></div>
    </div>
  `);

  load_presets();

  async function load_presets() {
    const grid = $body.find(".ui-presets-grid");
    grid.html(`<div class="text-muted">${__("Loading...")}</div>`);

    try {
      const r = await frappe.call({
        method: "galaxy_ui.api.theme.list_presets",
      });

      const presets = r.message || [];
      grid.empty();

      if (!presets.length) {
        grid.html(`<div class="text-muted">${__("No presets found.")}</div>`);
        return;
      }

      presets.forEach(p => {
        const title = p.preset_name || p.name;
        const image = p.preview_image || "";
        const description = p.short_description || "";

        const col = $(`
          <div class="col-md-3 col-sm-6" style="margin-bottom:20px;">
            <div class="card ui-preset-card" style="height:100%; display:flex; flex-direction:column;">
              ${
                image
                  ? `<img src="${image}" class="card-img-top" style="height:150px;object-fit:cover;">`
                  : `<div style="height:150px;display:flex;align-items:center;justify-content:center;background:#f5f5f5;">
                       <span class="text-muted">${__("No Preview")}</span>
                     </div>`
              }
              <div class="card-body d-flex flex-column">
                <h6 class="card-title mb-2">${frappe.utils.escape_html(title)}</h6>
                <p class="text-muted small flex-grow-1">
                  ${frappe.utils.escape_html(description)}
                </p>
                <button class="btn btn-primary btn-sm apply-btn">
                  ${__("Apply")}
                </button>
              </div>
            </div>
          </div>
        `);

        col.find(".apply-btn").on("click", async function () {
          frappe.show_alert({ message: __("Applying preset..."), indicator: "blue" });

          try {
            await frappe.call({
              method: "galaxy_ui.api.theme.apply_preset",
              args: { preset_name: p.name },
            });

            frappe.show_alert({ message: __("Preset applied"), indicator: "green" });

            // Simple full reload for now (safe + guaranteed)
            setTimeout(() => {
              window.location.reload();
            }, 800);

          } catch (e) {
            frappe.msgprint({
              title: __("Error"),
              message: __("Failed to apply preset"),
              indicator: "red",
            });
            console.error(e);
          }
        });

        grid.append(col);
      });

    } catch (e) {
      grid.html(`<div class="text-danger">${__("Failed to load presets.")}</div>`);
      console.error(e);
    }
  }
};

// frappe.pages["ui_preset_selector"].on_page_load = function (wrapper) {
//   const page = frappe.ui.make_app_page({
//     parent: wrapper,
//     title: __("UI Presets"),
//     single_column: true,
//   });
// frappe.pages["ui_preset_selector"].on_page_load = function (wrapper) {
//   const page = frappe.ui.make_app_page({
//     parent: wrapper,
//     title: __("UI Presets"),
//     single_column: true,
//   });

//   const $body = $(page.body);

//   $body.html(`
//     <div class="ui-preset-selector">
//       <div class="ui-presets-grid row"></div>
//     </div>
//   `);

//   load_presets();

//   async function load_presets() {
//     const grid = $body.find(".ui-presets-grid");
//     grid.html(`<div class="text-muted">${__("Loading...")}</div>`);

//     try {
//       const r = await frappe.call({
//         method: "galaxy_ui.api.theme.list_presets",
//       });

//       const presets = r.message || [];
//       grid.empty();

//       if (!presets.length) {
//         grid.html(`<div class="text-muted">${__("No presets found.")}</div>`);
//         return;
//       }

//       presets.forEach(p => {
//         const title =
//           p.title ||
//           p.preset_title ||
//           p.name;

//         const image =
//           p.image ||
//           p.preview_image ||
//           p.thumbnail ||
//           "";

//         const col = $(`
//           <div class="col-md-3 col-sm-6" style="margin-bottom:15px;">
//             <div class="card ui-preset-card" data-name="${p.name}" style="cursor:pointer;">
//               ${
//                 image
//                   ? `<img src="${image}" class="card-img-top" style="height:150px;object-fit:cover;">`
//                   : `<div style="height:150px;display:flex;align-items:center;justify-content:center;background:#f5f5f5;">
//                        <span class="text-muted">${__("No Preview")}</span>
//                      </div>`
//               }
//               <div class="card-body">
//                 <h6 class="card-title" style="margin-bottom:0;">${frappe.utils.escape_html(title)}</h6>
//               </div>
//             </div>
//           </div>
//         `);

//         grid.append(col);
//       });
//     } catch (e) {
//       grid.html(`<div class="text-danger">${__("Failed to load presets.")}</div>`);
//       console.error(e);
//     }
//   }
// };
// frappe.pages["ui_preset_selector"].on_page_load = function (wrapper) {
//   const page = frappe.ui.make_app_page({
//     parent: wrapper,
//     title: __("UI Presets"),
//     single_column: true,
//   });

//   const $body = $(page.body);

//   $body.html(`
//     <div class="ui-preset-selector">
//       <div class="ui-presets-grid row"></div>
//     </div>
//   `);

//   load_presets();

//   async function load_presets() {
//     const grid = $body.find(".ui-presets-grid");
//     grid.html(`<div class="text-muted">${__("Loading...")}</div>`);

//     try {
//       const r = await frappe.call({
//         method: "galaxy_ui.api.theme.list_presets",
//       });

//       const presets = r.message || [];
//       grid.empty();

//       if (!presets.length) {
//         grid.html(`<div class="text-muted">${__("No presets found.")}</div>`);
//         return;
//       }

//       presets.forEach(p => {
//         const title =
//           p.title ||
//           p.preset_title ||
//           p.name;

//         const image =
//           p.image ||
//           p.preview_image ||
//           p.thumbnail ||
//           "";

//         const col = $(`
//           <div class="col-md-3 col-sm-6" style="margin-bottom:15px;">
//             <div class="card ui-preset-card" data-name="${p.name}" style="cursor:pointer;">
//               ${
//                 image
//                   ? `<img src="${image}" class="card-img-top" style="height:150px;object-fit:cover;">`
//                   : `<div style="height:150px;display:flex;align-items:center;justify-content:center;background:#f5f5f5;">
//                        <span class="text-muted">${__("No Preview")}</span>
//                      </div>`
//               }
//               <div class="card-body">
//                 <h6 class="card-title" style="margin-bottom:0;">${frappe.utils.escape_html(title)}</h6>
//               </div>
//             </div>
//           </div>
//         `);

//         grid.append(col);
//       });
//     } catch (e) {
//       grid.html(`<div class="text-danger">${__("Failed to load presets.")}</div>`);
//       console.error(e);
//     }
//   }
// };
// frappe.pages["ui_preset_selector"].on_page_load = function (wrapper) {
//   const page = frappe.ui.make_app_page({
//     parent: wrapper,
//     title: __("UI Presets"),
//     single_column: true,
//   });

//   const $body = $(page.body);

//   $body.html(`
//     <div class="ui-preset-selector">
//       <div class="ui-presets-grid row"></div>
//     </div>
//   `);

//   load_presets();

//   async function load_presets() {
//     const grid = $body.find(".ui-presets-grid");
//     grid.html(`<div class="text-muted">${__("Loading...")}</div>`);

//     try {
//       const r = await frappe.call({
//         method: "galaxy_ui.api.theme.list_presets",
//       });

//       const presets = r.message || [];
//       grid.empty();

//       if (!presets.length) {
//         grid.html(`<div class="text-muted">${__("No presets found.")}</div>`);
//         return;
//       }

//       presets.forEach(p => {
//         const title =
//           p.title ||
//           p.preset_title ||
//           p.name;

//         const image =
//           p.image ||
//           p.preview_image ||
//           p.thumbnail ||
//           "";

//         const col = $(`
//           <div class="col-md-3 col-sm-6" style="margin-bottom:15px;">
//             <div class="card ui-preset-card" data-name="${p.name}" style="cursor:pointer;">
//               ${
//                 image
//                   ? `<img src="${image}" class="card-img-top" style="height:150px;object-fit:cover;">`
//                   : `<div style="height:150px;display:flex;align-items:center;justify-content:center;background:#f5f5f5;">
//                        <span class="text-muted">${__("No Preview")}</span>
//                      </div>`
//               }
//               <div class="card-body">
//                 <h6 class="card-title" style="margin-bottom:0;">${frappe.utils.escape_html(title)}</h6>
//               </div>
//             </div>
//           </div>
//         `);

//         grid.append(col);
//       });
//     } catch (e) {
//       grid.html(`<div class="text-danger">${__("Failed to load presets.")}</div>`);
//       console.error(e);
//     }
//   }
// };

//   const $body = $(page.body);
//   $body.html(`
//     <div class="ui-preset-selector">
//       <div class="text-muted">${__("Preset selector UI will be rendered here (cards + preview + apply).")}</div>
//       <div style="margin-top: 10px;">
//         <button class="btn btn-primary ui-load-presets">${__("Load Presets (stub)")}</button>
//       </div>
//       <div class="ui-presets-out" style="margin-top: 15px;"></div>
//     </div>
//   `);

//   $body.on("click", ".ui-load-presets", async () => {
//     // Stub: next step we will add API to fetch UI Preset list + preview images
//     const out = $body.find(".ui-presets-out");
//     out.empty().append(`<pre>${__("Next: implement API endpoint + card grid renderer")}</pre>`);
//   });
// };

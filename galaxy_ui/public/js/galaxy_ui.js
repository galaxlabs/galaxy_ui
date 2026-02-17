window.__galaxy_ui_js_loaded = (window.__galaxy_ui_js_loaded || 0) + 1;
console.log("[GalaxyUI] galaxy_ui.js loaded", window.__galaxy_ui_js_loaded);

(function () {
  const STYLE_ID = "galaxy-ui-theme";
  const MODE_KEY = "galaxy_ui_mode";
  const API = "/api/method/galaxy_ui.api.theme.get_active_theme";

  function ensureStyleTag() {
    let tag = document.getElementById(STYLE_ID);
    if (!tag) {
      tag = document.createElement("style");
      tag.id = STYLE_ID;
      (document.head || document.documentElement).appendChild(tag);
    }
    return tag;
  }

  function systemMode() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function setMode(mode) {
    document.documentElement.setAttribute("data-pt-mode", mode);
  }

  async function inject() {
    const tag = ensureStyleTag();

    try {
      const r = await fetch(API, { credentials: "same-origin", cache: "no-store" });
      const out = await r.json();
      const msg = out.message || {};

      tag.textContent = msg.css || "";

      const serverMode = String(msg.mode || "auto").toLowerCase();
      const saved = String(localStorage.getItem(MODE_KEY) || "").toLowerCase();

      if (saved === "light" || saved === "dark") setMode(saved);
      else if (serverMode === "light" || serverMode === "dark") setMode(serverMode);
      else setMode(systemMode());

      console.log("[GalaxyUI] injected", { len: tag.textContent.length, theme: msg.theme, mode: serverMode });
    } catch (e) {
      console.error("[GalaxyUI] inject failed:", e);
      setMode(systemMode());
    }
  }

  // Run when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inject);
  } else {
    inject();
  }
})();

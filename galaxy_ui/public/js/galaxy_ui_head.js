window.__galaxy_ui_head_loaded = (window.__galaxy_ui_head_loaded || 0) + 1;
console.log("[GalaxyUI] head.js loaded", window.__galaxy_ui_head_loaded);

(function () {
  const STYLE_ID = "galaxy-ui-theme";
  const MODE_KEY = "galaxy_ui_mode";
  const API = "/api/method/galaxy_ui.api.theme.get_active_theme";

  function ensureStyleTag() {
    let tag = document.getElementById(STYLE_ID);
    if (!tag) {
      tag = document.createElement("style");
      tag.id = STYLE_ID;
      document.head.appendChild(tag);
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

  async function boot() {
  const tag = ensureStyleTag();

  // MARKER: proves head.js executed
  document.documentElement.setAttribute("data-galaxy-ui-head", "1");

  try {
    const r = await fetch(API, { credentials: "same-origin", cache: "no-store" });
    const out = await r.json();
    const msg = out.message || {};

    const css = msg.css || "";
    tag.textContent = css;

    // watchdog: if cleared, re-apply for 30s
    const started = Date.now();
    const timer = setInterval(() => {
      if (Date.now() - started > 30000) return clearInterval(timer);
      if ((tag.textContent || "").length === 0 && css.length > 0) tag.textContent = css;
    }, 500);

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

  boot();
})();

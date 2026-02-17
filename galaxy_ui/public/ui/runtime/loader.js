/**
 * Global loader:
 * - fetch theme bundle
 * - set data-ui-mode
 * - inject tokens CSS
 * - optionally load layers (skin/cards/rules/tailwind) based on flags
 *
 * Put this file at:
 *   galaxy_ui/public/ui/runtime/loader.js
 */
(function () {
  const STYLE_ID = "ui-tokens-style";
  const MODE_KEY = "ui_mode_override"; // user override: light/dark/auto

  // -----------------------
  // Mode + CSS injection
  // -----------------------
  function setMode(mode) {
    document.documentElement.setAttribute("data-ui-mode", mode);
  }

  function setFlagAttr(attr, enabled) {
    if (enabled) document.documentElement.setAttribute(attr, "1");
    else document.documentElement.removeAttribute(attr);
  }

  // Normalize flags coming from server (can be 0/1, true/false, "0"/"1", etc.)
  function isOn(v) {
    return v === 1 || v === true || v === "1" || v === "true" || v === "yes" || v === "on";
  }

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function resolvedMode(bundleMode) {
    const override = localStorage.getItem(MODE_KEY);
    const m = (override || bundleMode || "auto").toLowerCase();
    if (m === "light" || m === "dark") return m;
    return systemPrefersDark() ? "dark" : "light";
  }

  function injectCss(cssText) {
    let el = document.getElementById(STYLE_ID);
    if (!el) {
      el = document.createElement("style");
      el.id = STYLE_ID;
      document.head.appendChild(el);
    }
    el.textContent = cssText || "";
  }

  // -----------------------
  // Dynamic layer loading
  // -----------------------
  function loadCss(url) {
    return new Promise((resolve, reject) => {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = url;
      link.onload = resolve;
      link.onerror = reject;
      document.head.appendChild(link);
    });
  }

  function loadJs(url) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = url;
      s.defer = true;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  // -----------------------
  // Wait for frappe.call
  // -----------------------
  function waitForFrappeCall(cb) {
    const started = Date.now();
    const timer = setInterval(() => {
      if (window.frappe && typeof frappe.call === "function") {
        clearInterval(timer);
        cb();
        return;
      }
      // stop after 10s to avoid infinite loop
      if (Date.now() - started > 10000) {
        clearInterval(timer);
        console.warn("[UI Loader] frappe.call not ready");
      }
    }, 200);
  }

  // -----------------------
  // Main loader
  // -----------------------
  async function main() {
    // IMPORTANT: this must exist server-side as a whitelisted method
    // galaxy_ui/api/theme.py -> get_active_theme_bundle
    const r = await frappe.call("galaxy_ui.api.theme.get_active_theme_bundle");
    const bundle = r && r.message ? r.message : {};

    // 1) Mode + tokens
    const mode = resolvedMode(bundle.mode);
    setMode(mode);
    injectCss(bundle.css_tokens);

    // Auto mode: live update on system theme change (only if no manual override)
    const override = localStorage.getItem(MODE_KEY);
    if (!override || override === "auto") {
      const mq = window.matchMedia("(prefers-color-scheme: dark)");
      if (mq && mq.addEventListener) {
        mq.addEventListener("change", () => setMode(systemPrefersDark() ? "dark" : "light"));
      }
    }

    // 2) Optional layers (loaded only if enabled by theme flags)
    const flags = bundle.flags || {};
    const base = "/assets/galaxy_ui/ui";

    try {
      const skinOn = isOn(flags.skin);
      const cardsOn = isOn(flags.cards);
      const rulesOn = isOn(flags.rules);
      const tailwindOn = isOn(flags.tailwind);

      // Toggle DOM attributes for CSS scoping (non-invasive by default)
      setFlagAttr("data-ui-skin", skinOn);
      setFlagAttr("data-ui-cards", cardsOn);
      setFlagAttr("data-ui-rules", rulesOn);
      setFlagAttr("data-ui-tailwind", tailwindOn);

      if (tailwindOn) await loadCss(`${base}/dist/tw-scoped.css?hash=${bundle.hash}`);
      if (skinOn) await loadCss(`${base}/styles/skin.css?hash=${bundle.hash}`);
      if (rulesOn) await loadJs(`${base}/runtime/rules.js?hash=${bundle.hash}`);
      if (cardsOn) await loadJs(`${base}/runtime/cards.js?hash=${bundle.hash}`);
    } catch (e) {
      // Don't break Desk if optional layers fail.
      console.warn("[UI Loader] Optional layer failed:", e);
    }
  }

  // Start after DOM is ready, but also wait for frappe.call to exist
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => waitForFrappeCall(main));
  } else {
    waitForFrappeCall(main);
  }
})();

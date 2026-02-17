#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   1) cd to your app root (where setup.py / pyproject.toml exists), e.g.:
#        cd ~/frappe-bench/apps/galaxy_ui
#   2) run:
#        bash ./scripts/init_ui_system_structure.sh
#
# This script ONLY creates folders + placeholder files (safe to re-run).

APP_PKG="${1:-galaxy_ui}"   # python package folder name inside the app (default: galaxy_ui)

ROOT="$(pwd)"
PKG_DIR="$ROOT/$APP_PKG"

if [[ ! -d "$PKG_DIR" ]]; then
  echo "ERROR: Package folder not found: $PKG_DIR"
  echo "Hint: run from app root, or pass the package folder name:"
  echo "  bash scripts/init_ui_system_structure.sh <package_folder>"
  exit 1
fi

mkdir -p "$ROOT/scripts"
mkdir -p "$PKG_DIR/core" "$PKG_DIR/api" "$PKG_DIR/doctype"
mkdir -p "$PKG_DIR/public/ui/runtime" "$PKG_DIR/public/ui/styles" "$PKG_DIR/public/ui/dist"

touch "$PKG_DIR/core/__init__.py" "$PKG_DIR/api/__init__.py"

# --- core layer (pure python) ---
cat > "$PKG_DIR/core/tokens.py" <<'PY'
"""
Token engine: normalize tokens and generate CSS variables (light/dark).
Keep this file pure-Python (no frappe import), so it remains testable.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class Token:
    name: str         # e.g. --ui-primary
    light: str        # e.g. #3b82f6
    dark: str         # e.g. #60a5fa
    type: str = "color"


def css_escape(s: str) -> str:
    return (s or "").strip()


def generate_tokens_css(tokens: Iterable[Token], dark_selector: str = 'html[data-ui-mode="dark"]') -> str:
    """
    Output:
      :root{--ui-...:...}
      html[data-ui-mode="dark"]{--ui-...:...}
    """
    t: List[Token] = [x for x in tokens if x and x.name]
    light_lines = []
    dark_lines = []
    for x in t:
        name = css_escape(x.name)
        light_lines.append(f"{name}:{css_escape(x.light)};")
        dark_lines.append(f"{name}:{css_escape(x.dark)};")

    light_block = ":root{" + "".join(light_lines) + "}"
    dark_block = f'{dark_selector}' + "{" + "".join(dark_lines) + "}"
    return light_block + "\n" + dark_block
PY

cat > "$PKG_DIR/core/bundle.py" <<'PY'
"""
Bundle helpers: compute hash/version and assemble payload for the runtime loader.
"""
from __future__ import annotations
import hashlib


def bundle_hash(*parts: str) -> str:
    raw = "\n".join([p or "" for p in parts]).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]
PY

# --- API layer (frappe whitelisted endpoints only) ---
cat > "$PKG_DIR/api/theme.py" <<'PY'
from __future__ import annotations
import frappe
from frappe import _

from ..core.bundle import bundle_hash


@frappe.whitelist()
def get_active_theme_bundle():
    """
    Contract for the client runtime loader.
    Return only data + CSS (no HTML).
    """
    # TODO: Replace with your UI Theme DocType lookup logic
    mode = "auto"  # auto|light|dark
    flags = {"skin": 0, "cards": 0, "rules": 0, "tailwind": 0}

    css_tokens = ""  # generated CSS variables
    css_components = ""  # optional components css (if you decide to serve it)
    h = bundle_hash(mode, str(flags), css_tokens, css_components)

    return {
        "mode": mode,
        "flags": flags,
        "css_tokens": css_tokens,
        "hash": h,
    }
PY

cat > "$PKG_DIR/api/publish.py" <<'PY'
from __future__ import annotations
import frappe


@frappe.whitelist()
def publish_theme(name: str):
    """
    Optional endpoint later:
    - mark theme active
    - generate/cache dist assets
    """
    frappe.only_for("System Manager")
    # TODO: implement
    return {"ok": True, "theme": name}
PY

# --- public runtime (JS) ---
cat > "$PKG_DIR/public/ui/runtime/loader.js" <<'JS'
/**
 * Global loader:
 * - fetch theme bundle
 * - set data-ui-mode
 * - inject tokens CSS
 * - optionally load layers (skin/cards/rules/tailwind) based on flags
 */
(function () {
  const STYLE_ID = "ui-tokens-style";
  const MODE_KEY = "ui_mode_override"; // user override: light/dark/auto

  function setMode(mode) {
    document.documentElement.setAttribute("data-ui-mode", mode);
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

  async function main() {
    if (!window.frappe || !frappe.call) return;

    const r = await frappe.call("galaxy_ui.api.theme.get_active_theme_bundle");
    const bundle = r && r.message ? r.message : {};

    const mode = resolvedMode(bundle.mode);
    setMode(mode);
    injectCss(bundle.css_tokens);

    // If mode is auto (no override), listen for system changes.
    const override = localStorage.getItem(MODE_KEY);
    if (!override || override === "auto") {
      const mq = window.matchMedia("(prefers-color-scheme: dark)");
      if (mq && mq.addEventListener) {
        mq.addEventListener("change", () => setMode(systemPrefersDark() ? "dark" : "light"));
      }
    }

    // Optional layers (later)
    const flags = bundle.flags || {};
    const base = "/assets/galaxy_ui/ui"; // built assets path

    try {
      if (flags.tailwind) await loadCss(`${base}/dist/tw-scoped.css?hash=${bundle.hash}`);
      if (flags.skin) await loadCss(`${base}/styles/skin.css?hash=${bundle.hash}`);
      if (flags.rules) await loadJs(`${base}/runtime/rules.js?hash=${bundle.hash}`);
      if (flags.cards) await loadJs(`${base}/runtime/cards.js?hash=${bundle.hash}`);
    } catch (e) {
      // Keep silent to avoid breaking Desk. Use console for debugging.
      console.warn("[UI Loader] Optional layer failed:", e);
    }
  }

  // Run after frappe boot
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
JS

cat > "$PKG_DIR/public/ui/runtime/rules.js" <<'JS'
// Placeholder: UI Rule engine (list rows/cards/forms)
// Will be implemented step-by-step.
JS

cat > "$PKG_DIR/public/ui/runtime/cards.js" <<'JS'
// Placeholder: ListView Card View renderer + toggle
// Will be implemented step-by-step.
JS

# --- public styles ---
cat > "$PKG_DIR/public/ui/styles/base.css" <<'CSS'
/* Safe base helpers only. No navbar/sidebar/background overrides here. */
:root{
  --ui-radius: 8px;
}
.ui-card{
  border-radius: var(--ui-radius);
}
CSS

cat > "$PKG_DIR/public/ui/styles/skin.css" <<'CSS'
/* OPTIONAL skin layer (should be enabled via flags.skin).
   Keep everything scoped to html[data-ui-skin="1"] to avoid changing backgrounds by default. */
html[data-ui-skin="1"] .navbar{
  /* example, will be filled later */
}
CSS

cat > "$PKG_DIR/public/ui/styles/components.css" <<'CSS'
/* OPTIONAL components layer (chips, badges, cards, etc.) */
CSS

# --- hooks.py patch note (create a minimal include snippet file) ---
cat > "$ROOT/scripts/hooks_snippet.txt" <<'TXT'
Add these to hooks.py (desk + web), step-by-step later:

app_include_css = [
  "/assets/galaxy_ui/ui/styles/base.css",
]

app_include_js = [
  "/assets/galaxy_ui/ui/runtime/loader.js",
]

website_include_css = [
  "/assets/galaxy_ui/ui/styles/base.css",
]

website_include_js = [
  "/assets/galaxy_ui/ui/runtime/loader.js",
]
TXT

echo "✅ UI System structure created under: $PKG_DIR"
echo "Next: we will wire hooks.py to include loader.js + base.css (safe)."
echo "Note: hooks snippet saved at: scripts/hooks_snippet.txt"

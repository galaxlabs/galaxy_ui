from __future__ import annotations

import json
import re

import frappe
from frappe.utils import cint


SCOPE_UI_PANEL = "UI Panel"
SCOPE_DESK = "Desk"
SCOPE_BOTH = "Both"
VALID_SCOPES = {SCOPE_UI_PANEL, SCOPE_DESK, SCOPE_BOTH}

_COMPONENT_ALIASES = {
    "topbar": "navbar",
    "listrow": "list_row",
    "list-row": "list_row",
    "pageshell": "page_shell",
}


def _safe_json(raw, default):
    if raw in (None, "", []):
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        parsed = json.loads(raw)
    except Exception:
        return default
    return parsed if isinstance(parsed, type(default)) else default


def _normalize_token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", (value or "").strip().lower())
    token = re.sub(r"_+", "_", token).strip("_")
    return token


def _normalize_component_name(raw_name: str) -> str:
    token = _normalize_token(raw_name)
    if token in _COMPONENT_ALIASES:
        return _COMPONENT_ALIASES[token]
    return token


def _normalize_var_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", (name or "").strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    if not cleaned:
        return ""
    if not cleaned.startswith("--"):
        cleaned = f"--{cleaned}"
    return cleaned


def validate_component_options_v1(raw_component_options) -> tuple[dict, list[str]]:
    warnings = []
    parsed = raw_component_options
    if isinstance(raw_component_options, str):
        text = raw_component_options.strip()
        if not text:
            parsed = {}
        else:
            try:
                parsed = json.loads(text)
            except Exception:
                return {}, ["Invalid component_options_json: expected valid JSON object"]
    else:
        parsed = _safe_json(raw_component_options, {})
    if not isinstance(parsed, dict):
        return {}, ["component_options_json must be a JSON object"]

    normalized = {}
    for component_key, config in parsed.items():
        comp = _normalize_component_name(str(component_key or ""))
        if not comp:
            warnings.append(f"Skipped empty component key: {component_key!r}")
            continue

        if isinstance(config, str):
            option_name = _normalize_token(config)
            if not option_name:
                warnings.append(f"Empty option value for component '{component_key}'")
                continue
            normalized[comp] = {"_direct_option": option_name}
            continue

        if not isinstance(config, dict):
            warnings.append(f"Component '{component_key}' must map to object or string")
            continue

        facet_map = {}
        for facet, value in config.items():
            facet_key = _normalize_token(str(facet or ""))
            facet_val = _normalize_token(str(value or ""))
            if not facet_key or not facet_val:
                warnings.append(f"Invalid facet '{facet}' for component '{component_key}'")
                continue
            facet_map[facet_key] = facet_val

        if facet_map:
            normalized[comp] = facet_map
        else:
            warnings.append(f"No valid facet options for component '{component_key}'")

    return normalized, warnings


def _component_catalog() -> dict:
    if not frappe.db.exists("DocType", "UI Component"):
        return {}
    rows = frappe.get_all(
        "UI Component",
        fields=["name", "component_name", "title", "enabled"],
        order_by="modified desc",
        limit_page_length=500,
    )
    catalog = {}
    for row in rows:
        if not cint(row.get("enabled") or 0):
            continue
        keys = {row.get("name"), row.get("component_name"), row.get("title")}
        for key in keys:
            token = _normalize_component_name(str(key or ""))
            if token and token not in catalog:
                catalog[token] = row.get("name")
    return catalog


def _candidate_option_names(facet_map: dict) -> list[str]:
    if "_direct_option" in facet_map:
        return [_normalize_token(facet_map["_direct_option"])]

    candidates = []
    variant = _normalize_token(facet_map.get("variant", ""))
    if variant:
        candidates.append(variant)

    for facet, value in sorted(facet_map.items()):
        if facet == "_direct_option":
            continue
        candidates.append(_normalize_token(f"{facet}_{value}"))
        candidates.append(_normalize_token(value))

    # Most specific combination candidate.
    pieces = [f"{k}_{v}" for k, v in sorted(facet_map.items()) if k != "_direct_option"]
    if pieces:
        candidates.insert(0, _normalize_token("_".join(pieces)))

    # De-duplicate while preserving order.
    seen = set()
    unique = []
    for cand in candidates:
        if not cand or cand in seen:
            continue
        seen.add(cand)
        unique.append(cand)
    return unique


def _fetch_component_option(component_name: str, candidates: list[str]):
    if not candidates:
        return None, None
    for candidate in candidates:
        names = frappe.get_all(
            "UI Component Option",
            filters={"component": component_name, "option_name": candidate, "enabled": 1},
            pluck="name",
            limit=1,
        )
        if names:
            return frappe.get_doc("UI Component Option", names[0]), candidate
    return None, None


def _extract_classes(classes_value) -> list[str]:
    out = []
    if isinstance(classes_value, str):
        for part in classes_value.split():
            part = part.strip()
            if part:
                out.append(part)
        return out

    if isinstance(classes_value, list):
        for part in classes_value:
            token = str(part or "").strip()
            if token:
                out.append(token)
        return out

    if isinstance(classes_value, dict):
        for _, value in classes_value.items():
            out.extend(_extract_classes(value))
        return out

    return out


def _semantic_classes(component_key: str, facet_map: dict) -> list[str]:
    classes = []
    variant = _normalize_token(facet_map.get("variant", ""))
    if variant:
        classes.append(f"ui-{component_key}-{variant}")
    for facet, value in sorted(facet_map.items()):
        if facet in {"_direct_option", "variant"}:
            continue
        classes.append(f"ui-{facet}-{value}")
    return classes


def resolve_layout_component_runtime(raw_component_options, apply_scope: str = SCOPE_UI_PANEL) -> dict:
    scope = (apply_scope or SCOPE_UI_PANEL).strip()
    if scope not in VALID_SCOPES:
        scope = SCOPE_UI_PANEL

    normalized, parse_warnings = validate_component_options_v1(raw_component_options)
    if not normalized:
        return {
            "apply_scope": scope,
            "css_vars": {},
            "classes": [],
            "warnings": parse_warnings,
            "matched": [],
            "unmatched": [],
        }

    if not frappe.db.exists("DocType", "UI Component Option"):
        return {
            "apply_scope": scope,
            "css_vars": {},
            "classes": [],
            "warnings": parse_warnings + ["UI Component Option DocType not found"],
            "matched": [],
            "unmatched": [{"component": k, "reason": "component_option_doctype_missing"} for k in normalized],
        }

    catalog = _component_catalog()
    css_vars = {}
    class_list = []
    matched = []
    unmatched = []
    warnings = list(parse_warnings)

    for component_key, facet_map in normalized.items():
        component_name = catalog.get(component_key)
        if not component_name:
            unmatched.append({"component": component_key, "reason": "component_not_found"})
            warnings.append(f"Unknown component '{component_key}'")
            continue

        candidates = _candidate_option_names(facet_map)
        option_doc, picked_candidate = _fetch_component_option(component_name, candidates)
        if not option_doc:
            unmatched.append({"component": component_key, "reason": "option_not_found", "candidates": candidates})
            warnings.append(f"No matching option for component '{component_key}'")
            class_list.extend(_semantic_classes(component_key, facet_map))
            continue

        option_css = _safe_json(option_doc.css_vars_json, {})
        if isinstance(option_css, dict):
            for key, value in option_css.items():
                var_name = _normalize_var_name(str(key or ""))
                if not var_name:
                    continue
                css_vars[var_name] = str(value if value is not None else "")

        option_classes = _safe_json(option_doc.classes_json, {})
        class_list.extend(_extract_classes(option_classes))
        class_list.extend(_semantic_classes(component_key, facet_map))

        matched.append(
            {
                "component": component_key,
                "component_name": component_name,
                "option_doc": option_doc.name,
                "option_name": option_doc.option_name,
                "matched_candidate": picked_candidate,
            }
        )

    # Stable class order without duplicates.
    deduped_classes = []
    seen = set()
    for cls in class_list:
        token = str(cls or "").strip()
        if not token or token in seen:
            continue
        seen.add(token)
        deduped_classes.append(token)

    return {
        "apply_scope": scope,
        "css_vars": css_vars,
        "classes": deduped_classes,
        "warnings": warnings,
        "matched": matched,
        "unmatched": unmatched,
    }


def resolve_layout_preset_runtime_doc(preset_doc, target_scope: str = SCOPE_UI_PANEL) -> dict:
    if not preset_doc:
        return {
            "preset_name": None,
            "preset_title": None,
            "apply_scope": SCOPE_UI_PANEL,
            "active_for_scope": 0,
            "css_vars": {},
            "classes": [],
            "warnings": ["No active layout preset"],
            "matched": [],
            "unmatched": [],
        }

    runtime = resolve_layout_component_runtime(
        raw_component_options=(preset_doc.component_options_json or ""),
        apply_scope=(preset_doc.apply_scope or SCOPE_UI_PANEL),
    )
    preset_scope = runtime.get("apply_scope") or SCOPE_UI_PANEL
    scope_norm = (target_scope or SCOPE_UI_PANEL).strip()
    active_for_scope = 1 if preset_scope in {SCOPE_BOTH, scope_norm} else 0
    if not active_for_scope:
        runtime = {
            **runtime,
            "css_vars": {},
            "classes": [],
            "warnings": list(runtime.get("warnings") or []) + [f"Layout scope '{preset_scope}' does not apply to '{scope_norm}'"],
        }

    return {
        "preset_name": preset_doc.name,
        "preset_title": preset_doc.title,
        "apply_scope": preset_scope,
        "active_for_scope": active_for_scope,
        **runtime,
    }

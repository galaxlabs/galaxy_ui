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

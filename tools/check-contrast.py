#!/usr/bin/env python3
"""WCAG contrast check for japandi-starter tokens.

Reads tokens.json (the single source of truth), resolves {category.name}
aliases, and asserts:
  - documented text/background pairs meet WCAG AA (4.5:1 for normal text)
  - non-text indicators (functional borders, focus ring) meet WCAG 1.4.11 (3:1)

Usage:  python3 tools/check-contrast.py
Exit 0 when every pair passes, 1 otherwise.
"""
import json
import re
import sys
from pathlib import Path

TOKENS_JSON = Path(__file__).resolve().parent.parent / "tokens.json"

# (label, foreground token, background token, minimum ratio)
PAIRS = [
    # Body text (WCAG AA 4.5:1)
    ("ink on paper",       "ink",           "paper",   4.5),
    ("ink on surface",     "ink",           "surface", 4.5),
    ("ink-soft on paper",  "ink-soft",      "paper",   4.5),
    ("ink-soft on surface","ink-soft",      "surface", 4.5),
    # Text-bearing accent fills (buttons, badges)
    ("paper on sage-deep", "paper",         "sage-deep", 4.5),
    ("paper on rust-deep", "paper",         "rust-deep", 4.5),
    # Stone's documented role: paired with dark, never light text on light bg
    ("ink on stone",       "ink",           "stone",   4.5),
    ("stone on ink",       "stone",         "ink",     4.5),
    # Non-text: functional borders and focus indicator (WCAG 1.4.11, 3:1)
    ("border-strong on paper",   "border-strong", "paper",   3.0),
    ("border-strong on surface", "border-strong", "surface", 3.0),
    ("focus ring on paper",      "focus-color",   "paper",   3.0),
    ("focus ring on surface",    "focus-color",   "surface", 3.0),
]


def load_tokens():
    data = json.loads(TOKENS_JSON.read_text())
    flat = {}
    for category, group in data.items():
        if category.startswith("$") or not isinstance(group, dict):
            continue
        for name, token in group.items():
            if name.startswith("$"):
                continue
            flat[name] = (category, token["$value"])
    return flat


def resolve(flat, value):
    seen = set()
    while True:
        m = re.fullmatch(r"\{([\w-]+)\.([\w-]+)\}", value.strip())
        if not m or value in seen:
            break
        seen.add(value)
        category, name = m.group(1), m.group(2)
        if name not in flat or flat[name][0] != category:
            raise SystemExit(f"unresolvable alias: {value}")
        value = flat[name][1]
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value.strip()):
        raise SystemExit(f"non-color value in contrast pair: {value}")
    return value.strip()


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(rgb):
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    l1, l2 = luminance(hex_to_rgb(fg)), luminance(hex_to_rgb(bg))
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def main():
    flat = load_tokens()
    needed = {name for _, fg, bg, _ in PAIRS for name in (fg, bg)}
    tokens = {name: resolve(flat, flat[name][1]) for name in needed}

    failures = 0
    print(f"{'pair':<24}{'fg':<10}{'bg':<10}{'ratio':<8}min   result")
    print("-" * 66)
    for label, fg_name, bg_name, minimum in PAIRS:
        try:
            fg, bg = tokens[fg_name], tokens[bg_name]
        except KeyError as e:
            print(f"{label:<24}{'--':<10}{'--':<10}{'--':<8}{minimum}  MISSING TOKEN {e}")
            failures += 1
            continue
        r = ratio(fg, bg)
        ok = r >= minimum
        failures += not ok
        print(f"{label:<24}{fg:<10}{bg:<10}{r:<8.2f}{minimum}  {'PASS' if ok else 'FAIL'}")

    print("-" * 66)
    if failures:
        print(f"{failures} pair(s) below their minimum.")
        return 1
    print("All pairs pass (4.5:1 text, 3:1 non-text).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

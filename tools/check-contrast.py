#!/usr/bin/env python3
"""WCAG contrast check for japandi-starter tokens.

Parses --jpd-* hex tokens from tokens.css and asserts the documented
text/background pairs meet WCAG AA (4.5:1 for normal text).

Usage:  python3 tools/check-contrast.py
Exit 0 when every pair passes, 1 otherwise.
"""
import re
import sys
from pathlib import Path

TOKENS_CSS = Path(__file__).resolve().parent.parent / "tokens.css"

# (label, foreground token, background token, minimum ratio)
PAIRS = [
    # Body text
    ("ink on paper",       "ink",       "paper",   4.5),
    ("ink on surface",     "ink",       "surface", 4.5),
    ("ink-soft on paper",  "ink-soft",  "paper",   4.5),
    ("ink-soft on surface","ink-soft",  "surface", 4.5),
    # Text-bearing accent fills (buttons, badges)
    ("paper on sage-deep", "paper",     "sage-deep", 4.5),
    ("paper on rust-deep", "paper",     "rust-deep", 4.5),
    # Stone's documented role: paired with dark, never light text on light bg
    ("ink on stone",       "ink",       "stone",   4.5),
    ("stone on ink",       "stone",     "ink",     4.5),
]


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
    css = TOKENS_CSS.read_text()
    tokens = dict(re.findall(r"--jpd-([\w-]+):\s*(#[0-9a-fA-F]{6})", css))

    failures = 0
    print(f"{'pair':<22}{'fg':<10}{'bg':<10}{'ratio':<8}min   result")
    print("-" * 64)
    for label, fg_name, bg_name, minimum in PAIRS:
        try:
            fg, bg = tokens[fg_name], tokens[bg_name]
        except KeyError as e:
            print(f"{label:<22}{'--':<10}{'--':<10}{'--':<8}{minimum}  MISSING TOKEN {e}")
            failures += 1
            continue
        r = ratio(fg, bg)
        ok = r >= minimum
        failures += not ok
        print(f"{label:<22}{fg:<10}{bg:<10}{r:<8.2f}{minimum}  {'PASS' if ok else 'FAIL'}")

    print("-" * 64)
    if failures:
        print(f"{failures} pair(s) below WCAG AA.")
        return 1
    print("All pairs meet WCAG AA (4.5:1).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

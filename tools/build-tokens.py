#!/usr/bin/env python3
"""Build generated files from tokens.json (the single source of truth).

Reads tokens.json and regenerates:
  - tokens.css            (:root custom properties)
  - tailwind.preset.js    (Tailwind v3 preset)
  - example/index.html    (its inlined :root token block only)

Usage:  python3 tools/build-tokens.py
Design decisions live in tokens.json. Presentational rules that live here:
  - Tailwind color nesting: `ink-soft` nests as ink.soft because `ink` exists
    as a color token; the base becomes DEFAULT. Same for sage-deep/rust-deep
    and border-strong.
  - fontSize line heights: text-xs/sm/base use leading-body; text-lg and up
    use leading-heading + tracking-heading.
  - The preset omits spacing and radius-full: both are identical to Tailwind's
    defaults, so emitting them would be noise.
  - Tailwind v4 theme (tailwind.v4.css): colors, fonts, type scale, radii,
    shadows and easings map to @theme namespaces. Motion durations, z-index
    and focus width/offset have no v4 theme namespace; v4 accepts them as
    bare values (duration-250, z-100, outline-2), so they are documented
    rather than emitted. Spacing and radius-full are omitted for the same
    reason as in the preset.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS_JSON = ROOT / "tokens.json"
TOKENS_CSS = ROOT / "tokens.css"
PRESET_JS = ROOT / "tailwind.preset.js"
V4_CSS = ROOT / "tailwind.v4.css"
EXAMPLE_HTML = ROOT / "example" / "index.html"

# Presentational order of categories in generated files.
CATEGORY_ORDER = ["color", "type", "space", "radius", "shadow",
                  "motion", "z", "focus"]

CSS_BANNER = """/* ==========================================================================
   japandi-starter - design tokens
   Warm, quiet, natural. Japanese restraint meets Scandinavian warmth.
   GENERATED from tokens.json - do not edit by hand.
   Edit tokens.json, then run: python3 tools/build-tokens.py
   ========================================================================== */"""

PRESET_HEADER = """/**
 * japandi-starter - Tailwind preset
 * Consumes the same tokens as tokens.json.
 * GENERATED - do not edit by hand. Edit tokens.json, then run:
 *   python3 tools/build-tokens.py
 *
 * Usage:
 *   // tailwind.config.js
 *   module.exports = {
 *     presets: [require('./tailwind.preset.js')],
 *     content: ['./src/*.{html,js,jsx,ts,tsx,vue,svelte}'],
 *   }
 *
 * Colors are literal values (not var() references) so opacity modifiers
 * like bg-sage/50 keep working.
 */"""


def load_tokens():
    data = json.loads(TOKENS_JSON.read_text())
    flat = {}   # name -> dict(category, type, value, description)
    ordered = []  # (category, section_title, name) in output order
    for category in CATEGORY_ORDER:
        group = data[category]
        for section in group["$sections"]:
            for name in section["tokens"]:
                if name in flat:
                    raise SystemExit(f"duplicate token name across categories: {name}")
                token = group[name]
                flat[name] = {
                    "category": category,
                    "type": token["$type"],
                    "value": token["$value"],
                    "description": token.get("$description", ""),
                }
                ordered.append((category, section["title"], name))
    # Validate every alias up front: a broken {category.name} anywhere must
    # fail here, before anything is written.
    for name in flat:
        resolve_literal(flat, flat[name]["value"])
    return flat, ordered


def resolve_literal(flat, value):
    """Resolve {category.name} aliases to their literal value."""
    seen = set()
    while True:
        m = re.fullmatch(r"\{([\w-]+)\.([\w-]+)\}", value.strip())
        if not m or value in seen:
            break
        seen.add(value)
        ref = flat.get(m.group(2))
        if ref is None or ref["category"] != m.group(1):
            raise SystemExit(f"unresolvable alias: {value}")
        value = ref["value"]
    return value


def css_value(flat, name):
    """Value for tokens.css: aliases become var(--jpd-*) references."""
    value = flat[name]["value"]
    m = re.fullmatch(r"\{([\w-]+)\.([\w-]+)\}", value.strip())
    if m:
        return f"var(--jpd-{m.group(2)})"
    return value


def build_root_block(flat, ordered):
    lines = [":root {"]
    current_section = None
    name_width = max(len(f"  --jpd-{name}:") for _, _, name in ordered)
    for _, section_title, name in ordered:
        if section_title != current_section:
            if current_section is not None:
                lines.append("")
            lines.append(f"  /* ---- {section_title} ---- */")
            current_section = section_title
        field = f"  --jpd-{name}:".ljust(name_width + 1)
        value = css_value(flat, name)
        desc = flat[name]["description"]
        if not desc:
            lines.append(f"{field}{value};")
            continue
        first, *rest = desc.split("\n")
        head = f"{field}{value};  /* {first}"
        if not rest:
            lines.append(head + " */")
        else:
            lines.append(head)
            pad = " " * (len(head) - len(first))
            for i, cont in enumerate(rest):
                close = " */" if i == len(rest) - 1 else ""
                lines.append(f"{pad}{cont}{close}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def build_css(flat, ordered):
    return CSS_BANNER + "\n\n" + build_root_block(flat, ordered)


def js_key(key):
    return key if re.fullmatch(r"[A-Za-z_$][\w$]*", key) else f"'{key}'"


def build_colors(flat, ordered):
    """Ordered list of (key, value) with nesting for ink/sage/rust/border."""
    color_names = [n for c, _, n in ordered if c == "color"]
    nameset = set(color_names)
    subs = {}    # base -> [(subkey, value)]
    order = []
    for name in color_names:
        base, sep, sub = name.partition("-")
        if sep and base in nameset and base != name:
            subs.setdefault(base, []).append(
                (sub, resolve_literal(flat, flat[name]["value"])))
            continue
        order.append(name)
    result = []
    for key in order:
        if key in subs:
            baseval = resolve_literal(flat, flat[key]["value"])
            result.append((key, [("DEFAULT", baseval)] + subs[key]))
        else:
            result.append((key, resolve_literal(flat, flat[key]["value"])))
    return result


def parse_font_stack(value):
    return [p.strip().strip("'\"") for p in value.split(",")]


def build_preset(flat, ordered):
    colors = build_colors(flat, ordered)
    type_names = [n for c, _, n in ordered if c == "type"]
    tmap = {n: flat[n]["value"] for n in type_names}
    leading_body, leading_heading = tmap["leading-body"], tmap["leading-heading"]
    tracking_heading = tmap["tracking-heading"]

    lines = [PRESET_HEADER, "", "/** @type {import('tailwindcss').Config} */",
             "module.exports = {", "  theme: {", "    extend: {"]

    # colors
    lines.append("      colors: {")
    key_w = max(len(k) for k, _ in colors)
    for key, val in colors:
        if isinstance(val, list):
            lines.append(f"        {js_key(key).ljust(key_w)}: {{")
            sub_w = max(len(s) for s, _ in val)
            for sub, subval in val:
                lines.append(f"          {js_key(sub).ljust(sub_w)}: '{subval}',")
            lines.append("        },")
        else:
            lines.append(f"        {js_key(key).ljust(key_w)}: '{val}',")
    lines.append("      },")

    # fontFamily
    lines.append("      fontFamily: {")
    for fname, tname in (("sans", "font-sans"), ("serif", "font-serif")):
        stack = parse_font_stack(tmap[tname])
        inner = ", ".join(f"'{p}'" for p in stack)
        lines.append(f"        {fname.ljust(5)}: [{inner}],")
    lines.append("      },")

    # fontSize
    lines.append("      fontSize: {")
    sizes = [(n.split("-", 1)[1], tmap[n]) for n in type_names if n.startswith("text-")]
    key_w = max(len(k) for k, _ in sizes)
    for key, val in sizes:
        if key in ("xs", "sm", "base"):
            lines.append(f"        {js_key(key).ljust(key_w)}: ['{val}', {{ lineHeight: '{leading_body}' }}],")
        else:
            lines.append(f"        {js_key(key).ljust(key_w)}: ['{val}', {{ lineHeight: '{leading_heading}', letterSpacing: '{tracking_heading}' }}],")
    lines.append("      },")

    # borderRadius (skip full: identical to Tailwind default)
    lines.append("      borderRadius: {")
    for rname in ("radius-sm", "radius-md", "radius-lg"):
        key = rname.split("-", 1)[1]
        lines.append(f"        {key.ljust(2)}: '{flat[rname]['value']}',")
    lines.append("      },")

    # boxShadow
    lines.append("      boxShadow: {")
    for sname in ("shadow-sm", "shadow-md", "shadow-lg"):
        key = sname.split("-", 1)[1]
        lines.append(f"        {key.ljust(2)}: '{flat[sname]['value']}',")
    lines.append("      },")

    lines += ["    },", "  },", "  plugins: [],", "};", ""]
    return "\n".join(lines)


V4_BANNER = """/* ==========================================================================
   japandi-starter - Tailwind v4 theme
   Warm, quiet, natural. Japanese restraint meets Scandinavian warmth.
   GENERATED from tokens.json - do not edit by hand.
   Edit tokens.json, then run: python3 tools/build-tokens.py

   Usage (Tailwind v4):
     @import "tailwindcss";
     @import "./tailwind.v4.css";

   Notes:
   - Duration, z-index, and focus width/offset tokens have no Tailwind v4
     theme namespace; v4 accepts them as bare values instead: duration-250,
     z-100, outline-2, outline-offset-2.
   - --ease-out and --ease-in-out intentionally override Tailwind's defaults
     with this system's quieter curves.
   ========================================================================== */"""


def v4_value(flat, name):
    """Theme value for tailwind.v4.css: color aliases stay as var() refs."""
    value = flat[name]["value"]
    m = re.fullmatch(r"\{([\w-]+)\.([\w-]+)\}", value.strip())
    if m and m.group(1) == "color":
        return f"var(--color-{m.group(2)})"
    return resolve_literal(flat, value)


def v4_entries(flat, ordered):
    """(section, var, value) triples for the @theme block, in order."""
    entries = []
    tmap = {n: flat[n]["value"] for c, _, n in ordered if c == "type"}
    leading_body, leading_heading = tmap["leading-body"], tmap["leading-heading"]
    tracking_heading = tmap["tracking-heading"]

    for category, section_title, name in ordered:
        value = v4_value(flat, name)
        if category == "color":
            entries.append((section_title, f"--color-{name}", value))
        elif name == "focus-color":
            # Semantic alias: used as outline-focus for focus rings.
            entries.append((section_title, "--color-focus", value))
        elif name in ("font-sans", "font-serif"):
            entries.append((section_title, f"--font-{name.split('-', 1)[1]}", value))
        elif name.startswith("text-"):
            size = name.split("-", 1)[1]
            entries.append((section_title, f"--text-{size}", value))
            if size in ("xs", "sm", "base"):
                entries.append((section_title, f"--text-{size}--line-height", leading_body))
            else:
                entries.append((section_title, f"--text-{size}--line-height", leading_heading))
                entries.append((section_title, f"--text-{size}--letter-spacing", tracking_heading))
        elif category == "radius" and name != "radius-full":
            entries.append((section_title, f"--radius-{name.split('-', 1)[1]}", value))
        elif category == "shadow":
            entries.append((section_title, f"--shadow-{name.split('-', 1)[1]}", value))
        elif name in ("ease-out", "ease-in-out"):
            entries.append((section_title, f"--{name}", value))
        # space-*: identical to v4 defaults, omitted (same as the v3 preset).
        # duration-*, z-*, focus-width/offset: bare values in v4, not emitted.
    return entries


def build_v4_theme(flat, ordered):
    entries = v4_entries(flat, ordered)
    var_width = max(len(var) for _, var, _ in entries)
    lines = [V4_BANNER, "", "@theme {"]
    current_section = None
    for section_title, var, value in entries:
        if section_title != current_section:
            if current_section is not None:
                lines.append("")
            lines.append(f"  /* {section_title} */")
            current_section = section_title
        lines.append(f"  {var.ljust(var_width)}: {value};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def build_example_html(root_block):
    html = EXAMPLE_HTML.read_text()
    pattern = re.compile(r"^:root \{$.*?^}", re.MULTILINE | re.DOTALL)
    matches = pattern.findall(html)
    if len(matches) != 1:
        raise SystemExit(f"expected exactly 1 :root block in example, found {len(matches)}")
    return pattern.sub(lambda _: root_block.rstrip("\n"), html, count=1)


def main():
    flat, ordered = load_tokens()
    # Build everything in memory first: files are written only after all
    # outputs (including the example sync) succeed, so a failure never
    # leaves a partially-updated tree behind.
    root_block = build_root_block(flat, ordered)
    css_text = build_css(flat, ordered)
    preset_text = build_preset(flat, ordered)
    v4_text = build_v4_theme(flat, ordered)
    example_html = build_example_html(root_block)
    TOKENS_CSS.write_text(css_text)
    PRESET_JS.write_text(preset_text)
    V4_CSS.write_text(v4_text)
    EXAMPLE_HTML.write_text(example_html)
    print(f"tokens: {len(ordered)}")
    print(f"wrote {TOKENS_CSS.relative_to(ROOT)}")
    print(f"wrote {PRESET_JS.relative_to(ROOT)}")
    print(f"wrote {V4_CSS.relative_to(ROOT)}")
    print(f"synced :root block in {EXAMPLE_HTML.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())

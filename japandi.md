# Japandi style guide (for AI coding tools)

Drop this file into the context of Claude Code, Antigravity, Cursor, or any AI
coding tool when generating frontend. It steers every generation toward one
look: warm, quiet, natural. Japanese restraint, Scandinavian warmth.

If the project uses `tokens.css` or the Tailwind preset from this repo, prefer
those tokens over the literal values below. The values here are the fallback.

## Palette rules

- Backgrounds are warm whites, never pure white. Use `#F6F3EC` (paper) for
  pages and `#FBF9F4` (surface) for cards and raised panels. Never `#FFFFFF`.
- Text is soft warm black `#2C2823` (ink), never `#000000`. Secondary text is
  `#6B6357` (ink-soft).
- Neutrals run warm: sand `#E9E2D3`, clay `#D3C6B0`, stone `#A79C89`. If you
  need a gray, warm it. Cool grays and blue-grays are off-palette.
- One accent per view. Default accent is sage `#7C8471`. Rust `#B0795B` is the
  warm alternative for rare emphasis. Never use both at full strength in one
  screen, and never invent a third accent.
- Text on an accent fill must use the deep variant: `sage-deep` `#62685A`
  or `rust-deep` `#8A5A3E` behind paper text. Base sage/rust are decorative
  only with text (3.5:1 / 3.3:1 - below AA).
- Borders are hairlines: 1px, `#E2DACB`. Prefer spacing over borders; use a
  border only when separation by space fails.

## Whitespace philosophy

- Generous negative space is the design. When a layout feels empty, that is
  usually correct. Do not fill it.
- Separate sections with space (`--jpd-space-12` to `--jpd-space-24`, 48-96px)
  before reaching for dividers or cards.
- Inside components, padding beats margins; consistent rhythm beats variety.
  Stick to the 4px spacing scale.
- Narrow content columns: cap body text around 65-75 characters per line.

## Typography

- Sans for UI and body: Inter or the system stack. Serif (Fraunces or Georgia)
  is allowed for display headings only, when warmth helps - never for body.
- Base 16px, ratio 1.25. Body line-height 1.6, headings 1.2 with -0.01em
  tracking.
- Headings earn their size. One `3xl` per page. Most headings are `lg` or `xl`.
- Weight contrast over size contrast: a `base` semibold label above `base`
  regular text often beats jumping a size.

## Texture and contrast

- Everything is matte and muted. Contrast is quiet: text pairings pass
  WCAG AA (4.5:1), but nothing shouts. Verified by `tools/check-contrast.py`.
- Text-safe pairings: ink or ink-soft on paper/surface; paper on sage-deep
  or rust-deep; ink on stone, or stone on ink. Base sage, rust, and stone
  are decorative only - never put small text on them over a light background.
- Natural textures belong: wood, linen, paper, stone. In code that translates
  to warm solid fills and subtle tone-on-tone layering, not gradients.
- Elevation is soft: warm-tinted shadows at 5-8% opacity
  (`rgba(44,40,35,0.05-0.08)`), small blur, no colored or harsh shadows.

## Components

- Cards: surface background, radius 8px, `shadow-sm` or a 1px border - not
  both. Padding `space-6` to `space-8`.
- Buttons: primary is sage-deep fill with paper text (5.2:1), radius 8px.
  Secondary is transparent with a 1px border and ink text. No pill buttons
  except small tags/badges.
- Inputs: surface or paper background, 1px border, radius 4-8px, focus ring in
  sage at low opacity.
- Icons: thin stroke (1.5px), ink or ink-soft color, no filled multicolor icons.
  Stone is too light for icons on light backgrounds (2.4:1).

## What to avoid

- Pure white (`#FFFFFF`) backgrounds and pure black (`#000000`) text.
- Loud or saturated accent colors, neon anything, more than one accent per view.
- Heavy borders (anything over 1px), dark dividing lines, boxed-in layouts.
- Harsh, large, or colored shadows; glassmorphism; gradients as decoration.
- Rounded-everything: radii stay at 4-16px. No circular cards.
- Dense dashboards. If a screen needs density to work, group and space the
  groups instead of shrinking the gaps.

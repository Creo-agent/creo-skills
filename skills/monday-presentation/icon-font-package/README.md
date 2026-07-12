# Monday Icons Font Package

Drop-in replacement for the 270-file SVG Icons folder. Collapses all icons into **2 files** — solving the 200-file skill limit on Claude org-level skills.

## What's Inside

| File | Purpose | Size |
|------|---------|------|
| `icon-font.css` | `@font-face` with base64-embedded WOFF2 + `.monday-icon` base class | ~145 KB |
| `ICON_FONT_REFERENCE.md` | LLM reference — every icon name, unicode entity, and semantic tags | ~22 KB |
| `monday-icons.woff2` | Standalone font file (also embedded in the CSS as base64) | ~108 KB |
| `README.md` | This file (not needed in the skill) | — |

## What It Replaces

| Before (SVG system) | After (font system) |
|------------------------|---------------------|
| `Icons/` folder — 270 SVG files | `icon-font.css` — 1 file, 268 icons |
| `ICON_MATCHING.md` — icon selection guide | `ICON_FONT_REFERENCE.md` — combined reference + selection |
| `ICON_GUIDE.md` — icon usage guide | Merged into `ICON_FONT_REFERENCE.md` |

**File count reduction**: 272 files → 2 files (**270 fewer files**)

---

## Integration Guide

### Step 1: Add files to the skill

Copy `icon-font.css` and `ICON_FONT_REFERENCE.md` into the skill root directory.

### Step 2: Remove old icon files

Delete the `Icons/` folder, `ICON_MATCHING.md`, and `ICON_GUIDE.md` from the skill.

### Step 3: Update CSS inlining order

Generated presentations are single self-contained HTML files with all CSS inlined in `<style>` blocks. The inlining order is critical — `icon-font.css` must come **FIRST** because `design-system.css` references `.monday-icon` to add size/color rules on top of the base class:

```html
<style>
  /* 1. ICON FONT — inline icon-font.css here FIRST */
  @font-face { ... }
  .monday-icon { ... }

  /* 2. DESIGN SYSTEM — inline design-system.css here SECOND */
  :root { ... }
  .monday-icon { display: inline-block; ... }  /* extends the base */
  .ds-icon-xs { ... }
  ...
</style>
```

If `design-system.css` is inlined first, the `.monday-icon` base class (font-family, font-style, etc.) won't exist yet, and icons may render as squares or use the wrong font.

### Step 4: Update design-system.css icon section

Replace the old SVG-based icon classes with font-based ones. The icon section in `design-system.css` has two parts:

**Part 1 — Icon tokens** (in `:root`):
```css
:root {
  --icon-xs: 3vmin;
  --icon-sm: 5vmin;
  --icon-md: 7vmin;
  --icon-lg: 10vmin;
  --icon-xl: 15vmin;
}
```

**Part 2 — Icon classes** (after the color utilities):
```css
/* ============================================
   ICONS (Icon Font)
   .monday-icon base class and @font-face are
   defined in icon-font.css — inline that file
   alongside this one.
   ============================================ */

.monday-icon {
  display: inline-block;
  flex-shrink: 0;
  font-size: var(--icon-md);
}

.ds-icon-xs { font-size: var(--icon-xs); }
.ds-icon-sm { font-size: var(--icon-sm); }
.ds-icon-md { font-size: var(--icon-md); }
.ds-icon-lg { font-size: var(--icon-lg); }
.ds-icon-xl { font-size: var(--icon-xl); }

.ds-icon-white { color: #ffffff; }
.ds-icon-dark  { color: #323338; }
.ds-icon-brand { color: var(--color-purple); }
.ds-icon-muted { opacity: 0.6; }
```

**Part 3 — Light theme icon overrides** (inside the light theme section at the bottom of `design-system.css`):
```css
/* Icons: ds-icon-white renders white on dark, dark on light — no HTML changes needed */
[data-theme="light"] .ds-icon-white { color: var(--color-text); }
[data-theme="light"] .ds-icon-dark  { color: #ffffff; }
```

These overrides automatically invert `.ds-icon-white` and `.ds-icon-dark` on light-theme slides so the developer never needs to change HTML between themes.

### Step 5: Add the Poppins font-family lockdown override

The skill uses a Poppins font lockdown that forces every element to use Poppins:

```css
html, body, h1, h2, h3, h4, h5, h6, p, span, div, li, a, button, input, textarea,
.slide-container, .slide-container * {
  font-family: 'Poppins', sans-serif !important;
}
```

**This breaks icon rendering** because `.slide-container *` matches `.monday-icon` elements and overrides their `font-family: "MondayIcons"` declaration — both have `!important`, but the wildcard selector wins because it appears later in the cascade.

**You MUST add this override immediately after the lockdown rule:**

```css
/* Icon font override — must come AFTER the Poppins lockdown above */
.slide-container .monday-icon {
  font-family: "MondayIcons" !important;
  font-style: normal !important;
}
```

The higher specificity (`.slide-container .monday-icon` vs `.slide-container *`) ensures icons use the MondayIcons font instead of Poppins. Without this rule, all icons render as empty rectangles or wrong characters.

### Step 6: Update HTML icon pattern

**Old approach** (SVG inlining):
```html
<svg class="ds-icon ds-icon-sm ds-icon-white" viewBox="0 0 60 60" fill="none">
  <path d="..."/>
</svg>
```

**New approach** (icon font):
```html
<span class="monday-icon ds-icon-sm ds-icon-white">&#xf096;</span>
```

### Step 7: Update SKILL.md workflow

Replace any step that says "Read the SVG file and inline it" with:

> Look up the icon in `ICON_FONT_REFERENCE.md`, find its HTML entity, and use:
> `<span class="monday-icon {size} {color}">&#x{code};</span>`

---

## Icon Color System

### Monochrome font — glyphs inherit CSS `color`

The WOFF2 has been stripped of COLR/CPAL color tables. All glyphs are monochrome and inherit the CSS `color` property, just like regular text.

**Why this was necessary:** The original IcoMoon export included COLR/CPAL tables with hardcoded purple (#6161FF) colors baked into every glyph. With those tables present, CSS `color` has **no effect** — icons always render purple regardless of what color class you apply. We used `fonttools` (Python) to strip the COLR and CPAL tables from the WOFF2, making the font behave like a standard monochrome icon font where glyphs respond to CSS `color`.

**If you ever regenerate the font from IcoMoon**, you must strip the color tables again. The command is:

```bash
pip install fonttools brotli
python3 -c "
from fontTools.ttLib import TTFont
font = TTFont('monday-icons.woff2')
for table in ['COLR', 'CPAL']:
    if table in font:
        del font[table]
font.save('monday-icons.woff2')
"
```

### Color modifier classes

All icon coloring uses the CSS `color` property, applied through these classes:

| Class | CSS | Use case |
|-------|-----|----------|
| `.ds-icon-white` | `color: #ffffff` | Icons on dark or colored backgrounds |
| `.ds-icon-dark` | `color: #323338` | Icons on light/yellow/colored card backgrounds |
| `.ds-icon-brand` | `color: var(--color-purple)` | Brand-colored accent icons |
| `.ds-icon-muted` | `opacity: 0.6` | De-emphasized/secondary icons |
| _(no class)_ | `color: currentColor` | Inherits from parent text color |

### `.ds-icon-dark` — hardcoded value, NOT a theme variable

```css
.ds-icon-dark { color: #323338; }  /* Always dark, regardless of theme */
```

**Critical:** Do NOT use `color: var(--color-text)` for `.ds-icon-dark`. On dark themes, `--color-text` resolves to `#ffffff` (white), which defeats the purpose. `.ds-icon-dark` means "force this icon to be dark" — it's used for icons sitting on yellow, green, or other light-colored card backgrounds where you need a dark icon regardless of the overall slide theme.

### Light theme auto-inversion

When a slide uses `data-theme="light"` on `<html>`, the icon color classes automatically invert:

| Class | Dark theme (default) | Light theme |
|-------|---------------------|-------------|
| `.ds-icon-white` | White (`#ffffff`) | Dark (`var(--color-text)` → `#1F2D3D`) |
| `.ds-icon-dark` | Dark (`#323338`) | White (`#ffffff`) |
| `.ds-icon-brand` | Purple | Purple (unchanged) |
| `.ds-icon-muted` | 60% opacity | 60% opacity (unchanged) |

This is handled by two CSS rules in the light theme section of `design-system.css`:

```css
[data-theme="light"] .ds-icon-white { color: var(--color-text); }
[data-theme="light"] .ds-icon-dark  { color: #ffffff; }
```

The developer never needs to change icon HTML between dark and light themes — the CSS handles the inversion.

---

## Icon Alignment

### Icons follow parent text alignment — no `text-align: center` on `.monday-icon`

`.monday-icon` is set to `display: inline-block` with NO `text-align` property. This means icons inherit alignment from their parent container:

- In a left-aligned card → icon aligns left with the text
- In a centered layout → icon centers with the text
- In a right-aligned element → icon aligns right

**Why no `text-align: center` on icons:** If `.monday-icon` had `text-align: center`, icons in left-aligned cards would visually break — they'd center while the headline and body text remained left-aligned. By inheriting alignment from the parent, icons always match the surrounding text.

**How to control alignment:** Set `text-align` on the **parent container**, not on the icon:

```html
<!-- LEFT: icon and text both left-aligned (default) -->
<div>
  <span class="monday-icon ds-icon-sm ds-icon-white">&#xf096;</span>
  <h3>Feature Title</h3>
</div>

<!-- CENTER: icon and text both centered -->
<div style="text-align: center">
  <span class="monday-icon ds-icon-sm ds-icon-white">&#xf096;</span>
  <h3>Feature Title</h3>
</div>
```

---

## Icon Sizing

### All sizes use vmin, not px or rem

The skill's `design-system.css` uses `vmin` units for icon sizes so they scale proportionally with the viewport. Since presentation slides are 16:9 (wider than tall), `1vmin ≈ 1vh`. This ensures icons look proportional at any screen size without media queries.

| Class | Token | Size | Typical use |
|-------|-------|------|-------------|
| `.ds-icon-xs` | `--icon-xs` | `3vmin` | Inline with small text |
| `.ds-icon-sm` | `--icon-sm` | `5vmin` | Card headers, bullet icons |
| `.ds-icon-md` | `--icon-md` | `7vmin` | Default — standalone icons |
| `.ds-icon-lg` | `--icon-lg` | `10vmin` | Feature hero icons |
| `.ds-icon-xl` | `--icon-xl` | `15vmin` | Full-slide accent icons |

**Default size:** If no size class is added, `.monday-icon` defaults to `font-size: var(--icon-md)` (7vmin).

**Never use hardcoded `px` or `rem` values** for icon sizes. These create fixed sizes that don't scale with the viewport, breaking the responsive design.

---

## Quote Mark Icon

The quote icon (`&#xf00e;`) is used in testimonial/quote slides. It has a dedicated `.quote-mark` class in `design-system.css`:

```css
.quote-mark {
  position: absolute;
  top: var(--space-6);
  left: var(--space-10);
  font-size: 7vmin;
  line-height: 1;
  color: var(--color-purple);
  user-select: none;
  pointer-events: none;
}
```

Usage inside a `.quote-box`:
```html
<div class="quote-box">
  <span class="monday-icon quote-mark">&#xf00e;</span>
  <p class="quote-text">Quote text here...</p>
  <div class="attribution">...</div>
</div>
```

The `.quote-mark` class handles its own size (7vmin) and color (purple) — no `.ds-icon-*` classes needed on quote mark icons.

---

## Quick Reference

### HTML pattern
```html
<span class="monday-icon">&#xf096;</span>                              <!-- default (7vmin, currentColor) -->
<span class="monday-icon ds-icon-sm ds-icon-white">&#xf096;</span>     <!-- small, white -->
<span class="monday-icon ds-icon-lg ds-icon-brand">&#xf098;</span>     <!-- large, purple -->
<span class="monday-icon ds-icon-md ds-icon-dark">&#xf10b;</span>      <!-- medium, dark -->
```

### Checklist for generated presentations

1. Inline `icon-font.css` **first** in the `<style>` block
2. Inline `design-system.css` **second** in the `<style>` block
3. Add `.slide-container .monday-icon { font-family: "MondayIcons" !important; font-style: normal !important; }` after the Poppins lockdown
4. Use `<span class="monday-icon {size} {color}">&#x{code};</span>` for all icons
5. Never add `text-align` to `.monday-icon` — control alignment from the parent
6. Never use `px` or `rem` for icon sizes — always use `.ds-icon-*` classes
7. Never use `var(--color-text)` for `.ds-icon-dark` — it must be hardcoded `#323338`

---

## Coverage

- **268 icons** in the font (monochrome, COLR/CPAL tables stripped)
- All 270 original SVGs are covered (2 filenames mapped to combined glyphs)
- Font source: IcoMoon project, post-processed with `fonttools` to remove COLR/CPAL color tables

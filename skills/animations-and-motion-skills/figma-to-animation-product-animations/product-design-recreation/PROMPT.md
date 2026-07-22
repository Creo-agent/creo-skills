# Product Design Recreation — Run Procedure

Pixel-accurate HTML/CSS from a Figma product UI. Every interactive element gets a stable
`data-anim-id` hook for animation targeting. No motion added here — that is `product-animation`.

## Step 0 — Standalone setup (skip if called by the orchestrator)

If invoked directly (not via `figma-to-animation-product-animations`), ask for what is missing:

- **Figma design** — URL or exported image/screenshot. Required. Ask if absent.
- **Viewport** — the fixed pixel dimensions to render at (e.g. 1440×900). Ask if absent; default
  to 1440×900 if the user is unsure. All downstream skills (animation, cursor, QA) must render
  at this exact size — declare it and stick to it.
- **Timeline plan** *(optional)* — if a `product-animation-planning` output exists, read its
  element list to know which items need `data-anim-id` hooks. Without it, apply hooks to all
  plausible interactive elements (buttons, rows, links, modals, form fields) and document them
  in the manifest. Pass the manifest forward so the Animation and Cursor skills can catch up.
- **Design system reference** *(optional)* — spacing scale, color tokens, typography scale,
  stroke widths, border-radii. Useful if available; if absent, extract values directly from Figma.

## Step 1 — Confirm the rendering viewport

Set the stage at the declared viewport. Every measurement, screenshot, and coordinate taken
downstream must use this exact size — a mismatched viewport causes coordinate drift for the
Cursor skill. Declare it in the output file: `<!-- Viewport: 1440x900 -->`.

## Step 2 — Extract design tokens first

Before writing a single line of markup, pull the exact values in use. Do not estimate:
- **Colors** — hex/rgba values and/or token names
- **Typography** — font family, weight, size, line-height for every text style in use
- **Spacing** — padding, margin, gap values from Figma auto-layout properties
- **Borders** — stroke width, border-radius for every component

Extract from Figma via `get_design_context` (plugin transport — does not time out) or the
design system source of truth. Confirm each value before placing it in CSS.

## Step 3 — Map layout to containers

Convert Figma auto-layout frames to CSS layout faithfully:
- Horizontal auto-layout → `display:flex; flex-direction:row`
- Vertical auto-layout → `display:flex; flex-direction:column`
- Preserve `gap`, `padding`, `align-items`, `justify-content` exactly as Figma defines them
- Absolute-positioned elements (overlays, floating cards) → `position:absolute` with Figma x/y
  converted via scale factor (`target_canvas_px / figma_frame_px`)
- Preserve draw-order stacking (Figma layer order = z-index or DOM order)

## Step 4 — Build semantic markup with data-anim-id hooks

Every element the Animation or Cursor skill will need to target must have a **stable, clearly-named**
`data-anim-id` attribute:

```html
<tr data-anim-id="table-row-3">...</tr>
<button data-anim-id="delete-btn">Delete</button>
<div data-anim-id="detail-panel">...</div>
```

Rules for `data-anim-id` values:
- kebab-case, descriptive (element type + identifier or position)
- Stable — do not use array indices that shift if rows are added
- Unique across the entire document

If working from a timeline plan, every element with a row in the plan table must have a hook.
If working standalone (no plan yet), apply hooks to all plausible interactive elements and list
them in the manifest. Flag any element you are unsure about.

Also add toggle-able state classes for each interactive element:
```css
.table-row--hover   { background: ... } /* declared, not applied via JS here */
.button--active     { transform: scale(0.97); }
.detail-panel--open { ... }
```
Leave transition timing out — the Animation skill adds that.

## Step 5 — Match assets exactly

- Export icons and logos from Figma at correct resolution via `get_design_context` to confirm
  exact dimensions, then export at natural size via the Figma MCP.
- Place assets with exact `width` / `height` attributes — no stretching.
- No placeholder substitutions. If an asset cannot be exported, note it in the manifest.

## Step 6 — State-readiness without animation

Structure the markup so interactive states can be toggled by adding/removing a CSS class.
Do **not** add `transition`, `animation`, or any JS-driven motion. The Animation skill owns
those. This skill's output is a static snapshot at resting state, with all state classes
defined but none applied.

## Step 7 — Self-check before handoff

- [ ] Colors match design tokens exactly (no approximated hex values)
- [ ] Font family, size, weight, line-height match exactly
- [ ] Spacing/padding/gap values match Figma auto-layout exactly
- [ ] Stroke widths and border-radii match exactly
- [ ] Container/grid structure mirrors Figma's auto-layout hierarchy
- [ ] All elements from the timeline plan (or plausible interactive elements) have `data-anim-id`
- [ ] State classes declared (`.--hover`, `.--active`, `.--expanded`) but none applied
- [ ] Logos/icons are correct assets at correct size, not stretched
- [ ] No invented UI elements not present in the original design
- [ ] Viewport declaration is in the file comment

## Output

1. **HTML/CSS file** — single file or component, at the declared viewport, resting state only.
2. **data-anim-id manifest** — a short table listing every hook:

```markdown
## data-anim-id Manifest

| data-anim-id  | Element                   | Interactive? | Notes          |
|---------------|---------------------------|--------------|----------------|
| table-row-3   | 3rd row of the data table | Yes          | hover + click  |
| delete-btn    | Delete button in toolbar  | Yes          | click → modal  |
| detail-panel  | Slide-in detail panel     | Yes          | animated in/out|
| page-header   | Top navigation bar        | No           | static         |
```

## Handoff

- **`product-design-qa`** — validates ≥95% visual accuracy against Figma before animation begins.
- **`product-animation`** — attaches transitions/keyframes to the identified elements.
- **`cursor-animation`** — uses element coordinates (post-render at the declared viewport).

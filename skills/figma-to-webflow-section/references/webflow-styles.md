# Webflow styles — how to create classes that behave

Styling headlessly means `data_style_tool`. It works well for base styles if you
respect two rules; it does **not** work for responsive styles at all.

## Rule 1 — Longhand properties only

The style tool wants individual CSS longhand properties. Shorthands get dropped
or misapplied. Always expand:

| Instead of | Write |
|---|---|
| `background: #000` | `background-color: #000` |
| `border: 4px solid rgba(...)` | `border-width: 4px` + `border-style: solid` + `border-color: rgba(...)` |
| `margin: auto` | `margin-top/right/bottom/left` as needed (or set them individually) |
| `font: ...` | `font-family`, `font-size`, `font-weight`, `line-height` separately |

Gradients belong in `background-image` (e.g. `linear-gradient(...)` /
`radial-gradient(...)`), with `background-size` / `background-position` as
separate longhand props.

## Rule 2 — Namespace every class

Use `section-name_element-name`, e.g. `agents-banner_heading`,
`pricing_card-title`. This keeps new classes from colliding with the rest of the
site's stylesheet. It also makes the freeform-code selectors in Phase 6
unambiguous.

## Rule 3 — Base breakpoint only; responsive lives elsewhere

`update_style`'s `breakpoint` parameter is silently ignored — everything lands
on base regardless (see `api-gotchas.md` #1). So:

- Use `create_style` / `update_style` for the **base** (desktop) appearance
  only.
- Put **all** breakpoint overrides in the freeform code block
  (`set_page_freeform_code`) with real `@media` queries. See
  `responsive-patterns.md`.

## Workflow

1. Create every class the section needs **before** building the DOM. Adding a
   forgotten class after elements exist is painful.
2. Keep `create_style` batches to 2–4 actions (socket-drop risk on big batches).
3. Reuse existing site classes where they already fit rather than duplicating.
4. Verify with `query_styles` / `get_styles` if something looks off — but
   remember a "successful" breakpoint write is a no-op, not a real style.

## Positioning decorative elements

Convert Figma pixel positions to **percentages** of the frame width so the
composition holds as the section scales. For absolute elements, set only the
sides you want to anchor — an element with both `left` and `right` gets pinned
across the axis (see `api-gotchas.md` #5). Release the other side with `auto`.

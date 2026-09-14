# Figma metadata — reading it correctly

## Coordinate space
- `get_metadata` positions are relative to the parent frame. For a flat scatter (cards as
  direct children of the frame), `x/y` are effectively frame-absolute — scale directly.
- If elements are nested inside sub-frames, add parent offsets, or just take the top-level
  child boxes (which is usually all you need for a scatter layout).

## Node roles you'll encounter
- **Image-fill rounded-rectangle** (often named like a placeholder, e.g. "pipeline",
  "NB Enhanced Image"): a rect whose fill is the hero image. Its box is the layout slot;
  the visible subject may not fill it edge-to-edge. Two of these often coexist with one
  `hidden="true"` — the hidden one is an alternate; use the visible one.
- **Card frames**: the outer frame box is what you position. Ignore the nested
  text/graph/icon children unless you're rebuilding the card itself.
- **Tiny stray nodes** (a few px, odd names): decorative artifacts — skip.

## Stacking
Order in the XML = paint order. Later = on top. For an intentional overlap (card A behind
card B), ensure A appears before B in your DOM / render array. A "hero on top of some
cards, behind others" layering is common — replicate the exact order if the overlap is
visible.

## Sizing the hero/subject
The Figma rect width may be tight to the artwork or include padding. If your image asset
has its own transparent margins, the container width that makes the *visible* subject match
the Figma render is usually a bit larger than `rect × scale`. Verify against the screenshot
and nudge the width, rather than trusting the raw rect blindly.

## Sanity check the scale
Pick one element, compute `figmaValue × scale`, then measure the rendered element
(`offsetLeft/Top/Width`). They should match within a pixel. If not, your frame dimension or
scale factor is wrong.

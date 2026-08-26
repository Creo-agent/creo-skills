
# Precise Figma composition

When a layout needs to match a Figma design *exactly* — positions, sizes, overlaps —
don't estimate from a screenshot. Read the real coordinates from Figma and transform
them once. This is how you nail a scattered composition (e.g. cards floating around a
central figure) that eyeballing always gets subtly wrong.

## 1. Pull exact geometry from Figma
Use the Figma MCP `get_metadata` on the node/frame URL. It returns XML with each node's
`x`, `y`, `width`, `height`, and nesting. Extract:
- the **frame** dimensions (your source coordinate space), and
- each element you care about (cards, hero image, badges) with its `x/y/w/h`.

Grab a `get_screenshot` of the same node too, as the visual target to verify against.

## 2. Compute the scale factor
```
scale = targetCanvas / figmaFrame       # e.g. 1080 / 1440 = 0.75
```
Every position and size becomes `figmaValue × scale`. Do this for x, y, width, height of
each element. Now you have exact absolute coordinates in your canvas space.

## 3. Map to code
- **HTML/CSS:** absolutely position each element — `left`, `top`, `width` in px (heights
  usually follow the image's aspect; set width and let height be natural, matching Figma).
- **Remotion / canvas:** emit a `CARDS`-style array of `{file, left, top, width, height}`.

### Preserve stacking (z-order)
Figma draw order = paint order: nodes **later** in the metadata paint **on top**. Replicate
it so intentional overlaps read correctly (e.g. one card tucked behind another). In HTML,
match with DOM order or `z-index`; in a render list, order the array the same way.

## 4. Identify element roles — don't place blindly
Read `references/figma-notes.md` for the traps. In short:
- A big **image-fill rounded-rectangle** is often the hero/character placeholder — its rect
  is the layout box, but the visible subject may be narrower (transparent padding). Size
  the subject to match the *visible* silhouette, not always the raw rect.
- **Hidden nodes** (`hidden="true"`) are alternates — ignore them.
- Text/title nodes inside a card are internal detail; you usually only need the card's
  outer frame box.

**Orientation is a rotation, not a flip.** Figma's `get_design_context` emits `rotate-[Xdeg]` — copy that angle verbatim (e.g. arrows at TL -164.87, TR -90.98, BL 80, BR 5.73). Never substitute `scaleX(-1)`/`scaleY(-1)`: a flip mirrors an asymmetric asset (cursor/arrow) into the wrong chirality. Position a rotated element by centering its HTML box on the Figma **axis-aligned bounding box (AABB)** center — not the viewBox.

**Equal visual gap = equal distance from the shape EDGE, not from center.** A circle's edge sits at its radius; a rounded-square's corner along the 45° diagonal sits `√2·(halfSide − cornerR) + cornerR` out — ~20px further than a same-width circle. Placing satellites at equal center-distance makes bubble gaps tighter (even overlapping). Compute the edge distance per shape in the placement direction, then place each satellite at `edgeDistance + constant gap`.

## 4b. Repeated components — pull one node, build once, swap content
When many elements share the same design (message pills, chips, list rows), don't read them
all. Call `get_design_context` on **one** instance to get its exact styling (radius, padding,
gap, fill, gradient, shadow, type) as reference code, build a single component, and vary only
the text/content from an array. Multiply/duplicate it to fill (a carousel row, a grid). All
sizes are still `figmaValue × scale`.

**Avatar / image cropped from a larger illustration:** a small circular avatar is often the
*whole* character image clipped to the face — a circle with `overflow:hidden` containing an
oversized `<img>` positioned by the node's negative offsets. Reproduce it by scaling the
image node's own `x/y/w/h` (which are negative/larger than the circle) by the same factor:
`img { position:absolute; width: W×scale; left: x×scale; top: y×scale; }` inside a
`width/height = circle×scale; overflow:hidden` box. Downscale the source file first — a 4K
illustration rendered at ~57px is wasteful.

### Sizing exported icon SVGs (drop-shadow, uniform size, uniform stroke)
- **Drop-shadow bleeds into the viewBox.** A Figma drop-shadow region is baked into the exported viewBox as transparent padding, so the visible shape is only ~60% of the viewBox (offset toward the top-left, since `feOffset` is positive). Size the HTML box to ~1.6–1.7× the *visible* Figma bbox and center it on the Figma AABB — never on the viewBox or the visible-art dimensions.
- **Uniform visible SIZE across files.** If several icons share a near-constant visible-shape-to-viewBox ratio (~0.60 here), give them one shared box size; under `preserveAspectRatio="meet"` the viewBox scale cancels and equal boxes render equal visible art (e.g. all four arrows at 112×115).
- **Uniform rendered STROKE across different viewBoxes.** Effective stroke px = `svgStrokeWidth × (boxW / viewBoxW)` under `meet` (use the *binding* dimension — width here, since `box/vbW < box/vbH`). To equalize rendered stroke at a shared box size, set each file's `stroke-width = targetPx × viewBoxW / boxW`. Normalize avatar CSS borders to the same target (e.g. 3.5px) so strokes and rings read as one system.

## 5. Verify against the Figma render
Put your result next to the `get_screenshot`. Check element-by-element: same corners, same
overlaps, same relative sizes. Measure in code (`offsetLeft/Top/Width/Height`) to confirm
the numbers match `figmaValue × scale`. Fix drift before finishing — "matched to Figma"
means measurably matched, not approximately.

**Measurement reliability.** `getBoundingClientRect()` can return 0/null right after navigate/reload — wait for stable layout and assert the read is sane before trusting it. When measuring inside a `transform: scale()` stage, divide by the scaler factor **only** for elements *inside* the scaled subtree (a probe on `document.body` already reports true px); see `frame-building` for the full trap. Magnitude-check values (~50px/char at 96px, not ~95), and prefer sizing to content or measuring at render time over hardcoding px (see `measuring-text`).

## Output
Absolute-positioned markup (or a coordinates array) whose geometry equals the Figma frame
scaled to the target. Hand off to `motion` to animate the placed elements, or
`export-as-gif` to render.

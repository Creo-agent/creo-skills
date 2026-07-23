---
name: precise-figma-composition
description: >-
  Reproduce a Figma frame's layout pixel-accurately in code by pulling each node's exact coordinates from Figma and scaling them to a target canvas — instead of eyeballing positions from a screenshot. Go-to skill whenever the user shares a figma.com link or node and wants a composition "matched exactly", "like in the figma", "pixel perfect", "the right positions", or wants a scattered/layered arrangement (cards, badges, floating elements around a hero) placed precisely — especially when a prior eyeballed layout was "close but wrong" and they point to Figma as source of truth. Prefer this over figma-design-to-code specifically for getting a scatter/overlay layout's geometry right. Do NOT use for: building a full Figma screen as a component, grabbing an animation off a website, animating/looping, rendering to gif/mp4, resizing, or exporting a Figma frame to png.
---

# Precise Figma Composition

When a layout must match a Figma design *exactly* — positions, sizes, overlaps — don't
estimate from a screenshot. Read the real coordinates from Figma and transform them once.
This is how you nail a scattered composition (cards floating around a central figure) that
eyeballing always gets subtly wrong.

## When This Skill Activates

- "Match this composition exactly to my figma <link> — the cards are in the wrong spots"
- "Place these floating elements pixel-perfect like in the figma frame"
- "My eyeballed positions are off — pull the real coords from figma and apply them"
- "The figma shows this card tucked behind that one; match the stacking"

Keywords: `figma`, `pixel perfect`, `match the figma`, `exact positions`, `scatter layout`,
`overlap`, `source of truth`, `right coordinates`.

## What This Skill Does

1. Pulls exact `x/y/w/h` per node via the Figma MCP `get_metadata`.
2. Computes a scale factor (target canvas ÷ Figma frame) and maps every node to absolute px.
3. Preserves draw-order stacking (intentional overlaps).
4. Emits absolute-positioned HTML/CSS or a coordinates array for Remotion.
5. Verifies element-by-element against a `get_screenshot`.

## Requirements

- A Figma design URL (path `/design/`) pointing at the frame/node. Ask for it if missing.

---

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
In short:
- A big **image-fill rounded-rectangle** is often the hero/character placeholder — its rect
  is the layout box, but the visible subject may be narrower (transparent padding). Size
  the subject to match the *visible* silhouette, not always the raw rect.
- **Hidden nodes** (`hidden="true"`) are alternates — ignore them.
- Text/title nodes inside a card are internal detail; you usually only need the card's
  outer frame box.

## 5. Verify against the Figma render
Put your result next to the `get_screenshot`. Check element-by-element: same corners, same
overlaps, same relative sizes. Measure in code (`offsetLeft/Top/Width/Height`) to confirm
the numbers match `figmaValue × scale`. Fix drift before finishing — "matched to Figma"
means measurably matched, not approximately.

## 6. Shadow extraction from Figma — exact mapping

Getting shadows pixel-perfect requires knowing which Figma property maps to which CSS property.

### `filter: drop-shadow` vs `box-shadow` — use the right one
- **`filter: drop-shadow(x y blur color)`** — traces the **alpha channel** of the element (PNG transparency). Use for character avatars, cursors, SVGs, or any element whose visible shape is defined by transparent pixels.
- **`box-shadow: x y blur spread color`** — traces the **CSS box model** (the rectangular container). Use for cards, frames, rounded-rect containers, anything with `border-radius`.

Wrong choice = shadow on the entire bounding rectangle instead of the visible shape, or vice versa.

### Reading Figma SVG filter values correctly

When Figma exports an SVG filter like:
```xml
<feGaussianBlur stdDeviation="8.24173"/>
<feOffset dx="4.94504" dy="4.94504"/>
<feColorMatrix values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.15 0"/>
```
The CSS equivalent is:
```css
filter: drop-shadow(4.94504px 4.94504px 8.24173px rgba(0,0,0,0.15));
```
Note: **CSS `drop-shadow` blur = `stdDeviation` directly**. Do NOT double it. An old approximation says "CSS blur = 2 × stdDeviation" — that was for `box-shadow`, not `filter: drop-shadow()`.

### Reading Figma frame/box shadow (via `get_design_context` or `get_metadata`)
Figma box shadows show as `effects: [{type:"DROP_SHADOW", offset:{x,y}, radius, color}]`.
Map to CSS: `box-shadow: {x}px {y}px {radius}px {spread}px rgba({r*255},{g*255},{b*255},{a})`.

### Figma-exported PNGs may have white corners
Figma sometimes bakes opaque white pixels into PNG corners (from a white artboard). If you then apply `filter: drop-shadow`, the shadow traces the white corners — it looks like a white card halo. Clean the PNG before use (see `animation-scaffold` skill's section 5: PNG cleanup).

## 7. Z-index trap: cursor/overlay hidden by a sibling avatar

When a cursor (or any overlay PNG) is a child of a container alongside an avatar circle,
the avatar typically gets a `z-index` for stacking context. If the cursor's own `z-index` is
lower than the avatar's, the cursor is fully hidden behind it — even if it's positioned
*outside* the avatar's visual bounds.

**Pattern:**
```css
#avatar  { z-index: 3; }   /* sets a local stacking context */
#cursor  { z-index: 1; }   /* WRONG — cursor is hidden behind avatar */

/* Fix: cursor z-index must be higher than the highest sibling */
#cursor  { z-index: 4; }   /* ✓ renders above avatar */
```

**How to diagnose:** if a PNG element is physically present in the DOM but invisible,
inspect its stacking context. The usual cause is a sibling with a higher explicit `z-index`.

## 8. Avatar photo zoom/crop — precise Figma match

`object-fit: cover` fills the container but can't control the zoom level — it always
shows the content at the maximum size that covers the box. When Figma crops a photo at
a specific zoom (e.g. showing face + upper chest, goggles at the top of the circle), you
need absolute positioning + explicit width override:

```css
/* Container (circle) */
#avatar {
  width: 113px;
  height: 113px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
}

/* Image inside — zoomed in to match Figma crop */
#avatar img {
  position: absolute;
  width: 225%;          /* 2.25× the circle width — zoom level from Figma */
  height: auto;
  left: 50%;
  top: -27%;            /* negative → shift up so face is in frame, not feet */
  transform: translateX(-50%);
}
```

**How to derive the values from Figma:**
1. In `get_metadata`, note the avatar circle size and the source image node size.
2. Compute zoom: `width% = (figma_image_width / circle_width) * 100`.
3. Compute `top%`: how far the *visible window* is from the top of the image.
4. Iterate: take a `get_screenshot` and compare crop visually; adjust `top` by small
   increments until the correct part of the photo (face, not full body) is visible.

## 9. Pill / label centering — use `translateY(-50%)`, not percentage bounds

When a label pill needs to be vertically centered on an avatar circle, do **not** use
`top: X%` + `bottom: Y%` on the pill container. That stretches the element and shifts the
text center well below the intended alignment.

**Wrong (stretches pill):**
```css
#label {
  top: 20%;
  bottom: 20%;
  /* pill height is determined by top+bottom → element stretches */
}
```

**Correct — pin to absolute px center + translate:**
```css
#label {
  top: 81px;                            /* = avatar_circle_vertical_center in px */
  left: 50%;
  transform: translateX(-50%) translateY(-50%);  /* centers pill on that point */
}
```

Derive `top` from Figma geometry: `top = avatar.y + avatar.height / 2` (scaled to canvas).

## 10. Cursor positioned outside container bounds

A cursor PNG child can legitimately have `top: Npx` values **larger than the container height**
(e.g. `top: 168px` inside a `height: 155px` container). This renders the cursor below the
container's bottom edge. This is correct when Figma places the cursor "hanging" below the
bubble.

**Make sure:** the parent container does **not** have `overflow: hidden`. If it does, the
out-of-bounds portion is clipped. The parent may have `overflow: visible` (default) even if
`border-radius` is set — `overflow: hidden` is only forced when you *want* the clip.

## Output
Absolute-positioned markup (or a coordinates array) whose geometry equals the Figma frame
scaled to the target. Hand off to `loop-animator` to animate the placed elements, or
`export-as-gif` to render.

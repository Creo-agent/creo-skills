
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

## 5. Verify against the Figma render
Put your result next to the `get_screenshot`. Check element-by-element: same corners, same
overlaps, same relative sizes. Measure in code (`offsetLeft/Top/Width/Height`) to confirm
the numbers match `figmaValue × scale`. Fix drift before finishing — "matched to Figma"
means measurably matched, not approximately.

## Output
Absolute-positioned markup (or a coordinates array) whose geometry equals the Figma frame
scaled to the target. Hand off to `loop-animator` to animate the placed elements, or
`export-as-gif` to render.

# Figma 1:1 Card

Rebuild a Figma component as DOM/CSS that is **measurably identical** to the design —
not "close enough", but verifiable pixel-for-pixel. Every value is pulled from the
Figma spec; nothing is estimated from a screenshot.

## 0. Understand the rendering context first

Before pulling any Figma data, answer two questions:
- What is the **natural size** of this node in Figma? (its `width` × `height` in the Figma frame)
- What **scale factor** sits between the Figma frame and your target canvas? (e.g. Figma 1440 → 1080 stage = ×0.75)

Build the card at **Figma natural size** and apply the scale factor as a single
`transform: scale(N); transform-origin: top left` on the card's outer wrapper.
This keeps every internal measurement identical to the Figma spec — no mental math.

## 1. Extract the full node spec from Figma

**Primary tool: `mcp__plugin_figma_figma__get_design_context`** on the full card node.
This returns complete per-node styling: exact px, colors, radii, fonts, effects, fill types.
The remote server (`mcp__e0cae42b-...__get_design_context`) times out on large nodes —
always try the plugin transport first.

Grab a **screenshot** too (`get_screenshot`) as the visual target to verify against.

What to extract per node:
| Property | Where to find it |
|---|---|
| Width / height | Node `width`, `height` fields |
| Border radius | `cornerRadius` or per-corner values |
| Fill | `fills[].type` + color/opacity |
| Stroke | `strokes[]` — note: gradient strokes are often dropped from codegen output (see §3) |
| Font | `fontName.family`, `fontName.style`, `fontSize` |
| Gap / padding | Auto-layout `itemSpacing`, `paddingTop/Right/Bottom/Left` |
| Shadows | `effects[]` of type `DROP_SHADOW` |
| Opacity | `opacity` field on the node |

For **child nodes** (icons, avatars, pills): use `get_metadata` to get the node-id tree,
then per-leaf `get_design_context` to retrieve asset URLs. Raster fills come back as
full-res image URLs; vectors come as SVG.

## 2. Build the DOM structure

Match Figma's layer hierarchy to HTML structure:

```
Figma: Frame (card bg) → Auto-layout column → [Title group, Items group → Item rows]
HTML:  .card-bg (position:absolute,inset:0) + .card-content (flex col, same padding/gap)
```

Split the card into **two separate layers** so each can be animated independently:
- `.card-bg` — the background, border-radius, shadow, gradient stroke (animatable)
- `.card-content` — everything visible on top: title, rows, etc.

```html
<div class="my-card">
  <div class="my-card-bg"></div>
  <div class="my-card-content">
    <p class="my-card-title">
      <span class="my-card-title-line">Line one</span>
      <span class="my-card-title-line">Line two</span>
    </p>
    <div class="my-card-items">
      <!-- rows -->
    </div>
  </div>
</div>
```

Use **Figma's exact px** (not rounded):
```css
.my-card {
  position: absolute; inset: 0;
  width: 237.446px;   /* Figma exact */
  height: 336.913px;
  transform: scale(0.75);   /* canvas scale factor */
  transform-origin: top left;
  font-family: 'Poppins', sans-serif;
}
```

## 3. Rebuild the glassy gradient stroke

Codegen often **drops gradient strokes** — confirm by sampling the rendered edge.
The pattern for a 1px gradient ring:

```css
.my-card-bg::before {
  content: "";
  position: absolute; inset: 0;
  border-radius: inherit;
  padding: 1px;   /* the stroke width */
  background: linear-gradient(157deg,
    rgba(255,255,255,0.45) 0%,
    rgba(255,255,255,0.14) 48%,
    rgba(255,255,255,0.07) 100%);
  /* Mask: show only the 1px padding ring, not the center */
  -webkit-mask: linear-gradient(#000 0 0) content-box,
                linear-gradient(#000 0 0);
  mask: linear-gradient(#000 0 0) content-box,
        linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
```

Adjust the gradient angle and stops to match the Figma visual.

## 4. Extract and embed icons and avatars

Use `get_design_context` on the individual leaf icon node (not a wrapper group) to get the asset URL.
- **Raster** (png/jpg): download at full res, scale down in CSS to the Figma-specified display size
- **SVG**: inline or embed via `<img>` — but always give explicit `width` and `height` matching
  the viewBox aspect ratio. Figma SVGs carry `preserveAspectRatio="none"`, so without explicit
  dimensions the glyph stretches into a bar.

```html
<!-- WRONG: stretches -->
<img src="icon-gmail.svg" />

<!-- RIGHT: explicit dimensions matching viewBox ratio -->
<img src="icon-gmail.svg" width="16.08" height="12.06" />
```

Common trap: a wrapper node named "Activity icon" or similar may export blank — the real
glyph is often a **sibling** node. Use `get_metadata` to find the sibling, then export that.

## 5. Map fonts

Check the Figma node's `fontName.family` and `fontName.style`:
- Load the correct Google Font weight in `<link>` (e.g. `Poppins:wght@500` for Poppins Medium)
- Figma "Medium" = `font-weight: 500`; "SemiBold" = 600; "Regular" = 400
- Different text groups inside one card may use different families (e.g. title in Poppins, labels in Figtree)

## 6. Verify against the screenshot

Put the built card next to `get_screenshot`. Check:
- Corner roundness matches
- Stroke is visible and graduates correctly (light top-left → subtle bottom-right)
- Icons are the right shape (not stretched)
- Font reads the same weight and size
- Spacing between rows feels identical

Measure in the browser if needed:
```js
const r = document.querySelector('.my-card').getBoundingClientRect();
// r.width should equal: Figma-width × scale-factor
```

Fix drift before declaring done. "Matched to Figma" = measurably matched.

## 7. Common gotchas

| Gotcha | Fix |
|---|---|
| `get_design_context` on full node times out | Use `mcp__plugin_figma_figma__get_design_context` (plugin transport) |
| Gradient stroke absent from codegen output | Rebuild manually with `::before` masked ring (§3) |
| SVG icon stretches | Add explicit `width` + `height` attributes matching viewBox ratio |
| Wrapper node exports blank | Find the actual glyph sibling via `get_metadata` |
| Avatar `contentsOnly:true` comes back blank | Re-render screenshot without that flag |
| Card clips at parent overflow | Parent may have `overflow:hidden` — override for inspection |
| Numbers look wrong after scale | Always build at Figma natural size, apply scale once on the outer wrapper |

## 8. Hand off

Once verified, the card is ready for:
- **`motion`** — add an orchestrated GSAP yoyo entrance animation (box → text → rows)
- **`motion`** — wire the card into a looping timeline
- **`frame-building`** — position the card at exact Figma coordinates in a full composition

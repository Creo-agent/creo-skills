---
name: frame-building
description: |
  WHAT: Build static, pixel-accurate HTML/CSS frames from Figma — the "make it look exactly right, before it moves" stage. Covers three modes: SCAFFOLD (fresh fixed-stage HTML/CSS/JS project, viewport scaler, GSAP load-gate, empty build() hook), LAYOUT (whole Figma frame reproduced pixel-accurately from real node coordinates), CARD (single component rebuilt as measurably 1:1 DOM+CSS). Also owns Figma asset and SVG download.
  TRIGGERS: "start a new animation / blank stage", "match this Figma exactly", "pixel-perfect / right positions", "build this card 1:1", "download assets from Figma", shares a figma.com link and wants accurate static HTML only (no motion yet).
  SUB-SKILL: figma-to-animation orchestrator routes here for its build stage. Usable standalone when you specifically need static Figma→HTML without the full pipeline.
  NOT FOR: adding GSAP motion → use motion/. Capturing animation off a live site → use extract-animation-from-web/. Resizing → use resize-animation/. Exporting to GIF/MP4 → use export-as-gif/. Full Figma→animation pipeline → use figma-to-animation/.
---

# Frame Building (static Figma → pixel-accurate HTML/CSS)

The "get it looking exactly right before it moves" stage. Everything downstream (motion, export)
assumes a correct, well-structured static frame — build that here, measurably matched to Figma, never
eyeballed from a screenshot. This is one skill with three modes plus shared asset handling; load the
matching reference doc.

## Pick the mode

| You need to… | Load |
|---|---|
| Start from nothing — a blank fixed stage to build on (1080², portrait, custom) | [`references/scaffold.md`](references/scaffold.md) |
| Match a whole Figma frame's layout exactly — scattered/overlapping elements in the right spots | [`references/layout.md`](references/layout.md) + [`references/figma-notes.md`](references/figma-notes.md) |
| Rebuild a single component/card 1:1 — exact px, gradient strokes, fonts, icons, avatars | [`references/card.md`](references/card.md) |
| Download Figma raster/SVG assets at the right size | see the **Assets** section below (covered inside `layout.md` §repeated-elements and `card.md` §icon/avatar) |

Typical order for a fresh build: **scaffold** the stage → place the **layout** (or build the **card**)
→ hand off to [`../motion/`](../motion/) to animate, then [`../export-as-gif/`](../export-as-gif/) to
render.

## Cross-cutting rules (shared across all three modes)
- **Measure, don't estimate.** Pull real values from the Figma MCP (`get_metadata` for coords,
  `get_design_context` for a full node spec). Verify element-by-element against a `get_screenshot`.
- **Watch the scaler's coordinate space.** On a `transform: scale()` stage, `getBoundingClientRect()`
  is post-scale while `offsetWidth/offsetLeft` are layout px — see `scaffold.md` and the pipeline's
  `../figma-to-animation/references/knowledge.md` (measurement discipline).
- **Structure for animation.** Give animated elements stable identifiers and a two-layer DOM where a
  card must move/scale later, so `../motion/` can target them cleanly.

## Assets (Figma raster/SVG download)
Detect the real file format (Figma often returns SVG bytes at a `.png` URL), pull assets at natural
size (a maxDimension cap doesn't upscale), give SVGs explicit width+height (they carry
`preserveAspectRatio="none"`), and reproduce cropped avatars by scaling the image node's own x/y/w/h.
Full workflows live in `references/layout.md` and `references/card.md`; the fidelity gotchas are in
`../figma-to-animation/references/knowledge.md` (Figma fidelity).

## Entry point
Load the reference doc for your mode (above). For a full Figma→animation job, start from
[`../figma-to-animation/`](../figma-to-animation/) instead — it orchestrates this skill and the rest.

# Sub · SVG Extraction from Figma

**Role (conditional, parallel with asset download; runs after 02, before 03):** extract vector
elements (icons, illustrations, shapes) as **native SVG code** straight from Figma — never recreated,
approximated, or swapped for a generic icon library. Skip if a frame has no vector elements. SVG is
far more reliable for an LLM to place accurately than inferring vectors from a raster.

**Inputs:** the frame analysis (02), which identifies vector elements.

**Method:** use the **`figma-export-assets`** skill (top-level skill at `../../figma-export-assets/`)
for all SVG exports — it runs the Vector Quality Check first (confirms the node has real vector
geometry, not an IMAGE fill that would produce a base64-wrapped raster), then exports via
`exportAsync({ format: 'SVG_STRING', svgOutlineText: true, useAbsoluteBounds: true, colorProfile: 'SRGB' })`
and writes the markup directly with the Write tool (no decode step). Refer to `frame-building` §4c
only for placement context; all *extraction* work goes through `figma-export-assets`. Key rules:
- Extract each vector as SVG code directly from Figma; store organized for drop-in at stage 03.
- Give exported SVGs **explicit width/height**; watch the `preserveAspectRatio="none"` distortion trap
  and the sibling-glyph export trap (see `frame-building`).
- Apply the icon-normalization rules from `references/knowledge.md`: drop-shadow viewBox bleed
  (~60% visible art), uniform box size across icons that share a visible/viewBox ratio, and uniform
  rendered stroke via `stroke-width = targetPx × viewBoxW / boxW`.

**Decorative / organic shapes (blobs, splotches, background fills) — de-clip on export.** Per-node
export bakes the containing group's clip and the node-box viewBox, so these come out with a **flat,
cut-off edge**. Don't ship the cropped shape. Per the `references/knowledge.md` "Decorative / organic
shapes" rules: (1) strip every baked `<clipPath>`/`clip-path` and clip `<defs>`; (2) strip baked
`feGaussianBlur`/`opacity` and re-apply them via CSS at stage 03/06 (reusable, animatable, uncropped);
(3) expand the viewBox to the path's true bounds — but only when the overflow lands inside the visible
stage — and record the re-derived center (`cx/cy`) so placement doesn't jump. Each shape is a separate
DOM node placed by its own center; never flatten the group to one image.

**QA:** SVGs render correctly, correct dimensions/aspect, no distortion, **no flat/clipped edge on any
organic shape** (a straight cut on a blob = an un-stripped baked clip — fix at export, not by masking).
**Output / handoff:** local SVG set → stage 03. **Standalone:** yes. (Does not touch animation logic.)

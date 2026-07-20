# 03 · Frame Building (static)

**Role:** build each frame as **static** HTML/CSS — no animation, no JS, no transitions. Runs once
per frame (and once per fix iteration inside Loop A). Kept separate from animation so each unit is
small enough to QA precisely against the ≥95 gate.

**Inputs:** the frame's per-frame prompt (02); local raster assets (`sub-asset-download`) and SVGs
(`sub-svg-extract`) — use them as-is, never re-fetch or re-derive.

**Method — use the engine skills, don't reimplement:**
- `frame-building` — pull each node's real `x/y/w/h` via `get_metadata`, scale by
  `target/frame`, place absolutely (`figmaValue × scale`), preserve paint-order/z-index.
- `frame-building` — for a self-contained component/card, rebuild measurably pixel-identical
  (`get_design_context`, explicit SVG width/height, masked gradient strokes).
- `figma:figma-design-to-code` — general design→code fallback.
- `frame-building` — if a fixed export stage is wanted, build inside it.
- Apply the Figma-fidelity rules from `references/knowledge.md`: rotation-not-flip, drop-shadow
  viewBox bleed, uniform icon size/stroke, negative-offset avatar crops, the measurement discipline.

**Fix mode (inside Loop A):** when static-QA returns a fix-prompt, apply it as a **targeted edit** to
the existing build (named element + property + expected value) — never rebuild from scratch. Keep the
frame index so the fix lands on the right frame.

**Output / handoff:** one static HTML/CSS build per frame → stage 04.
**QA:** bound to stage 04's ≥95 gate. **Standalone:** yes — build one static frame from Figma.

# frame-building — run procedure

Build the static frame(s) so they are measurably identical to Figma before any motion. This skill
bundles three previously-separate build skills as **mode reference docs** under `references/`; pick the
mode, load its doc, follow it. Nothing here is eyeballed — every value comes from the Figma MCP and is
verified against a screenshot.

## Modes (load the matching reference doc)

1. **Scaffold a fresh stage** — `references/scaffold.md`
   A single self-contained `index.html`: fixed pixel-exact `.stage`, a JS viewport-fit scaler (never
   changes the true render size), GSAP from CDN, a fonts+images load-gate, and an empty `build()` hook.
   Use at the very start of a new animation. Then place a layout or build a card into it.

2. **Whole-frame layout / scatter** — `references/layout.md` (+ `references/figma-notes.md`)
   Pull each node's exact `x/y/w/h` via `get_metadata`, compute one scale factor (target canvas ÷
   Figma frame), map every node to absolute px, preserve draw-order stacking, emit absolute-positioned
   HTML/CSS (or a coords array for Remotion). For repeated elements, pull one node via
   `get_design_context`, build the component once, swap content from an array.

3. **Single component 1:1 (card)** — `references/card.md`
   Build the component at Figma natural size with one `transform: scale(N)` on the wrapper; extract the
   full spec via `get_design_context` (plugin transport doesn't time out); two-layer DOM
   (`.card-bg` + `.card-content`) so it can animate later; rebuild the glassy gradient stroke codegen
   drops (masked 1px `::before` ring); extract icons/avatars with explicit SVG width/height; map Figma
   fonts to Google Font weights; verify measurably against the screenshot.

## Shared conventions
- **Requires a Figma design URL** (path `/design/`) for modes 2 and 3 — ask if missing.
- **Verify before handoff:** element `offset{Left,Top,Width,Height}` should equal `figmaValue × scale`;
  magnitude-check text width (~50px/char at 96px). See `../figma-to-animation/references/knowledge.md`.
- **Assets:** detect real format (SVG-at-.png trap), natural-size rendering, explicit SVG w/h
  (`preserveAspectRatio="none"`), negative-offset avatar crops — details in `layout.md`/`card.md`.

## Handoff
Static frame(s) done → [`../motion/`](../motion/) to animate → [`../export-as-gif/`](../export-as-gif/)
to render. For the full orchestrated pipeline, use [`../figma-to-animation/`](../figma-to-animation/).

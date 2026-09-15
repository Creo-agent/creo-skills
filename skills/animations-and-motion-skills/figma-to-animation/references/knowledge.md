# Pipeline knowledge base

Read this once at the start of a run. It's the distilled, hard-won knowledge the pipeline
depends on — the traps that cause silent quality loss and the bindings that resolve the specs'
unnamed dependencies. Sources are the existing engine skills (cited by name) and lessons from
prior builds.

## Bindings (resolving the specs' unnamed dependencies)
- **"Motion-principles skill"** (referenced by 01-index, 06a-animate) → the feel is defined by
  `gsap` (API + easing/stagger/timeline) and `motion` (loop shapes, seamlessness). Baseline:
  smooth `sine.inOut`/`power2.inOut` easing, never linear/abrupt; motion should make the product
  read as *grabbable and understandable*; restraint over excess.
- **"The existing Figma skill for Claude Code"** (04-static-qa, 08-validate) → use the Figma MCP
  plus `frame-building` (node geometry via `get_metadata`/`figmaValue×scale`, and single-component
  1:1 rebuild via `get_design_context`), and the plugin
  `figma:figma-design-to-code`. `figma-mcp-detector` routes a raw figma.com link into the MCP.
- **Rendered visual QA** → `design-critique` complements the structured/measured checks with a
  systematic critique of the *rendered* result.

## Measurement discipline (the #1 source of silent errors)
- On a fixed stage wrapped by a `transform: scale()` scaler, **`getBoundingClientRect()` returns
  post-transform (scaled) px; `offsetWidth`/`offsetLeft` are scale-invariant (layout px).** Divide
  a getBCR by the scaler factor **only for elements inside the scaled subtree** — a probe on
  `document.body` is already at scale 1, so dividing inflates it by `1/scale` (~1.875× at a 720px
  viewport) and silently decenters everything. Confirm with a 100px ruler div on body.
- **Magnitude-check** every measured/hardcoded px: Latin text at 96px ≈ 50px/char, not ~95; a
  ~1.9× deviation is a scale-inflation bug. Catch it before baking it in.
- **Prefer measuring at render time** (Remotion `measureText`, or size to content) over hardcoding
  px — hardcoded widths couple you to one font/scale environment and break silently.
- A layout/centering change can **mask** a data (measurement) error without fixing it — if a
  symptom persists after a plausible layout fix, isolate the root cause before declaring victory.
- Verify: `offset{Left,Top,Width,Height}` should equal `figmaValue × scale`.

## Figma fidelity (feeds 03-build-frame, sub-asset-download, sub-svg-extract, 04-static-qa)
- **Orientation is a rotation, not a flip.** Copy Figma's emitted `rotate-[Xdeg]` verbatim;
  `scaleX(-1)`/`scaleY(-1)` mirror asymmetric assets (cursors/arrows) into the wrong chirality.
  Position a rotated element by centering its box on the Figma AABB.
- **Drop-shadow bleeds into exported SVG viewBoxes** (~60% visible art, offset toward top-left).
  Size the HTML box to ~1.6–1.7× the visible bbox and center on the AABB.
- **Uniform icon size** across files with a near-constant visible/viewBox ratio → one shared box
  size (preserveAspectRatio=meet cancels the viewBox scale).
- **Uniform rendered stroke** across different viewBoxes: effective px = `strokeWidth × (boxW /
  viewBoxW)`; to equalize, set each file's `stroke-width = targetPx × viewBoxW / boxW`.
- **SVG-at-.png trap:** Figma often returns SVG bytes at a `.png` URL — detect real format
  (`file`) and rename; broken `<img>` otherwise. (Full workflow in `frame-building` §4c.)
- **Avatars/cropped images** = the whole illustration clipped to a shape via negative offsets;
  reproduce by scaling the image node's own x/y/w/h.
- **`preserveAspectRatio="none"` on Figma SVGs** stretches an `<img>` to whatever box you give it —
  set explicit width AND height matching the viewBox aspect (or it distorts).
- **Gradient strokes are often dropped** from the generated CSS: a card can have a glassy ~1px
  gradient stroke that isn't in the code. Sample the rendered edge to confirm, then rebuild it (a
  masked gradient-ring `::before`). Don't trust the emitted CSS to be complete here.
- **Keep text live; don't rasterize it.** Render headings/body as real HTML text (selectable,
  crisp at any scale, animatable per-line/word) — never bake a text layer to a PNG. If the brand font
  isn't available/licensed for web, substitute the nearest web font (e.g. Monday Pop → **Poppins**)
  and **tune the size/letter-spacing to preserve the original line breaks** — a substitute with
  different metrics silently rewraps a 2-line headline to 3 lines. Embed the substitute via
  `@font-face` in a standalone build so it's not CDN-dependent.

### Decorative / organic shapes (blobs, gradient splotches, background fills)
This is the #1 silent failure for ambient/decorative art — a shape that renders with one *flat,
straight, cut-off edge* is almost never the design; it's a baked clip. Diagnose and fix at export:
- **Per-node export bakes a clip that crops the shape.** Figma sets the exported SVG's viewBox to
  the node's frame bbox and often bakes a `<clipPath>`/mask (inherited from the containing group),
  so any part of the shape's path that bleeds past its own box is hard-clipped. Two-part fix:
  (1) **strip** every baked `<clipPath>`/`clip-path` attribute and clip `<defs>`; (2) **expand the
  viewBox to the path's true bounds** so the whole organic form shows. "Get the shape out of the
  group and bring it out, don't crop it."
- **Baked blur/opacity also clip — strip them, re-apply via CSS.** Figma bakes
  `feGaussianBlur`/`opacity` into the export, and a baked blur carries its own filter region that
  clips the shape at the box edge. Export clean, then set `filter: blur()` + `opacity` in CSS — it's
  reusable, animatable, and uncropped.
- **When you expand a viewBox, re-derive placement or the shape jumps.** Growing the box by
  `(dx, dy, dw, dh)` shifts the art inside it. Keep the original art anchored: recompute the element
  center so `new_left == original_art_left` (i.e. `cx = original_art_left + new_w/2`,
  `cy = original_art_top + new_h/2`). Don't just swap w/h.
- **Only expand for overflow that lands inside the visible stage.** If a shape's true bounds bleed
  *past* the stage edge, leave the node dims and let the stage's `overflow:hidden` clip it naturally
  — expanding there wastes box and can drag the shape inward, changing the composition. Decide
  per-shape: in-frame overflow → expand + reposition; fully-off-stage overflow → keep original.
- **Place & animate each decorative shape individually — never bake the group to one image.** A
  flattened group re-introduces the group's clip box and kills per-shape drift/rotate/breathe. One
  DOM node per shape, positioned by its own node center (`cx/cy`), so the cluster composition matches
  Figma and nothing is clipped by a shared box.
- **Figma MCP transport/timeouts.** Heavy `get_design_context`/`get_metadata` on a whole card can
  time out; `get_screenshot`/`get_variable_defs` stay reliable, and switching transport (not
  eyeballing) usually recovers the full spec. Which server + Dev Mode setup + the fallback order live
  in `setup.md` (Figma access) — read it once when MCP calls misbehave.

## Motion & seamless loops (feeds 06a-animate, 06c-flow, 07-export)
- **Loop shapes** (`motion`): yoyo (mirror reverse — free seamlessness), continuous
  (`repeat:-1`), forward-reset (engineer end-state == start-state when a phase must not reverse).
- **Seam-proof multi-oscillator loops:** when several non-commensurate motions must loop together,
  pick a loop length `L`, **snap every oscillator's period to an exact integer divisor of `L`**,
  and model a `sine.inOut` yoyo as `osc(t)=amp*(1−cos(2π(t−delay)/period))/2`. Because each period
  divides `L`, `value(0)==value(L)` AND `velocity(0)==velocity(L)` (C1-continuous, no jump/kink).
  Nudge a duration slightly (e.g. 0.32→0.30s) so `L` lands on a whole frame count.
- **Prove it** — verify `L/period ∈ ℤ` for every oscillator, that discrete cyclers return to their
  t=0 state at `t=L`, and render boundary stills (frame 0 vs frame N−1). Don't assert seamlessness.
- **Element reuse:** duplicated shared elements cause flashing/popping/misalignment at transitions;
  a shared element must be one continuous DOM node carried across frames.
- **transform-origin of a 0×0 wrapper** (`position:absolute; left:0; top:0`, only absolute
  children) resolves to `0px 0px` — GSAP pivots about the stage origin. Match it in a Remotion port
  (`transformOrigin:'0px 0px'`, `translate()` before `rotate()`).

## GSAP → Remotion port (feeds 07-export; full recipe in `export-as-gif`)
- Everything is `f(useCurrentFrame())`; CSS transitions/animations don't render — use
  `interpolate`/`spring`/`Easing`. GSAP-ease → Remotion `Easing` cheat-sheet is in `export-as-gif`.
- **Node ≥18** required (Remotion 4); if the system default is older it throws `EBADENGINE`. Select a
  node ≥18 portably (don't hardcode a personal nvm path) — full recipe + doctor check in `setup.md`.
- Figma SVGs with `fill="var(--x,#fallback)"` render the fallback via `<Img staticFile()>` — copy
  assets into `remotion/public`, no patching needed.
- Verify with **stills at boundary/key frames before rendering video**; a full-res photographic GIF
  is heavy (256-color) — offer `--scale=0.5` / `--every-nth-frame=2` or steer to MP4.

## The QA philosophy (feeds 04, 06b, 06c, 08)
- **Strict, then specific.** The ≥95 static gate and intent-matching are deliberately demanding.
  On failure, emit a precise, actionable fix-prompt naming element + property + current→expected —
  never "looks off," never a from-scratch rebuild.
- **Both structured and visual.** Structured (MCP tokens/coords + measurement) AND screenshots;
  neither alone is sufficient.
- **Prove before asserting done.** For anything looped, timed, or measured, show the check —
  boundary stills, value/velocity equality, `offset==figma×scale` — rather than claiming it.

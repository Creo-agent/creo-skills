# Pipeline knowledge base (product animations — deltas only)

This pipeline shares the `skills/animations-and-motion-skills/` group's reference layer. **Read those first**, then this
doc — it holds *only* what's specific to product animations (the shared clock and the cursor). Don't
re-derive what the shared layer already owns.

Shared layer (prefer these — see the "Shared animation env" note in `skill.md`):
- [`../../figma-to-animation/references/knowledge.md`](../../figma-to-animation/references/knowledge.md)
  — mechanical lessons: **measurement discipline** (scaled-stage `getBCR` vs `offsetWidth`,
  magnitude-check, `offset==figma×scale`), **Figma fidelity** (SVG-at-`.png`,
  `preserveAspectRatio="none"`, dropped gradient strokes, MCP transport/timeouts), GSAP→Remotion port.
- [`../../figma-to-animation/references/animation-knowledge.md`](../../figma-to-animation/references/animation-knowledge.md)
  — semantic layer: motion roles, timing/easing heuristics, `prefers-reduced-motion`, brand motion.
- [`setup.md`](setup.md) — prereqs for this pipeline (defers to the sibling for the full tool table).

Engine bindings (which sibling each stage reuses) are the Engine Registry table in `skill.md`:
recreation → `../frame-building/`, UI motion → `../motion/`, cursor primitives → `../gsap/`,
export → `../export-as-gif/`, rendered critique → the `design-critique` skill.

---

## The shared clock (this pipeline's defining discipline)

The one thing the general pipeline doesn't need and this one lives or dies on. Full contract:
[`timeline-clock.md`](timeline-clock.md). The essentials:

- Cursor and UI motion share **one** GSAP `master` timeline with labels drawn 1:1 from the planning
  table. This makes sync **structural** — a cursor click and its UI reaction sit on the same label, so
  they fire on one clock. Not reviewed after the fact; impossible to drift.
- **Never introduce a second time source.** `setTimeout`, a second `gsap.timeline()`, or CSS
  `animation-delay` measured from page load all create an independent clock that drifts against
  `master`. Any timeline-table event must live on `master`; only purely-hover `:hover` CSS
  transitions (never in the table) may stay outside it.
- **Units are seconds** end-to-end (planning table `Time (s)` ↔ GSAP seconds). Convert to ms only at
  a library boundary, never in the timeline.
- The shared layer's measurement discipline matters **doubly** here: cursor target coordinates come
  from those measurements, so a scale-inflation bug puts the cursor in the wrong place at every click.
  Extract targets at the timeline viewport, once, after fonts+images load.

## Cursor realism & fidelity

- **Chirality — never `scaleX(-1)`/`scaleY(-1)` the cursor asset.** A mouse cursor is asymmetric; a
  flip mirrors it into the wrong orientation. If it must rotate, use an explicit `rotate` and position
  on its bounding-box center (the chirality rule from [`../../frame-building/`](../../frame-building/)).
- **Move, don't teleport.** Every position change over distance is a tween with `power2.inOut`
  (accelerate out of a stop, decelerate into the target) — no constant-velocity straight lines, no
  instant jumps. Use [`../../gsap/`](../../gsap/) position parameters to land arrivals exactly on labels.
- **Click press.** Scale the cursor to ~85–90% and back over ~100 ms (`scale:0.88, yoyo:true,
  repeat:1, duration:0.05`) on the click label — the same label the UI state-change tween sits on.
- **One continuous element.** A single `#cursor` node carried across the whole timeline, never
  re-created per event (a duplicate flashes).

## QA philosophy (product specifics)

The shared QA philosophy ("strict then specific"; structured + visual; prove before asserting) applies.
Product-specific: the ≥95 design gate is a computed rubric ([`rubric.md`](rubric.md)); the timing/sync
gate reads **actual times off `master`** ([`timing-rubric.md`](timing-rubric.md)) rather than any
self-reported log — a cursor↔UI offset of anything but 0 ms means the shared-clock contract was broken.

# motion — run procedure

Add GSAP motion to an already-built static frame (build it first with `../frame-building/`). This skill
bundles four motion recipes as reference docs under `references/`; pick the recipe, load its doc, follow
it. Consult `../gsap/` for library specifics.

## Recipes (load the matching reference doc)

1. **Seamless loops** — `references/loops.md`
   Choose the loop shape (yoyo / restart / continuous / **forward-reset** — yoyo for clean reveals,
   forward-reset when a distinct end-screen must NOT play in reverse). One GSAP timeline (`repeat:-1`,
   `yoyo`/`repeatDelay`, or a forward timeline whose end state is engineered to equal its start).
   Ramping stagger, collapse-to-a-point (+ emerge-from-a-point), directional lead, cross-fades.

2. **Orchestrated UI entrance** — `references/ui-entrance.md`
   Multi-beat entrance inside a loop. On a **yoyo** loop, author the entrance on the forward pass *as a
   leave* (visible → hidden); the reversal replays it as an entrance for free. On a **forward-reset**
   loop, author explicit enter/exit tweens with independent stagger direction. Keep beats as
   `BASE + offset` constants, one easing family.

3. **Marquee / carousel** — `references/marquee.md`
   Each row = a track holding ≥2 identical content groups; an always-on tween translates by one
   group-width and modulo-wraps (`gsap.utils.wrap`) — seamless, per-row speed/direction for parallax.
   Measure copy-width only after fonts+images load. Ports to Remotion frame-math for export.

4. **Word ticker** — `references/word-ticker.md`
   Fixed-height clip + two stacked word slots; a one-step wipe (outgoing rolls up, incoming rolls in,
   clip width morphs `curW → nextW`), in GSAP (live) and Remotion (export). Keep the headline centered
   with a fixed full-width block. Measure word widths safely (avoid the scale-inflation bug). The
   ticker is the clock for a seamless loop (`L = WORDS.length × P`, landed on a whole frame count).

## Non-negotiables
- Prove loops seamless (value + velocity at the boundary; render boundary stills) — don't assert it.
- Element reuse (one continuous DOM node across states). Named-constant timing, one easing family.
- Verify deterministically by seeking timeline states / sampling `.time()`.

## Handoff
Motion done → [`../export-as-gif/`](../export-as-gif/) to render to GIF/MP4. For the full orchestrated
pipeline, use [`../figma-to-animation/`](../figma-to-animation/).

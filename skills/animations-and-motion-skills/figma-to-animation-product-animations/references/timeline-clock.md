# The shared master timeline (the sync contract)

This is the one primitive the product pipeline uniquely needs, and the mechanism that makes the
pipeline's central promise — *cursor and UI motion are frame-accurate to each other* — **structural
rather than aspirational**. Read this before running `product-animation` or `cursor-animation`.

## The problem it solves

Without a shared clock, `product-animation` and `cursor-animation` each read the planning timeline
table independently and each author their own `setTimeout`/`requestAnimationFrame` chain. Two
independent timers **drift** — different start origins (page load vs script start vs first paint),
`s` vs `ms` unit mismatches, accumulated rounding. A cursor that "clicks" at 1.2 s and a button that
goes active at "1.2 s" on a different clock are visibly offset. `product-animation-qa` calls this
"the most common failure point." The fix is to make it impossible: **one clock, one source of time.**

## The contract

Every run scaffolds a single shared module, `timeline.js`, that owns **one** GSAP timeline:

```js
// timeline.js — the single source of time for this prototype.
// Both product-animation and cursor-animation import THIS master. Neither creates its own timer.
export const master = gsap.timeline({ paused: true });

// Labels come 1:1 from the planning timeline table's "Label" column (see product-animation-planning).
// One label per planned timestamp; the label name IS the contract between the two skills.
master.addLabel("cursor-enter",   0.0);
master.addLabel("arrive-row-3",   0.4);
master.addLabel("hover-row-3",    0.4);
master.addLabel("click-row-3",    1.2);
master.addLabel("expand-row-3",   1.2);
master.addLabel("panel-in",       1.5);
```

Rules:

1. **One timeline, `paused:true`.** The run controls playback (`master.play()`), and QA/export drive
   it deterministically (`master.seek(t)`). Nothing animates off a wall-clock timer.
2. **Labels are the shared vocabulary.** Each row of the planning table emits a stable label
   (`click-row-3`), placed at that row's `Time (s)`. Both skills reference the *label*, never a raw
   numeric offset — so if planning re-times an event, both skills move together automatically.
3. **`product-animation` adds UI tweens at labels:**
   ```js
   master.to("[data-anim-id=table-row-3]", { height: 220, duration: 0.3, ease: "power2.out" }, "expand-row-3");
   ```
4. **`cursor-animation` adds cursor tweens to the SAME `master` at the SAME labels:**
   ```js
   master.to("#cursor", { x: 512, y: 318, duration: 0.4, ease: "power2.inOut" }, "arrive-row-3");
   master.to("#cursor", { scale: 0.88, duration: 0.05, yoyo: true, repeat: 1 }, "click-row-3");
   ```
5. **The click handoff is one label, two tweens.** The cursor press tween and the UI state-change
   tween both sit at `"click-row-3"`. They fire on one clock → zero offset is guaranteed, not
   reviewed.
6. **Never mix in a second time source.** No `setTimeout`, no CSS `animation-delay` off page load, no
   second `gsap.timeline()` running in parallel. Micro-interactions that are purely hover-driven in a
   *live* build may use CSS `:hover` transitions, but any event that appears in the timeline table
   must live on `master`.

## Units

The planning table is authored in **seconds** (`Time (s)`), and GSAP timelines are in seconds — so
seconds is the canonical unit end-to-end. Convert to ms only at a library boundary that demands it,
never in the timeline itself.

## Why GSAP (the chosen library)

GSAP is the house standard across the `skills/animations-and-motion-skills/` group (`gsap`, `motion`), loads from CDN
with no install, and its **timeline** gives exactly what the sync
contract needs: labels, [position parameters](../../gsap/PROMPT.md) (`"<"`, `"<0.2"`, `"label+=0.1"`),
one shared clock, and `seek()`/`pause()` for deterministic QA. It also ports cleanly to Remotion for
export (`master.seek(frame / fps)` ↔ `f(useCurrentFrame())`). `animation-library.md` at the project
root may override this per project, but the shared-clock contract above still applies whatever the
library — one timeline, labels from the plan, both skills on it.

## What QA gets for free

Because motion is one seekable timeline, `product-animation-qa` becomes measurable instead of
vibes-based:

```js
master.pause();
master.seek(master.labels["click-row-3"]);   // jump to the exact planned instant
// screenshot; assert cursor is over row 3 AND row 3 is in its active state at this same seek
```

Actual event times are readable straight off `master.labels` and each tween's `startTime()` — no
self-reported log to trust. See `references/timing-rubric.md`.

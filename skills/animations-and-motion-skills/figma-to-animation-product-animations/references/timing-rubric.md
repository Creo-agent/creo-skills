# Animation QA rubric — the timing & sync gate (product-animation-qa)

The final gate before export. Unlike a visual-fidelity score, this gate is a set of **boolean
checks** measured against the planning timeline — because motion now lives on one seekable GSAP
`master` timeline (`references/timeline-clock.md`), every check is *observed*, not read off a
self-reported log. **Pass = all checks true.** On failure, emit a targeted fix-prompt and route back
to `product-animation` and/or `cursor-animation`. The loop that consumes this is
`workflows/animation-qa-loop.js`.

## How to obtain actual times (the key difference from eyeballing)

The prototype exposes the shared `master`. Read planned vs actual directly:

```js
master.pause();
master.labels;                              // { "click-row-3": 1.2, ... } — planned instants
master.getById?.(...) // or inspect children:
master.getChildren(true, true, false).map(t => ({ target: t.vars, start: t.startTime(), dur: t.duration() }));
```

- **Actual event time** = the tween's `startTime()` on `master` (seconds, same origin as the plan).
- **Sync instants** = seek to a label and screenshot: `master.seek(master.labels["click-row-3"])`.

Never accept an implementation's written "I set this to 1.2s" as evidence — verify it off `master`.

## The checks

| Check | Passes when | How to measure |
|---|---|---|
| **Event completeness** | every timeline row has exactly one implemented tween on `master`; no extra unplanned events | diff `master` children against the plan's rows by label |
| **Timing accuracy** | each event's `startTime()` is within **±50 ms** of its planned `Time (s)`; each duration within ±50 ms of planned `Duration` | read `startTime()`/`duration()` per tween |
| **Cursor ↔ UI sync** | for every coincident pair (cursor click ↔ UI active; cursor arrival ↔ hover), both tweens sit at the **same label** with **0 ms** offset | assert both tweens' `startTime()` == `master.labels[label]`; seek there and screenshot to confirm visually |
| **Easing fidelity** | the ease on each tween matches the plan's intent (a planned `spring`/`elastic` isn't `none`/linear; a planned `ease-out` uses a `power*.out`/`sine.out`) | read each tween's `vars.ease` |
| **Dependency ordering** | any event marked `Depends On` starts at or after its prerequisite completes | compare `startTime()` vs prerequisite `startTime()+duration()` |
| **Coherence** | scrub `master` end-to-end (`master.seek(t)` across the range) — reads as one natural interaction, no teleporting cursor, no popping/flashing elements | seek sampling + `design-critique` on a few key seeks |

## Tolerances (why ±50 ms but 0 ms for sync)
- A ~50 ms drift on an *isolated* event is not visually detectable, so timing accuracy allows it.
- A cursor click and its UI reaction are **one event**; any offset between them reads as broken. The
  shared-label contract makes this 0 ms by construction — so a nonzero cursor↔UI offset means the
  contract was violated (someone used a raw offset or a second timer) and is a **high-severity**
  fix-prompt, not a tolerance discussion.

## Hard-fail overrides (force a fix loop regardless)
- Any event implemented with a **second time source** (`setTimeout`, a separate `gsap.timeline()`,
  CSS `animation-delay` off page load) instead of the shared `master` — this is the drift bug the
  whole contract exists to prevent. Grep the animation code for `setTimeout` / a second `timeline(`.
- Any **missing** planned event, or any element that **teleports** (a cursor jump with no movement
  tween over distance).
- Cursor↔UI offset > 0 ms on a coincident pair.

## Fix-prompt format (what animation-qa hands back)
> `#cursor` click press is at `startTime()` 1.35s but label `click-row-3` is 1.2s — move the press
> tween onto the `"click-row-3"` label so it shares the clock with the row-expand tween.
> `[data-anim-id=detail-panel]` slide-in uses `ease:"none"`; plan says `spring` — use
> `elastic.out(1, 0.5)` or a GSAP spring equivalent.

Name the element/selector, the observed value (from `master`), the planned value, and the labelled
fix. Vague feedback will not converge the loop.

# Cursor Animation — Run Procedure

Animate a realistic mouse cursor on a product UI. All tweens go on the shared `master`
at labels from the timeline plan — cursor movement and UI reactions fire at the same clock tick.

## Step 0 — Standalone setup (skip if called by the orchestrator)

If invoked directly, ask for:
- **HTML/CSS file** — the rendered product prototype. Required.
- **Timeline plan** — `timeline.md` from `product-animation-planning`. Required for cursor
  positions and click events. If absent, ask the user to describe the interaction flow.
- **Shared master** — check if `timeline.js` exists (from `product-animation`). If not, scaffold:

```js
// timeline.js
import { gsap } from "https://cdn.skypack.dev/gsap";
export const master = gsap.timeline({ paused: true });
```

- **Cursor asset** — if no cursor SVG exists in the project, use this default and place it
  in the `<body>`, initially off-screen:

```html
<div id="cursor" style="
  position: fixed; width: 20px; height: 20px; pointer-events: none; z-index: 9999;
  transform-origin: 2px 2px; left: -100px; top: -100px;
">
  <svg viewBox="0 0 20 20" width="20" height="20" xmlns="http://www.w3.org/2000/svg">
    <polygon points="2,2 2,16 6,12 9,18 11,17 8,11 14,11"
             fill="white" stroke="black" stroke-width="1.2"/>
  </svg>
</div>
```

## Step 1 — Extract target coordinates

For each interactive element the cursor must reach, get its actual rendered position at the
**declared viewport** — using `getBoundingClientRect()` at runtime:

```js
const el = document.querySelector('[data-anim-id="table-row-3"]');
const rect = el.getBoundingClientRect();
const clickX = rect.left + rect.width * 0.15; // left side reads more natural than dead center
const clickY = rect.top  + rect.height * 0.5;
```

Always measure at the declared viewport size. Coordinate drift between viewport sizes will
desync the cursor from the UI tweens in `product-animation`.

## Step 2 — Plan natural movement paths

Real cursor movement accelerates out of a stop and decelerates into a stop. Each move:
- Uses `power2.inOut` easing (or `power1.inOut` for very short hops <80px)
- Duration proportional to distance:

| Distance | Duration |
|---|---|
| <100px | 200–300ms |
| 100–300px | 300–450ms |
| 300–600px | 400–600ms |
| >600px | 500–700ms |

- Lets the cursor "rest" at a position for the duration of the hover/click event before
  the next movement tween begins

## Step 3 — Place tweens on master at plan labels

```js
import { master } from './timeline.js';

// Move to row 3 — at the same label as the hover activation in product-animation
master.to("#cursor", {
  left: clickX, top: clickY, duration: 0.35, ease: "power2.inOut"
}, "arrive-row-3");

// Click press — at the same label as the UI state-change tween
master.to("#cursor", {
  scale: 0.88, duration: 0.05, ease: "power1.in", yoyo: true, repeat: 1
}, "click-row-3");
```

**Why labels, not raw timestamps:** `product-animation` adds UI tweens at the same labels.
Both skills using `"click-row-3"` guarantees the cursor press and the row expansion fire on
the same clock tick — 0ms offset. Re-deriving a timestamp would drift.
See `../references/timeline-clock.md`.

## Step 4 — Vary speed realistically

- Never use `ease:"none"` (linear) for cursor movement over any visible distance.
- Default: `"power2.inOut"` for standard moves; `"power1.inOut"` for short hops (<80px).
- Pause naturally between events by letting the cursor rest at a position rather than
  starting the next move immediately.

## Step 5 — Click press effect

On every click event, add a brief scale-down-and-back at the click label. This ~100ms press
lands exactly when the UI state change fires — the two look like one physical click:

```js
master.to("#cursor", {
  scale: 0.88,
  duration: 0.05,
  ease: "power1.in",
  yoyo: true,
  repeat: 1,
}, "click-row-3");
```

## Step 6 — Never flip the cursor (chirality rule)

A mouse cursor arrow is asymmetric. Never apply `scaleX(-1)` or `scaleY(-1)` — it mirrors
the cursor into the wrong orientation and immediately reads as wrong. If rotation is needed
(e.g. cursor tilts toward a target), use `rotation` and set `transformOrigin` to the visual
tip (`"2px 2px"` for the standard arrow shape).

## Step 7 — One continuous node, no teleporting

- One `#cursor` element throughout the entire animation.
- Never remove-and-re-add the cursor between events.
- Never use `gsap.set("#cursor", { left: X, top: Y })` to jump position over a visible
  distance — use a tween. `gsap.set` is only for the initial off-screen position.
- Every position change over visible distance must be a tween.

## Step 8 — Idle behavior (optional)

If the plan includes pauses longer than ~1s, consider a subtle idle micro-movement
(3–5px drift over 2–3s, `sine.inOut`, `yoyo:true, repeat:-1`). Skip if the pause is short
or if it risks looking jittery. Only add if it genuinely improves the "real user" feel.

## Output

1. **Cursor element + animation code** in the HTML file or `timeline.js`.
2. **Cursor event log** for QA:

```markdown
## Cursor Event Log
| Label | Action | Target Element | X | Y | Duration |
|---|---|---|---|---|---|
| cursor-enter | enter from off-screen | — | -50→400px | 200px | 400ms |
| arrive-row-3 | move to row 3 | table-row-3 | 400→180px | 200→312px | 350ms |
| click-row-3 | click press | table-row-3 | 180px | 312px | 100ms |
```

## Handoff

- **`product-animation`** — shares the same `master` and labels; cursor and UI are in sync.
- **`product-animation-qa`** — validates cursor timing and cursor↔UI sync (0ms tolerance).

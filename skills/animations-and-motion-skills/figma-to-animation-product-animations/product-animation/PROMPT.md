# Product Animation — Run Procedure

Apply GSAP motion to QA-approved product HTML/CSS per the timeline plan. Every tween goes on
one shared `master` at a label from the plan — cursor and UI are synchronized by construction.

## Step 0 — Standalone setup (skip if called by the orchestrator)

If invoked directly, ask for:
- **HTML/CSS file** — QA-approved product markup. Required.
- **Timeline plan** — `timeline.md` from `product-animation-planning`. Required. If absent,
  offer to run `product-animation-planning` first, or ask the user to describe the events.
- **Shared master** — check if `timeline.js` already exists. If not, scaffold it:

```js
// timeline.js
import { gsap } from "https://cdn.skypack.dev/gsap";
export const master = gsap.timeline({ paused: true });
```

Import or link `timeline.js` from the HTML file so both this skill and `cursor-animation`
share the same `master` instance.

## Step 1 — Load the timeline

Read every row in the timeline plan as a **required** implementation target. Do not skip any
row and do not add events not in the plan. If a row's element is not in the HTML (missing
`data-anim-id`), stop and flag it — `product-design-recreation` needs to add the hook.

## Step 2 — Add each event as a tween on master at its label

```js
// master.to(element, vars, "label")
const el = document.querySelector('[data-anim-id="table-row-3"]');
master.to(el, { height: "auto", duration: 0.3, ease: "power2.out" }, "click-row-3");
```

**One-clock rule:** Never use `setTimeout`, a second `gsap.timeline()`, or CSS `animation-delay`
off page load. Those create a second clock that drifts from the cursor. All tweens go on `master`
at a label. See `../references/timeline-clock.md`.

Map event types to implementation:

| Timeline type | GSAP pattern |
|---|---|
| hover | Short tween on the label; purely-CSS `:hover` NOT in the timeline table may stay CSS |
| click / active | `scale` micro-interaction or state-class toggle tween |
| pop-in / pop-out | `autoAlpha` + `scale` 0.95→1; see `../motion/` patterns |
| expand / collapse | `scaleY` + `autoAlpha` or `height`; use `power2.out` |
| slide-in | `x` or `y` translate + `autoAlpha`; use `power2.out` |
| fade-in | `autoAlpha` with `"power1.inOut"` |

Route to `../motion/` for pop-in, stagger, and forward-reset patterns.
Route to `../gsap/` for easing family reference and timeline position parameter syntax.

## Step 3 — Respect easing intent

| Plan says | GSAP ease |
|---|---|
| ease-out | `"power2.out"` or `"sine.out"` |
| ease-in-out | `"power2.inOut"` or `"sine.inOut"` |
| spring | `"elastic.out(1, 0.5)"` or GSAP spring |
| ease-in | `"power2.in"` |
| linear | `"none"` |

Never leave a planned spring as `"none"` or linear.

## Step 4 — Respect dependencies

An event marked "depends on X" must not fire until X completes. Use the timeline position
parameter to place it after the prerequisite label ends:

```js
// panel-in starts after click-row-3's tweens finish
master.to(panel, { x: 0, autoAlpha: 1, duration: 0.35 }, ">=click-row-3");
```

## Step 5 — Keep durations within product norms

Unless the plan explicitly differs:
- Micro-interactions (hover, button press): 100–200ms
- Pop-ins / expansions: 200–400ms
- Slide-ins / larger transitions: 300–450ms

## Step 6 — Sync with cursor-animation via shared labels

For every event involving the cursor (hover on arrival, click-triggered state change), the UI
tween sits on the **same label** the cursor tween uses. Do not re-derive a raw timestamp.
The cursor click at `"click-row-3"` and the row expansion at `"click-row-3"` fire at the same
clock tick — 0ms offset by construction.

## Output

1. **Updated HTML/CSS/JS** with all timeline events on `master`.
2. **Implementation note** mapping each planned event to the technique used (for QA):

```markdown
## Implementation Notes
| Label | Element | Technique | Ease | Duration |
|---|---|---|---|---|
| hover-row-3 | table-row-3 | background autoAlpha | sine.out | 150ms |
| click-row-3 (UI) | table-row-3 | scaleY expand + autoAlpha | power2.out | 300ms |
| panel-in | detail-panel | x slide + autoAlpha | power2.out | 350ms |
```

## Handoff

- **`cursor-animation`** — runs in parallel, sharing the same `master` and labels.
- **`product-animation-qa`** — validates the final animated result against the original plan.

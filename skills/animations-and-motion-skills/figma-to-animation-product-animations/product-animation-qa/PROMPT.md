# Product Animation QA — Run Procedure

Final gate before export. Reads actual values off the shared GSAP `master` — not self-reported
logs — and validates against the original timeline plan.

## Step 0 — Standalone setup (skip if called by the orchestrator)

If invoked directly, ask for:
- **Animated HTML file** — the prototype with both `product-animation` and `cursor-animation`
  implemented. Required.
- **Timeline plan** — `timeline.md` from `product-animation-planning`. Required as ground truth.
- **Viewport** — declared render size. Required; render the HTML at this exact size.

**Expose master for inspection.** Add to a debug `<script>` block or the browser console:
```js
import { master } from './timeline.js';
window._master = master;
```

Then inspect in DevTools:
```js
_master.labels
// → { "arrive-row-3": 0.4, "click-row-3": 1.2, "panel-in": 1.5 }

_master.getChildren().map(t => ({
  label: t.vars.id,
  start: t.startTime(),
  dur: t.duration(),
  ease: t.vars.ease
}))

_master.seek("click-row-3") // scrub to label, take screenshot
```

## Check 1 — Event completeness

Diff `master`'s children against the plan's rows by label:
- Every plan row has exactly one tween on `master` at its label
- No extra tweens for events not in the plan
- Flag: missing event (plan row with no tween) or extra event (tween at unlisted label)

## Check 2 — Timing accuracy (±50ms tolerance)

For each tween:
- `tween.startTime()` within **±50ms** of its plan `Time (s)`
- `tween.duration()` within **±50ms** of plan duration

~50ms drift on an isolated event is visually undetectable. Larger is a real issue — flag it
with the observed vs planned values.

## Check 3 — Cursor↔UI sync (0ms tolerance — hard-fail)

For every coincident pair (cursor click + UI state change sharing a label):
- Both tweens must be at the **same label** with **0ms offset**
- Seek `master` to the label and screenshot — cursor and UI must visually coincide
- Any nonzero offset means the shared-clock contract was violated (raw timestamp or second
  timer) — **HARD-FAIL**

Pre-check: `grep -r "setTimeout\|new gsap.timeline\|animation-delay" <project>` — any hit
is a hard-fail. The only clock is `master`.

## Check 4 — Easing fidelity

Each `tween.vars.ease` must match the plan's intent:
- Planned "spring" → must be `"elastic.*"` or a GSAP spring, not `"none"` or `"power*.out"`
- Planned "ease-out" → must be `"power*.out"` or `"sine.out"`
- Planned "ease-in-out" → must be `"power*.inOut"` or `"sine.inOut"`
- Planned "linear" → `"none"` is correct

## Check 5 — Dependency ordering

For each "Depends On" relationship in the plan:
- `dependent.startTime() ≥ prerequisite.startTime() + prerequisite.duration()`
- Flag any inversion (dependent fires before prerequisite ends)

## Check 6 — Coherence

Scrub `master` end-to-end (`master.seek(t)` at multiple points):
- Reads as one natural interaction — no jarring jumps or out-of-order events
- No teleporting cursor (every position change over visible distance is a tween)
- No popping/flashing elements (all entrances are smooth)

## Hard-fail criteria

Any of these is an automatic FAIL regardless of other checks:
- Second time source found (`setTimeout`, second `gsap.timeline()`, `animation-delay`)
- Teleporting cursor (position changes without a covering movement tween)
- Nonzero cursor↔UI offset on any coincident pair

## Report Format

```markdown
# Animation QA Report: [Design Name]

## Result: PASS / FAIL

## Checks
| Check | Status | Details |
|---|---|---|
| Event completeness | PASS | All 6 plan events implemented |
| Timing accuracy | PASS | All within ±50ms |
| Cursor↔UI sync | FAIL | click-row-3: cursor tween at 1.2s, UI tween at 1.25s — 50ms offset |
| Easing fidelity | PASS | — |
| Dependency ordering | PASS | — |
| Coherence | PASS | — |
| Hard-fail: second clock | PASS | No setTimeout / second timeline found |
| Hard-fail: cursor teleport | PASS | — |

## Event Comparison
| Planned Time | Label | Event | Impl. Time | Delta | Notes |
|---|---|---|---|---|---|
| 1.2s | click-row-3 | Cursor click | 1.2s | 0ms | — |
| 1.2s | click-row-3 | Row 3 expand | 1.25s | +50ms | Label present but raw offset added |

## Issues Found
- click-row-3: UI tween startTime 1.25s, cursor tween 1.20s — 50ms offset violates the shared-label contract. Fix: move UI tween to the label (remove the +0.05 offset).

## Recommendation
FAIL — send back to product-animation for the click-row-3 offset fix, then re-run QA.
```

## Handoff

- **PASS** → confirm the export skill path and hand off to `export-as-gif` for GIF/MP4 render.
- **FAIL** → send report to `product-animation` and/or `cursor-animation` for targeted fixes,
  then re-run this skill. **Third consecutive FAIL on the same artifact** → stop and escalate
  to the user rather than looping further.

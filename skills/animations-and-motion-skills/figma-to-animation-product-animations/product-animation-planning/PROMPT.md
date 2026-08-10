# Product Animation Planning — Run Procedure

Analyze a Figma product design and produce a timestamped animation timeline. This is the
source of truth for all downstream skills — plan precisely enough that two different skills
implementing different parts will end up synchronized.

## Step 0 — Standalone setup (skip if called by the orchestrator)

If invoked directly, gather:
- **Figma design** — URL, exported image, or screenshot. Required. Ask if absent.
- **User intent notes** *(optional)* — e.g., "this is a table row expansion flow", "focus on
  the modal confirmation". Helps narrow the flow. Without notes, infer the most likely
  single-user flow from the design.
- **Design system reference** *(optional)* — token names help write precise element identifiers,
  but the plan can proceed from the visual alone.
- **Viewport** — ask for the target render size (default 1440×900). Declare it at the top of
  the timeline document — all downstream skills must render at this exact size.

## Step 1 — Identify the static structure

What are the distinct UI regions/components? (nav, table, modal, buttons, form fields, cards,
sidebars, etc.) Name them in a way that will be stable as `data-anim-id` values later.

## Step 2 — Identify plausible interactive elements

For each component: does it realistically respond to hover, click, focus, drag, or scroll in a
real product? Only flag elements where an interaction is genuinely expected by users. Do not
invent interactions on purely static content.

## Step 3 — Infer the user story

Pick **one coherent flow** a viewer should see. Examples:
- "User hovers a table row, clicks to expand it, sees a detail panel slide in."
- "User moves to a Delete button, clicks, a confirmation modal fades in."

If the user provided an intent note, honor it. If not, pick the most natural single interaction
visible in the design. For complex designs with multiple distinct flows, plan each as a separate
timeline file (`timeline-1.md`, `timeline-2.md`). Do not merge multiple flows into one document.

## Step 4 — Sequence the flow

Order the interactions into a logical, minimal sequence that tells that story clearly.
Start from cursor-off-screen, end when the UI has settled after the final event.

## Step 5 — Assign timing and easing

Standard timing norms (adjust if the design calls for something different):

| Interaction type | Duration range | Default easing |
|---|---|---|
| Micro-interaction (hover highlight, button press) | 100–200ms | ease-out |
| Pop-in / pop-out | 200–300ms | ease-out or spring |
| Expand / collapse (panel, row) | 250–400ms | ease-out |
| Slide-in (modal, drawer) | 300–400ms | ease-out |
| Fade-in overlay | 200–300ms | ease-in-out |
| Cursor movement short (<200px) | 300–400ms | ease-in-out |
| Cursor movement long (>400px) | 400–600ms | ease-in-out |

Avoid anything longer than ~600ms for a single transition unless it is a deliberate slow reveal.

## Step 6 — Note dependencies

For each event, ask: can it start before a prior event finishes, or must it wait?
- **Sequential:** "panel-in cannot start until click-row-3 completes"
- **Simultaneous:** cursor arrives at button AND button hover activates at the same timestamp

## Step 7 — Flag cursor involvement

For every click or hover event, note the cursor position (which element's center/click-point)
and the movement from the prior cursor position. The `cursor-animation` skill reads this to
plan natural movement paths.

## Step 8 — Assign labels

Give every event a short, stable **kebab-case label** (e.g. `arrive-row-3`, `click-row-3`,
`panel-in`). Rules:
- Labels become GSAP timeline labels referenced by both `product-animation` and `cursor-animation`
- Coincident events (a cursor click AND the UI state change it triggers) **share one label** —
  this is the sync contract. A cursor click at `"click-row-3"` and the row expansion at
  `"click-row-3"` fire on the same clock tick with zero offset by construction.
- See `../references/timeline-clock.md` for the full shared-clock contract.

## Timeline Output Format

Save as `timeline.md` (or return inline). One file per flow.

```markdown
# Animation Timeline: [Design Name]

## Viewport
[Fixed rendering viewport, e.g. 1440×900 — all downstream skills render/measure at this exact size]

## Flow Summary
[1–2 sentence description of the user story being animated]

## Timeline

| Time (s) | Label | Event | Element | Type | Duration | Easing | Depends On |
|----------|-------|-------|---------|------|----------|--------|------------|
| 0.0 | cursor-enter | Cursor enters frame from off-screen | cursor | movement | 0.4s | ease-in-out | — |
| 0.4 | arrive-row-3 | Cursor arrives at row 3 | cursor | movement | 0.3s | ease-in-out | cursor-enter |
| 0.4 | hover-row-3 | Row 3 hover highlight activates | table-row-3 | hover | 0.15s | ease-out | arrive-row-3 |
| 1.2 | click-row-3 | Cursor click on row 3 | cursor | click | 0.1s | ease-in-out | arrive-row-3 |
| 1.2 | click-row-3 | Row 3 expands | table-row-3 | expand | 0.3s | ease-out | click-row-3 |
| 1.5 | panel-in | Detail panel slides in | detail-panel | slide-in | 0.35s | ease-out | click-row-3 |

Note: `click-row-3` appears twice — cursor click and row expansion share one label.
That shared label guarantees they fire simultaneously in both downstream skills.

## Notes for Downstream Skills
- [Any special notes for design recreation, animation, or cursor skills]
```

## Handoff

Pass `timeline.md` to:
- **`product-design-recreation`** — needs the element list to know which items require `data-anim-id` hooks.
- **`product-animation`** — reads timing/easing/label per event to implement tweens on the shared master.
- **`cursor-animation`** — reads cursor positions and timestamps for movement path planning.
- **`product-animation-qa`** — uses the original plan as the ground truth to validate against.

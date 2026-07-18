# figma-to-animation-product-animations

Turn a **Figma product UI** into a fully animated, pixel-accurate HTML/CSS/JS prototype with a
realistic mouse cursor — then hand off to export. This is the **product-heavy sibling** of
`../figma-to-animation/`: same orchestrate-and-gate philosophy, but specialized for real product UIs
where fidelity to the existing design system is non-negotiable and interactions (hover, click,
expand, cursor movement) must read as one natural motion.

## When to use
- The user wants a Figma product design turned into an animated product demo/prototype.
- Accuracy to a real design system matters (not a creative reinterpretation).
- Motion involves a cursor driving UI reactions that must stay in sync.

Prefer `../figma-to-animation/` instead for a general storyboard→animation/video job with no product
UI or cursor.

## How it works
The orchestrator (`skill.md` + `PROMPT.md`) sequences six task subskills through two deterministic,
gated QA loops:

```
plan → [recreate ⇄ design-QA]≥95 → animate + cursor (one shared clock) ⇄ animation-QA → export
```

Two things make it work *properly* rather than aspirationally:

1. **One shared master timeline** (`references/timeline-clock.md`). Cursor and UI motion compile onto
   a single `gsap.timeline()` with labels drawn 1:1 from the planning table. Sync is structural —
   the cursor click and its UI reaction sit on the same label, so drift is impossible, not reviewed.
2. **Deterministic QA loops** (`workflows/`). The ≥95 design gate is a weighted rubric
   (`references/rubric.md`), and the timing/sync gate reads actual times off the `master` timeline
   (`references/timing-rubric.md`) — both computed, not eyeballed, and both looping targeted
   fix-prompts (never rebuilds) until they pass or escalate.

## Structure
```
skill.md                      orchestration (entry point) + engine registry
PROMPT.md                     executable run procedure (the 5 steps + gates)
product-animation-planning/   → timeline plan (labelled rows)
product-design-recreation/    → pixel-accurate static HTML/CSS
product-design-qa/            → ≥95 visual-accuracy gate
product-animation/            → UI motion onto the shared master
cursor-animation/             → realistic cursor onto the same master
product-animation-qa/         → timing & sync gate
references/                   timeline-clock, rubric, timing-rubric, knowledge, setup
workflows/                    design-qa-loop.js, animation-qa-loop.js (deterministic)
```

## Reuse, don't reinvent
Build/motion/export engines live as sibling skills in `../` and are referenced, never copied
(single source of truth): `frame-building`, `gsap`, `motion`, `export-as-gif`, and the
`design-critique` skill. See the engine
registry in `skill.md`.

## Prerequisites
GSAP (CDN), a Figma MCP server, a static server; Node ≥18 only for export. Doctor check in
`references/setup.md`.

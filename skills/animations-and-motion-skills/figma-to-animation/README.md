# figma-to-animation

The master **orchestrator** of the animation group. Turns a Figma frame or multi-frame storyboard
into a polished web animation (HTML/CSS/JS + GSAP) and, if asked, an exported MP4/GIF via Remotion —
by running the full pipeline and gating each stage on quality.

## When to use
"Animate this Figma", "turn these frames into an animation", "build the motion/transitions between
these designs", "make a looping animation from this storyboard", "Figma → video/gif". For a single
static card use `../frame-building/`; to grab motion off a live site use `../extract-animation-from-web/`;
to reformat an existing animation use `../resize-animation/`.

## What it does
Runs, in order: index → analyze (vision-first, per-transition deltas) → build each frame → strict
static QA (≥95, deterministic loop) → stitch → animate each frame → animation QA (deterministic loop)
→ connect the flow (seamless transitions + loop restart) → export → final validation. It sequences
and gates the **engine sibling skills** in this group; it doesn't reimplement them.

## Structure
- `SKILL.md` — the controller playbook (pipeline, engine registry, state model, cross-cutting rules).
- `PROMPT.md` — the step-by-step run procedure.
- `pipeline/` — the 10 stage docs + 3 conditional sub-skills (each usable standalone).
- `references/` — `knowledge.md` (the pipeline's hard-won lessons), `rubric.md` (the ≥95 static-QA
  rubric), `providers.md` (video-gen, stubbed/configurable).
- `workflows/` — `static-qa-loop.js` and `animation-qa-loop.js` (the two deterministic QA loops,
  invoked via the Workflow tool).

## Key files
`SKILL.md` · `PROMPT.md` · `pipeline/` · `references/knowledge.md` · `references/rubric.md` · `workflows/`

## Entry point
Load `SKILL.md`, then follow `PROMPT.md`.

## Dependencies
The engine sibling skills in this `animation/` group (referenced, not copied), the Figma MCP, and
Node.js for the Remotion export stage.

| | |
|---|---|
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-14 |

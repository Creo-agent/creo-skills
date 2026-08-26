---
name: product-animation-planning
description: |
  WHAT: Analyzes a Figma product design and produces a detailed, timestamped animation timeline — every interaction event, its timing, easing, and a kebab-case GSAP label — before any HTML/CSS or motion code is written. The timeline is the source of truth that all downstream skills read from.
  TRIGGERS: "plan the animation for this product UI", "what should move and when", "build an interaction timeline for this design", "I need an animation plan before we start coding", "turn this Figma screenshot into an animation spec". First step in the product animation pipeline.
  SUB-SKILL: figma-to-animation-product-animations routes here as its entry point. Usable standalone whenever a Figma product design needs an animation plan and none exists yet.
  NOT FOR: building HTML/CSS → use product-design-recreation/. Applying animation code → use product-animation/. Animating a marketing looping banner (not product UI) → use figma-to-animation/. Resizing or exporting → use resize-animation/ or export-as-gif/.
---

# Product Animation Planning

The entry point of the product animation pipeline. Analyzes a design and produces a
**timeline document** — a sequenced, timestamped plan of every interaction and animation event
in the prototype. Downstream skills (design, animation, cursor, QA) all read this as their
source of truth, so the plan must be precise enough that two different skills implementing
different parts of it end up perfectly synchronized.

This skill produces a spec, not code.

## When This Skill Activates

- "Plan the animation for this product UI"
- "What should move and when?"
- "Build an interaction timeline from this Figma design"
- "I need an animation spec before we start coding"
- Starting a product animation from a Figma design with no existing plan

Keywords: `animation plan`, `timeline`, `interaction spec`, `what moves`, `product animation`,
`timing`, `sequence`, `GSAP labels`, `cursor movement`, `animation planning`.

## What This Skill Does

Works through 8 analysis steps — identifies the UI structure, infers interactive elements,
picks one coherent user story, sequences the flow, assigns timing and easing, notes
dependencies, flags cursor involvement, and assigns a stable kebab-case label per event.
Outputs a markdown timeline table. Coincident events (a cursor click and the UI state change
it triggers) share one label — that label becomes the sync contract between downstream skills.

## Entry Point

Load **PROMPT.md** for the full analysis process, timing norms, the timeline output template
with a filled example, guidance on multi-flow designs, and the handoff format. The shared
clock contract is in `../references/timeline-clock.md`.

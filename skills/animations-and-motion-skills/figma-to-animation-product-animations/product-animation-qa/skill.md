---
name: product-animation-qa
description: |
  WHAT: Final timing and sync gate — validates that the animated product prototype matches the original timeline plan: correct event timing (±50ms), cursor↔UI sync (0ms offset on shared labels), correct easing, correct dependency ordering. Reads actual values off the shared GSAP master — not self-reported logs.
  TRIGGERS: "QA the animation", "validate the timing against the plan", "check the cursor sync", "does the animation match the spec?", "run the animation QA before export". Final gate before export.
  SUB-SKILL: figma-to-animation-product-animations routes here as its animation gate. Usable standalone to validate any product animation against its timeline plan.
  NOT FOR: QA-ing visual design (spacing/color) → use product-design-qa/. Building or fixing animation code → use product-animation/. Building or fixing cursor code → use cursor-animation/. Exporting to GIF/MP4 → use export-as-gif/.
---

# Product Animation QA

The final gate before export. Validates the finished animated prototype against the original
timeline plan — not against animation "vibes," but against the specific timestamps, durations,
dependencies, and easing that were planned. Reads actual tween values off the shared GSAP
`master`; never trusts self-reported implementation logs.

## When This Skill Activates

- "QA the animation against the timeline plan"
- "Check cursor↔UI sync"
- "Validate timing before we export"
- "Does the animation match the spec?"
- Automatically: after `product-animation` and `cursor-animation` both complete

Keywords: `animation QA`, `timing validation`, `cursor sync`, `master timeline`, `startTime`,
`easing fidelity`, `dependency ordering`, `hard-fail`, `animation gate`.

## What This Skill Does

Reads tween start times, durations, and easing directly off the shared `master`
(`master.labels`, `.startTime()`, `.duration()`, `.vars.ease`). Runs 6 checks against the
plan. Hard-fails on any second time source, teleporting cursor, or nonzero cursor↔UI offset
on a coincident pair. Emits a pass/fail report with fix-prompts.

## Entry Point

Load **PROMPT.md** for the full QA procedure: standalone setup, how to expose `master` for
inspection, the 6 checks with tolerances, hard-fail criteria, and the report template. The
detailed timing rubric is in `../references/timing-rubric.md`.

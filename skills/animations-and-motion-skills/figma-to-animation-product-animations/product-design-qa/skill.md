---
name: product-design-qa
description: |
  WHAT: Visual accuracy gate — validates that HTML/CSS from product-design-recreation matches the original Figma design with ≥95% accuracy across 7 weighted dimensions (positioning 25, spacing 20, color 15, typography 15, tokens 10, structure 10, radii 5). Hard-fails on missing data-anim-id hooks that a timeline event references.
  TRIGGERS: "QA the design recreation", "check if the HTML matches Figma", "does this match the design system?", "validate the markup before we animate", "score the visual accuracy". Run automatically after product-design-recreation in the pipeline.
  SUB-SKILL: figma-to-animation-product-animations routes here as its design gate. Usable standalone to validate any product HTML/CSS against its Figma source.
  NOT FOR: validating animation timing → use product-animation-qa/. Building the HTML/CSS → use product-design-recreation/. QA-ing a marketing banner → use figma-to-animation/ step 04-static-qa.
---

# Product Design QA

The ≥95% visual accuracy gate. Validates HTML/CSS against the Figma source before any
animation work begins. A real product UI must match the design system exactly — small drifts
in spacing or color compound into a UI that looks "close but off" and undermines trust.

## When This Skill Activates

- "QA this HTML against the Figma design"
- "Does the markup match the design system?"
- "Validate the recreation before we animate it"
- "Score the visual accuracy of this prototype"
- Automatically: after `product-design-recreation` in any product animation pipeline

Keywords: `QA`, `validate`, `visual accuracy`, `design check`, `rubric`, `≥95`, `pass fail`,
`data-anim-id`, `spacing`, `color`, `typography`, `token verification`.

## What This Skill Does

Runs a structured 7-dimension weighted rubric (summing to 100) against the HTML/CSS output,
reading actual computed CSS values rather than eyeballing. Issues a pass/fail report with
per-dimension scores and fix-prompts. Hard-fails if any element is missing/extra, mispositioned
by >16px, uses the wrong prominent color, has a broken asset, or is missing a `data-anim-id`
hook that a timeline event references.

## Entry Point

Load **PROMPT.md** for the full QA procedure: standalone setup, the 5-step verification
process, the weighted rubric table, the pass/fail report template, and handoff rules. The
detailed rubric is also in `../references/rubric.md`.

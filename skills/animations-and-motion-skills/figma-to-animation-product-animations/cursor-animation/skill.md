---
name: cursor-animation
description: |
  WHAT: Animate a realistic mouse cursor moving across a product UI — natural easing between positions, human-like movement paths, and a visible click/press effect synced to the timeline plan. Tweens live on the shared GSAP master at labels from the plan, so cursor movements and UI reactions fire at the same clock tick with zero offset.
  TRIGGERS: "add a cursor to this product animation", "animate the cursor moving to the button", "add realistic mouse movement", "the cursor needs to click the row", "make it look like a real user interacting with the UI". Runs in parallel with product-animation, sharing the same master timeline.
  SUB-SKILL: figma-to-animation-product-animations routes here for its cursor stage. Usable standalone when you need to add a realistic cursor to any product HTML animation.
  NOT FOR: animating UI elements themselves → use product-animation/. Planning what the cursor should do → use product-animation-planning/. QA-ing the final timing → use product-animation-qa/. A CSS :hover cursor (no GSAP needed) → just CSS.
---

# Cursor Animation

Animates a realistic mouse cursor across a product UI. Not a robotic linear slide —
natural easing between positions, human-like paths, and a visible click press. Runs in
tight coordination with `product-animation`: both write tweens to the **same shared GSAP
master timeline** at the same labels, so cursor arrival and UI state changes fire at the
same clock tick with zero offset by construction.

## When This Skill Activates

- "Add a cursor to this product animation"
- "Animate the mouse moving to and clicking the button"
- "Add realistic mouse movement to the prototype"
- "The cursor needs to hover, then click, row 3"

Keywords: `cursor`, `mouse movement`, `click effect`, `realistic cursor`, `cursor animation`,
`product prototype`, `shared master`, `cursor sync`, `pointer`.

## What This Skill Does

Extracts real element coordinates at the declared viewport, plans natural movement paths with
`power2.inOut` easing (never linear over distance), places cursor tweens on the shared `master`
at the plan's labels, and implements a click press effect (brief scale-down) on the click label.
Never flips the cursor asset. Uses one continuous `#cursor` DOM node — never recreates it per event.

## Entry Point

Load **PROMPT.md** for the full run procedure: standalone setup (including a default cursor SVG),
the 8-step animation process (coordinates → natural paths → labels → click effect → chirality →
one-node rule → idle), the shared-clock contract, and handoff. GSAP primitives in `../gsap/`;
shared clock in `../references/timeline-clock.md`.

---
name: product-animation
description: |
  WHAT: Apply GSAP motion to QA-approved product HTML/CSS — hover states, click responses, expand/collapse, pop-in/out — following the timeline plan exactly. Every tween lives on one shared master GSAP timeline at a label from the plan, so the cursor and UI stay frame-accurately synchronized with zero offset.
  TRIGGERS: "animate this product UI", "add the interaction states to the HTML", "implement the timeline plan", "make the hover/click/expand happen", "apply the animation spec to the markup". Runs after product-design-qa passes and in coordination with cursor-animation.
  SUB-SKILL: figma-to-animation-product-animations routes here for its animation stage. Usable standalone when you need to apply a timeline plan to existing product HTML/CSS.
  NOT FOR: building the static HTML/CSS first → use product-design-recreation/. Planning what should animate → use product-animation-planning/. Animating a cursor → use cursor-animation/. QA-ing the result → use product-animation-qa/. Marketing looping banners → use motion/ + figma-to-animation/.
---

# Product Animation

Brings static, QA-approved product HTML/CSS to life. Every animation event traces back to a
specific row in the timeline document — nothing invented on the fly. Runs in tight coordination
with `cursor-animation`: both add their tweens to **one shared GSAP master timeline** at the
same labels, so cursor movement and UI reactions are frame-accurately synchronized by
construction.

## When This Skill Activates

- "Add the interaction states to this product HTML"
- "Implement the animation timeline on this markup"
- "Make the hover/click/expand work per the plan"
- "Animate this product prototype"

Keywords: `product animation`, `interaction states`, `hover`, `click`, `expand`, `GSAP master`,
`shared timeline`, `animate`, `tweens at labels`, `implement timeline`.

## What This Skill Does

Loads the timeline plan and adds each event as a GSAP tween on a shared `master` timeline
at the event's label. Routes to `../motion/` for motion patterns (pop-in, entrance, stagger)
and `../gsap/` for library primitives. Respects easing intent, dependency order, and product
timing norms. Never uses `setTimeout`, a second timeline, or `animation-delay` — those create
a second clock that drifts from the cursor.

## Entry Point

Load **PROMPT.md** for the full run procedure: standalone setup, the 6-step animation process,
the one-shared-clock rule, routing decisions to `../motion/` and `../gsap/`, and handoff.
The shared clock contract is in `../references/timeline-clock.md`.

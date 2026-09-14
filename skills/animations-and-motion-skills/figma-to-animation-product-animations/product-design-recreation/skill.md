---
name: product-design-recreation
description: |
  WHAT: Recreate a product UI design as pixel-accurate HTML/CSS from Figma — the "make it look exactly right, no animation yet" stage. Every interactive element gets a stable data-anim-id hook for downstream animation targeting; output includes a manifest of those hooks.
  TRIGGERS: "recreate this Figma design as HTML/CSS", "build a pixel-perfect prototype of this product UI", "turn this Figma frame into static markup", "I need accurate HTML/CSS before we animate it", shares a figma.com link and wants accurate product HTML/CSS only (no motion yet).
  SUB-SKILL: figma-to-animation-product-animations routes here for its recreation stage. Usable standalone when you need pixel-accurate product HTML/CSS from Figma without the full pipeline.
  NOT FOR: adding animation or motion → use product-animation/. QA-ing the output → use product-design-qa/. Planning what to animate → use product-animation-planning/. Marketing/banner animations (not product UI) → use figma-to-animation/ + frame-building/. Full product animation pipeline → use figma-to-animation-product-animations/.
---

# Product Design Recreation

The "make it look exactly right before it moves" stage for product UIs. Pixel-accurate HTML/CSS
from a Figma design, with every interactive element tagged with a stable `data-anim-id` hook so
downstream animation and cursor skills can target them precisely without coordinate drift.

## When This Skill Activates

- "Recreate this Figma product screen as HTML/CSS"
- "Build a pixel-perfect static prototype of this UI"
- "I need accurate markup before we start animating"
- "Turn this Figma frame into HTML — exact colors, spacing, fonts"

Keywords: `recreate`, `pixel-perfect`, `static markup`, `product UI`, `HTML/CSS from Figma`,
`data-anim-id`, `design recreation`, `prototype`, `figma product`.

## What This Skill Does

Turns a Figma product design into accurate static HTML/CSS that exactly matches the design
system (colors, spacing, typography, stroke widths). Every element flagged as interactive gets
a `data-anim-id` attribute so the Animation and Cursor skills can target it. Outputs a manifest
of those hooks alongside the markup. Does **not** add animation — that is `product-animation`.

## Entry Point

Load **PROMPT.md** for the full step-by-step workflow: standalone setup, token extraction,
layout mapping, data-anim-id hooks, self-check checklist, and output format. The
`../references/rubric.md` is the QA gate the output goes through next.

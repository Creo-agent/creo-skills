---
name: animation-scaffold
description: >-
  Scaffold a fresh HTML/CSS/JS animation project from scratch — the export-ready starting point for a social/marketing/kiosk motion piece. Go-to skill at the very START of a new animation, whenever the user says "start a new animation", "set up the HTML/CSS/JS from scratch", "blank canvas / stage to animate on", "a new 1080 square (or portrait/landscape) animation", "let's do another project like this one", or has nothing yet and wants the boilerplate to build on. Produces a single self-contained index.html with a fixed pixel-exact stage (e.g. 1080×1080), a JS viewport-fit scaler that never changes the true render size, GSAP loaded, a fonts+images load-gate before measuring, and an empty build() hook. Then hands off to the placement/animation/render skills. Do NOT use when a stage already exists (skip straight to precise-figma-composition / loop-animator), for grabbing an animation off a website (extract-animation-from-web), or for React/Remotion-first work (export-as-gif scaffolds that).
---

# Animation Scaffold (fixed stage + scaler + GSAP)

The reliable starting point for an export-bound web animation: a **fixed, pixel-exact
stage** (so the render is deterministic at any screen size) plus everything the follow-on
skills expect — GSAP, a fonts+images load-gate, and a `build()` hook. Get this right once
and every later skill slots in cleanly.

## When This Skill Activates

- "Start a new animation from scratch — a 1080 square"
- "Set up the HTML/CSS/JS so I have a stage to animate on"
- "Let's do another project like the CRM one"
- "Give me the blank canvas / boilerplate for a portrait story animation"

Keywords: `new animation`, `from scratch`, `scaffold`, `boilerplate`, `blank stage`,
`1080 square`, `portrait`, `landscape`, `starting point`.

## What This Skill Does

1. Asks for (or infers) the canvas — square 1080², portrait 1080×1920, landscape, custom —
   and sets `STAGE_W`/`STAGE_H` up front.
2. Emits one self-contained `index.html`: a fixed pixel-exact `.stage`, a JS scaler that
   only *visually* fits it to the viewport (never changing the true render size), GSAP from
   CDN, a fonts+images load-gate, and an empty `build()` hook.
3. Explains converting `getBoundingClientRect` back to stage-local coords (undo the scaler).
4. Verifies over a local HTTP server (`file://` is blocked in preview) by seeking the timeline.
5. Hands off: `precise-figma-composition` (place) → `loop-animator` (animate) →
   `marquee-carousel` / `gsap-ui-entrance` → `export-as-gif` → `resize-animation`.

## Entry Point

Load **PROMPT.md** for the canvas decision, the full `index.html` scaffold, the fixed-stage
rationale, the serve-and-verify recipe, and the hand-off build order.

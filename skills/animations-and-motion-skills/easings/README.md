# easings

All 30 easing functions from [easings.net](https://easings.net) — the complete reference for
choosing and implementing the right motion curve in any animation context (GSAP, CSS, Remotion,
or plain JS).

## Key files

`SKILL.md` (router + decision tree + use-case table) · `PROMPT.md` (full reference: direction rules,
pick-by-use-case table, CSS cheat-sheet, GSAP shorthands) · `references/functions.md` (every JS
function body + CSS cubic-bezier value, organized by family)

## What's covered

- All 30 easings: Sine · Quad · Cubic · Quart · Quint · Expo · Circ · Back · Elastic · Bounce — each
  in easeIn / easeOut / easeInOut variants, plus linear.
- CSS `cubic-bezier()` values for the 24 easings that have one; "no CSS equivalent" noted for the 6
  that don't (Elastic and Bounce families).
- GSAP string shorthands (`"power2.out"`, `"back.inOut"`, etc.).
- A pick-by-use-case table: plain-language intent → recommended easing → one-line reason.
- Direction rule of thumb (easeOut for entrances, easeIn for exits, easeInOut for state changes).
- Intensity guide (Sine → Quad → Cubic → Quart → Quint → Expo; Back/Elastic/Bounce as special cases).

## Provenance

Source: [github.com/ai/easings.net](https://github.com/ai/easings.net) — JS functions and
cubic-bezier values extracted directly from `src/easings/easingsFunctions.ts` and `src/easings.yml`.
Not vendored as a snapshot; the math is stable and unlikely to change upstream.

---

**Owner:** Elior Siegelwachs · **Last updated by:** Elior Siegelwachs · **Last updated:** 2026-07-15

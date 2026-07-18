---
name: gsap
description: |
  WHAT: GSAP animation library API reference and motion guide. Covers tween methods (gsap.to/from/fromTo/set), vars, transform aliases + autoAlpha, easing, stagger, timelines (position parameter, labels, nesting, playback), matchMedia, and performance (transforms, will-change, quickTo). Vendored reference skill — knowledge, not a workflow.
  TRIGGERS: writing or debugging GSAP code; looking up tween/timeline API; picking an ease or stagger config; using the position parameter; wiring responsive/reduced-motion with gsap.matchMedia(); optimizing motion performance.
  NOT FOR: loop patterns / entrance / marquee / word-ticker → use motion/ (which calls this API). Building a Figma layout → use frame-building/. Exporting to GIF/MP4 → use export-as-gif/. Full pipeline → use figma-to-animation/. Remotion render rules → use remotion-best-practices/.
---

# GSAP

Reference for the GSAP animation library — the tween/timeline API surface, easing, transforms,
and performance guidance. This is a knowledge skill, not a workflow: consult it while writing
GSAP code.

## When This Skill Activates

- Writing a `gsap.to` / `from` / `fromTo` / `timeline` and needing the exact vars or syntax.
- Choosing an ease, a stagger config, or the timeline position parameter (`"<"`, `"+=0.5"`, labels).
- Optimizing motion (transforms vs layout props, `will-change`, `quickTo`).
- Wiring responsive / reduced-motion behavior with `gsap.matchMedia()`.

Keywords: `gsap`, `tween`, `timeline`, `ease`, `stagger`, `autoAlpha`, `transformOrigin`,
`quickTo`, `matchMedia`, `position parameter`.

## What This Skill Covers

- Core tween methods and common vars (duration, ease, stagger, repeat/yoyo, overwrite).
- Transform aliases + `autoAlpha`, function-based values, relative values, `clearProps`.
- Timelines: creation, position parameter, labels, nesting, playback control.
- Performance: compositor-friendly properties, `will-change`, `quickTo`, stagger over many tweens.

## Entry Point

Load **PROMPT.md** for the full API reference. On demand, read `references/effects.md` for
drop-in effects (typewriter, audio visualizer) and `scripts/extract-audio-data.py` for the
audio-data helper.

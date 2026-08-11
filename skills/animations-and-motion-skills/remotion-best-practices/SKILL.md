---
name: remotion-best-practices
description: |
  WHAT: Remotion best-practices and domain knowledge — video creation in React. A rules-index skill: detailed guidance lives in rules/*.md. Vendored reference skill — knowledge, not a workflow.
  TRIGGERS: writing, structuring, or debugging any Remotion code; questions about useCurrentFrame, Composition, Sequence, interpolate, spring, captions, voiceover, assets, fonts, gifs, transparent video, Tailwind, charts, 3D, Lottie, maps, audio visualization, trimming, Zod parameters, or text animations.
  NOT FOR: rendering/exporting an animation to GIF/MP4 → use export-as-gif/. GSAP animation code → use gsap/. Full pipeline → use figma-to-animation/.
---

# Remotion Best Practices

Domain-specific knowledge for Remotion (video creation in React). This is a router into a
`rules/` library — load the specific rule file relevant to the task rather than reading all of it.

## When This Skill Activates

- Any time you are writing, structuring, or debugging Remotion code and want the domain-specific way.
- Task-specific triggers: captions/subtitles, FFmpeg trimming/silence, audio visualization,
  sound effects, springs/timing, sequencing, transitions, fonts, charts, 3D, maps, voiceover.

Keywords: `remotion`, `useCurrentFrame`, `Composition`, `Sequence`, `interpolate`, `spring`,
`captions`, `voiceover`, `@remotion/*`.

## What This Skill Covers

- Fundamentals: animations, timing/interpolation/springs, sequencing, transitions.
- Compositions & metadata, parameters (Zod), assets, fonts, Tailwind.
- Media: images, videos, audio, gifs, transparent videos, trimming, decode/duration helpers.
- Rich content: captions/subtitles, audio visualization, sound effects, charts, 3D, Lottie, maps,
  text animations, voiceover.

## Entry Point

Load **PROMPT.md** for how to use the rules and the full index, then open the matching
`rules/*.md` file(s). Shared component examples live in `rules/assets/`.

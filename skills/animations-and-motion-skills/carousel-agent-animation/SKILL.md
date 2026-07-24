---
name: carousel-agent-animation
description: |
  WHAT: Generate a self-contained HTML/CSS/vanilla-JS animation featuring AI agent character cards, sourced from a Figma file. Two styles: (1) Carousel — 5-card overlapping fan loop, center card elevated with shadow and bold label, pure scale/position transitions, no opacity changes, no entrance flash; (2) Floating agents — fixed 1280×734 scene scaled to viewport, agent cards spring in after a typewriter prompt, float gently, then exit and loop.
  TRIGGERS: "create an agent card animation", "carousel animation from Figma", "floating agent cards animation", "make an animation with agent cards", "agent carousel", "generate a card carousel", "carousel-agent-animation", "card fan loop", "animate my agent cards".
  NOT FOR: general Figma-to-animation pipelines → use figma-to-animation/. Static frame building without motion → use frame-building/. GSAP motion on an existing frame → use motion/. Exporting to MP4/GIF → use export-as-gif/.
---

# Carousel Agent Animation

Generates two styles of agent-card animation entirely from a Figma source — no manual pixel work.

**Style A · Carousel** — An infinite fan loop of 5 portrait cards. Cards overlap in a stacked layout;
the center card is largest (scale 1.0) with a drop shadow and bold label; flanking cards scale down
(0.9, 0.826). Transitions are pure `transform` — no opacity changes. The loop is seamless: the
off-screen card teleports invisibly using a double-`requestAnimationFrame` + `no-transition` pattern.

**Style B · Floating agents** — A fixed 1280×734 scene that scales via JS to fill any viewport.
After a typewriter prompt animates in the chat bar, three agent cards spring in with a
`cubic-bezier(0.34, 1.56, 0.64, 1)` bounce, float on independent keyframe cycles, then exit and
loop. Background: a photo subject on a warm `#ecdfce` field.

## Entry point
Load `PROMPT.md` for the full run procedure — inputs to collect, Figma extraction, design value
derivation, complete CSS/JS templates for both styles, verification steps, and troubleshooting.

---
name: ds-section-animations
description: |
  WHAT: Add animation and interactivity to Clay Design System (Clay DS) section stories using native browser APIs — CSS + vanilla JS only (the DS does not use Framer Motion or GSAP). Niche skill for DS stories specifically.
  TRIGGERS: user shares a Relume or Framer Motion reference and says "add this animation to [section]"; asks for mouse-move parallax, scroll-driven parallax, a continuous marquee loop, or "make the media/images move" on a Clay DS section story.
  COVERS: reading Framer Motion reference code to pick the native equivalent; CSS --mx/--my mouse parallax; section-anchored JS scroll listeners (why NOT animation-timeline: scroll()); seamless CSS marquee loops; prefers-reduced-motion handling.
  NOT FOR: GSAP timelines or standalone looping banners → use motion/. Full Figma layout → use frame-building/. Full pipeline → use figma-to-animation/. Not part of the figma-to-animation GSAP pipeline — but shares its animation-knowledge and setup references.
---

# DS Section Animations

Add interactivity and motion to Clay DS section stories. The DS does **not** use Framer
Motion — all animations use native browser APIs (CSS + vanilla JS), living in the story file
so the section component stays stateless and animation-agnostic.

## When This Skill Activates

- "Add this Relume animation to the HeaderSection"
- "Give the hero a mouse-move parallax on the background images"
- "Make this scroll-driven parallax work like the Framer reference"
- "Make the media columns loop / auto-scroll forever"

Keywords: `Clay DS`, `section story`, `Relume`, `Framer Motion`, `parallax`, `mouse-move`,
`scroll-driven`, `scrollYProgress`, `marquee`, `auto-scroll`, `--mx/--my`, `prefers-reduced-motion`.

## What This Skill Does

- Reads the Framer Motion reference (`useScroll`/`useTransform`, `useMotionValue`/`useSpring`,
  `whileInView`, marquee classes) and maps each to its native Clay DS equivalent.
- Builds **mouse-move parallax** with CSS custom props `--mx/--my` (zero React re-renders).
- Builds **scroll-driven parallax** with a JS scroll listener whose progress is
  **section-anchored** (`-rect.top / rect.height`) — reproducing the reference `useTransform`
  ranges exactly, writing transforms directly (no rAF), and avoiding `animation-timeline: scroll()`.
- Builds **seamless CSS marquee loops** (`translateY(0 → -50%)`, `margin-bottom` not `gap`).
- Handles `prefers-reduced-motion` per technique and gives preview-verification recipes.

## Entry Point

Load **PROMPT.md** for the reference-code mapping table, the three motion patterns with full
code, the critical pitfalls (rAF, range mapping, spacer decorators), the finishing checklist,
and the in-codebase reference implementations.

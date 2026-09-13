---
name: resize-animation
description: |
  WHAT: Adapt an existing animation to a different canvas size or aspect ratio — and/or swap its images — to produce format variants (square, portrait, landscape, banner, story) without rebuilding the motion. Asks for target size(s)/aspect ratio first, then reflows element positions and re-verifies motion.
  TRIGGERS: "resize / reframe / reflow an animation", "make a portrait / square / vertical / 1080x1920 / 9:16 version", "adapt it for Instagram / story / reel / ad", "generate size variants", "swap the images in this animated layout".
  SUB-SKILL: figma-to-animation orchestrator routes here to reflow to new sizes. Usable standalone whenever the deliverable is the same animation at a new size.
  NOT FOR: resizing a static image/photo. Transcoding a video's resolution. Responsive website CSS. Building an animation from scratch → use figma-to-animation/. Capturing off a live site → use extract-animation-from-web/. Exporting to GIF/MP4 → use export-as-gif/.
---

# Resize Animation

Take an animation that already works at one size and re-target it to other dimensions or
new assets, producing clean variants (ad/social formats) fast. Move the composition — don't
rebuild the motion; the animation logic carries over untouched.

## When This Skill Activates

- "Make a portrait 1080×1920 version of this animation for stories"
- "Reframe this square animation to landscape 1920×1080"
- "I need Instagram story, feed, and reel versions of this loop"
- "Swap the images in this animated layout and adjust for the new sizes"

Keywords: `resize`, `reframe`, `reflow`, `portrait`, `square`, `vertical`, `9:16`,
`1080x1920`, `story`, `reel`, `ad size`, `variants`, `swap images`.

## What This Skill Does

1. **Asks for the target size(s)/aspect ratio first** — a portrait reflow and a landscape
   reflow move elements in opposite ways, so this must be pinned down before placing anything.
2. Reflows element positions for the new frame (from a Figma source, or proportionally then
   hand-adjusted), keeping margins/gaps legible and overlaps intentional.
3. Keeps the motion resize-proof (dynamic, hero-relative targets).
4. Optionally swaps assets; re-verifies each variant.

## Entry Point

Load **PROMPT.md** for the target-size questions, the reflow strategy, keeping motion
resize-proof, image swapping, batch variants, and per-variant verification.

---
name: resize-animation
description: >-
  Adapt an existing animation to a different canvas size or aspect ratio — and/or swap its images — to produce format variants (square, portrait, landscape, banner, story) without rebuilding the motion. Go-to skill whenever the user wants to resize / reframe / reflow an animation they already have, make a portrait/square/vertical/1080x1920/9:16 version, adapt it for Instagram/story/reel/ad, fit a different size, generate variants, or swap the images in an animated layout. It asks for the target size(s)/aspect ratio first, then reflows element positions and re-verifies the motion. Prefer this over the extract, loop, gif-export, and figma skills whenever the deliverable is the same animation at a new size. Do NOT use for: resizing a static image/photo, transcoding a video's resolution, responsive website CSS, or building an animation from scratch.
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

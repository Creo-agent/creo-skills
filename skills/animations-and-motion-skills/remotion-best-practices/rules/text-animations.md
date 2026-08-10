---
name: text-animations
description: Typography and text animation patterns for Remotion.
metadata:
  tags: typography, text, typewriter, highlighter ken
---

## Text animations

Based on `useCurrentFrame()`, reduce the string character by character to create a typewriter effect.

## Typewriter Effect

See [Typewriter](assets/text-animations-typewriter.tsx) for an advanced example with a blinking cursor and a pause after the first sentence.

Always use string slicing for typewriter effects. Never use per-character opacity.

## Slot-machine / word ticker

Cycle words (e.g. leads → deals → accounts) in a vertical ticker: an `overflow:hidden`, `inline-block` clip of height `1.3em` holding two absolutely-positioned (`left:0`) word spans that slide vertically over the wipe — outgoing span `translateY 0 → -LINE_H`, incoming `translateY +LINE_H → 0` — while the clip's `width` morphs `curW → nextW`. Derive `LINE_H` from font metrics (`fontSize × lineHeight`), never from `getBoundingClientRect` — a measured height pulls in transform/coordinate-space bugs.

**Size the clip by measuring, not hardcoding.** Get each word's width from `measureText` (see `measuring-text`) or size the clip to content; hardcoded px are brittle to font/scale mismatch. If you measure widths from a live CSS-scaled page, divide a `getBoundingClientRect()` by the scale factor *only* for elements inside the scaled subtree (a probe on `document.body` already reports true px; dividing inflates it ~1.875× — see `animation-scaffold`). Because the slot spans hug `left:0`, an over-wide clip adds empty space to the word's right and shifts the centered line off-center — so wrong widths decenter the headline even with perfect centering CSS.

## Word Highlighting

See [Word Highlight](assets/text-animations-word-highlight.tsx) for an example for how a word highlight is animated, like with a highlighter pen.

## Centering a headline with a variable-width word

Center each line with a fixed full-width block — `left:0; width:STAGE_W; text-align:center` — so it sits on the stage midline regardless of content width. Avoid `left:50%` + `translateX(-50%)` shrink-to-fit around a fixed-width inner clip: a mis-sized clip then overflows and decenters the line. Note that a centering change can *mask* a width/data error without fixing it — if the symptom persists after a plausible layout fix, isolate the root cause (are the widths right?) before declaring victory; the robustness improvement and the real data fix are independent.

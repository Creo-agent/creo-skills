---
name: marquee-carousel
description: >-
  Build an endless, auto-scrolling horizontal marquee / carousel in HTML/CSS/JS with GSAP — one or more rows of items (message pills, chips, logos, cards, tickers) that slide sideways forever with no seam. Go-to skill whenever the user wants content to "scroll continuously", "loop sideways like a ticker/marquee", "a row of cards moving right while another moves left", "a logo strip", "a news ticker", or a multi-row carousel with a parallax feel. Covers seamless wrapping (duplicated content), per-row speed/direction, measuring after fonts/images load, a moving gradient-stroke "reflection" highlight, and porting the scroll to Remotion frame-math for GIF/MP4. Pairs with loop-animator (as the scrolling layer inside a bigger reveal loop), precise-figma-composition (build the pill from Figma), and export-as-gif (render it). Do NOT use for: a reveal-then-reset loop (loop-animator), vertical scrolling / scroll-triggered effects, or a single static row.
---

# Marquee Carousel (endless horizontal scroll)

A row that scrolls forever without a visible jump. The whole trick is **duplicated content +
wrap**: translate the track by exactly one copy-width and modulo-wrap, so a second identical
copy slides into the spot the first just left.

## When This Skill Activates

- "Make this row of pills scroll sideways forever, like a ticker"
- "Top row moves right, middle row left, bottom row right — a parallax carousel"
- "Add a continuously scrolling logo strip / news ticker"
- "The message chips should loop horizontally under the character"

Keywords: `marquee`, `ticker`, `carousel`, `scroll continuously`, `loop sideways`,
`logo strip`, `parallax rows`, `endless scroll`.

## What This Skill Does

1. Structures each row as a track holding ≥2 identical content groups (built once, content
   swapped from an array).
2. Runs an always-on GSAP tween per row that translates by one group-width and modulo-wraps
   with `gsap.utils.wrap` — seamless, with per-row speed/direction for parallax.
3. Measures copy-width only after fonts + images load (widths depend on both).
4. Optionally adds a moving gradient-stroke "reflection" highlight (mask-composite border).
5. Slots into a `loop-animator` loop as the scrolling layer, and ports to Remotion frame-math
   for `export-as-gif` (skip the wrap — invisible at the loop boundary).

## Entry Point

Load **PROMPT.md** for the markup/CSS, the seamless-wrap tween, multi-row parallax, the
reflection shimmer, the Remotion port, and the verification recipe.

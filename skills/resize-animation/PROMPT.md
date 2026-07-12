
# Resize animation

Take an animation that already works at one size and re-target it to other dimensions or
new assets, producing clean variants (ad/social formats) fast. The goal is to move the
composition, not rebuild the motion — the animation logic should carry over untouched.

## Ask for the target size(s) FIRST
Don't guess the format. If the user hasn't already named the target, ask what they want —
the answer determines every position you compute, so it's the first thing to pin down:
- **Which size(s) / aspect ratio(s)?** Offer common presets and let them pick one or several:
  - Square 1080×1080 (feed post)
  - Portrait 1080×1920 (story / reel / TikTok)
  - Landscape 1920×1080 (YouTube / web hero)
  - Wide banner (e.g. 1500×500) or a custom W×H they specify
- **One variant or a batch?** (Generating several formats at once is common for ad/social.)
- **Any element that must stay fully visible / uncropped** at the new ratio (the hero, a logo)?

Only once the target frame(s) are known do you reflow — because a portrait reflow and a
landscape reflow move elements in opposite ways.

## What actually has to change
1. **Stage dimensions** — the canvas width/height (and, for Remotion, `width`/`height` +
   any layout constants that assumed the old size).
2. **Element positions** — the scatter/layout must be re-placed for the new frame's shape.
3. **Optionally the assets** — swapped images (and their card sizes if aspect differs).

What should NOT change: the timeline/loop, easings, stagger, cross-fades. If the motion is
written to compute targets dynamically (see below), it survives a resize for free.

## Reflowing positions for a new aspect ratio
Positions tuned for one shape rarely map by a single scale factor to a different shape
(e.g. wide → square crowds the sides; square → portrait leaves big top/bottom gaps). Re-place:
- **From a design source:** if there's a Figma frame for the target size, use
  `precise-figma-composition` to get exact coordinates. Best fidelity.
- **Proportionally, then adjust:** convert each element's position to a fraction of the old
  frame, apply to the new frame, then hand-adjust for the new shape — keep even margins,
  avoid crowding the hero, and preserve intentional overlaps. State any element you had to
  move materially so the user can veto.
- **Keep spacing legible:** consistent edge margins and gaps read as intentional; uneven
  ones read as broken. If the hero dominates more/less at the new size, resize it too.

## Keep the motion resize-proof
If the animation targets are computed at runtime (e.g. collapse-to-center via
`getBoundingClientRect`, or a `CONVERGE` point defined relative to the hero), a resize just
works — elements still fly to the right place. If any target was hardcoded to the old
canvas, re-derive it from the new hero center. Prefer refactoring hardcoded targets to
dynamic ones while you're here.

## Swapping images
- Replace assets in place; if a new image's aspect differs, set the card width and let
  height follow (don't distort). Re-check it doesn't now overlap a neighbor or the hero.
- Keep filenames/paths consistent so both an HTML version and a Remotion `public/` version
  stay in sync.

## Batch variants
For multiple formats, parameterize the stage size + position set and generate each
(square 1080², portrait 1080×1920, landscape 1920×1080, etc.). In Remotion, this is one
component with per-format layout constants or multiple `<Composition>`s; in HTML, one file
per format (or a size-driven layout).

## Verify each variant
Re-run the deterministic checks from `loop-animator`: rest frame, mid-motion, revealed
frame, and (for loops) that it still loops without a cut. Confirm nothing clips off-canvas
or collides at the new size. Then, if a video is wanted, hand each variant to `export-as-gif`.

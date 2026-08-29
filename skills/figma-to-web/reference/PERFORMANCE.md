# Performance & Efficiency — How to Write the HTML/CSS/JS

## Contents
- Why this file exists
- Core Web Vitals targets (what "fast" means here)
- Images — the highest-leverage category
- Fonts — this project's standing convention
- CSS delivery
- JavaScript
- Document-level basics
- Checklist to run before delivery

## Why this file exists

Confirmed real gap: an early section build (a hero image) shipped as an unoptimized 246KB PNG
with no `fetchpriority`, and logos as inline pixel-height guesses — visually fine, but neither
was ever evaluated against actual performance practice. Fidelity to Figma and performance are
not in tension; a pixel-accurate section built with a bloated image and no priority hints is
still an incomplete deliverable. This file is the concrete "how," researched against current
(2026) guidance from web.dev and Core Web Vitals reporting — sources linked inline — not
general impressions. Apply it to every section, the same way `ACCURACY-GATE.md` applies to
every section.

## Core Web Vitals targets (what "fast" means here)

Three metrics, all vision-QA-adjacent (you can eyeball two of them without tooling):

| Metric | Target | What breaks it | How to catch it here |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | < 2.5s | The largest above-the-fold element (almost always a hero image or heading) fetched late or without priority | Identify the LCP candidate per section (usually the hero media) and give it `fetchpriority="high"`, never `loading="lazy"` |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Images/fonts loading without reserved space, content jumping after load | Already covered by H10–H12, H16: explicit `width`/`height` on every `<img>`, `font-display: swap`, capped text-box widths |
| **INP** (Interaction to Next Paint) | < 200ms | Heavy JS blocking the main thread on interaction | Mostly N/A for static sections with no JS; becomes relevant once carousels/accordions/tabs are built — keep interaction handlers small and avoid layout thrashing (`GOTCHAS.md`'s synchronous-DOM-read note) |

Sources: [Core Web Vitals 2026 guide](https://www.digitalapplied.com/blog/core-web-vitals-2026-inp-lcp-cls-optimization-guide), [web.dev responsive images](https://web.dev/learn/design/responsive-images), [web.dev font best practices](https://web.dev/articles/font-best-practices).

## Images — the highest-leverage category

**1. Identify the LCP candidate per section and prioritize it.** The largest above-the-fold
image (almost always a hero) gets `fetchpriority="high"` on the `<img>` and no `loading`
attribute (eager is the default — never `lazy` on it). Confirmed impact in Google's own testing:
~2.6s → ~1.9s LCP from this one attribute. Every other image gets `loading="lazy"` unless it's
also clearly above the fold.

**2. Convert raster images to WebP, keep the original as a real-file fallback.** A confirmed
real case: a 246KB PNG hero image converted to WebP (quality 90) came out at 32KB — an 87%
reduction with no visible quality loss at delivery size. Use `<picture>` so the real PNG (or JPG)
stays as a genuine fallback file, per H4's "real files, never fabricated":
```html
<picture>
  <source srcset="images/hero/hero-visual.webp" type="image/webp">
  <img src="images/hero/hero-visual.png" alt="…" width="817" height="510" fetchpriority="high">
</picture>
```
Conversion (Python/Pillow, already available in this environment):
```python
from PIL import Image
Image.open("original.png").save("original.webp", "WEBP", quality=90, method=6)
```
AVIF is smaller still (~50% smaller than JPEG vs. WebP's ~25–35%) but Pillow support is less
uniform — WebP is the pragmatic default here; reach for AVIF only if the specific build already
has a working AVIF encode path.

**3. Explicit `width`/`height` on every `<img>`, matching intrinsic pixel dimensions** — already
H12 (and H16's item 2 for per-instance geometry). This is also a CLS requirement, not just a
fidelity one.

**4. SVG logos/icons need no format work** — already optimal. Don't rasterize them.

**5. Responsive `srcset` for large, full-bleed images** (not needed for a modest ~600–800px
hero, but required once an image spans near-viewport widths, e.g. a `split-full-image` or
`centered-strips` layout): provide at minimum 400w/800w/1200w variants, plus 1600–2000w for a
genuinely full-bleed hero, with a `sizes` attribute matching the layout's actual rendered width
at each breakpoint.

**6. Resize target = the image's actual rendered display width × 2 (retina), not a flat ceiling
applied to every asset regardless of size.** Confirmed real case: a row of carousel cards
displayed at ~300px CSS width shipped with Figma's raw uploaded source resolution (2304×4096–
3277×4096px) — several files at 1.5–2.9MB each for a slot that only ever needs ~600px of real
pixel width. A single flat cap (e.g. 1440px) is a reasonable *ceiling* for a full-bleed hero, but
applying it as the *default* for every image regardless of its own container size still leaves
small on-screen elements 5–10x oversized. Look up the image's real rendered CSS width for the
section being built (`get_design_context`'s layout data, or the slot/container it fills) and
resize to `min(display_width_px * 2, ceiling)` — see `SECTION-WORKFLOW.md` Step 8's
`resize_target_width()` for the exact pattern. Only fall back to the flat ceiling when no display
width is knowable (e.g. one background image reused at several different sizes).

## Fonts — this project's standing convention

**Current general best practice (2026) is to self-host fonts, not load them from the Google
Fonts CDN** — cross-origin cache partitioning (shipped across Chrome/Firefox/Safari since
~2020–2023) means there's no cross-site cache-sharing benefit to a shared CDN anymore, so
self-hosting a subsetted woff2 removes a DNS/connection hop for no downside. **This project has
an explicit standing exception: always use the standard Google Fonts embed for Poppins, never
self-hosted files** — confirmed by direct user instruction after a self-hosting attempt was
tried and reverted. Keep the standard embed:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
```
`&display=swap` in the URL is the one non-negotiable part regardless of hosting choice — it's
what keeps text visible (fallback font) instead of invisible while Poppins loads, and is already
present in this snippet. Don't add more weights than the page actually uses — the `wght@` list
should match what's really set in the CSS, not a default-everything set.

## CSS delivery

`images/_shared/clay-tokens.css` is loaded as an external, render-blocking stylesheet rather
than inlined. This is a deliberate tradeoff, not an oversight: this is a multi-page site (IT
persona page, HR persona page, more to come) that all share this one token file — loading it
externally lets the browser cache it once and reuse it across every page on a repeat visit,
which inlining would forfeit. On a first visit this costs one render-blocking round trip; that's
accepted in exchange for the cross-page cache win. If this project ever becomes single-page-only,
revisit this tradeoff (inlining would then be strictly better).

Section-specific CSS stays inlined in `<style>` blocks in `<head>`, as it already is — for a
handful of sections this avoids extra requests entirely, and per-section CSS isn't reused across
pages the way tokens are.

## JavaScript

- Any injected `<script src="...">` (GSAP, ScrollTrigger, etc.) needs `defer` — a bare
  `<script src>` in `<head>` blocks HTML parsing until it downloads and executes.
- **Don't include a library before a section that actually needs it exists.** Confirmed pattern
  worth avoiding: GSAP/ScrollTrigger were part of the IT page's `<head>` from early on, used by
  later animated sections — fine once those sections exist, but don't carry the pattern into a
  new page's skeleton speculatively. Add the dependency when the section that needs it is built,
  not before.
- Prefer vanilla JS for simple interactions (toggle a class, `aria-expanded`) over pulling in a
  library at all.

## Document-level basics

- `<meta name="description">` — every page needs one; write it from the actual hero copy, not a
  generic placeholder.
- `<html lang="...">` — already standard practice here, keep it.
- `<meta name="viewport" content="width=device-width, initial-scale=1.0">` — already standard.

## Checklist to run before delivery

For every section with a real image:
- [ ] Is this section's largest image the page's LCP candidate? If yes: `fetchpriority="high"`, no `lazy`.
- [ ] Is the raster image WebP (with the original format kept as a real fallback file)?
- [ ] Does the `<img>` have explicit `width`/`height` matching its real intrinsic pixels?
- [ ] Is every non-LCP image `loading="lazy"` if genuinely below the fold?
- [ ] Was each raster image resized to its own real display width × 2, not left at Figma's raw
      source resolution or a flat ceiling regardless of how small it renders?

Once per page:
- [ ] Google Fonts embed includes `&display=swap` and only the weights actually used.
- [ ] Any injected `<script src>` has `defer`.
- [ ] `<meta name="description">` is present and specific to this page's real content.

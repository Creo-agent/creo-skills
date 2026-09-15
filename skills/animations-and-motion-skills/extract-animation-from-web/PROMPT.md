
# Extract animation from web

Goal: turn one section of a live site into a **standalone HTML file** that renders
and animates identically on its own, with assets available locally. This is the
first stage of the animation pipeline — pairs with `motion` (make it loop),
`export-as-gif` (render to video/GIF), and `resize-animation` (reframe it).

## Why this is tricky

Modern sites (Webflow, Framer, Next.js) don't serve the finished HTML to a naive
request, lazy-load assets, and bury animation logic in bundles. The steps below are
ordered to defeat exactly those problems. Read `references/gotchas.md` when something
renders blank or unstyled.

## Workflow

### 1. Get the REAL rendered HTML (not a stub)
A plain `curl` often returns a tiny shell (a few KB) — the real markup arrives via
JS or only with browser-like headers. Always check the byte size; if it's suspiciously
small, add full browser headers:

```bash
curl -sL "<url>" \
  -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "Accept-Encoding: gzip, deflate, br" \
  --compressed -o /tmp/page.html
wc -c /tmp/page.html   # sanity-check it's the full page (100KB+), not a 4KB stub
```

If it's still a stub or the section is client-rendered, read the **live DOM** with the
browser tools instead (navigate, then `read_page`/`javascript_tool` to dump the
section's `outerHTML` and the resolved image `src`s).

### 2. Find the linked CSS and JS bundles
```bash
grep -oE '(href|src)="[^"]*\.(css|js)[^"]*"' /tmp/page.html
```
Download the CSS bundles. Note which script tags load GSAP, ScrollTrigger, Splide,
Lenis, etc., and whether the animation config is inline `<script>` or in a bundle.

### 3. Extract ONLY the section's markup
Find the section by a stable class/attribute (e.g. `class="hp-agents_section"` or a
`data-*` hook). Pull its full subtree with depth-matched closing tags — don't grab the
whole page.

### 4. Extract ONLY the CSS rules that apply
Parse the CSS into rule blocks and keep those whose selectors mention the section's
class prefixes (and their `@media` variants, `:root` variables, and any utility classes
the markup uses). `scripts/extract_css.py` does this — pass the CSS file(s) and a list
of class-name keywords, and it prints the matching rule blocks including media queries.

### 5. Capture the animation JS
Copy the inline animation config verbatim (GSAP timelines, ScrollTrigger setup, Splide
options). Keep the CDN `<script src>` for the library itself (pin the same version the
site uses). You'll usually keep this JS as-is now and rework it later with `motion`.

### 6. Download images (including srcset)
Grab every `src` AND the largest `srcset` candidate for the section's images into a local
`images/` folder with readable names, then rewrite the markup's `src`/`srcset` to the
local paths. Offline-proofs the file. (See `resize-animation`/`export-as-gif` which also
expect local assets.)

### 7. Assemble the standalone file
One HTML file: `<style>` with the extracted CSS, the section markup, CDN `<script>` for
the library, then the inline animation JS. Reference images locally.

### 8. Verify — don't assume
Serve the folder and open it in the browser preview. Check:
- console for errors, and that every image reports `complete && naturalWidth>0`;
- a screenshot of the resting state matches the source;
- if it's scroll/timeline-driven, seek to a few states and screenshot to confirm motion.
Fix and re-check before declaring done.

## Output
A single self-contained `.html` (+ local `images/`) that reproduces the section's look
and motion. Tell the user what external deps remain (e.g. GSAP from CDN) and offer to
vendor them locally if they need full offline use.

# Figma to Section — Single Section Builder Workflow

## Contents
- Input Requirements
- State Detection — Which Turn Am I In?
- Brief-skip inference
- Turn 1 — Scout Phase (Steps 0–3, Step 0 starts the timing log)
- Turn 2 — Build Phase (Steps 4–12)
- Output File Structure
- Known Limitations

Converts a single Figma section node into an HTML/CSS/JS preview and a companion
`images/<section-slug>/` folder, then injects the section into a cumulative page file. Run once
per section; each run grows the same page. The HTML and its `images/` folder travel together
(H4). **Before Step 1**, confirm `python3 tools/setup_dependencies.py --check` exits 0 (run the
full setup script first if the user has never installed dependencies — see `PREREQUISITES.md`).
Then run the agent preflight (Clay path + Figma MCP). **Before writing any HTML/CSS for the
section**, run `CLAY-INTEGRATION.md`'s resolution process. **The page shell and every content
section's wrapper nest come from `PAGE-STRUCTURE.md` (H27)** — do not invent a parallel tree.

**This is a two-turn skill.** Turn 1 scouts the design and asks for a brief. Turn 2 builds,
injects, and delivers.

## Input Requirements

- **Figma URL** (required before Turn 1): must include `?node-id=` pointing to the specific
  section frame. If missing, stop and ask: _"I need a URL that includes a specific node — copy
  the URL while the section frame is selected in Figma."_
- **Designer brief** (required before Turn 2, or explicitly skipped — see inference below):
  purpose, interactivity, copy notes, page slug.

## State Detection — Which Turn Am I In?

- **Turn 1 state:** no prior scout reply in this thread for this section → run Turn 1 (Steps 1–3).
- **Turn 2 state:** the scout message was posted and the designer replied with a brief → run
  Turn 2 (Steps 4–12).
- **Brief-skipped Turn 2 state:** the designer replied but skipped the questions ("just build
  it", "send me the html", "go ahead") → infer defaults, proceed to Turn 2.
- **Error state:** reply is incomplete (no page slug, no interactivity answer) → ask for the
  missing piece; do not proceed to build.
- **Resumed-after-compaction state (checkable trigger, see `HARD-RULES.md` H26):** the thread
  contains a system-generated conversation summary (not the designer's own words) covering any
  part of this build, and Phase 1 Resolve (`CLAY-INTEGRATION.md`) was run at any point before
  that summary → before proceeding to Turn 2 for any remaining section, explicitly re-state that
  section's Phase 1 anchor (type + component name) in this turn's own output. If the anchor
  itself isn't recoverable from the summary — only a claim that resolution "was done" — treat
  Phase 1 as not yet run for that section and re-run it fresh. Never take a summary's own stated
  "next step" as the process to follow instead of this file.

## Brief-skip inference

Use these inference rules — state your assumptions so the designer can correct anything:

| Brief field | Inference rule |
|---|---|
| **Interactivity** | Scan section dimensions: children arranged horizontally, total width > 2× viewport → CSS marquee; cards/tabs with alternating content → tabs; isolated large number elements → counter animation; otherwise → static. **If none of these patterns clearly apply, this is an `ASK-DONT-GUESS.md` trigger, not an inference case — halt and ask rather than picking one.** |
| **Purpose** | Read dominant text content (headlines, CTAs) — infer in 1 sentence |
| **Copy notes** | None — preserve all Figma copy as-is |
| **Page slug** | Derive from section name (slug formula in Step 1). If the section name implies a page, drop the section part |

State inferences before delivering, e.g.: _"No brief received — proceeding with inferred
defaults: CSS marquee (6 horizontal cards), social proof section, copy preserved, page slug
`scroll-page`. Reply if you'd like anything changed."_

## Turn 1 — Scout Phase

### Step 0: Start the timing log

Before any Figma call, run `date "+%Y-%m-%d %H:%M:%S"` and record the result. This is the only
reliable way to know how long a section actually took — a narrative trace log alone can't answer
"how much time did this take," and file-mtime archaeology after the fact only captures brief
asset-download moments, not the full working span (confirmed directly: reconstructing past
section durations this way was unreliable and had to be caveated as approximate). Log it to the
project's trace file as `[TIME] start <section-slug> (<node-id>): <timestamp>` — this is one
entry in the same tag convention as `[CLAY]`/`[BUG]`/`[TOOL]`/`[QA]`/`[ACCEPTED-GAP]`.

### Step 1: URL Parsing and Validation

Extract `fileKey` and `nodeId`:
```
https://www.figma.com/design/<fileKey>/<file-name>?node-id=<int>-<int>
```
`fileKey` = path segment between `/design/` and the next `/`. `nodeId` = the `node-id` value
with `-` replaced by `:` (e.g. `3556-14964` → `3556:14964`).

If no `node-id`, stop: _"I need a URL that includes a specific node — e.g. `?node-id=1234-5678`.
Select the section frame in Figma, then copy the URL."_

**Section slug derivation** (derive now, use throughout): lowercase → replace spaces/underscores/
slashes with hyphens → strip non `a-z0-9-` chars → collapse repeated hyphens → truncate to 48
chars. Example: `"Meet your new teammates"` → `"meet-your-new-teammates"`.

### Step 2: Figma Data Extraction

Run in order:

**2a. `get_metadata(fileKey, nodeId)`** — node name (→ slug), width/height, child count. If it
fails or returns no name, fall back to `section-<nodeId-with-colon-replaced-by-dash>`.

**2b. `get_screenshot(fileKey, nodeId, maxDimension=2048)`** — download immediately:
```bash
curl -sL -o "/tmp/<section-slug>-figma-ref.png" "<screenshot-url>"
```
QA reference only — never page content (H1).

**2c. `get_design_context(fileKey, nodeId, clientFrameworks="html", clientLanguages="html,css")`**
— extract: background color; section padding (T/R/B/L px); layout mode (`HORIZONTAL`→row,
`VERTICAL`→column, `NONE`→likely `position: absolute`); gap; max-width or `FILL`; per-text-node
typography (family, size, weight, color, line-height); border-radius/border/box-shadow; which
children are text/image-fill/vector-icon/nested-frame; gradient fills.

If the response exceeds context limits or returns partial data (see `FIGMA-EXTRACTION.md` for
the full reliability playbook): `get_metadata` to list children, then `get_design_context` per
child, merge results.

**2d. `get_variable_defs(fileKey, nodeId)`** (if variable bindings appear) — extract names +
resolved values.

**2e. `get_libraries(fileKey)`** (once, not per-section) — check for a Clay library subscription
to set `CLAY_DESIGN`.

**2f. Check for an `Assets` frame before decomposing any illustration/mockup panel (H9).** If
the section mixes an illustration with floating fake-UI mockup snippets, run `get_metadata` on
the file looking for `Assets`/`Visual assets`/`Illustrations`. If found, match child frames to
card/section titles, note matched node IDs (exported flat in Step 4c', not read via
`get_design_context`), skip reading their sub-layers. If not found, fall back to H9's naming/
structural heuristics and flag that the designer should consider staging one.

**2g. Emit the measured spec — before any CSS exists.** Everything above is *extraction*: it
gives you what Figma reports. This sub-step is *measurement*: it gives you the handful of numbers
Figma reports badly or not at all, and it must produce written output you build against, not a
mental note. Run all four:

```bash
T=~/.claude/skills/figma-to-web/tools/section_spec.py
python3 $T bg        /tmp/<slug>-figma-ref.png --orig-width <original_width from 2b>
python3 $T textnodes /tmp/<slug>-metadata.json --node-id <nodeId>
python3 $T textsize  /tmp/<slug>-figma-ref.png --box X,Y,W,H --orig-width <original_width>
# after Step 4c' exports the section's assets:
python3 $T assetbg   output/<page>/images/<slug>/*.png --on '<container fill hex>'
```

Two things this exists to force:

- **`--orig-width` is the `original_width` field from 2b's response, not the PNG's width.**
  `get_screenshot` returns a *scaled* PNG plus the design's real dimensions; every pixel you
  measure off that PNG is in PNG px and must be multiplied by `original_width / png_width` to
  become design px. Passing `--orig-width` makes the tool do that for you. Omitting it prints a
  warning and PNG-px numbers, which are wrong by a constant ratio in the same direction for every
  measurement — consistent enough to look like a deliberate scale rather than an error.
- **Measure any font size you did not receive as an explicit number from 2c.** `textsize` finds
  the ink band and divides by the family's cap-height ratio (`--family` selects it). Don't infer a
  size from a design-context snippet's surrounding classes, and don't carry one over from a
  similar-looking earlier section — visual similarity is not a measurement.

Write the results into the section's build notes and the trace (`[PRE-BUILD-CHECK]`, with the
values — see `PRE-BUILD-VERIFICATION.md`'s Logging rule). Then read
`PRE-BUILD-VERIFICATION.md`'s Tier 1 items for what still needs eyes.

### Step 3: Post the Scout Message and STOP

```
Here's what I see in this Figma section:
[Figma reference screenshot]

**<node-name>** — <width>×<height>px, <child-count> direct children
File: <fileKey> / Node: <nodeId>
Clay DS: <detected / not detected>

I have the design context. Before I build, I need a quick brief:

**1. Purpose** — What does this section communicate? What's the key message or call to action?
**2. Interactivity** — Tabs / Counter-stats / Marquee-carousel / GSAP scroll-reveal / Hover
   states / Other / None (static)
**3. Copy notes** — Placeholders to flag, copy to preserve exactly, or content that differs
**4. Page slug** — What page is this section being added to? (e.g. `monday-agents`)

Reply here and I'll build it.
```

**STOP after posting.** Do not proceed to Turn 2 until the reply arrives.

## Turn 2 — Build Phase

_Precondition: brief received. Extract `section_purpose`, `interactivity_list`, `copy_notes`,
`page_slug`._

**Before writing any HTML/CSS: run `CLAY-INTEGRATION.md`'s resolution process for this
section (H28 first: Clay-Web instance or matching component name → `connections.json`, do not
rebuild from pixels or ask which component)**, then continue below with the resolved anchor
(or lack of one) in hand.

Set paths:
```
DELIVERABLES_DIR = <deliverables folder>/fig-2-web/
PREVIEW_PATH    = DELIVERABLES_DIR/<section-slug>-preview-v01.html
PAGE_PATH       = DELIVERABLES_DIR/<page-slug>-page-v01.html
QA_PATH         = DELIVERABLES_DIR/<section-slug>-qa-v01.png
FIGMA_REF_PATH  = DELIVERABLES_DIR/<section-slug>-figma-ref-v01.png
ASSETS_DIR      = /tmp/<section-slug>-assets/
```
Create `DELIVERABLES_DIR` and `ASSETS_DIR` if missing.

### Step 4: Asset Download

**Two methods — try 4a first, fall back to 4b:**

**4a. CDN URL extraction (preferred).** `get_design_context` emits `const imgX = "https://www.figma.com/api/mcp/asset/..."`
constants — the original uploaded source images, no extra MCP call needed:
```python
import re
CDN_PATTERN = re.compile(r'const (img\w+) = ["\']([^"\']+www\.figma\.com/api/mcp/asset/[^"\']+)["\']')
cdn_assets = {}
for match in CDN_PATTERN.finditer(design_context_code):
    var_name, url = match.group(1), match.group(2)
    ext = url.rsplit('.', 1)[-1].lower() if '.' in url.rsplit('/', 1)[-1] else 'png'
    cdn_assets[var_name] = {'url': url, 'filename': f"{var_name}.{ext}", 'ext': ext}

import subprocess, os
os.makedirs(ASSETS_DIR, exist_ok=True)
for var_name, info in cdn_assets.items():
    dest = os.path.join(ASSETS_DIR, info['filename'])
    subprocess.run(['curl', '-sL', '-o', dest, info['url']], check=True)
```

**Multi-layer photo heuristic:** Figma often stacks multiple images in one card using the same
base variable (`imgImage`) as a placeholder with unique photos on top. The last-declared
variable in DOM order is on top (visible). A base layer shared identically across all cards is
a background texture, not the card photo — prefer the card-specific layer. When ambiguous, use
the variable with the largest declared bounding box.

**4b. Fallback: `download_assets(fileKey, nodeId)`** when 4a returns no CDN URLs. Download
immediately per asset:
```bash
curl -sL -o "<ASSETS_DIR>/<descriptive-name>.<format>" "<asset-url>"
```
Use the response's `format` field as the extension; if `"original"`, infer from the URL, default
`.png`.

**4c'. Export matched Assets-frame visuals as single flat images (H9)** — for each matched node
from Step 2f: `get_screenshot(fileKey, nodeId, maxDimension=<2x longer edge, capped>)`, download
immediately, named descriptively. Don't also pull CDN URLs for fills inside that same node.

**4c. Copy the Figma reference:** `cp "/tmp/<section-slug>-figma-ref.png" "<FIGMA_REF_PATH>"`.

**Before serving any downloaded asset, run `file <path>`** — an implied extension doesn't
always match the true format (see `GOTCHAS.md`).

### Step 5: Token Resolution

**Primary method: `CLAY-INTEGRATION.md`'s resolution process** for any section it resolved.

**Fallback — raw variable → CSS custom property mapping**, for values not covered:

| Figma variable pattern | CSS custom property |
|---|---|
| `color/brand/primary` | `var(--clay-color-brand-primary)` |
| `color/brand/secondary` | `var(--clay-color-brand-secondary)` |
| `color/bg/primary` | `var(--clay-color-bg-primary)` |
| `color/bg/secondary` | `var(--clay-color-bg-secondary)` |
| `color/bg/tertiary` | `var(--clay-color-bg-tertiary)` |
| `color/text/primary` | `var(--clay-color-text-primary)` |
| `color/text/secondary` | `var(--clay-color-text-secondary)` |
| `color/text/disabled` | `var(--clay-color-text-disabled)` |
| `color/border/primary` | `var(--clay-color-border-primary)` |
| `color/border/secondary` | `var(--clay-color-border-secondary)` |
| `spacing/4xl`…`spacing/2xs` | `var(--clay-spacing-4xl)` … `var(--clay-spacing-2xs)` |
| `radius/s`…`radius/full` | `var(--clay-radius-s)` … `var(--clay-radius-full)` |

For any variable not in this table, use the raw resolved hex/px value. **`grep` any token name
against the compiled `tokens.css` before trusting it** — names drift between repo versions.

**This table assumes the Figma file's own variable names resemble Clay's naming convention
(`color/brand/primary`, etc.) — a real downstream product file's variables may share no naming
convention with Clay's at all** (confirmed case: variable names were specific to that file's own
design-token system, unrelated to Clay's). When that's true, the table above is unusable as
written. **What actually works: resolve the Figma variable to its literal value (hex/px) first,
then `grep` the compiled `tokens.css` by *value*, not by name**, to find whether a matching real
Clay token already exists — matching by name only works when the source file happens to share
Clay's vocabulary, which is not guaranteed just because `CLAY_DESIGN=true`.

If `CLAY_DESIGN=false`: use raw hex/px values directly, no `var(--clay-*)` references.

### Step 6: HTML Section Block Generation

```html
<!-- SECTION: <section-slug> -->
<section id="<section-slug>" data-section="<section-slug>" data-page="<page-slug>" class="section-<section-slug>">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <!-- unique section content here — never directly in section / padding-global / container-large -->
      </div>
    </div>
  </div>
</section>
<!-- /SECTION: <section-slug> -->
```

Header/nav and footer do **not** use this nest. If this node's `role` is `header` or `footer`
(`FULL-PAGE-WORKFLOW.md` Step 2 / `PAGE-STRUCTURE.md`), emit:

```html
<header data-section="<section-slug>" data-chrome="header" data-page="<page-slug>">
  <!-- chrome content — own layout, H25 -->
</header>
```

(or `<footer data-chrome="footer">`). Do not wrap chrome in `padding-global`.

CSS as a scoped `<style>` block above the section, every *section-specific* class prefixed with the section slug.
Do **not** re-declare `.padding-global` / `.container-large` / `.padding-section-large` here — those live
once in the page shell (Step 7).
(never generic names like `.hero`/`.card`/`.button` without the prefix, to prevent collisions
when multiple sections share a page):

```html
<style>
.section-<section-slug> {
  background: <bg-color>;
  padding: <padding-top> <padding-right> <padding-bottom> <padding-left>;
  width: 100%;
}
.section-<section-slug>-inner {
  display: flex; flex-direction: <row|column>; gap: <gap>;
  align-items: <align from Figma>;
}
.section-<section-slug> .heading {
  font-family: <font-family>, system-ui, sans-serif;
  font-size: <size>px; font-weight: <weight>; color: <color>; line-height: <line-height>;
}
</style>
```

**Rules:** `px` for all extracted measurements. Responsive: `@media (max-width: 768px)` stacks
to `flex-direction: column`, reduces font sizes ~15%. Images: `<img src="..." alt="..." width="<intrinsic-w>" height="<intrinsic-h>" loading="<eager|lazy>" class="section-<slug>-<role>">`
(H11–H13).

**Media slot pattern (H9 + H10 + H12):**
```css
.section-<slug>-visual {
  width: <intrinsic-w>px;   /* or 100% in a flexible layout */
  aspect-ratio: <intrinsic-w> / <intrinsic-h>;
  border-radius: 0 <r>px <r>px 0;
  overflow: hidden;
  background: <fallback bg color matching the panel's own fill>;
}
.section-<slug>-visual img { width: 100%; height: auto; display: block; }
```
Never add a breakpoint override with a fixed `height` — only change `position`/`width` between
breakpoints; `aspect-ratio` + `height: auto` carries the correct height at every size.

**Approved CSS simplification for multi-layer/negative-offset photo compositions:** Figma's
`left: -Npx; width: W+Npx` panned-crop pattern maps to `overflow: hidden` on the container plus
`width: 100%; height: 100%; object-fit: cover; object-position: <match crop direction>` on the
`<img>` — faithful to the visual intent without replicating exact pixel offsets.

**Interactivity — add only what was specified in the brief, or halted-and-asked per
`ASK-DONT-GUESS.md` if unclear:**

_Tabs:_
```html
<div class="section-<slug>-tabs">
  <div class="tab-nav" role="tablist">
    <button class="tab-btn active" role="tab" data-tab-target="tab-<slug>-0" aria-selected="true">Tab 1</button>
    <button class="tab-btn" role="tab" data-tab-target="tab-<slug>-1" aria-selected="false">Tab 2</button>
  </div>
  <div class="tab-panels">
    <div class="tab-panel active" id="tab-<slug>-0" role="tabpanel">...</div>
    <div class="tab-panel" id="tab-<slug>-1" role="tabpanel">...</div>
  </div>
</div>
<style>
.section-<slug>-tabs .tab-panel { display: none; }
.section-<slug>-tabs .tab-panel.active { display: block; }
</style>
<script>
(function() {
  var tabs = document.querySelector('.section-<slug>-tabs');
  if (!tabs) return;
  var btns = Array.from(tabs.querySelectorAll('.tab-btn'));
  var panels = Array.from(tabs.querySelectorAll('.tab-panel'));
  function activate(i) {
    btns.forEach(function(b, j) { b.classList.toggle('active', j === i); b.setAttribute('aria-selected', j === i ? 'true' : 'false'); });
    panels.forEach(function(p, j) { p.classList.toggle('active', j === i); });
  }
  btns.forEach(function(btn, i) { btn.addEventListener('click', function() { activate(i); }); });
  var current = 0;
  var interval = setInterval(function() { current = (current + 1) % btns.length; activate(current); }, 5000);
  tabs.addEventListener('mouseenter', function() { clearInterval(interval); });
})();
</script>
```

_Counter/stats (IntersectionObserver):_ mark each stat with `data-count="<target>"`:
```javascript
<script>
(function() {
  var counters = document.querySelectorAll('[data-section="<section-slug>"] [data-count]');
  if (!counters.length) return;
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (!entry.isIntersecting) return;
      var el = entry.target, target = parseInt(el.getAttribute('data-count'), 10);
      var duration = 1500, start = null;
      function step(ts) {
        if (!start) start = ts;
        var progress = Math.min((ts - start) / duration, 1), eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * target).toLocaleString();
        if (progress < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step); observer.unobserve(el);
    });
  }, { threshold: 0.4 });
  counters.forEach(function(c) { observer.observe(c); });
})();
</script>
```

_CSS marquee:_
```html
<div class="section-<slug>-marquee-viewport" aria-hidden="true">
  <div class="section-<slug>-marquee-track"><!-- items, duplicated once for seamless loop --></div>
</div>
<style>
.section-<slug>-marquee-viewport { overflow: hidden; width: 100%; }
.section-<slug>-marquee-track {
  display: flex; gap: <gap from Figma>px; width: max-content;
  animation: marquee-<section-slug> <duration>s linear infinite;
  /* Duration: total_single_set_width_px / 100 ≈ 100px/s. Tune to ~150px/s for logo bars,
     ~60px/s for readable quote strips. */
}
.section-<slug>-marquee-track:hover { animation-play-state: paused; }
@keyframes marquee-<section-slug> { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
@media (prefers-reduced-motion: reduce) { .section-<slug>-marquee-track { animation: none; } }
</style>
```

_GSAP scroll-reveal:_ add `class="reveal"` to elements that should animate in:
```javascript
<script>
gsap.registerPlugin(ScrollTrigger);
gsap.from('[data-section="<section-slug>"] .reveal', {
  scrollTrigger: { trigger: '[data-section="<section-slug>"]', start: 'top 80%', toggleActions: 'play none none none' },
  y: 36, opacity: 0, duration: 0.65, stagger: 0.10, ease: 'power2.out'
});
</script>
```

_Static (no interactivity specified):_ pure HTML/CSS only, no `<script>` tags.

### Step 7: Page Shell Construction

Used for both the preview file and the initial page file.

**Custom font detection:** scan typography for any `font-family` not in the system stack
(`system-ui`, `Inter`, `Arial`, `Helvetica`, `Georgia`, `Times New Roman`). If found: check
Google Fonts availability; if available, set `GOOGLE_FONT_FAMILY`/`GOOGLE_FONT_WEIGHTS`; if not
(a custom/proprietary font), note the gap and fall back to `system-ui`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><page-slug> — <section-name></title>
  <!-- <link href="<GOOGLE_FONT_URL>" rel="stylesheet"> — only if a non-system font was detected -->
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { min-height: 100%; }
    body { font-family: '<detected-font>', system-ui, -apple-system, sans-serif; -webkit-font-smoothing: antialiased; color: #111; }
    img { display: block; max-width: 100%; height: auto; }
    /* PAGE-STRUCTURE.md shell — class names fixed; values = this page's H22 pair (Clay token or Figma, see PAGE-STRUCTURE.md) */
    .padding-global { padding: 0 var(--clay-layout-section-padding-x, 2.5rem); }
    @media screen and (max-width: 767px) {
      .padding-global { padding: 0 var(--clay-layout-section-padding-x-mobile, 1.5rem); }
    }
    .container-large { width: 100%; max-width: var(--clay-layout-container-large, 80rem); margin: 0 auto; }
    .padding-section-large { padding: clamp(4rem, 3.4286rem + 2.8571vw, 6rem) 0; }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }
  </style>
  <!-- GSAP CDN: only if this section uses scroll-reveal or another GSAP animation -->
</head>
<body>
<div class="page-wrapper">
  <header>
    <!-- empty until a role=header node is built; then replaced as a whole -->
  </header>
  <main class="main-wrapper">
<style>/* Section styles for <section-slug> */</style>
<!-- SECTION: <section-slug> -->
<section id="<section-slug>" data-section="<section-slug>" data-page="<page-slug>" class="section-<section-slug>">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <!-- section HTML content -->
      </div>
    </div>
  </div>
</section>
<!-- /SECTION: <section-slug> -->
<!-- section-scoped scripts here -->
<!-- SECTIONS_END -->
  </main>
  <footer>
    <!-- empty until a role=footer node is built; then replaced as a whole -->
  </footer>
</div>
</body>
</html>
```

**GSAP CDN rule:** uncomment the CDN `<script>` tags in `<head>` if and only if scroll-reveal or
another GSAP animation was requested. Tabs, counters, marquee need no GSAP — pure JS + CSS.

**Preview file** = this shell with the section (or chrome) inside, written to `PREVIEW_PATH`.
**Initial page file** (first node for this page) = the same shell, written to `PAGE_PATH`.

If this node's `role` is `header` or `footer`, put that chrome in `<header>` / `<footer>` and
leave `main.main-wrapper` containing only `<!-- SECTIONS_END -->` — do not also park a content
`<section>` in `main` for chrome.

### Step 8: Image Compression and Folder Export (H4 — no base64)

Run the PIL compression pipeline on `PREVIEW_PATH`, writing real files into
`IMAGES_DIR = <DELIVERABLES_DIR>/images/<section-slug>/` and rewriting `<img>` `src` to relative
paths — never base64.

**Size the resize target to the image's actual rendered display width, not a flat ceiling.**
Confirmed real case: a set of carousel cards displayed at ~300px CSS width shipped with Figma
source assets at their raw uploaded resolution (2304×4096–3277×4096px) — a flat `max_width=1440`
default still left each file 5–10x larger than its on-screen size ever needs (multiple 1.5–2.9MB
files for a 300px-wide slot), and was reproducibly heavy enough to cause visible scroll/render
jank in downstream QA tooling. `max_width=1440` is a reasonable *ceiling* for a genuinely
full-bleed/hero image, but it is not a safe default for every image regardless of how small its
own container actually is.

```python
import os
from PIL import Image

IMAGES_DIR = os.path.join(DELIVERABLES_DIR, "images", section_slug)
os.makedirs(IMAGES_DIR, exist_ok=True)

RETINA_FACTOR = 2       # render at 2x the CSS display width for crisp high-DPI screens
CEILING_WIDTH = 1600    # never exceed this even for a full-bleed hero/background image

def resize_target_width(display_width_px, ceiling=CEILING_WIDTH):
    """display_width_px = the image's real rendered CSS width in this section (from
    get_design_context/get_metadata, or the container it fills) — NOT the source asset's
    intrinsic width. Falls back to the ceiling only when no display width is knowable
    (e.g. a background used at multiple sizes) — never as the default for a normal <img>."""
    if display_width_px is None:
        return ceiling
    return min(int(display_width_px * RETINA_FACTOR), ceiling)

def compress_raster(image_path, dest_path, display_width_px=None, jpeg_quality=82):
    max_width = resize_target_width(display_width_px)
    with Image.open(image_path) as img:
        if img.mode == 'RGBA':
            if img.width > max_width:
                ratio = max_width / img.width
                img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
            img.save(dest_path, format='PNG', optimize=True); return
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        if img.mode not in ('RGB', 'L'): img = img.convert('RGB')
        img.save(dest_path, format='JPEG', quality=jpeg_quality, optimize=True)

def copy_svg(svg_path, dest_path):
    with open(svg_path, 'rb') as f: data = f.read()
    with open(dest_path, 'wb') as f: f.write(data)

RASTER_EXTS, SVG_EXTS = ('.png', '.jpg', '.jpeg', '.webp', '.gif'), ('.svg',)
exported = {}
for fname in os.listdir(ASSETS_DIR):
    fpath, dest, low = os.path.join(ASSETS_DIR, fname), os.path.join(IMAGES_DIR, fname), fname.lower()
    if low.endswith(SVG_EXTS): copy_svg(fpath, dest)
    elif low.endswith(RASTER_EXTS):
        # display_width_px: read from this image's own CSS width in the section being built
        # (get_design_context's layout data), not guessed — see resize_target_width above.
        compress_raster(fpath, dest, display_width_px=known_display_width_for(fname))
    else: continue
    exported[fname] = f"images/{section_slug}/{fname}"

def relink_assets_in_html(html_path, exported):
    """Point src="<filename>" at the exported relative path — used for BOTH the preview
    file here AND the page file in Step 9g. Never base64 for either (H4)."""
    with open(html_path, 'r', encoding='utf-8') as f: html = f.read()
    for fname, rel_path in exported.items():
        html = html.replace(f'src="{fname}"', f'src="{rel_path}"').replace(f"src='{fname}'", f"src='{rel_path}'")
    with open(html_path, 'w', encoding='utf-8') as f: f.write(html)
    return os.path.getsize(html_path)

preview_html_bytes = relink_assets_in_html(PREVIEW_PATH, exported)
images_total_bytes = sum(os.path.getsize(os.path.join(IMAGES_DIR, f)) for f in os.listdir(IMAGES_DIR))
print(f"Preview HTML: {preview_html_bytes/1024:.0f}KB — images/ folder: {images_total_bytes/1024:.0f}KB")
# The HTML should now be tiny (tens of KB) — no encoded image data. If it's still large,
# something is being embedded — check for a leftover data: URI.
```

Note the two files that must ship together from now on: the HTML and its
`images/<section-slug>/` folder. State this explicitly in Step 12.

### Step 9: Page Accumulation — Sentinel Injection

**9a.** `page_exists = os.path.isfile(PAGE_PATH)`.

**9b. Duplicate check (H6).** If `page_exists` and `data-section="<slug>"` already appears,
stop and warn: _"Section '<slug>' already exists in <page-slug>-page-v01.html. Reply 'replace
it' to overwrite, or 'skip' to keep it."_ Raise and await instruction. If the user said "replace
it," remove the existing block (`<!-- SECTION: slug --> … <!-- /SECTION: slug -->`) first, then
proceed as Case B.

**9c. Extract the new section block** (plus its scoped `<style>` block) from the preview HTML.

**9d. Extract new `<head>` dependencies** not already in the page file (script `src`s, link
`href`s) — only inject the ones missing (H8).

**9e. Case A — first section for this page:** copy `PREVIEW_PATH` → `PAGE_PATH` verbatim. The
preview must already be the `PAGE-STRUCTURE.md` shell (H27). Verify the sentinel sits immediately
before `</main>` (H7) — abort loudly if not.

**9f. Case B — subsequent content section (`role=section`):** back up `PAGE_PATH` first (`.bak`).
Inject the new section block + an audit comment (`<!-- SECTION_ADDED: <slug> on <date> -->`)
immediately before the sentinel; inject any new head dependencies before `</head>`. Write, then
re-read and verify the sentinel is still immediately before `</main>` (H7) — if not, restore the
backup immediately and raise, do not retry blindly. Remove the backup only after a verified
successful write.

**9f-chrome. Subsequent header/footer (`role=header` or `role=footer`):** replace the empty
`<header>` or `<footer>` in the shell with the chrome block (`data-chrome="header"` /
`data-chrome="footer"`). Do not inject chrome before the sentinel and do not wrap it in
`padding-global`. Same backup/verify discipline as 9f.

**9g. Relink assets in the page file — same pipeline as Step 8, never base64.** Run
`relink_assets_in_html(PAGE_PATH, exported)` (the same function from Step 8) so the accumulated
page's `<img>` tags point at the real `images/<section-slug>/` files exactly like the preview
does. **Do not run a base64-embed pipeline here** — H4 applies uniformly to both files; an
earlier draft of this workflow embedded the page file as base64 while keeping the preview file
as real links, which directly contradicted H4 and is not the intended behavior.

**9h.** Count sections: `page_final.count('<!-- SECTION:')`.

### Step 10: QA Screenshot

Take a screenshot of the preview file for comparison against the Figma reference — this feeds
the mandatory per-section vision QA in `ACCURACY-GATE.md`; the screenshot alone is not the QA
step, looking at it next to the Figma reference is.

**Serve over `http://localhost`, never `file://`** (`GOTCHAS.md`'s asset-loading gotcha: a bare
`file://` URL has no real network layer for local relative-path assets, so every `<img>` can
silently fail to load while the screenshot still looks plausible). Start the server **once per
session**, before the first section, not per section: `python3 -m http.server <port> --directory
<DELIVERABLES_DIR>` in the background, then load `http://localhost:<port>/<section-slug>-preview-v01.html`.

```python
import asyncio
from playwright.async_api import async_playwright

async def take_qa_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=CHROMIUM_PATH)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(f"http://localhost:{PORT}/{os.path.basename(PREVIEW_PATH)}")
        await page.wait_for_timeout(1800)  # let CSS animations (marquee, transitions) settle
        await page.screenshot(path=str(QA_PATH), full_page=True)
        await browser.close()

asyncio.run(take_qa_screenshot())
```

**`CHROMIUM_PATH` must be discovered, never hardcoded** — see `PREREQUISITES.md`/
`CLAY-INTEGRATION.md`'s discovery pattern; a prior version of this workflow hardcoded a
machine-specific path here that doesn't exist on other machines.

Sync API alternative (simpler, fine for static sections) uses the same discovered
`CHROMIUM_PATH`, scrolls to trigger IntersectionObserver-gated animations, then screenshots
full-page. If Playwright fails (chromium not found, launch error), note it and continue — the
HTML files are still valid deliverables.

### Step 10b: `tools/qa_gate.py` — mandatory, run here, not just described in `ACCURACY-GATE.md`

**Confirmed real regression this replaces:** the two third-party tools previously required at this
step were marked "mandatory, not optional," and a full section-by-section build still shipped
with neither ever invoked inside the actual per-section loop — the mandate living only in
a file that *describes* the gate conceptually, rather than in the file that drives the build turn
by turn, was not enough to make it run. The fix isn't a better reminder; it's a single command
with an exit code, run here, every section, right after the QA screenshot and before delivery:

```bash
python3 ~/.claude/skills/figma-to-web/tools/qa_gate.py section \
    --url http://localhost:<port>/<section-slug>-preview-v01.html \
    --selector '[data-section="<section-slug>"]' \
    --spec /tmp/<section-slug>-spec.json
```

See `ACCURACY-GATE.md` §1b for the full check list this runs (numeric re-diff against the
pre-build spec, leaf-centering, image-loaded, a11y disclosure state, 3-width overflow) and what
its `vision_owned` output means. Triage every finding: fix it, or log an explicit accepted-gap
reason. **Log the outcome either way** — `[QA] <slug>: qa_gate clean, N checks` or
`[BUG] <slug>: <rule-id> <measured> vs. <expected>` — so a later reader of the trace can tell "ran
clean" apart from "never ran," the same distinction `PRE-BUILD-VERIFICATION.md`'s
`[PRE-BUILD-CHECK]` tag makes for the pre-build checklist. A section is not through Turn 2 until
this has a log line and exits 0, same discipline as the vision QA screenshot.

### Step 11: File Delivery

Copy the preview HTML, QA screenshot, and the **entire images folder** together — never the
HTML alone (H4). State explicitly that both must travel together and that a plain file-preview
pane (e.g. Slack's) will likely show broken images unless both are downloaded into the same
local directory. The accumulated page file is not part of routine delivery — it can be large
after many sections; share it only if asked.

### Step 12: Delivery Reply

Before writing the reply, run `date "+%Y-%m-%d %H:%M:%S"` again and log
`[TIME] end <section-slug> (<node-id>): <timestamp>, duration <computed duration>` to the
project's trace file, right next to the `[TIME] start` entry from Step 0 — this pair is what
makes "how long did this take" answerable later without reconstruction. Note *why* in one clause
if the section was unusually fast or slow (e.g. "reused a prior build", "required fetching a live
site's real CSS", "straightforward Clay EXACT match") — that qualitative tag is what turns a
timing log into something actionable for shortening the process, not just a stopwatch.

```
Section built: **<node-name>** (<width>×<height>px)

Page: `<page-slug>-page-v01.html` — section <N> of <N> total
Preview: `<section-slug>-preview-v01.html` + `images/<section-slug>/` folder (download BOTH into
the same directory)

What was built:
- Layout: <flex row | flex column | grid>, <N> child elements
- Background: <color value>
- Interactivity: <what was added, or "none — static HTML/CSS">
- Images: <N> assets exported to `images/<section-slug>/` (<KB/MB total>, not embedded)
- Tokens: <Clay CSS custom properties | raw Figma values> | Clay anchor: <EXACT/CLOSEST/BORROWED/ATOMS_ONLY/none>

Sections in `<page-slug>-page-v01.html` so far: 1. <slug> … N. <slug> ← just added

Time: <duration> (started <start timestamp>, finished <end timestamp>)

QA screenshot attached — compared to the Figma reference from Turn 1 (per-section vision QA:
PASS/issues noted).

Known gaps (anything approximated, or halted-and-asked per ASK-DONT-GUESS.md): <list, or "none">

To add the next section, run this skill again with a new Figma section node URL and page slug
`<page-slug>`.
```

## Output File Structure

```
fig-2-web/
├── <section-slug>-figma-ref-v01.png
├── <section-slug>-preview-v01.html      ← standalone preview (links to images/, not self-contained)
├── <section-slug>-qa-v01.png
├── <page-slug>-page-v01.html            ← accumulated page (OVERWRITTEN each run, grows by one section)
└── images/
    ├── <section-slug>/                  ← this run's exported images (real files, H4)
    └── <other-section-slug>/            ← previous sections' images, still referenced
```

The page file is overwritten (not versioned) each run so one browser tab can reload to see the
page grow. The `images/` folder only ever grows — every prior section's subfolder must stay in
place.

## Known Limitations

- **Complex absolute/overlapping layouts** are usually a sign of a composite visual asset, not
  structure to translate — check for an `Assets` frame per H9 before hand-tuning CSS.
- **Multi-layer photo stacking:** a shared base/texture layer across cards is a placeholder, not
  a card photo — see the Step 4a heuristic. Doesn't apply to a matched H9 Assets-frame panel.
- **Figma prototype interactions** (hover states as prototype transitions, not component
  properties) are not captured by `get_design_context` — must come from the brief, or trigger
  `ASK-DONT-GUESS.md` if the brief doesn't cover them.
- **Custom/proprietary fonts** fall back to `system-ui` — flag it, don't silently substitute.
- **Context limit on dense sections:** `get_metadata` → per-child `get_design_context` → merge.
- **SVG fill images** appear in `download_assets` as `.svg` — copy byte-for-byte, no PIL
  compression; inline directly (`<svg>...</svg>`) rather than as `<img>` for CSS fill control.
- **Page file growth over time:** after many sections the page file may be large — the images
  stay as real linked files regardless (H4 has no size-based exception).

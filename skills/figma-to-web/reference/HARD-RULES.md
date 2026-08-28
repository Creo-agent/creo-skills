# Hard Rules — Read Before Every Task

## Contents
- H1 — No screenshots as content
- H2 — No Clay component names in vanilla HTML output
- H3 — Full-page mode is section-by-section, not one pass over the whole frame
- H4 — Real linked image files by default; base64 only for an optional single-file share variant
- H5 — Mandatory baseline interactivity for full-page builds
- H6 — Never duplicate a section in the page file
- H7 — Always preserve the sentinel
- H8 — One `<head>`, no duplicate dependencies
- H9 — Detect and flatten composite visual-asset frames; never hand-rebuild them
- H10 — Media sizing: aspect ratio always, literal inset geometry when the layer doesn't fill its slot
- H11 — Every image needs meaningful alt text
- H12 — Explicit width/height attributes on every `<img>`, paired with `height: auto` in CSS
- H13 — Lazy-load below the fold — but never inside a JS/transform-driven slider
- H14 — Explicit font-weight on every heading rule
- H15 — Trim the sibling, don't let text wrap
- H16 — Size from the element's own authored geometry, never from a sibling's convention, a prior build's convention, or today's copy length
- H20 — A mobile state-variant rule's specificity still applies at desktop unless explicitly overridden inside the desktop media query
- H21 — Every capsule/pill CTA button on a page shares one size+style, even when a later Figma instance's own literal size differs
- H22 — Every section on a page shares one container max-width and one responsive side-padding pair, even when a later Figma instance's own literal frame width differs
- H23 — Reproduce a design-context React snippet's `-scale-y-100`/`-scale-x-100` wrapper in the final CSS unless it's paired with a canceling `rotate-180deg` on the same element
- H24 — Never assume inherited `text-align: center` centers an `<img>`; a global `img { display: block }` reset silently breaks it — verify every leaf element's own position, not just its wrapper's
- H25 — For global chrome (header/nav/footer), always check `connections.json` for a real coded match before reverse-engineering a live reference
- H26 — Resuming after a context summary/compaction is not a fresh state — re-confirm every section's Clay anchor before writing any HTML/CSS
- H27 — Every page uses the PAGE-STRUCTURE.md skeleton (page-wrapper / header / main-wrapper / section nest / footer)
- H28 — A Clay-Web library instance (or matching Clay component name) must resolve to coded Clay — never rebuild from pixels
- H29 — A downloaded asset is not verified until its pixels are — `naturalWidth > 0` does not mean the file contains artwork
- H30 — Never substitute a Unicode glyph or emoji for a real Figma icon; a glyph passes every automated gate and hides at full-page zoom
- H31 — A static Figma frame carrying a motion/interaction tell (edge-clipped wide text, an emphasized card strip, duplicated/sliced items) resolves to motion, never a from-scratch static build
- H32 — A full-page build persists the page HTML + trace to disk after every section; never hold more than one section of unwritten work, never build in one large turn
- H33 — Never recreate a logo — use the real vector or stop and ask; fixed source order (product logo library → Figma SVG export → stop)

These are non-negotiable. They override any shortcut or heuristic in `SECTION-WORKFLOW.md` or
`FULL-PAGE-WORKFLOW.md`. **They apply the same way in both modes** — building one section and
building a full page are the same process at different scopes (see H3), not two different rule
sets.

## H1 — No screenshots as content

**Owner:** vision

`get_screenshot` and `download_assets` exports are **QA references only** — never section or
page content. Never use a Figma screenshot as a full-width `<img>` tag to "represent" a section.

This was the v02 failure on the monday AI Agents Page: high visual similarity (~9/10) but the
output was a screenshot gallery, not a website — not interactive, not responsive, not
accessible, not real code.

**The only images that belong in the HTML are:**
- Visual assets that exist as image *fills* in Figma nodes — photos, product UI screenshots,
  logos, illustrations — downloaded via `download_assets`
- SVG icons exported from vector layers

**Never:**
- A screenshot of a whole Figma section used as `<img>`
- A screenshot of a group/frame used as a section background or a workaround for "hard to code"
  sections

If a section is complex, code it — use `get_variable_defs`/`get_metadata` for exact values and
`get_screenshot` as a side-by-side reference while writing the CSS.

**Before deciding a "hard to code" section is a flat screenshot, rule out H31:** a section whose
frozen frame looks static-and-uncodeable is often the resting frame of a moving component
(marquee, carousel, looping track). Reaching for a screenshot-as-content because the motion is
what makes it hard to reproduce is exactly the failure H31 guards against — check the tell-list
first.

## H2 — No Clay component names in vanilla HTML output

**Owner:** script

Even when a Clay design is detected, this skill produces **raw HTML/CSS only**. Never use:
- Clay React component names as HTML class names (`HeaderSection`, `CardGrid`,
  `FeaturesSection`, etc.), IDs, or structural guidance
- Clay React component imports or JSX
- Clay section-template names anywhere in the output

Clay token CSS custom properties (`var(--clay-color-*)`, `var(--clay-spacing-*)`) are fine and
encouraged — they are just CSS variables. Clay component names are not.

This was the v01 failure on the monday AI Agents Page: mapping Figma sections to Clay section
templates produced a generic monday.com marketing page that looked nothing like the Figma.
Fidelity was ~2/10. **Refinement from `CLAY-INTEGRATION.md`:** this rule bans Clay component
names as *class names/structural labels in the output HTML* — it does not ban resolving a
section against Clay's real component library to derive accurate structure/CSS/copy. The output
is still plain HTML; where that HTML's structure and values came from is a build-time decision,
not something that leaks into the class names.

## H3 — Full-page mode is section-by-section, not one pass over the whole frame

**Owner:** n-a

**There is no separate "full-page build process."** Building a whole page means: discover the
page's top-level sections, sorted by real `y` position (document/child order is not visual
order — see `FIGMA-EXTRACTION.md`), then run the *exact same* per-section process — Phase 1
Resolve, Phase 2 Build, mandatory per-section vision QA, inject — on each one in turn,
accumulating into one page file. `SECTION-WORKFLOW.md` is not a different skill's process that
full-page mode approximates; it **is** the loop body.

This is also a hard technical requirement, not just an architectural preference: a full Figma
page frame processed with a single `get_design_context` call exceeds the tool's context limit on
large pages (~222K tokens for a 13-section, 14000px-tall frame — confirmed live). Always extract
section-by-section: `get_metadata` to list child sections → `get_design_context` on each child
node independently → build one `<section>` element per child. Never attempt a single
`get_design_context` call on an entire page frame.

**See also `FIGMA-EXTRACTION.md`**: `get_design_context` can also silently degrade to
metadata-only (generic layer names instead of real copy) on a single large *child* node, not
just the whole page — don't assume a suspiciously-generic result means "no content yet," drill
into smaller children instead.

**Named fallback when a single node still exceeds the inline cap (~82K chars):** some dense child
nodes (a carousel track, a floating-card collage, a full media panel) exceed the inline limit even
on their own. This is expected on large/dense nodes, **not an error to retry whole**. Drop to a
finer path immediately: `get_screenshot` for the visual reference + targeted per-child
`download_assets` for the exact media you need, rather than re-issuing the same over-cap
`get_design_context`. Treat the cap as the signal to go one level finer-grained (confirmed live on
the IT persona page: the agent-carousel track and the collage panel both tripped it and resolved
cleanly via screenshot + targeted export).

Once every section is built, run one additional full-page vision pass at desktop and mobile
widths (`ACCURACY-GATE.md` step 5) — this catches rhythm/spacing issues only visible in sequence
(a later section that doesn't fit the established visual rhythm, an overall page height gone
wrong) that no single section's own QA pass could catch.

## H4 — Real linked image files by default; base64 only for an optional single-file share variant

**Owner:** script

Do **not** embed images as base64 `data:` URIs in the primary deliverable — the working HTML
file must stay small and readable, and its `images/` folder is what makes it re-editable later.

- Compress each image via PIL and write it out as a real file into
  `<deliverables-dir>/images/<section-slug>/<descriptive-name>.<ext>`.
- Reference it with a plain relative path: `src="images/<section-slug>/<descriptive-name>.<ext>"`.
- Scope the subfolder per section so accumulating many sections into one page never collides two
  different sections' filenames.
- The `images/` folder must travel with the HTML — call this out explicitly in delivery.
- This applies uniformly to a single section's preview file AND the accumulated full-page file —
  no exceptions, including at accumulation time.

**Optional portable variant, for sharing where the file must survive without its `images/`
folder** (e.g. attaching one file to a message): produce a *second*, additional single
self-contained `.html` file with every image base64-embedded, PIL-compressed to JPEG q=60–70
first, targeting < 2MB total. Relative paths like `./assets/hero.png` break silently on macOS
when any parent directory name contains spaces — base64 sidesteps that for this one delivery
format. **This is an additional deliverable, not a replacement** — the real working folder with
linked files (per the rule above) still lives under the project directory as the editable record.

This was the v05 failure on the monday AI Agents Page: a ZIP with relative paths failed to open
because the path contained spaces; v06 fixed this with a single 0.9MB self-contained file offered
*alongside* the real linked-file version, not instead of it.

## H5 — Mandatory baseline interactivity for full-page builds

**Owner:** script

A full-page Figma-to-web output with no scroll animations, auto-advancing carousels, or entrance
effects is not acceptable as a final deliverable for a landing page.

**Required on every full-page build (not required for a single standalone section):**

| Feature | Implementation |
|---|---|
| **Scroll-reveal entrance animations** | GSAP + ScrollTrigger CDN; stagger fade-up on all major content blocks |
| **Auto-advancing tabs** | `setInterval` (4–6s) on any tab component; GSAP crossfade on panel switch |
| **CSS infinite marquee** | `@keyframes marquee` on logo strips and story carousels; pause on hover |
| **IntersectionObserver counters** | Animate numbers 0 → final value on scroll-enter for any stats/numbers section |
| **Sticky nav with scroll shadow** | `position: sticky; top: 0; z-index: 100;` + scrollY listener that adds a shadow class |

These features do not need to be pixel-identical to any Figma animation spec — they are
baseline production-quality web behaviors that any real landing page has. Apply them
intelligently based on section content.

**Non-negotiable companion (see `ASK-DONT-GUESS.md`):** H5 requires *some* baseline
interactivity on every full-page build, but never invent the *specifics* of a bespoke
interaction Figma doesn't specify (custom carousel behavior, an accordion's open/close rules, a
video's controls, or any section with ≥2 interdependent controls). Ship the generic H5 behaviors
freely; halt and ask before guessing anything more specific than that.

## H6 — Never duplicate a section in the page file

**Owner:** script

Before injecting, search the existing page file for `data-section="<slug>"`. If found, stop and
warn. Do NOT inject again until the user explicitly says "replace it". Applies whether you're
adding one section to an existing page or accumulating sections one by one in full-page mode.

## H7 — Always preserve the sentinel

**Owner:** script

The `<!-- SECTIONS_END -->` sentinel must be present immediately before `</main>` in the page
file at all times (inside `main.main-wrapper` — see `PAGE-STRUCTURE.md`). After writing, verify
the sentinel is still there. If missing, restore the pre-write backup immediately and report the
error. Do not place it before `</body>`: header/footer live outside `main`, and new content
sections inject immediately before this sentinel.

## H8 — One `<head>`, no duplicate dependencies

**Owner:** script

When injecting into an existing page file, never add duplicate `<script>` or `<link>` tags.
Read what's already in `<head>` before adding anything new.

## H9 — Detect and flatten composite visual-asset frames; never hand-rebuild them

**Owner:** vision

Some Figma layers are not structure to be translated 1:1 into HTML — they are pre-composed
**visual assets** (an illustration combined with floating "fake UI" mockup snippets: chat
bubbles, mini dashboards, cursors, stat cards) meant to be exported as a single flat image.
Recreating their internals as live HTML/CSS produces fragile, inaccurate output — treat this as
a bug, not a stylistic choice.

**Detection, in priority order:**
1. **Assets-frame convention (primary signal).** Look for a frame named `Assets` (or `Visual
   assets`/`Illustrations`) with children matching card/section titles. A match → export that
   child via `get_screenshot`, use as-is, never read its sub-layers.
2. **Naming fallback.** `Asset/`, `[export]` prefixes, or similar.
3. **Structural heuristic (last resort).** A frame mixing a raster illustration with clusters of
   tiny (<10px) decorative text/line-placeholder layers imitating a UI screenshot is almost
   always meant to be flattened.

**The real decision procedure, once a flatten candidate is identified:**
- **Section vs. asset, not size vs. asset.** A node being visually complex or "hard to code" is
  not sufficient reason to flatten it — check whether it has real interactive affordances (a
  button, tab, or accordion instance) or its own section-level heading/CTA. If so, it's a real
  section that happens to *contain* a flattenable asset, not itself a pure asset.
- **Flatten the smallest node that contains only the illustration.** Check whether a heading/
  subhead sibling sits next to the illustration (safe — flatten the illustration node alone) or
  the illustration is nested inside a container that also holds real text (flatten the child
  node, not the parent — flattening the parent bakes live text into the image as pixels).
- **Check whether `get_design_context` already resolved the composite to a single image
  constant** before running a separate `get_screenshot` flatten pass — sometimes the tool has
  already done this for you.
- **Not every image-heavy section is H9.** A repeated small-icon pattern (a glyph per feature
  item) is usually cheap and more maintainable to build as real HTML than to flatten — reserve
  H9 for genuinely composite, one-off illustrations.
- **When a flattened export comes back narrower than its declared frame**, use `object-fit:
  contain` against a matching background color — never stretch to fill or leave a mismatched
  edge.

If no Assets frame exists and the visuals aren't organized this way, say so explicitly and
suggest staging one, rather than silently reconstructing the mockup by hand.

**Before flattening a candidate, rule out H31:** a horizontal strip of peer cards or a
duplicated/frame-sliced row can *look* like a flatten candidate while actually being the resting
frame of a carousel or looping track. Flattening it bakes a moving component into a dead image.
Check H31's tell-list before treating any such frame as a pure visual asset — flatten a genuinely
static illustration, not the frozen frame of something that moves.

## H10 — Media sizing: aspect ratio always, literal inset geometry when the layer doesn't fill its slot

**Owner:** script

Every image container sizes itself from the image's own intrinsic aspect ratio — never an
independently chosen height. Set `aspect-ratio: <source-width> / <source-height>` on the
container (or derive it from `width` + `height: auto` on the `<img>`). Never write a breakpoint
override that sets a fixed `height` on a media slot without scaling `width` in the exact same
ratio — that mismatch is what silently forces an unintended `object-fit: cover` crop. A
deliberate crop is a conscious `object-position` decision, called out explicitly.

**When the populated image layer is smaller than its parent slot in Figma (not edge-to-edge),
reproduce its literal size/offset — don't stretch or `object-fit` it to fill the slot.** Check
the layer's own `x`/`y`/`width`/`height` against its parent slot's `width`/`height` from
`get_metadata`. If they differ (a confirmed real case: a 608×380 image at offset `41,130` inside
a 600×600 slot — an intentional inset with room to bleed past one edge, not a full-bleed photo),
express the child's geometry as percentages of the slot (`left: 41/600`, `top: 130/600`, `width:
608/600`, `height: auto` to preserve intrinsic ratio) with the container `position: relative`
and the image `position: absolute` — not `width: 100%; height: 100%` on the image with an
`object-fit` value chosen to compensate. Stretching to fill first and picking `object-fit` after
is what produces a wrong crop or a wrong scale; matching the authored geometry directly doesn't
need `object-fit` at all. This is a distinct failure mode from H9 (whether to flatten a
composite in the first place) — this is about a slot that legitimately holds one real image,
sized smaller than its own container on purpose.

**Sub-case — media that overlaps its own text frame ("peek" container):** for hero/portal/product
mockups, the media child's authored `y` sometimes places it *inside/over* its section's text
frame (the media starts partway up the section and bleeds below the fold). Reproducing this as a
hard-bounded full image looks wrong. Render the heading/sub as DOM, then place the media below in
a top-radius peek container — `border-radius:16px 16px 0 0; overflow:hidden` — so the mockup
appears to rise into the section and clip at the bottom, matching the design. Confirmed on the IT
persona page's SubTrack dashboard panel (media `y` sat inside a 252px-tall text frame within a
1016px section).

## H11 — Every image needs meaningful alt text

**Owner:** script

Content images get a real, descriptive `alt` — not an empty string, not the filename. Purely
decorative filler may use `alt=""`. When in doubt, describe it.

## H12 — Explicit width/height attributes on every `<img>`, paired with `height: auto` in CSS

**Owner:** script

Attributes match the source's intrinsic pixel dimensions (prevents CLS). CSS should control
only one axis — never fight the attributes with an independent CSS height, or you reintroduce
the H10 stretch/crop bug.

## H13 — Lazy-load below the fold — but never inside a JS/transform-driven slider

**Owner:** script

Normal below-the-fold images get `loading="lazy"`; above-the-fold get `loading="eager"`/no
attribute. **Hard exception:** carousels moved via `transform: translateX` must NOT use native
`loading="lazy"` on slides — unreliable (especially Safari/WebKit) behind an `overflow:hidden` +
transform ancestor rather than real scroll (confirmed real bug: cards 3+ of a 7-card slider
silently failed to load). Small/bounded carousels (~≤10 slides) load every slide eager instead.

## H14 — Explicit font-weight on every heading rule

**Owner:** script

Browsers apply a bold default to every `<h1>`–`<h6>` tag via the UA stylesheet. It's easy to
forget to override this when a design uses a regular-weight heading, especially when a *sibling*
heading elsewhere in the page happens to already have an explicit `font-weight` set (which masks
the bug on that one heading while leaving it live on others).

**Set `font-weight` explicitly on every heading-tag CSS rule, every time** — never rely on it
"happening" to render correctly just because another heading nearby does.

## H15 — Trim the sibling, don't let text wrap

**Owner:** vision

When a Figma text node's *declared* width exceeds its flex-sibling math (container width − gap −
sibling width), the designer's auto-sized text box tolerated the overflow but strict CSS flex
math doesn't — the text wraps to an extra line the design never intended.

**Fix pattern:** trim the gap or the sibling's width by the difference, rather than force-
shrinking the text or letting it wrap. This preserves the designer's intended line break.

## H16 — Size from the element's own authored geometry, never from a sibling's convention, a prior build's convention, or today's copy length

**Owner:** script

One governing principle, three confirmed failure sites — merged here because each is the same
mistake (a hand-picked or copied value standing in for a real measurement) at a different point
in the build, and reading three separate rules to recognize one pattern was costing more than the
rules were worth:

1. **A text node's CSS width.** Line breaks are a direct function of the width Figma gave the
   text box — cap the CSS element to that same `max-width` (from `get_metadata`), not whatever
   width the surrounding flex/grid math happens to compute at a given viewport. Confirmed real
   bug: a heading/body pair authored at a 600px text-box width wrapped correctly at the exact
   viewports checked by luck (the flex column happened to compute close to 600px there), then
   drifted at other widths between breakpoints, silently producing different line breaks than
   Figma's. Set the explicit `max-width` in px from the real text node's width. (Distinct from
   H15: H15 is about a sibling stealing width via flex math; this is about anchoring to the text
   box's own literal authored width regardless of what its siblings do.)
2. **N sibling instances in a row (a logo strip, an icon row, a badge list).** Confirmed real bug:
   7 logo instances got a flat `height:24px` on every `<img>`, copied from an already-shipped
   page's logo-bar convention — because the logos were the same brands, the sizing was assumed to
   be the same too. Each instance's own real geometry ranged ~11–43px; the flat value over-shrank
   some by half and over-grew others by 2x. Check each instance's own inner geometry individually
   — don't assume they share one dimension just because they look similar or came from the same
   family/brand set, or because a *different, already-built section* used one value. If Figma
   scales each one to fit a shared cell while preserving aspect ratio (the common case), reproduce
   a same-size wrapper box per item with `object-fit: contain` on the image inside, rather than
   hand-picking one dimension and applying it to every item.
3. **A placeholder/fallback that must always match its real siblings' size.** Confirmed real bug:
   a carousel's placeholder cards (standing in for slots with no real Figma content) were built
   with a skeleton sized to roughly match what the real cards' text happened to need *at the
   time* — visibly shorter once a real card's meta row (icons + CTA) was accounted for, and would
   silently drift again the next time any real card's copy changed length. Make matching a
   *structural guarantee*, not a content-matching exercise: `align-items: stretch` on the row,
   each item its own flex column, `flex: 1` on the item's growable text/body region — every item,
   placeholder or real, then takes on the height of whichever is tallest automatically, with no
   pixel value to keep in sync by hand.

Each site fails silently for the same reason: the wrong value still looks like a plausible design
choice (a nearby element, an earlier section, today's copy), so nothing about the result reads as
broken until it's placed next to the real geometry it should have been measured against
(`section_spec.py`'s pre-build measurement, or `CLAY-INTEGRATION.md`'s "Clay is the code basis,
Figma is the value source" applied to *this* section's own real nodes — never a sibling's, a
prior build's, or a guess).

## H20 — A mobile state-variant rule's specificity still applies at desktop unless explicitly overridden inside the desktop media query

**Owner:** script

Confirmed real bug: a horizontal card row (one card active/expanded, siblings collapsed) had a
mobile rule `.card[data-active="true"] { height: 420px; }` for its stacked mobile layout, and a
separate `@media (min-width: 900px) { .card { height: 100%; } }` meant to make every card the
same height at desktop, with only *width* changing on activation. At desktop widths, the active
card still rendered 420px instead of matching its siblings' 489px. Root cause: `.card{height:
100%}` (plain class, specificity 0,1,0) and `.card[data-active="true"]{height:420px}` (class +
attribute, specificity 0,2,0) are NOT equal specificity — the attribute-selector rule wins
regardless of source order or which one is inside a media query, because a `@media` block adds
no specificity of its own. The mobile-authored override kept winning at every viewport width.

**The fix pattern, and the rule going forward:** whenever a state-variant selector (`[data-
active]`, `[aria-expanded]`, `.is-open`, etc.) sets a property for one breakpoint that a plain
selector is meant to reset or normalize at another breakpoint, that reset must be written using
a selector of *equal or greater specificity* inside the later breakpoint's media query — e.g.
`.card[data-active="true"] { height: 100%; }` inside `@media (min-width: 900px)`, not just
`.card { height: 100%; }`. Before shipping any component whose active/inactive states differ
between mobile and desktop, explicitly check: for every property the mobile state-variant rule
sets, does the desktop breakpoint re-declare it on a selector that can actually beat that
attribute selector? A plain class-level override inside a later media query looks like it should
win by "coming later," but specificity is checked before source order, so it silently doesn't.

## H21 — Every capsule/pill CTA button on a page shares one size+style, even when a later Figma instance's own literal size differs

**Owner:** script

Confirmed real case: the page's first CTA button (in the hero) correctly used the real Clay
Button component's `mini` size (`class="btn mini style_primary color_black"`). A later section's
button, whose own Figma instance specified `size="Large"`, was built with an ad-hoc inline-style
override (`style="min-height:56px; padding:16px 24px; font-size:18px;"`) instead of reusing the
established `mini` class — same visual family (black capsule, primary), different actual size,
so the page ended up with two CTA buttons that don't match each other despite both reading as
"the primary button."

**The rule going forward:** once a page establishes its primary capsule-button size/style (from
whichever section builds it first — almost always the hero), **every subsequent primary CTA
button on that same page reuses that exact class combination**, not a new size class or an
inline-style override, even if that later section's own Figma instance literally specifies a
different size. This is one of the rare cases where page-level visual consistency outranks a
single instance's literal Figma value — Figma's per-instance size on a repeated CTA button is
usually itself just an authoring inconsistency (designers copy-pasting a button component and
occasionally picking the wrong size variant), not a deliberate "this one button should be
bigger" decision. Before writing any CTA button's markup, `grep` the page-in-progress for
`class="btn` first — if any prior section already established a size, match it exactly. Only
deviate if the user explicitly asks for a specific button to be visually distinct.

## H22 — Every section on a page shares one container max-width and one responsive side-padding pair, even when a later Figma instance's own literal frame width differs

**Owner:** script

Confirmed real case, on a page mixing sections built from a Clay component anchor, a live-site
reference (fetched per `CLAY-INTEGRATION.md`'s "user-supplied live-site reference" process), and
a reused prior test build: most sections correctly used `--clay-layout-container-large` (1440px)
for their container and the responsive `--clay-layout-section-padding-x-mobile`/`-x` pair
(24px → 80px) for side padding. Two sections silently deviated in each direction: one reused
section's own literal Figma frame width (1120px, or 1344px for another) was used as a *hardcoded
px* container cap instead of the shared token — even though this page's own loaded
`clay-tokens.css` resolves that exact token to 1440px, the same real number, just under a
different name. Two other sections used the *mobile* padding token (24px) unconditionally, with
no desktop override to the 80px value at all. Both mistakes are invisible in isolation (each
section "looks fine" on its own) and only show up as a real, visible width/alignment mismatch
once placed next to the rest of the page — caught here via `getBoundingClientRect()` measuring
the *actual rendered width* of every section's inner container side-by-side, not by reading the
CSS.

**The rule going forward:** exactly like H21 for buttons, a section's own literal Figma frame
width is not automatically the value to build with — check it against the page's already-
established container convention first. Before writing any section's container/padding CSS:
1. `grep` the page-in-progress for `.container-large` / `.padding-global` (the PAGE-STRUCTURE.md
   shell) or `max-width: calc(var(--clay-layout-container` (or any already-hardcoded max-width
   in a prior section) to find the established convention.
2. If a convention exists, use the exact same token/value, even if this section's own Figma
   frame is narrower or wider — a single instance's literal width is usually either an
   authoring artifact (an older/different iteration's frame width) or, for a genuinely-narrower
   inner content block, something that belongs on an *inner* content wrapper (a media composite,
   a text column) constrained *inside* the shared-width outer container — never on the section's
   own outermost container.
3. After all sections are built, verify with real measurements, not a read of the CSS:
   `document.querySelectorAll('[data-section]')` and `getBoundingClientRect().width` on each
   one's inner container at the same viewport width — every non-exempt section should report the
   same number. A section that's deliberately full-bleed/coast-to-coast (a carousel viewport, a
   marquee track) is a stated, intentional exception, not a silent deviation — it should still
   be a conscious design choice you can name, not a hardcoded leftover from a different source.

## H23 — Reproduce a design-context React snippet's `-scale-y-100`/`-scale-x-100` wrapper in the final CSS unless it's paired with a canceling `rotate-180deg` on the same element

**Owner:** vision

Confirmed real case: a `get_design_context` React snippet wrapped a flattened logo image in
`<div className="-scale-y-100 flex-none">` — Figma's own way of correcting an asset that's
authored upside-down in its raw exported file. That wrapper was dropped when converting the
snippet to a plain `<img>`, so the logo shipped upside-down. Caught only when the user pointed
at a screenshot — not by a QA pass, because the QA pass didn't specifically re-check image
*orientation* on every flattened logo/icon, only presence and general placement.

**Two rules, not one:**
1. **When converting any design-context snippet, treat every `-scale-y-100`/`-scale-x-100`
   class as a value to carry into the final CSS (`transform: scaleY(-1)` /
   `transform: scaleX(-1)`), not authoring noise to discard** — UNLESS that same element also
   carries `rotate-180deg` (or `rotate(180deg)`), in which case the two cancel to identity and
   neither needs to be reproduced (confirmed separately: a `-scale-y-100 rotate-180` combo on a
   different logo lockup earlier in this same build was correctly identity — net zero — and
   needed no CSS at all). Check for the pairing before deciding which case applies; don't assume
   either way from the class name alone.
2. **Per-section vision QA must include an explicit orientation check on every flattened
   logo/icon/wordmark image** — not just "is it present, is it roughly the right size and
   position." A brand logo (Gartner, a client mark, a wordmark) is exactly the kind of asset
   where an upside-down render can look "close enough" in a quick glance (right color, right
   rough shape) and still be wrong. Add this explicitly to `PRE-BUILD-VERIFICATION.md`'s
   checklist and `ACCURACY-GATE.md`'s per-section pass, not just to this file — a rule that only
   lives in HARD-RULES.md doesn't get *run*, it gets *known*.

## H24 — Never assume inherited `text-align: center` centers an `<img>`; verify every leaf element's own position, not just its wrapper's

**Owner:** script

Confirmed real case: a Gartner logo's card used `text-align: center` (inherited from an ancestor)
to center a logo + heading + description group. The heading and description centered correctly
— they're `<p>` tags, block-level, and `text-align` centers *text* within a block box. The `<img>`
did not center at all: the page's own global reset, `img { display: block; max-width: 100%; }`,
made the image a block box too, and **`text-align` only affects inline-level content — it has no
effect on a block box's own position.** With no `margin: 0 auto` of its own, the image sat flush
against its containing block's left edge, 90px off from where it visually needed to be.

This was reported by the user, investigated, and **incorrectly dismissed as a tooling artifact on
the first pass** — see `GOTCHAS.md`'s file:// asset-loading gotcha for how. The verification that
produced the wrong "no bug" conclusion measured `getBoundingClientRect()` on the *wrapper div*
around the logo+text group, found the wrapper centered, and stopped there. The wrapper being
centered is not the same claim as every child inside it being centered — it only proves the
group's overall bounding box lines up, not that each element inside independently occupies the
position it should.

**Two rules, not one:**
1. **Any `<img>` meant to be centered must get its own explicit `margin: 0 auto` (or sit inside a
   flex/grid ancestor with `align-items`/`justify-content: center`)** — never rely on an inherited
   `text-align: center` to reach it, because a `display: block` reset (extremely common, and
   already present on this very page for unrelated reasons — H4/H12's own image handling assumes
   it) silently defeats that inheritance with no visible error.
2. **When verifying a reported alignment/centering issue, measure the specific element being
   complained about, not just its nearest wrapper.** `getBoundingClientRect()` on a container
   proves the container's box is positioned correctly; it proves nothing about whether each child
   inside independently ended up where it should be. Before concluding "the wrapper is centered,
   therefore this isn't a bug," measure every visually-distinct child in that wrapper individually
   (image, heading, description, link — whatever the user is looking at) and compare each one's
   own center against the container's center. This is a specific, sharper case of
   `PRE-BUILD-VERIFICATION.md`'s general "for the section's root frame and every visually distinct
   sub-element" instruction — it applies just as much to *verifying a fix* as to building the
   first pass, and skipping it on the verification side produced a wrong answer reported straight
   to the user, not just a missed bug.

## H25 — For global chrome (header/nav/footer), always check `connections.json` for a real coded match before reverse-engineering a live reference

**Owner:** pre-build

Confirmed real case: a page's header and footer were rebuilt from a live-site reference — the
footer alone across **three** full rounds (guessed structure, corrected to real computed styles,
corrected again on real DOM structure) — before anyone checked `connections.json`, which had
exact matches for both the whole time (`Navbar`/"Nabar menu", confidence "shared";
`Footer`/"Format=Desktop, Style=Full", confidence "shared"), pointing at real, already-coded
components whose own source comment says outright: *"Canonical footer content for all pages...
never duplicate or override this content in individual pages."* This was the single most
expensive repeated miss across the whole build this rule is drawn from — full write-up and the
process to run in `CLAY-INTEGRATION.md`'s "Global chrome" section.

**The rule: for header/nav/footer specifically — global chrome, not page content — always check
`connections.json` for a real match FIRST, before treating a user-supplied live reference as the
primary source.** A live reference is the right tool when nothing coded exists for that element;
it's the wrong tool when something coded already does, because re-deriving from a rendered page
means re-guessing content and structure a real source already has exact — and, confirmed here,
getting it subtly wrong more than once before someone thinks to check the registry. This rule
previously lived only as a sub-section inside `CLAY-INTEGRATION.md`, discoverable only by someone
who happened to open that specific section — promoted here for the same visibility as every
other Hard Rule, since a sub-section note evidently wasn't enough to prevent this exact miss from
recurring within the same build it was first found in. **H28 is the same lookup for every
section**, not only chrome: a Clay-Web instance or Clay component name must resolve to coded
Clay before any live-site or pixel rebuild.

**Figma-source chrome branch (the source is the Figma file itself, not a live reference).** When
the Figma file *contains* the real nav/footer node — as opposed to a Reference-Site build where
you only have a live URL — and `connections.json` has no coded match, build the chrome as **pure
real-DOM straight from that node**: every link label verbatim, every brand mark a real exported
vector (H33), and **never a screenshot of the chrome** (H1 — chrome text is dev-handoff-critical
and must be selectable/linkable). The many small marks in a real footer (product-entity icons,
social icons, app-store badges, compliance badges) are exactly the many-logo case where the
design-context `const img… = '…svg|png'` asset URLs are the complete, cheapest source
(`FIGMA-EXTRACTION.md`). Confirmed on the IT persona page: a full 6-column footer + nav built this
way from nodes `1246:55705` / `1246:55388`, 34 real assets, zero recreation. **Precedence:**
coded match in `connections.json` first (the rule above) → else the real Figma chrome node →
else reverse-engineer a live reference. A live reference is the *last* resort for chrome, not the
first.

**Handoff gaps to always flag on a static chrome/page build** (don't silently ship them — list
them in the QA report's Accepted Gaps, per `QA-SCORECARD.md`): (a) nav/footer/FAQ links left as
placeholder `#` — emit a `TODO-links` note for dev rather than inventing URLs; (b) any web font
loaded from a public CDN (e.g. Google Fonts) instead of the design system's self-hosted font
token — fine for preview, call out the production swap; (c) any rasterized composite export
(H9) standing in for what would be live DOM in production.

## H26 — Resuming after a context summary/compaction is not a fresh state — re-confirm every section's Clay anchor before writing any HTML/CSS

**Owner:** n-a

Confirmed real case: a full-page build ran `CLAY-INTEGRATION.md`'s Phase 1 Resolve for all 14
sections of a page, produced a real anchor set (EXACT/CLOSEST/BORROWED/ATOMS_ONLY per section),
and posted a summary of that resolution mid-session. A context compaction occurred shortly after.
On resume, the conversation contained only a system-generated summary whose "Optional Next Step"
line read "call `get_design_context` on the first batch of sections... before writing HTML." The
agent followed that literally: called `get_design_context` on every section, downloaded assets,
and hand-wrote custom HTML/CSS/JS for all 14 sections from scratch — skipping `CLAY-
INTEGRATION.md`'s Phase 2 Build (render the real matched Clay component, extract its DOM +
computed CSS, swap only the sub-elements that don't match Figma) entirely, for every section,
despite Phase 1 anchors already existing earlier in the *same* session. The already-completed
resolution work was never re-surfaced or used — not because the rule requiring it was missing
(`SECTION-WORKFLOW.md` Turn 2 already says "before writing any HTML/CSS, run `CLAY-
INTEGRATION.md`'s resolution process"), but because a compacted summary's own "next step" note
was treated as the authoritative process to follow instead of the skill's reference files
themselves.

**The rule: a system-generated conversation summary is a memory aid, never a substitute for the
skill's own process.** Specifically, before writing any section's HTML/CSS in a build where a
context summary/compaction has occurred since Phase 1 Resolve last ran:

1. **Explicitly re-state the Phase 1 anchor (type + component name) for every remaining section**
   in the current turn's own output — not by trusting the summary's characterization of what was
   already resolved, but by confirming the anchor is genuinely in hand. If the summary didn't
   preserve the actual anchor set (only a narrative description that resolution "was done"),
   treat Phase 1 as **not yet run** for those sections and re-run it from `connections.json`
   rather than proceeding on the assumption that prior work is still valid.
2. **Never let a summary's "next step" bullet replace Turn 2's actual build sequence.** A
   compacted summary is written to help a human (or a future turn) remember *what happened* — it
   is not itself `SECTION-WORKFLOW.md`, and its own suggested next action is not a substitute for
   re-reading (or already knowing) what Turn 2 actually requires.
3. Same principle as H25's own promotion into this file: narrative caution alone did not prevent
   this from recurring across a compaction boundary the first time it was tried — this needs to
   be a rule checked before every section's build step in a resumed session, not a hope that the
   next resume "remembers" to check Clay first.

## H27 — Every page uses the PAGE-STRUCTURE.md skeleton

**Owner:** script

The page file is not a flat list of `<section>` tags in `<body>`. Every page this skill writes
uses the markup tree in `PAGE-STRUCTURE.md`:

```
.page-wrapper > header + main.main-wrapper + footer
main.main-wrapper > section[data-section] > .padding-global > .container-large > .padding-section-large
```

Unique content goes only in `.padding-section-large`. Header and footer sit beside `main`, not
inside it, and are not wrapped in that three-div nest (`data-chrome="header"` / `"footer"`).
Class names are fixed; `max-width` and side padding on `.container-large` / `.padding-global`
are the page's one H22 pair, written once in the shell, not per section.

`tools/qa_gate.py` checks the shell on every page run and the three-div nest on every content
section. A missing wrapper, a section whose unique content sits directly in `<section>`, or a
sentinel still parked before `</body>` is a hard fail — not a style preference.

## H28 — A Clay-Web library instance (or matching Clay component name) must resolve to coded Clay

**Owner:** pre-build

Clay's Figma library is **Clay Web**, file key `LyYrDV2oALKuPoePY9aeJJ`
(`https://www.figma.com/design/LyYrDV2oALKuPoePY9aeJJ/Clay-Web`). The published section
components live on that file (including the catalog around node `888:1951`). The coded map is
`packages/react/src/figma/connections.json` (`figmaFile` is this same key).

**The miss this closes:** Phase 1 used to wait for a slash in the *instance's own name*
(`Section/Header/Split/Default`). A product-file instance can still be a live Clay-Web
component while the layer is named `Hero` or `Frame 12`. Shape-guessing then rebuilds from
pixels and skips the coded component the instance already points at.

**Before writing any HTML/CSS for a section, this lookup is mandatory** (not optional, not
"if the name looks Clay-ish"):

1. Read `get_metadata` on the section. If the node or any descendant is an **INSTANCE** whose
   main component / component-set comes from file `LyYrDV2oALKuPoePY9aeJJ`, treat that as a
   Clay-Web hit. Match on `figmaComponentSetId` or `figmaComponentSetName` in
   `connections.json` — **never** on `figmaNodeId` (those ids are Clay Web's own demo frames
   and will not match a product file). See `CLAY-INTEGRATION.md` Phase 1.
2. If there is no instance link, still look up the frame name, any `/`-path descendant, and
   obvious Clay names (`Header`, `HeaderSection`, `Footer`, `Features/…`) against
   `figmaComponentSetName`, `figmaFrameName`, and family/variant in `connections.json`.
3. **Hit** → that coded component is the Phase 2 starting point. **Call `renderSection()` first**
   to get static `{ html, css }` — do not read `.tsx`/`.module.css` into the page. Fall back to
   Storybook/Chromatic rendered DOM only when `renderSection` doesn't cover the component. Figma
   still wins on copy, images, and every override (the governing principle). Do **not** ask the
   user which Clay component to use — the instance already said.
4. **Hit but Figma-only / not in `connections[]`** → closest coded variant in the same family
   (`CLOSEST`). Do not fall through to `ATOMS_ONLY` or a from-scratch pixel build.
5. **No Clay-Web instance and no name match** → continue the rest of Phase 1 (fingerprints,
   borrowed, atoms). H28 does not invent a Clay section that isn't there.

H25 (header/nav/footer vs a live-site URL) is this same rule for chrome. H28 is the
section-wide version: **library instance or Clay name → coded Clay first.**

## H29 — A downloaded asset is not verified until its pixels are

**Owner:** script

`img.complete && naturalWidth > 0` proves the file *decoded*. It does not prove the file contains
anything. A `get_design_context` asset URL can return a correctly-dimensioned, correctly-named,
non-zero-byte PNG that is **100% transparent**.

**The real case this closes (AI Template Center, security & compliance):** four certification
badges were downloaded from the design-context asset URLs at plausible sizes — 720×465, 802×802,
866×650, 600×600. Three of the four were fully transparent. They passed `img_loaded`, passed
`image_aspect_ratio`, passed `image_resolution_quality`, and the whole page passed the mechanized
gate with **0 hard failures**. The section rendered with one visible badge and three blank gaps.
Only a real look at the section caught it.

**Therefore, immediately after downloading any raster asset, assert it has visible pixels:**

```python
im = Image.open(path).convert("RGBA")
assert im.getbbox() is not None, f"{path} is fully transparent — re-export"
```

`Image.getbbox()` returns `None` for a fully-transparent image. Also treat a single-flat-colour
result (all pixels identical, pure white or pure black) as empty.

**When an asset comes back empty, do not hand-draw a substitute.** Re-export the *individual leaf
node* with `get_screenshot(nodeId=<the image node's own id>, contentsOnly=true)`. In the real case
the parent section's asset URLs were empty but per-node renders of `1:21399`–`1:21402` were
correct. Get the leaf node ids from `get_metadata` on the section first.

**Related tool limit:** `get_screenshot`'s `maxDimension` **caps** the longer edge, it never
magnifies — a 24px node returns a 24px PNG no matter what you pass. For anything that needs to be
crisp above its Figma size, use the `get_design_context` asset URLs instead: those return the
source-resolution originals (a 18px-rendered Slack logo came back as a 2048×2048 PNG).

## H30 — Never substitute a Unicode glyph or emoji for a real Figma icon

**Owner:** script

A stand-in glyph — `✣`, `M`, `✓`, `★`, `→`, `⌄` — renders as *something*. That is exactly why it
is dangerous: it trips no broken-image check, no alt check, no contrast check, no aspect-ratio
check, and at 24px it is invisible in a scaled-down full-page vision capture.

**The real case this closes (AI Template Center):** every agent, workflow, and skill card shipped
`<span class="app-dot">✣</span><span class="app-dot">M</span><span class="app-dot">✓</span>` where
Figma had a real `Apps` component — three 24px chips holding the Slack, Gmail, and monday.com
logos — plus `★` where Figma had a real rating-star SVG. This survived **three mechanized rebuild
rounds ending in a clean 0-failure gate and a full-page vision pass**. The user caught it by
zooming into a single card.

**Rules:**
1. If a Figma node is an `INSTANCE`, `VECTOR`, image fill, or anything named like an icon/logo,
   it resolves to an exported `<img>`/`<svg>` — never to a text character, ever, not even
   temporarily.
2. A glyph is only legitimate when Figma's own layer is a **TEXT node containing that character**
   (the `✍️` skill-card icon in this build is genuinely a Figma text node — that one is correct).
   Confirm from `get_metadata`, don't assume.
3. Composite icons arrive as N separate part-images with Tailwind `inset-[t_r_b_l]` percentages,
   not as one file (the four-colour plus icon here was 8 PNG parts). **Recomposite them at scale
   from those exact percentages** — never eyeball a replacement, and never flatten to a glyph
   because reassembly looks tedious.
4. Size the exported file to the *rendered* box ratio so H10/`image_aspect_ratio` passes — the
   Gmail logo displays at 14.1×10.58 (4:3), so it is exported 60×45, not at its source 57×43.
5. Do the icon-level vision check at **card zoom, not page zoom** (see `ACCURACY-GATE.md`).

## H31 — A static Figma frame carrying a motion/interaction tell resolves to motion, never a from-scratch static build

**Owner:** pre-build

Figma exports one frozen frame. A signature baked into that frame is frequently the *only*
evidence that the real component moves or reacts, and building the frozen frame verbatim ships a
dead version of a live thing that then passes every visual gate — it looks like the design,
because it *is* one frame of the design.

**The tells, each a positive detection — not a style to reproduce:**
- **Wide text clipped at / overflowing its frame edge** (a headline cut mid-word, a line wider
  than its container that doesn't wrap) → a **marquee / scrolling ticker**. Mechanized:
  `section_spec.py textsize` reports `clipped`/`marquee_tell` when a band's ink reaches both box
  edges.
- **A horizontal strip of peer cards with one emphasized** (larger, filled, lifted, focused) →
  a **carousel or hover-expand**.
- **Duplicated or frame-sliced repeating items** (the same card/logo twice, an item cut by the
  frame boundary) → a **looping track** duplicated for a seamless wrap.

Confirmed real case: a persona page's agents headline shipped as a static, edge-clipped centered
line and was corrected to a horizontal marquee only after the user pointed at the live reference
— the edge-clip had been rationalized (and even written into project memory) as a deliberate
static style.

**The rule: when a section's frame carries one of these signatures, the default hypothesis is
motion.** Halt and run `ASK-DONT-GUESS.md`'s question to confirm the interaction model before
writing any HTML/CSS. Do not rationalize the signature away to keep a static build moving — the
burden is on positive evidence to conclude "genuinely static," never the reverse. A tell does not
by itself specify the trigger, direction, timing, or mechanism — those stay unspecified and still
require the question — it only forbids silently shipping the frozen frame as if it were the whole
design. `PRE-BUILD-VERIFICATION.md` item 21 is the checklist form of this rule; `ASK-DONT-GUESS.md`
is the interactivity-side counterpart. This is the motion analogue of H1 (a Figma screenshot is a
QA reference, not content) and H9 (a composite is flattened, not hand-rebuilt): before treating a
visually static-looking section as a flat build, rule out that its frozen frame is hiding motion.

## H32 — A full-page build persists after every section; never build in one large turn

**Owner:** n-a

Confirmed real case (IT persona page, 15 sections / 11,540px): two consecutive attempts died
mid-build with **"API Error: Connection closed mid-response"** — a streaming/transport drop, not
a logic error. The first attempt had completed discovery and written notes before dropping; the
second dropped within a few turns. Both had attempted too much in a single long streamed session
(large metadata pulls + long reads + many sections + tracing). The scratch state that was only
held in the conversation — not written to disk — was lost each time.

**The rule: build one section at a time and write the accumulating page HTML *and* the decision
trace to disk immediately after each section completes.** Never hold more than one section's worth
of unwritten work. Keep every model turn small — per-section `get_design_context` / screenshot /
export, never a full-frame extraction (this is also H3). A file on disk survives a drop; anything
still only in the conversation does not.

Why this matters beyond one bot: long builds *will* be interrupted — by an infra drop, a context
compaction (H26), a turn/time ceiling, or a human pausing. A build that checkpoints to disk after
each section resumes from the last completed section at a cost of at most one section; a build
that doesn't restarts from zero. This is stated **tool-agnostically on purpose** — "persist to
disk" means the project's own working directory / deliverables folder, wherever that resolves for
the operator; it is not tied to any one bot's output convention. The recovery signal ("continue")
is likewise operator-specific and out of scope for this rule — the rule is only that the on-disk
state must always be complete enough to resume from.

## H33 — Never recreate a logo — use the real vector or stop and ask

**Owner:** pre-build

A logo is the one asset a build must never redraw, retype, trace, AI-generate, or hand-rebuild in
DOM/SVG/CSS. A hand-made approximation of a wordmark or brand mark is always subtly wrong
(kerning, weight, glyph shape, color) and reads as broken to anyone who knows the brand — and it
passes every automated gate, exactly like the H30 glyph-substitution failure it generalizes. Use
the real vector, or don't place the logo at all.

**Fixed source order:**
1. **monday / monday-product marks → the Clay DS logo library in the repo** (`clay-design-system/
   New logos/…`, e.g. `Monday.com/` and `Work management/`). Filenames encode the variant
   (Master / Box / Avatar / Com-Large × Primary / Black / White × on- / off-brand) — pick the
   correctly-colored SVG rather than recoloring one by hand.
2. **Any other logo (third-party / integration / customer)** → export the *real* node as SVG from
   Figma (`download_assets` `format:"svg"`, or the design-context `const img… = '…svg'` asset URL
   — see `FIGMA-EXTRACTION.md`). The many-logo case (customer strips, footers) is exactly where
   the design-context asset URLs are the fastest complete source.
3. **No real asset exists anywhere** → **STOP and ask** (`ASK-DONT-GUESS.md`). Never invent a
   placeholder, never approximate.

Confirmed real case (IT persona page): the "customer zero" mark, both monday.com header/footer
logos, and 32 footer brand/product icons were all sourced as real vectors this way (Clay repo for
the monday marks, Figma asset-URL export for the rest) — zero recreation, and it was cheaper than
any rebuild would have been. **This rule is shared with the resize skill** (where the master's own
logo node is already real — clone + scale it; only pull from the library / Figma when a logo is
missing or a different color/theme variant is needed) and should be cross-referenced anywhere a
skill places a brand mark (export, resize, Webflow).

# Gotchas — Tool and Environment Bugs Already Diagnosed

## Contents
- Extracted live-site HTML depends on an external CSS bundle that doesn't exist on the target platform
- CTA arrow SVGs: never apply `fill` on a stroke-only icon
- Card sizing: never derive card width from viewport percentage when Figma specifies absolute px
- `section_spec.py textsize` can false-positive MARQUEE_TELL on wrapping text
- Section height mismatches from default padding-section-large
- Shell state may not persist between tool calls
- Not every Figma MCP connection exposes the same tools
- Node/npx version drift
- The @layer precedence footgun
- CSS-comment `*/` truncation
- Browser screenshot capture going stale
- resize_window not persisting across navigate
- Port Clay variants incrementally, verify tokens exist
- file the downloaded asset before serving
- Known-unsolved: CSS-mask watermark logos
- A coordinate click on a small element may appear not to register — verify via JS before concluding the interaction is broken
- Refactoring a shared JS index/state convention breaks every consumer you didn't also update
- Vision QA against a bare `file://` URL can pass on a page whose images never loaded (but don't let that explanation talk you out of a real bug — verify each element individually)
- A Figma auto-layout flip trick can mirror a node's own reported x/y, not just its children's orientation
- `loading="lazy"` can silently never fire inside a `position: sticky` or transform-animated container
- Figma's flatten export always bakes an opaque background, even when the source node has none
- A static per-item icon/asset baked to match one hardcoded state breaks the moment that state becomes dynamic
- A negative-margin/overlap value tuned for one breakpoint needs its own value at every other breakpoint, not inheritance
- Inline chat-pasted images have no filesystem path — ask for one immediately, don't re-render the same unusable attachment
- A desktop `min-height` on a media element leaks into mobile and stops it shrinking — reset it inside the mobile media query
- A center-emphasis "peek" carousel should use plain CSS opacity/scale classes on Swiper slides, never the Coverflow effect
- Swiper's `loop: true` is unreliable for a few-real-slides + centeredSlides + fractional-slidesPerView carousel — no clone count fixes it; don't use loop mode at all for this shape (includes: a known false-positive explanation can mask a real bug with the identical symptom)
- A reported spacing/cropping defect can be baked into the source raster asset itself — pixel-inspect before writing any CSS fix
- Asset provenance: proximity in the layer tree, an odd opacity, or a derived crop are not proof of what an asset actually is
- Figma desktop-bridge tools (`get_metadata`/`get_design_context`) only resolve nodes on the page/tab currently active in the Figma app
- `flex: 1 1 0%` on a child with no in-flow content silently overrides an explicit `height`
- `align-items: center` on a section wrapping the standard container chain collapses unsized block children to fit-content
- A CSS custom-property fallback (`var(--token, fallback)`) never applies once a global stylesheet already defines that token
- Match a Figma variable to a Clay token by its resolved value, never by label name alone — applies to color/background tokens too, not just type scale
- Non-square icons/logos get distorted by matching fixed width and height on the same element
- `qa_gate.py`'s H6 duplicate-section check could false-positive on a section's own script re-selecting itself (fixed Sep 2026)
- Animating `grid-template-rows: 0fr → 1fr` is a more reliable expand/collapse technique than animating the `flex` shorthand directly
- `resize_window`'s `desktop` preset resets to the pane's own current size, which can be a narrow ~900px, not a real wide desktop viewport
- When both a staging and a production build of the same real reference component exist, prefer production — staging can be mid-deploy or simply broken
- A flex/grid `gap` is measured from the container's own box edge, not from content that escapes it via `overflow: visible`
- `aspect-ratio`-driven sizing tuned for one breakpoint's width can blow up (or collapse) at a breakpoint where the container width is drastically different
- A repeating card/tab slot showing different source images or text per instance needs every variable-height element constrained, not just one
- Figma's fixed per-item px widths need to become percentages inside a non-clipping multi-sibling row that must shrink across breakpoints
- An infinite horizontal marquee needs an `overflow-x`/`overflow-y` split (not one `overflow: hidden`) to avoid clipping text descenders
- A single `elementFromPoint` sample passing doesn't prove a control isn't visually obstructed across its clickable area by an overlapping sibling
- A "these aren't the same size" complaint can be a crop/zoom mismatch, not a box-dimension bug
- An isolated sub-frame's exported pixel dimensions can diverge from its Figma layout-frame's declared width/height when content overflows the frame
- Different device frames for "the same" section in a Figma file can drift out of sync — cross-check both before trusting either
- "You didn't copy it right" after a value-level match usually means a missing whole element, not a wrong value
- Verifying a local reference page needs a real local server, not the sandboxed preview tool
- Vague motion feedback ("smoother / less jarring") has a concrete default fix: scale existing durations ~1.5-1.7x, keep the easing curve
- `flex-wrap: wrap` + `justify-content: center` can look broken when it isn't -- the row's own content just happens to fill the container
- A single DOM order can't satisfy two breakpoints wanting the same wrapped item in different relative positions -- use per-breakpoint CSS `order`, and give every sibling an explicit value
- A reference page can have more than one marquee-style module -- verify the class chain against the actual section, don't assume the first marquee CSS you find is the relevant one
- Count top-level sections against the build todo-list before starting — global chrome falls through the cracks exactly like any other section
- A carousel with an enlarged "active" card by default needs its starting index AND its peek-card size/position verified independently
- Shared code/class does not prove shared behavior — verify every real consuming instance or state before trusting or changing it
- Document intentional content/asset substitutions — including any user-approved asset edit — as an explicit Accepted Gap or code comment
- Zoom into the actual source pixels before reporting a suspected color/tint mismatch
- Live-reference methodology: read the real DOM directly, check your own component system first, and let a specific live page override a general assumption
- A live reference page's unreliability can be transient — retry per request rather than writing it off permanently
- A flattened background image can already bake in an element the HTML also renders on top of it
- `align-items: stretch` only grows a column to match its tallest sibling — it never shrinks, and `min-height: 0` doesn't help once the natural content sum already exceeds the target
- `justify-content` assumptions: verify edge-hugging vs. fixed-gap intent against Figma, and remember `flex-start`/`flex-end` is a no-op without an explicit width under a centered parent
- Flex measurement gotchas: a `box-sizing: border-box` parent can make a child's width look "stuck," and a container-width change invalidates a previously-solved `flex-grow`/padding-floor equation
- Line-wrap verification: a hard `<br>` doesn't guarantee exactly the lines you expect, and a "coincidental" wrap won't repeat for a differently-sized asset
- Reconstructing a completely missing image asset from a flat export
- Solving font-size backward from content width + an observed line-break + character counting, when no live measurement or fresh screenshot is available
- An interactive component with desktop-only navigation needs a working, fully-wired mobile equivalent
- Animation pace ported from a live source must be computed as px/second, and re-derived per breakpoint
- Two "equal" gaps can be coincidentally equal from two entirely unrelated causes
- Swipe/drag/gesture testing and cross-input support
- A CSS rule change has zero effect when JS is setting the same property as an inline style
- A fixed-px dimension taken from a reference with structurally different content is wrong
- Hard `<br>` line breaks in a flex-1 heading work at only one viewport width

Check this file before spending time re-diagnosing a bug that's already been found once.

## Extracted live-site HTML depends on an external CSS bundle that doesn't exist on the target platform

Confirmed real case (PMO page → Marketing page, Aug 2026): sections extracted from a live
monday.com page rendered correctly on that page because they depended on monday.com's own
website CSS bundle (`@layer clay.components` and related external stylesheets). When the same
HTML was dropped into a Generated Page (which doesn't load that bundle), every class name from
the external bundle had no definition — the sections rendered broken (wrong spacing, missing
styles, collapsed layout).

This is distinct from the existing `@layer` precedence gotcha below, which is about *layered vs.
unlayered CSS within a single page*. This gotcha is about **importing HTML whose styles live
entirely outside the page, on a platform that doesn't serve those styles at all.**

**The rule:** when reusing a section from a live site (as opposed to building one fresh from
Figma), the section's CSS must be fully self-contained — every class used in the HTML must have
a corresponding rule in the page's own `<style>` blocks. If the source section's styling comes
from an external bundle, you must either (a) extract and inline the specific rules those classes
need (scoped to avoid conflicts), or (b) rebuild the section as self-contained HTML/CSS from
Figma specs. Option (b) is almost always cheaper — in the confirmed case, copying the literal
PMO HTML and letting its external classes fail took 5+ rounds of patching; rebuilding a fresh
self-contained version from Figma specs worked on the first attempt.

**Detection signal:** a section that renders correctly on its source page but breaks on the
target page, with no console errors (CSS class misses don't throw — they silently produce no
style). Inspect `document.styleSheets` on the target page: if the classes used by the section
don't appear in any sheet, the external-bundle dependency is the cause.

## CTA arrow SVGs: never apply `fill` on a stroke-only icon

Confirmed real case (IT page workflow tabs, Aug 2026): a CTA button's arrow icon was defined
correctly in the SVG (`fill="none"` on the `<svg>`, `stroke="currentColor"` on the `<path>`).
But the CSS rule `.cta svg { fill: currentColor }` overrode the inline `fill="none"` and
filled the arrow path solid — turning a clean outlined arrow `→` into a filled solid
triangle. The SVG markup was correct; the CSS broke it.

**The rule:** CTA/button icon SVGs that use `stroke` for their rendering must have
`fill: none` in CSS (or no `fill` rule at all). Never apply `fill: currentColor` as a
blanket rule on SVGs inside buttons — it works for filled icons but destroys stroke-only
icons. Check the SVG's own `fill`/`stroke` attributes before writing the CSS:
- `<path stroke="currentColor" ...>` → CSS must have `fill: none; stroke: currentColor`
- `<path fill="currentColor" ...>` → CSS can have `fill: currentColor`
- When both exist on different paths → don't set `fill` on the parent `svg` at all; let each
  path's own attributes control it.

## Card sizing: never derive card width from viewport percentage when Figma specifies absolute px

Confirmed real case (Agent carousel, Aug 2026): cards were set to `flex: 0 0 calc(50% - 12px)`
to show 2 cards per view — producing 628px cards. But Figma specifies each card at exactly
730px (wider than half viewport). The `50%` assumption made the cards too narrow, which
crushed the right-side illustration column from 330px to 230px — making it nearly invisible.

**The rule:** when Figma specifies an absolute card width (e.g. 730px), use that value in
`flex: 0 0 730px`. The carousel container's `overflow: hidden` handles the clipping. Don't
convert to percentages unless the Figma frame uses percentage-based layout (rare for cards).
A carousel with cards wider than half the viewport is a valid design — the overflow/track
translation handles revealing them.

**This is the opposite case from the next entry below — the deciding factor is whether the
row has its own overflow/clip mechanism, not whether Figma's own value happens to be in px.**

## Figma's fixed per-item px widths need to become percentages inside a non-clipping row that shrinks across breakpoints

Confirmed real case (guardrails and why-monday sections, Sep 2026): several two-item rows
(a text card beside a media panel) used Figma's own literal per-item pixel widths directly —
`flex: 0 0 806px` / `flex: 0 0 458px`, etc., only active from a 900px breakpoint up, with no
other override. This looked correct at exactly 1440px (where Figma measured it) and at exactly
900px (where a separate mobile-stacked layout took over), but overflowed the row at every width
in between — the container shrinks continuously from 1440px down to 900px, while a `flex: 0 0`
px value never shrinks at all.

**The rule:** when two or more Figma-specified px widths sit side-by-side in a row governed by
a fluid/max-width container (no `overflow: hidden` track absorbing the excess — contrast with
the carousel-card entry above, which *does* have that overflow mechanism and should stay in
literal px), convert each to a percentage of the row's own content width and add `min-width: 0`
so the flex item can actually shrink below its content size:

```css
/* was: flex: 0 0 806px; / flex: 0 0 458px;  (overflows between 900px and 1440px) */
.media { flex: 1 1 62.97%; min-width: 0; } /* 806 / 1280 content width at full desktop */
.card   { flex: 1 1 35.78%; min-width: 0; } /* 458 / 1280 */
```

Derive the percentage from Figma's own px value divided by the row's content width at the
viewport where Figma measured it (container max-width minus side padding), so the row still
reproduces the exact Figma pixel widths at that viewport and simply scales down proportionally
below it.

## A repeating card/tab slot showing different source images or text per instance needs every variable-height element constrained, not just one

Confirmed real case (agents carousel cards, Sep 2026): a shared card template renders a
different illustration + title + description depending on which agent occupies the slot.
Fixing only the image (`aspect-ratio` + `object-fit: cover` on `.agent-card-illustration`,
instead of `width:100%;height:auto` keyed to each image's own natural pixel size — source
illustrations ranged ~761–765×651–654px, close enough that letting each one drive its own
height still produced a several-px card-height drift as the carousel cycled between agents)
was not enough on its own: titles and descriptions that wrap to a different number of lines per
agent (most titles fit one line; a couple wrap to two — descriptions wrap two or three lines
depending on the agent) still made the card taller or shorter depending on which agent's text
currently occupied that slot, even with the image height now fixed.

**The rule:** when one template/slot is populated by different content per instance
(carousel cards, tab panels, repeated list items), audit *every* variable-height element inside
it, not just the first one you notice — an image, a title, and a description can each
independently cause slot-height drift, and fixing one doesn't fix the others:
- **Images:** a fixed `aspect-ratio` + `object-fit: cover` on the slot, not each image's own
  intrinsic ratio (this is a deliberate, scoped exception to `HARD-RULES.md` H10's general
  "always derive from the image's own intrinsic size" rule — H10 applies per single image; this
  is for one slot shared by several different images).
- **Wrapping text:** reserve a `min-height` computed from `line-height * font-size * max-lines`
  (the most lines any instance's text actually wraps to), not the number of lines the specific
  instance you're looking at happens to need:

```css
.agent-card-title { font-size: 18px; line-height: 1.53; min-height: calc(18px * 1.53 * 2); }
.agent-card-desc { font-size: 14px; line-height: 1.5; min-height: calc(14px * 1.5 * 3); }
```

## `section_spec.py textsize` can false-positive MARQUEE_TELL on wrapping text

Confirmed real case (IT hero section, Aug 2026): `textsize` flagged MARQUEE_TELL because
the heading's ink bands reached both edges of the measurement box. But the heading was a
normal 2-line wrapping headline (48px Poppins, 681px bounding box in a 600px column). Figma
reports the TEXT node's `absoluteBoundingBox` at the *unwrapped* width, which exceeds the
parent column — triggering the edge-detection heuristic.

**When textsize flags MARQUEE_TELL:** cross-check against the Figma node's parent container
width. If `text_node_width > parent_width` but `parent_width` is a normal column (not a
full-bleed banner), the text wraps — it's not a marquee. The real marquee tell is when the
*parent frame itself* is wider than its own parent, not just the text node.

**Related false-positive: comparing rendered pixel widths across two font-rendering engines
(Figma vs. the browser) can show a spurious gap even when nothing is actually wrong.** Read
`get_variable_defs` on the exact node first, before trusting a cross-engine pixel comparison as
evidence of a real mismatch.

## Section height mismatches from default padding-section-large

Confirmed real case (IT page, Aug 2026): the `.padding-section-large` default
(`clamp(4rem,...,6rem)` = ~96px top+bottom) was applied to every section, but many Figma
sections have `padding: [0,0,0,0]`. This added ~192px of phantom height to sections like
unified-platform, feature-grid, testimonials, and video-cta — making the page 12.9% taller
than Figma and sections visually crammed with wrong spacing.

**The rule:** ALWAYS check each Figma section's own `paddingTop/Bottom` from `get_metadata`
(or the node's API response) and override `.padding-section-large` per section. The default
is a fallback, not a universal value — most sections specify their own padding and it
frequently differs from the default. This is a PRE-BUILD-VERIFICATION item: verify padding
before writing CSS, not after QA flags the height delta.

## Shell state may not persist between tool calls

In some harnesses, each shell/bash tool call starts fresh — a `PATH` fix or discovered variable
from one command is gone in the next. If a Node-version-drift fix (below) or a discovered Clay
path only gets applied once "per session," it can silently stop taking effect on the very next
command. **Re-assert the fix in every individual command** that needs it, rather than assuming
it sticks once resolved — confirmed as a real failure mode, not a hypothetical one.

## Not every Figma MCP connection exposes the same tools

Two connections that both call themselves "the Figma MCP" are not guaranteed to have the same
tool surface. A confirmed real case: one connection lacked `download_assets`,
`search_design_system`, `get_libraries`, and `whoami` entirely, and its `get_screenshot`
returned image bytes inline with no curl-able URL — unlike a connection that does support
`download_assets`. **Don't assume a workflow step's exact mechanism (e.g. "download the
screenshot URL with curl") is universal** — if the active connection doesn't support it, fall
back to a secondary Figma connection for the missing capability rather than assuming the step
is broken.

## Node/npx version drift

`npx`'s shebang resolution can silently pick an old Node install (e.g. v16, lacking modern
ESM/`fetch` support) instead of the intended modern version (e.g. v24+), with no obvious error
— commands just fail as if a dependency were broken or missing. This affects any MCP server
launched via bare `npx` in `.mcp.json`, and any script invocation relying on `npx`/`node` in the
shell.

**Fix:** never rely on bare `npx`/`node` for anything that must be reliable. Use the fully
qualified path to the correct Node binary (resolve it once per session, e.g.
`command -v node` after activating the intended version) in `.mcp.json` `command` fields and in
any shell invocation.

## The @layer precedence footgun

Wrapping ported component CSS in `@layer` (matching a source design-system's own authoring
style) without also layering the rest of the page's CSS is a real, silent bug: per the CSS
Cascade Layers spec, **unlayered styles always beat layered styles regardless of specificity or
source order**. A confirmed real case: an unlayered `a { color: inherit }` page reset silently
overrode a layered `color: white` on a primary button, producing invisible black-on-black text
with no console error.

**Fix:** strip any `@layer` wrapper from ported source CSS unless the *entire* page adopts a
matching layer order. For a single hand-authored static page, this is a footgun with no upside.

## CSS-comment `*/` truncation

A CSS comment containing the literal substring `*/` — even accidentally, from adjacent tokens
like `word/*next` or a listing like `(btn/large/regular/style_*/color_*)` — closes the comment
early. Everything after it in that `<style>` block silently fails to parse (0 rules), with no
visible browser error.

**Detection:** if a section/button silently loses all its styling with no obvious cause, check
`document.querySelectorAll('style')[i].sheet.cssRules.length` per `<style>` tag before assuming
a selector-specificity bug — a `0` where you expect real rules is the signature of this bug.

**Fix:** never write `*/` inside a CSS comment, including accidentally via adjacent tokens.
Proofread comments for this exact character pair before shipping.

## Browser screenshot capture going stale

The browser-pane screenshot/scroll tooling can intermittently return blank/stale/all-white
results — sometimes right after a viewport resize combined with an immediate scroll — while the
actual page content is correct and present (confirmed via `document.elementFromPoint()` and
`getBoundingClientRect()` returning sane values). The capture pipeline can desync from actual
page state.

**Fix:** don't trust an all-white or obviously-wrong screenshot at face value — cross-check with
`elementFromPoint`/`getBoundingClientRect`/`naturalWidth` first. If a tab's screenshot capture
is stuck blank/stale for more than one retry, **stop retrying in place and open a fresh tab** —
this was the only fix that reliably worked; repeated retries on the same stuck tab did not
recover it.

**Confirmed variant — a backgrounded/hidden pane produces false-positive rendering bugs beyond
just blank screenshots.** Repeatedly across one long session (Sep 2026), whenever the browser
pane went hidden/backgrounded, `img.complete` reported `false` for images that had genuinely
already loaded, and `getComputedStyle`/`getBoundingClientRect` reads came back stale or
zero-width — not just the screenshot pixels. Each time, this was initially reported as a real
layout/loading bug before tracing it to the pane's visibility state. **Fix:** when any
screenshot, `img.complete`, or computed-style read looks wrong in a way that would be a serious
bug if true, check `tabs_context` for whether the pane is currently backgrounded before
concluding it's real — re-open/re-front the pane (`preview_start`/`tabs_select`) and re-check
before trusting a suspicious result from a possibly-hidden pane.

**Confirmed variant on a very tall page (10,000px+):** repeated `computer{action:"scroll"}`
calls on a single-page build this size produced a `computer timed out after 30s ... Browser pane
is currently hidden` error followed by an all-white screenshot, reproducibly, at multiple
different scroll depths — even after removing `html { scroll-behavior: smooth }` from the page's
own CSS (ruled out as the cause: a plain `window.scrollTo()` via the JS tool reproduced the same
blank capture). In every case, `getComputedStyle()`/`classList` checks on the actual element at
that scroll position confirmed `opacity: 1`, correct `transform`, and real text content — the
page was never actually broken; only the screenshot pipeline was. **What reliably recovered it:
close the affected tab(s), open a fresh tab, `navigate` directly to the URL again (force reload),
then drive scroll position via the JS tool's `window.scrollTo(0, y)` rather than the `computer`
tool's wheel-scroll action** — after that, screenshots at every scroll depth rendered correctly on
the first attempt, including sections with heavy box-shadows/gradients/backdrop-filter that were
initially (wrongly) suspected as the cause. Treat a blank capture on a tall page the same way as
the general case above: verify via DOM first, never conclude the page is broken from the
screenshot alone, and prefer a fresh tab + direct navigation + JS-driven scroll over repeated
wheel-scroll retries on the same tab.

## resize_window not persisting across navigate

Viewport size set via a resize call does not reliably persist across a subsequent navigation.
Re-assert the intended viewport size before every screenshot batch rather than assuming a prior
resize is still in effect.

## Port Clay variants incrementally, verify tokens exist

When hand-porting a design-system component's CSS (e.g. a Button), don't try to front-load every
possible variant combination up front — port variants incrementally as sections actually need
them. Before using any newly-ported variant's token names, `grep` them against the compiled
`tokens.css` to confirm they actually exist in the current repo — don't assume a full variant
matrix without checking; token names and variant coverage both drift between repo versions.

## file the downloaded asset before serving

A downloaded asset's implied file extension (from the response/URL) doesn't always match its
true format — a confirmed real case: an asset implied `.png` by its URL but was actually a JPEG
by content. A plain static file server sets `Content-Type` from the file extension, not the
actual bytes, so a mismatched extension silently serves the wrong MIME type.

**Fix:** run `file <path>` on every downloaded asset before serving it, and rename if the true
format doesn't match the extension.

## Known-unsolved: CSS-mask watermark logos

Some Figma logo assets are CSS-mask-based watermarks (alpha shapes meant to render as solid-
color cutouts). Rendering them as a plain `<img>` with `filter: brightness(0) invert(1)` works
for a wordmark-shaped alpha source but produces a barely-visible sliver for a compact icon-
shaped source — the filter approach doesn't generalize across differently-shaped mask sources.
No general fix found yet; document as a known limitation per-asset rather than assuming the
filter trick always works.

## A coordinate click on a small element may appear not to register — verify via JS

Confirmed real case: a `computer` tool coordinate click on an 8px dot-pagination control looked
like it should have hit the element (coordinates matched the element's real bounding box,
adjusted for the screenshot's scale factor), but the visible result didn't change. Before
concluding the interaction itself is broken, re-trigger it programmatically —
`document.querySelector(...).click()` via the JS tool — and check the resulting DOM state
directly (class list, `aria-*` attributes). In the confirmed case, the JS-triggered click worked
correctly and updated the DOM as expected; the coordinate click was the unreliable part (likely
a small scale/rounding mismatch on a very small hit target), not the underlying feature. Only
treat an interaction as genuinely broken once a direct JS trigger also fails to produce the
expected DOM change.

**The inverse case is also real: a passing `elementFromPoint` check doesn't prove a control is
actually clickable across its whole area.** Confirmed real case (agents carousel arrows, Sep
2026): `document.elementFromPoint()` at the arrow button's sampled coordinate correctly
returned the arrow, yet the user reported across three separate rounds of feedback that the
arrow was hard/impossible to click — a peek card, sized and spaced independently, visually and
functionally overlapped part of the arrow's real clickable area at the specific point the user
was actually clicking, even though one sampled point elsewhere on the button tested clean.
**Fix/detection:** when a click-registration check passes but a user still reports a control as
unclickable, compare the full `getBoundingClientRect()` of the control against every sibling
that can overlap it (especially one sized/positioned by a carousel's own transform or negative
margin), not just a single sampled point — an obstruction can cover part of a control's box
while leaving the rest, including whatever point you happened to test, clear.

## Refactoring a shared JS index/state convention breaks every consumer you didn't also update

Confirmed real case: a carousel's slot array got a leading clone inserted (to make a loop
animation seamless at rest, not just mid-transition), which shifted every real card's index by
+1 — real card *i* now lives at slot *i+1*. The `goTo()`/`center()`/`paint()` functions that
directly used the new offset were updated in the same edit; the dot/tab click handler, which
called those functions but computed its own slot index from a raw dataset value, was not — it
kept passing the old (unshifted) index straight through. Result: every dot and tab click landed
on the wrong card, silently, until the next round of testing caught it.

**The lesson: when changing a data structure's shape or indexing convention (adding/removing an
array element, shifting an offset, renaming what index 0 means), grep for every place that reads
or writes an index into that structure in the same pass — not just the function you're actively
editing.** A structural change to shared state is not "done" when the function you touched still
works in isolation; it's done when every consumer of the old convention has been checked.

## Vision QA against a bare `file://` URL can pass on a page whose images never loaded

A confirmed real case: opening a built section directly via a `file://` URL in the browser pane
rendered the page (headings, layout, text all correct via `get_page_text`), but every `<img>`
inside it silently failed to load — `read_network_requests` showed zero recorded requests for
the image paths, indicating this render mode has no real network layer for local relative-path
assets. A screenshot taken in this state can look plausible (or come back blank/stale, see the
gotcha above) without revealing that no image ever actually loaded.

**Fix — make this the default starting point, not a fallback discovered per section.** Several
sections across more than one build independently re-discovered this same `file://` failure the
hard way, each after it had already been written down from an earlier section — the lesson
existing in this file didn't stop it recurring because `file://` was still the *first* thing
tried each time. **Serve every section's vision QA over a real local HTTP server from the very
first attempt** (`python3 -m http.server <port>` from the output directory,
`http://localhost:<port>/...` in the browser pane) — never open a bare `file://` path at all for
any section with local image assets, not even as a quick first look. Confirm images loaded via JS
(`img.complete && img.naturalWidth > 0`) before trusting a screenshot as a real QA pass, not just
a DOM/text check.

**Recurred again (Sep 2026) — this time via an ad-hoc "check it in the browser" request outside
the formal per-section QA loop**, where the standing rule apparently wasn't top-of-mind because
the check wasn't part of the usual build-and-QA sequence. Treat this as true for **every** browser
tool call that touches the output directory, not only the main section-build loop's own QA
step — an ad-hoc spot check, a change-request verification, or a user-requested "look at this in
a browser" all carry the same risk. `SKILL.md` now carries a one-line pointer to this entry in
its core workflow for exactly this reason: a rule that lives only in this reference file has
already failed to stop the recurrence twice from being buried here alone.

**Caution — don't over-apply this as an excuse to dismiss a real report.** A confirmed real case
initially misread a genuine centering bug as "just a broken `file://` capture": a card's logo was
reported as left-aligned instead of centered; the `file://` preview had indeed failed to load the
SVG (`naturalWidth: 0`), which looked like the explanation. But re-serving over
`http://localhost` and measuring `getBoundingClientRect()` on the *wrapper div* (not the image
itself) showed the wrapper centered — leading to a wrong "no bug" conclusion, reported back to
the user, who correctly pushed back a second time. The actual bug (a global
`img { display: block }` reset silently breaking inherited `text-align: center` for that one
image — see `HARD-RULES.md` H24) only surfaced once every element was measured *individually*,
not just the wrapper. **The `file://` asset-loading gotcha is real and worth ruling out first,
but ruling it out is not the same as proving the design is correct — always follow up with a
per-element measurement (not just the outermost wrapper) over a real HTTP-served render before
telling the user a reported mismatch isn't real.**

## A Figma auto-layout flip trick can mirror a node's own reported x/y, not just its children's orientation

Figma designers sometimes apply `scaleY(-100%)` + `rotate(180deg)` together on an auto-layout's
children to make it grow upward while the content stays upright (the two transforms cancel for
orientation). A confirmed real case: `get_metadata` reported a floating overlay node's `x` as a
value that, combined with its own `width`, placed its right edge ~500px past its parent frame's
right edge — geometrically impossible for a node that renders fully on-canvas in `get_screenshot`.
The node's children used the scaleY+rotate trick; the width/height in metadata matched a
pixel-measured render exactly, but the x-anchor did not — the trick (or a related transform on
this node's own box) mirrored the reported anchor, not just the children's orientation.

**Fix:** if a node's metadata width/height match a real screenshot but the reported x/y implies
an impossible position (off-frame, overlapping siblings that visually don't overlap, etc.),
don't trust the raw x/y. Export the parent via `download_assets`, measure the node's real
position directly off the pixel data (e.g. a Python/PIL script scanning for the node's edge
discontinuities along a horizontal/vertical line), and build from that instead. Width/height
matching while only the anchor is wrong is itself a signal that this transform trick (or a
sibling variant of it) is in play, not that the export is wholly unreliable.

## `loading="lazy"` can silently never fire inside a `position: sticky` or transform-animated container

Confirmed real case: a page had a sticky-stacked card group (`position: sticky` cards covering
each other on scroll), a `position: sticky` media panel, and a horizontally-animated marquee row
— every `<img>` inside those three containers had `loading="lazy"` and never loaded, even after
scrolling the real page and waiting several seconds. This is a step beyond the `file://`
image-loading gotcha above: these images were served over a real local HTTP server (confirmed via
`curl` returning 200 with the correct `Content-Length`, and a manually-constructed `new Image()`
with the same `src` loading instantly) — the resource was always fetchable, but the specific
`<img>` element in the DOM never decoded. The browser's native lazy-load intersection check
appears not to fire reliably for images whose ancestor is sticky-positioned or moved into view via
CSS transform/animation rather than normal document flow — the element's static layout position
can differ from where it visually ends up, and native lazy-loading intersects against layout
position.

**Detection:** after scrolling and waiting, check `img.naturalWidth === 0` per element — don't
stop at "the page scrolled and I waited a few seconds," since this failure mode doesn't resolve
with more waiting. Cross-reference which broken images share `loading="lazy"` and a sticky/
animated ancestor; that combination is the signature.

**Fix:** don't use `loading="lazy"` on any image inside a `position: sticky` container or one
whose visible position depends on a CSS animation/transform rather than plain document flow. For
a single static marketing page, the safest default is to drop `loading="lazy"` from every image
in the sticky/animated regions we build with this skill's own techniques (sticky-stacked cards,
sticky media panels, marquee rows) — the reliability cost of a broken image outweighs the minor
lazy-load performance gain on that fraction of the page.

**A third trigger, distinct from sticky/transform: a `display: none` hidden tab/accordion/
carousel panel.** Confirmed real case (Sep 2026): images inside inactive tab panels (hidden via
`display: none` until clicked) never loaded under `loading="lazy"`, and never resolved no matter
how long a static crawl waited — a hidden element has no layout box at all, so it can never
intersect the viewport for the native lazy-load check to fire, even after the panel becomes
visible later via a class toggle rather than a fresh navigation. One tab in the same build had
already been shipped with `loading="eager"` as a one-off fix; the same fix wasn't carried to its
sibling tabs added afterward, so the same class of finding kept resurfacing. **Fix:** any
`<img>` inside a tab, accordion, or carousel panel that can be `display: none`/inactive at
initial page load must use `loading="eager"` — apply this to every sibling panel of the same
component consistently, not just the one that got flagged first.

## Figma's flatten export always bakes an opaque background, even when the source node has none

Confirmed real case twice in one session: a Figma group with no background fill on any layer
(confirmed via `get_metadata` — only lines, small chip frames, and images, no full-size rect) was
exported via `download_assets`/`get_screenshot` as PNG, and the resulting file had alpha=255
(fully opaque) at every corner, including a fresh re-export at a different scale. The flatten-
export pipeline composites transparent regions onto white/canvas color regardless of the source
node's actual fill — this is not a one-off cache issue, it reproduces every time for a node meant
to be transparent.

**Detection:** before trusting a flattened export's transparency, open it and check a corner
pixel's alpha channel (e.g. PIL `im.convert('RGBA').getpixel((0,0))`) — `255` where the source
node has no background fill confirms the flatten-bakes-white behavior, not a real design choice.

**Fix, in order of preference — see also `PRE-BUILD-VERIFICATION.md` item 19, which documents the
same defect for the ancestor-fill case and is the more rigorous version of this rule:**
1. **Ask the user to export it themselves from Figma** with the correct transparency settings —
   the Figma app's own manual export (not the MCP flatten pipeline) can produce a genuinely
   transparent PNG where the API-driven export cannot. This was the fix that actually worked in
   the confirmed case — the user supplied a properly-exported transparent PNG directly.
2. If no manual export is available, rebuild the composite from its individual layers
   (`get_design_context` on the group returns each child image/SVG with real transparency) and
   position them with CSS instead of using one flattened image. More work, but doesn't depend on
   the user re-exporting.
3. **Do not flood-fill the baked-white region to transparent as a *default* fix** — per item 19,
   this doesn't work in general: real UI art usually contains its own white/near-white elements
   (cards, bubbles, input fields) that are edge-connected to the baked margin with no boundary in
   between, so a border-connected flood-fill either stops short of the true background or eats
   part of the art. Whether it's safe is a property of the specific asset's own colors, not
   something to assume either way without checking.
   **Refined (marketing-page showcase collage, Sep 2026, 26 isolated-node exports): a
   border-connected flood-fill from the image's own edges (walk inward from all 4 borders,
   converting only *connected* near-exact-match pixels to alpha, stopping at any non-matching
   boundary) DID work correctly and safely across all 26 assets in this batch** — including one
   whose real card interior is itself near-black (`rgb(26,26,26)`, not pure `rgb(0,0,0)`) and one
   whose real card interior IS legitimately pure black edge-to-edge (a "Create new asset" popup)
   — because in both cases the baked padding was *exactly* the page's own canvas color
   (`rgb(0,0,0)` to the pixel) while the real content's own colors were either off by a few
   values (safe: not "near-exact-match" under a tight tolerance like ±6) or, for the genuinely
   pure-black card, not actually touching the image's 4 edges (a thin gap existed even there). The
   two failure modes item 19/this entry warn about (stopping short, or eating real content) are
   real risks, not universal - so **treat border-connected flood-fill as a candidate fix, not a
   banned technique, gated on verification**: (a) use a tight color-match tolerance (e.g. ±6, not
   a loose "roughly black/white" threshold), (b) render the result composited onto a
   *high-contrast* temporary background (bright green works well) and visually confirm no real
   content was eaten and no residual padding remains, for a representative sample of the batch —
   not just one asset — before trusting it across all of them. When that check fails on even one
   asset in the batch, fall back to option 1 or 2 instead of forcing the technique through.

## A static per-item icon/asset baked to match one hardcoded state breaks the moment that state becomes dynamic

Confirmed real case: an accordion had one item marked `open` by default in the static markup.
Rather than one shared chevron icon rotated by CSS based on an `.open` class, the *open* item's
markup used a different, separately-authored SVG path (pointing up) than the two closed items
(pointing down) — because at authoring time only that one item was ever open, so nobody wrote a
rotation rule; the "correct" arrow direction was simply baked into which SVG got used. The bug was
invisible until a later change (adding hover-to-open) made a *different* item open dynamically —
whichever item became open kept its own static arrow direction instead of flipping, so the visual
open/closed state and the arrow direction went out of sync.

**Fix:** whenever a component has more than one visual difference tied to open/closed (or any
other) state — icon direction, color, text — drive *all* of them from the same state class with
CSS, using one shared asset. Never let "this happens to be the only state we render right now"
justify hardcoding a per-instance asset variant; check for this pattern specifically before
wiring up any interaction (hover, click-to-toggle) that can change which instance holds a given
state, since that's exactly when a baked-per-instance asset surfaces as a bug.

## A negative-margin/overlap value tuned for one breakpoint needs its own value at every other breakpoint, not inheritance

Confirmed real case, twice in one session, same shape both times: a section used a negative
`margin-top` to intentionally float over the section above it (e.g. cards overlapping a color
boundary, a composite image overlapping the section above). The overlap amount was tuned
correctly for desktop. At a narrower breakpoint, either (a) no override existed at all, so the
same desktop-tuned negative margin applied against different, smaller padding — pulling the
floating element up *more* than the available space, causing content to touch or overlap with
zero gap — or (b) an override existed but its magnitude exactly canceled the other section's
padding at that breakpoint (e.g. both were 60px), again leaving zero effective gap that then broke
further whenever the covered content's height varied (like an accordion item open at different
heights).

**Fix:** any CSS rule using a negative margin/overlap for a deliberate floating effect must be
re-checked at *every* breakpoint that changes the padding/spacing of either the floating element
or the section it overlaps — don't assume a value that looked fine on desktop carries over, and
don't assume one breakpoint's override is enough if there's more than one narrower breakpoint in
play. When in doubt on mobile, prefer removing the overlap effect entirely (small positive gap
instead of a tuned negative one) over trying to get the negative-margin math exactly right against
variable-height content.

**When working from a live reference, measure at the real mobile viewport, not a desktop-guessed
one** — and every changed base-CSS rule needs an explicit override that preserves the existing
desktop value; this is the same "no inheritance across breakpoints" principle as above, applied
to measurement methodology rather than just the CSS values themselves.

## Inline chat-pasted images have no filesystem path — ask for one immediately, don't re-render the same unusable attachment

Confirmed real case: a user pasted a replacement image directly into chat (not as a file
reference) and asked for it to be swapped into the page. There is no way to read pixel data from
an inline chat attachment — it can be seen in context but not opened via `Read`/`Bash`, and no
amount of the user re-sending or re-describing the same attachment changes that. The first
response correctly identified this and asked for a path, but the user then re-pasted the same
image inline twice more across follow-up turns before finally saving it to an explicit path.

**Fix:** the moment an image arrives with no accompanying path/URL, say the concrete limitation
plainly in the very first response — "I can see this image but can't read or write it directly;
save it to a path (e.g. drag it into the project folder, or tell me a Downloads/Desktop path) or
give me a URL" — and stop there rather than proceeding on a guess or waiting for the user to
re-paste. Once a real path is given, verify the file actually exists and inspect its real
properties (size, mode, a corner-pixel alpha check per the flatten-export gotcha above) before
using it — don't assume a filename like `Group 123.png` matches what was described without
opening it.

## A desktop `min-height` on a media element leaks into mobile and stops it shrinking

Confirmed real case (persona mini-sites, features-media block): a media panel carried a
`min-height` set for wide viewports (to hold a fixed vertical size on desktop), and no mobile
override reset it. At mobile width the element couldn't shrink below that desktop floor, so it
either forced vertical overflow or pushed the section far taller than the Figma mobile frame
intended. The default `min-height: auto` on a flex child compounds this — a flex item won't
shrink below its own content/min-height floor either. The whole failure is **invisible on
desktop by construction**: at the width the value was tuned for, it looks correct.

**Detection:** if a section is right on desktop but too tall (or scrolls vertically) on mobile,
grep every `min-height` that's set outside a mobile media query and check for a matching reset
*inside* the mobile query. A desktop-scoped `min-height` with no mobile counterpart is the
signature.

**Fix:** add `min-height: 0` (or a mobile-appropriate value) to the element inside the mobile
media query — the confirmed fix here was `min-height: 0` on the features-media element. This is
the vertical-sizing counterpart of the negative-margin-per-breakpoint gotcha above: a sizing
value tuned for one breakpoint needs its own value (or an explicit reset) at every other
breakpoint, never inheritance.

## A center-emphasis "peek" carousel should use plain CSS opacity/scale classes on Swiper slides, never the Coverflow effect

Confirmed real case (marketing persona mini-site, agents carousel, Aug–Sep 2026): a 3-card
"peek" carousel — center card full-size and opaque, left/right neighbors partially visible,
smaller, and dimmed — was first hand-built with `.agent-card.is-left/.is-center/.is-right`
absolute-positioned percentage boxes, then migrated to Swiper.js with `effect: 'coverflow'`
driving the size/depth delta between active and peeking cards. The coverflow build worked at
first, but after enough prev/next clicks its 3D depth calculation desynced from Swiper's own
"active slide" bookkeeping — see the loop-mode entry below for how this compounded with a
second, deeper bug in the same carousel.

**The rule:** for this pattern — one emphasized centered slide with partial neighbors peeking
on both sides — do not use `effect: 'coverflow'` at all, even with its tilt/depth params
zeroed out. Use Swiper only for slide mechanics (touch/drag, `slidesPerView`, `spaceBetween`),
and drive the entire active/inactive visual delta with plain CSS classes keyed to Swiper's own
slide-position classes:

```css
.agent-card { opacity: 0; transition: opacity .35s cubic-bezier(.4,0,.2,1), transform .35s cubic-bezier(.4,0,.2,1); }
.swiper-slide-prev .agent-card, .swiper-slide-next .agent-card { opacity: .6; transform: scale(.93); }
.swiper-slide-active .agent-card { opacity: 1; transform: scale(1); }
```

```js
new Swiper(el, {
  grabCursor: true, centeredSlides: true, slidesPerView: 1.15, spaceBetween: -40,
  breakpoints: { 900: { slidesPerView: 2.3, spaceBetween: -40 } },
});
```

Wire external arrow buttons to `swiper.slidePrev()/slideNext()`, and external dots per the loop
entry directly below — this carousel's small, fixed slide count means loop mode is never the
right call, so the dot-click logic there is not the usual `slideTo(i)`.

**Half-finished-migration trap:** converting the *markup* to `swiper`/`swiper-wrapper`/
`swiper-slide` classes without also (a) loading the actual Swiper CSS/JS files and (b) calling
`new Swiper(...)` leaves the old hand-rolled CSS/JS silently still driving the visuals — the
section looks unchanged, so it's easy to believe the migration finished when only the HTML
shape changed. Grep for `new Swiper` and the vendor `<link>`/`<script>` tags before considering
a Swiper conversion done, not just the slide markup.

## Swiper's `loop: true` is unreliable for a few-real-slides + centeredSlides + fractional-slidesPerView carousel — no clone count fixes it

**This entry was revised in Sep 2026 after its own original fix shipped and turned out to be
wrong — read the whole thing, not just the final rule, since the earlier "confirmed fix" below
is exactly the kind of dead end this document exists to save you from repeating.**

Confirmed real case (agents carousel, 3 slides per tab): with `loop: true` and
`centeredSlides: true` — true regardless of `slidesPerView: 'auto'` or a fixed numeric
`slidesPerView`, and regardless of `loopAdditionalSlides`/`loopedSlides` overrides — Swiper
never creates any `.swiper-slide-duplicate` clones from only 3 source slides
(`swiper.slides.length` stays exactly 3). It silently repositions the 3 real elements so both
"prev" and "next" classed slides land on the *same* side of the active slide instead of
flanking it, with `swiper.params.loop` still reading `true` throughout.

**The fix that was tried first, and shipped as documented guidance here, was: duplicate the
real slide set to 6 (two copies of the same 3) before constructing `Swiper`, keep `loop: true`.**
This did make Swiper generate clones and briefly looked correct. But cycling `slideNext()`
repeatedly (5+ times, not just once) reveals a **second, separate, and worse bug**: `loop: true`
gets **permanently stuck** — `activeIndex` stops advancing at all — after exactly one
transition. This reproduces regardless of the duplication count (6, 7, more), regardless of any
`loopedSlides`/`loopAdditionalSlides` value, and regardless of whether `effect: 'coverflow'` or
the plain-CSS-classes approach above is used. It is a property of `loop: true` itself combined
with this carousel's shape (few real slides, `centeredSlides: true`, a fractional
`slidesPerView` like `1.15`/`2.3`), not of any one config value.

**The trap that made this take two rounds to actually fix: the exact same "stuck after one
transition" symptom also has a real, unrelated, and genuinely-benign explanation elsewhere in
this file — a backgrounded browser pane failing to fire `transitionend`, fixable by re-testing
with `speed: 0` or in a foregrounded tab (see the general backgrounded-pane entry). The first
time this stuck-loop symptom appeared, it was tested with `speed: 0`, appeared to resolve, and
was concluded to be that same benign false positive — so the clone-to-6 fix above was shipped
and documented as correct. It was not: a later session, cycling `slideNext()` many times with
real transitions in a genuinely foregrounded tab, confirmed the freeze is permanent and real.
**A known false-positive explanation for a symptom does not prove a new occurrence of that exact
symptom is the same false positive — re-verify by cycling the interaction well past one
transition (5–10+ times) with real transition speed in a foregrounded tab, and check actual
rendered geometry (`getBoundingClientRect()` on every slide) before trusting an existing
"this is just a rendering artifact" explanation over what you're currently seeing.**

**The actual fix: don't use `loop: true` at all for this carousel shape.** Repeat the real
slide set several times (enough that a user has to click prev/next dozens of times in one
direction to ever reach a real boundary — 7 copies for 3 real slides) as plain **non-looping**
slides, start on the middle copy, and hand-roll the "feels infinite" wraparound yourself instead
of leaning on Swiper's loop machinery at all:

```js
var REPEAT_COUNT = 7; // copies of the real slide set; high enough that a boundary is never practically reached
var dotCount = wrapper.querySelectorAll('.swiper-slide').length; // the logical/original count
if (dotCount > 1) {
  var originalSlides = Array.from(wrapper.children);
  for (var r = 1; r < REPEAT_COUNT; r++) {
    originalSlides.forEach(function (slide) { wrapper.appendChild(slide.cloneNode(true)); });
  }
}
var swiper = new Swiper(el, {
  centeredSlides: true, loop: false, /* ... */
  initialSlide: dotCount > 1 ? Math.floor(REPEAT_COUNT / 2) * dotCount + Math.floor(dotCount / 2) : 0,
});
swiper.dotCount = dotCount; // external dot/pagination UI still has only `dotCount` dots
```

External dots use `swiper.activeIndex % swiper.dotCount` to know which of the *original* dots
to mark active (not `realIndex`, which only exists in loop mode), and jump to the nearest
repeated copy of the target logical slide `i` — never `slideToLoop`, which doesn't exist without
loop mode — so a dot click never causes a jarring jump across the whole repeated list:

```js
dot.addEventListener('click', function () {
  var nearestCopy = Math.round((sw.activeIndex - i) / dotCount);
  sw.slideTo(nearestCopy * dotCount + i);
});
```

**Detection, either version of this bug:** check `getBoundingClientRect().left` on every
`.swiper-slide` directly, not just a screenshot (a broken peek side can be off-canvas and easy
to miss visually); for the stuck-loop version, click/call `slideNext()` at least 5–10 times in a
row and confirm `activeIndex` keeps advancing every time, not just once.

## A reported spacing/cropping defect can be baked into the source raster asset itself

Confirmed real case, twice independently (Sep 2026): a user asked to "reduce the spacing" above
and below a mobile hero image, and separately reported a composite dashboard mockup as
"cropped/cut off" on one side. In both cases the instinctive fix was CSS (margin/padding, or
`object-fit`/`object-position`) — and in both cases the real defect was baked into the source
PNG's own pixels: the hero image had ~300px of solid white padding above and below the actual
card content inside the file itself; the dashboard mockup's right column was genuinely cut off
at export time, not by any container crop. No CSS property can restore or hide content, or
remove whitespace, that lives inside the raster data rather than around it.

**Detection:** before writing any CSS in response to a spacing/cropping/whitespace complaint on
an image, open the actual source file and look at its real pixel content (view it directly, or
sample rows/columns with PIL) — don't assume the complaint describes a margin, padding, or
`object-fit` problem just because that's the more common cause. A tight crop, a wrong
`aspect-ratio`, or unexpected whitespace that doesn't respond to CSS changes the way it should is
the signature.

**Fix:** if the defect is in the source asset, fix the asset — re-export at the correct crop
from Figma if a wider/tighter capture is available, or crop/trim the existing file with PIL
(cutting at a real structural boundary — a full column, a rounded-corner edge — never an
arbitrary width that just relocates the same defect elsewhere). Update the CSS `aspect-ratio`
and the `<img>` width/height attributes (H12) to match the corrected file's real dimensions.
See `HARD-RULES.md` H10's swap-in-place sub-case for the multi-image/tab variant of this same
lesson.

## Asset provenance: proximity, an odd opacity, or a derived crop are not proof of what an asset actually is

Three confirmed real cases, same underlying mistake — trusting an asset's apparent context
instead of verifying its actual content/values:

1. **Proximity/naming similarity in the Figma layer tree does not confirm a candidate node is
   the source of a shipped asset.** A plausibly-named nearby node (`hp-agents-card-1`) turned out,
   on actual `get_screenshot` inspection, to be a completely different, unrelated mockup (a
   different product board, different mode) than the one actually used on the page. Always
   screenshot-verify a candidate source node's real content before treating it as an asset's
   origin — a nearby or similar-sounding layer is not evidence.
2. **A translucent/faded element is not automatically a rendering bug.** Twice, a user flagged
   an apparently low-opacity element as a defect; both times, checking the specific Figma node's
   own `opacity`/fill values (not a sibling's, not an assumption) confirmed the translucency was
   deliberate design (a `60%`-opacity chat bubble, a gradient-to-transparent table column).
   Before "fixing" an odd-looking opacity/fade, check the source node's own values first.
3. **Deriving a crop from a larger reference composite, instead of exporting the specific node
   directly, makes it hard to tell design intent from a cropping artifact** — both confirmed
   opacity cases above turned out to also be crops taken from a bigger reference image rather
   than a fresh per-node export, which is part of why they read as ambiguous in the first place.
   Prefer exporting directly from the specific node's own id over deriving a sub-crop from a
   larger composite whenever both are available.

## Figma desktop-bridge tools only resolve nodes on the page/tab currently active in the app

Confirmed real case (Sep 2026): `get_metadata`/`get_design_context` failed with a "node not
found" error for a node that lives on a different page than the one currently open in the Figma
desktop app, while `get_screenshot` and `download_assets` (which go through Figma's REST API,
not the live desktop bridge) kept working for the same node regardless of which page was active.
This is not a broken connection or a bad node id — it's a real scoping limit of the
bridge-based tools specifically.

**Fix:** in a multi-page Figma file, if `get_metadata`/`get_design_context` return "not found"
for a node you know exists, first check (or ask the user to check) whether that node's page is
the currently active tab in the Figma desktop app. If switching pages isn't practical mid-build,
fall back to `get_screenshot`/`download_assets` for that node — they work regardless of which
page is active.

## `flex: 1 1 0%` on a child with no in-flow content silently overrides an explicit `height`

Confirmed real case (Sep 2026): a collapsed accordion-style card used `position: absolute` for
all of its content (so the collapsed state shows nothing in normal flow) plus an explicit
`height: 120px` to hold a visible collapsed size. The card's own rule was `flex: 1 1 0%`. Because
the card has no in-flow content, its flex-basis of `0%` won — the explicit `height` was silently
ignored, collapsing the card to zero visible height instead of the intended 120px.

**Fix:** a flex child that must hold an explicit height regardless of its in-flow content needs
`flex: 0 0 auto` (or an explicit `flex-basis` matching the intended height), not `flex: 1 1 0%`
— the `0%` basis only behaves as expected when the child actually has in-flow content to size
against.

## `align-items: center` on a section wrapping the standard container chain collapses unsized block children to fit-content

Confirmed real case (Sep 2026): a section's outer `<section>` had `display: flex;
flex-direction: column; align-items: center` (to center its content), wrapping the standard
`.padding-global > .container-large` nest. `.padding-global` is a plain block `<div>` with no
explicit width. Under the default flex `align-items: stretch`, an unsized block child spans the
full cross-axis automatically; `align-items: center` instead shrinks it to fit-content, silently
collapsing the whole container chain from its intended ~1280px down to whatever width its content
happened to need (in the confirmed case, ~720–880px) — this reads as a working, "centered"
section right up until `HARD-RULES.md` H22's page-wide container-width measurement catches the
narrower box.

**Fix:** don't apply `display: flex` + `align-items: center` directly on a `<section>` that wraps
the standard container nest unless every layer in that chain has its own explicit width. If
centering is already handled at a deeper level (e.g. the actual content block inside
`container-large`), the outer section doesn't need its own flex/center rule at all — removing it
restores the default `stretch` behavior that keeps the chain full-width.

## A CSS custom-property fallback never applies once a global stylesheet already defines that token

Confirmed real case (Sep 2026): a rule read `color: var(--clay-color-text-default-secondary,
#676879)`, written with the expectation that the fallback hex would apply as an AA-contrast-safe
override. But `tokens.css` is linked globally on the page and already defines
`--clay-color-text-default-secondary` (to a grey that fails contrast in this context) — a CSS
custom-property fallback only ever applies when the property is **completely undefined**
anywhere in scope, never when it resolves to a value you simply don't want. The fallback was
dead code; the grey token's real, defined value won every time.

**Fix:** don't rely on a `var(--token, fallback)` fallback to override a token a global
stylesheet already defines. If a specific rule needs a different value than the token's global
definition, override the actual property directly on that selector (e.g.
`color: #1a1a1a;` or a locally-scoped custom property), not via the variable's own fallback
argument.

## Match a Figma variable to a Clay token by its resolved value, never by label name alone

Confirmed real case (Sep 2026): a Figma text style was named "heading-3/desktop" and set at
48px. The Clay codebase's own `h3-desktop` token, despite the matching label, actually resolves
to 56px — the real value-matching token was `h4-desktop`. Figma variable/style names and a
design system's own token names are chosen independently and can drift out of step even when
they look like an obvious match.

**Fix:** when mapping a Figma variable/style to a Clay CSS token, verify by the token's actual
resolved pixel/color value (read `tokens.css` or `get_variable_defs`), not by matching label
text. A name match is a hint to check, never confirmation on its own.

**This applies to color/background tokens too, not just type-scale.** Second confirmed case
(stack section media panel, Sep 2026): `background: var(--clay-color-grey-100)` looked like the
obviously-right token for a light-grey media placeholder background, but its resolved value
didn't match Figma's literal fill for that slot — had to hardcode `#F3F4F5` instead. Treat a
plausibly-named background/fill token exactly like a plausibly-named type token: check its
resolved value before trusting the name.

**Third confirmed case:** the same Figma style/token name (e.g. `h4-desktop`) used across
multiple text nodes in one file can resolve to different pixel sizes at each usage — check
`get_variable_defs` per node even when the name repeats.

## Non-square icons/logos get distorted by matching fixed width and height on the same element

Confirmed real case (Sep 2026): a footer icon row used `.footer-links-icon img, svg { width:
18px; height: 18px }`, forcing every icon into an 18×18 square. This was invisible for the
several icons that happen to be square, and stretched/squeezed the icons that aren't (three
product-integration logos measuring 26×18, 19×24, and 28×19 in their natural aspect ratio) —
easy to miss in a spot-check of the row since most items in it looked fine.

**Fix:** never size an icon/logo `<img>`/`<svg>` with matching fixed `width` and `height` unless
the source asset is confirmed square. Default to constraining a single dimension (commonly
`height: Npx; width: auto`) with an optional `max-width` cap, so non-square marks keep their
natural proportions — the same pattern `HARD-RULES.md` H16 item 2 already establishes for
logo-strip sizing generally.

## `qa_gate.py`'s H6 duplicate-section check could false-positive on a section's own script re-selecting itself (fixed)

Confirmed real case (Sep 2026): `tools/qa_gate.py`'s H6 check matched `data-section="<slug>"`
anywhere in the raw HTML text via a plain regex — including inside a section's own inline
`<script>` block, where a line like `document.querySelector('[data-section="stack"]')`
re-selecting the section from its own behavior script matched the exact same pattern as a real
second `<section data-section="stack">` tag. This produced a false "duplicated section" finding
for any section whose script used the attribute-selector form to find its own root.

**Fixed in `tools/qa_gate.py`**: `check_h6_duplicate_sections` now strips `<script>...</script>`
blocks from the HTML before running the duplicate-slug regex, so a script's own string literals
can no longer trigger it.

**Going forward, prefer `document.getElementById('<section-id>')` over
`document.querySelector('[data-section="..."]')`** for a section's own root-element lookup in
its behavior script (give the section an `id` matching its slug) — this also sidesteps the
underlying ambiguity entirely, independent of whether the gate itself is patched in the copy of
this skill you're running.

## Animating `grid-template-rows: 0fr → 1fr` is a more reliable expand/collapse technique than animating the `flex` shorthand directly

Confirmed real case (Sep 2026): a section-stack accordion item visibly "vanished" mid-transition
on mobile when its open/close animation was implemented by animating the `flex` shorthand
property directly. Checking Clay's own equivalent component (its real Chromatic story) showed it
instead animates a wrapping element's `grid-template-rows` between `0fr` and `1fr` — a technique
that clips smoothly to true content height without the timing/rendering inconsistencies of
animating `flex-grow`/`flex-basis` across browsers.

**Fix/pattern:** for any collapsible/expandable panel (accordion item, dropdown content, "show
more" region), wrap the collapsible content in a grid container and animate
`grid-template-rows: 0fr` (collapsed) → `1fr` (expanded) on a `transition`, with the actual
content in a single grid child that has `overflow: hidden` on its own box:

```css
.accordion-panel-wrapper {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s ease;
}
.accordion-panel-wrapper.is-open { grid-template-rows: 1fr; }
.accordion-panel-content { overflow: hidden; }
```

This matches Clay's own real implementation — when a section resolves to a Clay-anchored
accordion/disclosure component (H28/H39), extract and reuse this exact mechanism rather than
animating `flex` from scratch.

## `resize_window`'s `desktop` preset resets to the pane's own current size, which can be a narrow ~900px, not a real wide desktop viewport

Confirmed real case (agents carousel spacing work, Sep 2026): after using `resize_window` with
an explicit `{width, height}` for a while, calling it again with `preset: "desktop"` (intending
to "go back to a normal desktop view") reset the viewport to whatever the Browser pane's own
panel happened to be sized at — measured at `document.documentElement.clientWidth: 906` in this
case. That's just over the project's 900px mobile/desktop CSS breakpoint, so desktop rules were
active, but at a width the layout wasn't remotely designed for. This produced a large, entirely
fake "454px page overflow" that consumed several tool calls to diagnose before the actual
`docWidth` was checked and the mismatch became obvious.

**The rule:** `desktop` is not "a wide viewport" — it's "whatever the panel's own current
on-screen size is," which is frequently narrow. Never trust a `preset: "desktop"` measurement at
face value for anything spacing/overflow-related; either check `window.innerWidth` immediately
after the call, or skip the preset entirely and pass an explicit `{width, height}` (e.g. 1440x900)
whenever a reliable, reproducible desktop measurement actually matters.

## When both a staging and a production build of the same real reference component exist, prefer production

Confirmed real case (customer-stories accordion, mobile behavior, Sep 2026): the mobile
"collapsed card" behavior was first built by copying `mondaystaging.com`'s live DOM, which
collapsed non-active cards to `height: 0` — invisible and completely untappable, matching what
the user then reported as "can't operate the accordion on mobile." Re-checking the equivalent
component on the **production** site (`monday.com/departments/pmo`) showed the real, finished
behavior: collapsed cards stay visible at ~120px (photo + logo), clearly tappable. The staging
build was mid-deploy or simply incomplete for this specific interaction; production was correct.

**The rule:** a `*staging*` domain is not a more "raw" or equally-valid version of the same
component — it can be genuinely broken in ways production isn't (and vice versa, rarely). When
copying real-site behavior and something about it looks broken or doesn't match the design intent
(especially interaction/responsive behavior that's easy to half-ship), check the production
equivalent before assuming the staging version is authoritative. Don't average or split the
difference between the two — pick the one that's actually confirmed working end-to-end.

## A flex/grid `gap` is measured from the container's own box edge, not from content that escapes it via `overflow: visible`

Confirmed real case (agents carousel arrow spacing, Sep 2026): a Swiper coverflow carousel's
peek cards were deliberately allowed to spill past their `.section-agents-stack` container via
`overflow: visible` (so they'd read as sitting behind/under the active card, not hard-clipped by
it — see the Swiper Coverflow gotcha above). Separately, `spaceBetween` was set to a large
negative value to pull the peek cards in tight against the active card. The external "Previous"/
"Next" arrow buttons sat outside the container, spaced via a plain flex `gap` on their shared
parent. Raising that `gap` from 64px → 96px produced almost no visible change in the actual
clearance between the peek card's edge and the arrow (13px either way) — because the peek card,
via the negative `spaceBetween`, was itself extending ~70px past the container box the `gap` is
measured from. The `gap` property has no idea that content overflowed past its sibling's box; it
only ever sees the box's own declared width.

**The rule:** once any sibling of a `gap`-spaced flex/grid item uses `overflow: visible` (or
otherwise renders content outside its own box — a peek carousel, an intentionally-overflowing
badge, etc.), the *visible* clearance to the next item is `gap − overflow_amount`, not `gap`
itself. Measure the actual escape distance first (`getBoundingClientRect()` on the visually
escaping content vs. its nominal container), then size the `gap` to `desired_clearance +
overflow_amount` — don't just keep raising the raw `gap` value and re-measuring by eye, which
reads as "barely moved" and invites overshooting in the other direction (as happened here: the
next attempt jumped to a much-too-wide gap before dialing back to the correct value).

## `aspect-ratio`-driven sizing tuned for one breakpoint's width can blow up at a breakpoint where the container width is drastically different

Confirmed real case (customer-stories collapsed-card logo, Sep 2026): a company logo overlay
used `width: left/right: 12px` (i.e. width = container width − 24px) with a fixed
`aspect-ratio: 60 / 28` to derive its height — correctly sized for the *desktop* collapsed card,
which is a narrow ~100px sliver (so the logo rendered at a reasonable ~35px tall). The same rule,
unscoped, also applied to the *mobile* collapsed card, which is nearly full viewport width
(~340px+) once the card stopped being hidden entirely (see the loop/flex-basis gotcha above) —
at that width the same aspect-ratio formula produced a logo well over 100px tall, several times
taller than the card itself, overflowing and clipping badly.

**The rule:** `aspect-ratio` locks a fixed relationship between width and height, so any sizing
rule that derives width from "100% of the container minus padding" only stays reasonable if the
container's width stays within the range it was actually tuned for. The moment the same
component appears inside a container whose width differs by an order of magnitude at another
breakpoint (a narrow desktop sliver vs. a nearly-full-width mobile card is a common pairing),
recompute or cap the width explicitly at that breakpoint — don't assume the aspect-ratio formula
generalizes. The fix here was a fixed pixel width (140px) at the breakpoint with the much wider
container, restoring `left/right` percentage sizing only where the original narrow-sliver math
still applies.

## An infinite horizontal marquee needs an `overflow-x`/`overflow-y` split, not one `overflow: hidden`

Confirmed real case (marquee-cta section, Sep 2026): a horizontally-scrolling text ticker used
a single `overflow: hidden` on its track row to clip the track at the row's horizontal edges.
That same rule clips vertically too — it sliced off letter descenders (e.g. the tail of the "g"
in "marketing") on every line of scrolling text, since the row's own height was sized to the
text's cap-height/x-height box, not its full glyph bounds.

**Fix:** split the single `overflow: hidden` into `overflow-x: hidden; overflow-y: visible` —
this still clips the horizontally-scrolling track at the row's left/right edges (the actual
point of an infinite marquee) while letting descenders render past the row's own box vertically
without being cut. Since the horizontal clip is still real and necessary (the track has to end
somewhere), soften it with a horizontal fade instead of a hard edge, which reads as intentional
rather than "cropped":

```css
.marquee-track-row {
  overflow-x: hidden; overflow-y: visible;
  -webkit-mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
  mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
}
```

## A "these aren't the same size" complaint can be a crop/zoom mismatch, not a box-dimension bug

Confirmed real case (avatar stack, Sep 2026): a user flagged a row of avatar images as "not the
same size and style." Direct measurement showed every avatar's container box was pixel-identical
(40×40) — the actual defect was inconsistent crop/zoom between a real photo avatar and an
illustrated avatar sharing the same box, which reads visually as a size mismatch (the subject
fills more or less of the frame) even though the frame itself is uniform.

**Fix/detection:** when a "size" or "not matching" complaint comes in on a set of elements that
share an explicit, identical CSS box size, don't stop at confirming the box dimensions — check
each image's `object-position`/crop framing individually (how much of the frame the actual
subject fills), since that's what a viewer perceives as "size" even when it's really a crop
inconsistency the box-size check alone won't catch.

## An isolated sub-frame's exported pixel dimensions can diverge from its Figma layout-frame's declared width/height

Confirmed real case (marketing-page showcase collage decomposition, Sep 2026): rebuilding a
16-piece flattened illustration into individually-positioned real elements (see `HARD-RULES.md`
H9's scroll-motion exception) used each piece's Figma-declared `width`/`height` (from
`get_metadata`) both to size its CSS box AND to derive its aspect ratio. Several pieces' exported
PNGs came back at a visibly different aspect ratio than their metadata box — one frame declared
269×40 (6.7:1, a short wide strip) but exported at 308×117 (2.6:1) pixels. Forcing the export into
the metadata box's aspect ratio squished the visible content (an avatar circle that overflows its
parent pill frame's own declared bounds, a common pattern for a chat-bubble-style layer).

**Root cause:** `download_assets`/`get_screenshot` export the smallest bounding box that contains
every visible pixel in the subtree, which is not always equal to the parent frame's own declared
layout box — a child (an avatar, a badge, an icon) positioned to intentionally bleed outside its
parent's bounds expands the true export bbox beyond what `get_metadata` reports for the frame.

**Fix:** don't trust the metadata frame's aspect ratio for sizing once exported. For each
exported piece: read its own file's real pixel dimensions (`PIL.Image.open(path).size`), compute
`native_aspect = height/width`, keep the metadata `width%` (horizontal position is reliable — the
overflow in every confirmed case was vertical, an avatar centered on a pill's vertical midline),
and derive `height% = width_px * native_aspect / container_height_px * 100` instead of using the
metadata `height%` directly. Because the extra height typically comes from content overflowing
symmetrically above *and* below the frame (not just below), also re-center: shift `top%` up by
half the delta between the new derived height and the original metadata height
(`new_top = meta_top - (new_height - meta_height) / 2`). Verify by compositing the pieces
offline (or in a real browser) at final size and comparing side-by-side against a
`get_screenshot` of the full composite node — a squished avatar or an off-center pill is visible
immediately at that point, before it ever reaches the page.

## Different device frames for "the same" section in a Figma file can drift out of sync — cross-check both before trusting either

Confirmed real case (marketing-page showcase collage, Sep 2026): the same illustrated section had
a desktop frame and a separate mobile frame, both containing what should be the identical central
dashboard-mockup card ("Product launch campaign"). The mobile frame's card had real, finished
content (`$1.24M`, status pills, dates). The desktop frame's *same* card, at the *same* node
depth in the file, was a stale skeleton/placeholder — blurred gray bars, no real numbers, no
status pills — left over from an earlier iteration and never updated once the mobile version was
finished. Nothing about the desktop frame signaled "this is stale": it rendered cleanly, had a
plausible layout, and would have passed any structural check. Only a direct pixel comparison
against the mobile frame's equivalent piece revealed the mismatch.

**The rule: when a page or file provides separate desktop and mobile frames for what is
conceptually the same section, never assume both are equally current.** Before treating either
frame as the source of truth for a shared sub-element (a card, an illustration, a piece of copy)
that appears in both:
1. Fetch a real screenshot (`get_screenshot`) of the equivalent region in *both* frames, not just
   the one frame matching the breakpoint you're currently building.
2. Compare them directly — a shared element should be pixel-equivalent (modulo scale). If they
   differ in *content* (not just size), one of them is stale — don't assume it's the desktop
   frame or the mobile frame by default; check which one looks finished (real data/copy, not
   placeholder skeleton bars or Lorem ipsum) and use that one's asset for both breakpoints.
3. This applies even when you were only asked to fix one breakpoint — a stale placeholder found
   while building the mobile version is worth carrying over to the desktop build too (and vice
   versa), since it's the same underlying defect showing up wherever that shared piece is used.

## "You didn't copy it right" after a value-level match usually means a missing whole element, not a wrong value

Confirmed real case (marketing page customer-stories section ported from a live PMO reference,
Sep 2026): the port was verified by extracting every CSS rule for the relevant classes from the
reference's real compiled stylesheet, confirming every value matched byte-for-byte, and
side-by-side screenshotting the real rendered reference against the port at rest and mid-
interaction — everything matched, and this was reported back to the user as correct. The user
insisted it still wasn't right. The actual defect: the reference section has a whole CTA button
(`<a>...See customer stories...</a>`) sitting below the card track that the port never included
at all — a missing *element*, invisible to any check that only compares computed CSS values on
elements that already exist in both versions.

**The rule: value-level verification (computed styles match, screenshots line up) only proves
the elements you ported are styled correctly — it says nothing about whether you ported every
element that exists in the reference.** Before declaring a port complete, do an explicit element-
inventory pass: list every direct child of the reference section/component (by tag + class, from
its real DOM, not a summary of "the interesting parts") and confirm each one has a corresponding
element in the port — including things that look like page furniture (a trailing CTA, a small
caption, a decorative divider) and are easy to mentally file under "not part of the interaction
being copied" when the actual ask was to copy the whole thing.

**An "already sized correctly" claim about a frame/link needs verification by actual matching
pixel dimensions, not a general impression that it "looks like it fits."**

## Verifying a local reference page needs a real local server, not the sandboxed preview tool

Confirmed real case (Sep 2026, comparing a marketing page against a local PMO reference file):
opening a `file://` path outside the current project folder in the sandboxed browser-preview tool
rendered it as an inert "static snapshot" — relative-path images never loaded and a CDN `<script>`
tag for a carousel library never executed, making the reference page look broken (and, briefly,
making it look like the *port* was broken when it was actually the preview sandbox silently
failing to load the reference itself).

**Fix:** for any local HTML file that needs real interactivity/asset-loading to verify (a
reference page to compare against, or the page under test itself, when the sandboxed preview
tool won't do), spin up a throwaway local HTTP server (`python3 -m http.server` or a tiny
Node `http.createServer`) and drive it with a real headless browser instead. If the project
already has Playwright installed (check for a `perf/`-style tooling folder with its own
`node_modules`), reuse that install rather than a fresh global one — but the default
`chromium.launch()` can fail with "executable doesn't exist" if only a `chromium_headless_shell`
build is cached; look for a sibling `chromium-<version>/chrome-mac-arm64/Google Chrome for
Testing.app/Contents/MacOS/Google Chrome for Testing` (or platform equivalent) under
`~/Library/Caches/ms-playwright/` and pass it as `executablePath` explicitly. This unblocks real
screenshots, real computed styles, and real click/hover/tap interaction testing against both the
reference and the port — the only way to catch gaps that a static code-level comparison misses.

## Vague motion feedback ("make it feel smoother / less jarring / less abrupt") has a concrete default fix

Confirmed real case (marketing page agents-carousel tab switch, Sep 2026): the user asked for the
tab-switch animation to feel "smoother and less attacking" without giving exact numbers. The fix
that was confirmed correct on the first try: scale up the *existing* transition durations by
roughly 1.5–1.7× (here: a card's opacity/transform transition 350ms → 600ms, and the carousel's
own slide-`speed` 600ms → 900ms) while keeping the same easing curve (`cubic-bezier(.4,0,.2,1)`)
unchanged.

**The rule: when timing feedback is qualitative rather than numeric, don't invent a new easing
curve or guess at an arbitrary new duration — multiply every duration already driving that
specific interaction by ~1.5–1.7× and leave the curve alone.** Identify *every* timing value
involved first (a tab switch here meant two separate systems: the carousel library's own slide
`speed` option, and a plain CSS `transition` on the card element) — scaling only one of the two
would leave the other feeling unchanged and the fix half-done. Confirm which specific values
changed to the user rather than just asserting "it's slower now."

## `flex-wrap: wrap` + `justify-content: center` can look broken when it isn't — the row's own content just happens to fill the container

Confirmed real case (G2 trust badges, Sep 2026): a row of 5 differently-sized badges wrapped into
a 3+2 split at mobile width, and the "Leader" badge (last item in the first row of 3) rendered
flush against the row's right edge instead of looking centered. `justify-content: center` was
correctly applied the whole time — the actual cause was that the first row's 3 badges' combined
width (badge widths + gaps) came out to within ~2px of the container's own width, leaving
`justify-content: center` with essentially zero slack to distribute. The CSS was never broken;
there was just nothing for it to center *into*.

**Detection: before concluding a `justify-content: center` rule isn't working, measure the row's
actual content width against its container's width** (`getBoundingClientRect()` on the row vs.
the individual children, not a glance at the rendered screenshot) — if they're close, centering
is a no-op by construction, and the real fix is changing *what's in the row* (which item ends up
last, whether an item moves to a different row) rather than touching the centering rule at all.

## A single DOM order can't satisfy two breakpoints that want the same wrapped item in different relative positions — use per-breakpoint CSS `order`, and give every sibling an explicit value

Confirmed real case (G2 trust badges, following directly from the entry above, Sep 2026): once the
"Leader" badge's *row* position was fixed by moving it to the middle of DOM order (3rd of 5 —
which is what centers it on desktop's single unwrapped row), mobile's 3+2 wrap put it *last* in
row 1 again, just via a different mechanism (that DOM position happens to land as the 3rd/last
item of the first wrapped row). Desktop wanted it 3rd-of-5; mobile wanted it 2nd-of-3 in its row.
No single DOM order satisfies both — they're genuinely conflicting requirements from the same
element list.

**Fix: leave DOM order set for the breakpoint where it matters more structurally (here, desktop's
unwrapped row), and use CSS `order` inside a `max-width` media query to visually reposition the
item only at the other breakpoint.** The gotcha inside the gotcha: **every sibling in the flex
container needs an explicit `order` value once you're setting it on any of them** — leaving the
untouched siblings at the default `order: 0` sorts them *ahead of* any sibling given a higher
explicit value, which silently breaks the row's whole grouping (turned a clean 3+2 split into a
scrambled one) rather than just repositioning the one intended item. Assign a full explicit
sequence (1, 2, 3, 4, 5, or similar) to every child in that media query, not just the one moving.

## A reference page can have more than one marquee-style module — verify the class chain against the actual section, don't assume the first marquee CSS you find is the relevant one

Confirmed real case (mobile logo-strip, ported from a live PMO reference page, Sep 2026): the
reference's compiled CSS contained two entirely separate infinite-scroll marquee implementations
under different class-hash prefixes — a generic reusable "card row" marquee (pause-on-hover,
`animation: ... var(--marquee-duration, 30s)`) used elsewhere on the page, and the customer-logos
section's own dedicated, differently-named module (no hover-pause, a different keyframe name,
built specifically for that one section). Searching the CSS for "marquee"-shaped selectors and
grabbing the first believable match pulled in the *wrong* one — visually similar (both scroll
logos/cards infinitely) but mechanically different (different duration, different hover behavior,
different DOM shape).

**The rule: when porting a specific section's behavior from a reference page's real CSS/JS,
locate that section's actual rendered HTML first and read the exact classes *it* uses** — then
search the CSS/JS for those specific class names, not for a generic keyword like "marquee" that
can match an unrelated component elsewhere on the same page. A reference page reusing the same
visual pattern (infinite scroll, a card carousel, a modal) in more than one place is common
enough that class-name verification against the target section's own DOM is a required step, not
an optional sanity check.

## Count top-level sections against the build todo-list before starting — global chrome falls through the cracks exactly like any other section

Confirmed real case: Navbar and Footer were dropped entirely from a full-page build because
section discovery happened informally as the build progressed rather than as an explicit
enumerated list checked before the first section was written.

**Fix:** before Turn 2 of the first section, list every top-level child (by real y position, per
H3) — including header/nav/footer — as a numbered todo list, and don't report the build complete
until every item on that list, chrome included, has a corresponding built section.

## A carousel with an enlarged "active" card by default needs its starting index AND its peek-card size/position verified independently

Confirmed real case: an agents carousel opened on the wrong card in all 7 tabs — the emphasized-
card styling was correct, but the actual starting index (especially once the slide list was
duplicated/offset for a fake-infinite loop) never landed on the card that was supposed to read as
active. Separately, in the same carousel family: fixing a peek-card's scale doesn't fix its
position (`spaceBetween`) — they are two independent values that must each be checked against
Figma.

**Fix:** after wiring any centered/peek carousel, explicitly verify (a) which real card
`initialSlide` lands on, matching Figma's default screenshot, and (b) both the scale and the
spacing/position of neighboring cards, not just one.

## Shared code/class does not prove shared behavior — verify every real consuming instance or state before trusting or changing it

Three confirmed cases, same root mistake: (a) a repeating card/tab template rendering different
source images per instance showed a completely wrong logo on one Customer Stories card — it
loaded fine (no 404), it was just the wrong file, because only "did it load" was checked, not
"does it match this card's own name"; (b) two badges (Gartner vs. G2) that looked like the same
component and shared a CSS class turned out to have different real sizes on the live page; (c)
removing `flex: 1` because it looked unnecessary on the specific card being tested broke every
other card in the set that had a 1-line description.

**Fix:** before trusting that a shared class/template produces identical results across
instances, or before removing a rule that looks locally redundant, check it against every real
instance/state that consumes it — not just the one currently on screen.

## Document intentional content/asset substitutions — including any user-approved asset edit — as an explicit Accepted Gap or code comment

Confirmed real case: a hero video replacing an illustrated Figma mockup was a deliberate, approved
substitution, but with nothing marking it as such, later QA re-flagged it as a mismatch.
Separately, when a real asset limitation (not a CSS bug) blocks precision — e.g. a bento-grid
image whose full-width content can't be preserved under any aspect-ratio — the fix, with explicit
user permission, can be editing the asset itself: decomposing it into layers, deciding which
elements are "worth" the limited space, and serving the result via `<picture>`/`<source media>`
so an already-correct desktop crop isn't touched.

**Fix:** any deliberate deviation from a literal Figma-to-code match — a substituted asset type, a
re-composed/edited image — gets a one-line code comment or QA-report Accepted Gap entry naming
the substitution and why, the same discipline H22/H25 already establish for deliberate
width/link exceptions.

## Zoom into the actual source pixels before reporting a suspected color/tint mismatch

Confirmed real case: a small screenshot of a whole (especially dark) section was used to judge
whether chat-bubble colors matched Figma — it looked like a mismatch, but zooming into the actual
pixels showed the colors were correct; a small/whole-section capture is unreliable for
distinguishing near-black shades.

**Fix:** before reporting or fixing a suspected color/tint defect, zoom into the specific
element's actual rendered pixels (or sample them via PIL) rather than judging from a full-section
screenshot — this is the same discipline H30 already requires for icon-level checks, extended to
color judgments generally.

## Live-reference methodology: read the real DOM directly, check your own component system first, and let a specific live page override a general assumption

Three related confirmed cases: (a) rebuilding the Agents carousel from mondaystaging.com's real
source JS/CSS revealed a much simpler architecture than assumed from a screenshot alone — and a
Customer Stories CTA button was correctly copied from the live PMO page's real, already-existing
component rather than built from scratch; (b) "make it like page X" is answered fastest by
`getComputedStyle`/`getBoundingClientRect` directly on the real DOM, which reveals the real class,
wrapper relationship, and gap/`align-self` values in one shot — a screenshot-based guess took
longer and was less accurate; (c) a general component-library default (assumed, not verified
against a specific live page) contradicted what the real PMO page's Stack accordion actually does
on mobile (no image existed in the dropdown panel where one was assumed) — the specific live
instance won.

**Fix:** when a real live reference is available, go straight to its DOM/computed styles rather
than eyeballing a screenshot, check whether an existing component in your own system already
covers the need before building bespoke, and treat a specific live page's actual behavior as
overriding a general assumed default — while still preserving accessible/real text markup even
where the reference itself uses image-only text.

## A live reference page's unreliability can be transient — retry per request rather than writing it off permanently

Confirmed real case: a live PMO reference page was flagged unreliable earlier in a session
(content kept changing between checks), then came back reliable and became the most accurate
source in a later round of the same conversation.

**Fix:** don't treat one earlier "unreliable" verdict on a live page as permanent — try it again
on each new request. When it stays flaky across multiple attempts, fall back to a direct Figma
link and `get_variable_defs` on the exact node instead — stable ground truth that doesn't depend
on a live site's momentary state.

## A flattened background image can already bake in an element the HTML also renders on top of it

Confirmed real case: a card's background was a flat Figma-node screenshot that already contained
the card's logo baked into the pixels — the HTML then rendered the same logo again as a separate
live element on top, producing a visibly doubled logo.

**Fix:** before using a flat node screenshot as a background image, check (via `get_metadata` or a
zoomed look at the export) whether it already contains an element the HTML plans to render
separately — export only the layer that's actually missing, not the whole node, when this overlap
exists.

## `align-items: stretch` only grows a column to match its tallest sibling — it never shrinks, and `min-height: 0` doesn't help once the natural content sum already exceeds the target

Confirmed real case: a Stack section card meant to match a fixed-height sibling via
`align-items: stretch` overflowed by 3px in one content-length state — `stretch` will happily grow
a shorter sibling to match, but has no mechanism to shrink a taller one, and adding
`min-height: 0` (the usual flex-shrink unlock) doesn't help because the failure isn't a min-height
floor, it's that the content itself is taller than the target.

**Fix:** when using `stretch` to match a fixed-height sibling, check every real content-length
state the variable side can take, not just the one on screen — if any state's natural content
height exceeds the target, `stretch` cannot fix it; the fix has to bound the content itself
(line-clamp, a smaller target, or a scroll region).

## `justify-content` assumptions: verify edge-hugging vs. fixed-gap intent against Figma, and remember `flex-start`/`flex-end` is a no-op without an explicit width under a centered parent

Two confirmed cases: (a) a customer-story card's byline block used `justify-content: space-between`
to push a trailing element to the row's far edge — but Figma's real intent was a fixed gap
(`flex-start`), not edge-hugging, and `space-between` wrongly filled all available space; (b) an
Agents CTA button's `justify-content: flex-start`/`flex-end` alignment fix did nothing, twice,
because the container had no `width: 100%` under an `align-items: center` parent — without an
explicit width, the container shrinks to fit-content and there's no extra space for
`justify-content` to distribute in the first place.

**Fix:** check Figma directly for which of "hugs the edge" vs. "fixed gap" is intended before
choosing `space-between` vs. `flex-start`; and before trusting a `justify-content` alignment fix,
confirm the container actually has room to move within — check its real width in practice, not
just the rule you wrote.

## Flex measurement gotchas: a `box-sizing: border-box` parent can make a child's width look "stuck," and a container-width change invalidates a previously-solved `flex-grow`/padding-floor equation

Two confirmed cases: (a) debugging a Trust-badges container width, `getComputedStyle().width`
appeared stuck despite CSS changes — the actual cause was the parent's `box-sizing: border-box`,
which reports width inclusive of padding, so a child's `100%` will always read smaller than
expected; (b) a Customer Stories card's `flex-grow` value, originally solved against a
padding-floor equation at one container width, silently became wrong the moment the container's
width changed — the equation has to be re-solved against the new width, not assumed to still
hold.

**Fix:** when a computed width looks wrong, check the parent's `box-sizing` before assuming the
child rule is broken; and whenever a container width changes, re-derive any `flex-grow`/
padding-floor math that was solved against the old width — it doesn't carry over.

## Line-wrap verification: a hard `<br>` doesn't guarantee exactly the lines you expect, and a "coincidental" wrap won't repeat for a differently-sized asset

Two confirmed cases: (a) a Trust-section heading had a single hard `<br>` intended to force a
2-line break, but the first segment was itself too wide and wrapped again on its own — the actual
result was 3 lines, not 2, and this was only caught by checking in practice, not by reasoning
about the `<br>` alone; (b) G2 trust badges wrapped into a clean grouping in Figma only because
that specific graphic's size happened to fill the row exactly — when a differently-sized badge
asset was substituted, the same grouping didn't happen automatically and had to be forced
explicitly (e.g. `flex-basis: 100%` on the badge that needs its own row).

**Fix:** after adding any hard `<br>`, verify the actual resulting line count in the browser, not
just the break point; and treat any grouping/wrap that appears to happen "by coincidence" from one
specific asset's dimensions as something to force explicitly for every other asset, not something
that generalizes on its own.

## Reconstructing a completely missing image asset from a flat export

Confirmed real case: no real asset existed for a Software AG card background beyond a flat Figma
export with a known overlay baked in. The card was reconstructed by inverting the documented
overlay math (raw = observed × 2 for a known `rgba(0,0,0,.5)` overlay, so the live CSS overlay
doesn't double it) and inpainting/removing baked-in text regions before use.

**Note:** this is a specific recovery technique for a specific failure mode (no real asset
anywhere, only a flattened export with known, documented overlay math) rather than a general
rule — documented here as a technique (same precedent as this file's CSS-mask-watermark and
flood-fill entries) rather than a broadly-applicable lesson.

## Solving font-size backward from content width + an observed line-break + character counting, when no live measurement or fresh screenshot is available

Confirmed real case: bento-grid text cards needed a font-size decision with neither a live DOM
measurement nor a fresh screenshot available. The size was derived backward: known card width
minus padding, combined with a previously-observed line-break point and character counting,
produced a much more grounded estimate than a free guess.

**Fix:** when genuinely no live measurement or screenshot is available, this backward-derivation
method (content-box width + observed wrap point + char count) is an acceptable fallback — better
than eyeballing — but should be flagged in delivery notes as an estimate, not presented as a
measured value.

## An interactive component with desktop-only navigation needs a working, fully-wired mobile equivalent

Two related confirmed cases in the same carousel: (a) desktop arrows were hidden on mobile with no
substitute navigation — content became genuinely unreachable; (b) once dots were added, they were
wired only as a visual indicator, not to real click and touch-swipe navigation — an indicator with
no real navigation is part of the problem, not a fix.

**Fix:** any section with interaction affordances (arrows, tabs) that's already precision-matched
for desktop needs an explicit mobile-navigation check: does an equivalent mechanism exist
(dots/swipe), and is it wired to both a real click handler and real touch-swipe — not just
visually present. Cross-ref H40 (Clay mobile behavior) and H46 (library wiring is atomic).

## Animation pace ported from a live source must be computed as px/second, and re-derived per breakpoint

Two related confirmed cases: (a) copying a marquee's pace from a live reference by copying its
animation duration in seconds produces the wrong visual speed once your own text content is a
different length — compute px/second (total width ÷ duration) from the source instead, and derive
your own duration from your own content's width at that same speed; (b) doing this measurement at
one breakpoint and assuming it holds at another (e.g. desktop pace applied to mobile) is still an
estimate, not a measurement — a source may deliberately choose a different pace on mobile rather
than just scaling proportionally with text width.

**Fix:** always derive px/second from the source, never copy duration directly, and re-measure/
re-derive independently at each breakpoint you build for.

## Two "equal" gaps can be coincidentally equal from two entirely unrelated causes

Confirmed real case: the visual gap between a marquee and a CTA button, and the gap between the
CTA and the FAQ section below it, looked symmetric — but each side's spacing came from an
unrelated cause. Fixing only one side (in response to a report about one gap looking off) silently
broke the symmetry between them. Related: with no design reference at all for the value (no Figma
link, no live page given), guessing a symmetric-looking value (80/80) was wrong — the real value
was asymmetric (24/64).

**Fix:** when two gaps look equal, check both sources of spacing independently before changing
either one — don't assume fixing one side preserves the visual symmetry with the other. See also
`ASK-DONT-GUESS.md`'s "no reference at all" trigger for the other half of this case.

## Swipe/drag/gesture testing and cross-input support

A cluster of related confirmed findings from the same carousel bug, in the order they were found:

- Testing with only clean `touchstart`+`touchend` isn't enough to catch real gesture bugs — add
  `touchmove` with a small vertical deviation to trigger the real `touchcancel` behavior a browser
  sends when a gesture isn't purely horizontal.
- Never test swipe/drag by manually constructing `Touch`/`PointerEvent` objects and
  `dispatchEvent`-ing them — this bypasses the browser's real input-handling layer entirely. A
  synthetic-event test passed while the real gesture failed in a confirmed case, because it missed
  a native-image-drag hijack (see `HARD-RULES.md` H52) that only a real input path exposes. Fire
  real input instead: Playwright's `page.mouse.down`/`move`/`up`, or CDP
  `Input.dispatchTouchEvent`.
- Desktop "swipe" support must cover three distinct, non-overlapping input paths: real
  touch/pointer, mouse-drag-with-button-held, and two-finger trackpad swipe (which fires `wheel`
  events with horizontal `deltaX` and no mouse button at all). A fix that covers only two of the
  three will still fail completely for a Mac trackpad user — confirmed as the actual root cause
  after two earlier fixes both missed it.
- When a reported bug doesn't reproduce in your own test environment and you can't access the
  user's exact one, ask exactly how they're testing (browser/device/input method) before
  continuing to guess code fixes — this saved rounds once actually asked, after three rounds of
  guessing first.
- When a modern API (e.g. Pointer Events) seems unreliable in an environment you can't personally
  access or reproduce (no Xcode/Safari simulator, say), don't guess the specific missing behavior
  — add a robust, independent fallback path (e.g. classic `mousedown`/`mouseup` with an
  anti-double-fire guard) rather than continuing to patch the suspect API blindly.

## A CSS rule change has zero effect when JS is setting the same property as an inline style

Confirmed real case (agents carousel peek cards, Sep 2026): changing a CSS class rule from
`height: 350px` to `height: 406px` produced no visible change in the browser — the rendered height
stayed at 350px. Root cause: `setActiveCard()` called `card.style.height = '350px'` as a direct
inline style assignment on every state transition. Inline styles (`element.style.X`) have higher
specificity than any stylesheet rule, including rules written with high-specificity selectors or
inside `@media` blocks — so the CSS change was silently overridden on every transition.

**Detection:** when a CSS property change produces no effect, check for `element.style.<property>`
assignments in every JS state handler that touches the element — `grep -n "\.style\.height"` (or
the relevant property) across the JS. If found, the CSS alone will never win.

**Fix:** update both the CSS class rule *and* every JS inline setter to use the new value. Leaving
either one on the old value means it still loses.

## A fixed-px dimension taken from a reference with structurally different content is wrong

Confirmed real case (agents carousel peek cards, Sep 2026): the sidebar card `height` was 350px,
taken from mondaystaging.com's equivalent card — which was a flat image-only card with no real text.
Our card held a heading + multi-line description, so 350px was far too short: the description started
at `y=656` while the card's bottom edge was at `y=647`, hiding all text behind `overflow: hidden`.
The correct value (406px) came from `get_metadata` on the actual Figma node (node 2039:33046).

**Rule:** when a reference source's card has fundamentally different content from yours (image-only
vs. text+heading, single-line vs. multi-line body), never carry its height over as a default. The
right source is always the actual Figma node's own dimensions via `get_metadata`. The reference
value is only valid when the content structure is essentially identical.

## Hard `<br>` line breaks in a flex-1 heading work at only one viewport width

Confirmed real case (Hero heading + subtitle, Sep 2026): both the main heading and subtitle used
`<br class="hero-heading-break">` elements to force a 3-line split matching the Figma layout. A
code comment documented "works up to font-size 52px, breaks at 53px+", but this assumed a column
width of 600px. The Hero's text column is `flex: 1` inside a sibling row; its `max-width` sibling
is 600px, but the text column only *reaches* 600px at ~1432px viewport width and above. At common
desktop widths (1280px, 1366px) the column is significantly narrower, so each hard-break line wraps
again — 5–7 lines instead of 3, worse than no break markup at all.

**Fix:** remove all hard `<br>` elements and use `text-wrap: balance` on headings and
`text-wrap: pretty` on body/subtitle text. These produce a balanced, natural split at every
viewport width without assuming a fixed column width. See H53.

**Detection signal:** if a heading break is documented as "works at width/font-size X" but the
column is `flex`/`min-width`/`max-width`-bounded rather than a fixed px, test across the full
desktop range (900–1920px), not just the one width where the comment was verified.

## `display` computed style is not proof an element is visible to the user

Confirmed real case (agents-section pagination dots, Sep 2026): the user reported the desktop
pagination dots were missing. Every code-level check said they were fine — the markup existed,
`getComputedStyle(dots).display` returned `flex`, the bounding rect was non-zero and in a
plausible position, and the click handlers were wired. The dots were still completely invisible.
Root cause: a sibling `.agent-card.pos-center` (`position: absolute`, `z-index: 3`) rendered
directly on top of them. `display`, `getBoundingClientRect()`, and even a manual pixel-position
sanity check all describe where an element *would* paint in isolation — none of them detect that
a higher-stacked sibling is covering it.

**Fix / detection:** when confirming a UI element actually renders (not just that its CSS looks
right), check what's actually on top at its own coordinates:
```js
const r = el.getBoundingClientRect();
const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
// hit should be el (or a descendant of it) — if it's something else, that something else
// is covering it regardless of what el's own computed style says.
```
A real screenshot at the element's scrolled-into-view position is the other reliable check —
`display`/`opacity`/rect alone are not. See `HARD-RULES.md` H46's checklist.

## Moving an element to fix a z-index/overlap bug can silently change its layout algorithm

Confirmed real case (same pagination-dots bug, Sep 2026): the fix above required getting the dots
out from behind the absolutely-positioned center card. The first attempt moved the dots' closing
tag so they became a direct sibling of `.section-agents-stack` instead of a nested child inside
it. That resolved the z-index collision but created a new, different bug: the new parent
(`.section-agents-cards`) was `display: flex` with the default row direction, so the dots — now a
direct flex child — laid out *beside* the stack instead of below it.

**Rule:** don't relocate an element up the DOM tree to escape an overlap/z-index bug without first
checking what layout context (flex row vs. column, grid, positioned-ancestor) the new parent
imposes on its children — moving to fix one visual bug can introduce a different one that only
shows up in the new position. Prefer fixing the bug in place with explicit CSS (e.g.
`position: absolute` pinned to a specific edge of the original, unmoved parent) when the
surrounding markup structure has a reason to stay as-is (here: matching a colleague's file with
minimal diff).

## A normal-flow child inside a box of otherwise-absolutely-positioned elements renders at the top, not "after" them

Confirmed real case (same pagination-dots bug, Sep 2026): the dots `<div>` was the last child in
the markup, inside `.section-agents-stack` (`position: relative`, fixed height, `overflow:
hidden`), after three `.agent-card` elements. All three cards were `position: absolute`, so none
of them occupy space in normal flow. The dots — the *only* normal-flow child — didn't render
"after" the cards the way their DOM order suggests; flow layout has no concept of the
out-of-flow siblings at all, so the dots rendered at the very top of the box, exactly where the
absolutely-positioned center card (`top: 33px`) also sits.

**Rule:** DOM order only predicts visual order among elements in the same flow. A normal-flow
element that shares a positioned ancestor with absolutely-positioned siblings will lay out as if
those siblings don't exist — it does not "flow after" them just because it comes later in the
markup. To place a flow element visually below a stack of absolutely-positioned ones, either give
it explicit positioning too (`position: absolute; bottom: ...`) or move the absolutely-positioned
elements into their own wrapper so the flow element has a clean box to sit after.

## Sizing a shared fixed-height container off its first content variant instead of its worst case

Confirmed real case (agents-section pagination dots, Sep 2026): fixing the overlap above required
adding ~40px of clearance to a fixed-height (`529px`, `overflow: hidden`) card stack shared across
6 tab categories, each with a different agent-card description length. Measuring only the default
("Creative") tab showed ~52px of free space below the card content — comfortable. Checking the
other 5 tabs found one (`social-web`, a 3-line description) with only ~11px of free space at the
same box height — a description just one line longer used up more than 4x the vertical slack of
the default tab.

**Rule:** before picking a margin/clearance/height value for something added into a fixed-height
container that's reused across multiple content variants (carousel categories, tab panels,
repeated cards), measure the tallest/worst-case variant's actual rendered content height — not
just the first or default one. The default variant can have several times the slack of the
tightest one; sizing off it alone risks clipping or overlap for every other variant. See
`HARD-RULES.md` H46's checklist.

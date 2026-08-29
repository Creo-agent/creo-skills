# Gotchas — Tool and Environment Bugs Already Diagnosed

## Contents
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

Check this file before spending time re-diagnosing a bug that's already been found once.

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
3. **Do not flood-fill the baked-white region to transparent as a fix** — per item 19, this
   cannot work in general: real UI art usually contains its own white/near-white elements (cards,
   bubbles, input fields) that are edge-connected to the baked margin with no boundary in between,
   so a border-connected flood-fill either stops short of the true background or eats part of the
   art. It happened to look acceptable in one confirmed case only because that specific asset's
   interior whites weren't edge-connected to the border — that's a property of the specific
   asset, not a general guarantee, and isn't something to check for and rely on. Treat it as not
   a real fix; escalate to option 1 or 2 instead.

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

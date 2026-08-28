# Figma Extraction — Reliability Playbook

## Contents
- Nodes that fail get_design_context on every server
- Silent degrade to metadata-only
- Canvas-type (whole-page) nodes hard-fail
- Document order is not visual order
- get_variable_defs scope warning
- design.md expect-incomplete
- Prefer get_design_context asset URLs for many-glyph nodes; download_assets truncates at 20 SVGs
- download_assets' rawImages[] is not scoped to your node
- A media-slot's resolved SVG can be the placeholder layer, not the real content
- A text node's own `name` field can be stale relative to its live rendered text

This was the single biggest source of lost time in a prior live build. Read this before
assuming a Figma MCP failure is transient.

## Nodes that fail get_design_context on every server

Certain nodes reproducibly fail `get_design_context` with a generic "unexpected error" — on
**every** available server backend (confirmed across 3+ separate nodes on 2 independent server
implementations: the official remote server and the `plugin:figma:figma` connection). This is
not a transient network issue, and retrying the identical call does not help.

**The reliable fallback:** `get_metadata` on the failing node → drill into its child node IDs
individually with `get_design_context` per child → merge results. Never retry the same
whole-node call a second or third time hoping for a different result.

## Silent degrade to metadata-only

On very large nodes, `get_design_context` can silently return **metadata only** (generic layer
names like "Frame 2147241061" instead of real prose copy) with no explicit warning that this
happened. If a result's text content looks like layer names rather than actual copy, don't
conclude the section has no real content yet — drill into smaller child nodes instead; the real
content is usually there, just not surfaced at that node size.

## Canvas-type (whole-page) nodes hard-fail

`get_screenshot`/`get_design_context` hard-fail on `canvas`-type nodes (an entire Figma
**page**, not a frame — `x`/`y`/`width`/`height` all report `0`). Unlike the large-node case
above, there is no smaller child to drill into that fixes this — the page itself has no bounds.
**Always check node type via `get_metadata` first**, and target a bounded frame, never a page-
level canvas id.

## Document order is not visual order

`get_metadata`'s child list order reflects Figma's internal document/z-order, not top-to-bottom
visual position. **Sort top-level children by `y` position** before assuming section sequence.
Also expect that a single visual section is sometimes composed of 2–3 sibling root-level nodes
(a large illustration + a floating icon + a supporting frame) rather than one clean wrapper
frame — reconstructing true section boundaries may require grouping siblings by proximity, not
assuming one node = one section.

## get_variable_defs scope warning

`get_variable_defs` returns the **entire** multi-library token set the file subscribes to —
Clay tokens mixed with unrelated product design systems, if the file happens to subscribe to
more than one library. **Confirm via `get_libraries` which library is actually relevant to this
page**, and filter to that before recording tokens anywhere — don't dump the raw variable
response into a design doc or token table.

## design.md / token-doc expect-incomplete

Whatever token/design documentation this build produces, expect the first pass to be
incomplete — real token gaps tend to surface mid-build (a specific radius/spacing value used
only once, discovered only when that section is reached), not all upfront. Patch the doc
opportunistically as gaps surface rather than treating an initial pass as final.

## Prefer get_design_context asset URLs for many-glyph nodes; download_assets truncates at 20 SVGs

`get_design_context` already emits every image/SVG it references as a constant with a real,
downloadable URL: `const imgFoo = "https://www.figma.com/api/mcp/asset/….svg"` (or `.png`). For a
node with many small marks — a footer, an icon grid, a logo strip — **curl-batch those URLs
directly** instead of re-exporting each child node one at a time. It's one already-paid call
versus N export calls.

This also sidesteps a hard limit: `download_assets` **truncates at 20 SVG assets** on a rich
subtree, returning `svgAssetsTruncated: true` and the message *"more than 20 SVG assets (only the
first 20 returned)."* On a real footer that silently drops marks. The design-context URL list does
not have that cap for the node it describes, so it's the complete source for dense chrome.
Confirmed live (IT persona page): the footer's 32 product/social/app-store/compliance marks came
straight from one `get_design_context` result's asset URLs, curl-batched in a single step.

**Caveats:** these asset URLs are short-lived (~7 days) — download promptly, don't paste a URL
into a deliverable expecting it to persist. And still pixel-verify each downloaded file (H29): an
isolated export can come back alpha-empty even when the URL resolves.

## download_assets' rawImages[] is not scoped to your node

`download_assets(nodeId)`'s `rawImages[]` array can include raster images that have nothing to
do with the requested node — confirmed live: a call scoped to one persona page's hero returned 4
raw images, but 2 of them were photos from a completely different persona page's hero elsewhere
in the same file. **Don't assume `rawImages[0]` (or any fixed index) is the right one.** Download
and actually look at each candidate (dimensions alone aren't enough to disambiguate — two
unrelated images can share nearly the same aspect ratio) before wiring one into the build.

## A media-slot's resolved SVG can be the placeholder layer, not the real content

When a media-slot node contains both a generic "Placeholder Image" shape (a flat icon-in-a-box,
present as an authoring fallback) and a real populated image on top of it (e.g. a layer literally
named "Screenshot ..." or similar), `get_design_context`'s flattened-image resolution can return
the **placeholder's** exported SVG, not the real content — even though `get_screenshot` on the
same node renders the real image correctly. If the exported SVG for a media slot looks like a
generic icon-in-a-rounded-box rather than the section's actual illustration/photo, don't trust
it — cross-check against a `get_screenshot` render of the same node, then fall back to
`download_assets`' `rawImages[]` (verified per the gotcha above) to find the real asset.

## A text node's own `name` field can be stale relative to its live rendered text

Confirmed real case: a text node's `name` attribute (as shown in `get_metadata`'s output) read
"Already trusted by 250K+ customers worldwide," but that node's actual rendered/resolved text
(confirmed both via a per-node `get_design_context` call and independently via a screenshot) was
"Trusted by 250,000+ customers worldwide" — different wording, different number format, no
"Already." Figma text-node names often get set once at authoring time and never kept in sync
with later copy edits. **Never use a text node's `name` as the copy to build from** — it's a
label for navigating the layer tree, not a content source. Always pull the actual text from a
successful `get_design_context` call (or, if that hard-fails per the gotcha above, from the
node's real rendered pixels via `get_screenshot`) before writing it into the HTML.

**This extends to whole wrapper *groups*, not just leaf text nodes.** Confirmed real case: a
card's outer group was named "Creative Producer," and its real rendered content (title,
description, and the illustration itself) was ALSO "Creative Producer" — internally consistent,
but reading unmistakably as marketing-production copy sitting inside an otherwise HR-themed
section, next to two other cards ("Candidate Sourcer," "Resume Screener") that were genuinely
HR-consistent. One sibling card's own group was named "Asset Generator" but its real title was
the HR-correct "Candidate Sourcer" — while its illustration was still the marketing content.
This pattern (a stale/mismatched group name, AND/OR stale content that was never fully
re-authored when a section template got reused for a different persona/page) is a real content-
accuracy signal, not just a naming annoyance — when one item in an otherwise-consistent list
reads as thematically out of place, that's worth flagging to the user as a likely source-file
error (per `ASK-DONT-GUESS.md`'s spirit) rather than silently reproducing it without comment or
silently "fixing" it by inventing replacement copy.

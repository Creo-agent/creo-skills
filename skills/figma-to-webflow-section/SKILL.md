---
name: figma-to-webflow-section
description: >-
  Build any Figma design section into a Webflow page headlessly via the Webflow
  Data API — heroes, feature grids, pricing, testimonials, navs, footers, CTAs,
  card rows, and more. Handles the full pipeline: reading the design, extracting
  tokens, uploading assets, creating styles, building the DOM, and adding
  responsive behavior plus interactions (hover, focus, click, scroll, entrance
  and ambient animation). Use this skill whenever the user shares a Figma URL
  and wants it built, implemented, recreated, or "made real" in Webflow — even
  if they only say "build this in Webflow", "implement this design", or paste a
  figma.com link with a Webflow site in context. It encodes the non-obvious
  Webflow Data API behavior (silent breakpoint failures, longhand-only styles,
  the freeform-code path for responsive CSS, the two-step asset upload) that
  otherwise costs many failed calls to rediscover.
---

# Figma → Webflow Section Builder

Recreate a Figma design section inside a Webflow page, working **headlessly**
through the Webflow Data API MCP tools. The output is a pixel-faithful,
responsive, interactive section — correct assets, typography, animations, and
zero horizontal overflow — built without a Designer canvas open.

This skill exists because the Webflow Data API has a handful of non-obvious
behaviors (some tools silently do the wrong thing) that are expensive to
rediscover each time. The reference files capture that hard-won knowledge so a
run gets it right on the first pass.

**Not for:** embedding a pre-built standalone HTML/CSS/JS animation prototype
(e.g. a Figma-derived motion file someone hands you as a `.html` file) into an
existing Webflow section — use
[`animation-to-webflow`](../animation-to-webflow/SKILL.md) for that. That
skill covers the JS DOM-builder pattern needed to survive Webflow's HTML
sanitization, which this skill's interaction phase doesn't.

---

## Before you start: read the map

You don't need every reference file loaded at once — that's the point of
splitting them out. But **read `references/webflow-data-api.md` and
`references/api-gotchas.md` before making any Webflow API calls this session.**
Those two contain the envelope format, the tool signatures, and the silent
failures. Skipping them is the single biggest source of wasted calls.

The other reference files are pulled in per-phase, called out in `PROMPT.md`.

| File | When to read it |
|---|---|
| `references/webflow-data-api.md` | Before any API call — envelope format, tool signatures, action shapes |
| `references/api-gotchas.md` | Before any API call — silent failures and their workarounds |
| [`../../knowledge/webflow-mcp/tools-index.md`](../../knowledge/webflow-mcp/tools-index.md) | When `webflow-data-api.md`'s cheat sheet doesn't cover a tool/action you need — full per-tool, per-action parameter reference for every Webflow MCP tool |
| `references/asset-pipeline.md` | Phase 3, before uploading any image |
| `references/webflow-styles.md` | Phase 4, before creating styles |
| `references/interaction-patterns.md` | Phase 2.5 and Phase 6 — element → interaction recipes |
| `references/responsive-patterns.md` | Phase 6 — viewport fill, pill scroll, media queries |
| `references/section-types.md` | Phase 2 — per-section-type watch-outs |
| `references/webflow-active-states.md` | Phase 4 and Phase 6 — active/selected state patterns; read before building any tabs, pills, or nav |
| `scripts/logo-fix.py` | Phase 3, only if a logo has a non-transparent background |

## Security constraint

Only build into Webflow sites the user owns or has authorized. Only touch
GitHub repos under the **dapulse** or **mondaycom** orgs unless the user grants
explicit permission for another repo. Do not publish a site without the user
asking.

---

## Workflow summary

1. **Pre-flight** — confirm Webflow IDs (`site_id`/`page_id`/insertion parent) and Figma `fileKey`/`nodeId`; screenshot the Figma node as ground truth; scan the page for existing interactive patterns to reuse.
2. **Design analysis** — classify the section type; extract backgrounds, typography, color tokens, percentage-based positions, and asset list.
3. **Interaction audit** — produce a plain-language Interaction Brief (element → hover/focus/click/scroll/entrance behavior) and confirm it with the user before writing CSS.
4. **Asset pipeline** — download each Figma asset and upload it to Webflow immediately (URLs expire fast); fix non-transparent logo backgrounds first.
5. **Style system** — create every class up front, longhand properties only, namespaced per section; no responsive styles here.
6. **DOM construction** — build the tree in one nested call; use `TextLink` for anything needing `set_text`; wire images by asset ID.
7. **Responsive + interactions** — all CSS (including media queries) goes in head freeform code; all JS goes in a body `HtmlEmbed` (head scripts don't run in Webflow preview).
8. **QA** — test every interaction in preview first, then screenshot at 1440/1024/768/375 and compare against the Figma screenshot.
9. **Publish** — only when the user asks, with `site_id` inside the action object.

See **[`PROMPT.md`](PROMPT.md)** for the complete phase-by-phase procedure, code
patterns, and QA checklist.

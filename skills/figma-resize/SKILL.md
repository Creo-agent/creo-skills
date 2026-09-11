---
name: figma-resize
description: >
  Resizes a Master Key Visual (KV) frame in Figma into native Figma frame variants at social ad
  placements — Story/Reel 1080×1920, Facebook Feed 1080×1350, LinkedIn Feed 1200×1200 — by
  cloning the master and repositioning/rescaling its real elements through the Figma Plugin API.
  Also produces a Reddit comment-style crop (1440×1080) via a distinct crop-only workflow. The
  master is the source of truth for every value; the placement spec is the source of truth for
  every position. Runs a mandatory three-layer QA gate on each placement as it is built
  (side-by-side vision comparison + a numeric measurement diff against the recorded master
  baseline + an element-zoom pass), including size floors on microcopy/CTA text, a WCAG contrast
  recheck, and CTA inclusion that follows the master rather than a fixed default — a placement is
  not done until zero hard rules fail. Use this skill whenever the user wants to resize a KV or
  master design, adapt a design to a different aspect ratio, produce story / reel / feed /
  comment-crop formats, generate social creatives or size variants from an existing Figma frame,
  or asks for "all the sizes" from a master — even when they don't name Figma explicitly.
---

# Figma Resize — Master KV to Social Placement Variants

Takes a Master Key Visual frame and produces native Figma frames at social placement sizes.
Output is always real Figma frames created by `use_figma` in the open document — never images,
never a rebuild from pixels.

## The governing principle

**The master KV is the source of truth for every _value_. The placement spec is the source of
truth for every _position_.**

Values — colours, fonts, text, gradients, shadows, opacity, icon set, element proportions — come
from the master and must survive the transform unchanged. Positions, canvas size and safe zones
come from the placement spec in `placements.json`, never from memory.

This matters because of *how* output is produced: **the output frame is a clone of the master,
then transformed.** Nothing is translated into a new medium and nothing is rebuilt. That single
fact determines the entire failure profile of this skill:

- `clone()` already preserves fonts, text, colours, effects and icons. Checks that merely
  re-assert those are near-guaranteed to pass, and a QA pass built from them *feels* thorough
  while the real defects sail through.
- What actually breaks is the **transform**: non-uniform scaling that squashes elements, image
  rects drifting out of their mask groups, `imageTransform` matrices going non-uniform on CROP
  fills, descendants landing off-canvas or inside a reserved safe zone.
- Those defects are arithmetic on node properties, and **three of the four are close to
  invisible in a full-frame screenshot.** A 0.99-vs-1.09 transform scale on a 120px avatar
  inside a 1920px frame is a couple of pixels of distortion — nothing to the eye, glaring as a
  number.

So in this skill, unlike a design-to-code skill, **the measurement pass catches the primary
failure class and vision catches the residue.** Both run. Neither substitutes for the other.

## Four non-negotiables

1. **Measure before you transform; diff after.** Run `scripts/measure_frame.js` on the master
   *before any clone exists* and keep the result as the session baseline. Every placement is
   verified by re-measuring the output and diffing against that recorded number — not against a
   recollection of it. See `PRE-RESIZE-MEASUREMENT.md`.
2. **The per-placement gate is mandatory, all three layers, as each size is built** — never
   batched to the end, never reduced to "it looks right." A placement is DONE **iff zero hard
   rules fail.** See `ACCURACY-GATE.md`.
3. **The geometry post-passes are not optional cleanup.** `fix_mask_images.js` (R7) and
   `fix_crop_transform.js` (R8) run on every placement, every time. They exist because both bugs
   shipped in production builds that passed every other check.
4. **When the design doesn't say, ask — never invent.** Converting 1:1 to 9:16 leaves real dead
   space. Filling it with invented elements is the single most tempting wrong move in this skill.
   See `ASK-DONT-GUESS.md`.

## Process discipline

**This skill is a checklist, not a suggestion list.** One placement at a time: build it, gate it,
show it, get approval, then start the next. Never batch several sizes into one `use_figma` run —
a failed batch gives you N broken frames and no way to tell which step caused it.

Per-placement audit, run mentally before calling a size done:

- ☐ Did I load the placement spec from `placements.json` rather than recall its numbers?
- ☐ Do I have a master baseline measurement from *before* the clone?
- ☐ Did I use `uScale = √(scaleX × scaleY)` for element size, per-axis only for position? (R1–R3)
- ☐ Did both geometry post-passes actually run? (R7, R8)
- ☐ Did I sweep for off-canvas and safe-zone violations on `absoluteBoundingBox`? (R24, R25)
- ☐ Did all three gate layers run, and did I report the numbers?

If any box is unchecked, the placement is not done.

## Supported placements

Every placement carries an `operationType` — `resize` (clone the whole composition and
transform it) or `crop` (extract one fragment, discard the rest). The two run through entirely
different engines; check this before doing anything else with a placement.

| Placement | Operation | Canvas | Frame name |
|---|---|---|---|
| Story / Reel | `resize` | 1080×1920 | `1080×1920 STORY` |
| Facebook Feed | `resize` | 1080×1350 | `1080×1350 FB` |
| LinkedIn Feed | `resize` | 1200×1200 | `1200×1200 LI` |
| Reddit Comment-Style | **`crop`** | 1440×1080 | `1440×1080 REDDIT-COMMENT` |

Exact numbers (including safe zones) live in `reference/placements.json`; the reasoning and
per-placement layout order live in `reference/PLACEMENTS.md`. **Never work from this table or
from memory** — Story's own safe zone has already changed twice, most recently to the team's own
tested figures rather than the platform's published guidance. Read the JSON every time.

`resize` placements run `RESIZE-WORKFLOW.md`'s ten-step engine. `REDDIT_COMMENT` runs
`REDDIT-COMMENT-WORKFLOW.md` instead — a six-step crop process that shares almost none of the
resize engine's steps, because it isn't building a composition at all.

## Out of scope

**Display advertising (DV) sizes were deliberately removed** — 970×250, 728×90, 300×250,
300×600, 160×600. If the user asks for one, say plainly that this skill now covers social
placements only and ask whether they want it added back, rather than improvising a layout.

Route elsewhere:
- AI image-generation resize with no Figma involved → `resize-with-nano-banana`
- Changing content, text or colours in a Figma design → `figma-modify`
- Layout/composition repair after an edit → `figma-recompose`
- Resizing an existing web animation → `resize-animation`

## Requirements

- **A Figma URL is mandatory.** If the user hasn't given one, stop and ask before anything else.
  It must point at the master KV frame (`.../design/:fileKey/...?node-id=...`).
- Convert the node id from the URL's hyphen form to a colon: `node-id=47-1515` → `47:1515`.
- A **Full Figma seat** — Dev seats are read-only and `use_figma` fails on them.
- The Figma MCP server connected and answering `get_metadata` on the target file.

## Preflight

1. Confirm the Figma plugin is present: `claude plugin list 2>/dev/null | grep -i figma`
   (install with `claude plugin install figma@claude-plugins-official`).
2. Load the mandatory prerequisite skill — **required before every `use_figma` call:**
   `Skill({ skill: "figma:figma-use" })`. If it asks what the output should be, the answer is
   always **"Figma Plugin JS (use_figma)"** — answer it yourself, don't surface it to the user.
3. Load the Figma MCP tools:
   `ToolSearch({ query: "select:mcp__figma-write__get_screenshot,mcp__figma-write__get_metadata,mcp__figma-write__use_figma" })`
   If any fail to resolve, tell the user the Figma MCP server isn't connected and stop.

## What this skill does, at a glance

1. Preflight, then extract `fileKey` + `nodeId` and screenshot the master to confirm the frame.
2. Confirm which placements to build and in what order (never assume "all").
3. **Measure the master once** → session baseline (`PRE-RESIZE-MEASUREMENT.md`).
4. Per placement, run the ten-step engine in `RESIZE-WORKFLOW.md`: brief → plan → clone → resize
   canvas → geometry pass → placement layout → geometry post-passes → bounds enforcement → gate
   → deliver.
5. The gate is three layers and binary: vision, measurement diff, element zoom; zero hard-rule
   failures or it isn't done (`ACCURACY-GATE.md`, scored per `QA-SCORECARD.md`).
6. Deliver each placement with its screenshot, its QA report, and any accepted gaps stated by
   name — never silently smoothed over.

## Reference files

| File | When to read it |
|---|---|
| [`HARD-RULES.md`](reference/HARD-RULES.md) | Always — R1–R46, non-negotiable, each with its owner and the defect behind it |
| [`RESIZE-WORKFLOW.md`](reference/RESIZE-WORKFLOW.md) | `resize`-type placements only — the per-placement engine, Steps 0–10 — read this first |
| [`REDDIT-COMMENT-WORKFLOW.md`](reference/REDDIT-COMMENT-WORKFLOW.md) | `crop`-type placements only (REDDIT_COMMENT) — a different six-step engine, not a resize |
| [`BATCH-WORKFLOW.md`](reference/BATCH-WORKFLOW.md) | Multiple placements in one session — a thin loop over the engine |
| [`PRE-RESIZE-MEASUREMENT.md`](reference/PRE-RESIZE-MEASUREMENT.md) | **Before any clone exists** — how to record the master baseline |
| [`PLACEMENTS.md`](reference/PLACEMENTS.md) | Per-placement reasoning, layout order, size-unique rules |
| [`placements.json`](reference/placements.json) | The per-placement numbers — the only source for canvas size and safe zones |
| [`ACCURACY-GATE.md`](reference/ACCURACY-GATE.md) | Per placement, at Step 9 — the three-layer gate |
| [`QA-SCORECARD.md`](reference/QA-SCORECARD.md) | The scoring rubric and QA report format |
| [`resize-rules.csv`](reference/resize-rules.csv) | The pass/fail authority — `severity` decides DONE, `owner` says who checks it |
| [`QA-CHECKLIST-ALIGNMENT.md`](reference/QA-CHECKLIST-ALIGNMENT.md) | Traceability matrix against the source Ad-Specific QA Checklist — what's implemented, pending, or out of scope, and why |
| [`ASK-DONT-GUESS.md`](reference/ASK-DONT-GUESS.md) | The moment the design doesn't specify something — especially dead space |
| [`GOTCHAS.md`](reference/GOTCHAS.md) | Figma API bugs already diagnosed — check here before debugging one yourself |
| [`scripts/measure_frame.js`](scripts/measure_frame.js) | Steps 2 and 9b — the measurement probe, run on master and on every output |
| [`scripts/resize_qa_diff.py`](scripts/resize_qa_diff.py) | Step 9b — diffs output against the master baseline and placement spec |
| [`scripts/fix_mask_images.js`](scripts/fix_mask_images.js) | Step 7 — R5–R7 mask-group image alignment post-pass |
| [`scripts/fix_crop_transform.js`](scripts/fix_crop_transform.js) | Step 7 — R8 CROP `imageTransform` squash post-pass |

## Closing step: knowledge capture

At the end of a session, review what was learned and classify it:

- **Already documented** in `HARD-RULES.md` / `GOTCHAS.md` / `PLACEMENTS.md` → skip, cite where.
- **A placement number** → it belongs in `placements.json`, not in prose.
- **Genuinely new** — a Figma API bug, a transform failure mode, a judgment call worth keeping →
  propose it.

For every proposed item, ask in **one batched question** whether to write it into the specific
file it belongs in, phrased as a general principle rather than a note about today's KV. Never
write without that consent, and never write to personal `~/.claude` memory from this step — only
this skill's own bundled files, so the next person who uses the skill inherits it too.

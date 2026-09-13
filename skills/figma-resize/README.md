# Figma Resize — Master KV to Social Placement Variants

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that takes a Master Key
Visual (KV) frame in Figma and produces native Figma frame variants at social ad placements. It
clones the master and repositions/rescales its real elements through the Figma Plugin API — no
image export, no rebuild from pixels.

Every placement passes a mandatory three-layer QA gate as it is built, and is not considered done
until zero hard rules fail.

## Supported placements

| Placement | Operation | Canvas | Frame name | Safe zone | Source |
|---|---|---|---|---|---|
| Story / Reel | `resize` | 1080×1920 | `1080×1920 STORY` | 10.4% top · 28.1% bottom · 6% sides | internal-tested |
| Facebook Feed | `resize` | 1080×1350 | `1080×1350 FB` | 10% top/bottom · 6% sides | derived (crop survival) |
| LinkedIn Feed | `resize` | 1200×1200 | `1200×1200 LI` | 6% all sides | Creo house standard |
| Reddit Comment-Style | **`crop`** | 1440×1080 | `1440×1080 REDDIT-COMMENT` | none | — |

Exact figures live in [`reference/placements.json`](reference/placements.json) — that file is the
only source the skill reads. Display advertising (DV) sizes were deliberately removed; see
[Scope](#scope). Every placement carries an `operationType`: `resize` clones the whole composition
and transforms it; `crop` extracts one fragment of one element and discards the rest — a
fundamentally different engine (`REDDIT-COMMENT-WORKFLOW.md`, not `RESIZE-WORKFLOW.md`).

## The idea

**The master owns every value. The placement spec owns every position.**

Colours, fonts, text, gradients, shadows, the icon set, element proportions — all come from the
master and must survive the transform unchanged. Canvas size, safe zones and layout order come
from the spec file.

This matters because of *how* the output is made. **The output frame is a clone of the master,
then transformed.** Nothing is translated into another medium and nothing is rebuilt, which
inverts the usual failure profile:

- `clone()` already preserves fonts, text, colours, effects and icons. Checks that merely
  re-assert those are near-guaranteed to pass — and a QA pass built from them *feels* thorough
  while the real defects go through untouched.
- What actually breaks is the **transform**: non-uniform scaling that squashes elements, image
  rects drifting out of their mask groups, `imageTransform` going non-uniform on CROP fills,
  descendants landing off-canvas or inside a reserved safe zone.
- Three of those four are close to invisible in a full-frame screenshot. A 0.99-vs-1.09 transform
  scale on a 120px avatar inside a 1920px frame is a couple of pixels of distortion.

So unlike a design-to-code skill, here **the measurement pass catches the primary failure class
and vision catches the residue.** Both run; neither substitutes for the other.

## How it works

Ten steps per placement, one placement at a time:

| Step | | Step | |
|---|---|---|---|
| 0 | Load the placement spec | 5 | Geometry pass (uniform size, per-axis position) |
| 1 | Confirm the per-placement brief | 6 | Placement layout |
| 2 | Measure the master → baseline | 7 | Geometry post-passes (mask, CROP transform) |
| 3 | State the plan | 8 | Bounds enforcement |
| 4 | Clone + resize the canvas | 9 | **The gate** |
| | | 10 | Deliver, await approval |

### The gate

Three layers, all mandatory, in this order:

1. **Vision** — master and output side by side, actually looked at. Runs first so the visual read
   is independent, before diff numbers anchor where you look.
2. **Measurement diff** — re-measure the output, diff against the recorded master baseline and the
   placement spec. Emits `expected`/`measured` pairs per rule. **This is the primary layer.**
3. **Element zoom** — individual small nodes captured at high scale and inspected. Catches a blank
   asset with correct dimensions, a wrong crop, a glyph standing in for a real icon.

**Verdict is binary: a placement is DONE iff zero hard rules fail.** No averaging, no score that
lets small passes offset a serious failure. Soft findings are logged as weighted findings.

A clean script run reports the rules it did *not* check, read live from the rules file — so it can
never be mistaken for a complete QA.

## Architecture

```
figma-resize/
├── SKILL.md                          principle, non-negotiables, reference table
├── reference/
│   ├── HARD-RULES.md                 R1–R46, each with its owner and the defect behind it
│   ├── RESIZE-WORKFLOW.md            the per-placement resize engine (Steps 0–10)
│   ├── REDDIT-COMMENT-WORKFLOW.md    the distinct crop engine (Steps 1–6) — not a resize
│   ├── BATCH-WORKFLOW.md             thin loop for several placements + consistency pass
│   ├── PRE-RESIZE-MEASUREMENT.md     the measurement contract; measure before any clone exists
│   ├── ACCURACY-GATE.md              the three-layer gate
│   ├── QA-SCORECARD.md               rubric + report format
│   ├── resize-rules.csv              pass/fail authority — 42 rules, severity + weight + owner
│   ├── PLACEMENTS.md                 per-placement reasoning and size-unique rules
│   ├── placements.json               the numbers (safe zones computed from percentages)
│   ├── QA-CHECKLIST-ALIGNMENT.md     traceability matrix against the source ad-QA checklist doc
│   ├── ASK-DONT-GUESS.md             halt conditions
│   └── GOTCHAS.md                    Figma API behaviours already diagnosed
└── scripts/
    ├── measure_frame.js              the probe — run on master, run on every output
    ├── resize_qa_diff.py             the diff — 29 rule checks (28 resize-only + 1 crop-only), stdlib only
    ├── fix_mask_images.js            mask-group image realignment (R5/R7)
    └── fix_crop_transform.js         CROP imageTransform repair (R8)
```

**Rules are prose + severity + owner; values are data.** `resize-rules.csv` decides pass/fail and
names who checks each rule (`script` or `vision`), which is what makes "this was never checked at
all" structurally impossible. `placements.json` holds every number, so per-placement differences
are parameters rather than three near-copies of the same rule set.

**46 rules · 42 CSV rows · 35 hard / 7 soft · 29 script-owned / 13 vision-owned.**

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Figma MCP connected, answering `get_metadata` on the target file
- The `figma:figma-use` skill (`claude plugin install figma@claude-plugins-official`) — a hard
  prerequisite before every `use_figma` call
- **A Full Figma seat.** Dev seats are read-only; write tools fail with a permission error
- Python 3 for the diff script (stdlib only — no install step)

## Installation

```bash
cp -r figma-resize ~/.claude/skills/
```

Self-contained — no companion skill required.

## Usage

Provide a Figma URL pointing at the master frame:

```
Resize this KV to the story and LinkedIn sizes:
https://figma.com/design/ABC123/my-design?node-id=1:2
```

Also triggers on: "adapt this master to social sizes", "make the story format", "create the size
variants", "generate the feed placements".

The skill confirms which placements and in what order, measures the master once, then works
through them one at a time — screenshot plus QA report for each, waiting for approval before
starting the next.

## Scope

**Covers:** Story/Reel, Facebook Feed and LinkedIn Feed placements from a Figma master (all
`resize`-type), plus a Reddit comment-style crop (`crop`-type — a genuinely different operation,
see `REDDIT-COMMENT-WORKFLOW.md`). Reddit feed and Google DV360 are documented as on hold, not
implemented.

**Display advertising (DV) sizes were deliberately removed** — 970×250, 728×90, 300×250, 300×600,
160×600. If asked for one, the skill says so rather than improvising a layout.

**Routes elsewhere:** AI image-generation resize with no Figma involved → `resize-with-nano-banana`
· changing content/text/colours → `figma-modify` · layout repair after an edit →
`figma-recompose` · resizing a web animation → `resize-animation`.

## Notable corrections in this version

Four things the previous version had wrong, found while rebuilding and verifying:

- **Story bottom safe zone: 21% → 35%.** Meta specifies 14% top / 35% bottom / 6% sides
  identically for Facebook Stories, Instagram Stories and Reels image ads. The old 403px value
  treated **269px of Meta-reserved space as usable**, so Story frames built against it may have a
  headline, logo or CTA sitting behind the platform CTA on a real device.
- **The dead-space claim was wrong twice over.** The old docs said a 1:1 master reaching 9:16
  "always creates ~400–450px of dead space." It was measured against the superseded usable band,
  and the corrected usable area is nearly square (950×979) — so a 1:1 master leaves **29px**. The
  ~445px figure actually corresponds to a **16:9** master. Dead space is a landscape-master
  problem, not an inherent Story problem.
- **The documented k-factor formula for mask realignment appears inverted** — it multiplies the
  canvas delta by the wrapper scale where it should divide, an `s²` error.
  `fix_mask_images.js` avoids depending on the direction: apply, re-measure, repeat until it
  converges.
- **The geometry pass and the bounds pass are two halves of one operation.** Going 1080×1350 →
  1080×1920, `scaleX` is exactly 1.000 while `uScale` is 1.193 — every element grows ~19% wider on
  a canvas that gained no width, so anything wider than ~906px overflows *by construction*.

The previous version also carried a "post-pipeline cleanup" step instructing the agent to run
`ps aux | grep -i claude` and shut down matching processes. It has been removed: the skill never
starts separate sessions, and that command matches any Claude Code process including the live one.

## Ad-Specific QA Checklist alignment (2026-09-01)

A second pass aligned the skill against a team-authored Ad-Specific QA Checklist (Rachel) —
[`reference/QA-CHECKLIST-ALIGNMENT.md`](reference/QA-CHECKLIST-ALIGNMENT.md) is the full
traceability matrix, item by item. Highlights:

- **Added 15 new rules (R32–R46)**: minimum text sizes for microcopy (28px) and CTA labels
  (36px), a WCAG contrast recheck triggered by any background/position/size change, CTA
  inclusion that follows the master instead of a fixed per-placement default (with Story's native
  platform CTA as a hard exception), an absolute minimum-clearance floor independent of
  proportional scaling, and a full rule set for the new crop-type placement.
- **Story's safe zone changed source, not just value.** The team's own tested figures (200px
  top / 540px bottom) superseded the platform-published guidance used since the previous pass
  (269px / 672px) — a real, meaningful difference, not a refinement. Every downstream number
  (usable area, the dead-space fit table, example text) was recomputed rather than patched.
  The dead-space conclusion changed with it: the usable area is now portrait (0.805 ratio, not
  0.970), so even a 1:1 master leaves ~230px of real dead space — the earlier "close to a clean
  fit" finding no longer holds.
- **Added a fourth placement, Reddit comment-style, as a `crop` operation** — the skill's first
  placement that doesn't clone a whole composition. It has its own workflow file, its own rule
  set, and is explicitly *not* run through the resize engine.
- **A testing-only finding, not from the source doc:** TEXT nodes were excluded from the
  aspect-ratio geometry check (R1) — a text box's bounding-box ratio changes naturally with
  content and font size, which isn't the squashing defect that check exists to catch. Found by
  building a fixture with a real CTA label, not anticipated in advance.

## License

MIT

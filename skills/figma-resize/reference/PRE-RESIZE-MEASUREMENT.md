# Pre-Resize Measurement — Record the Baseline Before Anything Exists

## Contents
- Why this file exists
- The rule
- What gets measured
- The measurement contract (schema)
- Node matching — why index paths, not names
- Running it
- Caching and invalidation
- What a valid baseline contains
- What this replaces

---

## Why this file exists

Every defect this skill actually ships is a **transform** defect: an element squashed by
per-axis scaling, an image rect drifted out of its mask, a CROP fill gone non-uniform, a
descendant landing off-canvas. All four are arithmetic on node properties, and three of the four
are close to invisible in a full-frame screenshot.

You cannot diff arithmetic against a memory. If the master's numbers were never recorded, the
only thing available after the resize is a second opinion formed after the fact — and two frames
can look equally plausible while differing in every number that matters.

So: **measure the master before a clone exists, keep the result, and diff against it.** The
baseline is what turns "does this look right?" into "this node's aspect ratio moved by 9%."

The old workflow asked the model to hand-transcribe roughly fifteen categories of master values
into prose — fonts, colours, gradients, shadows, positions, gaps, opacity. That is unreliable
(transcription drops things), expensive (it burns context on data), and useless downstream
(nothing can diff against a paragraph). One script run replaces all of it.

## The rule

**Measure the master once per session, before any clone exists.** Every placement is verified
against that same recorded baseline — not against a fresh reading, and never against another
output frame.

This is R-adjacent process discipline, enforced by the gate: `resize_qa_diff.py` refuses to run
without a baseline whose `role` is `master`.

## What gets measured

`scripts/measure_frame.js` walks the frame recursively and records, for every node:

| Group | Fields |
|---|---|
| Identity | `path` (index path), `id`, `name`, `type`, `depth` |
| Geometry | `abs` (absoluteBoundingBox), `local` (x/y/width/height), `rotation` |
| Presentation | `opacity`, `visible`, `isMask`, `cornerRadius` |
| Paint | `fills[]` (type, hex, opacity, gradient transform + stops), `strokes[]` |
| Effects | `effects[]` (type, offset, radius, spread, colour) |
| Text | `characters`, `fontFamily`, `fontStyle`, `fontSize`, `letterSpacing`, `lineHeight`, `textAutoResize` |
| Image | `scaleMode`, `imageHash`, `imageTransform`, plus extracted `transformScaleX` / `transformScaleY` |

Plus a `derived` block computed once so the differ doesn't have to re-derive it: mask-group
pairings, per-node aspect ratios, text-node count, and logo/icon candidates.

## The measurement contract (schema)

```json
{
  "meta": {
    "fileKey": "AbCdEfGhIjKl",
    "nodeId": "47:1515",
    "frameName": "Master KV",
    "parentName": "Page 1",
    "role": "master",
    "placement": null,
    "frameAbs": { "x": 0, "y": 0, "width": 1080, "height": 1350 }
  },
  "nodes": [
    {
      "path": "0/2/1",
      "id": "47:1600",
      "name": "Headline",
      "type": "TEXT",
      "depth": 2,
      "abs":   { "x": 120, "y": 240, "width": 840, "height": 180 },
      "local": { "x": 120, "y": 240, "width": 840, "height": 180 },
      "rotation": 0,
      "opacity": 1,
      "visible": true,
      "isMask": false,
      "cornerRadius": 0,
      "fills": [{ "type": "SOLID", "hex": "#181B34", "opacity": 1 }],
      "strokes": [],
      "effects": [],
      "text": {
        "characters": "Work without limits",
        "fontFamily": "Poppins",
        "fontStyle": "Semi Bold",
        "fontSize": 64,
        "letterSpacing": { "unit": "PERCENT", "value": -2 },
        "lineHeight":    { "unit": "PERCENT", "value": 110 },
        "textAutoResize": "HEIGHT"
      },
      "image": null
    }
  ],
  "derived": {
    "maskGroups": [
      { "path": "0/3", "maskPath": "0/3/0", "imagePath": "0/3/1",
        "absDelta": { "x": 0, "y": 0 } }
    ],
    "aspectRatios": { "0/2/1": 4.6667 },
    "textNodeCount": 6,
    "logoCandidates": ["0/0"],
    "iconCandidates": ["0/4/0", "0/4/1", "0/4/2"],
    "ctaCandidates": ["0/5"],
    "ctaLabelCandidates": ["0/5/0"],
    "headlineCandidates": ["0/2/1"]
  }
}
```

**Added 2026-09-01** for R32/R33/R38 (microcopy and CTA size floors, CTA-follows-master):
`ctaCandidates` (name-based — a frame/component named "cta"/"button"/"capsule"),
`ctaLabelCandidates` (the TEXT node nested inside a CTA candidate — the label itself, which is
what R33's size floor actually measures), `headlineCandidates` (name-based, or the TEXT node(s)
at the master's single largest font size when no name says "headline" — this is the operational
definition of "the dominant H1" that R34 checks against). Same caveat as `logoCandidates`: these
are suggestions the workflow confirms with the user when ambiguous, never a silent decision.

`role` is `"master"` for the baseline and `"output"` for a resized frame. `placement` is `null`
on the master and the placement key (`STORY` / `FB` / `LI`) on an output. The differ validates
both before comparing anything — comparing two outputs, or a master against itself, is a silent
way to produce a clean report that means nothing.

## Node matching — why index paths, not names

To diff master against output, nodes must be paired across two trees. **Pair them by structural
index path** — `"0/2/1"` meaning root child 0 → its child 2 → its child 1 — with `name` as a
secondary assertion.

This matters more than it looks. Figma layer names duplicate constantly: a frame can hold eight
nodes called `Rectangle 5`. Matching by name pairs the wrong nodes, and the resulting report is
not empty — it is **confidently wrong**, reporting aspect-ratio failures on elements that are
fine and passing ones that are broken. A wrong report is worse than no report, because it gets
acted on.

The output is a clone, so structure is identical by construction and paths line up exactly. Two
consequences:

- **A path that exists in the master but not the output** means an element was deleted or hidden.
  That is a finding (R11/R16), not a matching error — report it, don't silently skip it.
- **If a large share of paths fail to match**, something structural changed. Stop and investigate
  rather than reporting on the subset that happened to line up.

When a path matches but the `name` differs, record it as a warning: the geometry comparison is
still valid, but a renamed node usually means someone restructured something.

## Running it

The probe runs inside Figma through `use_figma`, which means loading the mandatory prerequisite
skill first:

```
Skill({ skill: "figma:figma-use" })
```

Then pass the contents of `scripts/measure_frame.js` as the code body, with the target node id
and the role set. Write the returned JSON to the session's working directory:

```
<deliverables>/measure-master.json          # role: master, once per session
<deliverables>/measure-<placement>-v<NN>.json  # role: output, once per gate run
```

Keep them as files. The baseline has to survive across placements, and a fix pass needs to
re-measure without re-reading the master.

## Caching and invalidation

**Measure the master once per session and reuse it for every placement.** Re-measuring per
placement wastes a round trip and, worse, risks measuring a master that someone has edited
mid-session — which would silently move the baseline and make earlier placements look wrong.

Re-measure only when:

- the user edits the master mid-session (they will usually say so — if a screenshot looks
  different from the one captured at the start, ask)
- the session resumes after a context summary and no `measure-master.json` is on disk
- the master node id changes because the user pointed at a different frame

After any re-measure, previously-approved placements were gated against the old baseline. Say so
rather than quietly carrying the approval forward.

## What a valid baseline contains

Before starting any placement, confirm the baseline actually holds what the gate will need:

- ☐ `meta.role === "master"` and `meta.frameAbs.width/height` match the master's real dimensions
- ☐ `nodes[]` is non-empty and its depth reaches the leaves — a baseline that stopped at direct
  children cannot check R25 (off-canvas descendants) or R16 (icon count)
- ☐ every TEXT node has `characters` populated — this is what R12's text diff compares against
- ☐ `derived.maskGroups` is present, even if empty; an absent key means the probe failed rather
  than the frame having no masks, and R7 would then be unverifiable
- ☐ any image fill in CROP mode has `imageTransform` recorded — R8 cannot be checked without it

A baseline missing any of these is not a baseline. Re-run the probe rather than proceeding and
discovering the gap at gate time.

## What this replaces

The previous Step 2 instructed the model to record, in prose: frame dimensions, layout mode,
top-level children by role, font families and weights, text colours per element, letter spacing
and line height, image container style, background type, gradient angles and stops, drop shadows,
overlay opacity, source element positions and sizes, source spacing measurements, and third-party
brand names.

All of it is now in the JSON, measured rather than observed, and — the part that matters — in a
form something can subtract later.

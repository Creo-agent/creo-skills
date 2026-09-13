# Accuracy Gate — The Per-Placement Verdict

## Contents
- The verdict
- Layer order: why "first" is not "primary"
- 9a — Vision comparison
- 9b — Measurement diff (the primary layer)
- 9c — Element zoom
- The fix loop
- Accepted gaps
- Logging

---

## The verdict

**`resize-rules.csv`'s `severity` column is the only pass/fail authority in this skill.**

> **A placement is DONE if and only if zero `hard`-severity rules fail.**
> Not "mostly done." Not "9/10." A placement with 29 of 30 rules passing and one failing hard
> rule is **NOT DONE** — no averaging, no offsetting a hard failure against unrelated successes.

`soft`-severity findings never block DONE. They are logged as weighted findings in the report,
neither silently passed nor silently dropped.

The only way past a failing hard rule is to **fix it**, or to record it as an **explicit accepted
gap with a stated reason** (see below). An accepted gap is a deliberate, named exception the user
has seen — never a quiet pass.

Every rule also carries an `owner` — `script` or `vision` — naming which layer checks it. That
column is what makes "this rule was never checked at all" structurally impossible rather than
something to remember.

## Layer order: why "first" is not "primary"

The three layers run **look → measure → zoom**. But the layer that runs first is not the layer
that matters most here, and conflating the two is how this gate gets misapplied.

In a design-to-code skill, vision is primary: the output is a translation into another medium, so
the eye is the instrument that catches mistranslation. **This skill is not that.** The output is
a *clone* of the master, so fonts, text, colours, effects and icons arrive intact for free. What
breaks is transform arithmetic — squashed elements, drifted mask images, non-uniform CROP
transforms, off-canvas descendants — and three of those four are close to invisible at full-frame
zoom. A 0.99-vs-1.09 transform scale on a 120px avatar inside a 1920px frame is a couple of
pixels of distortion.

So: **9b is the primary layer.** It catches the failure class that actually ships.

Vision still runs **first**, for a reason worth stating: an independent visual read, formed
before the numbers arrive, catches composition problems no rule enumerates — a placement that is
technically perfect and reads wrong. Once you have seen a diff report, your eye goes to the
flagged nodes and stops being independent. Look, then measure, then zoom.

## 9a — Vision comparison

1. Capture both frames: `get_screenshot` on the master node and on the output frame. Fetch both
   to disk immediately — these URLs expire fast.
   ```bash
   curl -sL -o "<deliverables>/<placement>-master-ref-v01.png" "<master_url>"
   curl -sL -o "<deliverables>/<placement>-output-v<NN>.png"   "<output_url>"
   ```
2. **Actually look at both, side by side.** Score the `vision`-owned rules in `resize-rules.csv`.
3. Ask the questions no script can: does the composition read as intentional or scattered? Is the
   reading order intact? Does it look like it came from the same campaign as the master?
4. If the master screenshot was never captured at session start, get it now. **Never score an
   output against a recollection of the master** — the side-by-side is the point.

A blank, all-white or obviously-wrong screenshot is not evidence of anything. Re-capture before
concluding anything from it.

## 9b — Measurement diff (the primary layer)

Re-measure the output and diff it against the recorded master baseline:

```bash
# 1. measure the output frame (use_figma + scripts/measure_frame.js, role: output)
#    → <deliverables>/measure-<placement>-v<NN>.json

# 2. diff against the baseline and the placement spec
python3 scripts/resize_qa_diff.py \
    --baseline  <deliverables>/measure-master.json \
    --output    <deliverables>/measure-<placement>-v<NN>.json \
    --placement STORY \
    --spec      reference/placements.json \
    --rules     reference/resize-rules.csv
```

This is a diff against a **recorded number**, not another opinion formed after the fact. That
distinction is the whole reason `PRE-RESIZE-MEASUREMENT.md` exists: two frames can look equally
plausible while differing in every value that matters, and looking is not good at arithmetic.

Output format — every finding scoped to its rule id and R-number, with an `expected`/`measured`
pair, so a defect always arrives with a number attached rather than a judgement call:

```
RESIZE QA — 1080×1920 STORY
baseline: measure-master.json (1080×1350)    output: measure-STORY-v01.json
nodes matched: 47/47

HARD RULES
  ✗ geometry_aspect_ratio_preserved    R1/R2/R9
      0/3/1  "Avatar 3"         expected 1.000    measured 1.094    Δ +9.4%
      0/3/4  "Avatar 5"         expected 1.000    measured 1.087    Δ +8.7%
  ✗ crop_transform_uniform             R8
      0/3/1  "Avatar 3"         expected X≈Y      measured X 0.993 / Y 1.089
  ✓ exact_dimensions                   R23       1080×1920
  ✓ safe_zone_respected                R24       all content within y 269–1517, x 65–1015
  ✓ text_content_verbatim              R12       6/6 text nodes identical
  ✓ no_offcanvas_elements              R25       0 of 47 nodes out of bounds
  … 15 more passing

SOFT FINDINGS
  ! spacing_proportional               R26
      text→visual gap    expected ≈0.83×    measured 1.41×

VISION-OWNED — NOT CHECKED HERE (9 rules)
  visual_not_cropped · no_invented_elements · cta_single_line · cta_solid_fill ·
  icon_style_unchanged · image_container_preserved · background_master_colors_only ·
  geometry_text_group_centered · composition_no_dead_space

VERDICT: NOT DONE — 2 hard rules failing
```

The `VISION-OWNED — NOT CHECKED HERE` block is read live from the CSV's `owner` column, not
hand-maintained. It exists so a clean script run can never be mistaken for a complete QA (R31).

## 9c — Element zoom

**A full-frame capture cannot verify anything much smaller than ~32px.** A 1920px-tall frame
rendered into a chat-sized image is a heavy downscale — a 24px integration chip lands on about
three pixels.

So before calling a placement done, capture individual small nodes and look at them:

```
get_screenshot(fileKey, <child node id>)     # the node, not the frame
```

One representative instance of each repeated component is enough: person bubbles, avatars,
integration marks, icon rows, badges, the logo, the CTA capsule.

**What only this layer catches:**

- a glyph or emoji standing in for a real icon (R16) — passes every numeric check and hides at
  frame zoom
- an asset that decoded but is **blank or fully transparent** — correct dimensions, no artwork
- a logo at the wrong crop
- 1–2px border or corner-radius drift
- a face crop that survived R8's transform fix numerically but framed badly

This layer is why R8's warning against converting CROP to FILL matters: FILL produces a
numerically clean transform and a visibly wrong crop. Only looking at the bubble catches it.

## The fix loop

1. Fix the failing hard rules.
2. **Re-run all three layers** — not just the one that failed. A geometry fix can move something
   else, and a re-run that checks only the previous failure will miss it.
3. Re-report.

**Two attempts, then stop.** After two failed fix passes on the same placement, present the
remaining failures and ask whether to skip the placement, try a different approach, or hand it
over. Grinding a third and fourth pass on the same defect reliably produces the same broken frame
more slowly.

## Accepted gaps

Some hard rules cannot be satisfied from the material available. The canonical case: converting a
1:1 master to 9:16 leaves roughly 400–450px of dead space below the visual, and no amount of care
will find source material for it (see `ASK-DONT-GUESS.md`).

An accepted gap requires all three of:

1. a **named rule** it fails,
2. a **stated reason** why it cannot be fixed from the master, and
3. the **user having seen it** — surfaced in the delivery reply, not buried in a report file.

Anything short of that is a silent pass. In particular, never resolve a gap by inventing an
element to fill it (R13) — that converts a visible, honest gap into an invisible fabrication.

## Logging

Every finding — fixed, accepted or skipped — goes into the placement's QA report
(`QA-SCORECARD.md` format), saved to the deliverables folder and shown in-session.

A gate run that finds nothing still gets a one-line confirmation that it ran. "Ran clean" and
"never ran" must be distinguishable to anyone reading the session later, including you after a
context summary.

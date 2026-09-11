# Hard Rules — Read Before Every Resize

## Contents

**Geometry & transform** — the mechanical laws of a clone-and-transform pipeline
- R1 — Never scale element size per-axis
- R2 — `uScale = √(scaleX × scaleY)` is the uniform factor
- R3 — Element *positions* use per-axis scale
- R4 — Text groups get explicit horizontal centering
- R5 — `group.resize()` does not preserve image rects inside nested mask groups
- R6 — Process direct children only
- R7 — Post-pass: realign mask-group image rects in absolute coordinates
- R8 — Post-pass: fix non-uniform `imageTransform` on CROP fills

**Content & brand integrity**
- R9 — Never rotate, never distort
- R10 — Never crop the visual to fit
- R11 — Logo integrity
- R12 — Never rewrite, paraphrase, or repeat text
- R13 — Never invent elements to fill dead space
- R14 — Brand preservation
- R15 — CTA stays a single horizontal line, solid fill
- R16 — Icons survive intact

**Visual fidelity** — mostly free via `clone()`, cheap to verify
- R17 — Fills and text colours unchanged
- R18 — Gradients preserved
- R19 — Effects preserved
- R20 — Opacity preserved
- R21 — Image container treatment preserved
- R22 — Typography preserved

**Layout, bounds & placement**
- R23 — Exact target dimensions, verified not assumed
- R24 — Placement safe zones come from `placements.json`
- R25 — No off-canvas descendants
- R26 — Spacing relationships preserved proportionally
- R27 — Background extended using only master colours
- R28 — Frame naming and parenting

**Process**
- R29 — One placement at a time
- R30 — All three gate layers run
- R31 — A clean measurement run is not "QA complete"

**Ad-Specific QA Checklist alignment** — new 2026-09-01, sourced from Rachel's Ad-Specific QA
Checklist doc (shared baseline, plus the resize-specific sections)
- R32 — Minimum microcopy size: 28px @1x
- R33 — Minimum CTA text size: 36px @1x
- R34 — Message hierarchy: H1/H2 line caps and minimum H2 size
- R35 — Never silently ship a shrink below the floor
- R36 — Overflowing copy gets alternatives offered, not silent overflow
- R37 — Newly added text is set in Poppins
- R38 — CTA inclusion follows the master, with a hard platform exception
- R39 — Line-count change forces a recompose, not a collision
- R40 — Contrast is rechecked whenever the task could have broken it
- R41 — Conflicting rules get flagged, not silently resolved
- R42 — An absolute minimum clearance floor, independent of proportionality

**Crop operations** — REDDIT_COMMENT only; do not apply these to a `resize`-type placement
- R43 — A crop placement contains only the cropped fragment
- R44 — Crop from the master's original visual, never from a placement's output
- R45 — The subject's focal point stays visible and centred
- R46 — A crop is a genuine sub-region, never the whole visual squeezed to fit

**Out of scope, noted for completeness — not rules this skill enforces:** the source doc's
Use-Case Adaptation section (message/tone fit for a new persona, CTA strength matching funnel
stage, claim accuracy in a new context) is content/messaging work, not geometry. It belongs in
whatever skill handles ad adaptation, not here — see `QA-CHECKLIST-ALIGNMENT.md`.

---

These are non-negotiable. They override any shortcut or heuristic in `RESIZE-WORKFLOW.md`,
`BATCH-WORKFLOW.md` or `PLACEMENTS.md`, and they apply identically to every placement.

Each rule carries an **Owner**:

- `script` — mechanized in `scripts/measure_frame.js` + `scripts/resize_qa_diff.py`. Cannot be
  silently skipped, because the diff prints an `expected`/`measured` pair for it.
- `vision` — the deliberately short list that only looking can settle.
- `process` — a rule about how the skill runs, not about a property of the output.

**Why the owners matter here specifically.** The output frame is a *clone* of the master, so
fonts, text, colours, effects and icons arrive intact for free. The defects that actually ship
are transform arithmetic — and most of them are close to invisible at full-frame zoom. That is
the opposite of a design-to-code skill, where the eye is the primary instrument. Here the eye is
the secondary one.

---

# Geometry & transform

## R1 — Never scale element size per-axis

**Owner:** script

Never do this:

```js
child.resize(child.width * scaleX, child.height * scaleY);   // WRONG
```

Applying the horizontal ratio to width and the vertical ratio to height squashes **every element
in the frame** the moment the source and target aspect ratios differ — which is every interesting
resize this skill performs. Faces stretch, logos flatten, circular avatars become ovals.

The check that catches it: for every matched node, the aspect-ratio delta between master and
output must be ≈ 1.0.

```
(w_out / h_out) ÷ (w_master / h_master) ≈ 1.0    tolerance ±0.01
```

`resize_qa_diff.py` runs this at every depth of the tree, which is what makes R1 impossible to
violate quietly. Before the diff existed, a squashed element was found only when somebody
happened to look closely at the right part of the frame.

**TEXT nodes are excluded from this specific check** (found via testing, 2026-09-01). A text
box's own width/height ratio is governed by its content and `fontSize`, not by uniform-scale
geometry — it changes shape naturally when a line wraps differently or R12 reduces `fontSize` to
fit, with no squashing having occurred. This rule polices shapes, images and groups; a text
node's bounding box was never what it was meant to protect. R22 is what governs text.

**Source — Ad-Specific QA Checklist (Rachel), general resize principle:** *"Do not distort or
resize individual pieces within what's defined as 'the visual' independently of one another. If
the visual as a whole needs to grow or shrink, resize it as a single unit — even if it's made up
of multiple layers."* R1/R2/R6 together are this principle stated as three checkable mechanics
rather than one sentence — this is the same rule, arrived at independently, not a coincidence
worth losing track of.

## R2 — `uScale = √(scaleX × scaleY)` is the uniform factor

**Owner:** script

```js
const scaleX = TW / SW;
const scaleY = TH / SH;
const uScale = Math.sqrt(scaleX * scaleY);   // geometric mean
```

Use the **geometric mean** — not `Math.max`, not `Math.min`, not either axis alone. The geometric
mean preserves the element's effective area across the aspect-ratio change, so a design scaled
from 1080×1350 to 1200×1200 keeps its visual weight instead of growing or shrinking overall.

Picking `max` inflates everything and pushes content past the safe zone; picking `min` leaves the
composition looking thin and under-filled on the new canvas.

**`uScale` can be greater than 1 even when the canvas gains no width.** For 1080×1350 →
1080×1920, `scaleX` is exactly 1.0 but `uScale` is 1.193 — so every element grows ~19% wider on
a canvas that did not widen. This is correct behaviour, not a bug, and it means the bounds pass
(R25, workflow Step 8) is not optional cleanup for this placement pair: any element wider than
~906px overflows the moment Step 5 is applied properly. Treat Step 5 and Step 8 as two halves of
one operation.

*Validated 2026-07-16, Community Hub post, 1080×1350 → 1200×1200.*

## R3 — Element *positions* use per-axis scale

**Owner:** script

Position is the one place per-axis scaling is correct:

```js
child.x = child.x * scaleX;
child.y = child.y * scaleY;
```

Size must stay uniform (R1/R2), but position must redistribute to fill the new canvas shape.
Scaling positions uniformly instead leaves the composition clustered toward one corner with dead
space on the other two sides.

Read the pair together: **uniform for size, per-axis for position.** Getting one right and the
other wrong is the most common way this pipeline fails.

## R4 — Text groups get explicit horizontal centering

**Owner:** script

```js
textGroup.x = Math.round((TW - textGroup.width) / 2);
textGroup.y = Math.round(textGroup.y * scaleY);
```

Proportional X positioning (`x * scaleX`) is right for a visual anchored to one side, and wrong
for a headline block that reads as centred. Centred text drifts a few percent off-axis, which the
eye reads as "sloppy" long before it can name why.

Centre horizontally, scale vertically. Round both — sub-pixel text positions render soft.

## R5 — `group.resize()` does not preserve image rects inside nested mask groups

**Owner:** script

`group.resize(w * uScale, h * uScale)` scales descendants internally, but image fill rectangles
inside nested mask groups **drift** — most often in Y, where the image floats above the shape
that is supposed to clip it. The visible symptom is a masked photo showing background, or a
circular avatar with a crescent of empty space along one edge.

This is why R6's "direct children only" carries an explicit exception, and why R7's post-pass is
mandatory rather than conditional. Do not assume a mask group survived a resize because it looks
plausible in a thumbnail.

## R6 — Process direct children only

**Owner:** script

Iterate the frame's **direct children**. Do not recurse to apply scaling per node — Figma's
`resize()` already scales all descendants internally, so recursing multiplies the scale factor at
every level and collapses the design.

The single exception is R7's mask-group repair, which runs *after* all direct children are sized,
as a separate corrective pass rather than as part of the scaling walk.

## R7 — Post-pass: realign mask-group image rects in absolute coordinates

**Owner:** script · implemented in `scripts/fix_mask_images.js`

After all direct children are resized, walk the output frame for every mask group — a `GROUP`
containing a child with `isMask === true` — and realign its image rect to the mask shape.

**Do not simply set `image.x = mask.x`.** Sibling nodes inside a wrapper group that was previously
scaled non-uniformly have different local→canvas scale factors, so local coordinates put the image
in the wrong place on canvas. Work in `absoluteBoundingBox` space:

```js
const mAbs = maskShape.absoluteBoundingBox;   // canvas-space bounds of the mask shape
const iAbs = imageRect.absoluteBoundingBox;   // canvas-space bounds of the image rect

const deltaAbsX = mAbs.x - iAbs.x;
const deltaAbsY = mAbs.y - iAbs.y;

// local units per canvas pixel for this node — differs per node when a wrapper
// group carries a residual scale transform
const kX = iAbs.x !== 0 ? imageRect.x / (iAbs.x - frameAbsX) : 1;
const kY = iAbs.y !== 0 ? imageRect.y / (iAbs.y - frameAbsY) : 1;

imageRect.x += deltaAbsX / kX;
imageRect.y += deltaAbsY / kY;
imageRect.resize(maskShape.width, maskShape.height);
```

**The order to apply it in:** try the simple form first, then *verify*, then fall back.

```js
imageRect.x = maskShape.x;
imageRect.y = maskShape.y;
imageRect.resize(maskShape.width, maskShape.height);
```

The shortcut is valid only when the wrapper group has no residual scale transform. Confirm with
`absoluteBoundingBox` that `imageRect.abs ≈ maskShape.abs`; if they differ by more than 5px, use
the k-factor form above.

Shortcut → verify → fall back. Skipping the verify step is how this ships broken: the shortcut
succeeds often enough to look reliable and fails silently when it doesn't.

## R8 — Post-pass: fix non-uniform `imageTransform` on CROP fills

**Owner:** script · implemented in `scripts/fix_crop_transform.js`

`imageTransform` is **not** reliably preserved through a resize. Even with a correct uniform
`uScale`, image fills in `CROP` mode can end up with different X and Y scale factors in their
transform matrix, squashing the photo inside an otherwise correctly-sized frame.

```js
for (const fill of [...imageRect.fills]) {
  if (fill.type !== 'IMAGE' || fill.scaleMode !== 'CROP') continue;
  const T = fill.imageTransform;   // [[a, c, tx], [b, d, ty]]
  const scaleA = T[0][0];          // X scale
  const scaleD = T[1][1];          // Y scale

  if (Math.abs(scaleA - scaleD) < 0.01) continue;   // already uniform, leave it

  const u = Math.sqrt(scaleA * scaleD);             // geometric mean, as R2

  // preserve the crop centre in layer UV space
  const centerX = T[0][2] + scaleA / 2;
  const centerY = T[1][2] + scaleD / 2;

  imageRect.fills = imageRect.fills.map(f =>
    f === fill
      ? { ...f, imageTransform: [[u, 0, centerX - u / 2], [0, u, centerY - u / 2]] }
      : f
  );
}
```

**Never switch `CROP` to `FILL` to "fix" this.** `FILL` re-centres automatically, which discards
an intentional crop — a portrait framed on someone's face becomes a shot of their torso. The
geometric-mean fix removes the squash while keeping whatever the designer chose to show.

Only `CROP` fills need this. `FILL` fills are auto-centred by Figma and are always correct.
Uniform scale on both axes with a correct translation is fine — skip it.

*Validated 2026-07-16 on the Community Hub 1200×1200 LI frame, where **three of five person
bubbles were squashed** (X = 0.993 against Y = 1.089) and every other check passed.*

---

# Content & brand integrity

## R9 — Never rotate, never distort

**Owner:** script

No element is rotated, skewed, stretched or warped. Every node's aspect ratio in the output must
match its aspect ratio in the master. This is R1's consequence stated as an output property, and
it is checked the same way — by the per-node aspect-ratio delta.

`rotation` on every matched node must equal the master's.

**Source — Ad-Specific QA Checklist, F2:** *"Everything that was not part of the task stays
exactly as it was (position, color, font, spacing)."* A resize's task is the canvas change, not
the individual element — so every element not being actively repositioned for the new layout
should read as untouched.

## R10 — Never crop the visual to fit

**Owner:** vision

When the visual doesn't fit the new canvas, extend or recompose — do not slice it. Anchor primary
visuals to one side (left **or** right), never floating in the middle of unexplained space.

Cropping is the fastest way to make a resize *look* finished while destroying the thing the
creative was built around.

**Amendment — the visual may shrink, but must not disappear.** Source: Ad-Specific QA Checklist,
S1: *"image (can shrink, must not disappear unless the format dictates otherwise)."* The
"unless the format dictates otherwise" clause is real, not a loophole — `REDDIT_COMMENT` is a
placement whose entire job is to show a crop of the visual and nothing else (see
`REDDIT-COMMENT-WORKFLOW.md`). For every `resize`-type placement, though, a visual hidden as a
side effect of a layout squeeze — rather than an explicit user-requested exclusion — is a defect,
not a valid outcome of "it didn't fit."

## R11 — Logo integrity

**Owner:** script (count, geometry) · vision (placement)

One logo in the master means exactly one logo in the output. Never duplicate it, never invent a
second placement, never scale it non-proportionally, and never redraw it.

`resize_qa_diff.py` asserts the logo node count matches and its aspect ratio is unchanged. Where
the logo sits within the placement is a vision call against `PLACEMENTS.md`.

**Source — Ad-Specific QA Checklist, S1:** *"logo (mandatory, no exceptions)."* No `resize`-type
placement may exclude the logo, even when space is tight — that's a scale-it-down problem, not an
exclude-it problem. (`REDDIT_COMMENT` is the one placement where the logo is deliberately absent
by design, not by exception — see its `forbiddenElements` in `placements.json`.)

## R12 — Never rewrite, paraphrase, or repeat text

**Owner:** script

Text content is cloned — it arrives correct. The failure mode is a model *retyping* it: a CTA
label re-entered by hand, a headline "tightened" to fit, a line duplicated to fill space.

If text doesn't fit, reduce `fontSize`. Never stretch glyphs, never edit the copy, never repeat a
block to fill a gap. `resize_qa_diff.py` diffs `characters` on every TEXT node against the master
baseline — any change is a hard failure unless the user explicitly asked for new copy.

**Source — Ad-Specific QA Checklist, F2** (see R9) covers this the same way: text is squarely
"something not part of the task," so it stays exactly as it was unless the task is specifically
to change it. **F1** states the umbrella principle this rule and most of R9–R16 sit under:
*"every change made has a justification tied to the requested task — not a change for its own
sake."* When in doubt about whether a change is in-scope, F1 is the test to apply.

## R13 — Never invent elements to fill dead space

**Owner:** vision

Converting a master to a taller or squarer canvas than it started with can leave real empty
space below the visual — exactly how much depends on both master and target ratio, and has to be
computed fresh each time; see `ASK-DONT-GUESS.md`'s fit table (its numbers have already changed
twice as the Story safe zone was corrected). That space, whatever its size, is **structural** —
there is no source material for it, and no amount of care will find some. Adding a shape, a
pattern, a second CTA or a stray brand bar to make it look intentional is inventing design that
nobody approved.

Surface it as a creative decision with real options (CTA lockup, brand bar, background extension,
or leave it) and let the user choose. Full handling in `ASK-DONT-GUESS.md`.

**Source — Ad-Specific QA Checklist, "Other notes":** *"Focal point of a photo/illustration stays
visible and centered in the new crop — not just 'not cut off.'"* Written there about cropping, but
the same standard applies to composing a visual into new dead space: "technically present" is a
lower bar than "reads as intentional," and this rule is about the gap between the two.

## R14 — Brand preservation

**Owner:** script

- **monday.com marks** stay exactly as they are — English, original typeface, original colour.
- **Third-party brand names** — Gmail, Slack, Mailchimp, Asana, Stripe, Salesforce and the rest —
  keep their exact original form. Never translated, never restyled, never abbreviated.
- **Tech terms and acronyms** — OKRs, C-levels, KPIs — remain in English.

Covered by R12's text diff, called out separately because these are the strings a model is most
tempted to "correct."

## R15 — CTA stays a single horizontal line, solid fill

**Owner:** vision

A CTA label is always one horizontal line. If it's too long, reduce the font size — never wrap to
a second line, never letter-space it tighter to force a fit.

CTA buttons are solid-filled. Never outlined, never ghost, never semi-transparent.

## R16 — Icons survive intact

**Owner:** script (count) · vision (at element zoom)

Every icon in the master appears in the output: same count, same style, same relative size. None
removed, none replaced with a Unicode glyph or emoji, none restyled from outline to filled.

Icon-sized elements are exactly what a full-frame screenshot cannot resolve — a 24px chip inside
a 1920px frame is a few pixels once the capture is scaled into a chat window. This is what the
gate's element-zoom layer (9c) exists for.

---

# Visual fidelity

These six are largely guaranteed by `clone()`. They are cheap to verify from the same measurement
data the geometry checks already use, so they stay as script checks — but treat a failure here as
a signal that something *actively rewrote* a property, not as routine drift.

**Source — Ad-Specific QA Checklist, F2:** *"Everything that was not part of the task stays
exactly as it was (position, color, font, spacing)."* R17–R22 are F2 broken into six independently
checkable properties. F2 also implies the corollary in R40 below: when a property in this list
*is* deliberately changed as part of the task (background recoloured, text resized), recheck
anything that depended on it — starting with contrast.

## R17 — Fills and text colours unchanged

**Owner:** script

Every fill colour, per element role — headline, subheadline, body, CTA label, legal, background —
matches the master exactly. No hue shifts, no near-miss substitutes, no "close enough" brand
purple.

## R18 — Gradients preserved

**Owner:** script

Gradients keep their transform (angle), colour stops and opacity transitions. A gradient that
survives a resize with its angle rotated is a real and easy failure when a frame changes aspect
ratio.

## R19 — Effects preserved

**Owner:** script

Drop shadows and other effects keep their offset, spread, radius, opacity and colour.

## R20 — Opacity preserved

**Owner:** script

Semi-transparent layers, overlays and frosted containers keep their source opacity values, on the
node and on its fills.

## R21 — Image container treatment preserved

**Owner:** vision

If the master shows images inside rounded rectangles, circular masks or bordered frames, the
output does too. Contained images never become edge-to-edge, and edge-to-edge images never
acquire a container.

Corner radius is measurable, but "this photo now bleeds to the frame edge" is a composition
judgement, which is why this one stays with vision.

## R22 — Typography preserved

**Owner:** script

Font family, weight, letter spacing and line height match the master per element role.

**Preservation is the rule — not any particular typeface.** A rule that asserts "Poppins only"
does two unhelpful things: it fails on a legitimately non-Poppins master, and it re-checks
something `clone()` already guarantees, which pads a QA report with a check that cannot
meaningfully fail. What can fail is a font being *changed* during the resize, and that is what
this rule catches.

`fontSize` is the deliberate exception: R12 permits reducing it to fit. Every other type property
must match.

---

# Layout, bounds & placement

## R23 — Exact target dimensions, verified not assumed

**Owner:** script

The output frame measures exactly the placement's `width × height`. No rounding drift, no
off-by-one from an auto-layout mode left enabled.

Verify by measurement after the resize — never by assuming `frame.resize()` did what was asked.
A frame still in an auto-layout mode silently ignores a fixed resize; set
`layoutSizingHorizontal`/`layoutSizingVertical` to `'FIXED'` first.

## R24 — Placement safe zones come from `placements.json`

**Owner:** script

No content — text, logo, CTA or important visual — falls inside a placement's reserved zones.
Read the numbers from `reference/placements.json` every time. Never from memory, never from this
document, never from a previous session's summary. **This has already burned the skill twice —
Story's own top/bottom figures have changed on two separate dates (see `PLACEMENTS.md`) — so
"I remember the number" is specifically the failure mode this rule exists to prevent.**

Story's zones are not a house style choice: **the platform's own interface occupies those
pixels**, whether the figure comes from the platform's published guidance or the team's own
tested measurement of the same coverage (`safeZoneSource: platform` vs `internal-tested` — see
`PLACEMENTS.md`). A headline placed in the reserved top band sits behind the profile chip and
handle on a real phone. The skill cannot see that; only the spec knows it.

## R25 — No off-canvas descendants

**Owner:** script

After scaling and placement, sweep the **whole tree** — not just direct children — for anything
whose bounds fall outside the canvas.

Measure on `absoluteBoundingBox`, not local `x`/`y`. A child sitting at a comfortable local x can
still be off-canvas once its parent group's own offset is applied, and local coordinates will
report it as fine.

```js
function findOffscreen(node, frameAbsX, frameW, out = []) {
  for (const child of node.children ?? []) {
    const b = child.absoluteBoundingBox;
    if (b) {
      const left = b.x - frameAbsX;
      if (left < 0 || left + b.width > frameW) {
        out.push({ id: child.id, name: child.name, left, right: left + b.width });
      }
    }
    findOffscreen(child, frameAbsX, frameW, out);
  }
  return out;
}
```

When something is out of bounds: shift the whole containing group back inside first. Only if the
group is genuinely too wide to fit does it get scaled down uniformly — and never clip individual
children to hide the problem.

## R26 — Spacing relationships preserved proportionally

**Owner:** script

The master's spacing relationships survive the transform: logo clearspace, logo→headline gap,
headline→subheadline gap, text→visual gap, CTA internal padding, and the gaps between repeated
items such as integration rows or feature lists.

Gaps must not collapse or balloon as a side effect of repositioning. Repeated-item gaps in
particular must stay uniform with each other — one row spaced differently from its siblings reads
as a bug immediately.

This rule checks *proportionality* — did the gap scale the way everything around it scaled. It
does not check an absolute floor — two elements can shrink proportionally and still end up too
close together to read comfortably. That's R42, below.

## R27 — Background extended using only master colours

**Owner:** vision

Extending the background to fill a taller or wider canvas uses only colours already present in
the master. Never introduce a gradient the master doesn't have, never add a vignette, texture or
glow to make the extension "feel designed."

If the master's background is a gradient, extend along its existing axis rather than restating
it — a gradient re-fitted to a new aspect ratio must keep its angle (R18).

## R28 — Frame naming and parenting

**Owner:** script

Every output frame is named with the convention from `placements.json` — `1080×1920 STORY`,
`1080×1350 FB`, `1200×1200 LI` — and is parented into the session's `Generated Ad Sizes N`
container.

Naming is not cosmetic: it is how a later session, a QA pass, or a handoff identifies which
placement a frame is, without measuring it.

---

# Process

## R29 — One placement at a time

**Owner:** process

Build one placement, gate it, present it, get approval, then start the next. Never batch several
placements into a single `use_figma` run.

A batched run that fails leaves N broken frames and no signal about which step broke them —
`use_figma` is atomic per call, so a mid-batch error rolls back work that was already correct.
One at a time also means the user catches a wrong interpretation on placement one instead of
placement three.

## R30 — All three gate layers run

**Owner:** process

Vision (9a), measurement diff (9b) and element zoom (9c) each run on every placement. None
substitutes for another, and the order matters: look first, then measure, then zoom.

They cover genuinely different failure classes. Vision catches wrong composition. The diff
catches wrong numbers. The zoom catches a blank asset, a wrong crop, or a glyph standing in for
a real icon — none of which the other two can see.

## R31 — A clean measurement run is not "QA complete"

**Owner:** process

`resize_qa_diff.py` exiting clean means **the mechanizable half is clean**. It does not mean the
placement is done.

The script reports which rules it checked and which it did not. Every rule it lists as
`vision`-owned still needs a human or model to actually look. Reporting a clean diff as a passing
QA is the specific failure this rule exists to prevent — it is how a build gets declared excellent
while an entire category of defect was never examined at all.

---

# Ad-Specific QA Checklist alignment

New 2026-09-01. Sourced from Rachel's Ad-Specific QA Checklist — the shared baseline that runs
across every ad task (iteration, resize, localization, adaptation), plus its resize-specific
sections. Where a rule above already covered the same ground, the citation was added there
instead of duplicating it here (R1/R2/R6, R9, R10, R11, R12/R14, R13, R17–R22, R26). What follows
is genuinely new — either a floor that didn't exist before, or a rule this skill's own R1–R31
didn't cover at all.

## R32 — Minimum microcopy size: 28px @1x

**Owner:** script

**Source:** *"Minimum microcopy size inside the creative: 28px @1x export, at every frame size."*

Every non-headline, non-CTA text node — subheadlines, labels, legal/fine print — renders at
**≥28px** at 1x export, on every placement. This is a floor beneath R12's permission to reduce
`fontSize`: reducing is allowed until it isn't.

**Assumption stated explicitly:** "@1x export" is read here as the frame's native authored pixel
size (`fontSize` as recorded by `measure_frame.js`), not a further export multiplier. If whatever
pipeline actually exports these creatives applies its own scale factor, this floor needs to be
read at *that* scale, not the raw node value — confirm this before trusting a borderline result.

```python
if fontSize < 28 and node.role not in ("headline", "cta"):
    FAIL  # see R35 for what to do about it — never ship a silent shrink
```

## R33 — Minimum CTA text size: 36px @1x

**Owner:** script

**Source:** *"Minimum CTA text size: 36px @1x export."*

Same mechanism as R32, floor of **36px**, scoped to the CTA label specifically. A CTA rendered
below this is illegible at the sizes these creatives are actually viewed at, regardless of how
the rest of the composition looks.

## R34 — Message hierarchy: H1/H2 line caps and minimum H2 size

**Owner:** script (H2 minimum size — measurable) · vision (line count as actually rendered —
wrapping depends on render width, which node data alone can't determine)

**Source:** *"Message hierarchy: one dominant H1, up to 2–3 lines depending on format. If an H2
exists, total cap is 2 lines H1 + 2 lines H2. Minimum H2 size: 45px."*

- Exactly one dominant H1 per placement.
- If an H2 exists: H1 ≤ 2 lines **and** H2 ≤ 2 lines, combined.
- H2 minimum size: **45px** — mechanizable the same way as R32/R33.

**Open item, not yet resolved:** the source doesn't specify the per-format H1 line-count numbers
behind "up to 2–3 lines depending on format" — which format gets 2, which gets 3. Until that's
defined, treat anything past 2 lines as a vision judgement call ("does this still read as
dominant over the rest of the hierarchy") rather than inventing a per-placement number nobody
confirmed. Logged in `QA-CHECKLIST-ALIGNMENT.md` alongside the source's own two open items.

## R35 — Never silently ship a shrink below the floor

**Owner:** process

**Source:** *"If a change pushes text below these minimums and it can't be enlarged without
breaking the composition → hard stop, alert the user. Never ship a silent shrink."*

R32/R33/R34's floors are non-negotiable. If satisfying the intended layout would require going
below one, that's a halt condition — `ASK-DONT-GUESS.md`, not a judgement call to make alone.

**This is a second, independent constraint, not a restatement of an existing one.**
`ASK-DONT-GUESS.md`'s trigger 5 already halts when text drops below ~60% of the *master's*
size — a check relative to where the text started. R32–R34 are **absolute** floors, unrelated to
what the master used. A resize must satisfy both: font size can be perfectly reasonable relative
to the master and still be illegible in absolute terms, or vice versa on an unusually large
master. Whichever fires first, stop.

## R36 — Overflowing copy gets alternatives offered, not silent overflow

**Owner:** vision · process

**Source:** *"Requested copy that exceeds this cap → don't silently overflow; offer alternatives
(shorten the copy / drop weaker sub-messages) to keep intent low and the CTA/message prominent."*

When copy exceeds R34's hierarchy cap even at the R32 floor, the fix is a conversation, not a
silent overflow and not a unilateral edit: offer to shorten the copy or drop a weaker sub-message,
and let the user choose. This is R12's "never edit the copy" holding even under pressure — the
alternative to overflow is asking, not rewriting.

## R37 — Newly added text is set in Poppins

**Owner:** script

**Source:** *"Any newly added text is set in Poppins."*

Distinct from R22, which governs **existing** text keeping **whatever font the master used** —
R22 deliberately doesn't hardcode a typeface, because preservation is the rule, not Poppins
specifically. R37 is the opposite case: a text node with **no equivalent in the master** — a CTA
label the user supplied fresh, say — defaults to Poppins, because there's no "preserve the
original" to fall back on.

```python
# a node with no matching baseline path is new, not modified
new_text_nodes = [n for n in output_nodes if n.type == "TEXT" and n.path not in baseline_paths]
for n in new_text_nodes:
    if n.text.fontFamily != "Poppins":
        FAIL
```

## R38 — CTA inclusion follows the master, with a hard platform exception

**Owner:** script

**Source — "CTA rule for resize":** *"'Follows master' means: unless the user asks otherwise,
match the master creative. If the master has a CTA button, include one in the resized output (at
whatever size that format needs). If the master doesn't have one, don't add one."* Refined by the
**CTA-by-Format table**: Meta Story never gets an in-canvas CTA regardless of the master, because
the platform renders its own native CTA over the creative.

This **replaces** the old free-form "should this size include a CTA?" question in
`RESIZE-WORKFLOW.md` Step 1 with an actual answer derived from the master: check whether the
baseline has a CTA-candidate node, then follow it — except Story, which is always no. The user can
still override either way; the point is the *default* stops being a guess.

`placements.json`'s `ctaRule` field encodes this per placement: `"follows-master"` (FB, LI) or
`"never"` (STORY, and REDDIT_COMMENT for a different reason — see R43).

```python
if placement.ctaRule == "never":
    include_cta = False
elif placement.ctaRule == "follows-master":
    include_cta = baseline_has_cta_candidate  # unless the user explicitly overrides
```

## R39 — Line-count change forces a recompose, not a collision

**Owner:** vision

**Source:** *"Proportions between logo / copy / button / image stay balanced; if line count
changed (e.g. 2→3 lines), fix the composition accordingly (e.g. reposition the image) rather than
leaving a collision."*

If reducing font size (R12) still leaves more lines than the master had, the fix is repositioning
the affected neighbour — not letting the text box grow into whatever sits below it. This is R26's
spacing-preservation principle applied to the specific case where the *shape* of the text block
itself changed, not just its size.

## R40 — Contrast is rechecked whenever the task could have broken it

**Owner:** script

**Source — F3, F4, F5, consolidated into one check because they ask the same question:**
*"Background color changed → recheck contrast against any text sitting on it (target 4.5:1, floor
3:1 for 'large' text). An element moved onto a different background → same contrast recheck. Text
resized → recheck contrast. If borderline, first fix is increasing weight (Light→Regular,
Regular→Medium) before escalating to the user."*

Compute the WCAG contrast ratio from hex values directly — never estimate it visually when the
data is right there. "Large text" is 24px+ or ~19px+ bold, and R32/R33's own floors (28px, 36px)
mean **most ad text in this skill's outputs already clears that threshold by construction** — the
practical bar for most nodes is 3:1, not 4.5:1. Anything smaller (legal/fine print) still needs
4.5:1.

**Fix order, as specified — don't skip to escalation:** if a contrast check is borderline, try
increasing font weight first (Light→Regular, Regular→Medium) before asking the user. Only
escalate if that isn't enough.

```python
L = lambda c: 0.2126*lin(c.r) + 0.7152*lin(c.g) + 0.0722*lin(c.b)
ratio = (max(L(fg), L(bg)) + 0.05) / (min(L(fg), L(bg)) + 0.05)
threshold = 3.0 if (fontSize >= 24 or (fontSize >= 19 and bold)) else 4.5
```

**Stated limitation:** "background" here means the nearest ancestor with a solid fill — a real
approximation of what's visually behind a text node, not a full occlusion/z-order analysis. It
will not catch text sitting on top of a busy photo, or a sibling shape overlapping from outside
the tree. Those need a human eye — R21 and general vision QA are the backstop, not this check.

## R41 — Conflicting rules get flagged, not silently resolved

**Owner:** process

**Source — F6:** *"Two design rules conflict → flag to the user with the choice made + reasoning.
Optional: duplicate the frame with the alternate rule applied, so the user can pick."*

Full halt-condition mechanics (trigger 9) and the "what to ask" pattern live in
`ASK-DONT-GUESS.md` — this entry exists so the rule has an R-number and shows up in
`resize-rules.csv`'s traceability, not to restate the mechanics twice.

## R42 — An absolute minimum clearance floor, independent of proportionality

**Owner:** script

**Source — S9:** *"Elements that ended up too close to each other as a result of the change."*
The source states the condition without a specified consequence or threshold — flagged as
incomplete in `QA-CHECKLIST-ALIGNMENT.md`. The **concept** (elements can end up too close as a
side effect of a resize) is Rachel's; the **numbers** enforcing it are this skill's own
pre-existing `minGaps` values in `placements.json` (logo→headline, headline→subheadline,
text→visual, any→CTA) — set during the original build, not supplied by the source doc.

This is a different failure mode from R26. R26 checks *proportionality* — did a gap scale the way
everything around it scaled. Two elements can shrink in perfect proportion and still land closer
than `minGaps` allows in absolute pixels. R26 wouldn't catch that; this rule does.

```python
for pair, floor_px in placement.minGaps.items():
    if measured_gap(pair) < floor_px:
        FAIL
```

---

# Crop operations (REDDIT_COMMENT only)

Everything below applies **only** to a placement whose `operationType` is `crop`. Do not apply
these to STORY/FB/LI, and do not apply R1–R31 (composition/resize rules — logo integrity, text
preservation, CTA rules, spacing) to a crop placement: a crop placement isn't a composition, and
most of those rules assume elements this operation deliberately doesn't have. Full workflow in
`REDDIT-COMMENT-WORKFLOW.md`.

## R43 — A crop placement contains only the cropped fragment

**Owner:** script

**Source — "Reddit comment — what goes there":** *"Small visual next to a one-line text ad. What
belongs there: an eye-catching visual crop pulled from the source ad's original (full) size — not
text, not the CTA, not the logo, and not the full visual as-is."*

The output frame contains **no visible TEXT nodes, no logo-candidate node, no CTA-candidate
node** — only the cropped visual. This is R11/R12/R15's opposite: on every other placement,
excluding the logo or CTA is the exception; here, including one is the defect.

```python
if any(visible(n) for n in output_nodes if n.type == "TEXT"): FAIL
if any(visible(n) for n in output_nodes if n.path in logo_candidates): FAIL
if any(visible(n) for n in output_nodes if n.path in cta_candidates): FAIL
```

## R44 — Crop from the master's original visual, never from a placement's output

**Owner:** process

**Source:** same section — *"pulled from the source ad's original (full) size."*

Always crop from `measure-master.json`'s visual node — the original, unscaled asset. Never from an
already-built STORY/FB/LI output: those have already been resized and recomposed, and no longer
represent "the source ad's original full size."

## R45 — The subject's focal point stays visible and centred

**Owner:** vision

**Source — "Other notes":** *"Focal point of a photo/illustration stays visible and centered in
the new crop — not just 'not cut off.'"*

No script can locate a photo's subject without object or face detection, which isn't available
here — this stays entirely vision-owned. The source's own emphasis matters: "not cut off" is
necessary but not sufficient. A crop that keeps the subject fully in-frame but crowded into a
corner still fails this.

## R46 — A crop is a genuine sub-region, never the whole visual squeezed to fit

**Owner:** vision (primary) · script (supporting signal only)

**Source:** same section — *"not the full visual as-is (usually too small to read at this
size)."*

The crop should read as a meaningfully zoomed-in fragment, not the entire source image shrunk to
fit 4:3. A supporting fact a script can report: the image fill's `scaleMode` should be `CROP`
(not `FILL`), since `FILL` auto-fits the whole image. That fact is a signal, not a verdict — it
doesn't distinguish a good crop from a badly-chosen one, which is why this stays vision-primary.


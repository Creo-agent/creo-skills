# Resize Workflow — The Per-Placement Engine

This is the engine for every placement whose `operationType` is `"resize"` (STORY, FB, LI) —
clone the whole composition, transform it, keep every element. One placement goes through all
ten steps, in order, every time. Building three placements means running this file three times —
not once with a bigger scope. See `BATCH-WORKFLOW.md` for what wraps around it.

**Not for `REDDIT_COMMENT` or any other `crop`-type placement.** A crop placement extracts one
fragment and discards the rest — a fundamentally different operation. See
`REDDIT-COMMENT-WORKFLOW.md` instead; do not adapt this file's steps to it.

## Contents
- Input requirements
- State detection — which step am I in?
- Defaults that are never asked
- Step 0 — Load the placement spec
- Step 1 — Confirm the per-placement brief
- Step 2 — Master baseline
- Step 3 — State the plan
- Step 4 — Clone and resize the canvas
- Step 5 — Geometry pass
- Step 6 — Placement layout
- Step 7 — Geometry post-passes
- Step 8 — Bounds enforcement
- Step 9 — The gate
- Step 10 — Deliver
- Change requests
- Error recovery

---

## Input requirements

| Input | Required | If missing |
|---|---|---|
| Figma URL with `node-id` | yes | Stop and ask. The skill cannot start without it. |
| Which placements to build | yes | Present the three and ask. **Never assume "all".** |
| Order | yes | Propose one, confirm it. |
| CTA inclusion | per placement | Derived from the master + `ctaRule` at Step 1 (R38) — not asked as a free question. |
| CTA label / colour | per placement | Asked at Step 1 only when a CTA applies. |
| Exclusions | per placement | Asked at Step 1. |
| Separate logo asset | optional | Assume embedded in the master unless the user says otherwise. |

Convert the node id from the URL's hyphen form to a colon: `node-id=47-1515` → `47:1515`.

## State detection — which step am I in?

On resuming a session, work out where you are before doing anything:

- No `measure-master.json` on disk → you are before Step 2. Start there.
- Baseline exists, no `Generated Ad Sizes` container in the file → Step 4 has not run.
- Container exists with N frames, none gated → you are at Step 9 for the last one.
- A placement was approved and another remains → Step 0 for the next placement.

**Resuming after a context summary is not a fresh start.** Re-read the placement spec and the
baseline from disk rather than trusting a summarised recollection of their numbers.

## Defaults that are never asked

- Output is **always native Figma frames** created by `use_figma`. Never ask about output format.
- The container is **always** `Generated Ad Sizes N`, auto-incrementing per session.
- Frame naming always follows `placements.json`.
- Excluded elements are **hidden** (`visible = false`), never deleted.

---

## Step 0 — Load the placement spec

Read the placement's entry from `reference/placements.json`. Every number used from here on —
canvas size, safe zones, minimum gaps, layout order, frame name — comes from that file.

**Never work from memory, from `SKILL.md`'s summary table, or from a previous session's notes.**
Story's safe zones in particular are not house style: Meta's own interface physically covers
those pixels on a real phone, and only the spec knows the current figures.

Read `reference/PLACEMENTS.md` for the same placement to get the reasoning, the layout order and
any rule unique to that size.

## Step 1 — Confirm the per-placement brief

**CTA inclusion is derived, not asked (R38).** Read the placement's `ctaRule` from
`placements.json`:

- `"never"` — no CTA, full stop, regardless of the master. State this rather than asking.
- `"follows-master"` — check whether the master's baseline has a visible CTA-candidate node
  (`derived.ctaCandidates` in `measure-master.json`, once Step 2 has run). If it does, a CTA goes
  in this placement too. If it doesn't, none goes in. This is the default — confirm it, don't
  re-derive it as a fresh question each placement.

Ask, in one message, before touching the file:

> Ready to start **[placement]** ([W]×[H]). [State the derived CTA answer: "The master has a
> CTA, so this placement will too" / "No CTA here — [placement] never gets an in-canvas CTA" /
> "The master has no CTA, so none is added here."]
> 1. *(only if a CTA applies)* What should the **label** say — same as the master, or different?
> 2. *(only if a CTA applies)* What **colour** — same as the master, white, black, or a hex?
> 3. Anything to **exclude** from this size? (headline, visual, logo, specific icons)
> 4. Want to override the CTA default above? Say so now rather than after it's built.

If the user says "same as before" or "same defaults," carry the previous placement's answers
forward and state what you carried so they can correct it. An override the user gives here is
now part of the brief — but `cta_matches_master_rule` will still flag it as a deviation, so log
it as an accepted gap with the override as the stated reason (`ACCURACY-GATE.md`), not as a
silent exception.

Wait for answers. Starting the clone before the brief is settled means redoing it.

## Step 2 — Master baseline

If `measure-master.json` does not exist for this session, produce it now — **before any clone
exists.** Full contract, schema, caching rules and validity checklist in
`PRE-RESIZE-MEASUREMENT.md`.

If it already exists, confirm `meta.role === "master"` and that its `frameAbs` matches the
master you are actually working from, then reuse it. Do not re-measure per placement.

## Step 3 — State the plan

Before writing anything, tell the user what you intend to do, as a table:

| Element | Master position | Target zone | Treatment |
|---|---|---|---|
| Logo | top-left, 120,96 | top of usable area | uniform scale ×0.83 |
| Headline | centred, y 240 | below logo, min 40px gap | centred, scale Y only |
| Visual | full width, y 520 | focal zone, y ≈ 700 | uniform scale ×0.83 |
| CTA | — | above bottom safe zone | added per brief |
| Integration row | y 1180 | excluded this size | hidden |

State also: the source→target aspect ratio change, the computed `uScale`, and anything you plan
to exclude. Element roles come from `derived.logoCandidates` / `iconCandidates` in the baseline —
if a role is ambiguous, list the candidates and ask rather than guessing which node is the logo.

This is the last cheap moment to catch a wrong interpretation. After Step 4 the cost of a
misunderstanding is a rebuild.

## Step 4 — Clone and resize the canvas

Create the container **once per session**, then clone into it.

```js
// --- container, once per session ---
let maxY = 0;
for (const child of figma.currentPage.children) {
  if (child.type === 'FRAME' && child.name.startsWith('Generated Ad Sizes')) {
    maxY = Math.max(maxY, child.y + child.height);
  }
}
const existingCount = figma.currentPage.children.filter(
  c => c.type === 'FRAME' && c.name.startsWith('Generated Ad Sizes')
).length;

const container = figma.createFrame();
container.name = `Generated Ad Sizes ${existingCount + 1}`;
container.layoutMode = 'HORIZONTAL';
container.itemSpacing = 100;
container.paddingLeft = container.paddingRight = 0;
container.paddingTop = container.paddingBottom = 0;
container.layoutSizingHorizontal = 'HUG';
container.layoutSizingVertical = 'HUG';
container.x = 0;
container.y = maxY > 0 ? maxY + 100 : 0;
figma.currentPage.appendChild(container);
```

```js
// --- per placement ---
// Load every font the master uses before touching any text node.
await figma.loadFontAsync({ family: FAMILY, style: STYLE });   // repeat per font

const source = await figma.getNodeByIdAsync(SOURCE_NODE_ID);
const frame  = source.clone();
frame.name   = SPEC.frameName;                    // e.g. "1080×1920 STORY"

const container = await figma.getNodeByIdAsync(CONTAINER_ID);
container.appendChild(frame);

// A frame still in an auto-layout mode silently ignores a fixed resize (R23).
frame.layoutSizingHorizontal = 'FIXED';
frame.layoutSizingVertical   = 'FIXED';
if (frame.layoutMode !== 'NONE') {
  frame.layoutSizingHorizontal = 'FIXED';
  frame.layoutSizingVertical   = 'FIXED';
}
frame.resize(SPEC.width, SPEC.height);
```

Fonts first, always. A font that isn't loaded turns any later text operation into a hard error
partway through the run — and because `use_figma` is atomic, that discards everything the call
had already done.

Apply exclusions here, by hiding rather than deleting:

```js
const excluded = frame.findOne(n => n.name.toLowerCase().includes('integration'));
if (excluded) excluded.visible = false;
```

Hiding preserves the user's ability to change their mind without a rebuild, and keeps the node
tree aligned with the baseline so the differ's paths still match (`PRE-RESIZE-MEASUREMENT.md`).
Leave no placeholder or empty frame in the vacated zone.

## Step 5 — Geometry pass

**Uniform for size, per-axis for position.** This is R1–R4 and it is the single most
consequential moment in the engine.

```js
const scaleX = SPEC.width  / SOURCE_W;
const scaleY = SPEC.height / SOURCE_H;
const uScale = Math.sqrt(scaleX * scaleY);   // geometric mean — R2

for (const child of frame.children) {        // DIRECT children only — R6
  if (isTextGroup(child)) {
    child.x = Math.round((SPEC.width - child.width) / 2);   // R4
    child.y = Math.round(child.y * scaleY);
    continue;
  }
  child.resize(child.width * uScale, child.height * uScale); // R1, R2
  child.x = child.x * scaleX;                                // R3
  child.y = child.y * scaleY;
}
```

Three ways this goes wrong, all of which look reasonable while you are writing them:

- Using `scaleX` for width and `scaleY` for height. Squashes everything. (R1)
- Recursing into groups to "make sure" descendants scaled. `resize()` already scales them, so
  recursing multiplies the factor at every level and collapses the design. (R6)
- Positioning a centred text block with `x * scaleX`. It lands a few percent off-axis, which
  reads as sloppy without being obviously wrong. (R4)

## Step 6 — Placement layout

Move elements into the placement's zones, following the layout order in `PLACEMENTS.md` and the
numbers in `placements.json`.

This is the one step with genuine per-placement judgement in it — which is exactly why it is not
scripted. A script here would fight the layout decisions instead of supporting them. The
geometry it produces gets *verified* at Step 9 rather than constrained up front.

Keep the master's spacing relationships proportional as you place (R26): logo clearspace,
logo→headline, headline→subheadline, text→visual, CTA padding, and the gaps between repeated
items, which must stay uniform with each other.

## Step 7 — Geometry post-passes

**Both run, every placement, every time.** They are not conditional cleanup — both bugs shipped
in builds that passed every other check.

1. `scripts/fix_mask_images.js` — realigns image rects inside mask groups (R5, R7). Applies the
   simple form, verifies against `absoluteBoundingBox`, and falls back to the k-factor form when
   the wrapper group carries a residual scale transform.
2. `scripts/fix_crop_transform.js` — repairs non-uniform `imageTransform` on CROP fills (R8) via
   the geometric mean, preserving the crop centre. **Never converts CROP to FILL** — FILL
   re-centres and turns a deliberate face crop into a shot of someone's torso.

Run them in that order. Realigning the rect first means the transform fix operates on a rect
that is already where it belongs.

## Step 8 — Bounds enforcement

Sweep the **whole tree**, not just direct children, on `absoluteBoundingBox` (R25). A child at a
comfortable local `x` can still be off-canvas once its parent group's offset applies, and local
coordinates report it as fine.

```js
const frameAbsX = frame.absoluteBoundingBox.x;
const frameAbsY = frame.absoluteBoundingBox.y;

function sweep(node, out = []) {
  for (const child of node.children ?? []) {
    const b = child.absoluteBoundingBox;
    if (b) {
      const left = b.x - frameAbsX, top = b.y - frameAbsY;
      if (left < 0 || top < 0 ||
          left + b.width  > SPEC.width ||
          top  + b.height > SPEC.height) {
        out.push({ id: child.id, name: child.name, left, top,
                   right: left + b.width, bottom: top + b.height });
      }
    }
    sweep(child, out);
  }
  return out;
}
```

**Step 8 is not a safety net for edge cases — for some placement pairs it is mandatory
arithmetic.** When the target is taller but no wider, the horizontal scale is 1.0 while `uScale`
is greater than 1. Going from 1080×1350 to 1080×1920:

```
scaleX = 1080/1080 = 1.000
scaleY = 1920/1350 = 1.422
uScale = √(1.000 × 1.422) = 1.193      ← every element gets ~19% WIDER
                                          on a canvas that got no wider at all
```

So any element wider than `1080 / 1.193 ≈ 906px` overflows the frame **by construction**, purely
from applying Step 5 correctly. A 900px headline becomes 1073px; a 920px visual becomes 1097px.
Nothing was done wrong — the geometry pass and the bounds pass are two halves of one operation,
and skipping the second leaves a frame that is out of bounds every time.

Resolution order, and it matters:

1. **Shift the containing group** back inside the bounds.
2. If shifting would push it past the opposite margin, **scale the whole group down uniformly.**
3. **Never clip individual children** to hide the overflow — that trades a visible defect for an
   invisible one and destroys content the master had.

Then enforce the placement's safe zones from the spec (R24): no text, logo, CTA or important
visual inside a reserved band.

## Step 9 — The gate

Full process in `ACCURACY-GATE.md`, scored per `QA-SCORECARD.md`. Three layers, all of them:

- **9a Vision** — master and output side by side, actually looked at.
- **9b Measurement diff** — re-measure the output with `scripts/measure_frame.js`, then
  `scripts/resize_qa_diff.py` against `measure-master.json` and the placement spec.
- **9c Element zoom** — `get_screenshot` on individual small nodes, then look.

**A placement is DONE iff zero hard rules fail.** Fix, re-run the gate, repeat — at most twice.
After two failed fix passes, stop and ask the user whether to skip the placement, try a different
approach, or take it over manually. Grinding a third and fourth attempt on the same defect is how
a session burns an hour producing the same broken frame.

## Step 10 — Deliver

Present, in one reply:

- the output screenshot
- the QA verdict and score, with any failing rule named
- **accepted gaps stated explicitly** — never silently smoothed over
- the question: does this look right, or should anything change before the next placement?

Wait for explicit approval before starting the next placement (R29). "Looks good", "yes", "next"
all count; silence does not.

---

## Change requests

When the user asks for a fix after delivery, do not jump straight to editing.

1. **Scope it.** Which placement, which element, what specifically. If the request implies a
   change to every placement built so far, say so before starting.
2. **Re-measure before fixing.** Read the current state from a fresh output measurement rather
   than from what you believe you set. The frame may have been edited in Figma since.
3. **Apply the fix**, keeping every hard rule intact — a fix that fixes spacing by stretching an
   element trades one hard failure for another.
4. **Re-run the full gate** on that placement. Not a partial check, and not "the part I touched"
   — the fix may have moved something else.
5. **Confirm nothing else broke.** Compare against the previous output measurement, not just the
   master.
6. **Report** what changed, with the before/after numbers.

For a genuinely lightweight change — hiding one element, changing a CTA label — steps 2 and 5
can be folded into the gate run. Anything geometric gets the full sequence.

---

## Error recovery

| Symptom | Cause | Fix |
|---|---|---|
| Script error, nothing changed | `use_figma` is atomic — a failed call rolls back everything it did | Read the error, fix the cause, re-run. Nothing partial was left behind. |
| `Cannot read properties of null` | Wrong node id, or the node is on another page | Re-run discovery; confirm the page with `figma.currentPage` |
| Font load error | Style name is not what it looks like | `await figma.listAvailableFontsAsync()`. Note the spacing: `Semi Bold`, not `SemiBold`; `Extra Bold`, not `ExtraBold` |
| Frame ignores `resize()` | Auto-layout still active | Set `layoutSizingHorizontal`/`Vertical` to `'FIXED'` first (R23) |
| Page switch appears to do nothing | `figma.currentPage = page` fails silently | Use `await figma.setCurrentPageAsync(page)` |
| Masked image drifted after resize | R5 | Step 7's `fix_mask_images.js` — and check its verify step actually ran |
| Photo looks squashed but node aspect is correct | Non-uniform `imageTransform` on a CROP fill | Step 7's `fix_crop_transform.js` (R8) |
| Diff reports failures on elements that look fine | Nodes paired by name instead of index path | See `PRE-RESIZE-MEASUREMENT.md` — matching must be path-based |

Anything not listed here that turns out to be a Figma API behaviour rather than a mistake belongs
in `GOTCHAS.md` at the end of the session.

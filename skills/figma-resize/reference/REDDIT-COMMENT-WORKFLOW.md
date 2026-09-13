# Reddit Comment-Style Workflow — The Crop Engine

This is a different engine from `RESIZE-WORKFLOW.md`, for a placement whose `operationType` is
`"crop"`. Do not run `RESIZE-WORKFLOW.md`'s steps against `REDDIT_COMMENT`, and do not adapt this
file's steps to STORY/FB/LI — the two operations share a master and little else.

## Contents
- Why this is a separate engine
- What belongs in the output
- The six-step process
- The gate, scoped to what a crop can actually violate
- Maturity note

---

## Why this is a separate engine

Every other placement clones the **whole** master composition and transforms it, keeping every
element. `REDDIT_COMMENT` does the opposite: it extracts a **single fragment of one element**
(the visual) and discards everything else — no logo, no headline, no CTA. Source, from the
Ad-Specific QA Checklist's "Reddit comment — what goes there":

> *"Small visual next to a one-line text ad. What belongs there: an eye-catching visual crop
> pulled from the source ad's original (full) size — not text, not the CTA, not the logo, and
> not the full visual as-is (usually too small to read at this size)."*

Most of `HARD-RULES.md` (R1–R42) assumes a composition being transformed — logo integrity, text
preservation, CTA rules, spacing between elements that don't exist here. Applying those rules to
a crop placement doesn't just waste effort; some of them would flag *correct* behaviour as a
defect (R11's "one logo in the master means one in the output" is backwards here — the correct
output has **zero**).

## What belongs in the output

| | Included | Excluded |
|---|---|---|
| The cropped visual fragment | ✅ always | — |
| Logo | — | ✅ always excluded — not hidden as an exception, structurally absent |
| Headline / subheadline / any text | — | ✅ always excluded |
| CTA | — | ✅ always excluded — `ctaRule: "never"` |

No safe zone applies (`safeZoneSource: "n-a"`) — this runs next to platform-rendered comment
text, not over any platform UI.

## The six-step process

### Step 1 — Confirm the placement

Same as `RESIZE-WORKFLOW.md` Step 1's opening: confirm the Figma URL, screenshot the master,
confirm this placement is wanted. Skip the CTA/exclusion questions entirely — there's nothing to
configure. State plainly: *"Reddit comment-style has no logo, text or CTA by design — just a
cropped visual."*

### Step 2 — Measure the master (shared with the resize engine)

If a session baseline doesn't already exist, produce it exactly as `PRE-RESIZE-MEASUREMENT.md`
describes. **Crop from this baseline's visual node, never from an already-built STORY/FB/LI
output (R44).** Those have already been resized and recomposed — they no longer represent "the
source ad's original full size," which is specifically what the source spec asks for.

### Step 3 — Identify the visual and its focal point

Find the visual candidate (the largest IMAGE-fill node in the baseline). Then — and this is the
step with no mechanical shortcut — identify its **focal point**: the subject a viewer's eye goes
to. A product shot's focal point is the product; a photo of a person is usually their face.

If it's ambiguous, ask rather than guess (`ASK-DONT-GUESS.md` trigger 2 applies here too — role
ambiguity isn't specific to logo/headline).

### Step 4 — Choose the crop region

At 1440×1080 (4:3), choose a sub-region of the visual that:

- Keeps the focal point fully visible **and centred** — not just uncut. A subject that's
  technically in-frame but crowded into a corner still fails this (R45).
- Is a genuine **zoom in**, not the whole image shrunk to fit. If the visual's native aspect
  ratio is close to 4:3, this may mean deliberately cropping tighter than "the whole thing"
  rather than accepting a full-fit as the answer (R46).

This step is a judgement call, not a formula — there's no `uScale` here, because nothing is
being uniformly scaled. State the intended crop region to the user before executing it if it's
not obvious which part of the visual is the eye-catching one.

### Step 5 — Build the frame

```js
await figma.loadFontAsync(...);  // only if the source visual node requires it for rendering

const container = await figma.getNodeByIdAsync(CONTAINER_ID);   // same session container as resize placements
const frame = figma.createFrame();
frame.name = "1440×1080 REDDIT-COMMENT";
frame.resize(1440, 1080);
container.appendChild(frame);

const visual = await figma.getNodeByIdAsync(VISUAL_NODE_ID);   // from the MASTER, per Step 2
const crop = visual.clone();
frame.appendChild(crop);

// Position and scale the clone so the chosen focal region fills the 1440x1080 frame.
// This is a crop, not a resize — the intent is to show a fragment large, not the whole
// thing shrunk down. Compute crop.x/crop.y/crop.resize() from the region chosen in Step 4.
```

Nothing else gets added to this frame. If you find yourself reaching for the logo "just in
case" or a text label "for context" — stop; that's R43.

### Step 6 — Gate and deliver

Run the scoped gate below, screenshot, and deliver per `RESIZE-WORKFLOW.md` Step 10's pattern
(screenshot + verdict + accepted gaps + wait for approval) — that part of the process is shared
even though the build steps aren't.

---

## The gate, scoped to what a crop can actually violate

The full three-layer structure still applies (`ACCURACY-GATE.md`), but which rules run is
different:

**Still checked, mechanically:**
- Exact dimensions (R23) — 1440×1080, same as any placement.
- No off-canvas descendants (R25).
- Frame naming and parenting (R28).
- **Composition purity (R43)** — the output has zero visible TEXT nodes, zero logo, zero CTA.
  This is the crop-specific replacement for the entire logo/text/CTA rule set that doesn't apply.

**Vision-owned, no mechanical substitute:**
- Focal point visible and centred (R45) — no face/subject detection is available; this needs a
  human or model actually looking.
- Genuine sub-region, not a shrink-to-fit (R46) — a script can report the image fill's
  `scaleMode` as a supporting fact, but can't judge whether the *chosen* crop is a good one.

**Explicitly does not apply here — do not run these against a crop placement:**
R1–R22 (all composition/geometry/fidelity rules assuming logo/text/CTA exist), R24 (no safe
zone), R26/R42 (no spacing between elements that don't exist), R32–R41 (text-size and CTA rules
— there is no text or CTA).

## Maturity note

Every other placement in this skill has been reasoned through in depth across multiple sessions
and tested against synthetic fixtures. This workflow has not — it's a first pass, written from
the source spec rather than from hands-on iteration. If something about the crop-selection
process (Step 4 especially) turns out to be unworkable against a real master, that's expected
territory to refine, not a sign the rest of the skill is unreliable.

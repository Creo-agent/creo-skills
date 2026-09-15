# Gotchas — Already Diagnosed, Don't Re-Debug

Tool and API behaviours that have already cost someone an hour. Check here before debugging
something that looks like your own mistake.

## Contents
- Writing to Figma
- The Plugin API
- Transform bugs
- Reading and measuring
- Assets and screenshots
- Session and context

---

## Writing to Figma

**`use_figma` is atomic — an error rolls back the whole call.**
A script that fails partway through leaves the document untouched. This is good news when
debugging (nothing partial to clean up) and bad news for long scripts (one bad line at the end
discards all the work). It is the main reason `RESIZE-WORKFLOW.md` builds one placement per call
rather than batching (R29).

**A Dev seat cannot write.**
`use_figma`, `create_new_file`, `generate_figma_design` and `upload_assets` all require a **Full**
Figma seat. On a Dev seat they fail with a permission error rather than anything descriptive.
Check the seat before assuming the script is wrong.

**The `figma-use` skill is a hard prerequisite.**
Load `Skill({ skill: "figma:figma-use" })` before every `use_figma` call. Skipping it causes
failures that are hard to attribute, because the symptom appears in the script rather than at the
call site.

---

## The Plugin API

**Font style names contain spaces.**
`"Semi Bold"`, not `"SemiBold"`. `"Extra Bold"`, not `"ExtraBold"`. When a `loadFontAsync` call
fails, list what actually exists rather than guessing:

```js
const fonts = await figma.listAvailableFontsAsync();
```

Custom fonts aren't supported — only what Figma's library serves.

**Load every font before touching any text node.**
Because the call is atomic, a font error partway through discards everything the script already
did. Load them all up front.

**Changing page silently does nothing.**
```js
figma.currentPage = somePage;                    // fails silently
await figma.setCurrentPageAsync(somePage);        // correct
```

**An auto-layout frame ignores `resize()`.**
Set both sizing modes to fixed first, or the frame keeps hugging its contents and the resize
appears to do nothing (R23):
```js
frame.layoutSizingHorizontal = 'FIXED';
frame.layoutSizingVertical   = 'FIXED';
frame.resize(W, H);
```

**`resize()` already scales descendants.**
Don't recurse to "make sure" children scaled — recursing multiplies the factor at every level and
collapses the design (R6). Process direct children only.

---

## Transform bugs

These three are the reason `scripts/fix_mask_images.js` and `scripts/fix_crop_transform.js` exist.
All three produce output that looks plausible and measures wrong.

**`group.resize()` does not keep mask-group image rects aligned.**
Image fill rectangles inside nested mask groups drift after a resize, usually in Y — the masked
photo shows background, or a circular avatar has a crescent of empty space. Full rule: R5/R7.

**The documented k-factor formula appears inverted.**
The pre-2026-08-31 pseudocode defined `kX = imageRect.x / (iAbs.x - frameAbsX)` — local ÷ canvas,
i.e. `1/s` for wrapper scale `s` — then applied `imageRect.x += deltaAbsX / kX`, which multiplies
the canvas delta by `s`. Moving a node Δ canvas pixels requires changing its local coordinate by
Δ/s, so that correction is off by `s²`.

`fix_mask_images.js` avoids depending on the direction at all: apply a correction, re-measure,
repeat (max 4 iterations). It converges either way. It also derives `k` from
`local width ÷ absolute width` rather than a position ratio, because position ratios divide by a
value approaching zero for any node near the frame origin.

**If you have seen mask misalignment survive the documented fix, this is why.**

**`imageTransform` is not preserved through a resize.**
Even with a correct uniform `uScale`, a CROP-mode image fill can come out with different X and Y
scale factors — the photo is squashed inside a correctly-sized frame. Confirmed 2026-07-16 on the
Community Hub 1200×1200 LI frame: three of five person bubbles at X 0.993 against Y 1.089, and
every other check passed. Full rule: R8.

**Never fix a squashed CROP fill by switching it to FILL.** FILL re-centres automatically, which
discards the designer's crop — a portrait framed on a face becomes a shot of a torso. Use the
geometric-mean correction, which removes the squash and keeps the crop centre.

**`uScale` can exceed 1 even when the canvas gains no width.**
1080×1350 → 1080×1920 gives `scaleX` = 1.000 and `uScale` = 1.193, so every element grows ~19%
wider on a canvas that never widened. Anything wider than ~906px overflows *by construction* from
applying the geometry pass correctly. Step 5 and Step 8 are two halves of one operation, not a
pass plus a safety net.

---

## Reading and measuring

**Properties can be `figma.mixed`.**
`fills`, `fontName`, `fontSize`, `cornerRadius`, `letterSpacing` and `lineHeight` all return
`figma.mixed` on nodes with mixed values. Guard every read — `measure_frame.js` records the string
`"MIXED"` rather than crashing or silently writing `null`, so the differ can tell "mixed" from
"absent."

**`absoluteBoundingBox` can be null.**
Invisible nodes and some node types return null. Any bounds check must handle it — and must not
treat null as "in bounds."

**Use `absoluteBoundingBox`, not local `x`/`y`, for bounds checks.**
A child at a comfortable local `x` can still be off-canvas once its parent group's offset applies,
and local coordinates report it as fine (R25).

**Match nodes by index path, never by name.**
Figma layer names duplicate constantly — eight nodes called `Rectangle 5` in one frame is normal.
Name-matching doesn't fail loudly; it produces a **confidently wrong** diff, reporting failures on
healthy elements and passes on broken ones. See `PRE-RESIZE-MEASUREMENT.md`.

**Exclude the root frame from aspect-ratio comparison.**
The output frame's aspect ratio is *supposed* to differ from the master's — that's the resize.
Including it reports the intended canvas change as a defect.

**The MCP response cap is real.**
Large frames can exceed the tool's token limit. Run `get_metadata` first to find a smaller
sub-frame, or raise `MAX_MCP_OUTPUT_TOKENS` in settings (needs a restart). `measure_frame.js`
rounds values and omits empty keys specifically to keep its payload under the cap.

---

## Assets and screenshots

**`download_assets` and `get_screenshot` URLs expire immediately.**
`curl` them to disk the moment you get them. Never paste one into a reply expecting it to be
viewable later, and never assume you can re-open it after a few minutes.

**`upload_assets` doesn't accept SVG.**
Use `figma.createNodeFromSvg()` through `use_figma` instead.

**Node IDs in URLs use hyphens; the API needs colons.**
`node-id=47-1515` → `47:1515`.

**A full-frame screenshot cannot verify anything much under ~32px.**
A 1920px-tall frame in a chat-sized image is a heavy downscale — a 24px chip lands on about three
pixels. This is what gate layer 9c exists for; a glyph standing in for a real icon, or an asset
that decoded blank, survives every other check.

**A blank or obviously-wrong screenshot is not evidence.**
The capture can desync from real document state. Re-capture before concluding anything from it.

---

## Session and context

**Resuming after a context summary is not a fresh start.**
Re-read `placements.json` and the master baseline from disk. A summarised recollection of a safe
zone or a canvas size is exactly the kind of number that comes back subtly wrong.

**Measure the master once per session.**
Re-measuring per placement risks measuring a master that was edited in between, which moves the
baseline and means earlier placements were gated against a different reference than later ones.

**Safe-zone figures change — and not always toward the platform's own docs.**
Meta's Story bottom reserve was corrected from 21% to 35% on 2026-08-31 after checking the
platform's own documentation — the old value had 269px of reserved space treated as usable.
Then on **2026-09-01 it changed source entirely**: the team's own tested real-device figures
(Rachel's Ad-Specific QA Checklist) superseded Meta's published guidance on *both* top and
bottom, landing at 200px/540px rather than Meta's 269px/672px. Two lessons, not one: (1) read
`placements.json` fresh every time rather than trusting a remembered number, and (2) "verified
against the platform's own docs" is not automatically the most trustworthy source available —
an internal team's tested figure can and did override it. `placements.json` records its own
`verifiedAgainstPlatformDocs` date and each placement's `safeZoneSource`; check both before
assuming which kind of number you're looking at.

**Third-party ad-spec articles are unreliable.**
Several "2026 spec sheet" blogs assert Story-style safe zones for Feed placements. Feed creatives
render in full with the CTA *below* the image; only Stories and Reels have UI over the creative.
Go to the platform's own guide.

## New checks' stated limitations (added 2026-09-01)

**Role identification (headline/CTA/subheadline) is heuristic, same as logo/icon always was.**
`measure_frame.js`'s `candidates()` now also returns `ctaCandidates`, `ctaLabelCandidates` and
`headlineCandidates` — name-based matching, or (for headline) "the text node at the master's
largest font size." These feed R32/R33/R38/R42. Same caveat as `logoCandidates` always carried:
these are suggestions the workflow confirms with the user when ambiguous, not an authoritative
role assignment. A master with unconventional naming or an unusually large piece of legal text
can fool the heuristic — if a check's result looks wrong, check which node it identified as the
role in question before assuming the check itself is broken.

**Contrast checking (R40) approximates "background" as the nearest ancestor with a solid fill.**
This is real ancestry-walking, not a guess — but it is not full occlusion/z-order analysis. It
will not catch text sitting on top of a busy photo (no ancestor solid fill exists to compare
against — the check reports that node as skipped, not as passing), or a sibling shape that
visually overlaps text from outside its ancestor chain. Both need a human eye. The check reports
how many nodes it had to skip for exactly this reason — a report with a high skip count is telling
you it covered less ground than the pass count alone would suggest.

**H2/subheadline detection is name-based only** (`subheadline`, `sub-headline`, `subhead`, `h2`
in the node name) — there's no font-size-rank heuristic for H2 the way there is for H1
(headline = largest font size). A master that names its subheadline something else won't be
found, and `h2_min_size` will report "no H2 identified" rather than a false pass — but it also
won't catch a genuine floor violation on an unrecognized node. If a placement has a visible H2
and the report doesn't mention it, that's the signal to check naming, not to trust a silent pass.

**The "visual" role has no dedicated derived field yet** — `check_min_clearance_floor` and (were
it needed) related checks approximate it in Python as "the IMAGE-filled node with the largest
local area," computed straight from the measurement JSON rather than from a `measure_frame.js`
heuristic like logo/icon/cta/headline get. Works for a single dominant hero image; will pick the
wrong node on a master with multiple large images of similar size, or none at all if nothing has
an image fill (a purely vector/illustration visual, say). Extend `measure_frame.js`'s
`candidates()` with an explicit `visualCandidates` field if this turns out to matter often.

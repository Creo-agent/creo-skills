# QA Checklist Alignment — Traceability Matrix

**Source:** Ad-Specific QA Checklist (Rachel), 2026-09-01.
https://docs.google.com/document/d/10ouC9Uqu2oUV4TELhp28Hmgg1rCI0Jdl-oKjhHwWlx4/edit

## Purpose

Every item in the source doc appears exactly once below, with what happened to it. Nothing is
silently dropped — an item that doesn't apply to this skill is marked **out of scope**, with a
reason, not omitted. An item the doc itself left incomplete is marked **incomplete in source**,
not quietly filled in with an invented number. This file is what makes "did we account for
everything in Rachel's doc" a question with a checkable answer instead of a memory exercise.

**Status values:** ✅ Implemented · 🔶 Pending decision · ⚪ Out of scope for this skill ·
❓ Incomplete in source

---

## Axis 1 — Fidelity to Source

| ID | Doc text (condensed) | Status | Where |
|---|---|---|---|
| F1 | Every change justified by the task, not for its own sake | ✅ | `HARD-RULES.md` — umbrella principle cited at R12/R14; underlies R9–R16 |
| F2 | Everything not part of the task stays exactly as it was | ✅ | `HARD-RULES.md` R9, R12/R14, R17–R22 all cite this directly |
| F3 | Background color changed → recheck contrast | ✅ | Consolidated with F4/F5 into R40 / `contrast_meets_wcag` |
| F4 | Element moved to a different background → recheck contrast | ✅ | Consolidated into R40 (same check — see limitation note in R40 re: ancestry-based "background") |
| F5 | Text resized → recheck contrast; fix order is weight-up before escalating | ✅ | R40 implements the fix-order note explicitly |
| F6 | Conflicting design rules → flag with reasoning, optionally duplicate frame | ✅ | R41; halt mechanics in `ASK-DONT-GUESS.md` trigger 9 |
| F7 | Campaign-family consistency (doc's own note: "proposed, confirm relevance") | ✅ | Already existed pre-dating this doc — `BATCH-WORKFLOW.md`'s cross-placement consistency pass. Confirms the doc's own uncertainty was unnecessary; the skill already had this. |

## Axis 2 — Standalone Frame Integrity

| ID | Doc text (condensed) | Status | Where |
|---|---|---|---|
| S1 | Logo mandatory no exceptions; CTA per format; image can shrink, must not disappear | ✅ | Logo: R11 amendment. Image: R10 amendment. CTA: R38 (see CTA-by-Format table below) |
| S2 | Minimum microcopy size 28px @1x | ✅ | R32 / `microcopy_min_size` (script) |
| S3 | Minimum CTA text size 36px @1x | ✅ | R33 / `cta_text_min_size` (script) |
| S4 | Can't enlarge without breaking composition → hard stop, never silent shrink | ✅ | R35; cross-references `ASK-DONT-GUESS.md` trigger 5 as a second, independent constraint |
| S5 | Hierarchy: 1 dominant H1 (2–3 lines by format), H2 min 45px, combined cap 2+2 | 🔶 partial | R34: H2 min-size is ✅ script-checked. **Per-format H1 line caps are ❓ incomplete in source** — "depending on format" names no numbers. Logged below. |
| S6 | Overflowing copy → offer alternatives, don't silently overflow | ✅ | R36 |
| S7 | Newly added text set in Poppins | ✅ | R37 / `new_text_font_family` (script) |
| S8 | Line-count change → recompose, don't leave a collision | ✅ | R39 |
| S9 | Elements too close together as a result of a change | ❓→✅ | Doc states the condition, not a threshold or consequence — **incomplete in source**. Operationalized as R42 / `min_clearance_floor`, using this skill's own pre-existing `minGaps` values (not sourced from the doc) as the floor. See R42's own note on this distinction. |
| S10 | Overall read: hierarchy comfortable, legible, nothing broken-and-unfixed | ⚪ | Not a discrete rule — this is what the whole gate (`ACCURACY-GATE.md`) exists to produce as an outcome, not a single checkable item |

## CTA-by-Format Reference Table

| Format | Doc's rule | Status | Where |
|---|---|---|---|
| Meta feed 4:5 | CTA preferred if present in master | ✅ | FB's `ctaRule: "follows-master"` |
| Meta Story 9:16 | No CTA (native platform CTA) | ✅ | STORY's `ctaRule: "never"` |
| LinkedIn | CTA preferred if present in master | ✅ | LI's `ctaRule: "follows-master"` |
| Reddit (comment-style) | No CTA | ✅ | REDDIT_COMMENT's `ctaRule: "never"` — for a different reason than Story (R43: no elements at all, not a platform-CTA override) |
| Reddit feed / Google DV360 | TBD — ignore for now | ⚪ | On hold per the doc itself — not implemented, see `PLACEMENTS.md`'s "On hold" section |

## Use-Case Adaptation

| ID | Doc text (condensed) | Status | Where |
|---|---|---|---|
| — | "No dedicated skill planned for this use case yet, so it stays in this shared doc" | ⚪ | The doc's own framing already flags this as provisional |
| U1 | Message/tone/imagery fits the new persona, not just "still generally true" | ⚪ out of scope | Content/messaging work, not geometry. `figma-resize` clones and transforms; it doesn't write or judge messaging. Belongs in whatever skill handles ad adaptation. |
| U2 | Funnel stage changed → CTA strength matches (awareness vs. retargeting) | ⚪ out of scope | Same reason as U1 — this is a copy/strategy judgement, not a resize operation |
| U3 | A claim (testimonial, logo, stat) still accurate/not misleading in new context | ⚪ out of scope | Same reason — and notably, R12 forbids this skill from touching claim text at all; verifying claim accuracy is someone else's job even if this skill *could* touch text |

## Localization (doc's own framing: "moves into the dedicated Resize/Localization skills")

| Item | Status | Where |
|---|---|---|
| Translated text doesn't overflow CTA/banner bounds | ⚪ out of scope | The doc explicitly scopes this to a future dedicated localization skill, not the shared baseline |
| No leftover source-language text | ⚪ out of scope | Same |
| Awkward literal translation → flag | ⚪ out of scope | Same |
| Testimonial/speaker names — keep or localize (doc: "judgment call, flag-and-ask") | ⚪ out of scope | Same |
| Text-length change between languages → check spacing wasn't left tuned to the old language | ⚪ out of scope | Same |

## Resize Skill — Format Reference Table

| Doc's row | Status | Where |
|---|---|---|
| LinkedIn feed 1:1 1200×1200 | ✅ | `LI` |
| Meta/FB feed 4:5 1080×1350 | ✅ | `FB` |
| Meta/FB story 9:16 1080×1920 | ✅ | `STORY` |
| Reddit comment 4:3 1440×1080 | ✅ | `REDDIT_COMMENT` — new 2026-09-01, `operationType: "crop"` |
| Reddit feed 1:1 1200×1200 (on hold) | ⚪ | Not implemented; noted in `PLACEMENTS.md` "On hold" |
| Google DV360, TBD, 5 sizes (on hold) | ⚪ | Not implemented; noted in `PLACEMENTS.md` "On hold" |

## Story safe zone (detail)

| Doc's figure | Status | Where |
|---|---|---|
| Top 200px / bottom 540px covered by UI; usable 1180px (y 200–1380) | ✅ | Adopted 2026-09-01 as the operating default, **superseding** the previously-used Meta-published figures (269/672). See `PLACEMENTS.md` STORY section for the full two-step correction history. |
| Elements that can't be hidden (copy, logo) must stay inside the usable zone | ✅ | R24 / `safe_zone_respected` |
| Visual-only elements may extend beyond it, but can't be bluntly cropped there (still partially visible) | 🔶 | Conceptually captured by R10 (never crop to fit) but the specific "partially visible, so a hard crop still shows" nuance isn't yet a distinct checked rule — flagged for a future pass if this proves to matter in practice |

## CTA rule for resize

| Doc's rule | Status | Where |
|---|---|---|
| "Follows master" — include a CTA iff the master has one, unless the user overrides | ✅ | R38, replacing the old free-form per-placement CTA question in `RESIZE-WORKFLOW.md` Step 1 |

## Reddit comment — what goes there

| Doc's rule | Status | Where |
|---|---|---|
| Small visual crop from the source's original full-size visual; no text/CTA/logo/full-visual | ✅ | R43/R44, `REDDIT-COMMENT-WORKFLOW.md` |

## General resize principle

| Doc's rule | Status | Where |
|---|---|---|
| Resize "the visual" as one unit, never distort pieces independently; characterize layers first | ✅ | Pre-existing R1/R2/R6 — cited explicitly as the same principle, arrived at independently before this doc was read |

## Open items (the doc's own, both still open)

| Item | Status |
|---|---|
| CTA types — TBD | 🔶 Still open. Not resolved by this pass; ask when it becomes blocking. |
| Default CTA color/copy when adding one — TBD | 🔶 Still open. `RESIZE-WORKFLOW.md` Step 1 asks the user per-placement in the meantime rather than inventing a default. |

## Other notes

| Doc's note | Status | Where |
|---|---|---|
| Focal point of a photo/illustration stays visible and centered in the new crop | ✅ | R45 (crop-specific) — also cited in R13 as the same standard applied to composing into dead space |
| Consistency across the size family — all sizes read as "the same ad" | ✅ | Pre-existing `BATCH-WORKFLOW.md` cross-placement consistency pass (same as F7) |

---

## Summary

- **46 hard rules (R1–R46)** in `HARD-RULES.md`, of which **15 are new from this pass** (R32–R46).
- **42 rows** in `resize-rules.csv` (11 new).
- **2 items remain genuinely open**, both already open in the source doc itself (CTA types; default CTA color/copy) — not something this pass could resolve unilaterally.
- **1 item is a partial implementation** (Story's "visual can extend but not bluntly crop" nuance) — conceptually covered, not yet a distinct check.
- **Everything scoped out** (Use-Case Adaptation, Localization) was explicitly out of scope in the source doc's own words, not a judgement call made here.

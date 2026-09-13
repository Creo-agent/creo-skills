# QA Scorecard — Rubric and Report Format

## Contents
- Two layers, only one decides
- Why the 100-point rubric was retired
- The informational readout
- Ordering findings
- Per-placement report format
- Set-level report format
- Where reports live

---

## Two layers, only one decides

**1. `resize-rules.csv` — the pass/fail layer.**
A placement is DONE iff zero `hard`-severity rules fail. Strict, per placement, no averaging.
This is the verdict. Full statement in `ACCURACY-GATE.md`.

**2. The four-dimension readout below — informational only.**
A 1–10 gut-check that makes placements comparable at a glance in a report. It **never** overrides,
softens or substitutes for the hard-rule verdict. A placement can read 9/10 across all four
dimensions and still be NOT DONE because one hard rule fails — most often one the four dimensions
structurally cannot see.

Keeping these separate is deliberate. The readout exists because "how did this one go?" is a real
question with a useful short answer. It stops being useful the moment it can be mistaken for the
verdict.

## Why the 100-point rubric was retired

The previous scorecard started at 100 and deducted: Fatal −100, Major −30, Minor −10, with
verdicts at 100 (ship), 80–99 ("Conditional Pass — fix spacing only"), ≤79 (reject).

Two problems, both structural rather than matters of tuning:

- **It licensed shipping with real defects.** Two Minor defects score 80 — inside "Conditional
  Pass," i.e. ship it. Three of five person bubbles squashed by a non-uniform `imageTransform`
  is not a spacing nit, but nothing in a deduction model stops it landing in a passing band.
- **Arithmetic invites offsetting.** A score is a single number, and a single number implies that
  many small passes can compensate for one serious failure. They cannot. An avatar with a
  9% aspect distortion is wrong regardless of how many other checks were clean.

Binary hard rules remove the arithmetic. A rule either holds or it does not, and the report says
which. Severity ordering within the failures comes from the CSV's `weight` column — used to
decide *what to fix first*, never to compute a total.

**The Fatal / Major / Minor vocabulary is retired with it.** Two competing severity vocabularies
in one skill is how findings get quietly re-graded into a passing band. `hard` and `soft` from the
CSV are the only severities.

## The informational readout

| Dimension | What it covers | Rules it draws on |
|---|---|---|
| **Geometry integrity** | squash, distortion, rotation, mask alignment, CROP transforms | R1–R9 |
| **Content fidelity** | text verbatim, logo count, icons, colours, gradients, effects, type | R11–R12, R14, R16–R22 |
| **Placement & bounds** | exact dimensions, safe zones, off-canvas, naming | R23–R25, R28 |
| **Composition** | spacing relationships, balance, dead space, background extension | R10, R13, R26–R27 |

Score 1–10: **10** = indistinguishable from a correct resize · **8–9** = minor delta ·
**6–7** = noticeable but functional · **4–5** = structural problems · **1–3** = wrong.

## Ordering findings

Within the report, order failures by the CSV `weight`, descending — highest weight first. That
puts `text_content_verbatim` (1.0) and `exact_dimensions` (1.0) above
`frame_named_and_parented` (0.7), which is the order you actually want to fix them in.

Weight orders the work. It does not produce a total.

## Per-placement report format

Save to `<deliverables>/<placement>-qa-report-v<NN>.md` and show it in-session.

```markdown
# Resize QA — 1080×1920 STORY
**Version:** v01  **Date:** YYYY-MM-DD
**Master:** <figma-url>  ·  1080×1350
**Output:** <frame name>  ·  1080×1920  ·  Generated Ad Sizes 1
**Baseline:** measure-master.json  ·  **Output measurement:** measure-STORY-v01.json

## Verdict
**NOT DONE — 2 hard rules failing**

| Layer | Result |
|---|---|
| 9a Vision | run — 2 findings |
| 9b Measurement diff | run — 47/47 nodes matched, 2 hard / 1 soft |
| 9c Element zoom | run — 6 components inspected, 1 finding |

| Dimension (informational) | Score |
|---|---|
| Geometry integrity | 5/10 |
| Content fidelity | 9/10 |
| Placement & bounds | 10/10 |
| Composition | 7/10 |

## Hard-rule failures
| Rule | R | Node | Expected | Measured |
|---|---|---|---|---|
| crop_transform_uniform | R8 | 0/3/1 "Avatar 3" | X≈Y | X 0.993 / Y 1.089 |
| geometry_aspect_ratio_preserved | R1/R2/R9 | 0/3/4 "Avatar 5" | 1.000 | 1.087 (+8.7%) |

## Soft findings
| Rule | R | Detail |
|---|---|---|
| spacing_proportional | R26 | text→visual gap expected ≈0.83×, measured 1.41× |

## What is good
- Text verbatim across all 6 nodes; no paraphrase or retype
- All content inside the Meta safe zones (y 269–1517, x 65–1015)
- Logo count, colours, gradients and effects all preserved

## Accepted gaps
| Rule | Reason | User informed |
|---|---|---|
| composition_no_dead_space | 1:1 → 9:16 leaves ~430px with no source material; four options offered | yes — awaiting choice |

## Fixes for the next pass
1. Re-run `fix_crop_transform.js` on the visual group — bubbles 3 and 5 kept non-uniform
   transforms. Verify X and Y land within 1% of each other afterwards.
2. Reduce the text→visual gap to ~0.83× of master proportion (currently 1.41×).
```

If a placement passes with nothing to report, still write the report. "Ran clean" and "never ran"
must be distinguishable later — including to you, after a context summary.

## Set-level report format

After every placement in a batch is individually DONE, add one set-level report covering what no
single placement can check (`BATCH-WORKFLOW.md`):

```markdown
# Resize QA — Set Summary
**Placements:** 1080×1920 STORY · 1080×1350 FB · 1200×1200 LI
**Container:** Generated Ad Sizes 1
**Shared baseline:** measure-master.json

| Placement | Verdict | Hard failures | Accepted gaps |
|---|---|---|---|
| 1080×1920 STORY | DONE | 0 | 1 (dead space — user chose brand bar) |
| 1080×1350 FB | DONE | 0 | 0 |
| 1200×1200 LI | DONE | 0 | 0 |

## Cross-placement consistency
| Check | Result |
|---|---|
| CTA label identical | ✓ "Get started free" on all three |
| CTA colour identical | ✓ white |
| Logo treatment consistent | ✓ |
| Exclusions deliberate | ✓ integration row excluded from STORY only, confirmed |
| Same baseline throughout | ✓ |

## Set coherence
One-paragraph read of the three together: do they look like one campaign?
```

## Where reports live

Reports and screenshots go to the session's deliverables folder and are shown in-session. There
is **no Slack copy step** — that was removed so the skill stays portable across harnesses.

Versioning: `v01`, `v02` per fix pass on the same placement. Append fix passes to the same file
rather than creating a new one per attempt, so the file reads as the history of that placement.
Start a new file only for a genuinely new QA session on the same placement.

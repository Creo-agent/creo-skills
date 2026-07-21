# Product Design QA — Run Procedure

Visual accuracy gate before any animation work begins. Validates HTML/CSS against Figma using
a weighted rubric — score ≥95 to pass. Issues a fix-prompt report on failure.

## Step 0 — Standalone setup (skip if called by the orchestrator)

If invoked directly, ask for:
- **HTML/CSS file** — path or inline content to validate. Required.
- **Figma design** — URL or exported image at the same viewport. Required.
- **Timeline plan** *(if available)* — used to check that all `data-anim-id` hooks a planned
  event references are present in the markup.
- **Viewport** — the size the HTML was built at (e.g. 1440×900). Must match the declared
  viewport in the file comment.

Render the HTML at the declared viewport before proceeding. Take a screenshot.

## Step 1 — Side-by-side visual comparison

Take a screenshot of the rendered HTML at the declared viewport. Compare directly against the
Figma export at the same dimensions. Note areas that look off before diving into measurements.

## Step 2 — Token-level verification (do not eyeball)

For each design token in use, compare the computed CSS value against the design source:

| Token type | How to verify |
|---|---|
| Color | `getComputedStyle(el).color / backgroundColor / borderColor` → compare to hex from Figma |
| Typography | `getComputedStyle(el).fontFamily / fontSize / fontWeight / lineHeight` |
| Spacing | `getComputedStyle(el).padding / margin / gap` |
| Border | `getComputedStyle(el).borderRadius / borderWidth` |

A color that is "close" (e.g. `#1F2D3D` vs `#1E2D3C`) is still a mismatch — flag it.

## Step 3 — Structural verification

Confirm layout behavior mirrors Figma's auto-layout structure:
- Flex/grid direction, alignment, and wrapping match
- Gap and padding values match at each nesting level
- Absolute-positioned elements are within ±4px of their Figma coordinates at the declared viewport

## Step 4 — Asset verification

- Logos and icons are the correct assets (not placeholders)
- Images/icons are at the correct resolution and dimensions (not stretched or distorted)
- Fonts are loading (not falling back to a system font) — check `document.fonts.ready`

## Step 5 — Score using the rubric

Each dimension is scored 0–1; multiply by weight for the weighted contribution.

| Dimension | Weight | How to measure | Hard-fail threshold |
|---|---:|---|---|
| Positioning | 25 | `offsetLeft/Top` vs `figmaX/Y × scale` | Any element >16px off |
| Spacing / padding / gaps | 20 | Computed `padding`, `gap`, `margin` vs Figma auto-layout values | — |
| Color fidelity | 15 | Computed colors vs design token hex values | Wrong prominent color |
| Typography | 15 | Font family, size, weight, line-height | — |
| Token adherence | 10 | Are token values used consistently (not ad-hoc hex/px)? | — |
| Structure / hierarchy | 10 | DOM hierarchy matches Figma frame nesting | — |
| Radii / stroke | 5 | `borderRadius`, `borderWidth` vs Figma | — |
| **Total** | **100** | | |

**Hard-fail overrides** (cap the total below 95 regardless of weighted sum):
- Missing or extra element vs the Figma design
- Any element mispositioned by >16px
- Wrong prominent color (background, headline text, primary button fill)
- Broken or missing asset
- Missing `data-anim-id` hook on any element the timeline plan references

`pass = weighted_score ≥ 95 AND no hard-fail`

## Output

```markdown
# Design QA Report: [Design Name]

## Result: PASS / FAIL
## Score: XX / 100   (pass ≥ 95 AND no hard-fail)

## Dimension Scores
| Dimension | Weight | Score (0–1) | Weighted |
|---|---:|---:|---:|
| Positioning | 25 | 0.98 | 24.5 |
| Spacing/padding/gaps | 20 | 0.90 | 18.0 |
| Color fidelity | 15 | 1.00 | 15.0 |
| Typography | 15 | 1.00 | 15.0 |
| Token adherence | 10 | 0.95 | 9.5 |
| Structure/hierarchy | 10 | 1.00 | 10.0 |
| Radii/stroke | 5 | 1.00 | 5.0 |
| **Total** | **100** | | **97.0** |

## Hard-fail overrides triggered: none

## Issues Found
| Element | Property | Expected | Actual | Severity | Fix-prompt |
|---|---|---|---|---|---|
| table-row-3 | padding | 12px 16px | 10px 16px | Minor | Set `padding: 12px 16px` on `.table-row` |

## Recommendation
Pass to product-animation + cursor-animation / Send back to product-design-recreation
```

## Handoff

- **PASS** → forward markup/CSS to `product-animation` and `cursor-animation`.
- **FAIL** → send the report with fix-prompts back to `product-design-recreation` for a targeted
  fix (never a full rebuild), then re-run this QA skill. If this is the **third consecutive FAIL**
  on the same artifact, stop and escalate to the user — do not loop further.

# Design QA rubric — the ≥95 gate (product-design-qa)

`score = Σ(dimension_score × weight)`, each `dimension_score ∈ [0,1]`, total 0–100. **Pass ≥ 95.**
The threshold is intentionally strict — do not soften it to escape a fix loop. On a sub-95 score,
emit a precise fix-prompt (`element + property + current→expected`) and route back to
`product-design-recreation` as a **targeted edit**; never rebuild from scratch.

This replaces any "estimate a percentage" step: the score is *computed* from the dimensions below,
not eyeballed. The loop that consumes it is `workflows/design-qa-loop.js`. (Adapted from the sibling
[`../../figma-to-animation/references/rubric.md`](../../figma-to-animation/references/rubric.md).)

## Dimensions & weights (sum = 100)

| Dimension | Weight | Full credit (score 1.0) | Penalty model |
|---|---:|---|---|
| Element positioning | 25 | every element's `offset{Left,Top}` == `figmaX/Y × scale` | per element: full ≤±2px, linear→0 at ±16px, averaged over elements |
| Spacing / padding / gaps | 20 | gaps/padding match Figma auto-layout (px or token) | same ±2px→±16px band |
| Color fidelity | 15 | exact hex/token on every fill, stroke, text | exact=1; small ΔE tolerance; a visible mismatch is heavy |
| Typography & text alignment | 15 | family, size, weight, line-height, letter-spacing, alignment all match | fraction of properties correct |
| Design-token correctness | 10 | tokenizable props use the *right* design-system variable, not a look-alike literal | fraction using the correct token |
| Structure / hierarchy / z-order | 10 | nesting, containment, paint order match Figma | checklist fraction |
| Corner radii & stroke width | 5 | radii and stroke widths match | full ≤±1px, linear→0 at ±8px |

## Hard-fail overrides (cap the total below 95 regardless of the weighted sum → force a fix loop)
- Any **missing or extra** element vs the Figma frame.
- Any element **mispositioned > 16px**.
- **Wrong color** on a prominent element (background, primary text, key shape, brand/logo).
- A **broken / distorted / missing asset** (image fails to load, wrong aspect ratio, stretched icon).
- **Missing an animation hook** the timeline plan requires — every element the plan marks interactive
  must carry its stable `data-anim-id` (see product-design-recreation). A build with no target for a
  planned event cannot pass, because animation would have nothing to attach to.

## How to measure each dimension (reuse the engine skills — don't invent a method)
- **Positions & sizes** — Figma MCP `get_metadata` for each node's `x/y/w/h`; in the build read
  `offsetLeft/Top/Width/Height` and compare to `figmaValue × scale` (the
  [`../../frame-building/`](../../frame-building/) verify method). Respect the measurement discipline in
  the shared [`knowledge.md`](knowledge.md) (scaled-stage getBCR vs offsetWidth; magnitude-check).
- **Colors, type, tokens** — `get_variable_defs` and `get_design_context` for the token/variable a
  prop *should* use; compare against the built CSS. Prefer **token identity**, not just a matching
  literal (`#0073EA` matching by luck is not the same as using the design-system color token).
- **Visual overlay** — `get_screenshot` of the source frame vs a screenshot of the build at the
  timeline viewport, compared element-by-element (same corners, overlaps, relative sizes). Screenshot
  comparison alone is **not** sufficient — always pair it with the structured/measured checks.
- **Rendered critique** — run the built HTML through the `design-critique` skill for a systematic pass
  on visual polish, alignment, and hierarchy. Treat its findings as inputs to the
  structure/typography/spacing dimensions, not a separate score.
- **Build technique** — the recreation itself should use [`../../frame-building/`](../../frame-building/):
  build at natural size + one outer `transform: scale(N)`, node geometry `figmaValue × scale`, on its
  fixed `.stage-scaler` stage, then assert `getBoundingClientRect().width === figmaWidth × scale`.

## Fix-prompt format (what design-qa hands back to recreation)
> `.detail-panel`: `padding` is 12px, should be 24px (token `spacing-lg`).
> `.avatar-circle`: `left` is 246px, should be 232px (figmaX 174 × scale 1.333). Off by 14px.

Name the element (by `data-anim-id`/selector), the property, the current value, and the expected
value (with the token or the `figma×scale` derivation). Vague feedback ("spacing looks off") is not
acceptable and will not converge the loop.

## Note
Weights are the pipeline default. A project may tune them (e.g. a type-dense dashboard may raise
Typography), but any change is a deliberate config choice, not a way to pass a failing build. Do not
lower the ≥95 threshold.

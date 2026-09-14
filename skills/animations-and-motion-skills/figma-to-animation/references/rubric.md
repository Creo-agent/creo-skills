# Static QA rubric (Skill 04) — the ≥95 gate

`score = Σ(dimension_score × weight)`, each `dimension_score ∈ [0,1]`, total 0–100. **Pass ≥ 95.**
The threshold is intentionally strict — do not soften it to escape a fix loop. On a sub-95 score,
emit a precise fix-prompt (`element + property + current→expected`) and route to `03-build-frame`;
never rebuild from scratch.

## Dimensions & weights (sum = 100)

| Dimension | Weight | Full credit (score 1.0) | Penalty model |
|---|---:|---|---|
| Element positioning | 25 | every element's `offset{Left,Top}` == `figmaX/Y × scale` | per element: full ≤±2px, linear→0 at ±16px, averaged over elements |
| Spacing / padding / gaps | 20 | gaps/padding match Figma (px or token) | same ±2px→±16px band |
| Color fidelity | 15 | exact hex/token on every fill, stroke, text | exact=1; small ΔE tolerance; a visible mismatch is heavy |
| Typography & text alignment | 15 | family, size, weight, line-height, letter-spacing, alignment all match | fraction of properties correct |
| Design-token correctness | 10 | tokenizable props use the *right Figma variable*, not a look-alike literal | fraction using the correct token |
| Structure / hierarchy / z-order | 10 | nesting, containment, paint order match | checklist fraction |
| Corner radii | 5 | radii match | full ≤±1px, linear→0 at ±8px |

## Hard-fail overrides (cap the total below 95 regardless of the weighted sum → force a fix loop)
- Any **missing or extra** element vs the Figma frame.
- Any element **mispositioned > 16px**.
- **Wrong color** on a prominent element (background, primary text, key shape).
- A **broken / distorted / missing asset** (image fails to load, wrong aspect ratio).

## How to measure each dimension (reuse existing skills — don't invent a new method)
- **Positions & sizes** — `figma:get_metadata` for each node's `x/y/w/h`; in the build read
  `offsetLeft/Top/Width/Height` and compare to `figmaValue × scale` (this is exactly the
  `frame-building` §5 verify method). Respect the measurement discipline in
  `references/knowledge.md` (scaled-stage getBCR vs offsetWidth; magnitude-check).
- **Colors, type, tokens** — `figma:get_variable_defs` and `figma:get_design_context` for the
  token/variable a prop should use; compare against the built CSS. Prefer token identity, not just
  a matching literal.
- **Visual overlay** — `figma:get_screenshot` of the source frame vs a screenshot of the build,
  compared element-by-element (same corners, overlaps, relative sizes). Screenshot comparison alone
  is **not** sufficient — always pair it with the structured/measured checks above.
- **Rendered critique** — run the built frame through `design-critique` (the website/UI QA method)
  for a systematic pass on visual polish, alignment, and hierarchy that complements the numbers.
  Treat its findings as inputs to the structure/typography/spacing dimensions, not a separate score.

## Fix-prompt format (what 04 hands back to 03)
> Frame 2 — `.headline`: `margin-top` is 12px, should be 24px (token `spacing-lg`).
> Frame 2 — `.avatar-circle`: `left` is 246px, should be 232px (figmaX 174 × scale 1.333). Off by 14px.

Name the element, the property, the current value, and the expected value (with the token or the
`figma×scale` derivation). Vague feedback ("spacing looks off") is not acceptable and will not
converge the loop.

## Note
Weights are the pipeline default. They can be tuned per project (e.g. a type-heavy poster may raise
Typography), but any change is a deliberate config choice, not a way to pass a failing frame.

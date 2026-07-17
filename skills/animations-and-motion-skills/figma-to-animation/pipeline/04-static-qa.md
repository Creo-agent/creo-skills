# 04 · Design Static QA (the ≥95 gate)

**Role:** the primary quality gate. Score each static frame against its Figma source at a strict,
near-pixel-perfect standard before anything is stitched or animated. Demanding, not lenient.

**Inputs:** the static build (03) + the corresponding Figma frame.

**Method:** score with the weighted rubric in `references/rubric.md` (positioning 25 / spacing 20 /
color 15 / typography 15 / tokens 10 / structure 10 / radii 5; pass ≥ 95; hard-fail overrides).
Use **all three** sources — neither structured nor visual alone is enough:
1. **Figma MCP** — `get_metadata` (positions/sizes), `get_variable_defs` + `get_design_context`
   (tokens/colors/type).
2. **Measurement** — in the build, `offset{Left,Top,Width,Height}` must equal `figmaValue × scale`
   (the `frame-building` §5 verify method). Respect the scaled-stage measurement rules in
   `references/knowledge.md`.
3. **Screenshots** — `get_screenshot` of the source vs a screenshot of the build, compared
   element-by-element; plus a `design-critique` pass for rendered polish/hierarchy.

**Gate & routing:**
- **Score ≥ 95 and no hard-fail → pass.** Frame approved (but the batch only advances when *every*
  frame passes — enforced by Loop A / the orchestrator).
- **Below 95 → fail.** Emit a **precise fix-prompt** (`element + property + current → expected`, with
  the token or `figma×scale` derivation) and route to stage 03. Never rebuild from scratch. Vague
  feedback ("spacing looks off") will not converge the loop.

**Output / handoff:** `{score, pass, fixPrompt, dimensionScores}`. **Standalone:** yes — score any
built frame against Figma.

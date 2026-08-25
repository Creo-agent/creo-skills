# Product Design QA

**What it does:** Validates HTML/CSS output from `product-design-recreation` against its Figma source using a 7-dimension weighted rubric (≥95 to pass). Issues a scored pass/fail report with per-dimension breakdowns and fix-prompts on failure.

**When to use:** Immediately after `product-design-recreation`, before any animation work begins. Also re-run after each fix iteration until the score clears 95.

**Input:** HTML/CSS file, Figma design URL or export, declared viewport size, optionally a timeline plan to check `data-anim-id` completeness.

**Output:** A scored QA report. On pass: clears for animation. On fail: returns fix-prompts to `product-design-recreation`.

**Next step (pass):** `product-animation` + `cursor-animation` can begin in parallel.

Last updated: 2026-07-16 · Owner: Elior Siegelwachs

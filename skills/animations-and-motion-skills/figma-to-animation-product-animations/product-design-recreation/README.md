# Product Design Recreation

**What it does:** Turns a Figma product UI design into pixel-accurate, animation-ready HTML/CSS — matching the design system exactly and tagging every interactive element with a `data-anim-id` hook for downstream animation and cursor targeting.

**When to use:** When you need accurate static markup from a Figma product design before any animation work begins. Invoke standalone with a Figma URL, or as the first execution step inside `figma-to-animation-product-animations`.

**Input:** Figma design URL or export, viewport size (default 1440×900), optionally a timeline plan from `product-animation-planning`.

**Output:** Static HTML/CSS at resting state + a `data-anim-id` manifest.

**Next step:** Run `product-design-qa` to validate against the Figma original (≥95 accuracy gate) before handing off to `product-animation`.

Last updated: 2026-07-16 · Owner: Elior Siegelwachs

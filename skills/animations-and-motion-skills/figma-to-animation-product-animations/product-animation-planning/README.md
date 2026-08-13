# Product Animation Planning

**What it does:** Analyzes a Figma product design and produces a detailed, timestamped animation timeline — the source of truth for every downstream skill. No code is written; the output is a precise spec.

**When to use:** First step whenever a product UI needs to become an animated prototype and no timeline exists yet. Also re-run if the design changes significantly.

**Input:** Figma design URL, export, or screenshot. Optionally: viewport size (default 1440×900) and intent notes about which flow to animate.

**Output:** `timeline.md` — a markdown table mapping time → label → event → element → type → duration → easing → dependencies.

**Next step:** Pass the timeline to `product-design-recreation` (for HTML/CSS), `product-animation` (for motion code), and `cursor-animation` (for cursor paths). They can all read from the same plan.

Last updated: 2026-07-16 · Owner: Elior Siegelwachs

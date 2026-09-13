# Product Animation QA

**What it does:** Final timing and sync gate before export. Reads actual tween values off the shared GSAP `master` and validates them against the original timeline plan — event completeness, timing accuracy (±50ms), cursor↔UI sync (0ms offset), easing fidelity, dependency ordering, and coherence.

**When to use:** After both `product-animation` and `cursor-animation` have completed. Also re-run after each fix iteration.

**Input:** Animated HTML file, `timeline.md` from `product-animation-planning`, declared viewport size.

**Output:** A pass/fail QA report. On pass: clears for export. On fail: returns fix-prompts to `product-animation` or `cursor-animation`.

**Next step (pass):** `export-as-gif` for GIF/MP4 render.

Last updated: 2026-07-16 · Owner: Elior Siegelwachs

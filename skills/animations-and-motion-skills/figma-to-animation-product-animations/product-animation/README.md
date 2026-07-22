# Product Animation

**What it does:** Applies GSAP motion to QA-approved product HTML/CSS following the timeline plan exactly. Every tween lives on one shared `master` GSAP timeline at a label from the plan — the cursor and UI animate in frame-accurate sync with zero offset.

**When to use:** After `product-design-qa` passes, using the timeline plan from `product-animation-planning`. Runs in parallel with `cursor-animation` — both write to the same shared master.

**Input:** QA-approved HTML/CSS, `timeline.md` from `product-animation-planning`, and a shared `timeline.js` master (creates it if missing).

**Output:** Animated HTML/CSS/JS with all timeline events on `master` + an implementation note.

**Next step:** `product-animation-qa` validates timing and sync before export.

Last updated: 2026-07-16 · Owner: Elior Siegelwachs

# Cursor Animation

**What it does:** Animates a realistic mouse cursor moving across a product UI — natural easing between positions, human-like movement paths, and a click/press effect — synced frame-accurately to UI animations by sharing the same GSAP master timeline.

**When to use:** In parallel with `product-animation`, after a timeline plan from `product-animation-planning` exists and the HTML/CSS has been built. Both skills write to the same shared `master`, so no external sync is needed.

**Input:** HTML/CSS product prototype, `timeline.md` from `product-animation-planning`, shared `timeline.js` master (creates it if missing). Optional cursor SVG (a default is provided in PROMPT.md).

**Output:** Cursor element + animation tweens on the shared master + a cursor event log for QA.

**Next step:** `product-animation-qa` validates cursor↔UI sync (0ms tolerance) before export.

Last updated: 2026-07-16 · Owner: Elior Siegelwachs

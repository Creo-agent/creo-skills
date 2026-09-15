# Figma-to-Web Skill — Improvement TODO

**Note:** all items below marked "Done" (through item 7, the Visual Diff Tool) have been merged
into this skill's `reference/HARD-RULES.md` (H31–H45), `SECTION-WORKFLOW.md`,
`FULL-PAGE-WORKFLOW.md`, and `tools/visual_diff.py` / `tools/diff_enrich.py`. This file is kept
as the historical record of the request; it is not re-litigated here.

## Source
Feedback from Elior (Aug 30, 2026) in Agentic Design Playground group.
Based on analysis of Yotam's successful sessions vs non-expert sessions.

---

## 1. Replace Scout Questionnaire with Build Plan Table
**Status:** ✅ Done (Aug 30, 2026)
**File:** `reference/SECTION-WORKFLOW.md` (Step 3)

**Current:** Turn 1 posts a screenshot and asks 4 questions (Purpose, Interactivity, Copy notes, Page slug). Waits for answers.

**Proposed:** Turn 1 analyzes the Figma, runs Clay matching (Phase 1 Resolve), and presents a build plan table for approval:

| Section | Clay Match | Confidence | Plan |
|---------|-----------|------------|------|
| Hero split | HeaderSection/Split | Exact | Use Clay render, swap content |
| Logo strip | CustomerLogoSection | Exact | Same component, update logos |
| Features tabs | No match | — | Build from scratch, atoms+tokens |

User approves or corrects the plan — no questionnaire.

## 2. Predefined Defaults (Never Ask)
**Status:** ✅ Done (Aug 30, 2026)

These should be stated as assumptions, not questions:
- **Font:** Poppins (main font — only flag if Figma shows something different)
- **Breakpoints:** 899px mobile (Clay standard)
- **Color palette:** From Clay tokens / Figma variables
- **Container:** Clay layout tokens
- **Image handling:** Cloudinary upload, 2x retina
- **QA:** Per-section vision comparison (always on)

## 3. Conditional Questions Only
**Status:** ✅ Done (Aug 30, 2026)

**Interactivity/Forms/Animations:** Only ask if actually detected in the Figma or reference page. If the section is static, don't ask "is there interactivity?" — just state "this section is static, no interactions detected."

The existing `ASK-DONT-GUESS.md` triggers should be the ONLY reason to ask — not a default behavior.

## 4. Don't Re-Ask What's in the Brief
**Status:** ✅ Done (Aug 30, 2026)

If the user already provided information in their initial message (page name, Figma link, purpose, interactivity details), never ask for it again. Extract answers from the brief first, only ask about gaps.

## 5. Build Plan Table = Section-by-Section Component Map
**Status:** ✅ Done (Aug 30, 2026) — merged into item 1

The build plan table (item 1) should show:
- Where Clay components will be used (and which ones)
- Where components from other live pages will be borrowed
- Where building from scratch is needed
- This is essentially a "plan for the page" that the user approves before any code is written

This replaces the old "Type A (PMO reference) vs Type B (new component)" split from page-builder with real Clay resolution results.

## 6. Change Request Workflow
**Status:** ✅ Done (Aug 30, 2026)
**File:** `reference/SECTION-WORKFLOW.md` (new section after Turn 2)

Added a structured workflow for post-build change requests: scope → re-measure → fix → QA section → verify full page → report. Same tools as initial build, scoped to what changed. Lightweight shortcut only for pure content swaps with no CSS changes.

---

## 7. Visual Diff Tool — Figma vs Built HTML Overlay
**Status:** ✅ Done (Aug 30, 2026)
**Files:** `tools/visual_diff.py`, `tools/diff_enrich.py`

Two-tool pipeline:

**visual_diff.py** — Pixel-level comparison between Figma reference screenshot and built HTML screenshot.
- Side-by-side image with red bounding boxes on diff regions (always generated)
- Overlay blend at 50% opacity (when diff > threshold)
- Delta heatmap — white = identical, red = different (when diff > threshold)
- SSIM score + pixel diff percentage
- DOM element mapping via optional --dom-map JSON
- Diff type classification: layout, spacing, color, missing_element
- Anti-aliasing noise suppression via Gaussian blur + sensitivity threshold
- Default threshold: 5% pixel diff

**diff_enrich.py** — Enriches the diff report with Figma-vs-HTML property comparisons.
- Fetches Figma node properties (depth=10) for the section
- Extracts computed CSS from the built HTML via Playwright
- Matches diff regions to both Figma nodes and DOM elements by bounding box overlap
- Compares: font-size, font-weight, font-family, line-height, letter-spacing, color, padding, gap, border-radius, width, height
- Outputs actionable fix brief: "padding-top is 40px, Figma says 23px. Fix: padding-top: 23px;"
- Deduplication: same property fix on same DOM element reported only once
- Tolerance: pixel values within 1.5px treated as equal

**Usage in QA flow:**
1. Export Figma section screenshot at 2x scale
2. Take HTML screenshot at 2x (deviceScaleFactor=2) via Playwright
3. Run visual_diff.py → diff images + report JSON
4. Run diff_enrich.py → enriched report with CSS fix suggestions
5. Agent reads fix brief → fixes CSS → re-screenshots → re-diffs until threshold passes

## 8. Non-Expert Onboarding — Graceful Fallback for Screenshot Users
**Status:** Planned

The skill currently requires a Figma URL with `?node-id=`. Users like Amit or Beja send screenshots or verbal descriptions instead. The skill should:
- Detect when a user sends a screenshot/image instead of a Figma URL
- Guide them step-by-step: "Select the section frame in Figma → right-click → Copy link → paste here"
- If they can't provide a Figma link (no Figma access), offer a degraded mode: use the screenshot as the reference, extract specs manually, flag lower accuracy
- Never just fail with "I need a URL" — help them get there

---

## Implementation Notes
- Only change Turn 1 (scout/intake). Turn 2 (build engine) stays untouched.
- Clay resolution engine, QA gate, hard rules — all unchanged.
- This should make figma-to-web usable by non-experts (Amit, Beja, Adi) without needing Yotam-level technical input.
- Goal: figma-to-web becomes a viable alternative to page-builder, not just a developer tool.

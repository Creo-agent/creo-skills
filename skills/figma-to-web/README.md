# Figma to Web — Pixel-Faithful HTML from Figma

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that converts any Figma frame into production-ready HTML/CSS/JS. Output opens in any browser with no build step. The primary deliverable is a real HTML file with a linked `images/` folder (PIL-compressed, real files — never base64, see H4); an *additional* single self-contained `.html` with every image base64-embedded is available for delivery contexts where the file must survive without its `images/` folder.

Handles both Clay DS designs (maps Figma variables to Clay CSS tokens) and arbitrary designs (extracts raw hex/px values). Full-page builds include mandatory production-quality GSAP interactivity — scroll-reveal entrance animations, auto-advancing tabs, CSS marquees, IntersectionObserver counter animations, and a sticky nav.

## What It Does

Given a Figma URL pointing to a frame or page, this skill:

1. Extracts fileKey + nodeId from the URL
2. Classifies the frame (single component / single section / full page)
3. Runs section-by-section Figma extraction for full pages — `get_metadata` to enumerate child sections, then `get_design_context` on each independently (single full-page calls fail at ~222K tokens for large frames)
4. Takes per-section Figma reference screenshots to use as QA ground truth
5. Downloads real image/SVG assets via `download_assets`; detects Clay DS subscription via `get_libraries`
6. Maps Figma variable references to Clay CSS custom properties (if Clay design) or extracts raw values to a `:root` block (non-Clay)
7. Generates semantic HTML/CSS — no Clay React component names, no screenshots used as page content (both are documented live failures)
8. Adds mandatory GSAP interactivity: GSAP + ScrollTrigger scroll-reveals, auto-advancing tab panels (5s interval), CSS `@keyframes marquee` on logo/story strips (hover-pause), IntersectionObserver counter animation on stats, sticky nav with scroll shadow
9. PIL-compresses every image and writes real linked files into `images/<section-slug>/`; optionally also produces a base64 self-contained variant for portable single-file sharing
10. Runs `tools/qa_gate.py` (per section and once for the whole page) plus Playwright QA: full-page desktop (1440px) + mobile (390px) + 820px screenshots, horizontal overflow checks, per-section crop vs Figma ref side-by-side strips, 4-dimension scored report (Layout / Assets / Copy / Color+Type)
11. Delivers the real linked-file HTML + `images/` folder (primary) + QA screenshots + scored report; the self-contained variant only if requested

## Hard Rules (Non-Negotiable, H1–H53 — see `reference/HARD-RULES.md`)

- **H1 — No screenshots as page content.** `get_screenshot` outputs are QA references only. Never embed a Figma section screenshot as an `<img>` tag to represent a section.
- **H2 — No Clay component names in HTML.** Even for Clay designs, output is raw HTML/CSS. Clay component names (`HeaderSection`, `CardGrid`, etc.) are prohibited as class names or structural guidance.
- **H3 — Section-by-section extraction for full pages.** For frames with 5+ child sections, always use `get_metadata` → per-child `get_design_context`. Never attempt a single `get_design_context` call on a large full-page frame.
- **H4 — Real linked image files by default.** Base64 is for an *optional additional* single-file share variant only — the primary deliverable is a real HTML file + `images/` folder, which is also what makes it re-editable.
- **H5 — Mandatory interactivity for full-page builds.** GSAP scroll-reveals, auto-advancing tabs, CSS marquees, IntersectionObserver counters, and sticky nav are required on every full-page build. Not optional polish.

The remaining rules (H6–H45 — sentinel preservation, page skeleton, Clay-Web instance lookup, media sizing, alt text,
page-wide CTA/container consistency, blank-asset/glyph gates, motion-tell detection (H31), and more) live only in
`reference/HARD-RULES.md`; this list is a preview, not the authority.

## Prerequisites

Run **before your first build** (see `reference/PREREQUISITES.md` for full detail):

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or **Cursor** with agent skills enabled
- **Clay design-system** checkout (local clone — path discovered automatically or via `CLAY_DESIGN_SYSTEM_PATH`)
- **Figma MCP** connected and authenticated in your editor
- **Python 3.9+**, **Node ≥ 24**, **pnpm**
- **Pillow** and **Playwright + Chromium** (installed by the setup script)

## Installation

```bash
# 1. Copy the skill into your skills directory:
cp -r figma-to-web ~/.claude/skills/

# 2. Install and verify all dependencies (required before first use):
cd ~/.claude/skills/figma-to-web
python3 tools/setup_dependencies.py
```

The setup script installs Pillow and Playwright/Chromium when missing, checks Node and pnpm,
locates your Clay checkout, and writes `.f2w-setup.json`. **Do not ask the agent to build until
this exits 0.** Connect Figma MCP in your editor separately (the agent verifies auth on first use).

For Cursor, copy to wherever your skills live (e.g. `~/.claude/skills/` if symlinked, or your
project's `.cursor/skills/`).

## Usage

Provide a Figma URL and ask to build:

```
/figma-to-web https://figma.com/design/ABC123/my-design?node-id=7:8089
```

Or use any of these trigger phrases:
- "Convert this Figma design to HTML"
- "Build a landing page from this Figma frame"
- "Implement this design as a webpage"
- "Make an HTML version of this design"

The skill walks through extraction, generation, and QA, delivering the real linked-file HTML +
`images/` folder + per-section comparison strips.

### Giving feedback/corrections effectively

When asking for a fix, the more precise your feedback, the faster and more accurate the fix. See
[`reference/FEEDBACK-GUIDE.md`](reference/FEEDBACK-GUIDE.md) for the full guide — short version:

- Always paste the exact Figma URL with `node-id`, not a description of the frame.
- Say what's wrong **and** what it should be instead — never just "this doesn't look good."
- Pinpoint the element with a screenshot, the Figma layer name, or the class/id from the browser
  inspector — don't make Claude search for it.
- If a lesson should be remembered for every future build (not just this page), say so explicitly
  — Claude always asks before writing it into the skill's shared reference files.

## Output

```
output/<page-slug>/
├── index.html                                   ← real page file, real linked images (H4)
├── images/<section-slug>/...                    ← one subfolder per section
├── <page-slug>-self-contained.html               ← optional, only if requested
├── section-ref/                                  ← per-section Figma reference screenshots
├── qa-desktop-v01.png · qa-mobile-v01.png        ← full-page pass (1440/390px, + 820px checked)
└── figma-to-web-qa-report-v01.md
```

## Modes

| Mode | Trigger | Output |
|---|---|---|
| **Single component** | One atomic UI element (Button, Card) | Component HTML with extracted CSS |
| **Single section** | One full-width content area | Section HTML |
| **Full page** | Multiple section-level children | Complete landing page with GSAP interactivity |

**Clay detection:** If `get_libraries` shows Clay DS file key `LyYrDV2oALKuPoePY9aeJJ` subscribed → Figma variables are mapped to Clay CSS custom properties. Token CSS is inlined from the local Clay repo.

## Documented Failures and Fixes

All six failure modes from the monday AI Agents Page live test (v01–v06, 2026-08-09) are documented in `reference/FULL-PAGE-WORKFLOW.md` under "Lessons from live tests." Failures: Clay component name mapping (v01), section screenshots as content (v02), no section-level QA (v03 gap), wrong scale factor (v04), broken relative paths + no interactivity (v05). v06 resolved all of them.

## File Structure

```
figma-to-web/
  SKILL.md                — Frontmatter, trigger phrases, requirements, reference-file index
  reference/
    SECTION-WORKFLOW.md   — The actual per-section engine (read this first)
    FULL-PAGE-WORKFLOW.md — Thin wrapper looping SECTION-WORKFLOW.md over a page's sections
    PAGE-STRUCTURE.md     — Page shell (page-wrapper / header / main / three-div nest / footer)
    HARD-RULES.md         — H1–H53, non-negotiable
    ACCURACY-GATE.md       — Vision QA + tools/qa_gate.py, in what order and why
    PREREQUISITES.md      — Toolchain + one-time setup + agent preflight
    DESIGN-FILE-GAPS.md   — What to do when the Figma source itself has a content gap
    FEEDBACK-GUIDE.md     — How to write feedback/corrections so Claude acts on them precisely
    web-design-rules.csv  — The 45-rule hard/soft pass/fail authority, with an owner column
    ...                   — CLAY-INTEGRATION.md, PRE-BUILD-VERIFICATION.md, GOTCHAS.md, etc.
  tools/
    section_spec.py        — Pre-build measurement (bg/textsize/textnodes/overlap/assetbg/spec)
    qa_gate.py              — Mechanized per-section/per-page accuracy gate
    visual_diff.py          — Pixel-level Figma-vs-HTML comparison (side-by-side, heatmap, SSIM)
    diff_enrich.py          — Enriches a visual_diff report with Figma-vs-HTML CSS fix suggestions
    setup_dependencies.py   — One-time install + verify (run before first use)
    lint_skill.py           — Checks this skill's own internal consistency
  README.md               — This file
```

## License

MIT

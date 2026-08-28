---
name: figma-to-web
description: >
  Converts a Figma frame, section, or full page into pixel-faithful HTML/CSS/JS — the Figma
  design is always the accuracy target. Two modes, one engine: build a single section (two-turn
  scout + build, injects into an accumulating page file) or build a whole page (walks every
  top-level section in order, running the exact same per-section process on each one into one
  file). Uses Clay's real coded component library (when present) as an accelerant for correct
  structure/CSS/copy, `tools/qa_gate.py` as a mechanized accuracy gate, and mandatory per-section
  vision QA as the primary check. Halts and asks for an interactivity brief rather than guessing
  when Clay doesn't cover a section, Figma leaves behavior unspecified, or a section has multiple
  interdependent controls needing a state-model plan. Use when: converting a Figma design to
  HTML, building one section, building a full landing page, adding a section to a page you've
  already started, or exporting a Figma frame as production-ready static code.
---

# Figma to Web — Pixel-Faithful HTML from Figma

Converts a Figma URL into real HTML/CSS/JS. Output opens in any browser with no build step and
no external dependencies beyond its own `images/` folder. **Mode A — Vanilla HTML** (default,
this skill). For Clay React page output instead of vanilla HTML, see `figma-to-clay-web` (not
part of this skill).

## Two modes, one engine

**Building one section and building a whole page are the same process at different scopes —
not two different skills, not two different rule sets.**

- **Section mode**: point at a single Figma section node. Two turns — Turn 1 scouts the design
  and asks for a brief; Turn 2 builds, injects into an accumulating page file, and delivers. Full
  process: `SECTION-WORKFLOW.md`.
- **Full-page mode**: point at a Figma page/frame with multiple top-level sections. Discovers
  every section (sorted by real position, not document order), then runs section mode's exact
  process on each one in turn, into the same page file, finishing with one full-page vision pass
  across everything. Full process: `FULL-PAGE-WORKFLOW.md` — which is a thin wrapper around
  `SECTION-WORKFLOW.md`, not a separate implementation.

The only behavioral difference: full-page mode defaults to brief-skip inference for every
section (stating assumptions once in the final reply) instead of pausing for an interactive
brief N times — but `ASK-DONT-GUESS.md`'s hard triggers still fire per-section regardless of
mode. Every hard rule and every other reference file applies identically in both modes.

## The governing principle

**The Figma design is the source of truth for the final look and behavior, full stop.** Clay is a
resource this skill consults to get there faster and with fewer bugs — it is never the
destination. Clay is read through **static rendering** (`renderSection()` → plain `html` + `css`,
or rendered Storybook/Chromatic DOM) — never by copying React/`.module.css` source into the page
(H2, `CLAY-INTEGRATION.md` rule 1). If a matched Clay component's default doesn't match Figma
exactly — in a value (color, size, padding) **or in its layout mechanism** (how many items are
visible, how they're arranged) — Figma wins, at every property, not just the obvious ones. If
nothing in Clay covers a section, that doesn't lower the bar; it just means building from smaller
ingredients. See `CLAY-INTEGRATION.md` for the full resolution process.

**Three non-negotiables:**
1. **Per-section vision QA is mandatory, on every section, as it's built** — not batched to the
   end, never substituted with a DOM assertion. See `ACCURACY-GATE.md`.
2. **When the skill doesn't know what a section should do, it asks — it never guesses.** This
   includes sections with ≥2 interdependent controls (tabs+dots+autoplay, multi-step state) —
   present a concrete plan for confirmation before writing code, not just a content brief. See
   `ASK-DONT-GUESS.md`.
3. **Before writing CSS, measure — don't remember.** Run `tools/section_spec.py`'s four
   pre-build subcommands (`bg`, `textsize`, `textnodes`, `assetbg`) on every section and `overlap`
   once per page at manifest time (`spec` consolidates the first three into one JSON file for
   `tools/qa_gate.py` to diff against later). These are the four bug classes that kept escaping a prose checklist,
   and they all have one thing in common: the answer is a number a script can print. Then run
   `PRE-BUILD-VERIFICATION.md`'s remaining items — size, border presence, radius, padding, order,
   layout mechanism — in one pass, rather than shipping an assumed value and fixing each wrong
   property reactively across several rounds.

## Before anything else: setup + preflight

**The user must install dependencies before the first build.** After copying this skill, they run
`python3 tools/setup_dependencies.py` once (see `PREREQUISITES.md`). **Do not start any Figma
extraction, scouting, or HTML/CSS work until that script exits 0** on this machine — run it
yourself at session start if `.f2w-setup.json` is missing, stale, or `"ok": false`.

Then run the agent preflight in `PREREQUISITES.md`: verify setup, confirm Clay, confirm Figma MCP
responds to `get_metadata` on the target file. Five tools are hard-required (Clay checkout, Figma
MCP, Python+Pillow, Playwright+Chromium, Node ≥ 24 + pnpm). Halt with the setup script's fix text
for anything still missing — never proceed on a partial toolchain or "we'll install Playwright
later when QA runs."

## Requirements

- A Figma URL with `node-id` is mandatory before the skill can start. If missing, stop and ask.
- Figma MCP must be connected and returning tool results — verified in preflight.
- Which mode applies is determined by `get_metadata` on the given node (see `FULL-PAGE-WORKFLOW.md`
  Step 1's frame-classification table) — not by which words the user used to ask.

## What this skill does, at a glance

1. Runs `python3 tools/setup_dependencies.py --check` (or full setup if not yet installed) per
   `PREREQUISITES.md`, then agent preflight including Figma MCP.
2. Extracts fileKey + nodeId, classifies the frame (single section vs. full page).
3. **Full-page mode only:** discovers every top-level section, sorted by real position.
4. Per section: runs `CLAY-INTEGRATION.md`'s resolution process. **H28:** if the frame is a
   Clay-Web library instance (`LyYrDV2oALKuPoePY9aeJJ`) or its name matches `connections.json`,
   that coded component is the reference — do not rebuild from pixels or ask which component.
   Otherwise name/shape match, then structural/borrowed-pattern search.
5. Extracts real content/assets from Figma (never Clay's placeholder copy).
6. **Before writing CSS**, runs `PRE-BUILD-VERIFICATION.md`'s checklist on anything visually
   complex — size, color, border, radius, padding, overlap, order, layout mechanism.
7. Generates semantic HTML/CSS using the `PAGE-STRUCTURE.md` skeleton — real component
   structure/CSS where resolved, hand-built from atoms/tokens where not, real downloaded assets
   throughout (H1/H2/H27). Clay-Web instances resolve to coded Clay first (H28).
8. Adds baseline interactivity (mandatory in full-page mode, H5) and halts to ask before
   inventing anything more specific, including the state model for any multi-control section
   (`ASK-DONT-GUESS.md`).
9. Delivers real linked-file HTML + `images/` folder as the primary artifact (H4); optionally a
   base64 self-contained single file for portable sharing.
10. Runs the full accuracy gate per section: vision QA (primary) + `tools/qa_gate.py`
    (`ACCURACY-GATE.md`, scored against `QA-SCORECARD.md`'s rubric). **Full-page mode adds one
    more pass across the whole assembled page** once every section is in.
11. Delivers the file(s) + QA report, with any accepted gaps and halted-and-asked items stated
    explicitly — never silently smoothed over.

## Reference files

| File | When to read it |
|---|---|
| [`PREREQUISITES.md`](reference/PREREQUISITES.md) | **Before starting anything** — user runs `tools/setup_dependencies.py` once; agent verifies before every session |
| [`tools/setup_dependencies.py`](tools/setup_dependencies.py) | One-time install + verify (Pillow, Playwright, Node, pnpm, Clay discovery) |
| [`HARD-RULES.md`](reference/HARD-RULES.md) | Always — H1–H33, non-negotiable, same rules in both modes |
| [`SECTION-WORKFLOW.md`](reference/SECTION-WORKFLOW.md) | The actual per-section engine — read this first |
| [`FULL-PAGE-WORKFLOW.md`](reference/FULL-PAGE-WORKFLOW.md) | Full-page mode only — the thin wrapper that loops `SECTION-WORKFLOW.md` |
| [`PAGE-STRUCTURE.md`](reference/PAGE-STRUCTURE.md) | The page shell — `page-wrapper` / `header` / `main-wrapper` / three-div nest / `footer`. Write this in Step 7; class names fixed, values from H22 |
| [`PRE-BUILD-VERIFICATION.md`](reference/PRE-BUILD-VERIFICATION.md) | **Before writing any CSS** for a visually complex section — one checklist pass instead of five reactive fixes |
| [`tools/section_spec.py`](tools/section_spec.py) | With it — the mechanized half of that checklist (`bg`/`textsize`/`textnodes`/`overlap`/`assetbg`/`spec`). Run it, read the output, build against it |
| [`tools/qa_gate.py`](tools/qa_gate.py) | After building/injecting a section (or the whole page) — the mechanized half of the accuracy gate |
| [`CLAY-INTEGRATION.md`](reference/CLAY-INTEGRATION.md) | Per section, before writing any HTML/CSS for it |
| [`PERFORMANCE.md`](reference/PERFORMANCE.md) | Before writing any HTML/CSS — images, fonts, CSS delivery, JS loading |
| [`ACCURACY-GATE.md`](reference/ACCURACY-GATE.md) | Per section (vision QA + `tools/qa_gate.py`) and before delivery (full-page pass) |
| [`QA-SCORECARD.md`](reference/QA-SCORECARD.md) | The scoring rubric and report format used by the accuracy gate |
| [`web-design-rules.csv`](reference/web-design-rules.csv) | The only pass/fail authority (`hard`/`soft`) — every rule's `owner` column says whether `tools/qa_gate.py` checks it or vision does |
| [`ASK-DONT-GUESS.md`](reference/ASK-DONT-GUESS.md) | The moment behavior is unclear, uncovered by Clay, or a section has ≥2 interdependent controls |
| [`FIGMA-EXTRACTION.md`](reference/FIGMA-EXTRACTION.md) | When a Figma MCP call fails, degrades, or structure is ambiguous |
| [`DESIGN-FILE-GAPS.md`](reference/DESIGN-FILE-GAPS.md) | When Figma shows an affordance with no populated content behind it |
| [`GOTCHAS.md`](reference/GOTCHAS.md) | Tool/environment bugs already diagnosed — check before debugging one yourself |

## Closing step: knowledge capture

At the end of every build (one section or a full page), before final delivery:

1. Review the session's own trace log (keep one throughout, in the `[CLAY]`/`[BUG]`/`[TOOL]`/
   `[QA]`/`[ACCEPTED-GAP]`/`[TIME]` tag convention used elsewhere in this skill —
   `SECTION-WORKFLOW.md`'s Step 1 and Step 12 cover the `[TIME]` entries specifically).
2. Classify each entry:
   - **Already documented** in `CLAY-INTEGRATION.md`/`GOTCHAS.md`/`DESIGN-FILE-GAPS.md`/
     `HARD-RULES.md`/`PRE-BUILD-VERIFICATION.md` → skip, cite where.
   - **Mechanically re-derivable** by re-running `tools/derive_family_fingerprints.py` → skip,
     note that the script should be re-run against the current Clay checkout.
   - **Genuinely new** (a bug, a process lesson, a judgment call worth remembering) → propose.
3. For every proposed item, in **one batched `AskUserQuestion`**: ask whether to write it into
   the specific file it belongs in, phrased as a general principle — never a page-specific note.
   **Never write without this consent.**
4. **Never write to personal `~/.claude` memory from this step** — only this skill's own
   bundled files, since that's what makes the knowledge shareable to whoever uses this skill
   next, not just useful in this one session.

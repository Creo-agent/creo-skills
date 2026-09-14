# figma-to-web — Skill Handoff

**Version:** as of 2026-09-01 (HARD-RULES H1–H46). **Bundle:** `figma-to-web-skill-handoff-v01.zip`.
**Upstream:** `DaPulse/marketing-design-ai-hub` → `skills/figma-to-web/` (PRs #41 motion-tell, #42 IT-page process locks).
**Audience:** a new operator/agent picking this skill up cold. Read this file top-to-bottom once, then `SKILL.md`, then start.

---

## 0. What's in this bundle vs. what you must provide

**The zip contains the complete skill** — every instruction file, reference doc, and tool that *is*
figma-to-web. It is self-contained and lint-clean. But a skill is instructions, not a runtime: three
external things **cannot** be zipped and must exist on the target machine. This is by design, not an
omission.

**✅ In the zip (the whole skill):**
- `SKILL.md`, `README.md`, this `HANDOFF.md`
- `reference/` — 14 docs (HARD-RULES H1–H46, SECTION/FULL-PAGE workflows, CLAY-INTEGRATION,
  PRE-BUILD-VERIFICATION, ACCURACY-GATE, QA-SCORECARD, ASK-DONT-GUESS, FIGMA-EXTRACTION,
  DESIGN-FILE-GAPS, GOTCHAS, PAGE-STRUCTURE, PERFORMANCE, PREREQUISITES) + `web-design-rules.csv`
- `tools/` — 7 Python tools (setup_dependencies, section_spec, qa_gate, derive_family_fingerprints,
  lint_skill, visual_diff, diff_enrich)

**⚙️ NOT in the zip — you provide these once on the target machine (all covered in §3–4):**
1. **Runtime packages** — Pillow, Playwright + Chromium, Node ≥ 24 + pnpm. **The bundled
   `tools/setup_dependencies.py` installs and verifies these for you** (`python3 tools/setup_dependencies.py`).
   They're not bundled because they're platform-specific binaries, not skill content.
2. **A local Clay Design System checkout** (`clay-design-system/`). This is a separate monday.com git
   repo (large) — it holds the coded Clay components, the compiled tokens, the **`connections.json`**
   Code Connect registry, Clay's `wiki-index.json`, and the **logo library** (H33 monday marks). The
   skill *reads* it; it can't ship inside a skill zip. **Without it the skill still runs** (it builds
   from Figma + atoms, and third-party logos still come from Figma SVG export), but Clay acceleration,
   the `connections.json` chrome/component lookups (H25/H28), and the monday-logo source (H33) are
   unavailable. If your target is a non-Clay project, this is optional; for monday.com pages, clone it.
3. **A connected Figma MCP server** (read tools) + a **Figma URL with a `node-id`**. That's a live
   service + auth in the host/agent, not a file — configure it in your harness (e.g. `.mcp.json`).

So: **yes, the zip is everything the skill *is*** — but "using it" also needs the setup script run once,
Figma MCP connected, and (for monday.com/Clay work) the Clay repo cloned. Nothing else.

> One cosmetic note found in the completeness audit: `tools/derive_family_fingerprints.py`'s docstring
> cites a `CLAY-SECTION-DECISION-TREE.md` that isn't in this skill version — a stale comment only; the
> tool runs without it and nothing at build time depends on that file.

## 1. What this skill does

Converts a **Figma frame, section, or full page into pixel-faithful HTML/CSS/JS**. The output opens
in any browser with **no build step and no external dependencies** beyond its own `images/` folder.
The **Figma design is always the accuracy target** — not "close enough," not a redesign.

- **Mode A — Vanilla HTML** (this skill): plain semantic HTML/CSS/JS.
- (For Clay **React** page output instead, that's a sibling skill `figma-to-clay-web` — not in this bundle.)

It uses monday.com's **Clay Design System** coded component library *as an accelerant* (correct
structure/CSS/copy) when the design maps to Clay — but Clay is a resource consulted, never the
destination. If Clay doesn't cover a section, the bar doesn't drop; you build from smaller atoms/tokens.

**Use it when:** converting a Figma design to HTML · building one section · building a full landing
page · adding a section to a page you already started · exporting a Figma frame as production-ready
static code.

**Do NOT use it for:** Figma *write* operations (that's `use_figma`/`figma-use`); AI image resize;
animation/motion authoring; or React/Clay page output (`figma-to-clay-web`).

---

## 2. The governing principle + 3 non-negotiables

**The Figma design is the source of truth for final look and behavior, full stop.** Where a matched
Clay component's default differs from Figma — in a value (color/size/padding) *or* a layout mechanism
(how many items show, how they're arranged) — **Figma wins, at every property.**

1. **Per-section vision QA is mandatory, on every section, as it's built** — never batched to the end,
   never swapped for a DOM assertion. (`reference/ACCURACY-GATE.md`)
2. **When the skill doesn't know what a section should do, it asks — it never guesses.** Includes any
   section with ≥2 interdependent controls (tabs+dots+autoplay, multi-step state): present a concrete
   state-model plan for confirmation *before* writing code. (`reference/ASK-DONT-GUESS.md`)
3. **Before writing CSS, measure — don't remember.** Run the deterministic pre-build measurements
   (`tools/section_spec.py`) + the `PRE-BUILD-VERIFICATION.md` checklist, so you ship measured values
   instead of fixing wrong assumptions reactively across many rounds.

---

## 3. Prerequisites (hard-required — the skill refuses to start without them)

| # | Requirement | How it's checked |
|---|---|---|
| 1 | **Python 3 + Pillow** | `tools/setup_dependencies.py` |
| 2 | **Playwright + Chromium** (QA renders) | `tools/setup_dependencies.py` |
| 3 | **Node ≥ 24 + pnpm** (only for Clay React/Storybook rendering) | `tools/setup_dependencies.py` |
| 4 | **A local Clay Design System checkout** (`clay-design-system/`) — the coded component library + logo library | discovery in setup script |
| 5 | **Figma MCP connected** and returning results (read tools) | agent preflight: `get_metadata` on the target file |
| 6 | **A Figma URL with a `node-id`** | mandatory input; stop and ask if missing |

Clay checkout gives you both the coded section components *and* the **logo library**
(`clay-design-system/New logos/…`) that H33 draws monday/product marks from.

---

## 4. Install & first run

```bash
# once, after copying the skill onto a machine:
python3 tools/setup_dependencies.py           # installs missing packages + verifies all checks
python3 tools/setup_dependencies.py --check    # verify only (re-run any time a check starts failing)
python3 tools/setup_dependencies.py --json      # machine-readable report
```

It must **exit 0** before any Figma extraction/scouting/HTML work begins. State is cached in
`.f2w-setup.json`; if that file is missing/stale/`"ok": false`, re-run. Then run the agent preflight
in `reference/PREREQUISITES.md` (verify setup + confirm Clay + confirm Figma MCP).

---

## 5. Two modes, one engine

**Building one section and building a whole page are the same process at different scopes** — not two
skills, not two rule sets.

- **Section mode** — point at a single section node. **Two turns:** Turn 1 scouts the design + asks
  for a brief; Turn 2 builds, injects into an accumulating page file, delivers. Engine:
  `reference/SECTION-WORKFLOW.md`.
- **Full-page mode** — point at a page/frame with multiple top-level sections. Discovers every section
  (sorted by **real position, not document order**), runs the section engine on each in turn into the
  *same* page file, then one full-page vision pass across everything. Wrapper:
  `reference/FULL-PAGE-WORKFLOW.md` (a thin loop over the section engine).

The only behavioral difference: full-page mode defaults to **brief-skip inference** per section
(stating assumptions once at the end) instead of an interactive brief N times — but
`ASK-DONT-GUESS.md`'s hard triggers still fire per-section, and every hard rule applies identically.

Which mode applies is decided by `get_metadata` on the node (frame-classification table in
`FULL-PAGE-WORKFLOW.md` Step 1) — **not** by the words the user used.

---

## 6. Workflow summary (end to end)

1. **Setup + preflight** — `setup_dependencies.py --check`, then agent preflight (Figma MCP, Clay).
2. **Extract fileKey + nodeId; classify the frame** (single section vs. full page).
3. **(Full-page) Discover sections**, sorted by real `y` position → build order manifest.
4. **Per section — resolve against Clay** (`CLAY-INTEGRATION.md`): a Clay-Web library instance or a
   `connections.json` name match *is* the reference (don't rebuild from pixels or ask which
   component); otherwise name/shape match → structural/borrowed-pattern search; else build from atoms.
5. **Extract real content + assets from Figma** (never Clay's placeholder copy).
6. **Before writing CSS — measure** (`section_spec.py` + `PRE-BUILD-VERIFICATION.md`): background,
   real glyph sizes, text-node counts, section overlap, baked-in export margins, border/radius/padding,
   order, layout mechanism.
7. **Generate semantic HTML/CSS** on the `PAGE-STRUCTURE.md` skeleton — real coded structure where
   resolved, atoms/tokens where not, **real downloaded assets throughout** (H1/H2/H27; logos per H33).
8. **Add baseline interactivity** (mandatory full-page, H5); **halt and ask** before inventing anything
   more specific, including any multi-control section's state model.
9. **Deliver real linked-file HTML + `images/` folder** as the primary artifact (H4); optionally a
   base64 self-contained single file for portable sharing.
10. **Accuracy gate, per section:** vision QA (primary) + `qa_gate.py` (mechanized), scored against
    `QA-SCORECARD.md`. **Full-page adds one whole-page pass** once every section is in.
11. **Deliver file(s) + QA report** — every accepted gap and halted-and-asked item stated explicitly,
    never silently smoothed over.
12. **Knowledge capture** (`SKILL.md` closing step): propose genuinely-new lessons back into the
    skill's own bundled files (never personal memory), phrased as general principles.

**Drop-resilience (H32):** a full-page build **persists the page HTML + trace to disk after every
section**, in small turns — so an interruption (infra drop, context compaction, time/turn ceiling)
costs at most one section, and the build resumes from disk.

---

## 7. Hard rules (H1–H46) — the non-negotiables

Full text in `reference/HARD-RULES.md`. One-line index:

- **H1** No screenshots as content · **H2** No Clay component names in vanilla output · **H3**
  Full-page = section-by-section, never one full-frame pull (names the ~82K inline-cap fallback) ·
  **H4** Real linked image files by default; base64 only for the optional single-file variant ·
  **H5** Mandatory baseline interactivity on full-page builds · **H6** Never duplicate a section ·
  **H7** Preserve the sentinel · **H8** One `<head>`, no dup deps · **H9** Flatten composite
  visual-asset frames, never hand-rebuild · **H10** Media sizing: aspect-ratio always, literal inset
  geometry, + "peek" container for media overlapping its own text frame · **H11** Meaningful alt on
  every image · **H12** Explicit width/height + `height:auto` · **H13** Lazy-load below the fold
  (never inside a JS slider) · **H14** Explicit font-weight on every heading · **H15** Trim the
  sibling, don't wrap · **H16** Size from the element's own authored geometry · **H20** Mobile
  variant specificity persists at desktop unless overridden · **H21** One shared CTA size/style ·
  **H22** One shared container max-width + responsive side-padding · **H23** Reproduce `-scale-*`
  wrappers unless canceled · **H24** Never assume inherited centering on an `<img>` · **H25** Global
  chrome (nav/footer): check `connections.json` first; else the real Figma chrome node as pure DOM +
  real logo vectors, never a screenshot · **H26** Resuming after compaction ≠ fresh state ·
  **H27** PAGE-STRUCTURE skeleton · **H28** Clay-Web instance/name → coded Clay, never pixels ·
  **H29** A downloaded asset isn't verified until its pixels are · **H30** Never substitute a
  glyph/emoji for a real Figma icon · **H31** A static frame carrying a motion tell resolves to
  motion · **H32** Persist after every section; small turns; never build in one large turn ·
  **H33** Never recreate a logo — Clay repo → Figma SVG export → stop-and-ask · **H34** Never
  paraphrase Figma copy — extract `characters` verbatim · **H35** Always read layout values
  (padding/gap/radius) from the Figma API, never guess · **H36** Detect implicit padding on an
  autolayout frame whose height exceeds its children + gaps · **H37** Export small composed
  elements (avatars, icon rows, logos) as images, not inline SVG · **H38** Never flatten an
  interactive component as a static image · **H39** A Clay match without extracting its rendered
  HTML/CSS/aria pattern is decoration, not a match · **H40** A Clay component's mobile behavior
  is part of its spec — check and replicate it · **H41** CTA capsule buttons stay inline-width
  pills on mobile, never full-width rectangles · **H42** Verify the target Figma node against the
  user's latest message before starting any build · **H43** Track every change request as a
  numbered checklist, verified with grep/DOM inspection before reporting done · **H44** Preserve
  image alpha channels — never convert a transparent PNG to JPEG · **H45** Every section's
  JavaScript is wrapped in a scoped IIFE with try/catch · **H46** Wiring a JS interaction
  library (Swiper, etc.) into converted markup — CSS link, JS load, init call, old-JS removal,
  loop-mode slide-count check — is one atomic step, verified in one pass, not markup now/wiring
  later.

---

## 8. Tools this skill uses

### Figma MCP (read-only side)
| Tool | Used for |
|---|---|
| `get_metadata` | Classify the frame; list child sections; get real `x/y/width/height` (build order + geometry). Never a full-frame `get_design_context`. |
| `get_design_context` | Per-section structure/copy/tokens (React-ish). Also the fast source for many-glyph asset URLs (`const img…='…svg'`) — see FIGMA-EXTRACTION. |
| `get_screenshot` | QA reference image per section + the fallback when a node exceeds the ~82K inline cap. |
| `download_assets` | Export real media/logos (PNG/SVG). Note: silently truncates at 20 SVGs on rich subtrees — prefer design-context URLs for dense chrome. |

> This skill never uses `use_figma` (that's the write side / `figma-use`).

### Clay Design System (local checkout)
- Read via **static rendering** (`renderSection()` → plain `html`+`css`, or rendered Storybook/Chromatic
  DOM) — **never** by copying React/`.module.css` source into the page (H2).
- The **logo library** (`New logos/…`) is the first source for monday/product marks (H33).

### Bundled Python tools (`tools/`)
| Script | What it does |
|---|---|
| `setup_dependencies.py` | One-time install + verify the toolchain (Pillow, Playwright, Node/pnpm, Clay discovery). `--check` / `--json`. Gates the whole skill. |
| `section_spec.py` | Deterministic **pre-build measurement**. Subcommands: `bg`, `textsize`, `textnodes`, `overlap`, `assetbg`, `spec` (consolidates for the QA diff). Run BEFORE writing CSS; build against its output. |
| `qa_gate.py` | One **mechanized accuracy check** per section/page after build, before the vision look. Strictly additive to vision QA; its `vision_owned` key lists what it does NOT check so `exit 0` is never read as "QA complete." |
| `visual_diff.py` | Pixel-level Figma-vs-HTML comparison after `qa_gate.py` passes — side-by-side image, overlay blend, delta heatmap, SSIM score, and a structured JSON fix brief mapping diff regions to DOM areas. |
| `diff_enrich.py` | Enriches a `visual_diff.py` report when it's NEEDS_FIX — fetches Figma node properties via the API and computed CSS via Playwright, then diffs them into exact per-region fix suggestions. |
| `derive_family_fingerprints.py` | Derives Clay section-family structural fingerprints from the real Clay TS source + Clay's `wiki-index.json` (never hand-written). Feeds Clay component matching. Re-run against the current Clay checkout. |
| `lint_skill.py` | Self-consistency lint of the skill itself (rule-reference resolution, owner validity, counts, links). Run after editing the skill. |

### Playwright + Chromium
- Renders desktop (1440) + mobile (390) full-page screenshots for QA; runs the mechanical gates
  (mobile no-horizontal-overflow = fail; height-delta vs the Figma frame = info, ±10% band). Serve over
  `localhost`, never `file://` (relative-path assets silently fail on `file://`).

---

## 9. Reference file map (read-when)

| File | When to read it |
|---|---|
| `reference/PREREQUISITES.md` | Before anything — setup + agent preflight |
| `reference/HARD-RULES.md` | Always — H1–H46, non-negotiable |
| `reference/SECTION-WORKFLOW.md` | The per-section engine — read first |
| `reference/FULL-PAGE-WORKFLOW.md` | Full-page mode — the loop wrapper |
| `reference/PAGE-STRUCTURE.md` | The page shell (fixed class names, values from H22) |
| `reference/PRE-BUILD-VERIFICATION.md` | Before writing any CSS on a complex section |
| `reference/CLAY-INTEGRATION.md` | Per section, before writing HTML/CSS — the Clay resolution process |
| `reference/PERFORMANCE.md` | Images, fonts, CSS/JS delivery |
| `reference/ACCURACY-GATE.md` | Per-section vision QA + `qa_gate.py`; full-page pass before delivery |
| `reference/QA-SCORECARD.md` | Scoring rubric + report format |
| `reference/web-design-rules.csv` | The pass/fail authority; `owner` column = who checks each rule (script vs vision) |
| `reference/ASK-DONT-GUESS.md` | The moment behavior is unclear/uncovered/multi-control |
| `reference/FIGMA-EXTRACTION.md` | When a Figma MCP call fails/degrades or asset sourcing is dense |
| `reference/DESIGN-FILE-GAPS.md` | When Figma shows an affordance with no content behind it |
| `reference/GOTCHAS.md` | Tool/environment bugs already diagnosed — check before debugging |

---

## 10. Outputs / deliverables

- **Primary:** a real linked-file `.html` + its `images/<section-slug>/…` folder (must travel together).
- **Optional:** a single self-contained `.html` with every image base64-embedded (for sharing where the
  file must survive without its folder — e.g. attaching one file to a message; target < 2MB).
- **A QA report** (`QA-SCORECARD.md` format): per-section scores, critical/major/minor issues, and an
  explicit **Accepted Gaps** list — including standing handoff flags (placeholder `#` links → `TODO-links`
  note; CDN font vs DS token; rasterized composite exports).
- **A decision trace** (tag convention `[DECISION]/[CLAY]/[BUG]/[TOOL]/[QA]/[ACCEPTED-GAP]/[OFF-PAGE]/[TIME]`).

---

## 11. Known limitations / gotchas (see `GOTCHAS.md` for the full list)

- Complex product mockups / illustrative collages are **flattened to an exported image** (H9), not live
  DOM — faithful, but not production-editable per element.
- Some Figma logo assets are CSS-mask watermarks that export alpha-empty; always pixel-verify (H29).
- `download_assets` `rawImages[]` is **not scoped** to the node — verify each candidate, don't trust an index.
- `get_design_context` can silently degrade to metadata-only on a large child — drill into smaller children.
- Static frames can hide motion (marquee/carousel/looping track tells, H31) — don't ship the frozen frame.

---

## 12. Portability notes (what's generic vs. Creo-specific)

This skill is written **tool-agnostically** and is safe to hand to any Claude Code / agent harness:

- The bundled entry point is **`SKILL.md`** + the `reference/` files + `tools/`. That's the whole skill.
- `figma-to-web.md` (the sibling dispatcher, included for completeness) is **Creo's Slack `/figma-to-web`
  command loader** — a wrapper specific to the Creo bot. Other harnesses can ignore it and load `SKILL.md`
  directly.
- Rules say "persist to disk" / "the deliverables folder," never a specific bot's output convention — so
  nothing here assumes Creo's `.slack-outputs/` or its 40-min/80-turn session model. Those live in Creo's
  own `AGENTS.md`, not in this skill.
- One thing to provide in a new environment: a **local `clay-design-system/` checkout** (for coded
  components + the logo library). Without it the skill still runs, but Clay acceleration and the H33
  monday-logo source are unavailable — third-party logos still come from Figma SVG export.

---

## 13. First build, in three lines

1. `python3 tools/setup_dependencies.py` → must exit 0.
2. Read `SKILL.md` → `reference/HARD-RULES.md` → `reference/SECTION-WORKFLOW.md`.
3. Give the skill a Figma URL **with a `node-id`** and go. It classifies the frame and runs the right mode.

# Figma to Web — Full-Page Workflow (Orchestrates Section-Workflow)

## Contents
- The one idea this file is built on
- Step 1 — Extract fileKey + nodeId, classify the frame
- Step 2 — Discover and order the page's sections
- Step 3 — Build every section, one at a time, via SECTION-WORKFLOW.md
- Step 4 — Full-page vision pass
- Step 5 — Optional self-contained single-file variant
- Step 6 — Deliver
- Known limitations (full-page specific)
- Lessons from live tests
- Cross-references

## The one idea this file is built on

**There is no separate full-page build engine.** Building a whole page means: discover its
top-level sections, then run `SECTION-WORKFLOW.md`'s exact process — Turn 1 scout, Turn 2 build
(Phase 1 Resolve via `CLAY-INTEGRATION.md`, Phase 2 Build, per-section vision QA, sentinel
injection) — on each one in turn, into the *same* accumulating page file. This file covers only
what's genuinely different about doing that N times instead of once: discovering and ordering
the sections up front, not pausing for an interactive brief on every single one, and a final
cross-section pass once every section is in. Every hard rule, every reference file
(`CLAY-INTEGRATION.md`, `ACCURACY-GATE.md`, `ASK-DONT-GUESS.md`, `PRE-BUILD-VERIFICATION.md`,
`PERFORMANCE.md`, `FIGMA-EXTRACTION.md`, `DESIGN-FILE-GAPS.md`, `GOTCHAS.md`,
`PAGE-STRUCTURE.md`) applies exactly the
same way per section here as it does when building one section standalone.

**Before Step 1**, confirm dependency setup passed (`python3 tools/setup_dependencies.py --check`
exits 0 — see `PREREQUISITES.md`) and run agent preflight (Figma MCP + Clay). Do not start on a
partial toolchain.
Both steps below run **once per full-page build, not per section**:

- **Start a local HTTP server immediately**, before building any section:
  `python3 -m http.server <port> --directory <DELIVERABLES_DIR>` in the background. Every
  section's QA screenshot and `qa_gate.py` run (`SECTION-WORKFLOW.md` Steps 10/10b) then loads
  `http://localhost:<port>/...` from the very first section — never a bare `file://` path, not
  even for a quick first look (`GOTCHAS.md`'s asset-loading gotcha: `file://` has no real network
  layer for local relative-path assets, so images silently fail to load while the screenshot still
  looks plausible). This was previously a narrated lesson that still recurred per section because
  `file://` stayed the first thing tried each time — starting the server here, once, removes the
  first attempt entirely rather than relying on remembering to avoid it.
- Preflight itself only needs to run **once per session** — see `PREREQUISITES.md`'s own note on
  caching the result; re-running all its checks per section was one of the largest confirmed fixed
  costs across this skill's own build traces.

## Step 0.5 — Verify Target Node (H42)

Before classifying or building anything, run `SECTION-WORKFLOW.md`'s Step 0.5: parse the URL
from the user's **most recent message**, run `get_metadata` to get the node/page name, echo it
back, and **wait for confirmation**. This applies to full-page mode exactly as it does to
section mode — building an entire wrong page is more expensive than building one wrong section.

## Step 1 — Extract fileKey + nodeId, classify the frame

Same URL parsing as `SECTION-WORKFLOW.md` Step 1 (`fileKey` from the path, `nodeId` from
`node-id` with `-` → `:`). Then classify what you were actually given, via `get_metadata`:

| Frame type | Detection | What to do |
|---|---|---|
| **Single component** | One atomic UI element (Button, Card, Input) | Not this file — build it directly, no section loop needed |
| **Single section** | Full-width frame, one content area | Run `SECTION-WORKFLOW.md` once, standalone — not this file either |
| **Full page** | Multiple section-level children in one frame | This file applies — continue to Step 2 |
| **Component set** | Multiple variants of the same component | Use the Default/Primary variant; note variant props in comments |

## Step 2 — Discover and order the page's sections

`get_metadata(fileKey, nodeId)` on the page frame → its direct children are the section
candidates. **Sort by real `y` position, not document/child order** (`FIGMA-EXTRACTION.md`) —
Figma's child list is z-order/authoring order, not visual order. Layers in Figma are stacked
by z-index, which may differ from their top-to-bottom visual position on the page. A designer
may reorder layers for editing convenience without changing the page's visual flow.

**The build plan must always reflect the visual page order** (sorted by `absoluteBoundingBox.y`),
not the Figma layer panel order. This is what users see when they scroll the page — the
Figma layer order is an implementation detail they don't think about.

**Filter decorative/non-section elements from the manifest:**
- Elements smaller than ~100×100px are likely decorative overlays (cursors, icons), not sections → tag as `decorative`, skip in manifest
- Elements wider than the page frame (e.g. 1712px on a 1440px page) are overflow decorations → tag as `decorative`, skip
- Elements with `y` < 0 relative to the page frame are background layers behind the content → tag as `background`, skip unless they contain real content
- Floating elements that overlap other sections (check y ranges) may be decorative overlays → verify before including

Tag skipped elements explicitly in the build plan so the designer knows what was excluded and why.

Build a manifest before writing anything:

```
SECTION_MANIFEST = [
    {"idx": 1, "slug": "nav",      "nodeId": "7:8080", "y": 0,    "h": 80,  "role": "header"},
    {"idx": 2, "slug": "hero",     "nodeId": "7:8089", "y": 80,   "h": 1013, "role": "section"},
    {"idx": 3, "slug": "logo-bar", "nodeId": "7:8091", "y": 1093, "h": 178, "role": "section"},
    {"idx": 14, "slug": "footer",  "nodeId": "7:9001", "y": 8000, "h": 400, "role": "footer"},
]
```

Tag every entry with `role` (`PAGE-STRUCTURE.md` / H27 / H25):

| `role` | Detection | Injects into |
|---|---|---|
| `header` | name matches nav/header/navbar, or Clay `Navbar` / H25 chrome | `<header data-chrome="header">` — not inside `main`, no three-div nest |
| `footer` | name matches footer, or Clay `Footer` / `Section/Footer` | `<footer data-chrome="footer">` — not inside `main`, no three-div nest |
| `section` | everything else | `<section data-section>` inside `main`, with `padding-global > container-large > padding-section-large` |

A real nav or footer that existed on the page frame the whole time must still be discovered here
— that is the H25 miss this step already exists to prevent. Classifying `role` is what makes that
discovery land in the right slot instead of becoming "just another section" in `main`.

**Make this discovery a literal numbered todo list, not an informal scan.** Confirmed real case:
navbar and footer were dropped entirely from a full-page build because section discovery happened
informally as the build progressed rather than as an explicit enumerated list checked before the
first section was written (see `GOTCHAS.md`). Before Turn 2 of the first section begins, list
every top-level child from this manifest — header/nav/footer included — as a numbered todo list,
and don't report the build complete until every item on that list, chrome included, has a
corresponding built section.

**Record `y` and `h` for every section, and immediately run the overlap pre-scan on the
manifest** — you already have every number it needs, so this costs one command and it is the last
moment the answer is free:

```bash
python3 ~/.claude/skills/figma-to-web/tools/section_spec.py overlap /tmp/<page>-manifest.json
```

It prints each adjacent pair's gap, flags negative ones as overlaps, and emits the exact CSS an
overlapping section requires.

**Why this belongs at manifest time and nowhere later:** an overlapping section's *background* is
a decision, not a value, and it has to be made before its CSS exists. The default instinct — give
the section its own opaque `background` — silently covers the bottom N px of the section above it,
including anything interactive that lives there. The correct pattern is

```css
margin-top: -Npx; position: relative; z-index: 2;
background: transparent; pointer-events: none;   /* on the overlapping wrapper */
```

with `pointer-events: auto` restored on the wrapper's own content, so the neighbour's overlapped
strip stays both visible **and** clickable. Getting this wrong is only discoverable by noticing
that content you weren't looking at has gone missing — from data that was in the manifest before
any CSS was written. Log the scan's output (`[PRE-BUILD-CHECK] overlap scan: N overlapping pairs,
<slug> -> -Npx`) so a later reader can tell it ran.

Never attempt a single `get_design_context` call across the whole page frame — it exceeds the
tool's context limit on large pages (~222K tokens for a 13-section, 14000px-tall frame,
confirmed live). Section-by-section is a hard technical requirement here, not a style choice.

**Confirmed real failure mode — do this even when sections arrive one URL at a time.** A task
that received individual section URLs across several turns (rather than one page-frame URL up
front) skipped this step entirely — each new URL seemed sufficient on its own, so the page
frame's own `get_metadata` call never happened. Only near the end did fetching the actual
top-level frame reveal: a real nav node and a real Clay `Section/Footer` instance that had
existed the whole time (never checked, both rebuilt from a live reference instead — see H25 /
`CLAY-INTEGRATION.md`'s "Global chrome" section), plus two entire sections between already-built
ones that nobody had sent a URL for.

**This was narrated here as a lesson and recurred anyway in the very next full-page build** —
narrative prose describing a past failure doesn't reliably prevent a repeat; a literal, checkable
condition does. **The explicit trigger, check it every time a section URL arrives:**

> If 2 or more individual section URLs have arrived across this conversation without a
> page-frame-level `get_metadata` call having been made yet, **stop building from the latest URL
> and fetch the top-level page/frame URL now** — ask the user for it if it wasn't given, run this
> Step 2 properly, build the real manifest, and only then continue.

This fires regardless of how confident the latest URL looks on its own, and regardless of whether
the user explicitly said "other sections" or "the rest of the page" — the trigger is the URL
count, not a keyword match, because the failure mode this guards against is exactly a sequence of
individually-plausible-looking URLs that never adds up to someone checking the whole page.
Building from whichever URL just arrived is not the same as building from a real manifest, and
the gap only surfaces once someone notices something's missing — later and more expensively than
running this step up front would have cost.

## Step 3 — Build every section, one at a time, via SECTION-WORKFLOW.md

For each entry in `SECTION_MANIFEST`, in order: run `SECTION-WORKFLOW.md`'s Turn 1 (Steps 1–3)
and Turn 2 (Steps 4–12) on that section's `nodeId`, targeting the *same* `page_slug` so every
section accumulates into one page file via its own sentinel-injection logic (Step 9 there).

**Complexity pre-check for subagent delegation.** Before delegating a section to a subagent,
estimate its complexity from the manifest data + `get_metadata` child count:

| Signal | Action |
|---|---|
| Child count > 20 OR nesting depth > 5 | Build directly in main session (no subagent) |
| Footer/nav with 30+ links or multi-column layout | Build directly — these consistently exceed subagent timeouts |
| Clay EXACT match with < 15 children | Safe for subagent delegation |
| ATOMS_ONLY + interactivity (tabs, accordion, carousel) | Build directly — interactive sections need iterative QA |
| Any section that previously timed out in this build | Build directly on retry |

**Subagent timeout:** Set to 25 minutes minimum (not 15). Complex sections like footers,
accordions with media panels, and card grids routinely take 18-22 minutes through the full
skill process (extract → Clay resolve → pre-build → build → QA → visual diff). A 15-minute
timeout wastes all progress on sections that were 80% complete.

**When a subagent times out:** Do not retry with another subagent. Build that section directly
in the main session. Log `[TIMEOUT] <section-slug> timed out at <N>min — building directly`.

**Origin:** Aug 31 2026 — 4 subagents timed out (15min limit) on complex sections (footer,
card grid, guardrails, FAQ). Each timeout wasted 15 minutes of compute with zero output.
Building these sections directly in the main session completed them in 18-22 minutes each.

**Slow and steady — never batch sections.** Build ONE section at a time, run the full QA
pipeline (Steps 10, 10b, 10c) on it, fix any issues, then move to the next. After each section:

1. **Show the user what was just built** — a screenshot or live preview link of the section.
2. **Report the visual diff score** — SSIM + pixel diff percentage.
3. **Fix before moving on** — if QA finds issues, fix them on this section before starting
   the next one.
4. **Progress update** — "Section 5/14 done, here’s what it looks like."

**Why this matters more than speed:** A user who sees 5 great sections trusts the remaining 9
will be great too. A user who sees 14 sections at once — some broken — questions everything.
Building fast and showing a broken result makes the agent look incapable. Building slow with
visible quality at every step builds confidence.

**Never switch to “batch mode”** even when under time pressure. The pattern of “first 4
sections are great, then quality drops off a cliff” is worse than building fewer sections
well. If time is limited, build fewer sections properly rather than all sections poorly.

**3-section review gate.** After every 3 sections:
1. **Publish the current page** to html.page (or send a screenshot)
2. **Report visual diff scores** for the 3 sections just built
3. **Ask the user:** “Here are sections [N-N+2]. Continue with the next 3, or do you have
   feedback on these?”
4. **Wait for the response.** Do not proceed until the user approves or gives corrections.

This creates natural checkpoints throughout a full-page build. The user stays in control,
can catch issues while they're small, and never faces a “surprise” of 10 broken sections
at once.

**Per-section process audit.** After completing each section (before moving to the next),
verify every checkbox:
- ☐ Figma data extracted (text verbatim, layout values from API)
- ☐ Clay match used if exists (Storybook opened, HTML/CSS extracted, structure followed)
- ☐ Interactive components built as HTML/JS (not flattened as images)
- ☐ Page-structure skeleton used (padding-global → container-large → padding-section-large)
- ☐ Visual diff run (SSIM + pixel diff reported)
- ☐ Score acceptable or issues fixed before moving on
- ☐ For any interactive component with desktop-only controls (arrows, tabs), a mobile-equivalent
  navigation mechanism exists, is wired to both a real click handler and real touch-swipe (not
  just visually present), and mobile precision-matching also checked structure
  (`flex-direction`/`order`), not just size (`HARD-RULES.md` H40, `GOTCHAS.md`)

If any checkbox is unchecked, the section is not done. Do not start the next section.

**Origin:** Aug 30 2026 — full-page marketing build. First 4 sections had proper QA (SSIM
83-93%). Then switched to batch mode for sections 5-14: skipped per-section QA, exported
interactive components as flat images, skipped Clay render extraction despite having matches.
Required full rebuild of 2 sections and a catchup QA pass on all remaining ones. Elior:
“I rather that you build slow and steady section by section and show the progress during
creation than you build fast and make the user feel that you are not capable of doing this.”

**Drop-resilience is mandatory here (`HARD-RULES.md` H32).** Write the accumulating page file
*and* the decision trace to disk immediately after each section injects — never carry more than
one section of unwritten work, and keep every model turn small (per-section extraction, never a
full-frame pull). A long full-page build *will* be interrupted eventually — an infra/transport
drop, a context compaction (H26), a turn/time ceiling, or a human pause. When the on-disk state is
always complete through the last finished section, the build resumes from there at a cost of at
most one section; when it isn't, it restarts from zero. Confirmed live: the IT persona page
(15 sections) lost two full attempts to "Connection closed mid-response" before switching to
persist-after-each-section, then completed across later passes with no lost work.

**The one behavioral difference from standalone section mode: full-page mode presents one
consolidated build plan table covering all sections, not one plan per section.** The build plan
table (from `SECTION-WORKFLOW.md` Step 3) covers every discovered section in one message —
Clay match, confidence, and planned approach for each. The user approves the whole plan at once.

**This default does NOT override `ASK-DONT-GUESS.md`.** If a specific section hits one of its
hard trigger conditions (unspecified interactivity, a design-file content gap, ≥2 interdependent
controls needing a state-model plan), that section's question appears in the build plan's
"Questions" block — but only for that section, not as a blanket questionnaire for all sections.

**The build plan's Reference check (Step 3) is asked once per page, not once per section.**
State it as a single line covering the whole discovered section list ("does any section above
match an existing live page? name the section + link") rather than repeating the question per
row of the table — the point is to surface a hidden reference dependency before building, not to
turn a 15-section page into 15 separate prompts for the same question.

Before writing any CSS for a section with real visual complexity (a matched Clay component,
overlapping elements, custom colors/borders/radii), run `PRE-BUILD-VERIFICATION.md`'s checklist
once for that section — this is what keeps a full-page build from turning into the same
multi-round reactive-fix cycle a single complex section can fall into, N times over.

**Cost trigger, on top of that:** a section with ≥2 interdependent controls, a manifest-time
overlap (`overlap` scan above), or a `likely`-tier (rather than `exact`) Clay match is
predictably the most expensive class of section to get right — confirmed across live builds as
the single largest source of rebuild rounds and logged `[BUG]` tags, concentrated in a small
number of sections rather than spread evenly. For any section matching one of these three
signals specifically, require `PRE-BUILD-VERIFICATION.md`'s full pass **and** a written
state-model plan before any CSS, even if the section would not otherwise have triggered
`ASK-DONT-GUESS.md`'s own halt — the trigger here is *predicted cost*, not ambiguity.

## Step 4 — Full-page vision pass

Once every section in the manifest is built and injected, do one additional vision pass — not a
per-section repeat, a pass across the *whole* assembled page — at both desktop (1440px) and
mobile (390px). This catches rhythm/spacing issues only visible in sequence: a later section
that doesn't match the established visual rhythm, a duplicate pattern that should have varied,
an overall page height gone wrong. Per-section QA (`ACCURACY-GATE.md`) checks each section
against its own Figma reference; this step checks the sections against *each other*.

**Measure inter-section spacing explicitly — don't rely on eyeballing the sequence.** A real
gap between two sections is not always visible in either section's own `paddingTop`/`paddingBottom`
(`PRE-BUILD-VERIFICATION.md` item 23): a Figma section frequently sits inside a taller
**wrapper frame** than its own named inner-content frame, and the leftover space between the
wrapper's boundary and the inner frame's boundary *is* real page spacing that a per-section
extraction silently drops if you only read the inner content frame. Confirmed real case (Sep
2026): the gap after one section's CTA button and the top margin above a following section's
heading were both short by a fixed amount that traced directly to this wrapper-vs-inner-frame
delta, flagged explicitly by the user as something "part of the skill" should catch automatically.
For every section boundary in the manifest: read both the section's own wrapper frame height and
its inner content frame height from `get_metadata`; a nonzero delta is spacing to add (distributed
per the wrapper's `primaryAxisAlignItems`, same implicit-padding logic as `HARD-RULES.md` H36) —
then screenshot each section boundary **against the section immediately before it**, not in
isolation, to confirm the rendered gap matches.

**Also run `tools/qa_gate.py page` here, once, across the whole page**:

```bash
python3 ~/.claude/skills/figma-to-web/tools/qa_gate.py page --url http://localhost:<port>/<page-slug>-page-v01.html
```

This mechanizes exactly the page-level rule groups a prior build's QA pass never checked at all
despite declaring the build ~9.7/10 — `nav_links_functional`, the `a11y_*` rules, the perf/SEO
rules, plus the page-wide consistency checks no single section owns (H21 one CTA size per page,
H22 one container-width convention per page). These are properties of the *page*, not naturally
scoped to any single section's own vision QA pass, and are exactly the kind of check that keeps
silently dropping out precisely because no single section "owns" them — running one command
instead of remembering a list is what makes that stop happening. Log the result the same way as
every other accuracy-gate finding (`[QA]`/`[BUG]`/`[ACCEPTED-GAP]`), even when it passes clean —
"ran clean" needs to be distinguishable from "never ran" in the trace.

## Step 5 — Optional self-contained single-file variant

The primary deliverable is the real page file with its `images/` folder (H4) — same as
single-section mode, just with more sections accumulated in. **Optionally**, for delivery
contexts where the file must survive without its `images/` folder (e.g. sharing one attachment),
produce an *additional* single self-contained `.html` with every image base64-embedded:

```python
import base64, io, os
from PIL import Image

MAX_WIDTH, JPEG_Q = 1600, 65

def compress_and_encode(path):
    img = Image.open(path)
    if img.width > MAX_WIDTH:
        h = int(img.height * MAX_WIDTH / img.width)
        img = img.resize((MAX_WIDTH, h), Image.LANCZOS)
    if img.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1] if img.mode != 'RGB' else None)
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=JPEG_Q, optimize=True)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"

# Walk the page's images/ folder, build a {relative_src: data_uri} map (SVGs base64 as
# image/svg+xml, not JPEG-recompressed), then string-replace src="..."/url(...) occurrences.
```

**Size guidelines:** < 1MB excellent · 1–2MB good · 2–3MB marginal (drop `JPEG_Q` to 50 or
`MAX_WIDTH` to 1200) · > 3MB too large, re-run before delivering. This is an *additional*
deliverable — never a replacement for the real linked-file version (H4).

## Step 6 — Deliver

```
output/<page-slug>/
├── index.html                                   ← real page file, real linked images (H4)
├── images/<section-slug>/...                    ← one subfolder per section
├── <page-slug>-self-contained.html               ← optional, only if Step 5 was run
├── section-ref/                                  ← per-section Figma reference screenshots
├── qa-desktop-v01.png · qa-mobile-v01.png        ← Step 4's full-page pass
└── figma-to-web-qa-report-v01.md
```

Delivery reply: section count, per-section Clay anchor (EXACT/CLOSEST/BORROWED/ATOMS_ONLY/none),
every brief-skip inference made (stated together, per section, even if nothing was flagged
individually during the build), interactivity shipped, accepted gaps, halted-and-asked items,
and the full-page vision pass result (desktop/mobile overflow check, broken images: none).

## Known limitations (full-page specific)

- Figma prototype interactions (hover states as prototype transitions, not component
  properties) are not captured by `get_design_context` at any scope — same limitation as
  single-section mode, just N times over; each section's gap gets its own
  `ASK-DONT-GUESS.md` halt if the brief-skip inference can't resolve it.
- Figma variables with modes (light/dark) are extracted as the default mode only, page-wide.
- A full-page build's own length means a genuinely complex section (per
  `ASK-DONT-GUESS.md`'s multi-control trigger) is *more* likely to appear somewhere in a large
  page than in a single hand-picked section — don't let the volume of "easy" sections build
  false confidence that the next one will be easy too; run `PRE-BUILD-VERIFICATION.md` on each
  one that has real visual complexity, not just the first one.

## Lessons from live tests — monday AI Agents Page (v01→v06)

**v01 (Clay class names):** mapped Figma sections to Clay DS class names directly. Result:
generic template, ~2/10 fidelity. Fixed by H2.

**v02 (section screenshots as `<img>`):** visual ~9/10 but not real code. Fixed by H1.

**v03 (raw HTML/CSS/JS + downloaded assets):** correct pattern established — each section
rebuilt as real HTML/CSS via what's now `SECTION-WORKFLOW.md`, product UI screenshots
downloaded, tabs built with vanilla JS.

**v03 QA gap (no section-level comparison):** full-page screenshots only. Fixed by per-section
reference screenshots + mandatory per-section vision QA (`ACCURACY-GATE.md`), now the default
for every section regardless of full-page or standalone mode.

**v04 (scale calibration):** 1920px frames were output with a spurious 0.75x multiplier. Fix:
`get_design_context` values are already relative to the design viewport — use px directly.

**v05 (broken paths + no interactivity):** delivered as a ZIP with relative paths that broke on
macOS due to spaces in the parent directory path. Fixed by H4 (real files + optional
self-contained variant) + H5 (mandatory baseline interactivity).

**v06 (self-contained + interactive):** single 0.9MB HTML, all images embedded, GSAP
scroll-reveals, a 7-tab auto-advancing system, CSS marquee, counter animation, sticky nav. QA
8.6/10 average, all sections real HTML.

## Cross-references

- **The page shell:** `PAGE-STRUCTURE.md` — `page-wrapper` / chrome / `main-wrapper` / three-div nest
- **The actual per-section engine:** `SECTION-WORKFLOW.md` — read this first, this file is a
  thin wrapper around it.
- **Clay resolution process:** `CLAY-INTEGRATION.md`
- **Pre-build verification checklist:** `PRE-BUILD-VERIFICATION.md`
- **Full accuracy gate (vision QA + `tools/qa_gate.py`):** `ACCURACY-GATE.md`
- **QA scoring rubric:** `QA-SCORECARD.md`
- **Figma reliability playbook:** `FIGMA-EXTRACTION.md`
- **Design-file gap handling:** `DESIGN-FILE-GAPS.md`
- **Halt-and-ask gate (including the multi-control-section trigger):** `ASK-DONT-GUESS.md`
- **Performance checklist:** `PERFORMANCE.md`
- **Tool/environment bugs:** `GOTCHAS.md`
- **Toolchain prerequisites:** `PREREQUISITES.md`

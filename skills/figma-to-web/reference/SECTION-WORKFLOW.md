# Figma to Section — Single Section Builder Workflow

## Contents
- Input Requirements
- State Detection — Which Turn Am I In?
- Predefined Defaults (never ask)
- Inference-first approach
- Turn 1 — Scout Phase (Steps 0–3, Step 0 starts the timing log)
- Turn 2 — Build Phase (Steps 4–12)
- Change Request Workflow
- Output File Structure
- Known Limitations

Converts a single Figma section node into an HTML/CSS/JS preview and a companion
`images/<section-slug>/` folder, then injects the section into a cumulative page file. Run once
per section; each run grows the same page. The HTML and its `images/` folder travel together
(H4). **Before Step 1**, confirm `python3 tools/setup_dependencies.py --check` exits 0 (run the
full setup script first if the user has never installed dependencies — see `PREREQUISITES.md`).
Then run the agent preflight (Clay path + Figma MCP). **Before writing any HTML/CSS for the
section**, run `CLAY-INTEGRATION.md`'s resolution process. **The page shell and every content
section's wrapper nest come from `PAGE-STRUCTURE.md` (H27)** — do not invent a parallel tree.

**This is a two-turn skill.** Turn 1 scouts the design, runs Clay resolution, and presents a
build plan for approval. Turn 2 builds, injects, and delivers.

## Input Requirements

- **Figma URL** (required before Turn 1): must include `?node-id=` pointing to the specific
  section frame. If missing, stop and ask: _"I need a URL that includes a specific node — copy
  the URL while the section frame is selected in Figma."_
- **Designer brief** (optional — the skill infers everything it can from Figma analysis and
  Clay resolution, then presents a build plan for approval. Only genuinely ambiguous items
  trigger questions. If the user provided context in their initial message, those answers are
  extracted automatically — never re-asked).

## State Detection — Which Turn Am I In?

- **Turn 1 state:** no prior scout reply in this thread for this section → run Turn 1 (Steps 1–3).
- **Turn 2 state:** the build plan was posted and the designer replied with approval,
  corrections, or additional context → apply any corrections, then run Turn 2 (Steps 4–12).
- **Quick-approve Turn 2 state:** the designer replied with approval ("looks good", "go ahead",
  "approved", 👍) → proceed to Turn 2 with the plan as stated.
- **Correction state:** the designer corrected something in the plan ("section 3 should use
  the PMO accordion, not build from scratch") → update the plan, confirm the change, proceed.
- **Resumed-after-compaction state (checkable trigger, see `HARD-RULES.md` H26):** the thread
  contains a system-generated conversation summary (not the designer's own words) covering any
  part of this build, and Phase 1 Resolve (`CLAY-INTEGRATION.md`) was run at any point before
  that summary → before proceeding to Turn 2 for any remaining section, explicitly re-state that
  section's Phase 1 anchor (type + component name) in this turn's own output. If the anchor
  itself isn't recoverable from the summary — only a claim that resolution "was done" — treat
  Phase 1 as not yet run for that section and re-run it fresh. Never take a summary's own stated
  "next step" as the process to follow instead of this file.

## Predefined Defaults (never ask)

These are always assumed unless the Figma design explicitly shows otherwise:

| Property | Default | Override trigger |
|---|---|---|
| **Font** | Poppins | Figma shows a different font family |
| **Mobile breakpoint** | 899px | — (Clay standard) |
| **Color palette** | Clay tokens / Figma variables | — |
| **Container** | Clay layout tokens | — |
| **Image handling** | Cloudinary upload, 2x retina | — |
| **QA** | Per-section vision comparison | — (always on) |
| **Copy** | Preserve all Figma copy as-is | — |

State these once in the build plan as assumptions. Never ask about them.

## Inference-first approach

The default mode is **inference, not questions.** For every field the old workflow used to ask
about, the skill now infers from Figma analysis:

| Field | Inference rule |
|---|---|
| **Interactivity** | Scan section dimensions: children arranged horizontally, total width > 2× viewport → CSS marquee; cards/tabs with alternating content → tabs; isolated large number elements → counter animation; otherwise → static. **If none of these patterns clearly apply, this is an `ASK-DONT-GUESS.md` trigger — halt and ask rather than picking one.** |
| **Purpose** | Read dominant text content (headlines, CTAs) — infer in 1 sentence |
| **Page slug** | Derive from section name (slug formula in Step 1), or from the Figma file/page name. If the user already named the page in their message, use that. |
| **Forms** | Only flag if a form element is detected in the Figma (input fields, dropdowns, submit buttons). If no form elements → don't mention forms at all. |
| **Animations** | Only flag if motion tells are detected (marquee clipping, carousel indicators, hover states). If static → state "static section" and move on. |

**Brief extraction rule:** If the user already provided answers in their initial message
(e.g. "build the marketing page from this Figma with tabs"), extract those answers and use
them. Never re-ask what was already stated.

## Turn 1 — Scout Phase

### Step 0: Start the timing log

Before any Figma call, run `date "+%Y-%m-%d %H:%M:%S"` and record the result. This is the only
reliable way to know how long a section actually took — a narrative trace log alone can't answer
"how much time did this take," and file-mtime archaeology after the fact only captures brief
asset-download moments, not the full working span (confirmed directly: reconstructing past
section durations this way was unreliable and had to be caveated as approximate). Log it to the
project's trace file as `[TIME] start <section-slug> (<node-id>): <timestamp>` — this is one
entry in the same tag convention as `[CLAY]`/`[BUG]`/`[TOOL]`/`[QA]`/`[ACCEPTED-GAP]`.

### Step 0.5: Verify Target Node (H42)

**Before parsing or building anything**, confirm you're building the right thing:

1. Identify the Figma URL from the user's **most recent message** in this conversation.
   Do not use URLs from memory, prior turns, or earlier conversations.
2. Parse `fileKey` and `nodeId` from that URL.
3. Run `get_metadata(fileKey, nodeId)` to get the node name.
4. Echo back to the user: _"Building [node name] from node [nodeId]. Correct?"_
5. **Wait for confirmation** before proceeding to Step 1.

If the user sent multiple URLs across messages, use the **last one** unless they explicitly
said otherwise. If no URL was provided in the current conversation, ask for one — never
fall back to a URL from a prior session.

This step exists because of a confirmed ~1hr waste building the wrong Figma page from a
stale memory reference (Aug 31 2026). The cost of asking one question is always less than
the cost of rebuilding from scratch.

### Step 1: URL Parsing and Validation

Extract `fileKey` and `nodeId`:
```
https://www.figma.com/design/<fileKey>/<file-name>?node-id=<int>-<int>
```
`fileKey` = path segment between `/design/` and the next `/`. `nodeId` = the `node-id` value
with `-` replaced by `:` (e.g. `3556-14964` → `3556:14964`).

If no `node-id`, stop: _"I need a URL that includes a specific node — e.g. `?node-id=1234-5678`.
Select the section frame in Figma, then copy the URL."_

**Section slug derivation** (derive now, use throughout): lowercase → replace spaces/underscores/
slashes with hyphens → strip non `a-z0-9-` chars → collapse repeated hyphens → truncate to 48
chars. Example: `"Meet your new teammates"` → `"meet-your-new-teammates"`.

### Step 2: Figma Data Extraction

Run in order:

**2a. `get_metadata(fileKey, nodeId)`** — node name (→ slug), width/height, child count. If it
fails or returns no name, fall back to `section-<nodeId-with-colon-replaced-by-dash>`.

**2b. `get_screenshot(fileKey, nodeId, maxDimension=2048)`** — download immediately:
```bash
curl -sL -o "/tmp/<section-slug>-figma-ref.png" "<screenshot-url>"
```
QA reference only — never page content (H1).

**2c. `get_design_context(fileKey, nodeId, clientFrameworks="html", clientLanguages="html,css")`**
— extract: background color; section padding (T/R/B/L px); layout mode (`HORIZONTAL`→row,
`VERTICAL`→column, `NONE`→likely `position: absolute`); gap; max-width or `FILL`; per-text-node
typography (family, size, weight, color, line-height); border-radius/border/box-shadow; which
children are text/image-fill/vector-icon/nested-frame; gradient fills.

If the response exceeds context limits or returns partial data (see `FIGMA-EXTRACTION.md` for
the full reliability playbook): `get_metadata` to list children, then `get_design_context` per
child, merge results.

**2d. `get_variable_defs(fileKey, nodeId)`** (if variable bindings appear) — extract names +
resolved values.

**2e. `get_libraries(fileKey)`** (once, not per-section) — check for a Clay library subscription
to set `CLAY_DESIGN`.

**2f. Check for an `Assets` frame before decomposing any illustration/mockup panel (H9).** If
the section mixes an illustration with floating fake-UI mockup snippets, run `get_metadata` on
the file looking for `Assets`/`Visual assets`/`Illustrations`. If found, match child frames to
card/section titles, note matched node IDs (exported flat in Step 4c', not read via
`get_design_context`), skip reading their sub-layers. If not found, fall back to H9's naming/
structural heuristics and flag that the designer should consider staging one.

**2g. Emit the measured spec — before any CSS exists.** Everything above is *extraction*: it
gives you what Figma reports. This sub-step is *measurement*: it gives you the handful of numbers
Figma reports badly or not at all, and it must produce written output you build against, not a
mental note. Run all four:

```bash
T=~/.claude/skills/figma-to-web/tools/section_spec.py
python3 $T bg        /tmp/<slug>-figma-ref.png --orig-width <original_width from 2b>
python3 $T textnodes /tmp/<slug>-metadata.json --node-id <nodeId>
python3 $T textsize  /tmp/<slug>-figma-ref.png --box X,Y,W,H --orig-width <original_width>
# after Step 4c' exports the section's assets:
python3 $T assetbg   output/<page>/images/<slug>/*.png --on '<container fill hex>'
```

Two things this exists to force:

- **`--orig-width` is the `original_width` field from 2b's response, not the PNG's width.**
  `get_screenshot` returns a *scaled* PNG plus the design's real dimensions; every pixel you
  measure off that PNG is in PNG px and must be multiplied by `original_width / png_width` to
  become design px. Passing `--orig-width` makes the tool do that for you. Omitting it prints a
  warning and PNG-px numbers, which are wrong by a constant ratio in the same direction for every
  measurement — consistent enough to look like a deliberate scale rather than an error.
- **Measure any font size you did not receive as an explicit number from 2c.** `textsize` finds
  the ink band and divides by the family's cap-height ratio (`--family` selects it). Don't infer a
  size from a design-context snippet's surrounding classes, and don't carry one over from a
  similar-looking earlier section — visual similarity is not a measurement.

Write the results into the section's build notes and the trace (`[PRE-BUILD-CHECK]`, with the
values — see `PRE-BUILD-VERIFICATION.md`'s Logging rule). Then read
`PRE-BUILD-VERIFICATION.md`'s Tier 1 items for what still needs eyes.

### Step 2.5: Run Clay Resolution (Phase 1)

**Before posting the scout message**, run `CLAY-INTEGRATION.md`'s Phase 1 Resolve on the
section. This was previously done at the start of Turn 2 — it now moves here so the build plan
can include Clay matching results.

For full-page mode: run Phase 1 on every top-level section discovered in the page frame.

Record the anchor set for each section: EXACT / CLOSEST / BORROWED / ATOMS_ONLY, with the
matched component name and confidence level.

### Step 3: Post the Build Plan and STOP

The scout message is now a **build plan for approval**, not a questionnaire. It presents what
the skill understood from the Figma, what Clay components will be used, and what will be built
from scratch. The user approves, corrects, or adds context — they don't fill out a form.

```
Here's what I see and my build plan:
[Figma reference screenshot]

**<node-name>** — <width>×<height>px, <child-count> direct children
File: <fileKey> / Node: <nodeId>

**Build Plan:**

| # | Section | Clay Match | Confidence | Plan |
|---|---------|-----------|------------|------|
| 1 | <name>  | <component or "—"> | <EXACT/CLOSEST/BORROWED/none> | <what I'll do> |
| 2 | ...     | ...       | ...        | ...  |

**Assumptions:**
- Font: Poppins
- Page slug: `<inferred-slug>`
- Interactivity: <detected interactions or "static — no interactions detected">
- Copy: preserving all Figma text as-is
<any other inferred details from the user's brief>

**Reference check** — does any section above visually or behaviorally match an existing live
page, competitor site, or prior build (not just "looks like a generic pattern")? If so, name
the section and paste the URL — I'll treat it as the source of truth for that section's
interaction/behavior (never its visuals; Figma still governs those). If none, no reply needed
on this point.

<ONLY if ASK-DONT-GUESS triggers fired:>
**Questions (couldn't figure these out from the design):**
- <specific question about ambiguous interaction, form behavior, etc.>

Approve the plan and I'll build. Or correct anything above.
```

**STOP after posting.** Do not proceed to Turn 2 until the reply arrives.

**What triggers a question (exhaustive list):**
- `ASK-DONT-GUESS.md` conditions: genuinely ambiguous interactivity, forms with unknown
  fields, animations with unspecified behavior, ≥2 interdependent controls needing a state model
- A section resolves to CLOSEST or BORROWED with multiple plausible adaptations
- Figma shows an interactive affordance with no populated content behind it

**What is now always asked, not just on a trigger:** the **Reference check** line above is
part of the standard build-plan template for every section/page build — post it every time,
whether or not any `ASK-DONT-GUESS.md` trigger fired. This is not the general questionnaire
`SKILL.md` deliberately avoids; it's one narrow, standing question folded into the approval
message that already exists, not a separate round-trip.

**Why this exists:** confirmed real case (marketing page, Sep 2026): two separate sections
(a customer-testimonials accordion and a mobile logo-strip marquee) were built to a Figma-only
reading, then had to be substantially reworked over several follow-up turns once the user
revealed — reactively, well after the initial build — that each one was actually meant to match
a specific live reference page's exact CSS/JS mechanism, down to timing values and DOM
structure. The gap wasn't a bad guess; it's that the build plan never asked the question that
would have surfaced the reference *before* building. A Figma frame can look like an
original, from-scratch design and still secretly be a reproduction of something that already
exists live — the model has no way to know that without asking, and the cost of asking once,
up front, is far lower than the cost of reworking a section 5 turns later against a reference
that was known the whole time but never volunteered.

**What NEVER triggers a question:**
- Purpose (read the headlines)
- Font (Poppins unless Figma shows otherwise)
- Copy notes (preserve as-is by default)
- Page slug (infer from file/section name or user's message)
- Whether there's interactivity when the section is clearly static
- Anything the user already stated in their message

## Turn 2 — Build Phase

_Precondition: brief received. Extract `section_purpose`, `interactivity_list`, `copy_notes`,
`page_slug`, `reference_urls` (any link the user gave in reply to the Reference check —
per-section, may be empty)._

**If `reference_urls` has an entry for a section:** treat it exactly as `ASK-DONT-GUESS.md`'s
"After the answer" describes a supplied reference — secondary source of truth for that
section's *behavior only* (interaction model, timing, DOM/CSS mechanism if it's cheap to read
the real page's source). Figma still governs appearance; don't let the reference's visual style
leak in. Read the reference's real rendered behavior (and, where feasible, its actual compiled
CSS/JS rather than just eyeballing the page) before writing that section's interactivity —
the goal is to match the reference's real mechanism the first time, not approximate it and
correct across several follow-up turns.

**Clay resolution was already run in Step 2.5 (Turn 1). Use the anchor set from that step.**
If the designer corrected the plan (e.g. "use PMO accordion instead of building from scratch"),
update the anchor accordingly.

Set paths:
```
DELIVERABLES_DIR = <deliverables folder>/fig-2-web/
PREVIEW_PATH    = DELIVERABLES_DIR/<section-slug>-preview-v01.html
PAGE_PATH       = DELIVERABLES_DIR/<page-slug>-page-v01.html
QA_PATH         = DELIVERABLES_DIR/<section-slug>-qa-v01.png
FIGMA_REF_PATH  = DELIVERABLES_DIR/<section-slug>-figma-ref-v01.png
ASSETS_DIR      = /tmp/<section-slug>-assets/
```
Create `DELIVERABLES_DIR` and `ASSETS_DIR` if missing.

### Step 4: Asset Download

**Two methods — try 4a first, fall back to 4b:**

**4a. CDN URL extraction (preferred).** `get_design_context` emits `const imgX = "https://www.figma.com/api/mcp/asset/..."`
constants — the original uploaded source images, no extra MCP call needed:
```python
import re
CDN_PATTERN = re.compile(r'const (img\w+) = ["\']([^"\']+www\.figma\.com/api/mcp/asset/[^"\']+)["\']')
cdn_assets = {}
for match in CDN_PATTERN.finditer(design_context_code):
    var_name, url = match.group(1), match.group(2)
    ext = url.rsplit('.', 1)[-1].lower() if '.' in url.rsplit('/', 1)[-1] else 'png'
    cdn_assets[var_name] = {'url': url, 'filename': f"{var_name}.{ext}", 'ext': ext}

import subprocess, os
os.makedirs(ASSETS_DIR, exist_ok=True)
for var_name, info in cdn_assets.items():
    dest = os.path.join(ASSETS_DIR, info['filename'])
    subprocess.run(['curl', '-sL', '-o', dest, info['url']], check=True)
```

**Multi-layer photo heuristic:** Figma often stacks multiple images in one card using the same
base variable (`imgImage`) as a placeholder with unique photos on top. The last-declared
variable in DOM order is on top (visible). A base layer shared identically across all cards is
a background texture, not the card photo — prefer the card-specific layer. When ambiguous, use
the variable with the largest declared bounding box.

**4b. Fallback: `download_assets(fileKey, nodeId)`** when 4a returns no CDN URLs. Download
immediately per asset:
```bash
curl -sL -o "<ASSETS_DIR>/<descriptive-name>.<format>" "<asset-url>"
```
Use the response's `format` field as the extension; if `"original"`, infer from the URL, default
`.png`.

**4c'. Export matched Assets-frame visuals as single flat images (H9)** — for each matched node
from Step 2f: `get_screenshot(fileKey, nodeId, maxDimension=<2x longer edge, capped>)`, download
immediately, named descriptively. Don't also pull CDN URLs for fills inside that same node.

**4c. Copy the Figma reference:** `cp "/tmp/<section-slug>-figma-ref.png" "<FIGMA_REF_PATH>"`.

**Before serving any downloaded asset, run `file <path>`** — an implied extension doesn't
always match the true format (see `GOTCHAS.md`).

### Step 5: Token Resolution

**Primary method: `CLAY-INTEGRATION.md`'s resolution process** for any section it resolved.

**Fallback — raw variable → CSS custom property mapping**, for values not covered:

| Figma variable pattern | CSS custom property |
|---|---|
| `color/brand/primary` | `var(--clay-color-brand-primary)` |
| `color/brand/secondary` | `var(--clay-color-brand-secondary)` |
| `color/bg/primary` | `var(--clay-color-bg-primary)` |
| `color/bg/secondary` | `var(--clay-color-bg-secondary)` |
| `color/bg/tertiary` | `var(--clay-color-bg-tertiary)` |
| `color/text/primary` | `var(--clay-color-text-primary)` |
| `color/text/secondary` | `var(--clay-color-text-secondary)` |
| `color/text/disabled` | `var(--clay-color-text-disabled)` |
| `color/border/primary` | `var(--clay-color-border-primary)` |
| `color/border/secondary` | `var(--clay-color-border-secondary)` |
| `spacing/4xl`…`spacing/2xs` | `var(--clay-spacing-4xl)` … `var(--clay-spacing-2xs)` |
| `radius/s`…`radius/full` | `var(--clay-radius-s)` … `var(--clay-radius-full)` |

For any variable not in this table, use the raw resolved hex/px value. **`grep` any token name
against the compiled `tokens.css` before trusting it** — names drift between repo versions.

**This table assumes the Figma file's own variable names resemble Clay's naming convention
(`color/brand/primary`, etc.) — a real downstream product file's variables may share no naming
convention with Clay's at all** (confirmed case: variable names were specific to that file's own
design-token system, unrelated to Clay's). When that's true, the table above is unusable as
written. **What actually works: resolve the Figma variable to its literal value (hex/px) first,
then `grep` the compiled `tokens.css` by *value*, not by name**, to find whether a matching real
Clay token already exists — matching by name only works when the source file happens to share
Clay's vocabulary, which is not guaranteed just because `CLAY_DESIGN=true`.

If `CLAY_DESIGN=false`: use raw hex/px values directly, no `var(--clay-*)` references.

### Step 6: HTML Section Block Generation

```html
<!-- SECTION: <section-slug> -->
<section id="<section-slug>" data-section="<section-slug>" data-page="<page-slug>" class="section-<section-slug>">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <!-- unique section content here — never directly in section / padding-global / container-large -->
      </div>
    </div>
  </div>
</section>
<!-- /SECTION: <section-slug> -->
```

Header/nav and footer do **not** use this nest. If this node's `role` is `header` or `footer`
(`FULL-PAGE-WORKFLOW.md` Step 2 / `PAGE-STRUCTURE.md`), emit:

```html
<header data-section="<section-slug>" data-chrome="header" data-page="<page-slug>">
  <!-- chrome content — own layout, H25 -->
</header>
```

(or `<footer data-chrome="footer">`). Do not wrap chrome in `padding-global`.

CSS as a scoped `<style>` block above the section, every *section-specific* class prefixed with the section slug.
Do **not** re-declare `.padding-global` / `.container-large` / `.padding-section-large` here — those live
once in the page shell (Step 7).
(never generic names like `.hero`/`.card`/`.button` without the prefix, to prevent collisions
when multiple sections share a page):

```html
<style>
.section-<section-slug> {
  background: <bg-color>;
  padding: <padding-top> <padding-right> <padding-bottom> <padding-left>;
  width: 100%;
}
.section-<section-slug>-inner {
  display: flex; flex-direction: <row|column>; gap: <gap>;
  align-items: <align from Figma>;
}
.section-<section-slug> .heading {
  font-family: <font-family>, system-ui, sans-serif;
  font-size: <size>px; font-weight: <weight>; color: <color>; line-height: <line-height>;
}
</style>
```

**Rules:** `px` for all extracted measurements. Responsive: `@media (max-width: 768px)` stacks
to `flex-direction: column`, reduces font sizes ~15%. Images: `<img src="..." alt="..." width="<intrinsic-w>" height="<intrinsic-h>" loading="<eager|lazy>" class="section-<slug>-<role>">`
(H11–H13).

**Media slot pattern (H9 + H10 + H12):**
```css
.section-<slug>-visual {
  width: <intrinsic-w>px;   /* or 100% in a flexible layout */
  aspect-ratio: <intrinsic-w> / <intrinsic-h>;
  border-radius: 0 <r>px <r>px 0;
  overflow: hidden;
  background: <fallback bg color matching the panel's own fill>;
}
.section-<slug>-visual img { width: 100%; height: auto; display: block; }
```
Never add a breakpoint override with a fixed `height` — only change `position`/`width` between
breakpoints; `aspect-ratio` + `height: auto` carries the correct height at every size.

**Approved CSS simplification for multi-layer/negative-offset photo compositions:** Figma's
`left: -Npx; width: W+Npx` panned-crop pattern maps to `overflow: hidden` on the container plus
`width: 100%; height: 100%; object-fit: cover; object-position: <match crop direction>` on the
`<img>` — faithful to the visual intent without replicating exact pixel offsets.

**Interactivity — add only what was specified in the brief, or halted-and-asked per
`ASK-DONT-GUESS.md` if unclear:**

_Tabs:_
```html
<div class="section-<slug>-tabs">
  <div class="tab-nav" role="tablist">
    <button class="tab-btn active" role="tab" data-tab-target="tab-<slug>-0" aria-selected="true">Tab 1</button>
    <button class="tab-btn" role="tab" data-tab-target="tab-<slug>-1" aria-selected="false">Tab 2</button>
  </div>
  <div class="tab-panels">
    <div class="tab-panel active" id="tab-<slug>-0" role="tabpanel">...</div>
    <div class="tab-panel" id="tab-<slug>-1" role="tabpanel">...</div>
  </div>
</div>
<style>
.section-<slug>-tabs .tab-panel { display: none; }
.section-<slug>-tabs .tab-panel.active { display: block; }
</style>
<script>
(function() {
  var tabs = document.querySelector('.section-<slug>-tabs');
  if (!tabs) return;
  var btns = Array.from(tabs.querySelectorAll('.tab-btn'));
  var panels = Array.from(tabs.querySelectorAll('.tab-panel'));
  function activate(i) {
    btns.forEach(function(b, j) { b.classList.toggle('active', j === i); b.setAttribute('aria-selected', j === i ? 'true' : 'false'); });
    panels.forEach(function(p, j) { p.classList.toggle('active', j === i); });
  }
  btns.forEach(function(btn, i) { btn.addEventListener('click', function() { activate(i); }); });
  var current = 0;
  var interval = setInterval(function() { current = (current + 1) % btns.length; activate(current); }, 5000);
  tabs.addEventListener('mouseenter', function() { clearInterval(interval); });
})();
</script>
```

_Counter/stats (IntersectionObserver):_ mark each stat with `data-count="<target>"`:
```javascript
<script>
(function() {
  var counters = document.querySelectorAll('[data-section="<section-slug>"] [data-count]');
  if (!counters.length) return;
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (!entry.isIntersecting) return;
      var el = entry.target, target = parseInt(el.getAttribute('data-count'), 10);
      var duration = 1500, start = null;
      function step(ts) {
        if (!start) start = ts;
        var progress = Math.min((ts - start) / duration, 1), eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * target).toLocaleString();
        if (progress < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step); observer.unobserve(el);
    });
  }, { threshold: 0.4 });
  counters.forEach(function(c) { observer.observe(c); });
})();
</script>
```

_CSS marquee:_
```html
<div class="section-<slug>-marquee-viewport" aria-hidden="true">
  <div class="section-<slug>-marquee-track"><!-- items, duplicated once for seamless loop --></div>
</div>
<style>
/* Full-bleed: a marquee track must span the real browser viewport, not just its parent's
   content box — mount it outside .container-large/.padding-global, or break out of them:
   width: 100vw; margin-left: calc(-50vw + 50%);  (parent must not have overflow-x: hidden
   above this point in the tree, or the breakout clips itself). A marquee built inside the
   page's normal padded container silently looks "contained," not full-bleed, even though
   nothing about the animation itself is wrong. */
.section-<slug>-marquee-viewport { overflow: hidden; width: 100%; }
.section-<slug>-marquee-track {
  display: flex; gap: <gap from Figma>px; width: max-content;
  animation: marquee-<section-slug> <duration>s linear infinite;
  /* Duration: total_single_set_width_px / 100 ≈ 100px/s. Tune to ~150px/s for logo bars,
     ~60px/s for readable quote strips. */
}
.section-<slug>-marquee-track:hover { animation-play-state: paused; }
/* -50%, not -100%: the track holds TWO copies of the content (duplicated once above for a
   seamless loop), so its own width is 2x one copy's width. Translating by -100% moves a full
   two-copy distance — past where the second copy lines up with the viewport start — leaving a
   blank gap before the loop repeats. -50% moves exactly one copy's width, landing the second
   copy where the first one started, which is what makes the loop actually seamless. Confirmed
   real bug (Sep 2026): a build used -100% here and produced a visible blank flash every cycle. */
@keyframes marquee-<section-slug> { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
@media (prefers-reduced-motion: reduce) { .section-<slug>-marquee-track { animation: none; } }
</style>
```

_GSAP scroll-reveal:_ add `class="reveal"` to elements that should animate in:
```javascript
<script>
gsap.registerPlugin(ScrollTrigger);
gsap.from('[data-section="<section-slug>"] .reveal', {
  scrollTrigger: { trigger: '[data-section="<section-slug>"]', start: 'top 80%', toggleActions: 'play none none none' },
  y: 36, opacity: 0, duration: 0.65, stagger: 0.10, ease: 'power2.out'
});
</script>
```

_Static (no interactivity specified):_ pure HTML/CSS only, no `<script>` tags.

### Step 7: Page Shell Construction

Used for both the preview file and the initial page file.

**Custom font detection:** scan typography for any `font-family` not in the system stack
(`system-ui`, `Inter`, `Arial`, `Helvetica`, `Georgia`, `Times New Roman`). If found: check
Google Fonts availability; if available, set `GOOGLE_FONT_FAMILY`/`GOOGLE_FONT_WEIGHTS`; if not
(a custom/proprietary font), note the gap and fall back to `system-ui`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><page-slug> — <section-name></title>
  <!-- <link href="<GOOGLE_FONT_URL>" rel="stylesheet"> — only if a non-system font was detected -->
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { min-height: 100%; }
    body { font-family: '<detected-font>', system-ui, -apple-system, sans-serif; -webkit-font-smoothing: antialiased; color: #111; }
    img { display: block; max-width: 100%; height: auto; }
    /* PAGE-STRUCTURE.md shell — class names fixed; values = this page's H22 pair (Clay token or Figma, see PAGE-STRUCTURE.md) */
    .padding-global { padding: 0 var(--clay-layout-section-padding-x, 2.5rem); }
    @media screen and (max-width: 767px) {
      .padding-global { padding: 0 var(--clay-layout-section-padding-x-mobile, 1.5rem); }
    }
    .container-large { width: 100%; max-width: var(--clay-layout-container-large, 80rem); margin: 0 auto; }
    .padding-section-large { padding: clamp(4rem, 3.4286rem + 2.8571vw, 6rem) 0; }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }
  </style>
  <!-- GSAP CDN: only if this section uses scroll-reveal or another GSAP animation -->
</head>
<body>
<div class="page-wrapper">
  <header>
    <!-- empty until a role=header node is built; then replaced as a whole -->
  </header>
  <main class="main-wrapper">
<style>/* Section styles for <section-slug> */</style>
<!-- SECTION: <section-slug> -->
<section id="<section-slug>" data-section="<section-slug>" data-page="<page-slug>" class="section-<section-slug>">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <!-- section HTML content -->
      </div>
    </div>
  </div>
</section>
<!-- /SECTION: <section-slug> -->
<!-- section-scoped scripts here -->
<!-- SECTIONS_END -->
  </main>
  <footer>
    <!-- empty until a role=footer node is built; then replaced as a whole -->
  </footer>
</div>
</body>
</html>
```

**GSAP CDN rule:** uncomment the CDN `<script>` tags in `<head>` if and only if scroll-reveal or
another GSAP animation was requested. Tabs, counters, marquee need no GSAP — pure JS + CSS.

**Preview file** = this shell with the section (or chrome) inside, written to `PREVIEW_PATH`.
**Initial page file** (first node for this page) = the same shell, written to `PAGE_PATH`.

If this node's `role` is `header` or `footer`, put that chrome in `<header>` / `<footer>` and
leave `main.main-wrapper` containing only `<!-- SECTIONS_END -->` — do not also park a content
`<section>` in `main` for chrome.

### Step 8: Image Compression and Folder Export (H4 — no base64)

Run the PIL compression pipeline on `PREVIEW_PATH`, writing real files into
`IMAGES_DIR = <DELIVERABLES_DIR>/images/<section-slug>/` and rewriting `<img>` `src` to relative
paths — never base64.

**Size the resize target to the image's actual rendered display width, not a flat ceiling.**
Confirmed real case: a set of carousel cards displayed at ~300px CSS width shipped with Figma
source assets at their raw uploaded resolution (2304×4096–3277×4096px) — a flat `max_width=1440`
default still left each file 5–10x larger than its on-screen size ever needs (multiple 1.5–2.9MB
files for a 300px-wide slot), and was reproducibly heavy enough to cause visible scroll/render
jank in downstream QA tooling. `max_width=1440` is a reasonable *ceiling* for a genuinely
full-bleed/hero image, but it is not a safe default for every image regardless of how small its
own container actually is.

```python
import os
from PIL import Image

IMAGES_DIR = os.path.join(DELIVERABLES_DIR, "images", section_slug)
os.makedirs(IMAGES_DIR, exist_ok=True)

RETINA_FACTOR = 2       # render at 2x the CSS display width for crisp high-DPI screens
CEILING_WIDTH = 1600    # never exceed this even for a full-bleed hero/background image

def resize_target_width(display_width_px, ceiling=CEILING_WIDTH):
    """display_width_px = the image's real rendered CSS width in this section (from
    get_design_context/get_metadata, or the container it fills) — NOT the source asset's
    intrinsic width. Falls back to the ceiling only when no display width is knowable
    (e.g. a background used at multiple sizes) — never as the default for a normal <img>."""
    if display_width_px is None:
        return ceiling
    return min(int(display_width_px * RETINA_FACTOR), ceiling)

def compress_raster(image_path, dest_path, display_width_px=None, jpeg_quality=82):
    max_width = resize_target_width(display_width_px)
    with Image.open(image_path) as img:
        if img.mode == 'RGBA':
            if img.width > max_width:
                ratio = max_width / img.width
                img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
            img.save(dest_path, format='PNG', optimize=True); return
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        if img.mode not in ('RGB', 'L'): img = img.convert('RGB')
        img.save(dest_path, format='JPEG', quality=jpeg_quality, optimize=True)

def copy_svg(svg_path, dest_path):
    with open(svg_path, 'rb') as f: data = f.read()
    with open(dest_path, 'wb') as f: f.write(data)

RASTER_EXTS, SVG_EXTS = ('.png', '.jpg', '.jpeg', '.webp', '.gif'), ('.svg',)
exported = {}
for fname in os.listdir(ASSETS_DIR):
    fpath, dest, low = os.path.join(ASSETS_DIR, fname), os.path.join(IMAGES_DIR, fname), fname.lower()
    if low.endswith(SVG_EXTS): copy_svg(fpath, dest)
    elif low.endswith(RASTER_EXTS):
        # display_width_px: read from this image's own CSS width in the section being built
        # (get_design_context's layout data), not guessed — see resize_target_width above.
        compress_raster(fpath, dest, display_width_px=known_display_width_for(fname))
    else: continue
    exported[fname] = f"images/{section_slug}/{fname}"

def relink_assets_in_html(html_path, exported):
    """Point src="<filename>" at the exported relative path — used for BOTH the preview
    file here AND the page file in Step 9g. Never base64 for either (H4)."""
    with open(html_path, 'r', encoding='utf-8') as f: html = f.read()
    for fname, rel_path in exported.items():
        html = html.replace(f'src="{fname}"', f'src="{rel_path}"').replace(f"src='{fname}'", f"src='{rel_path}'")
    with open(html_path, 'w', encoding='utf-8') as f: f.write(html)
    return os.path.getsize(html_path)

preview_html_bytes = relink_assets_in_html(PREVIEW_PATH, exported)
images_total_bytes = sum(os.path.getsize(os.path.join(IMAGES_DIR, f)) for f in os.listdir(IMAGES_DIR))
print(f"Preview HTML: {preview_html_bytes/1024:.0f}KB — images/ folder: {images_total_bytes/1024:.0f}KB")
# The HTML should now be tiny (tens of KB) — no encoded image data. If it's still large,
# something is being embedded — check for a leftover data: URI.
```

Note the two files that must ship together from now on: the HTML and its
`images/<section-slug>/` folder. State this explicitly in Step 12.

### Step 9: Page Accumulation — Sentinel Injection

**9a.** `page_exists = os.path.isfile(PAGE_PATH)`.

**9b. Duplicate check (H6).** If `page_exists` and `data-section="<slug>"` already appears,
stop and warn: _"Section '<slug>' already exists in <page-slug>-page-v01.html. Reply 'replace
it' to overwrite, or 'skip' to keep it."_ Raise and await instruction. If the user said "replace
it," remove the existing block (`<!-- SECTION: slug --> … <!-- /SECTION: slug -->`) first, then
proceed as Case B.

**9c. Extract the new section block** (plus its scoped `<style>` block) from the preview HTML.

**9d. Extract new `<head>` dependencies** not already in the page file (script `src`s, link
`href`s) — only inject the ones missing (H8).

**9e. Case A — first section for this page:** copy `PREVIEW_PATH` → `PAGE_PATH` verbatim. The
preview must already be the `PAGE-STRUCTURE.md` shell (H27). Verify the sentinel sits immediately
before `</main>` (H7) — abort loudly if not.

**9f. Case B — subsequent content section (`role=section`):** back up `PAGE_PATH` first (`.bak`).
Inject the new section block + an audit comment (`<!-- SECTION_ADDED: <slug> on <date> -->`)
immediately before the sentinel; inject any new head dependencies before `</head>`. Write, then
re-read and verify the sentinel is still immediately before `</main>` (H7) — if not, restore the
backup immediately and raise, do not retry blindly. Remove the backup only after a verified
successful write.

**9f-chrome. Subsequent header/footer (`role=header` or `role=footer`):** replace the empty
`<header>` or `<footer>` in the shell with the chrome block (`data-chrome="header"` /
`data-chrome="footer"`). Do not inject chrome before the sentinel and do not wrap it in
`padding-global`. Same backup/verify discipline as 9f.

**9g. Relink assets in the page file — same pipeline as Step 8, never base64.** Run
`relink_assets_in_html(PAGE_PATH, exported)` (the same function from Step 8) so the accumulated
page's `<img>` tags point at the real `images/<section-slug>/` files exactly like the preview
does. **Do not run a base64-embed pipeline here** — H4 applies uniformly to both files; an
earlier draft of this workflow embedded the page file as base64 while keeping the preview file
as real links, which directly contradicted H4 and is not the intended behavior.

**9h.** Count sections: `page_final.count('<!-- SECTION:')`.

### Step 10: QA Screenshot

Take a screenshot of the preview file for comparison against the Figma reference — this feeds
the mandatory per-section vision QA in `ACCURACY-GATE.md`; the screenshot alone is not the QA
step, looking at it next to the Figma reference is.

**Serve over `http://localhost`, never `file://`** (`GOTCHAS.md`'s asset-loading gotcha: a bare
`file://` URL has no real network layer for local relative-path assets, so every `<img>` can
silently fail to load while the screenshot still looks plausible). Start the server **once per
session**, before the first section, not per section: `python3 -m http.server <port> --directory
<DELIVERABLES_DIR>` in the background, then load `http://localhost:<port>/<section-slug>-preview-v01.html`.

```python
import asyncio
from playwright.async_api import async_playwright

async def take_qa_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=CHROMIUM_PATH)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(f"http://localhost:{PORT}/{os.path.basename(PREVIEW_PATH)}")
        await page.wait_for_timeout(1800)  # let CSS animations (marquee, transitions) settle
        await page.screenshot(path=str(QA_PATH), full_page=True)
        await browser.close()

asyncio.run(take_qa_screenshot())
```

**`CHROMIUM_PATH` must be discovered, never hardcoded** — see `PREREQUISITES.md`/
`CLAY-INTEGRATION.md`'s discovery pattern; a prior version of this workflow hardcoded a
machine-specific path here that doesn't exist on other machines.

Sync API alternative (simpler, fine for static sections) uses the same discovered
`CHROMIUM_PATH`, scrolls to trigger IntersectionObserver-gated animations, then screenshots
full-page. If Playwright fails (chromium not found, launch error), note it and continue — the
HTML files are still valid deliverables.

### Step 10b: `tools/qa_gate.py` — mandatory, run here, not just described in `ACCURACY-GATE.md`

**Confirmed real regression this replaces:** the two third-party tools previously required at this
step were marked "mandatory, not optional," and a full section-by-section build still shipped
with neither ever invoked inside the actual per-section loop — the mandate living only in
a file that *describes* the gate conceptually, rather than in the file that drives the build turn
by turn, was not enough to make it run. The fix isn't a better reminder; it's a single command
with an exit code, run here, every section, right after the QA screenshot and before delivery:

```bash
python3 ~/.claude/skills/figma-to-web/tools/qa_gate.py section \
    --url http://localhost:<port>/<section-slug>-preview-v01.html \
    --selector '[data-section="<section-slug>"]' \
    --spec /tmp/<section-slug>-spec.json
```

See `ACCURACY-GATE.md` §1b for the full check list this runs (numeric re-diff against the
pre-build spec, leaf-centering, image-loaded, a11y disclosure state, 3-width overflow) and what
its `vision_owned` output means. Triage every finding: fix it, or log an explicit accepted-gap
reason. **Log the outcome either way** — `[QA] <slug>: qa_gate clean, N checks` or
`[BUG] <slug>: <rule-id> <measured> vs. <expected>` — so a later reader of the trace can tell "ran
clean" apart from "never ran," the same distinction `PRE-BUILD-VERIFICATION.md`'s
`[PRE-BUILD-CHECK]` tag makes for the pre-build checklist. A section is not through Turn 2 until
this has a log line and exits 0, same discipline as the vision QA screenshot.

**For any section with an interactive component that has desktop-only controls** (carousel
arrows, a tab bar), explicitly verify a mobile-equivalent navigation mechanism exists (dots,
swipe), that it's wired to both a real click handler and real touch-swipe — not just visually
present — and that mobile precision-matching also checked structure (`flex-direction`/`order`),
not just size. See `HARD-RULES.md` H40 and `GOTCHAS.md`'s entry on desktop-only navigation.

### Step 10c: `tools/visual_diff.py` + `tools/diff_enrich.py` — pixel-level Figma comparison

After qa_gate passes (Step 10b), run the visual diff pipeline for an objective pixel-level
comparison between the Figma reference and the built HTML. This is the final automated QA step
before delivery.

**Important: screenshot at 2x to match Figma's 2x export.** 1x vs 2x comparison creates
massive false positives from upscaling — this is a hard rule.

```bash
# 1. Take HTML screenshot at 2x
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 2000}, device_scale_factor=2)
    page.goto('http://localhost:<port>/<preview-file>')
    page.wait_for_load_state('networkidle')
    section = page.query_selector('[data-section=\"<slug>\"]')
    section.screenshot(path='/tmp/<slug>-html-2x.png')
    # DOM map for region-to-element matching
    import json
    dom_map = page.evaluate('''() => {
        const s = document.querySelector('[data-section=\"<slug>\"]');
        if (!s) return [];
        const r = s.getBoundingClientRect();
        const d = window.devicePixelRatio || 1;
        return [...s.querySelectorAll('*')].map(el => {
            const b = el.getBoundingClientRect();
            return {
                selector: el.tagName + (el.className ? '.' + [...el.classList].join('.') : ''),
                label: el.getAttribute('aria-label') || (el.textContent||'').trim().slice(0,40) || '',
                x: Math.round((b.x - r.x) * d), y: Math.round((b.y - r.y) * d),
                width: Math.round(b.width * d), height: Math.round(b.height * d)
            };
        }).filter(d => d.width > 10 && d.height > 10);
    }''')
    with open('/tmp/<slug>-dom-map.json', 'w') as f: json.dump(dom_map, f)
    browser.close()
"

T=~/.claude/skills/figma-to-web/tools

# 2. Run visual diff
python3 $T/visual_diff.py \
    --figma /tmp/<slug>-figma-ref.png \
    --html /tmp/<slug>-html-2x.png \
    --output /tmp/<slug>-diff/ \
    --section-name <slug> \
    --dom-map /tmp/<slug>-dom-map.json \
    --threshold 5.0

# 3. If diff > threshold, run enrichment for actionable fix brief
python3 $T/diff_enrich.py \
    --report /tmp/<slug>-diff/<slug>-diff-report.json \
    --url http://localhost:<port>/<preview-file> \
    --selector '[data-section="<slug>"]' \
    --figma-file <fileKey> \
    --figma-node <nodeId>
```

**Interpreting results:**
- **Pixel diff ≤ 5%:** PASS — proceed to delivery. Log `[QA] <slug>: visual_diff PASS, SSIM <score>%`.
- **Pixel diff > 5%:** Read the enriched fix brief. Each region lists the DOM element, the
  diff type (layout/spacing/color/missing_element), and the Figma-vs-HTML CSS comparison
  with exact fix suggestions. Apply the top fixes, re-screenshot, re-diff.
- **Image-heavy sections** may show persistent diff from rendering pipeline differences
  (Figma exports vs browser rendering). If the only remaining diffs are in exported-image
  regions and text/layout regions pass — log as accepted gap and proceed.

**Outputs attached to delivery (Step 12):**
- Side-by-side diff image
- SSIM score + pixel diff % in the delivery reply
- If NEEDS_FIX: heatmap + enriched fix brief summary

Log: `[QA] <slug>: visual_diff <PASS|NEEDS_FIX>, SSIM <score>%, pixel_diff <pct>%, <N> regions`.

### Step 11: File Delivery

Copy the preview HTML, QA screenshot, and the **entire images folder** together — never the
HTML alone (H4). State explicitly that both must travel together and that a plain file-preview
pane (e.g. Slack's) will likely show broken images unless both are downloaded into the same
local directory. The accumulated page file is not part of routine delivery — it can be large
after many sections; share it only if asked.

### Step 12: Delivery Reply

Before writing the reply, run `date "+%Y-%m-%d %H:%M:%S"` again and log
`[TIME] end <section-slug> (<node-id>): <timestamp>, duration <computed duration>` to the
project's trace file, right next to the `[TIME] start` entry from Step 0 — this pair is what
makes "how long did this take" answerable later without reconstruction. Note *why* in one clause
if the section was unusually fast or slow (e.g. "reused a prior build", "required fetching a live
site's real CSS", "straightforward Clay EXACT match") — that qualitative tag is what turns a
timing log into something actionable for shortening the process, not just a stopwatch.

```
Section built: **<node-name>** (<width>×<height>px)

Page: `<page-slug>-page-v01.html` — section <N> of <N> total
Preview: `<section-slug>-preview-v01.html` + `images/<section-slug>/` folder (download BOTH into
the same directory)

What was built:
- Layout: <flex row | flex column | grid>, <N> child elements
- Background: <color value>
- Interactivity: <what was added, or "none — static HTML/CSS">
- Images: <N> assets exported to `images/<section-slug>/` (<KB/MB total>, not embedded)
- Tokens: <Clay CSS custom properties | raw Figma values> | Clay anchor: <EXACT/CLOSEST/BORROWED/ATOMS_ONLY/none>

Sections in `<page-slug>-page-v01.html` so far: 1. <slug> … N. <slug> ← just added

Time: <duration> (started <start timestamp>, finished <end timestamp>)

QA screenshot attached — compared to the Figma reference from Turn 1 (per-section vision QA:
PASS/issues noted).

Known gaps (anything approximated, or halted-and-asked per ASK-DONT-GUESS.md): <list, or "none">

To add the next section, run this skill again with a new Figma section node URL and page slug
`<page-slug>`.
```

## Change Request Workflow

After the initial build, the designer may request changes — fix spacing, adjust font sizes,
swap content, change colors, rework layout, etc. **These fixes must go through the same
measurement → fix → verify loop as the initial build.** The difference is scope (one property
or section, not the whole page) — not rigor.

**Why this exists:** Confirmed pattern across multiple builds — initial sections score 8-9/10
through the full QA pipeline, then regress to 6-7/10 after ad-hoc fixes that skip measurement
and verification. The fix itself is usually correct, but it breaks something adjacent (spacing,
alignment, responsive behavior) that only shows up in a QA screenshot.

### CR Step 1: Scope the change

Identify exactly what's being changed:
- **Which section(s)?** Re-scope to that section only.
- **Which property?** Size, color, spacing, content, layout, interaction, image.
- **Is this a Figma delta or a subjective adjustment?** If the Figma was updated, re-extract
  the updated values from Figma (re-run `get_design_context` on the changed nodes). If it's a
  subjective request ("make it bigger", "more padding"), confirm the exact target value before
  changing.

### CR Step 2: Re-measure before fixing

Run the relevant `section_spec.py` subcommand(s) for the property being changed:

| Change type | Re-measure with |
|---|---|
| Font size/weight/line-height | `textsize` on the affected text area |
| Background/color | `bg` on the section screenshot |
| Content/copy | `textnodes` on the section metadata |
| Spacing/padding/gap | `get_design_context` on the section + parent |
| Image/asset swap | `assetbg` on the new asset |
| Layout/structure | `get_design_context` + `PRE-BUILD-VERIFICATION.md` items for that section |
| Interaction/animation | Re-read `ASK-DONT-GUESS.md` — does the change introduce ambiguity? |

If the change involves layout or structural modification, run `PRE-BUILD-VERIFICATION.md`'s
checklist items relevant to the affected section. Not the full checklist — just the items that
touch what's changing.

Get the actual value from Figma or from the measurement tool. Don't eyeball it.

### CR Step 2.5: Build the change checklist (H43)

Before applying anything, decompose the request into a **numbered checklist**:

```
Change checklist:
1. [specific change 1] — section: <slug>, property: <what>
2. [specific change 2] — section: <slug>, property: <what>
...
```

Each item must be specific enough to verify with `grep` or DOM inspection after applying.
Vague items like "fix the section" must be decomposed into concrete properties.

Post the checklist to the user before applying, so they can confirm scope.

### CR Step 3: Apply the fix

- Change ONLY what was requested (R5 — don't touch what wasn't asked).
- If the fix requires touching CSS that's shared with other sections, note which sections
  could be affected.

### CR Step 4: Re-run QA on the affected section

1. **`qa_gate.py`** on the changed section — compare against the Figma reference.
2. **`visual_diff.py` + `diff_enrich.py`** — re-run the pixel diff pipeline (Step 10c).
   Compare the SSIM score before and after the fix. If the score went down, the fix broke
   something. If it went up but is still above threshold, check what remains.
3. **Vision QA:** Screenshot the section after the fix. Compare:
   - Against the Figma reference (did the fix bring it closer?)
   - Against the pre-fix state (did the fix break anything else in this section?)
4. **Neighbor check:** If the section shares spacing, overlapping elements, or visual flow with
   adjacent sections, screenshot the surrounding context too. A padding fix on section 3 can
   break the visual rhythm with sections 2 and 4.

### CR Step 5: Verify nothing else broke

1. **`qa_gate.py`** on the full page (not just the changed section).
2. **Quick vision scan** of adjacent sections — especially if CSS changes could cascade.
3. **Section count check:** `grep -c "<section" file.html` — confirm no duplicates were
   introduced by the edit.

### CR Step 5.5: Verify the change checklist (H43)

Before reporting, verify every item from CR Step 2.5:

```
Verification:
1. ✅ grep confirms "new text" present in section (line N)
2. ✅ computed padding-top is 48px (was 32px)
3. ❌ CTA color still blue — fixing now
```

- Use `grep -n` for text/content changes
- Use Playwright `evaluate` or screenshot for visual/CSS changes
- Use `qa_gate.py` output for structural changes

**Never report "done" with any ❌ items.** Fix first, re-verify, then report.

### CR Step 6: Report the change

```
**Change applied:** <what was changed>
**Section:** <section name>
**Measured value:** <what Figma/spec says> → **Applied:** <what was set>
**Checklist:** all N items verified ✅
**QA:** <PASS / issues noted>
**Neighbor impact:** <none / list affected sections>
```

Attach the QA screenshot.

### When to skip (lightweight changes only)

The full CR workflow can be abbreviated to CR Steps 3 + 4 only (skip re-measurement, skip
full-page QA) when ALL of these are true:
- The change is pure content swap (replacing text, not resizing/repositioning)
- No CSS is modified
- No layout properties are affected
- The section has no shared CSS with other sections

If any of these conditions are false, run the full CR workflow.

---

## Output File Structure

```
fig-2-web/
├── <section-slug>-figma-ref-v01.png
├── <section-slug>-preview-v01.html      ← standalone preview (links to images/, not self-contained)
├── <section-slug>-qa-v01.png
├── <page-slug>-page-v01.html            ← accumulated page (OVERWRITTEN each run, grows by one section)
└── images/
    ├── <section-slug>/                  ← this run's exported images (real files, H4)
    └── <other-section-slug>/            ← previous sections' images, still referenced
```

The page file is overwritten (not versioned) each run so one browser tab can reload to see the
page grow. The `images/` folder only ever grows — every prior section's subfolder must stay in
place.

## Known Limitations

- **Complex absolute/overlapping layouts** are usually a sign of a composite visual asset, not
  structure to translate — check for an `Assets` frame per H9 before hand-tuning CSS.
- **Multi-layer photo stacking:** a shared base/texture layer across cards is a placeholder, not
  a card photo — see the Step 4a heuristic. Doesn't apply to a matched H9 Assets-frame panel.
- **Figma prototype interactions** (hover states as prototype transitions, not component
  properties) are not captured by `get_design_context` — must come from the brief, or trigger
  `ASK-DONT-GUESS.md` if the brief doesn't cover them.
- **Custom/proprietary fonts** fall back to `system-ui` — flag it, don't silently substitute.
- **Context limit on dense sections:** `get_metadata` → per-child `get_design_context` → merge.
- **SVG fill images** appear in `download_assets` as `.svg` — copy byte-for-byte, no PIL
  compression; inline directly (`<svg>...</svg>`) rather than as `<img>` for CSS fill control.
- **Page file growth over time:** after many sections the page file may be large — the images
  stay as real linked files regardless (H4 has no size-based exception).

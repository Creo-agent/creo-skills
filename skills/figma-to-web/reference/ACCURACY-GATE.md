# Accuracy Gate

## Contents
- The severity vocabulary — the only pass/fail gate
- 1. Per-section vision QA (primary, mandatory)
- 1b. tools/qa_gate.py — the numeric re-diff against the pre-build spec
- 1c. Component-zoom pass — small elements are invisible at page zoom
- 2. Full-page vision pass
- 3. Logging

## The severity vocabulary — the only pass/fail gate

**`web-design-rules.csv`**'s `hard`/`soft` severity is the only pass/fail gate in this skill. Per
`QA-SCORECARD.md`'s locked decision: **a section is DONE iff zero `hard` rules fail.** Every rule
also carries an `owner` column — `script` (mechanized in `tools/qa_gate.py`, can never be silently
skipped), `vision` (the deliberate, short list a human/model actually looks for), `pre-build`
(checked before any CSS exists, via `CLAY-INTEGRATION.md`/`PRE-BUILD-VERIFICATION.md`), or `n-a`.
`HARD-RULES.md`'s own H-rules carry the same tag inline under each heading. **Run-validator → fix
→ repeat, in this order, every time** — `tools/qa_gate.py` catches what the eye tends to miss
(arithmetic, accessibility attributes, page-wide consistency); vision QA catches what no script
can (does this actually look like the Figma reference). Neither step is optional and neither
substitutes for the other.

## 1. Per-section vision QA (primary, mandatory)

**For every section, as it's built — never skipped, never batched to the end.**

1. Capture the built section and its Figma reference at the same viewport (`section-ref/` from
   `FULL-PAGE-WORKFLOW.md` Step 3B / `SECTION-WORKFLOW.md` Step 2b).
2. **Actually look at both images side by side.** Score against `web-design-rules.csv` (below)
   and the legacy 4-dimension rubric in `QA-SCORECARD.md`.
3. **Every `hard`-severity rule in `web-design-rules.csv` must pass.** A section with any
   failing hard rule is not done — average it against nothing, don't let unrelated successes
   offset a hard failure.
4. `soft`-severity findings are logged as weighted findings, not silently passed and not
   silently ignored.
5. DOM/computed-style checks (`getBoundingClientRect`, `getComputedStyle`, `naturalWidth`) are
   for **diagnosing** what the eye caught, or for cross-checking a screenshot that looks
   suspicious — they never substitute for the visual comparison itself. **When a DOM check is
   used to confirm or refute a specific reported issue (e.g. "X isn't centered"), measure the
   exact element named, not its nearest wrapper** — a wrapper's own bounding box can be correctly
   centered while a specific child inside it (an `<img>` especially — see `HARD-RULES.md` H24)
   is not. A wrapper-level measurement that contradicts a user's direct visual report is a signal
   to measure one level deeper, not to conclude the report is wrong.
6. **An all-white, blank, or obviously-wrong screenshot is not evidence of anything** — the
   capture pipeline can desync from real page state (see `GOTCHAS.md`). Cross-check with
   `elementFromPoint`/`getBoundingClientRect`/`naturalWidth`; if a tab's screenshot capture is
   stuck for more than one retry, open a fresh tab rather than retrying in place, then re-capture
   and actually compare.
7. **When fixing a `responsive_touch_targets` finding, target comfortably above the 24px minimum,
   not exactly at it — then confirm with a live DOM measurement, not just the gate's reported
   pass/fail.** Confirmed real case (Sep 2026): an initial padding fix measured 23.5px live in
   the browser despite `qa_gate.py` reporting a pass — subpixel/line-height rounding between the
   gate's own arithmetic and actual browser layout don't always agree exactly at the boundary.
   Add a couple of px of margin above the threshold, and re-check the final size with
   `getBoundingClientRect()` at the target viewport rather than trusting the tool's boundary
   verdict alone.
8. **When fixing a `color_contrast_accessibility` finding, search the enclosing component/section
   for an existing local AA-safe override of the same base token before introducing an
   independent new value.** Confirmed real case (Sep 2026): a footer's "|" separators used the
   raw `--clay-color-grey-300` token (1.62:1 on white, failing AA) while the same footer already
   defined a local `--clay-color-grey-500` override for exactly this purpose elsewhere — the bug
   was inconsistent application of an already-correct fix, not a missing one. Reusing the
   existing override keeps the fix consistent across the component; picking an independent value
   risks a second inconsistency later.

**`web-design-rules.csv`** — 45 rules (`type: llm`, vision-evaluated unless `owner: script`),
each with `id`, `severity` (31 `hard` / 14 `soft`), `weight` (0.6–1.0), `owner`, `instruction`, and
worked `example_pass`/`example_fail`. Grouped: layout (4), spacing (8), responsive (8), typography
(3), text (2), color (3), imagery (4), design-system reuse (1), interaction (3), a11y (3), perf
(2), SEO (2).

Rules worth calling out because a prior build's QA pass never checked them at all, despite
declaring the build ~9.7/10: `nav_links_functional` (weight 1.0 — the highest in the set),
`a11y_disclosure_state` (accordions/tab bars need `aria-expanded`, updated on toggle),
`a11y_keyboard_navigation`, `a11y_semantic_structure`, `color_contrast_accessibility` (hard,
0.95), `responsive_touch_targets`, `interactive_states_present` (hover/focus states),
`responsive_intermediate_viewports` (don't test only two breakpoints — check widths between
them too), `layout_repeated_items_wrap`, and the perf/SEO rules. **All of these are `owner:
script`** — `tools/qa_gate.py` checks every one of them itself now, which is what makes "never
checked at all" structurally impossible going forward rather than a thing to remember. Run the
full 45 (script + vision together), not a subset that happens to be convenient.

**Clay-default visual inconsistencies** — when a Clay component is the anchor, its defaults
(divider lines, borders, fills, padding, box-shadows) are not automatically correct for the
Figma design. During vision QA, explicitly scan every Clay-anchored element for visual
properties that appear in the built output but have no equivalent in the Figma screenshot. The
canonical check: compare the full rendered element in the browser against the `get_screenshot`
reference. Any border, divider, background, or shadow present in HTML but absent from Figma is
a hard `inconsistency` — remove it. (Confirmed real case: Clay accordion adds `border-top`
between items; Figma design has none; user flagged it — see `PRE-BUILD-VERIFICATION.md` item 15
for the full rule and the fix pattern.) This check belongs in every section that uses any Clay
component, not only accordion/tab patterns.

Also directly relevant to this skill's own rules: `ds_component_reuse_check` (hard, 0.9,
`owner: pre-build`) is precisely what `CLAY-INTEGRATION.md` operationalizes — flag any element
built from scratch when a matching component/anchor was available and unused. `image_aspect_ratio`
restates H10, `image_alt_text` restates H11 — both `owner: script`.
`text_no_placeholder_content` (hard, 0.95, `owner: script`) — no lorem ipsum or bracketed
placeholders may reach the final build.

## 1b. `tools/qa_gate.py` — the numeric re-diff against the pre-build spec (per section, right after step 1)

Step 1 is a *look*, and looking is genuinely good at what looking is good at: wrong image, wrong
order, missing element, bad proportion, something that just reads wrong. It is measurably bad at
small quantitative deltas — a few px of font size, a couple dozen px of padding, one hex step of
fill, a paragraph that's one `<p>` instead of two, a container whose whole content scaled down
proportionally. Defects of that kind routinely survive a vision pass that was genuinely run and
correctly recorded as PASS, because **two renderings can look the same and differ in every number
that matters.** Looking is not the weak link; asking looking to do arithmetic is.

So re-measure the built page with the same tool that produced the spec, and diff — as one command,
not a checklist someone has to remember to paste:

```bash
# after Step 9 (page accumulation) and Step 10 (QA screenshot), serve over localhost, then:
python3 ~/.claude/skills/figma-to-web/tools/qa_gate.py section \
    --url http://localhost:<port>/<page-slug>-page-v01.html \
    --selector '[data-section="<slug>"]' \
    --spec /tmp/<slug>-spec.json
```

`--spec` is the consolidated JSON `section_spec.py spec` wrote from Step 2g's measurements (bg,
textnodes, textsize) before any CSS existed — this is what makes the comparison a diff against a
recorded number rather than another opinion formed after the fact. `qa_gate.py` diffs the built
render against it (section background color, and — when the request's `text_boxes`/`container`
entries carried a `selector` — border-box **content** width, never box width: under border-box
the padding lives inside `max-width`, so the box can be correct while the content is short by both
paddings; measuring the box width would confirm that bug as correct, which is why the check is a
subtraction, not a reading).

In the same pass, `qa_gate.py` also mechanizes every other check that used to be a loose JS
snippet someone had to remember: leaf-element centering (H24 — a wrapper being centered proves
nothing about a specific child inside it, an `<img>` especially), every `<img>` actually loaded
(`img.complete && naturalWidth > 0`, not just present in the DOM — a "the layout looks right"
screenshot can hide a broken image entirely, see `GOTCHAS.md`'s `file://` gotcha), a11y disclosure
state (every tab/accordion/disclosure control needs a live `aria-selected`/`aria-expanded`, not
just a visual active/open class), and overflow at **three** widths — desktop (1440px) and mobile
(390px) alone miss the CSV's `responsive_intermediate_viewports` rule; `qa_gate.py` always checks
a mid-range width (820px) too, per section and again across the whole page.

Run `qa_gate.py page --url ...` once, after every section in the manifest is built, for the checks
no single section owns (`nav_links_functional`, the container-width and CTA-consistency page-wide
checks — H21/H22 — the PAGE-STRUCTURE.md skeleton — H27 — and the a11y/perf/SEO groups): the container-width class of error is systematic
in cause but sporadic in occurrence, so it only reveals itself as a pattern when every section is
measured side by side (`PRE-BUILD-VERIFICATION.md` item 14).

This is not the DOM-check exception in step 1's item 5 — that rule is about not letting a
`getBoundingClientRect` *replace* looking. This step runs **in addition to** the look, and every
finding it prints is scoped to the exact `web-design-rules.csv` id or `HARD-RULES.md` H-number it
enforces, with an `expected`/`measured` pair — a defect with a number attached, no judgment call.
`qa_gate.py`'s own `vision_owned` output field lists every rule it does **not** check, read live
from the same `owner` columns — **exit 0 from this script is never "QA complete," only "the
mechanizable half is clean."** Log the result (`[QA] <slug>: qa_gate clean, N checks` or
`[BUG] <slug>: <rule-id> <measured> vs. <expected>`).

## 1c. Component-zoom pass — small elements are invisible at page zoom

**A full-page capture cannot verify anything smaller than roughly 32px.** A 4493px-tall page
rendered into a chat-sized image is a ~7x downscale: a 24px app-logo chip lands on ~3 pixels.

**The real miss this closes (AI Template Center):** every card shipped `✣`/`M`/`✓` text glyphs
where Figma had real Slack/Gmail/monday logos, and `★` where Figma had a real rating-star SVG.
That survived three mechanized rebuild rounds ending in a clean gate *and* a full-page vision
pass. The user caught it immediately by looking at one card. See `HARD-RULES.md` H30.

**So, after the section pass and before calling a section done, capture at component zoom:**

```python
page = browser.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=3)
page.locator('.some-card').first.screenshot(path='/tmp/card.png')   # element, not page
```

Element-scoped `.screenshot()` at `device_scale_factor` 2–3, then **actually look at it**. One
representative instance of each repeated component is enough — cards, chips, badges, avatars,
icon rows, rating widgets, arrows, form controls.

**What only this pass catches:** glyph/emoji stand-ins for real icons (H30), an asset that
decoded but is blank (H29 — three of four badges here were fully transparent and every numeric
check passed), a logo at the wrong crop, and 1–2px border/radius drift.

## 2. Full-page vision pass

In addition to per-section passes: once all sections are built, do a full-page vision pass at
both desktop (1440px) and mobile (390px) widths — this catches rhythm/spacing/regression issues
only visible in sequence (a later section that doesn't fit the established visual rhythm, a
duplicate pattern that should have varied, an overall page height gone wrong).

This pass is for **sequence and rhythm only** — never treat it as coverage of anything small
enough to need §1c.

## 3. Logging

Every skipped/accepted finding from any of the above (steps 1–2) gets logged to the session's
trace file, in the same tag convention used elsewhere in this skill (`[QA]`, `[BUG]`,
`[ACCEPTED-GAP]`) — this is what feeds the knowledge-capture step at the end of the build. An
accuracy check that finds nothing worth logging is itself worth a one-line confirmation that it
ran, so a later reviewer can tell "ran clean" from "never ran."

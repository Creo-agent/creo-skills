# QA Scorecard

## Contents
- Full-page Playwright pass
- Section-by-section comparison
- Scoring dimensions
- Report format

This is the mechanical/scripted half of QA. **The per-section vision QA in `ACCURACY-GATE.md`
is the primary check — this file's scripts produce the screenshots and structural checks that
feed that visual comparison; they do not replace looking at the images.**

## Full-page Playwright pass

Run after the HTML file is written.

```python
from playwright.sync_api import sync_playwright

# Never file:// — GOTCHAS.md's asset-loading gotcha (no real network layer for local
# relative-path assets, images silently fail to load). Serve over localhost instead:
# python3 -m http.server <port> --directory <output-dir>
OUTPUT_FILE = "http://localhost:<port>/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="<chrome-binary-path>")
    page = browser.new_page()
    page.goto(OUTPUT_FILE)
    page.wait_for_load_state("networkidle")

    page.set_viewport_size({"width": 1440, "height": 900})
    page.screenshot(path="<output-dir>/qa-desktop-v01.png", full_page=True)

    page.set_viewport_size({"width": 390, "height": 844})
    page.screenshot(path="<output-dir>/qa-mobile-v01.png", full_page=True)

    page.set_viewport_size({"width": 1440, "height": 900})
    overflow_desktop = page.evaluate(
        "document.documentElement.scrollWidth > document.documentElement.clientWidth")

    page.set_viewport_size({"width": 390, "height": 844})
    overflow_mobile = page.evaluate(
        "document.documentElement.scrollWidth > document.documentElement.clientWidth")

    broken_images = page.evaluate("""
        [...document.querySelectorAll('img')]
            .filter(img => !img.naturalWidth)
            .map(img => img.src)
    """)

    hardcoded_colors = page.evaluate("""
        [...document.styleSheets]
            .flatMap(s => { try { return [...s.cssRules]; } catch(e) { return []; } })
            .flatMap(r => r.cssText ? [r.cssText] : [])
            .filter(t => /#[0-9a-fA-F]{3,8}/.test(t) || /rgb\\(/.test(t))
            .length
    """)

    # Height-delta vs the Figma frame (info, not fail — see gate note below)
    page.set_viewport_size({"width": 1440, "height": 900})
    built_height = page.evaluate("document.body.scrollHeight")
    # figma_frame_height = the top-level frame's height from get_metadata
    # delta_pct = abs(built_height - figma_frame_height) / figma_frame_height * 100

    browser.close()
```

### Two mechanical gates from the pass above

- **Mobile horizontal-overflow gate (FAIL if true).** `overflow_mobile` must be `False`. A mobile
  build with `document.documentElement.scrollWidth > clientWidth` has a section that doesn't
  collapse — a hard fail, not a cosmetic note. (`overflow_desktop` should also be `False`.) Fix the
  offending section's responsive rule before shipping; don't paper over it with `overflow-x:hidden`
  on the body, which just clips the bug.
- **Height-delta check (INFO, with a band).** Compare the built page height to the Figma top-level
  frame height. Within **±10%** is normal — collapsed inter-section whitespace and font metrics
  account for it (confirmed: IT persona page built 10,673px vs a 11,540px frame, ~7.5% short,
  correct). **Outside ±10%**, stop and look: a large *shortfall* usually means a section silently
  collapsed to near-zero height (the classic invalid-`clamp()`→`padding:0` bug), and a large
  *overshoot* usually means a media slot rendered at the wrong scale. Log the number in the report
  either way; only investigate when it leaves the band.

## Section-by-section comparison

**Mandatory for any full-page build.** Runs after the full-page pass above, and feeds the
per-section vision QA in `ACCURACY-GATE.md`.

### Render each section

```python
import os
from playwright.sync_api import sync_playwright

OUTPUT_FILE = "http://localhost:<port>/index.html"  # never file:// — see the note above
SECTION_DIR = "<output-dir>/section-ref"
QA_STRIPS_DIR = "<output-dir>/section-qa"
os.makedirs(QA_STRIPS_DIR, exist_ok=True)

SECTION_MANIFEST = []  # from Step 3B — {"idx": N, "slug": "...", "ref": "section-NN-slug.png"}
section_renders = {}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="<chrome-binary-path>")
    page = browser.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(OUTPUT_FILE)
    page.wait_for_load_state("networkidle")

    for s in SECTION_MANIFEST:
        el = page.locator(f'[data-section="{s["slug"]}"]').first
        el.scroll_into_view_if_needed()
        box = el.bounding_box()
        if not box:
            print(f"[WARN] Section {s['slug']} not found in DOM — skipping")
            continue
        clip = {"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]}
        render_path = os.path.join(QA_STRIPS_DIR, f"render-{s['idx']:02d}-{s['slug']}.png")
        page.screenshot(path=render_path, clip=clip)
        section_renders[s["slug"]] = render_path

    browser.close()
```

### Build side-by-side strips

```python
from PIL import Image

STRIP_WIDTH, LABEL_H = 2800, 40
scores = []

for s in SECTION_MANIFEST:
    slug = s["slug"]
    ref_path = os.path.join(SECTION_DIR, s["ref"])
    render_path = section_renders.get(slug)
    if not render_path or not os.path.exists(render_path):
        scores.append({**s, "status": "MISSING_RENDER", "score": None}); continue
    if not os.path.exists(ref_path):
        scores.append({**s, "status": "MISSING_REF", "score": None}); continue

    ref_img = Image.open(ref_path).convert("RGB")
    render_img = Image.open(render_path).convert("RGB")
    panel_w = STRIP_WIDTH // 2
    ref_h = int(ref_img.height * panel_w / ref_img.width)
    render_h = int(render_img.height * panel_w / render_img.width)
    ref_img = ref_img.resize((panel_w, ref_h), Image.LANCZOS)
    render_img = render_img.resize((panel_w, render_h), Image.LANCZOS)

    strip_h = LABEL_H + max(ref_h, render_h)
    strip = Image.new("RGB", (STRIP_WIDTH, strip_h), (30, 30, 30))
    strip.paste(ref_img, (0, LABEL_H))
    strip.paste(render_img, (panel_w, LABEL_H))
    strip_path = os.path.join(QA_STRIPS_DIR, f"strip-{s['idx']:02d}-{slug}.png")
    strip.save(strip_path)
    scores.append({**s, "strip": strip_path, "status": "OK"})

all_strips = [Image.open(s["strip"]) for s in scores if s.get("strip")]
if all_strips:
    total_h = sum(img.height for img in all_strips)
    composite = Image.new("RGB", (STRIP_WIDTH, total_h), (20, 20, 20))
    y = 0
    for img in all_strips:
        composite.paste(img, (0, y)); y += img.height
    composite.save("<output-dir>/figma-to-web-qa-strips-v01.png")
```

## Scoring dimensions

**This scorecard has two layers. Only one of them determines pass/fail — the other is
informational. This is a locked decision (Open Question #7), not a matter of judgment per build.**

1. **`web-design-rules.csv`** (45 rules, `type: llm`, vision-evaluated) — **this is the pass/fail
   layer, and it is strict per-section, not an aggregate score.**
   > **A section is DONE if and only if zero `hard`-severity rules fail. It is NOT DONE if even
   > one `hard`-severity rule fails — full stop, no averaging, no exceptions, regardless of how
   > many other rules pass or how good the section looks otherwise.** A section with 44 of 45
   > rules passing and 1 failing `hard` rule is NOT DONE.
   `soft`-severity rule violations never block DONE status — they are logged as weighted
   findings for the report, not silently dropped and not treated as blocking.
   The only way past a failing `hard` rule is to fix it, or to log it as an **explicit accepted
   gap with a stated reason** (e.g. a Design-File Gap per `DESIGN-FILE-GAPS.md`) — an accepted
   gap is a deliberate, named exception, never a silent pass.
2. **The 4-dimension legacy rubric below** — **informational only, never a pass/fail
   determinant.** Its 1–10 score is a fast human-readable gut-check for the delivery report
   (comparable across sections at a glance) — it does not override, soften, or substitute for
   the `hard`-rule pass/fail above. A section can score 9/10 on this rubric and still be NOT
   DONE if it fails a single `hard` rule the legacy rubric's 4 dimensions don't happen to cover
   (accessibility and functional-link correctness, most commonly — see `ACCURACY-GATE.md`'s
   list of categories the legacy rubric structurally cannot see).

| Dimension | What to check | Severity if wrong |
|---|---|---|
| **Layout** | Column count, stacking order, alignment, centering | CRITICAL if structure differs, MAJOR if off-axis |
| **Assets** | All images/logos/icons present, correct sizes, no broken img | MAJOR if missing, MINOR if wrong size |
| **Copy** | All text present, headings/body match Figma | CRITICAL if text missing, MAJOR if wrong hierarchy |
| **Color & Type** | Background color, text colors, font weights | MAJOR if visibly wrong, MINOR if subtle |

Score: 10 = pixel-faithful · 8–9 = minor delta · 6–7 = noticeable but functional · 4–5 =
structural issues · 1–3 = section wrong.

## Report format

Write to `<output-dir>/figma-to-web-qa-report-v01.md`:

```markdown
# figma-to-web QA Report — <frame-name>
**Version:** v<NN>  **Date:** YYYY-MM-DD  **Source:** <figma-url>

## Overall
| Metric | Result |
|---|---|
| Sections scored | N |
| Average score (legacy rubric) | X.X / 10 |
| web-design-rules.csv hard-rule failures | N (must be 0 to ship) |
| web-design-rules.csv soft-rule findings | N (logged, weighted) |
| Overflow (desktop 1440px) | PASS / FAIL |
| Overflow (mobile 390px) | PASS / FAIL |
| Broken images | N |

## Visual Diff Tool — Automated Pixel Comparison

After the per-section Playwright screenshot, run `visual_diff.py` + `diff_enrich.py` for an
objective pixel-level comparison. This is additive to the vision QA, not a replacement.

### Setup
```bash
T=~/.claude/skills/figma-to-web/tools

# 1. Export Figma section screenshot at 2x
#    (already done in Step 2b — use the saved reference PNG)

# 2. Take HTML screenshot at 2x (MUST match Figma's 2x export)
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 2000}, device_scale_factor=2)
    page.goto('http://localhost:<port>/index.html')
    page.wait_for_load_state('networkidle')
    section = page.query_selector('[data-section=\"<slug>\"]')
    section.screenshot(path='/tmp/<slug>-html-2x.png')
    browser.close()
"

# 3. Run visual diff
python3 $T/visual_diff.py \
  --figma /tmp/<slug>-figma-ref.png \
  --html /tmp/<slug>-html-2x.png \
  --output /tmp/<slug>-diff/ \
  --section-name <slug> \
  --threshold 5.0

# 4. Run enrichment (adds Figma-vs-HTML CSS comparison)
python3 $T/diff_enrich.py \
  --report /tmp/<slug>-diff/<slug>-diff-report.json \
  --url http://localhost:<port>/index.html \
  --selector '[data-section="<slug>"]' \
  --figma-file <fileKey> \
  --figma-node <nodeId>
```

### Hard Rules for Visual Diff
- **Always screenshot HTML at 2x** (`device_scale_factor=2`) to match Figma's 2x export.
  1x vs 2x comparison produces massive false positives from upscaling.
- **Filter the full-image region** — Region 1 is often the entire image due to anti-aliasing
  noise + tiny size mismatches. Weight findings by pixel density, not raw area.
- **SSIM is misleading for image-heavy sections** — Figma-exported composites re-rendered in
  a browser always differ slightly. Separate image regions from layout/text regions in scoring.
- **Normalize backgrounds** — If Figma section has transparent bg, the export shows canvas
  color. The tool should compare content regions, not background.

### Fix Loop
1. Read the enriched diff report (`*-diff-report.enriched.json`)
2. For each flagged region: inspect the DOM element's CSS, compare against the Figma expected value
3. Fix the CSS
4. Re-screenshot → re-diff → confirm score improvement
5. Repeat until pixel diff < threshold (5%) or only image-rendering differences remain

## Per-Section Scores
| # | Section | Score | Layout | Assets | Copy | Color/Type | Hard-rule failures | Issues |
|---|---|---|---|---|---|---|---|---|
| 01 | hero | 9/10 | MATCH | MATCH | MATCH | CLOSE | 0 | Minor heading padding |

## Critical Issues  ## Major Issues  ## Minor / Info  ## Accepted Gaps (with reason)
```

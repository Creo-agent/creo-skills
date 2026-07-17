# Resize QA — Full Workflow

## Step 1 — Capture Both Images

Before scoring anything, get both baselines. Run these in parallel:

```
A. get_screenshot(fileKey, originalMasterNodeId)   → master_screenshot
B. get_screenshot(fileKey, outputFrameNodeId)       → output_screenshot
```

Fetch both to local paths using `curl`:

```bash
curl -sL -o "<deliverables_folder>/<format>-master-ref-v01.png" "<master_screenshot_url>"
curl -sL -o "<deliverables_folder>/<format>-output-v<NN>.png" "<output_screenshot_url>"
```

Copy both to `.slack-outputs/` so they appear in the Slack thread as visible images:

```bash
cp "<deliverables_folder>/<format>-master-ref-v01.png" ".slack-outputs/<format>-master-ref-v01.png"
cp "<deliverables_folder>/<format>-output-v<NN>.png" ".slack-outputs/<format>-output-v<NN>.png"
```

> If the original nodeId was not captured at the start of the session, ask the user for the master frame URL before proceeding. Never skip the master capture — the side-by-side comparison is mandatory.

---

## Step 2 — Technical & Metadata Verification

Use `get_design_context` on the output frame to get exact layer data. Check:

| Check | Rule | Pass / Fail |
|-------|------|-------------|
| Dimensions | Output measures exactly `{W}×{H}` px (no rounding) | |
| Font family | Only Poppins used on all text layers | |

Mark each as ✅ Pass or ❌ Fail before proceeding. A dimension mismatch is an immediate **Fatal Defect (−100 pts)**.

---

## Step 3 — Critical Integrity Checks (Binary Pass/Fail)

Scan layer data and visual. Any Fail here = **instant reject**.

| Element | Rule |
|---------|------|
| No Distortion | All elements maintain original aspect ratios — no stretching, squeezing, or skewing |
| No Invention | Zero new decorative elements (background patterns, extra icons, emojis, unauthorized lines) |
| Text Content | Character-for-character match with master (spelling, capitalization, punctuation) |
| Logo Count | Same number of logos as the master (usually 1:1) |

---

## Step 4 — Element & Layout Placement

Check against the layout rules:

**Logo:**
- [ ] Oriented horizontally (not rotated or vertically aligned)
- [ ] Placed in an approved zone: TOP, BOTTOM, TOP-LEFT, TOP-RIGHT, BOTTOM-LEFT, BOTTOM-RIGHT
- [ ] Not flush against or centered on the absolute vertical left or right edges

**CTA Button:**
- [ ] Placed in a valid zone: BOTTOM, BOTTOM-RIGHT, BOTTOM-LEFT, CENTER-BOTTOM
- [ ] Solid fill (not transparent, ghost, or outlined)
- [ ] Color: if master had a button → exact color match. If not → solid Black on light bg, solid White on dark bg.
- [ ] Text contrast passes readability check

**Visuals & Containers:**
- [ ] Images preserve original framing (rounded corners → rounded corners; contained boxes → not full-bleed)
- [ ] Primary visuals anchored left or right, not floating in the center

---

## Step 5 — Safe Zone & Spacing Measurements

Use layer position data from `get_design_context`.

**Safe zone padding:**
- Formats ≤600px: minimum 10–15px from all canvas edges
- Formats >600px: minimum 20–30px from all canvas edges
- Story (1080×1920): top 269px clear, bottom 403px clear, left/right 65px clear (Meta official)

**Minimum element spacing (reading flow: Logo → Headline → Subheadline → Visual → CTA):**
- Logo → Headline: min 30–40px
- Headline → Subheadline: min 20–30px
- Subheadline → Visual: min 25–35px
- Visual → CTA: min 30px

---

## Part 2 — Defect Scoring

Start at 100. Deduct per defect found. **Final Score = 100 − (Total Defect Points)**

### Fatal Defects (−100 pts each = Instant Reject)
- Incorrect output dimensions
- Visual distortion (stretched logo, warped text, skewed images)
- Text wording changed (typo, omission, unauthorized paraphrase)
- Wrong font family (anything other than Poppins)
- Added elements / decorations not in the master

### Major Defects (−30 pts each)
- Logo or CTA on vertical side margins/edges
- Visual container styling lost (e.g. rounded corners made square)
- Elements bleeding into safe-zone boundaries (touching canvas edge)
- Ghost/transparent button when solid is required
- Incorrect CTA color (fails contrast rule)

### Minor Defects (−10 pts each)
- Spacing between elements slightly below minimum threshold
- Composition feels crowded or has awkward empty gaps (see note below)
- Brand name (e.g. "monday.com") broken into two lines

> **Note — inherent empty lower third in Story format:** When resizing a 1:1 master to 1080×1920 (Story), ~400–450px of empty space below the visual is structural, not a placement error — there is no source material to fill it. Score this as a single Minor −10 (composition gap) only once, and flag it as "requires creative direction" rather than a fixable layout defect. Do not score it as Major or Fatal.

### Score → Verdict

| Final Score | Verdict | Action |
|-------------|---------|--------|
| 100 pts | Perfect Pass | Ship immediately |
| 80–99 pts | Conditional Pass | Fix spacing/padding only — no full redesign |
| ≤79 pts | Fail / Reject | Full correction required |

---

## Part 3 — Vision Inspection (5 Pillars)

Do this visually from the two screenshots captured in Step 1. Examine each pillar:

### 1. Spacing & Structure
- Does the composition feel intentional or randomly scattered?
- No "floating" elements with disconnected margins
- Reading order flows: Headline → Visual → CTA → Logo
- Left/right margins balanced and consistent

### 2. Color Fidelity & Contrast
- Background extension matches master color (no color-shifting, unexpected gradients)
- CTA button and typography contrast against background — absolute readability

### 3. Typography & Hierarchy
- Poppins is the only font visible
- Headline visually larger and more dominant than subheadline
- Brand names (e.g. "monday.com") on a single, unbroken line

### 4. Crop Prevention
- No text characters, descenders (g, j, p, q, y), or punctuation clipped by bounding boxes or canvas edges
- Main visual subject fully visible (not awkwardly cut off unless intentionally cropped that way in master)

### 5. Spacing Structure (No Crowding)
- Copy blocks never overlap or collide with visual elements
- CTA button has at least 30px clear space around it
- Safe-zone boundaries completely clear of design elements

---

## Output — VISION QA REPORT

After every review, post this structured report to Slack. Always include both image names so the thread has the side-by-side reference.

```
VISION QA REPORT: [{W}×{H} — {Format Name}]

VISUAL BASELINE COMPARISON
Original master: <format>-master-ref-v01.png (in thread above)
Current output: <format>-output-v<NN>.png (in thread above)

Technical Checks:
• Dimensions: ✅ / ❌ {W}×{H}
• Font: ✅ / ❌ Poppins only

Score: {N}/100 — {VERDICT}

✅ WHAT IS GOOD
• [What was successfully preserved or fixed in this iteration]

❌ WHAT WENT WRONG
Pillar | Issue | Visual Impact
Spacing & Structure | [issue] | [impact]
Colors | [issue] | [impact]
Typography | [issue] | [impact]
Cropping | [issue] | [impact]
Spacing Structure | [issue] | [impact]

🔧 ACTIONABLE FIXES FOR NEXT ITERATION
Fix 1: [exact instruction with pixel values]
Fix 2: [exact instruction with pixel values]
Fix 3: [exact instruction with pixel values]
```

If the score is 100 and there are no defects in the visual inspection, the "What Went Wrong" and "Actionable Fixes" sections can be omitted. Still post the report.

---

## Save the Report

Write the full report to `<deliverables_folder>/<format>-qa-report-v<NN>.md`. Append to the same file on subsequent rounds — don't create a new file per fix pass. Increment the version (`v01`, `v02`, etc.) only when starting a completely new QA session for the same format.

---

## Important Rules

1. **Never skip the master screenshot** — the side-by-side comparison is the foundation of every QA.
2. **Never estimate dimensions** — always verify from `get_design_context` layer data.
3. **Score honestly** — don't omit defects because the score will look bad. The rubric exists to catch problems early.
4. **One report per format** — if multiple formats were resized in one session, generate one report per format.
5. **If score is ≤79:** list the fixes clearly and ask the user whether to apply them. Do not auto-apply without surfacing the QA report first.

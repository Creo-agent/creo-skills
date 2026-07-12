# Resize with Nano Banana — Execution Prompt

The full workflow for the `resize-with-nano-banana` skill. Load `SKILL.md` first, then follow this file. YOU (the model running this skill) drive the whole flow: collect the inputs and assets from the user, analyze the master design with your own vision, build the prompts, and generate each resized creative via Google Gemini's image model — applying the exact Nano Banana prompt system in the reference appendix below.

## Runnable Workflow Overview

Run these steps **in order**. Do not skip the intake questions or the analysis step.

1. **Check / obtain the Gemini API key** (Step 1)
2. **Ask the user for all inputs and assets** (Step 2)
3. **Analyze the master design — MANDATORY, using your own vision** (Step 3)
4. **Confirm the per-size configuration** (Step 4)
5. **Build the prompts and generate each size** (Step 5)
6. **Deliver the results** (Step 6)

A helper script lives at [`scripts/nano_banana.py`](scripts/nano_banana.py) and mirrors the plugin's exact Gemini calls (two-call pattern, `imageConfig`, aspect-ratio handling, retries).

---

## Step 1 — Gemini API Key (required)

Image generation uses Google Gemini, which needs an API key. Resolve it in this order:

1. **Check the environment** for `GEMINI_API_KEY` or `GOOGLE_API_KEY`:
   ```bash
   printenv GEMINI_API_KEY GOOGLE_API_KEY 2>/dev/null
   ```
2. **Check for a `.env` file** in the working directory (and parent) and look for the key:
   ```bash
   grep -sE '^(GEMINI_API_KEY|GOOGLE_API_KEY)=' .env ../.env 2>/dev/null
   ```
3. **If not found, ask the user** with `AskUserQuestion` — request they paste the key or tell you where it lives. Offer to save it to a local `.env` (gitignored) for reuse. Never echo the full key back or commit it.

Export it into the environment before running the script (e.g. `export GEMINI_API_KEY=...`), or pass `--api-key` to the script. The key is used ONLY for the Gemini image generation (and, if you have no vision, the fallback analysis).

---

## Step 2 — Gather Inputs & Assets (ask the user)

Before generating, collect everything below. Use `AskUserQuestion` for multiple-choice items (sizes, resolution, per-size elements); ask directly for file paths / free text. Do not assume — confirm each item.

### Intake checklist

| # | Item | Notes |
|---|------|-------|
| 1 | **Master design** (required) | Path to the master image file (PNG/JPG). If the user only has it in Figma, ask them to export the frame as PNG and give you the path. |
| 2 | **Logo asset** (optional) | Path to a logo PNG to use as a clean reference (INPUT B). If none, skip — the logo from the master is used. |
| 3 | **Target sizes** (required) | Which of the 8 predefined sizes (below), and/or custom W×H (max 2400px). |
| 4 | **Elements per size** (required) | Which of Headline / Visual / Logo / Button to INCLUDE for each size. Anything not included becomes an explicit EXCLUDE. |
| 5 | **Button text** (if Button enabled) | CTA copy. Default `Get Started`. |
| 6 | **Button color** (if Button enabled) | `white`, `black`, or a `#RRGGBB` hex. Default `white`. Master button colors always win if the master already has a button. |
| 7 | **Resolution** (required) | `1K` (fast), `2K` (balanced), or `4K` (best/slowest). Default `2K`. |
| 8 | **Output folder** | Where to write the generated PNGs. Default: an `output/` folder next to the master. |

### Predefined sizes

| Group | Name | Dimensions | Suggested default elements |
|-------|------|------------|----------------------------|
| DV | Billboard | 970×250 | Headline, Visual, Logo, Button |
| DV | Leaderboard | 728×90 | Headline, Visual, Logo, Button |
| DV | Medium Rectangle | 300×250 | Headline, Visual, Logo, Button |
| DV | Half Page | 300×600 | Logo, Headline, Visual, Button |
| DV | Skyscraper | 160×600 | Logo, Headline, Visual, Button |
| META | Story | 1080×1920 | Logo, Headline, Visual |
| META | Facebook Feed | 1080×1350 | Logo, Headline, Visual |
| LI | LinkedIn Feed | 1200×1200 | Logo, Headline, Visual |

Suggest these defaults but let the user override per size. If the user says "all sizes with defaults," you may proceed without asking element-by-element.

---

## Step 3 — Analyze the Master Design (MANDATORY — use YOUR OWN vision)

This step is **required** (not optional) and produces the `MASTER CONTEXT` brief prepended to every size's user prompt.

**Do the analysis yourself with your own vision** — do NOT use Gemini for this if you can see images:

1. `Read` the master image file directly (Claude can view images).
2. Produce a concise brief (≤200 words) following exactly this structure:
   ```
   VISUAL: images/photos/illustrations, position, container style (rounded, bordered)
   GRAPHIC: background type, decorative elements, overall style
   TEXT: exact headline, subheadline, CTA text (verbatim)
   LOGO: description, position, count
   COLORS: background, text, accent, CTA colors (be specific — hex if possible)
   COMPOSITION: layout structure, visual hierarchy, spacing
   STYLE: mood, design trend
   ```
3. Show the brief to the user and let them correct it before generating.

**Fallback (only if the running model has NO vision):** delegate to Gemini `gemini-2.0-flash`:
```bash
python3 scripts/nano_banana.py analyze --master /path/to/master.png
```
Use the printed brief as `MASTER CONTEXT`. Only fall back when you genuinely cannot process the image.

The accuracy of TEXT and COLORS here matters most — the generator relies on this brief to keep copy verbatim and colors faithful.

---

## Step 4 — Confirm Per-Size Configuration

Summarize back to the user, as a table, what you're about to generate: each size, its included/excluded elements, button text/color, and resolution. Get a quick confirmation (or use `AskUserQuestion`) before spending API calls.

---

## Step 5 — Build Prompts & Generate

For **each** confirmed size:

1. **Render the system prompt** — start from the exact **System Prompt** (appendix below). Substitute `{W}`/`{H}` with the size. Write to a temp file, e.g. `/tmp/nb_system_<W>x<H>.txt`.
2. **Render the user prompt** — start from the **User Prompt Template** (appendix). Fill placeholders using the **Dynamic Prompt Building** rules:
   - `{ELEMENTS_LIST}` from the included elements (use the exact tokens; use the logo-reference token if a logo asset was provided)
   - `{BUTTON_COLOR_INFO}` only if Button is included and a color is set
   - `{EXCLUDED_ELEMENTS}` verbose block for every non-included element
   - `{SIZE_SPECIFIC_INSTRUCTIONS}` = the matching per-size block (appendix), or empty for non-standard sizes
   - `{Placement Name}`, `{ButtonText}`, `{W}`, `{H}` substituted
   - Prepend the `MASTER CONTEXT:` brief from Step 3
   - Write to `/tmp/nb_user_<W>x<H>.txt`.
3. **Generate** with the helper script:
   ```bash
   python3 scripts/nano_banana.py generate \
     --master /path/to/master.png \
     --logo /path/to/logo.png \            # omit if no logo asset
     --system-prompt /tmp/nb_system_970x250.txt \
     --user-prompt /tmp/nb_user_970x250.txt \
     --width 970 --height 250 \
     --resolution 2K \
     --out output/970x250_DV.png
   ```
   The script runs the two-call pattern, adds `aspectRatio` for extreme ratios (e.g. 728×90), retries on 503/timeout, and writes the PNG.
4. Process sizes sequentially; report progress after each (`✓ 970×250 done`).

---

## Step 6 — Deliver

- List every generated file with its size, e.g. `output/970x250_DV.png`.
- Offer to open the output folder or `Read` a generated image back to visually spot-check it against the master and the rules (dimensions, verbatim text, logo integrity, safe zones).
- If a result violates a hard constraint (wrong text, distorted logo, wrong dimensions), regenerate that single size.

---

# Reference Appendix — Exact Prompts & Rules

Everything below is the verbatim Nano Banana prompt system (extracted from the plugin's `ui.html`). Use it to render the system/user prompts in Step 5. The [`scripts/nano_banana.py`](scripts/nano_banana.py) helper implements the API mechanics (two-call pattern, `imageConfig`, aspect ratio, retries).

## System Prompt (Exact)

```
ROLE
You are an expert Digital Advertising Designer specializing in Adaptive Creative Resizing. Transform a Master Key Visual into new aspect ratios while preserving brand identity and visual hierarchy.

=====================================
ABSOLUTE CONSTRAINTS
=====================================

These 5 rules override ALL other instructions:

1. OUTPUT DIMENSIONS - Generate EXACTLY the specified {W}x{H} pixels. No approximation.
2. NO DISTORTION - Never rotate, stretch, skew, warp, or change aspect ratio of any element.
3. NO INVENTION - Never add elements, objects, or text not in the master image.
4. FONT LOCKED - ALL text must use Poppins font family ONLY. No substitutions. No approximations.
5. MASTER = TRUTH - The master image is the sole source for colors, style, textures, and mood.

=====================================
ELEMENT RULES
=====================================

LOGO
  MUST:
  - Use only the provided logo asset OR logo from master image
  - Preserve exact count (1 logo in master = 1 in output)
  - Maintain original orientation and proportions

  PLACEMENT (CRITICAL):
  - Valid positions: TOP, BOTTOM, TOP-LEFT, TOP-RIGHT, BOTTOM-LEFT, BOTTOM-RIGHT
  - NEVER place on LEFT or RIGHT vertical side edges
  - NEVER orient vertically along side margins
  - Logo must always be horizontally oriented

  MUST NOT:
  - Invent, hallucinate, or modify the logo
  - Duplicate logos to fill space
  - Rotate or distort
  - Place on vertical left/right edges

TEXT
  CONTENT PRESERVATION (ABSOLUTE):
  - Text content is SACRED — every word is legally binding copy
  - Extract and preserve EXACT wording from master with ZERO modifications

  ALLOWED (Layout Only):
  - Line breaks can change
  - Text positioning can change
  - Text size can scale proportionally

  FORBIDDEN (Content):
  - Do NOT change any words
  - Do NOT remove or add words
  - Do NOT paraphrase, abbreviate, or shorten
  - If text cannot fit, SCALE IT DOWN — never modify words

  MUST:
  - Use Poppins font family exclusively
  - Preserve exact font weights, casing, and styling from master
  - Keep brand names (e.g., "monday.com") on one line
  - Preserve exact text colors from master

  MUST NOT:
  - Add bold, color, highlights, or accent colors not in master
  - Repeat text to fill space
  - Apply perspective, 3D effects, curves, or any transformation

VISUALS/IMAGES
  MUST:
  - Preserve ALL container styling from master:
    • Rounded corner containers → keep rounded corners
    • Circular image masks → keep circular masks
    • Bordered image frames → keep border treatment
    • Images in boxes/cards → preserve box/card style
  - Anchor images to one side (left OR right), not centered floating

  MUST NOT:
  - Add new objects, characters, icons, or decorative elements
  - Invent new parts of illustrations to fill space
  - Duplicate visual elements to extend composition
  - Remove rounded corners or container styling from master
  - Make photos bleed to edges if master has them in contained boxes

CTA BUTTON
  STYLING PRIORITY (Follow in Order):
  1. If Master Image has a button → use its EXACT colors (fill + text)
  2. If Master has NO button → analyze background brightness:
     - Light/bright backgrounds → Black button (#000000) + White text (#FFFFFF)
     - Dark backgrounds → White button (#FFFFFF) + Black text (#000000)
  3. User-specified color is fallback only if no master button and contrast is good

  PLACEMENT (CRITICAL):
  - Valid positions: BOTTOM, BOTTOM-RIGHT, BOTTOM-LEFT, CENTER-BOTTOM
  - NEVER place on LEFT or RIGHT vertical side edges
  - NEVER orient vertically
  - Button must always be horizontally oriented and readable

  MUST NOT:
  - Use outlined, ghost, or transparent styles

=====================================
LAYOUT RULES
=====================================

SAFE ZONES
- Standard formats: 10-15px padding from all edges
- Larger formats (>600px): 20-30px padding
- No text or logo may touch edges

ELEMENT SPACING (Minimums)
- Logo to headline: 30-40px
- Headline to subheadline: 20-30px
- Text to visuals: 25-35px
- Any element to CTA: 30px

TEXT SCALING BY FORMAT
- Short/wide banners (height ≤250px): Compact text, max 50% of canvas height
- Tall/narrow banners (width ≤300px): Text can wrap, stay readable
- Text size proportional to canvas — never oversized

COMPOSITION
- Fill canvas intentionally, avoid large empty gaps
- Scale visuals larger to occupy significant area
- Each element needs its own zone — don't crowd
- Maintain visual flow: headline → visual → CTA → logo

=====================================
INPUT HANDLING
=====================================

INPUT A (Master Image)
- Source of truth for: background, colors, textures, style, text treatment
- Never override or replace this aesthetic

COLOR FIDELITY:
- Preserve EXACT colors from master — do NOT shift hues
- When extending backgrounds, use ONLY colors that exist in master
- Do NOT introduce gradients, shadows, or effects unless master uses them

INPUT B (Logo Asset)
- Element only — ignore its background
- Place atop master image's visual world
- Ensure contrast but do not restyle

=====================================
SIZE-SPECIFIC RULES
=====================================

Size-specific rules in the user prompt override LAYOUT RULES but never override ABSOLUTE CONSTRAINTS or ELEMENT RULES.

=====================================
PRE-OUTPUT VALIDATION
=====================================

Before generating, verify:
[ ] Dimensions exactly match {W}x{H}
[ ] No elements rotated or distorted
[ ] Logo count matches master
[ ] ALL text uses Poppins font family (no other fonts)
[ ] ALL text matches master exactly (word-for-word, no changes)
[ ] Logo and button NOT on vertical side edges (left/right)
[ ] Safe zones maintained
[ ] Background style matches master
[ ] Excluded elements completely absent
[ ] No invented elements added
```

---

## User Prompt Template (Exact — as coded in plugin)

```
OUTPUT: {W}x{H}px EXACT
Placement: {Placement Name}

---

INCLUDE:
{ELEMENTS_LIST}

{BUTTON_COLOR_INFO}

---

EXCLUDE:
{EXCLUDED_ELEMENTS}

---

SOURCE RULES:
- Master image (INPUT A) = background, colors, textures, style
- Logo file (INPUT B) = element only, ignore its background

---

LAYOUT:
- Extend master background to fill {W}x{H} canvas
- Recompose for new aspect ratio while maintaining balance
- Preserve visual hierarchy and breathing room
- Keep all elements min 15px from edges

---

TYPOGRAPHY:
- Font: Poppins ONLY (no substitutions allowed)
- Preserve exact font weights and casing from master

---

TEXT CONTENT:
- Preserve EXACT wording from master - do not change, remove, or add words
- Line breaks may change, but words must remain identical
- If text doesn't fit, scale it down - never modify words

---

SIZE-SPECIFIC:
{SIZE_SPECIFIC_INSTRUCTIONS}

---

VALIDATE: Output must be exactly {W}x{H}px
```

---

## Dynamic Prompt Building (how variables are filled — `generateUserPromptForSize`)

The plugin fills the template's placeholders at generation time based on per-size element toggles and settings.

### `{ELEMENTS_LIST}` — from enabled elements
Each enabled element becomes a token (joined by blank lines). If none enabled → `None specified`.

| Enabled element | Token inserted |
|-----------------|----------------|
| Headline | `{Headline}` |
| Visual | `{Visual}` |
| Button (Call-to-Action) | `{Capsule Button: {ButtonText}}` |
| Logo (no logo image provided) | `{Logo}` |
| Logo (logo image provided) | `{Logo = Use the logo reference image to make sure that the logo not getting distorted or changed. The style and design should be according to the master design only}` |

### `{ButtonText}` substitution (`replaceVariables`)
- If button text set → replaces `{ButtonText}` with the value
- If empty → `{Capsule Button: {ButtonText}}` becomes `Capsule Button`, and bare `{ButtonText}` is removed

### `{BUTTON_COLOR_INFO}` — only added when a Button is enabled AND a color is set
Color is normalized (`white`, `black`, `#RRGGBB`, or `RRGGBB` → `#RRGGBB`). Inserted block:

```
**BUTTON COLOR REQUIREMENT:**

PRIORITY ORDER:
1. If the Master Image contains a button, use its EXACT colors (this overrides settings below)
2. If no button in master, analyze background brightness and apply smart contrast:
   - Light backgrounds → Black button with white text
   - Dark backgrounds → White button with black text
3. User-specified fallback color: <colorDescription> (<exactColorSpec>)

Ensure high contrast for readability. Button must be solid fill only.
```

### `{EXCLUDED_ELEMENTS}` — from disabled elements
Any element type NOT enabled is added to an exclusion block. Each excluded element gets verbose "DO NOT include…" text, e.g.:

- **Visual** → "DO NOT include any visual elements, visual graphics, background visuals, or visual imagery…"
- **Headline** → "DO NOT include any headline text, headline copy, headline typography…"
- **Button (Call-to-Action)** → "DO NOT include any button, CTA button, call-to-action button…"
- **Logo** → "DO NOT include any logo, brand mark, logo graphic, or logo element…"

Wrapped with: `IMPORTANT - Elements to EXCLUDE (DO NOT include these in the generated visual): … These elements must be completely absent from the final design.`

### `MASTER CONTEXT:` prepend (only if "Analyze Master" was run)
When a brief exists, it's prepended above the whole user prompt:
```
MASTER CONTEXT:
<extracted brief>

---

<user prompt>
```

### Master analysis prompt (`EXTRACTION_PROMPT`, sent to `gemini-2.0-flash`)
```
Analyze this ad design. Be concise (200 words max).

VISUAL: What images/photos/illustrations? Position? Container style (rounded, bordered)?
GRAPHIC: Background type? Decorative elements? Overall style?
TEXT: Exact headline, subheadline, CTA text.
LOGO: Description, position, count.
COLORS: Background, text, accent, CTA colors.
COMPOSITION: Layout structure, visual hierarchy, spacing.
STYLE: Mood, design trend.

Output a brief that helps recreate this design at different sizes.
```

---

## Size-Specific Instructions (Exact — as coded in `getSizeSpecificInstructions()`)

These are injected verbatim into `{SIZE_SPECIFIC_INSTRUCTIONS}` in the user prompt.

### 728×90 — Leaderboard (DV)

```
LEADERBOARD (728x90)

ABOUT:
- Description: Very wide, thin horizontal strip - 8:1 aspect ratio
- Platform: Google Display Network, programmatic display ads
- Purpose: Top/bottom of webpage placement, brand awareness with minimal page disruption

LAYOUT:
- Logo: RIGHT, stacked vertically above CTA
- Text: LEFT-CENTER zone, 16-24px max
- Visual: LEFT side (preserve container styling if present)
- CTA: RIGHT, below logo in vertical stack

CONSTRAINTS:
- CRITICAL: Only 90px height - all elements must be compact
- Text must not exceed 60% of banner height (54px max)
- Single-line headline strongly preferred
- Min 25px margin from left edge for text
- Min 20px spacing between text block and logo/CTA group
- Horizontal reading flow: Visual → Text → Logo/CTA
```

### 970×250 — Billboard (DV)

```
BILLBOARD (970x250)

ABOUT:
- Description: Wide horizontal banner - 4:1 aspect ratio, larger than leaderboard
- Platform: Google Display Network, premium publisher sites
- Purpose: High-impact display placement, more room for messaging than leaderboard

LAYOUT:
- Logo: RIGHT, stacked vertically above CTA
- Text: CENTER-RIGHT zone, 28-40px max
- Visual: LEFT side (preserve container styling if present)
- CTA: RIGHT, below logo in vertical stack

CONSTRAINTS:
- Moderate height (250px) - text should be compact but readable
- Text must not exceed 50% of banner height (125px max)
- Min 30px margin from left edge for text
- Min 30px spacing between headline and logo/CTA group
- Visual should occupy 30-40% of width on left side
- Horizontal reading flow: Visual → Text → Logo/CTA
```

### 1080×1920 — Story (META)

```
STORY (1080x1920)

ABOUT:
- Description: Full-screen vertical format - 9:16 aspect ratio (phone screen)
- Platform: Instagram Stories, Facebook Stories, TikTok, Snapchat
- Purpose: Immersive mobile-first content, full attention capture

LAYOUT:
- Logo: TOP of canvas (within top safe zone)
- Text: Below logo, larger text size acceptable for mobile viewing
- Visual: CENTER of canvas, 40-50% of usable height
- CTA: Above bottom safe zone (not in bottom 250px)

CONSTRAINTS:
- CRITICAL: Bottom 250px must be COMPLETELY CLEAR (platform UI overlay)
- Usable content area: top 1670px only
- Vertical flow mandatory: Logo → Headline → Visual → CTA
- Min 40px spacing between logo and headline
- Min 50px from top edge for logo (status bar safe zone)
- Preserve image container styling - no edge-to-edge if master has styled boxes
- Text can be larger (36-48px) for mobile readability
```

### 300×250 — Medium Rectangle (DV)

```
MEDIUM RECTANGLE (300x250)

ABOUT:
- Description: Compact rectangular format - 6:5 aspect ratio, most common display size
- Platform: Google Display Network, in-article placements, sidebar ads
- Purpose: Versatile placement, works in content and sidebar, high fill rate

LAYOUT:
- Logo: FOOTER area, side-by-side with CTA (left or right)
- Text: UPPER section of canvas, 18-28px max
- Visual: UPPER section, above footer area
- CTA: FOOTER area, side-by-side with logo

CONSTRAINTS:
- Footer area: 50-60px height with dark/contrasting background
- Small format - use compact, efficient text
- Min 15px margin from all edges (safe zone)
- Min 15px spacing between headline and visual
- Logo and CTA must fit side-by-side in footer without crowding
- Visual should fill most of upper 190-200px area
```

### 160×600 — Skyscraper (DV)

```
SKYSCRAPER (160x600)

ABOUT:
- Description: Tall, narrow vertical strip - 1:3.75 aspect ratio
- Platform: Google Display Network, sidebar placements
- Purpose: Persistent visibility while scrolling, sidebar branding

LAYOUT:
- Logo: TOP of canvas (with safe zone padding)
- Text: Below logo, text WILL wrap due to narrow width (160px)
- Visual: MID or LOWER section, 40-50% of canvas height
- CTA: Near BOTTOM (above bottom safe zone)

CONSTRAINTS:
- Very narrow (160px) - text must wrap to multiple lines
- Use full vertical height - distribute elements evenly
- Don't cluster all elements at top or bottom
- Min 30px spacing between logo and headline
- Min 15px margins from left/right edges
- Visual should be sized to fill width (with container styling if applicable)
- Avoid large empty vertical gaps - scale elements to fill space
```

### 300×600 — Half Page (DV)

```
HALF PAGE (300x600)

ABOUT:
- Description: Large vertical rectangle - 1:2 aspect ratio, double the medium rectangle
- Platform: Google Display Network, premium sidebar placements
- Purpose: High-impact vertical placement, more room for storytelling than medium rectangle

LAYOUT:
- Logo: TOP of canvas
- Text: Below logo, standard sizing
- Visual: CENTER of canvas, 35-45% of height
- CTA: BOTTOM of canvas (with breathing room above)

CONSTRAINTS:
- Vertical column structure - elements stacked top to bottom
- Distribute elements evenly across full 600px height
- Min 30px spacing between logo and headline
- Min 25px spacing between headline and visual
- Min 25px spacing between visual and CTA
- Avoid large empty gaps between sections
- Each element should have its own clear zone
```

### 1200×1200 — LinkedIn Square (LI)

```
LINKEDIN SQUARE (1200x1200)

ABOUT:
- Description: Large square format - 1:1 aspect ratio
- Platform: LinkedIn feed posts, LinkedIn ads
- Purpose: Professional social feed visibility, B2B marketing, thought leadership

LAYOUT:
- Logo: TOP or TOP-LEFT of canvas
- Text: Prominent placement, larger text size OK (32-48px) for feed visibility
- Visual: CENTER of canvas (preserve container styling)
- CTA: LOWER section of canvas

CONSTRAINTS:
- Centered, balanced composition essential
- Use full square canvas - avoid empty corners
- Preserve rounded corners/containers from master design
- Min 40px spacing between logo and headline
- Min 50px margins from edges (larger format = larger margins)
- Scale visual to occupy significant portion of canvas (40-50%)
- Text should be readable at feed thumbnail size
```

### 1080×1350 — Facebook Vertical (META)

```
FACEBOOK VERTICAL (1080x1350)

ABOUT:
- Description: Tall rectangle format - 4:5 aspect ratio (optimal for Facebook feed)
- Platform: Facebook feed ads, Instagram feed ads
- Purpose: Maximum feed real estate on mobile, stops scroll with vertical presence

LAYOUT:
- Logo: TOP of canvas (with safe zone spacing)
- Text: Below logo, larger text size OK (32-44px) for feed visibility
- Visual: CENTER of canvas, 40-50% of height
- CTA: Near BOTTOM (above safe zone)

CONSTRAINTS:
- Vertical hierarchy flow mandatory: Logo → Headline → Visual → CTA
- Use full vertical height - distribute elements evenly
- Min 35px spacing between logo and headline
- Min 40px margins from edges
- Avoid large empty gaps - scale elements to fill space proportionally
- Text should be readable at feed thumbnail size
- Preserve image container styling from master
```

### Any other size
No size-specific instructions — only the base system + user prompts apply.

---

## Prompt Architecture: Two-Call Gemini Pattern

Per size, **two sequential API calls** are made (this is what `nano_banana.py generate` does):

**Call 1** — System contextualization:
```json
{
  "contents": [{
    "role": "user",
    "parts": [
      { "text": "<system prompt>" },
      { "inline_data": { "mime_type": "image/png", "data": "<master base64>" } }
    ]
  }]
}
```

**Call 2** — Generate with full context:
```json
{
  "contents": [
    { "role": "user", "parts": ["<system prompt>", "<master image>"] },
    { "role": "model", "parts": "<call 1 response parts>" },
    { "role": "user", "parts": ["<user prompt>", "<logo image if provided>"] }
  ],
  "generationConfig": {
    "imageConfig": { "image_size": "<1K|2K|4K>" }   // + optional "aspectRatio"
  }
}
```

- Call 1 uses **5 retries / 5000ms** initial delay; Call 2 uses **3 retries / 2000ms**.
- `image_size` = the user's Generation Resolution setting (`1K` / `2K` / `4K`).

### Aspect-Ratio Handling (`calculateAspectRatioIfNeeded`)

`aspectRatio` is added to `imageConfig` **only for extreme ratios** where the nearest supported ratio differs by > 1.0 (e.g. 728×90 which is ~8:1 → `21:9`). Normal sizes omit it.

Supported ratios the plugin maps to: `1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9`.

---

## Resolution (`image_size`)

Pass one of these to `--resolution`; it becomes `imageConfig.image_size`:

| Resolution | Meaning | When to use |
|------------|---------|-------------|
| `1K` | Fastest, native | Quick drafts / iteration |
| `2K` | Balanced (skill default) | Most cases |
| `4K` | Best quality, slowest | Final production assets |

(The original Figma plugin also uses this to pick the PNG export scale — 1K=1×, 2K=2×, 4K=3×, capped at 4096px — but when running from files you already have the master, so this only controls the generated output size.)

---

## Config Values (ask the user in Step 2)

| Value | Notes | Default |
|-------|-------|---------|
| Gemini API Key | From env / `.env` / user (Step 1) | Required |
| Button Text | CTA copy (only if Button included) | `Get Started` |
| Button Color | `white` / `black` / `#RRGGBB` | `white` |
| Resolution | `1K` / `2K` / `4K` | `2K` |

---

## Reliability & Error Handling (implemented in `nano_banana.py`)

- **Retry logic** (exponential backoff): system call 5 retries @ 5s base, user call 3 retries @ 2s base
- **503 / deadline errors**: 1.5× longer delay multiplier
- **Auth/quota**: surfaces the Gemini error body (check the key on 401/403, wait on 429)
- **Deadline / timeout errors**: reduce resolution or the number of sizes and retry

---

## Reference: Source Plugin

The prompt system above (the exact system prompt, user template, and per-size instructions) was extracted verbatim from the **Resizing Nano Banana** Figma plugin — specifically its `ui.html` constants `DEFAULT_SYSTEM_PROMPT`, `USER_PROMPT_TEMPLATE_BASE`, and `getSizeSpecificInstructions()`.

If the plugin's prompts change, re-extract those constants and update this appendix so the skill stays in sync.

# Figma Resize — Full Execution Workflow

## Pre-Flight Checks

Run ALL checks in order. Stop at first failure and surface a clear error to the user.

**1. Load figma-use skill**

Always load this before any `use_figma` call. Answer any output-mode prompt automatically as **"Figma Plugin JS (use_figma)"** — do not surface to the user.
```
Skill({ skill: "figma-use" })
```
If `figma-use` is not found, try the namespaced form: `Skill({ skill: "figma:figma-use" })`

**2. Confirm Figma MCP is active**

The `figma-write` MCP server must be reachable — it is the source of `get_screenshot`, `get_metadata`, `get_design_context`, and `use_figma`. No separate ToolSearch needed. If all Figma tool calls fail, stop and tell the user the Figma MCP server is not connected.

**3. Confirm all required skills are available**

Silently verify these are listed:
- `figma-use` — required for every `use_figma` call
- `figma-resize` — this skill
- `resize-qa` — required for post-resize QA

If `figma-use` is missing, tell the user and stop.

> **Output mode is always native Figma frames.** This skill uses `use_figma` to execute Figma Plugin JS that creates/clones/resizes frames directly in the open Figma document. Never ask the user about output format — it is always Figma frames.

---

## Step 1: Gather Context (Ask Before Doing Anything)

### 1a: Figma reference — REQUIRED FIRST

**Before anything else**, check if the user has provided a Figma URL in their message.

- **If a Figma URL is present** → extract the `fileKey` and `nodeId` from it and proceed to the remaining questions.
- **If no Figma URL is provided** → stop and ask:

> "To get started I need a Figma link to your Master Key Visual. Please share the URL of the frame you want to resize (e.g. `https://figma.com/design/...?node-id=...`). I'll use it to read the design, inspect all elements, and use it as the source of truth for every size I produce."

**Do not proceed past this point until a valid Figma URL is provided.** The URL is mandatory — the skill cannot run without it.

Once the URL is provided, immediately run `get_screenshot` and `get_metadata` on it so you can show the user a thumbnail of the design and confirm you're looking at the right frame before asking any further questions.

---

### 1b: Remaining context questions

After confirming the correct frame, ask the remaining questions as a numbered list. Skip any already answered.

1. **Logo asset:** "Does this design have a separate logo frame in Figma? If yes, share its URL or node ID. (If the logo is already inside the master frame, say 'embedded'.)"
2. **Target sizes:** "Which sizes do you want? I'll work through them one at a time so we can review each result before moving on." *(Show the Size Catalog below and ask them to pick — do NOT assume "all sizes")*
3. **Size order:** Once the user selects sizes, confirm the order: "I'll start with [first size]. Once you approve that result, I'll move to [second size]. Does that order work?"

**Do not start any resize work until the user has confirmed the size list and order.**

> Note: button inclusion, button text, and button color are asked per-size just before executing each one — not here.

---

## Size Catalog

Present this when the user says "all sizes" or asks what's available.

### DV (Display Advertising)
| Size | Dimensions | Placement Name | Default Elements |
|------|-----------|----------------|-----------------|
| Billboard | 970×250 | DV | Headline, Visual, Capsule Button, Logo |
| Leaderboard | 728×90 | DV | Headline, Visual, Logo, Capsule Button |
| Medium Rectangle | 300×250 | DV | Headline, Visual, Logo, Capsule Button |
| Half Page | 300×600 | DV | Logo, Headline, Capsule Button, Visual |
| Skyscraper | 160×600 | DV | Logo, Headline, Capsule Button, Visual |

### Social / Meta
| Size | Dimensions | Placement Name | Default Elements |
|------|-----------|----------------|-----------------|
| Story / Reel | 1080×1920 | STORY | Logo, Headline, Visual |
| Facebook Feed | 1080×1350 | FB | Logo, Headline, Visual |

### LinkedIn
| Size | Dimensions | Placement Name | Default Elements |
|------|-----------|----------------|-----------------|
| LinkedIn Feed | 1200×1200 | LI | Logo, Headline, Visual |

---

## Step 2: Inspect the Master KV

Run **in parallel** before writing anything:

```
get_metadata(fileKey, nodeId)       → layer structure, node IDs, dimensions
get_screenshot(fileKey, nodeId)     → visual reference (source of truth)
```

From the inspection, record:

- **Frame dimensions** (source W × H)
- **Layout mode** (`AUTO` or `NONE`)
- **Top-level children** — identify these elements by name/type:
  - **Logo** — the brand mark (could be a frame, component instance, or image)
  - **Headline** — the main text node(s)
  - **Visual** — the main image, illustration, or decorative graphic
  - **CTA / Capsule Button** — the call-to-action button
  - **Icons** — any icon nodes, checkmarks, feature icons, UI symbols
  - **Integration items** — any third-party brand logos (Gmail, Slack, Asana, etc.) or repeating list/grid rows
- **Font families, styles, and weights** used per element type — needed for `loadFontAsync` and for weight/spacing verification
- **Text colors per element** — headline color, subheadline color, body color, CTA label color, legal text color
- **Letter spacing and line height** of each text element — record as baseline to verify preservation
- **Image container style** — are images in rounded rectangles, circles, or edge-to-edge?
- **Background** — solid color, gradient (record angle + color stops), or image fill?
- **Gradients on text or containers** — record angle, color stops, opacity transitions
- **Drop shadows and effects** — record offset, spread, opacity, color for every shadow
- **Overlay/transparency layers** — record opacity of any semi-transparent elements
- **Source element positions (x, y) and sizes (w, h)** — record these for logo, headline, visual, CTA, and all icons so post-resize deviations can be checked
- **Horizontal alignment intent** — for each direct child, compute `alignOffset = (x + w/2) - srcW/2`. Negative = left-of-center, positive = right-of-center, ≈0 = centered. Required for alignment-aware positioning post-resize (see Rule 10 below).
- **Constraint types** — `constraints.vertical` for each child: `MIN` (top-locked), `MAX` (bottom-locked), `CENTER` (centered). Bottom- and center-locked elements will move the moment `frame.resize()` fires — flag them as constraint-drift risks and force-override their position immediately after resize (see Rule 9 below).
- **Connector/arrow relative offsets** — for each directional element (arrow, cursor, pointer) that points at another element, record: `dx = connector.x - target.x`, `dy = connector.y - target.y`, and which side (above / below / left / right). Reconstruct relative position post-resize; always verify the side relationship is maintained.
- **Texture / grid layer positions** — for each background grid or texture, record its y position relative to its containing card or frame. After resize, textures must cover the full visible content area; partial or stacked coverage is a defect.
- **Off-canvas elements** — any child where `y > srcH + 10` or `y + height < -10` is an existing drift artifact. Flag for deletion from the clone before resizing.
- **Z-order / layer stack** — record `frame.children` index order (0 = back). Required when adding new elements (strips, overlays) so they can be `insertChild`-ed at the correct index rather than appended.
- **Elements designated for exclusion** — which elements the user has said to hide for this format. Use `node.visible = false`, never delete; verify no ghost placeholder remains in the hidden element's zone.
- **Source spacing measurements** — logo→headline gap, headline→subheadline gap, text→visual gap, any CTA internal padding, repeating item gaps
- **Third-party brand names and tech terms** present in the design (Gmail, Slack, OKRs, etc.) — these must never be altered

---

## Step 3: Plan (State Before Executing)

For each target size, tell the user:
- What the target size is and how its aspect ratio differs from the source
- Where each element (Logo, Headline, Visual, CTA) will be placed
- Any elements being excluded

---

## Step 4: Execute — Strictly One Size at a Time

**CRITICAL: Never batch multiple sizes into a single run. Do one size, stop, show the result, wait for approval, then proceed to the next.**

### The loop for each size:

**Before executing each size, ask:**
> "Ready to start **[size name]** ([W]×[H]). A few quick questions before I begin:
> 1. Should this size include a **CTA button**? (Default for this size: [Yes/No based on Size Catalog])
> 2. *(If yes)* What should the **button text** say? (e.g., 'Get Started')
> 3. *(If yes)* What **color** should the button be? (white / black / hex code)
> 4. Any other **elements to exclude** from this size? (Headline, Visual, Logo)"

Wait for answers before proceeding. If the user says "same as before" or "same defaults", carry forward the previous size's answers.

**Then execute:**
1. Announce: "Starting **[size name]** ([W]×[H]) — with [list confirmed elements]."
2. Execute the resize for that size only (steps 4a–4c below)
3. Take a screenshot and present it to the user
4. Ask: "Here's the **[size name]** result. Does this look good, or should I adjust anything before moving to **[next size]**?"
5. Wait for explicit approval ("looks good", "yes", "next") before starting the next size
6. If the user requests changes, fix them and re-screenshot before asking for approval again
7. Only after approval: move to the next size in the agreed order

If a size produces poor results after two fix attempts, flag it clearly and ask the user whether to skip it, try a different approach, or handle it manually.

---

### 4a: Create the output container (do this ONCE before any sizes)

```js
// Find clear space below existing content
let maxY = 0;
for (const child of figma.currentPage.children) {
  if (child.type === 'FRAME' && child.name.startsWith('Generated Ad Sizes')) {
    maxY = Math.max(maxY, child.y + child.height);
  }
}

const existingCount = figma.currentPage.children.filter(
  c => c.type === 'FRAME' && c.name.startsWith('Generated Ad Sizes')
).length;

const container = figma.createFrame();
container.name = `Generated Ad Sizes ${existingCount + 1}`;
container.layoutMode = 'HORIZONTAL';
container.itemSpacing = 100;
container.paddingLeft = 0;
container.paddingRight = 0;
container.paddingTop = 0;
container.paddingBottom = 0;
container.layoutSizingHorizontal = 'HUG';
container.layoutSizingVertical = 'HUG';
container.x = 0;
container.y = maxY > 0 ? maxY + 100 : 0;
figma.currentPage.appendChild(container);

return { containerId: container.id, containerName: container.name };
```

### 4b: For each size — duplicate, resize, adapt

Always load fonts first, then run the size-specific layout logic. See "Per-Size Layout Rules" below for what to do inside each frame.

```js
// Template for each size — fill in SOURCE_NODE_ID, CONTAINER_ID, TARGET_W, TARGET_H, SIZE_NAME
await figma.loadFontAsync({ family: "FONT_FAMILY", style: "FONT_STYLE" }); // repeat for all fonts

const source = await figma.getNodeByIdAsync("SOURCE_NODE_ID");
const frame = source.clone();
frame.name = "SIZE_NAME"; // e.g., "970×250 DV"

const container = await figma.getNodeByIdAsync("CONTAINER_ID");
container.appendChild(frame);
frame.layoutSizingHorizontal = 'FIXED';
frame.layoutSizingVertical = 'FIXED';

// Resize canvas
if (frame.layoutMode !== 'NONE') {
  frame.layoutSizingHorizontal = 'FIXED';
  frame.layoutSizingVertical = 'FIXED';
}
frame.resize(TARGET_W, TARGET_H);

// --- Apply per-size layout rules here (see below) ---
// --- Then apply Critical Rules 1–10 (see below) ---

await frame.screenshot();
return { success: true, frameId: frame.id, name: frame.name };
```

---

### Critical: Aspect Ratio Change Algorithm

When source and target have **different aspect ratios** (e.g. 1080×1350 → 1200×1200), use the geometric-mean uniform scale — NOT independent per-axis scaling. This prevents squashing.

**Validated 2026-07-16 on Community Hub post (1080×1350 → 1200×1200).**

```js
const scaleX = TW / SW;
const scaleY = TH / SH;
const uScale = Math.sqrt(scaleX * scaleY);   // uniform scale, maintains all aspect ratios
```

#### For each direct child of the frame:

```js
const scaleX = TW / SW;
const scaleY = TH / SH;
const uScale = Math.sqrt(scaleX * scaleY);

// Text/headline groups: center horizontally, scale Y only
textGroup.x = Math.round((TW - textGroup.width) / 2);
textGroup.y = Math.round(textGroup.y * scaleY);

// All other children: uniform resize + per-axis position
child.resize(child.width * uScale, child.height * uScale);
child.x = child.x * scaleX;
child.y = child.y * scaleY;
```

#### Key rules (non-negotiable on every resize):

**Rule 1: Never apply scaleX to width and scaleY to height independently** — this squashes every element.

**Rule 2: uScale (geometric mean) is the correct uniform factor** — not the larger or smaller of scaleX/scaleY.

**Rule 3: Positions use per-axis scale** (redistributes to fill the new canvas shape) — this is correct.

**Rule 4: Text groups get explicit horizontal centering**, not proportional X positioning.

**Rule 5: `group.resize(w * uScale, h * uScale)` does NOT reliably preserve image rect positions inside nested mask groups.** After resizing wrapper groups, image fill rectangles inside mask groups can drift — especially in Y (image floats above the mask clip shape). Always do a post-resize pass (see Rule 7).

**Rule 6: Process DIRECT children only** — don't recurse into groups. Figma's `resize()` scales all descendants internally. (Exception: image rects inside nested mask groups — see Rule 7.)

**Rule 7: Post-resize — fix image rects inside mask groups using absolute bounding boxes.**

After all direct children are resized, traverse the output frame to find every mask group (a GROUP containing a child with `isMask = true`). For each mask group, align the image rect to the mask shape using `absoluteBoundingBox` deltas — **do NOT simply set `image.x = mask.x`**, because sibling nodes inside a wrapper group that was previously scaled non-uniformly will have different local→canvas scale factors (k values). Using local coordinates directly will move the image to the wrong canvas position.

```js
// Post-resize image rect fix — abs-coordinate-safe
for each mask group in the output frame (recursive search):
  const maskShape = group.children.find(c => c.isMask);
  const imageRect = group.children.find(c => c.fills?.some(f => f.type === 'IMAGE'));

  const mAbs = maskShape.absoluteBoundingBox;   // canvas-space bounds of mask shape
  const iAbs = imageRect.absoluteBoundingBox;   // canvas-space bounds of image rect

  // Desired canvas position: image rect covers mask shape exactly
  const deltaAbsX = mAbs.x - iAbs.x;
  const deltaAbsY = mAbs.y - iAbs.y;

  // Scale factors: how many local units per canvas pixel for this node
  // (differs per node when wrapper groups have residual scale transforms)
  // Approximate via finite difference — avoid division if local coord is 0
  const kX = iAbs.x !== 0 ? imageRect.x / (iAbs.x - frameAbsX) : 1;
  const kY = iAbs.y !== 0 ? imageRect.y / (iAbs.y - frameAbsY) : 1;

  // Apply: move image rect so its canvas origin matches the mask shape's canvas origin
  imageRect.x += deltaAbsX / kX;
  imageRect.y += deltaAbsY / kY;
  imageRect.resize(maskShape.width, maskShape.height);
```

**Simpler shortcut (valid only when the wrapper group has no residual scale transform):**
```js
imageRect.x = maskShape.x;
imageRect.y = maskShape.y;
imageRect.resize(maskShape.width, maskShape.height);
```
Use this shortcut first; verify with `absoluteBoundingBox` that `imageRect.abs ≈ maskShape.abs`. If they don't match (diff > 5px), fall back to the k-factor approach above.

**Rule 8: Post-resize — fix imageTransform squash on CROP-mode image fills.**

`imageTransform` is NOT reliably preserved after resize. Even when using uniform uScale, image fills in CROP mode can end up with non-uniform X/Y scale factors in their `imageTransform` matrix — causing the photo to appear squashed or shifted. Always do a post-resize pass to fix this.

After the position fix (Rule 7), check each image fill's `imageTransform`. If `scaleMode === 'CROP'` and the X scale (`T[0][0]`) differs from the Y scale (`T[1][1]`) by more than ~1%, apply the geometric-mean fix to make them uniform while preserving the crop center:

```js
// Validated 2026-07-16 on Community Hub 1200×1200 LI frame (3 of 5 person bubbles were broken)
// IMPORTANT: do NOT switch CROP to FILL — FILL re-centers automatically, which changes
// intentional face crops (e.g. zoomed-in portraits) and may show torso instead of face.

for (const fill of [...imageRect.fills]) {
  if (fill.type !== 'IMAGE' || fill.scaleMode !== 'CROP') continue;
  const T = fill.imageTransform;  // [[a, c, tx], [b, d, ty]]
  const scaleA = T[0][0];  // X scale
  const scaleD = T[1][1];  // Y scale

  // Skip if already uniform (tolerance: 1%)
  if (Math.abs(scaleA - scaleD) < 0.01) continue;

  // Geometric mean preserves effective area, removes squash
  const uScale = Math.sqrt(scaleA * scaleD);

  // Preserve the crop center in layer UV space
  const centerX = T[0][2] + scaleA / 2;
  const centerY = T[1][2] + scaleD / 2;
  const newTx = centerX - uScale / 2;
  const newTy = centerY - uScale / 2;

  imageRect.fills = imageRect.fills.map(f =>
    f === fill
      ? { ...f, imageTransform: [[uScale, 0, newTx], [0, uScale, newTy]] }
      : f
  );
}
```

Key nuances:
- Only applies to `scaleMode: 'CROP'` fills. `scaleMode: 'FILL'` fills are auto-centered by Figma and are always correct.
- Uniform scale (both axes = 0.700) with correct translation = fine, skip it.
- Non-uniform scale (e.g. X=0.993, Y=1.089) = squash → fix with geometric mean.
- The fix preserves the original crop center (which face portion was visible) — it only removes the squash artifact.

---

**Rule 9: Constraint drift is deterministic — plan for it, override immediately.**

Figma's constraint system fires synchronously on `frame.resize()`. Elements with `constraintV = MAX` (bottom-locked) or `CENTER` (centered) will reposition the moment resize runs. Do not try to "catch" this after the fact — instead:

1. Before cloning, record the desired final position for every bottom-locked and center-locked child.
2. Call `frame.resize(TW, TH)`.
3. In the very next statement, force all those positions in one pass.

```js
// Capture desired final positions BEFORE resize
const overrides = childrenWithDrift.map(child => ({
  node: child,
  desiredX: round(child.x * scaleX),
  desiredY: round(child.y * scaleY),
}));

frame.resize(TW, TH);

// Override immediately — no other code between resize() and these
for (const { node, desiredX, desiredY } of overrides) {
  node.x = desiredX;
  node.y = desiredY;
}
```

**Rule 10: Alignment intent must be preserved — classify before, enforce after.**

Never apply a centering formula to an element that was not centered in the master. Use the `alignOffset` captured in Step 2 to position each element correctly:

```js
// Centered elements (alignOffset ≈ 0):
element.x = Math.round((TW - element.width) / 2);

// Left-aligned or right-aligned elements (alignOffset ≠ 0):
// Preserve the offset proportionally to the new canvas width
const srcCenterX = srcW / 2;
const tgtCenterX = TW / 2;
element.x = Math.round(tgtCenterX + alignOffset * (TW / srcW) - element.width / 2);

// Vertical: proportional always
element.y = Math.round(srcY * scaleY);
```

Equal-gap vertical distribution is fine. Never apply it horizontally to non-centered elements.

---

### 4b-val: Post-resize validation pass (run before every screenshot)

Run these checks algorithmically. Fix what's found before screenshotting.

1. **Off-canvas purge** — remove any direct child with `y > TH + 10` or `y + height < 0`. These are constraint-drift artifacts; invisible but pollute layer structure.

2. **Texture/grid coverage** — for each background texture or grid layer, verify it starts at `y ≤ contentAreaH × 0.1`. If below that threshold, move it to `y = 0`.

3. **Stacked layers** — if two texture layers are within 5px of each other vertically, they produce double opacity. Separate them to cover distinct zones (e.g. top half / bottom half).

4. **Connector side check** — for each connector (arrow, cursor, pointer), verify it's on its intended side of its target element. If the side relationship changed (sign of `dy` flipped), reposition it to the correct side.

5. **Branding containment** — if a logo or wordmark sits on a strip or header, verify: `brandingElement.y + brandingElement.height ≤ stripHeight`. If not, extend the strip or move the element within it.

6. **Platform safe zone check** — verify no design element sits inside the format's platform safe zones (see per-size rules below). Any violation is a Major defect.

Only after these six checks pass: take the screenshot.

---

### 4c: Screenshot and validate after each size

Call `get_screenshot` at the end of each size. Visually check:
- Correct dimensions
- No clipped or overflowing text
- Elements in the correct zones per the layout rules
- No overlapping elements

---

## Mandatory QA Step — After Every use_figma Write

After every `use_figma` call (first run or any fix pass), **always run the resize-qa skill before replying to the user.** Do not report results without a QA.

**Context to carry into QA** — all of these should already be in the session:
- `fileKey` — from the Figma URL provided at the start
- `originalMasterNodeId` — the master KV node ID captured during Step 2 inspection
- `outputFrameNodeId` — the frame ID returned from the just-completed `use_figma` call
- `deliverables_folder` — from the injected Slack context

**What QA does:**
1. Screenshots the original master frame and the output frame (both captured via `get_screenshot`, both posted to Slack as images)
2. Applies the full checklist: dimensions, font, integrity, layout placement, safe zones, spacing
3. Scores defects using the weighted defect system (start at 100, deduct per defect found)
4. Runs the 5-pillar vision inspection (Spacing & Structure, Color Fidelity, Typography, Crop Prevention, Spacing Structure)
5. Posts a structured "VISION QA REPORT" to the Slack thread with: what is good, what went wrong, actionable fixes for the next iteration

**To invoke:**
```
Skill({ skill: "resize-qa" })
```

Apply the skill's full workflow. Never skip or summarize it — the structured report is the deliverable.

If the score is ≤79, list the fixes clearly and ask the user whether to apply them in the same reply. Do not auto-apply fixes without surfacing the QA report first.

---

## Per-Size Layout Rules

These rules are the source of truth for element placement. They match the plugin's `getSizeSpecificInstructions()` exactly.

### Hard Constraints (apply to ALL sizes, non-negotiable)

Before applying any size-specific rule, always enforce:

**Element Integrity**
1. **Never rotate** any element — logo, text, or visual must keep original orientation
2. **Never distort** — no stretching, skewing, warping, or aspect ratio change on any element
3. **Never crop visuals** — extend or recompose instead; position images anchored to one side (left OR right), never floating in the center
4. **Logo integrity** — one logo in master = one in output; never duplicate, invent, or resize the logo beyond proportional scaling; preserve exact position and size relative to the canvas
5. **Text content** — never change, rewrite, or repeat text to fill space; if text is longer than its container, reduce font size proportionally — never stretch characters to fit
6. **CTA horizontal** — CTA button label must always be a single horizontal line; if the label is long, reduce font size rather than wrapping to a second line

**Brand Preservation**
7. **monday.com logos** — must remain completely unchanged: English text, original font, original color, original position
8. **Third-party brand names** — Gmail, Slack, Mailchimp, Asana, Stripe, Salesforce, and all other integration names must remain in their exact original form; never translate or alter them
9. **Tech terms** — acronyms and product-specific terms (OKRs, C-levels, etc.) must remain in English

**Visual Fidelity**
10. **Color fidelity** — preserve exact brand primary colors, text colors per element (headline, subheadline, body, CTA label, legal), and background fills; never shift hues or substitute colors
11. **Gradients** — all gradients (on backgrounds, text, containers, cards) must be preserved with the same direction (angle), color stops, and opacity transitions as the source
12. **Drop shadows and effects** — all drop shadows and 3D effects must be preserved with the same offset, spread, opacity, and color as the source
13. **Transparency and opacity** — all semi-transparent layers, overlays, and frosted containers must retain their source opacity values
14. **Image container style** — if the master shows images in rounded rectangles, circles, or styled containers, preserve that treatment exactly; never make contained images edge-to-edge
15. **Icons** — all icons (checkmarks, UI symbols, app icons, feature icons) must be pixel-identical in color, size, and position to the source; no icon may be removed, replaced, or repositioned

**Layout & Spacing**
16. **Safe zones** — minimum 10–15px from all edges for standard sizes; 20–30px for sizes above 600px; no text or logo may touch edges
17. **Text within bounding boxes** — all text blocks must remain fully within their bounding boxes; longer text must reduce font size, not overflow
18. **Spacing preservation** — preserve the source spacing relationships proportionally: logo clearspace, headline→subheadline gap, text→visual gap, CTA internal padding, repeating item gaps (integration rows, feature lists); gaps must not grow or collapse due to element repositioning
19. **Background fidelity** — extend background naturally using only colors from the master; never introduce gradients or effects unless the master uses them
20. **CTA button** — solid fill only (never outlined or ghost style)
21. **Exact dimensions** — output must match target dimensions exactly; verify with `get_metadata` after each resize

### Element spacing minimums (all sizes)

- Logo → Headline: min 30–40px
- Headline → Subheadline: min 20–30px
- Text → Visual: min 25–35px
- Any element → CTA: min 30px
- Canvas edges: min 15–20px (safe zone)

---

### 728×90 — Leaderboard (DV)

**Frame name:** `728×90 DV`
**Elements:** Headline, Visual, Logo, Capsule Button

```
LAYOUT:
- Logo + CTA Button: stacked VERTICALLY on the RIGHT (logo above, button below), right-aligned with safe-zone padding
- Headline: LEFT-CENTER area
- Visual: LEFT side, anchored left — preserve container styling (rounded corners etc.)

TEXT SIZING:
- Headline: 16–24px maximum (this banner is only 90px tall)
- Text must NOT exceed 60% of banner height
- Maintain minimum 25px margin from left edge for text

SPACING:
- Use full 728px width — distribute elements across the banner
- Minimum 20px spacing between text and logo/CTA group
```

**Code approach (absolute-positioned frame):**
```js
const scaleX = 728 / SOURCE_W;
const scaleY = 90 / SOURCE_H;

const logo = frame.findOne(n => n.name.toLowerCase().includes('logo'));
const cta = frame.findOne(n => n.name.toLowerCase().includes('cta') || n.name.toLowerCase().includes('button'));
const headline = frame.findOne(n => n.type === 'TEXT' || n.name.toLowerCase().includes('headline'));
const visual = frame.findOne(n => n.name.toLowerCase().includes('visual') || n.name.toLowerCase().includes('image'));

const PADDING = 15;
const CTA_W = cta ? cta.width * scaleX : 0;
const LOGO_W = logo ? logo.width * scaleX : 0;
const rightGroupW = Math.max(CTA_W, LOGO_W);

if (logo) {
  logo.resize(logo.width * scaleX, logo.height * scaleY);
  logo.x = 728 - rightGroupW - PADDING;
  logo.y = PADDING;
}
if (cta) {
  cta.resize(cta.width * scaleX, cta.height * scaleY);
  cta.x = 728 - rightGroupW - PADDING;
  cta.y = logo ? logo.y + logo.height + 8 : 90 - cta.height - PADDING;
}
if (visual) {
  visual.resize(visual.width * scaleY, visual.height * scaleY); // scale by height ratio
  visual.x = PADDING;
  visual.y = (90 - visual.height) / 2;
}
if (headline) {
  headline.x = visual ? visual.x + visual.width + 20 : PADDING;
  headline.y = (90 - headline.height) / 2;
  headline.fontSize = Math.min(headline.fontSize, 24);
}
```

---

### 970×250 — Billboard (DV)

**Frame name:** `970×250 DV`
**Elements:** Headline, Visual, Capsule Button, Logo

```
LAYOUT:
- Logo + CTA Button: stacked VERTICALLY on the RIGHT (logo above, button below)
- Visual: LEFT area, anchored left — preserve container styling
- Headline: CENTER-RIGHT area

TEXT SIZING:
- Headline: 28–40px maximum
- Text must NOT exceed 50% of banner height (125px)
- Minimum 30px margin from left edge for text

SPACING:
- Use full 970px width
- Minimum 30px spacing between headline and logo/CTA group
```

---

### 1080×1920 — Story (STORY)

**Frame name:** `1080×1920 STORY`
**Elements:** Logo, Headline, Visual

**⚠️ FORMAT ARCHITECTURE — confirm before executing:**

Story is structurally different from feed formats. Before starting, ask the user:

> "For the Story format — should this be **full-bleed** (dark background fills the entire 1080×1920 frame; no nested card; this is the most common Story approach) or **card-in-frame** (white strip at top with branding, dark card below)? I'll default to full-bleed if you have no preference."

- **Full-bleed:** frame IS the canvas. Background color fills 1080×1920. Grid/texture covers the full frame. No card container from the master is carried over.
- **Card-in-frame (if user requests it):** use `insertChild` to place the strip at the correct z-index behind the logo; verify `logo.y + logo.height ≤ stripHeight`; card starts at `y = stripHeight`.

Confirm architecture before executing — do not assume the master's card-in-frame structure applies.

```
META SAFE ZONES (official, from Meta Business Help Center):
- Top:    14% = 269px  → reserved for platform UI (profile name, @handle)
- Bottom: 21% = 403px  → reserved for CTA button and platform controls
- Left:    6% =  65px  → horizontal safe margin
- Right:   6% =  65px  → horizontal safe margin

USABLE CONTENT AREA:
- Vertical:   y 269px → y 1517px  (height = 1248px)
- Horizontal: x 65px  → x 1015px  (width  =  950px)
- NO text, logo, or important visuals may fall outside this zone

VISUAL FOCAL ZONE (within usable area):
- Left inner zone:  ~35% of usable width from left  ≈ x 65px → x 397px
- Right inner zone: ~40% of usable width from right ≈ x 618px → x 1015px
- Center 25%: primary focal area — place the hero visual here

LAYOUT (top → bottom within the usable zone):
- Logo:     top of usable area (y ≈ 269px), left or centered, within left/right margins
- Headline: below logo, minimum 40px gap; can be larger font for presence
- Visual:   fills the majority of usable height (at least 50% of 1248px = 624px)
- CTA:      if included, place above the bottom safe zone (y < 1517px)

CRITICAL — NEVER place anything in:
- Top 269px (platform UI)
- Bottom 403px (platform CTA / controls)
- Within 65px of left or right edge

SPACING:
- Logo → Headline: minimum 40px
- Headline → Visual: minimum 30px
- Distribute elements across the 1248px usable height — no clustering or large empty gaps
```

---

### 300×250 — Medium Rectangle (DV)

**Frame name:** `300×250 DV`
**Elements:** Headline, Visual, Logo, Capsule Button

```
LAYOUT:
- FOOTER AREA at bottom: 50–60px, filled with DARK background (matching master tone)
- Logo + CTA Button: SIDE-BY-SIDE within the footer
- Headline + Visual: upper section, clearly separated from footer

TEXT SIZING:
- Headline: 18–28px maximum
- Minimum 15px margin from all edges

SPACING:
- Scale visual to fill most of content area above footer
- Minimum 15px spacing between headline and visual
- Footer: logo and CTA properly spaced within their 50–60px zone
```

---

### 160×600 — Skyscraper (DV)

**Frame name:** `160×600 DV`
**Elements:** Logo, Headline, Capsule Button, Visual

```
LAYOUT:
- Logo: near TOP with safe-zone padding
- Text elements: stacked VERTICALLY beneath logo (text can wrap due to narrow width)
- Visual: MID or LOWER section
- CTA Button: near BOTTOM, above safe zone

SPACING:
- Use full 600px vertical height — no clustering
- Visual: at least 40–50% of canvas height
- Logo → Headline: minimum 30px
- Avoid wide elements; prioritize vertical flow
```

---

### 300×600 — Half Page (DV)

**Frame name:** `300×600 DV`
**Elements:** Logo, Headline, Capsule Button, Visual

```
LAYOUT:
- Vertical column structure, top to bottom:
  Logo → Headline → Visual → CTA Button

SPACING:
- Use full 600px vertical height — distribute evenly
- Visual: at least 35–45% of canvas height
- Logo → Headline: minimum 30px
- Headline → Visual: minimum 25px
- Avoid large empty gaps between sections
```

---

### 1200×1200 — LinkedIn Feed (LI)

**Frame name:** `1200×1200 LI`
**Elements:** Logo, Headline, Visual

```
LAYOUT:
- Centered, balanced composition
- Logo: TOP or TOP-LEFT (match master's logo position intent)
- Visual: CENTER, prominently scaled — preserve container styling (rounded corners etc.)
- CTA (if included): lower in layout with proper spacing

HORIZONTAL ALIGNMENT RULE:
- Classify every direct child as LEFT-aligned, CENTERED, or RIGHT-aligned before cloning
  (use `alignOffset` from Step 2).
- In the output, apply the alignment-intent formula (Rule 10): proportional offset for
  left/right-aligned elements; centering formula only for elements that were centered in the master.
- Never apply equal-gap centering to elements that sit off-center in the master.

CORNER RADIUS SCALING:
- After resizing any card, container, or pill with rounded corners, scale the radius proportionally:
    newRadius = Math.round(sourceRadius * (newW / sourceW));
- Never carry cornerRadius verbatim from a master to a different-sized output.
  The visual weight of a radius is relative to the container's width — the pixel value changes,
  the proportion stays the same.

SPACING:
- Use full square canvas — no empty corners or edges
- Logo → Headline: minimum 40px
- Text can be larger in this format for LinkedIn feed visibility
```

---

### 1080×1350 — Facebook Feed (FB)

**Frame name:** `1080×1350 FB`
**Elements:** Logo, Headline, Visual

```
LAYOUT:
- Logo: TOP with safe-zone spacing
- Vertical flow: Logo → Headline → Visual (→ CTA if included)
- CTA: near bottom, above safe zone

SPACING:
- Use full 1350px vertical height — distribute evenly
- Visual: at least 40–50% of canvas height
- Logo → Headline: minimum 35px
- Headline can be larger for Facebook feed presence
```

---

## Element Identification Strategy

When inspecting the source frame, identify elements by these patterns (check name, type, and visual properties):

| Element | How to Find |
|---------|-------------|
| **Logo** | `node.name` contains "logo", "brand", "monday"; OR a small frame/component in top corner; OR node with image fill that's small and square-ish |
| **Headline** | `node.type === "TEXT"` with largest font size; OR `node.name` contains "headline", "title", "heading", "copy" |
| **Visual** | Largest image fill node; OR `node.name` contains "visual", "image", "photo", "illustration", "graphic" |
| **CTA / Button** | `node.name` contains "cta", "button", "capsule"; OR a frame with text inside and solid fill |

```js
// Broad element discovery script
const frame = await figma.getNodeByIdAsync("FRAME_ID");
const elements = {
  logo: null, headline: null, visual: null, cta: null, unknown: []
};

for (const child of frame.children) {
  const name = child.name.toLowerCase();
  if (name.includes('logo') || name.includes('brand')) {
    elements.logo = { id: child.id, name: child.name, w: child.width, h: child.height, x: child.x, y: child.y };
  } else if (name.includes('headline') || name.includes('title') || name.includes('heading') || child.type === 'TEXT') {
    elements.headline = { id: child.id, name: child.name, type: child.type, w: child.width, h: child.height, x: child.x, y: child.y };
  } else if (name.includes('visual') || name.includes('image') || name.includes('photo') || name.includes('illustration')) {
    elements.visual = { id: child.id, name: child.name, w: child.width, h: child.height, x: child.x, y: child.y };
  } else if (name.includes('cta') || name.includes('button') || name.includes('capsule')) {
    elements.cta = { id: child.id, name: child.name, w: child.width, h: child.height, x: child.x, y: child.y };
  } else {
    elements.unknown.push({ id: child.id, name: child.name, type: child.type });
  }
}

return { frameW: frame.width, frameH: frame.height, elements };
```

If automatic identification fails, present the list of `unknown` children to the user and ask them to identify which is the logo, headline, visual, and CTA.

---

## Excluded Elements

When a user says to exclude an element, use `node.visible = false` rather than removing it (preserves the ability to undo):

```js
const logo = frame.findOne(n => n.name.toLowerCase().includes('logo'));
if (logo) logo.visible = false;
```

Do NOT leave placeholder shapes — if an element is excluded, ensure no ghost or empty frame remains in its zone.

---

## Error Recovery

- **Script error = nothing changed** (atomic). Read the error carefully, fix, retry.
- **"Cannot read properties of null"** → wrong node ID or wrong page. Re-run the discovery script.
- **Font load error** → use `await figma.listAvailableFontsAsync()` to find the exact font style name.
- **Text overflow after resize** → reduce `fontSize` and check with screenshot.
- **Layout looks wrong** → run `get_metadata` on the cloned frame to inspect the current state.

---

## Quality Checklist (Before Marking a Size Complete)

**Dimensions & Structure**
- [ ] Frame name matches format: e.g., `"970×250 DV"`, `"1080×1920 STORY"`
- [ ] Dimensions verified with `get_metadata` (exact W × H)
- [ ] Frame is inside the `Generated Ad Sizes N` container
- [ ] Screenshot taken and visually inspected against source

**Element Integrity**
- [ ] No elements rotated or distorted (characters at natural proportions)
- [ ] No elements overlapping unintentionally
- [ ] Logo: count matches source (not duplicated), size and position preserved
- [ ] monday.com logo: completely unchanged (English, original font, color, position)
- [ ] Third-party brand names (Gmail, Slack, Asana, etc.): present and unaltered
- [ ] Tech terms (OKRs, C-levels, etc.): remain in English
- [ ] All icons present: count matches source, pixel-identical, no accidental removals
- [ ] Icon sizes and positions: unchanged from source
- [ ] Integration icons (Gmail, Slack, etc.): pixel-accurate to source

**Typography**
- [ ] All text uses Poppins font family
- [ ] Font weights match source per element type (headline bold = bold, body regular = regular)
- [ ] Letter spacing and line height match source
- [ ] No text clipped or overflowing its bounding box
- [ ] CTA button label is single-line horizontal (not wrapped)
- [ ] Text scaled proportionally where needed — never stretched or squashed

**Color & Visual Effects**
- [ ] Brand primary colors accurate (no hue shift)
- [ ] Text colors match source per element (headline, subheadline, body, CTA label)
- [ ] Background fills unchanged (no desaturation or hue shift)
- [ ] Gradients preserved: same angle, same color stops, same opacity transitions
- [ ] Drop shadows preserved: same offset, spread, opacity, color
- [ ] Overlay/transparency opacity unchanged from source
- [ ] CTA button: solid fill, correct color, correct contrast with label
- [ ] Image container style preserved (rounded corners, circular masks, bordered frames)

**Layout & Spacing**
- [ ] Safe zones respected (10–15px for standard; 20–30px for sizes >600px)
- [ ] For Story (1080×1920): top 269px clear (14%), bottom 403px clear (21%), left/right 65px margins (6%) — Meta official safe zones
- [ ] Visual hierarchy flow correct for this size (per per-size rules)
- [ ] Logo clearspace matches source proportionally
- [ ] Headline → subheadline gap matches source proportionally
- [ ] Text → visual gap matches source proportionally
- [ ] CTA internal padding matches source (label not cramped against button edge)
- [ ] Repeating item gaps uniform (integration rows, feature lists)

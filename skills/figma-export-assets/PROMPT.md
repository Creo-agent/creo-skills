# Figma Export Assets — Full Execution Reference

---

## Pre-Flight

Run ALL checks before any export work.

**1. Figma plugin installed?**
```bash
claude plugin list 2>/dev/null | grep -i figma
```
If missing: `claude plugin install figma@claude-plugins-official`

**2. Load figma-use skill**
```
Skill({ skill: "figma:figma-use" })
```
When asked about output mode — answer **"Figma Plugin JS (use_figma)"** automatically; do not surface to user.

**3. Load Figma MCP tools**
```
ToolSearch({ query: "select:mcp__figma__download_assets,mcp__figma__get_screenshot,mcp__figma__get_metadata,mcp__figma__use_figma" })
```
If any fail, tell the user the Figma MCP server is not connected and stop.

---

## Finding the Right Node ID

**From a Figma URL:** `?node-id=109-1465` → node ID is `109:1465` (replace `-` with `:`).

**From metadata inspection:**
```
get_metadata(fileKey)           → lists top-level pages
get_metadata(fileKey, pageId)   → lists frames on that page
get_metadata(fileKey, frameId)  → lists children of a frame
```

---

## Format & Size Selection — When to Ask vs. Proceed

### Proceed directly (no question needed)

| Condition | Action |
|---|---|
| Format and size explicitly stated ("export as 2x PNG", "give me the SVG") | Proceed with exactly what was asked |
| Called as a dependency from another skill | Proceed with what the calling skill specified |
| Request clearly implies a format ("I need the vector" → SVG; "for print" → PDF; "for retina" → PNG 2x/3x) | Infer and proceed |
| "All formats" or "all sizes" stated or strongly implied | Produce the full confirmed set (see below) |

### When to ask

If the user says something like "export this logo", "give me the icon", "download this frame" — no format, no size, no calling context — ask ONE question:

> *"Which formats and sizes do you need?*
> *Options: PNG (1x / 2x / 3x / 4x), SVG, JPG 2x, PDF — or say 'all' for the full set."*

### Format defaults by context

| Use case | Default export set |
|---|---|
| Web / dev handoff | SVG + PNG 1x + PNG 2x + PNG 3x |
| Marketing / social media | PNG 2x or 3x + JPG 2x |
| Print / production | PDF |
| Animation frame | PNG at the scale the pipeline needs (1x or 2x typically) |
| Quick preview or review | `get_screenshot` at 1024px (not a production asset) |
| "All formats" requested | Full confirmed set — see below |

### The "all formats" confirmed set

When the user asks for all formats, produce exactly these:

| Format | Method | Notes |
|---|---|---|
| SVG | `use_figma` + `exportAsync({ format: 'SVG_STRING', svgOutlineText: true, useAbsoluteBounds: true, colorProfile: 'SRGB' })` → Write tool | Only if node passes Vector Quality Check |
| PNG 1x | `download_assets(fileKey, nodeId, defaultFormat: 'png', defaultScale: 1)` + curl | |
| PNG 2x | `download_assets(fileKey, nodeId, defaultFormat: 'png', defaultScale: 2)` + curl | |
| PNG 3x | `download_assets(fileKey, nodeId, defaultFormat: 'png', defaultScale: 3)` + curl | |
| PNG 4x | `download_assets(fileKey, nodeId, defaultFormat: 'png', defaultScale: 4)` + curl | |
| JPG 2x | `download_assets(fileKey, nodeId, defaultFormat: 'jpg', defaultScale: 2)` + curl | Warn: JPEG artifacts visible on logos with sharp edges |
| PDF | `download_assets(fileKey, nodeId, defaultFormat: 'pdf')` + curl | Preserves vectors |

Run all `download_assets` calls in parallel (`&` in Bash), then run SVG export separately.

---

## Vector Quality Check — Do This Before Exporting SVG

> **Critical distinction:** SVG ≠ vector. A Figma node whose fills are `IMAGE` type will export as an SVG that wraps a base64-encoded raster inside `<image>` tags — not actual `<path>` elements.

### Step 1 — Inspect the node's fill type

Use `get_figma_data` (figma-rest MCP) on the node. Look at the `fills` array:
- `"type": "IMAGE"` → **raster fill** — SVG export embeds a base64 PNG, not paths. No Figma export method can produce vectors from this.
- `"type": "SOLID"` / `"GRADIENT_LINEAR"` / etc. → **safe** — real vector geometry.
- Children of type `VECTOR`, `BOOLEAN_OPERATION`, `ELLIPSE`, `RECTANGLE` → actual vector geometry.

If `figma-rest` is unavailable: do a test export, then check the SVG content for `<image>` tags.

### Step 2 — Decision tree

```
Node has IMAGE fill?
  ├─ YES → Vector export from Figma is impossible for this node.
  │         Fallback options (in order of quality):
  │           1. Check official brand sources (press kit, CDN, Wikimedia, GitHub)
  │           2. Import a different library component that IS vector (e.g. Vibe Icons)
  │           3. potrace auto-trace the raster (loses color, lower fidelity)
  │
  └─ NO  → Export using: exportAsync({ format: 'SVG_STRING', svgOutlineText: true,
            useAbsoluteBounds: true, colorProfile: 'SRGB' })
            Result will contain real <path> elements.
```

### What "vector" looks like in the Figma tree

| Node structure | SVG export quality |
|---|---|
| `VECTOR` or `BOOLEAN_OPERATION` children with SOLID/GRADIENT fills | ✅ Clean `<path>` elements |
| `RECTANGLE`/`ELLIPSE` with SOLID fills | ✅ Clean `<rect>`/`<circle>` or paths |
| `RECTANGLE` with `IMAGE` fill | ❌ `<image>` tag wrapping base64 PNG |
| `INSTANCE` of a component that internally uses IMAGE fills | ❌ Same — raster propagates through |

---

## Color Accuracy & No-Distortion — Export Settings

Always set these explicitly on every export call:

| Setting | Value | Why |
|---|---|---|
| `colorProfile` | `'SRGB'` | Default is `'DOCUMENT'` — forces sRGB for consistent colors across screens |
| `useAbsoluteBounds` | `true` | Default `false` crops drop shadows/glows that extend outside the node's layout box |
| `svgOutlineText` | `true` | Converts text to `<path>` elements — visual accuracy regardless of font availability |

---

## Export Methods — Choosing the Right One

| Method | Best for | Formats | Notes |
|---|---|---|---|
| **`download_assets`** (MCP) | Single node + any raw embedded bitmaps | PNG (default), or pass `defaultFormat` | Returns rendered export + all raw source images in fills. Default for rasters. |
| **`get_screenshot`** (MCP) | Quick visual reference / inspection | PNG only | Fast, no format options. Previews only — not final assets. |
| **`use_figma` + `exportAsync()`** (Plugin API) | SVG, multi-scale, full control | PNG, SVG, JPG, PDF | Only method that supports SVG. Required for `SVG_STRING`. |

> **Payload size rule:** If expected raster output is over ~20KB, use `download_assets` + curl — no payload limit. `SVG_STRING` is text (not bytes) and never hits this limit — **always export SVG via `use_figma` + `SVG_STRING`**.

---

## Method 1 — `download_assets` (Default for Rasters)

```
download_assets(fileKey, nodeId)                          → PNG at 1x
download_assets(fileKey, nodeId, defaultFormat: 'png', defaultScale: 2)  → PNG at 2x
download_assets(fileKey, nodeId, defaultFormat: 'svg')   → SVG (use use_figma instead for guaranteed vector)
download_assets(fileKey, nodeId, defaultFormat: 'jpg', defaultScale: 2)  → JPG at 2x
download_assets(fileKey, nodeId, defaultFormat: 'pdf')   → PDF
```

**Workflow:**
1. Call `download_assets` with the node ID
2. `curl -sL -o "<dest_path>" "<url>"` — URLs are short-lived, download immediately
3. Extension = the `format` field from the response (e.g. `.png`, `.jpeg`)

---

## Method 2 — `get_screenshot` (Quick Preview Only)

```
get_screenshot(fileKey, nodeId, maxDimension: 1024)    → 1024px longest edge
get_screenshot(fileKey, nodeId, maxDimension: 2048)    → higher detail
```

Returns a short-lived PNG URL. Download with curl immediately. Not a production asset.

---

## Method 3 — `use_figma` + `exportAsync()` (SVG / Multi-Scale)

### SVG export (preferred method for all SVG)

```js
// Switch to the correct page first
const page = figma.root.children.find(p => p.id === 'PAGE_ID');
await figma.setCurrentPageAsync(page);

const node = await figma.getNodeByIdAsync('NODE_ID');

const svgString = await node.exportAsync({
  format: 'SVG_STRING',
  svgOutlineText: true,       // text → paths (default, but be explicit)
  useAbsoluteBounds: true,    // no clipping
  colorProfile: 'SRGB',       // consistent colors
});

return { svg: svgString };
// SVG_STRING is a plain string — write directly with Write tool. No decode step needed.
```

### Batch SVG export — multiple nodes

```js
const nodeIds = ['NODE_ID_1', 'NODE_ID_2', 'NODE_ID_3'];
const results = await Promise.all(nodeIds.map(async id => {
  const node = await figma.getNodeByIdAsync(id);
  const svgString = await node.exportAsync({
    format: 'SVG_STRING',
    svgOutlineText: true,
    useAbsoluteBounds: true,
    colorProfile: 'SRGB',
  });
  return { id, name: node.name, svg: svgString };
}));
return results;
```

### Export constraints reference

| Constraint | Usage | Example |
|---|---|---|
| `{ type: 'SCALE', value: 2 }` | Multiply natural size | 200×32 → 400×64 |
| `{ type: 'WIDTH', value: 600 }` | Fix width, scale height to match | |
| `{ type: 'HEIGHT', value: 400 }` | Fix height, scale width to match | |

### Format options

| Format | `exportAsync` param | Notes |
|---|---|---|
| PNG | `{ format: 'PNG' }` | Lossless, transparent bg. Add `colorProfile: 'SRGB'`, `useAbsoluteBounds: true`. |
| JPG | `{ format: 'JPG' }` | Lossy, no transparency. Same settings. |
| SVG_STRING | `{ format: 'SVG_STRING' }` | **Preferred SVG method.** Returns markup as plain string. No Uint8Array/base64. |
| SVG | `{ format: 'SVG' }` | Returns Uint8Array — use `SVG_STRING` instead. |
| PDF | `{ format: 'PDF' }` | Scale constraints ignored. |

### Writing files to disk

```bash
# PNG/JPG from download_assets — download URL directly
curl -sL -o "<output-path>.png" "<url>"

# SVG — write SVG_STRING directly with Write tool (it's already a plain string)
# No decode step needed.

# PNG/JPG from use_figma exportAsync (base64 in result) — decode with python
python3 -c "import base64,sys; open(sys.argv[1],'wb').write(base64.b64decode(sys.argv[2]))" \
  "<output-path>.png" "<base64_string>"
```

---

## Smart Naming — Evaluate and Rename Before Saving

### Step 1 — Is the node name usable?

A name is **not usable** if it:
- Is a generic Figma default: `"Frame"`, `"Group"`, `"Rectangle"`, `"Ellipse"`, `"Vector"`, or any of those followed by a number
- Is a UUID or hash string
- Contains only Figma internal syntax (e.g. `"mj-image, (mjml:mj-image), (type: logo)"`)
- Is longer than ~40 characters
- Contains special characters that break filenames (`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`, `&`)

### Step 2 — Name resolution

**2a.** If the layer name is usable → clean it (lowercase, spaces→hyphens, strip special chars).

**2b.** If not usable → use vision to name it:
```
get_screenshot(fileKey, nodeId, maxDimension: 512)
→ download PNG via curl to a temp path
→ read the image with Read tool (multimodal)
→ describe in 2–4 words: "crm-logo", "monday-icon-teal", "hero-banner-purple"
```

Vision prompt: *"What is this image? Give me a 2-4 word lowercase hyphenated description that works as a filename — be specific about the content, not the format."*

**2c.** Fallback (if vision not possible): component set name → parent node name → file name + asset type → user's request wording.

### Step 3 — Apply naming convention

Format: `<short-descriptive-name>-v<NN>.<ext>` (single-scale or SVG)
Multi-scale rasters: `<name>-<scale>x-v<NN>.<ext>` e.g. `crm-logo-2x-v01.png`

Always check existing files in the folder and pick the next version number — never overwrite.

```
crm-logo-v01.svg               ✅
monday-icon-teal-v01.svg       ✅
crm-logo-2x-v01.png            ✅
hero-banner-1200x628-v01.png   ✅

Frame 47-v01.png               ❌  (generic default — run vision)
Group 2147240983-v01.svg       ❌  (generic — run vision)
Layout=Left,Capsule=On-v01.svg ❌  (variant suffix — strip to component set name)
```

---

## Saving Exports — Where to Put Files

In Creo / Slack-bot environments: use the `Deliverables folder for this conversation` path from the `[Slack context]` block.

In other environments (Claude Code CLI/Desktop): save to the current project directory or a named subfolder the user expects.

If the file also needs to appear in Slack: copy (not move) to `.slack-outputs/` — that folder is uploaded automatically at task end. Always keep the durable copy in the project folder too.

---

## Visual Integrity Check — Verify Every Export Before Delivering

Run after saving each file. Catches blank files, cropped content, color shifts, and partial renders before they reach the user.

### When to run it

Always run for:
- Logos and icons (wrong color or crop is a brand issue)
- Any asset where the user specified quality requirements
- Exports from deep instances, many nested layers, or gradient fills

Skip for quick preview screenshots where speed matters more than perfection.

### How to run it

```
1. Read the saved PNG/JPG with the Read tool (multimodal — Claude will see the image).
   For SVG: use get_screenshot on the node as the visual reference instead.

2. Check:
   ✅ Full asset visible — nothing clipped at the edges
   ✅ Proportions correct — not stretched or squashed
   ✅ Colors match the Figma design
   ✅ Content complete — no missing elements
   ✅ File has real content — not blank, not all-white

3. If anything fails:
   → Do NOT copy to .slack-outputs/
   → Log what's wrong
   → Retry with adjusted settings:
      - Add useAbsoluteBounds: true if not already set
      - Higher maxDimension if get_screenshot was used
   → Re-run the check on the retry
```

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Content cropped at edges | `useAbsoluteBounds: false` | Add `useAbsoluteBounds: true` |
| Colors washed out or shifted | Document color profile is Display P3 | Add `colorProfile: 'SRGB'` |
| Blank or white file | Node was off-screen or invisible | Check node visibility; try a different node ID |
| Only partial content | Wrong node ID (exported a child) | Move up the node tree |
| File too small (few bytes) | Export URL expired before curl ran | Re-request `download_assets` and curl immediately |

---

## Common Patterns by Use Case

### "Export this logo" (no format specified)
→ **Ask first.** Reply: *"Which formats and sizes do you need? Options: PNG (1x / 2x / 3x / 4x), SVG, JPG 2x, PDF — or say 'all' for the full set."*

### "Export all formats" / "export all sizes"
→ Produce the full confirmed set: SVG + PNG 1x/2x/3x/4x + JPG 2x + PDF.

### "Export at 1x, 2x, and 3x"
→ `download_assets` with `defaultScale: 1`, `2`, `3` in parallel. Save as `<name>-1x-v01.png`, `<name>-2x-v01.png`, `<name>-3x-v01.png`.

### "Get the SVG" / "I need the vector"
→ Run Vector Quality Check first. If node has vector geometry: `use_figma` + `SVG_STRING` → Write tool. If IMAGE fills: look for vector alternative in Vibe Icons or official brand sources.

### "For the website" / "for dev handoff"
→ SVG + PNG 1x/2x/3x. No JPG (needs transparency support). Run Vector Quality Check for SVG.

### "For print" / "as PDF"
→ `download_assets(fileKey, nodeId, defaultFormat: 'pdf')` + curl. Scale constraints ignored for PDF.

### "For social media" / "for marketing"
→ PNG 2x or 3x + JPG 2x. Warn if asset is a logo: *"JPG can show compression artifacts on logos with sharp edges — PNG is usually better."*

### "Give me all the images/photos from this frame"
→ `download_assets` — returns rendered frame export AND all raw embedded bitmap fills in `rawImages`.

### "Quick screenshot" / "show me how it looks"
→ `get_screenshot(fileKey, nodeId, maxDimension: 1024)` — preview only.

### "Export all icons from this page" (batch)
→ `get_metadata` to discover node IDs, then `use_figma` + batch `SVG_STRING` pattern. For PNGs: `download_assets` per node in parallel.

---

> **JPG note:** JPG compression produces visible block artifacts on sharp geometric edges (logos, icons). Prefer PNG for logos/icons. JPG is appropriate for photos and illustration-heavy banners. If a user requests JPG for a logo, produce it but add: *"JPG can show compression artifacts on logos with sharp edges — PNG is usually better for this asset."*

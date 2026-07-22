---
name: figma-export-assets
description: Export any Figma asset — logo, icon, illustration, frame, component, ad creative — to disk in any format and scale. Covers PNG (1x/2x/3x/4x), SVG (true vector via SVG_STRING), JPG, PDF, batch export, raw embedded images, and screenshots. Enforces color accuracy (sRGB), no-distortion bounds (useAbsoluteBounds), and runs a visual integrity check on every export. Call this skill from animation pipelines, landing page generators, ad resize workflows, or any task that needs a Figma asset as a local file.
---

# Figma Export Assets

**The standard asset extraction primitive for any workflow that needs a Figma asset as a local file.** Export any visual — logo, icon, illustration, banner, component — from a Figma file in the right format and size. Covers every export method and knows when to use each one.

---

## When This Skill Activates

### Direct user requests

Use when the user wants to:
- **Export** a logo, icon, illustration, banner, or any design asset from Figma
- **Download** a frame or component as PNG, SVG, JPG, or PDF
- **Get multiple sizes** of an asset (e.g. 1x, 2x, 3x for dev handoff)
- **Extract embedded images** from a design (photos, textures, placed bitmaps)
- **Screenshot** a frame for a quick visual reference
- **Batch export** several nodes in one go
- **Convert** a vector component to SVG for web use

Keywords: "export", "download", "get", "extract", "save", "screenshot", "grab", "pull", "output", "render", "give me the", "PNG", "SVG", "JPG", "PDF", "2x", "3x", "retina", "high-res", "assets"

### Called as a dependency by other skills

Any skill or workflow that needs a Figma asset as a local file should run this skill's steps rather than reinventing the export logic:

| Calling skill / workflow | What it needs from here |
|---|---|
| Animation pipelines (`/figma-to-animation`, `/export-as-gif`, etc.) | PNG frames or SVG assets to composite or animate |
| Landing page / web generation | SVG icons and logos, PNG hero images at 1x/2x |
| Ad resize (`/figma-resize`, `/resize-with-nano-banana`) | Source KV as PNG at correct scale |
| Design review / audit | Screenshots of frames for visual comparison |

When called as a dependency: run steps 1–10 (through integrity check) and return the local file path(s). Step 11 (Slack delivery) is the calling skill's decision.

---

## Setup & Dependencies

### Step 0: Verify Figma Plugin

```bash
claude plugin list 2>/dev/null | grep -i figma
```

If missing: `claude plugin install figma@claude-plugins-official`

### Step 1: Load figma-use Skill (MANDATORY before any `use_figma` call)

```
Skill({ skill: "figma:figma-use" })
```

When asked "What should the output be?" — answer **"Figma Plugin JS (use_figma)"** automatically.

### Step 2: Load Figma MCP tools

```
ToolSearch({ query: "select:mcp__figma__download_assets,mcp__figma__get_screenshot,mcp__figma__get_metadata,mcp__figma__use_figma" })
```

If tools resolve as `mcp__plugin_figma_figma__*` (plugin-installed MCP), use those names instead — same tools, different prefix.

### Dependency Chain

```
figma-export-assets (this skill)
  ├── Figma plugin installed (claude plugin install figma@claude-plugins-official)
  ├── figma:figma-use skill loaded — MANDATORY before every use_figma call
  ├── figma MCP tools: download_assets, get_screenshot, get_metadata, use_figma
  └── figma-rest MCP (optional) — get_figma_data for Vector Quality Check pre-flight
        If unavailable: do a test export and check SVG output for <image> tags instead
```

---

## Workflow Summary

1. **Get the node ID** — from the Figma URL, user input, or `get_metadata`
2. **Resolve format & size** — proceed if clear, ask one question if not
3. **Vector Quality Check** — if SVG needed, inspect node fills first
4. **Evaluate the node name** — use Smart Naming; fall back to vision for generic names
5. **Choose the right method** — `download_assets` for rasters; `use_figma` + `SVG_STRING` for SVG
6. **Export** — include `colorProfile: 'SRGB'` and `useAbsoluteBounds: true` on all calls
7. **Download URLs immediately** — `download_assets` URLs are short-lived, curl them right away
8. **Write SVG_STRING directly** — it's a plain string; use the Write tool
9. **Save to project folder** — `<short-name>-v<NN>.<ext>` naming convention
10. **Visual Integrity Check** — read each raster with Read tool (vision); retry if cropped/distorted
11. **Deliver** — return local file path; copy to `.slack-outputs/` only if Slack delivery was asked

See **PROMPT.md** for the complete method reference, Vector Quality Check, Smart Naming rules, format selection guide, all export code patterns, and integrity check procedure.

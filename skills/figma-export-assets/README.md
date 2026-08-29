# figma-export-assets

Export any visual asset from Figma to disk — logo, icon, illustration, frame, component, or ad creative — in any format and scale.

## What it does

- Exports any Figma node as PNG (1x/2x/3x/4x), SVG (true vector via `SVG_STRING`), JPG, or PDF
- Enforces color accuracy (`colorProfile: 'SRGB'`) and no-distortion bounds (`useAbsoluteBounds: true`)
- Validates SVG is truly vector (not a base64-wrapped raster) before exporting
- Generates smart filenames from layer names — falls back to model vision for generic names
- Runs a visual integrity check on every raster export before delivering
- Asks the user for format/size if ambiguous; uses context defaults otherwise

## Requirements

1. **Figma plugin** — `claude plugin install figma@claude-plugins-official`
2. **Figma MCP authenticated** — OAuth via the Figma plugin
3. **figma:figma-use skill** — loaded before any `use_figma` call
4. **figma-rest MCP** (optional) — for the Vector Quality Check pre-flight; can skip if unavailable

## Skill structure

| File | Purpose |
|---|---|
| `SKILL.md` | Frontmatter, activation triggers, setup/dependencies, workflow summary |
| `PROMPT.md` | Full execution reference: export methods, SVG quality check, naming rules, integrity check, all code patterns |
| `README.md` | This file |

## Usage

Trigger phrases: "export this logo", "give me the SVG", "download this frame as PNG", "get all sizes", "export all formats", "extract assets from this frame"

The skill handles format/size selection automatically based on context, or asks one clarifying question if ambiguous.

## Skills Index entry

| Field | Value |
|---|---|
| **Folder** | [`skills/figma-export-assets/`](.) |
| **Purpose** | Export any Figma asset to disk in any format: PNG (1x–4x), SVG (true vector), JPG, PDF. Enforces color accuracy and runs visual integrity checks. |
| **Triggers** | "Export this logo", "give me the SVG", "download this frame as PNG", "get all sizes", "extract images from this frame" |
| **Keywords** | `export`, `download`, `PNG`, `SVG`, `JPG`, `PDF`, `2x`, `3x`, `retina`, `assets`, `extract`, `vector` |
| **Dependencies** | Figma plugin · `figma:figma-use` skill · figma-rest MCP (optional, for Vector Quality Check) |
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-15 |

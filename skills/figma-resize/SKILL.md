---
name: figma-resize
description: Resize a Figma Master Key Visual (KV) into standard ad and social media formats by natively repositioning and adapting elements in Figma using the Plugin API. Applies the exact layout rules, element placement, and creative constraints used by the Resizing Nano Banana plugin. Triggers when the user wants to create size variants, resize a banner, adapt a KV to multiple formats, produce display ad sizes, or generate social media creatives from a master design.
---

# Figma Resize — Master KV to Ad Format Variants

Takes a Master Key Visual (KV) frame in Figma and produces native Figma frame variants at standard ad and social sizes, following the exact layout rules from the Resizing Nano Banana plugin.

## When This Skill Activates

- "Resize this KV to all banner sizes"
- "Create the DV sizes from this master"
- "Make the story format"
- "Generate all ad formats"
- "Resize to 300×250"
- "Adapt this to social sizes"

Keywords: "resize", "KV", "master", "banner sizes", "ad formats", "DV", "story", "social sizes", "all sizes", "create variants"

## What This Skill Does

Uses the Figma Plugin API via `use_figma` to:
1. Inspect the master KV frame and identify its key elements (logo, headline, visual, CTA)
2. Duplicate the frame for each target size
3. Resize the canvas and reposition/rescale each element according to strict per-size layout rules
4. Group all outputs in a labeled `Generated Ad Sizes` container frame

## Setup & Dependencies

### Step 0: Verify Figma Plugin

```bash
claude plugin list 2>/dev/null | grep -i figma
```

If missing: `claude plugin install figma@claude-plugins-official`

### Step 1: Load figma-use Skill

```
Skill({ skill: "figma:figma-use" })
```
When it asks "What should the output be?" — answer **"Figma Plugin JS (use_figma)"** automatically. Do not ask the user.

### Step 2: Load Figma MCP tools

```
ToolSearch({ query: "select:mcp__plugin_figma_figma__get_screenshot,mcp__plugin_figma_figma__get_metadata,mcp__plugin_figma_figma__use_figma" })
```

## Requirements

- **A Figma URL is mandatory before the skill can start.** If the user does not provide one, stop and ask for it before doing anything else.
- The URL must point to the Master KV frame (e.g. `https://figma.com/design/:fileKey/...?node-id=...`).

## Execution Workflow

See PROMPT.md for the complete step-by-step workflow, hard constraints, per-size layout rules, and quality checklist.

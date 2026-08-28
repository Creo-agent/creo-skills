---
name: figma-resize
description: |
  WHAT: Resize a Figma Master Key Visual (KV) into standard ad and social media formats by natively repositioning and adapting elements in Figma via the Plugin API. Applies the exact layout rules of the Resizing Nano Banana plugin.
  TRIGGERS: "create size variants", "resize this banner / KV", "adapt to multiple formats", "produce display ad sizes", "generate social media creatives from this master", "make the DV sizes / story / reel / 300x250".
  NOT FOR: AI image generation resize (no Figma involved) → use resize-with-nano-banana. Modifying content/text/colors in a Figma design → use figma-modify. Resizing an existing web animation → use resize-animation (in animations-and-motion-skills/).
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
5. Run mandatory QA (via `resize-qa` skill) after every write — never deliver results without a scored report

## Setup & Dependencies

### Step 1: Load figma-use Skill

```
Skill({ skill: "figma-use" })
```
If `figma-use` is not found, try `Skill({ skill: "figma:figma-use" })`. When it asks "What should the output be?" — answer **"Figma Plugin JS (use_figma)"** automatically. Do not ask the user.

### Step 2: Figma MCP tools

The `figma-write` MCP server is always active — no separate ToolSearch or load step needed. Tools `get_screenshot`, `get_metadata`, `get_design_context`, and `use_figma` are available immediately.

## Requirements

- **A Figma URL is mandatory before the skill can start.** If the user does not provide one, stop and ask for it before doing anything else.
- The URL must point to the Master KV frame (e.g. `https://figma.com/design/:fileKey/...?node-id=...`).

---

## Execution Workflow

See **PROMPT.md** for the complete step-by-step workflow, hard constraints, per-size layout rules, critical resize rules (Rules 1–10), mandatory QA step, element identification strategy, error recovery, and quality checklist.

> **Output mode is always native Figma frames.** This skill uses `use_figma` to execute Figma Plugin JS that creates/clones/resizes frames directly in the open Figma document. Never ask the user about output format — it is always Figma frames.

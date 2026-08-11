# Figma Resize — Master KV to Ad Format Variants

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that takes a Master Key Visual (KV) frame in Figma and produces native Figma frame variants at standard ad and social media sizes. Uses the Figma Plugin API to natively reposition and adapt elements, following the exact layout rules from the Resizing Nano Banana plugin. Includes a mandatory QA pass (via `resize-qa`) after every write — results always come with a scored vision report.

## What It Does

Given a Figma URL pointing to a master design frame, this skill:

1. Inspects the master KV and catalogs all elements (logo, headline, visual, CTA, icons, integration marks, gradients, shadows, spacing)
2. Presents the size catalog and confirms which sizes to generate and in what order
3. Before each size: asks about CTA inclusion, button text, button color, and element exclusions
4. Executes one size at a time — duplicates the frame, resizes the canvas, repositions elements per the size-specific layout rules
5. Applies Critical Rules 1–10 on every resize (geometric-mean scale, mask-group image rect fix, CROP imageTransform squash fix, constraint drift override, alignment intent preservation)
6. Screenshots each result and waits for explicit approval before moving to the next size
7. Runs `resize-qa` after every write — delivers a scored VISION QA REPORT with defects and fix instructions

## Supported Sizes

### Display Advertising (DV)

| Size | Dimensions |
|------|-----------|
| Billboard | 970×250 |
| Leaderboard | 728×90 |
| Medium Rectangle | 300×250 |
| Half Page | 300×600 |
| Skyscraper | 160×600 |

### Social / Meta

| Size | Dimensions |
|------|-----------|
| Story / Reel | 1080×1920 |
| Facebook Feed | 1080×1350 |

### LinkedIn

| Size | Dimensions |
|------|-----------|
| LinkedIn Feed | 1200×1200 |

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- [Figma MCP plugin](https://www.figma.com/community/plugin/claude-code-figma) connected and running in a Figma file
- `resize-qa` skill installed alongside this one (required for the mandatory QA step)
- A Figma file with a Master KV frame

## Installation

```bash
# Copy both skills into ~/.claude/skills/
cp -r figma-resize ~/.claude/skills/
cp -r resize-qa ~/.claude/skills/
```

## Usage

In Claude Code, provide a Figma URL and ask to resize:

```
Resize this KV to all banner sizes: https://figma.com/design/ABC123/my-design?node-id=1:2
```

Or use any of these trigger phrases:
- "Resize this KV to all banner sizes"
- "Create the DV sizes from this master"
- "Make the story format"
- "Generate all ad formats"
- "Resize to 300×250"
- "Adapt this to social sizes"

The skill walks you through the process one size at a time, showing a screenshot + QA report for each result before moving to the next.

## Hard Constraints (non-negotiable on every resize)

- No rotation or distortion of any element
- No visual cropping — extends or recomposes instead
- Logo integrity — never duplicated, never resized beyond proportional scaling
- Text preservation — never rewritten; font size reduced if needed, never stretched
- Brand preservation — monday.com logos, third-party brand names (Gmail, Slack, etc.), and tech terms kept exactly as-is
- Color fidelity — exact brand colors, gradients, shadows, and opacity preserved
- Safe zones — minimum padding from all edges; Meta-official safe zones for Story format
- Spacing preservation — proportional relationships between elements maintained

## Critical Resize Rules (added 2026-07-16)

Six Figma-specific bugs caught in production — all fixed by Rules 1–10 in PROMPT.md:

- **Rules 1–4:** Geometric-mean uniform scale (`uScale = √(scaleX × scaleY)`) prevents element squashing when aspect ratios change. Never use independent per-axis scaling on element size.
- **Rules 5–7:** Post-resize pass using `absoluteBoundingBox` to fix image rects inside nested mask groups. The simple `imageRect.x = maskShape.x` shortcut breaks when wrapper groups have residual scale transforms — use the k-factor approach when the shortcut fails.
- **Rule 8:** Post-resize pass to fix `imageTransform` squash on CROP-mode image fills. Even with uniform uScale, Figma can produce non-uniform X/Y scale factors in `imageTransform`. Fix with geometric mean, preserving the crop center.
- **Rule 9:** Constraint drift is deterministic — elements with `constraintV = MAX` (bottom-locked) or `CENTER` reposition the moment `frame.resize()` fires. Capture desired final positions before resize, then override immediately after.
- **Rule 10:** Alignment intent must be preserved — classify each element as left/center/right-aligned before cloning using `alignOffset = (x + w/2) - srcW/2`, then apply proportional offset (not centering formula) for non-centered elements.

## File Structure

```
figma-resize/
  SKILL.md    — Frontmatter, trigger phrases, setup, requirements
  PROMPT.md   — Full execution workflow, Rules 1–10, per-size layout rules, QA step, quality checklist
  README.md   — This file

resize-qa/    — Required companion skill
  SKILL.md    — Frontmatter, when/what, invocation
  PROMPT.md   — Full QA workflow, scoring rubric, 5-pillar vision inspection
  README.md   — Docs
```

## License

MIT

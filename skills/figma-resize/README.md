# Figma Resize — Master KV to Ad Format Variants

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that takes a Master Key Visual (KV) frame in Figma and produces native Figma frame variants at standard ad and social media sizes. It uses the Figma Plugin API to natively reposition and adapt elements, following the exact layout rules from the Resizing Nano Banana plugin.

## What It Does

Given a Figma URL pointing to a master design frame, this skill:

1. Inspects the master KV and identifies key elements (logo, headline, visual, CTA, icons)
2. Duplicates the frame for each requested target size
3. Resizes the canvas and repositions/rescales each element according to strict per-size layout rules
4. Groups all outputs in a labeled `Generated Ad Sizes` container frame
5. Takes a screenshot of each result for review before proceeding to the next size

## Supported Sizes

### Display Advertising (DV)

| Size | Dimensions |
|------|-----------|
| Billboard | 970x250 |
| Leaderboard | 728x90 |
| Medium Rectangle | 300x250 |
| Half Page | 300x600 |
| Skyscraper | 160x600 |

### Social / Meta

| Size | Dimensions |
|------|-----------|
| Story / Reel | 1080x1920 |
| Facebook Feed | 1080x1350 |

### LinkedIn

| Size | Dimensions |
|------|-----------|
| LinkedIn Feed | 1200x1200 |

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- [Figma MCP plugin](https://www.figma.com/community/plugin/claude-code-figma) connected and running
- A Figma file with a Master KV frame

## Installation

### Option 1: Install from this repo

```bash
claude skill add /path/to/claude-figma-resize
```

### Option 2: Copy files manually

Copy `SKILL.md` and `PROMPT.md` into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/figma-resize
cp SKILL.md PROMPT.md ~/.claude/skills/figma-resize/
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
- "Resize to 300x250"
- "Adapt this to social sizes"

The skill will walk you through the process one size at a time, showing a screenshot of each result for approval before moving to the next.

## How It Works

### Workflow

1. **Gather context** — Reads the master frame via `get_screenshot` and `get_metadata` to catalog all elements, fonts, colors, gradients, shadows, and spacing
2. **Confirm sizes** — Presents the size catalog and confirms which sizes to generate and in what order
3. **Per-size questions** — Before each size, asks about CTA inclusion, button text, button color, and any element exclusions
4. **Execute one at a time** — Duplicates the frame, resizes the canvas, repositions elements per the size-specific layout rules, then screenshots the result
5. **Review loop** — Shows each result and waits for approval before proceeding. If adjustments are needed, fixes and re-screenshots

### Hard Constraints

The skill enforces strict rules on every resize:

- **No rotation or distortion** of any element
- **No visual cropping** — extends or recomposes instead
- **Logo integrity** — never duplicated, never resized beyond proportional scaling
- **Text preservation** — never rewritten; font size reduced if needed, never stretched
- **Brand preservation** — monday.com logos, third-party brand names (Gmail, Slack, etc.), and tech terms kept exactly as-is
- **Color fidelity** — exact brand colors, gradients, shadows, and opacity preserved
- **Safe zones** — minimum padding from all edges; Meta-official safe zones for Story format
- **Spacing preservation** — proportional relationships between elements maintained

### Per-Size Layout Rules

Each size has specific layout instructions defining where elements go:

- **728x90 Leaderboard** — Logo + CTA stacked vertically on right; visual anchored left; headline center-left
- **970x250 Billboard** — Logo + CTA stacked vertically on right; visual left; headline center-right
- **300x250 Medium Rectangle** — Dark footer with logo + CTA side-by-side; headline + visual in upper section
- **300x600 Half Page** — Vertical column: logo, headline, visual, CTA top-to-bottom
- **160x600 Skyscraper** — Logo top, text stacked vertically, visual mid/lower, CTA near bottom
- **1080x1920 Story** — Meta safe zones enforced (top 14%, bottom 21%, sides 6%); logo top, headline below, visual fills majority
- **1080x1350 Facebook Feed** — Vertical flow: logo top, headline, visual, optional CTA
- **1200x1200 LinkedIn Feed** — Centered balanced composition; logo top/top-left, visual prominently centered

Full layout specifications with code examples are in [PROMPT.md](PROMPT.md).

## File Structure

```
figma-resize/
  SKILL.md    — Skill metadata, trigger phrases, setup steps, and requirements
  PROMPT.md   — Full execution workflow, per-size layout rules, code templates, and quality checklist
  README.md   — This file
```

## License

MIT

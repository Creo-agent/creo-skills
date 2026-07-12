# Resize with Nano Banana — AI Ad Resizing

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that resizes a master banner/ad design (a Key Visual) into multiple ad and social sizes using the **Nano Banana** prompt system and **Google Gemini** image generation.

Unlike the `figma-resize` skill (which repositions native Figma elements), this skill **AI-generates** each resized creative from an exported image — recomposing, not cropping — while preserving brand identity, verbatim copy, and visual hierarchy.

## What It Does

It's an **interactive, runnable** skill. When invoked, Claude:

1. **Checks for a Gemini API key** (`GEMINI_API_KEY` / `GOOGLE_API_KEY` in env or `.env`) and asks for it if missing
2. **Asks the user** for all inputs and assets — master image, optional logo, target sizes, per-size elements, button text/color, resolution
3. **Analyzes the master design** — *mandatory* — using Claude's own vision (falls back to Gemini `gemini-2.0-flash` only if the running model can't see images)
4. **Builds the exact Nano Banana system + user prompts** per size (dynamic element/exclusion lists + per-size layout rules)
5. **Generates** each resized creative via `gemini-3-pro-image-preview`
6. **Delivers** the output PNGs and offers a visual spot-check against the rules

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
| Story | 1080×1920 |
| Facebook Feed | 1080×1350 |

### LinkedIn

| Size | Dimensions |
|------|-----------|
| LinkedIn Feed | 1200×1200 |

Custom sizes (any W×H, max 2400px) are also supported.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- **Python 3** (standard library only — no pip installs)
- A **Google Gemini API key** with access to `gemini-3-pro-image-preview`
- A **master design image** (PNG/JPG). If it only lives in Figma, export the frame to PNG first.

## Installation

### Copy files manually

```bash
mkdir -p ~/.claude/skills/resize-with-nano-banana
cp -r SKILL.md PROMPT.md README.md scripts ~/.claude/skills/resize-with-nano-banana/
```

### Provide the API key

```bash
export GEMINI_API_KEY="your-key"      # or GOOGLE_API_KEY
# ...or add it to a local .env — the skill checks env and .env, and asks if missing
```

## Usage

In Claude Code:

```
Resize this with nano banana: /path/to/master.png
```

Or use any trigger phrase:

- "Resize with nano banana"
- "Generate all ad sizes with AI"
- "Adapt this KV to social sizes"
- "Create banner variants from this master"

Claude will ask for anything it's missing, analyze the master, confirm the plan, then generate each size.

## How It Works

### Prompt system

Each size gets a two-part prompt sent to Gemini in a two-call conversation:

- **System prompt** — hard constraints (exact dimensions, no distortion, no invention, Poppins-only text, master-as-truth), element rules (logo/text/visual/CTA), layout rules, color fidelity, and a pre-output validation checklist.
- **User prompt** — the target dimensions, a dynamically built INCLUDE list, an EXCLUDE list, source-handling rules, and the **per-size layout instructions** (e.g. 728×90 → logo+CTA stacked right; 1080×1920 → bottom 250px kept clear for platform UI).

The master-design brief from the analysis step is prepended as `MASTER CONTEXT` so copy stays verbatim and colors stay faithful.

### Hard constraints enforced

- Exact output dimensions — no approximation
- No rotation, distortion, or cropping of elements
- Logo integrity — never invented, duplicated, or distorted
- Text preserved word-for-word (scaled down, never rewritten), Poppins only
- Master image is the sole source for colors, textures, and mood

Full specifications — the exact prompts, dynamic prompt-building rules, all per-size layout blocks, the two-call API pattern, and aspect-ratio handling — are in [PROMPT.md](PROMPT.md).

## File Structure

```
resize-with-nano-banana/
  SKILL.md            — Skill metadata, triggers, setup, and requirements
  PROMPT.md           — Full workflow + exact prompts + per-size rules + generation commands
  README.md           — This file
  scripts/
    nano_banana.py    — Helper: mirrors the plugin's Gemini calls (analyze + generate)
```

## Relationship to `figma-resize`

Both skills resize a master KV to the same size catalog and share the Nano Banana layout rules. The difference:

- **`figma-resize`** — repositions native Figma elements via the Figma Plugin API (editable vector output, needs a Figma URL).
- **`resize-with-nano-banana`** — AI-generates flattened image creatives via Gemini (works from an exported image file, needs a Gemini API key).

## License

MIT

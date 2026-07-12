---
name: resize-with-nano-banana
description: Resize a master banner/ad design (a Key Visual) into multiple ad sizes using the Nano Banana prompt system and Google Gemini image generation. This is an INTERACTIVE, runnable skill — it asks the user for all needed inputs and assets, analyzes the master design using your own vision, then generates each resized creative. Triggers when the user wants to "resize with nano banana", generate AI-resized ad variants, create banner sizes with AI, or adapt a KV to multiple ad/social formats.
---

# Resize with Nano Banana

An **interactive, runnable** skill. When invoked, YOU (the model running this skill) drive the whole flow: collect the inputs and assets from the user, analyze the master design with your own vision, build the prompts, and generate each resized creative via Google Gemini's image model. It applies the exact Nano Banana prompt system (hard constraints, dynamic element lists, and per-size layout rules).

## When This Skill Activates

- "Resize with nano banana"
- "Generate all ad sizes with AI"
- "Adapt this KV to social sizes"
- "Create banner variants from this master"
- "AI resize to the DV sizes"

Keywords: "nano banana", "resize", "ad sizes", "banner sizes", "KV", "ai resize", "generate ad variants"

## What It Does

Given a master design image (and optionally a logo), this skill:

1. **Checks for a Gemini API key** in the environment / `.env`, and asks the user if missing
2. **Asks the user** for all inputs and assets (master, logo, target sizes, per-size elements, button text/color, resolution)
3. **Analyzes the master design** — MANDATORY — using your own vision (falls back to Gemini `gemini-2.0-flash` only if the running model can't see images)
4. **Builds the system + user prompts** per size (dynamic element/exclusion lists + per-size layout rules)
5. **Generates** each resized creative via `gemini-3-pro-image-preview` (two-call pattern, exact dimensions)
6. **Delivers** the output PNGs and offers a visual spot-check against the rules

## Setup & Dependencies

- **Python 3** (standard library only — the helper uses `urllib`, no pip installs)
- A **Google Gemini API key** — `GEMINI_API_KEY` or `GOOGLE_API_KEY` in the environment or a local `.env`. If absent, the skill asks the user for it.
- A **master design image file** (PNG/JPG). If it only exists in Figma, the user exports the frame to PNG first.
- Helper script: [`scripts/nano_banana.py`](scripts/nano_banana.py) — mirrors the plugin's Gemini calls (two-call pattern, `imageConfig`, aspect-ratio handling, retries).

## Supported Sizes

| Group | Name | Dimensions |
|-------|------|------------|
| DV | Billboard | 970×250 |
| DV | Leaderboard | 728×90 |
| DV | Medium Rectangle | 300×250 |
| DV | Half Page | 300×600 |
| DV | Skyscraper | 160×600 |
| META | Story | 1080×1920 |
| META | Facebook Feed | 1080×1350 |
| LI | LinkedIn Feed | 1200×1200 |

Custom sizes (any W×H, max 2400px) are also supported.

## Requirements

- Do **not** skip the intake questions (Step 2) or the mandatory master analysis (Step 3).
- The master analysis must be done with **your own vision** (Read the image); delegate to Gemini only if you truly cannot process images.

## Execution Workflow

See [PROMPT.md](PROMPT.md) for the complete step-by-step workflow, the exact system/user prompts, the dynamic prompt-building rules, all per-size layout instructions, and the generation commands.

# Resize Animation

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that adapts an existing
animation to a **different canvas size or aspect ratio** — and/or swaps its images — to produce
format variants (square, portrait, landscape, banner, story) **without rebuilding the motion**.

## What It Does

1. **Asks for the target size(s)/aspect ratio first** — a portrait reflow and a landscape reflow
   move elements in opposite directions, so this is pinned down before anything is placed.
2. Reflows element positions for the new frame — from a Figma source (via
   `precise-figma-composition`) or proportionally then hand-adjusted — keeping margins/gaps
   legible and overlaps intentional.
3. Keeps the motion **resize-proof** (dynamic, hero-relative collapse targets).
4. Optionally swaps assets, then re-verifies each variant (rest / mid / revealed / clean loop).

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed.
- An existing animation to adapt (HTML/GSAP or a Remotion composition).

## Key Files

`SKILL.md` (entry) · `PROMPT.md` (target-size questions, reflow strategy, resize-proof motion,
batch variants, verification)

## Installation

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/resize-animation
git checkout
cp -r skills/resize-animation ~/.claude/skills/
```

Use it by typing `/resize-animation`, or ask for a portrait/story/landscape version of an animation.

---

**Owner:** Elior Siegelwachs · **Last updated:** 2026-07-12

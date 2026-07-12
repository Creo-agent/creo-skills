# Precise Figma Composition

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that reproduces a Figma
frame's layout **pixel-accurately** in code — by pulling each node's exact coordinates from
Figma and scaling them to your target canvas, instead of eyeballing positions from a screenshot.

## What It Does

1. Pulls exact `x/y/w/h` per node via the Figma MCP `get_metadata`.
2. Computes a scale factor (target canvas ÷ Figma frame) and maps every node to absolute px.
3. Preserves draw-order stacking so intentional overlaps read correctly.
4. Emits absolute-positioned HTML/CSS, or a coordinates array for Remotion.
5. Verifies element-by-element against a `get_screenshot` of the same node.

Best for **scatter / overlay** layouts — cards, badges, and floating elements arranged around
a hero — where "close but wrong" eyeballing is obvious.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed.
- Figma MCP connected (design file, URL path `/design/`).
- A Figma URL pointing at the frame/node to reproduce.

## Key Files

`SKILL.md` (entry) · `PROMPT.md` (full workflow) · `references/figma-notes.md` (reading the
metadata correctly)

## Installation

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/precise-figma-composition
git checkout
cp -r skills/precise-figma-composition ~/.claude/skills/
```

Use it by typing `/precise-figma-composition`, or share a Figma link and ask to match it exactly.

---

**Owner:** Elior Siegelwachs · **Last updated:** 2026-07-12

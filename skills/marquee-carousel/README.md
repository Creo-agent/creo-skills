# Marquee Carousel

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that builds an endless,
auto-scrolling horizontal **marquee / carousel** in HTML/CSS/JS with GSAP — one or more rows
of items sliding sideways forever with no seam.

## What It Does

- Structures each row as a track holding ≥2 identical content groups (built once, content
  swapped from an array).
- Runs an always-on GSAP tween per row that translates by one group-width and **modulo-wraps**
  (`gsap.utils.wrap`) — seamless, with per-row speed/direction for a **parallax** feel.
- Measures copy-width only after fonts + images load (widths depend on both).
- Adds an optional moving **gradient-stroke "reflection"** highlight.
- Slots into a `loop-animator` loop as the scrolling layer, and ports to Remotion frame-math
  for `export-as-gif` (skip the wrap — invisible at the loop boundary).

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed.
- GSAP (loaded from CDN in the output). Typically used inside an `animation-scaffold` stage.

## Key Files

`SKILL.md` (entry) · `PROMPT.md` (markup/CSS, seamless-wrap tween, parallax, reflection, Remotion port, verification)

## Installation

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/marquee-carousel
git checkout
cp -r skills/marquee-carousel ~/.claude/skills/
```

Use it by typing `/marquee-carousel`, or just describe what you want.

---

**Owner:** Elior Siegelwachs · **Last updated:** 2026-07-13

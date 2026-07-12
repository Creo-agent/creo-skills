# Loop Animator

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that turns a static
composition (or a scroll/hover-triggered web animation) into a smooth, **auto-playing looping**
animation in HTML/CSS/JS with GSAP — without the jump cut most naive loops produce.

## What It Does

- Picks the right loop shape: **yoyo** (forward → hold → smooth reverse → repeat) for clean
  reveals, restart, or continuous.
- Builds one GSAP timeline (`repeat: -1`, `yoyo`, `repeatDelay`) that the whole scene rides.
- Adds the polish: **ramping-up stagger** (accelerating cadence, overlapping flights),
  **collapse-to-a-point** motion, and layer **cross-fades**.
- Sets up a fixed export-ready stage + JS scaler when the result is headed for video/social.
- Verifies deterministically by seeking timeline states and sampling `.time()`.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed.
- The composition to animate (an HTML file, or one produced by `extract-animation-from-web`).
- GSAP (loaded from CDN in the output).

## Key Files

`SKILL.md` (entry) · `PROMPT.md` (loop shapes, GSAP structure, motion patterns, verification)

## Installation

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/loop-animator
git checkout
cp -r skills/loop-animator ~/.claude/skills/
```

Use it by typing `/loop-animator`, or just describe what you want.

---

**Owner:** Elior Siegelwachs · **Last updated:** 2026-07-12

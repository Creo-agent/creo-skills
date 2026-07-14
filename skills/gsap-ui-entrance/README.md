# GSAP UI Entrance

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that adds a staggered,
**orchestrated UI entrance** to a DOM card inside a GSAP loop — box scales in, then text,
then rows, as one unified timeline.

## What It Does

- On a **yoyo** loop: authors the entrance as a forward *leave* so the reversal replays it as
  an entrance for free (order set by forward position).
- On a **forward-reset** loop: authors explicit **enter** and **exit** tweens with independent
  stagger direction (e.g. enter `from:'start'`, exit `from:'end'`).
- Excludes the orchestrated card from any generic collapse so it assembles in place.
- Keeps beats as `BASE + offset` constants and one easing family; verifies by scrubbing states.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed.
- A card already built as separate animatable layers (see `figma-1to1-card`) inside an
  existing GSAP loop (see `loop-animator`).

## Key Files

`SKILL.md` (entry) · `PROMPT.md` (core principle, beat map, leave/enter tweens, stagger rules, tuning table, verification)

## Installation

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/gsap-ui-entrance
git checkout
cp -r skills/gsap-ui-entrance ~/.claude/skills/
```

Use it by typing `/gsap-ui-entrance`, or just describe what you want.

---

**Owner:** Elior Siegelwachs · **Last updated:** 2026-07-13

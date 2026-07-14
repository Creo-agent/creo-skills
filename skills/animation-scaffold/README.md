# Animation Scaffold

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that scaffolds a fresh
HTML/CSS/JS animation project **from scratch** — the export-ready starting point for a
social / marketing / kiosk motion piece.

## What It Does

- Asks for the canvas first (square 1080², portrait 1080×1920, landscape, custom) and sets
  `STAGE_W`/`STAGE_H` up front.
- Emits one self-contained `index.html` with a **fixed pixel-exact stage**, a JS viewport-fit
  **scaler** that never changes the true render size, **GSAP** from CDN, a **fonts+images
  load-gate**, and an empty **`build()`** hook.
- Explains the fixed-stage rationale (deterministic export) and how to convert
  `getBoundingClientRect` back to stage-local coordinates.
- Verifies over a local HTTP server (since `file://` is blocked in the preview) by seeking
  the timeline.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed.
- Nothing else — this is the from-scratch entry point. GSAP loads from CDN.

## Key Files

`SKILL.md` (entry) · `PROMPT.md` (canvas decision, full `index.html` scaffold, verify recipe, hand-off order)

## Installation

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/animation-scaffold
git checkout
cp -r skills/animation-scaffold ~/.claude/skills/
```

Use it by typing `/animation-scaffold`, or just describe what you want.

---

**Owner:** Elior Siegelwachs · **Last updated:** 2026-07-13

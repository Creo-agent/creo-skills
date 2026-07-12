# Export as GIF (via Remotion)

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that renders an animation
into a real **GIF, MP4, or WebM** by rebuilding it in [Remotion](https://www.remotion.dev) —
frame-based and deterministic, so renders are exact and loops are seamless.

## What It Does

1. **Asks for the output spec first** — dimensions/resolution, fps, format, and any hard size
   limit (e.g. "under 5 MB for Slack") — because these drive the composition and render flags.
2. Scaffolds a Remotion project and ports the motion to frame-based (`useCurrentFrame`), with a
   GSAP-ease → Remotion `Easing` cheat-sheet.
3. Reproduces seamless loops with a **triangle-wave** timeline (forward → hold → reverse → hold).
4. Verifies with still renders, then renders the GIF/MP4 and tunes `--scale` / `--every-nth-frame`
   until it hits the size target.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed.
- Node.js + npm (Remotion installs its own headless renderer).
- The animation to render (an HTML/GSAP loop, or a motion spec).

## Key Files

`SKILL.md` (entry) · `PROMPT.md` (output-spec questions, scaffold, easing cheat-sheet,
triangle-wave loop, GIF size levers)

## Installation

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/export-as-gif
git checkout
cp -r skills/export-as-gif ~/.claude/skills/
```

Use it by typing `/export-as-gif`, or just describe what you want (e.g. "render this as a gif under 5mb").

---

**Owner:** Elior Siegelwachs · **Last updated:** 2026-07-12

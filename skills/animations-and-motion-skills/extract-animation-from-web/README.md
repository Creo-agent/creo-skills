# Extract Animation from Web

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that extracts a single
animated section from a live website into one **self-contained HTML file** — markup, the CSS
that styles it, the JS that animates it (GSAP/ScrollTrigger/Splide/etc.), and all its images.
First stage of the animation pipeline (`extract → loop → resize → export`).

## What It Does

Given a URL (or a live page open in the browser), this skill:

1. Fetches the **real rendered HTML**, defeating the common JS-stub response (browser headers,
   or reading the live DOM).
2. Locates the CSS/JS bundles and extracts **only** the rules + animation config for the section.
3. Downloads images (including the largest `srcset` candidate) and rewires them to local paths.
4. Assembles a single `.html` with CSS + JS inlined and assets local.
5. Verifies in a browser preview — console errors, image load, and motion states.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed.
- A URL to the page, or the page open in the browser tools.
- `curl` and `python3` (used by `scripts/extract_css.py`).

## Key Files

`SKILL.md` (entry) · `PROMPT.md` (full workflow) · `references/gotchas.md` · `scripts/extract_css.py`

## Installation

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/extract-animation-from-web
git checkout
cp -r skills/extract-animation-from-web ~/.claude/skills/
```

Use it by typing `/extract-animation-from-web`, or just describe what you want.

---

**Owner:** Elior Siegelwachs · **Last updated:** 2026-07-12

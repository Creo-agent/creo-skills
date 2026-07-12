# Creo Skills Registry

This repo tracks the skills installed on the Creo Slack bot, synced from the
monday.com marketing design team's canonical hub at
[DaPulse/marketing-design-ai-hub](https://github.com/DaPulse/marketing-design-ai-hub/tree/master/skills).

## How it works

- **Source of truth:** `DaPulse/marketing-design-ai-hub/skills/`
- **Runtime install:** `~/.claude/skills/<name>/` on the Creo Mac
- **Creo bot wrappers:** `Creo Workspace/skills/<name>.md` — flat files the bot injects as skill instructions
- **Daily sync:** A cron agent runs every day at ~8am, checks for upstream changes,
  and opens a PR to this repo if any skill is new or updated.
  Elior reviews and merges; merge = skill is live on next Creo session.

## Skills

| Skill | Purpose | Status |
|---|---|---|
| `export-as-gif` | Render HTML/GSAP animation to GIF/MP4/WebM via Remotion | ✅ installed |
| `extract-animation-from-web` | Rip an animated section off a live site into a standalone HTML | ✅ installed |
| `figma-modify` | Modify/tweak existing Figma designs via MCP | ✅ installed |
| `figma-resize` | Resize a Figma KV into all standard ad & social formats | ✅ installed |
| `loop-animator` | Turn a scroll/hover animation into a seamless auto-playing GSAP loop | ✅ installed |
| `monday-presentation` | Generate branded monday.com HTML slide decks | ✅ installed |
| `precise-figma-composition` | Reproduce a Figma frame layout pixel-accurately in code | ✅ installed |
| `resize-animation` | Adapt an animation to new canvas sizes/aspect ratios | ✅ installed |

## Sync script

`scripts/sync-skills.sh` — run this to manually check for updates and install them.

## Adding a new skill

1. Add it to `DaPulse/marketing-design-ai-hub/skills/`
2. The daily cron will detect it and open a PR here automatically
3. Review and merge — skill is active on next Creo session

# carousel-agent-animation

Generate a self-contained HTML/CSS/vanilla-JS animation featuring AI agent character cards from a Figma file. Two styles:

- **Carousel** — infinite 5-card fan loop, center card elevated, pure scale/position transitions, seamless with no entrance flash
- **Floating agents** — viewport-scaled 1280×734 scene, cards spring in after a typewriter prompt, float, then exit and loop

## Usage

```
/carousel-agent-animation
```

Claude will ask for: Figma file URL · agent labels · animation style · output folder · Figma token (if MCP not connected).

If you already have images (PNG or SVG), share their folder path — Claude skips the Figma download steps.

## Install

```bash
mkdir -p ~/.claude/skills

git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub 2>/dev/null || (cd /tmp/mdai-hub && git pull)
cd /tmp/mdai-hub
git sparse-checkout set skills/animations-and-motion-skills/carousel-agent-animation
git checkout

cp -r skills/animations-and-motion-skills/carousel-agent-animation ~/.claude/skills/
echo "✓ Installed"
```

## Examples

```
/carousel-agent-animation https://www.figma.com/design/XYZ/Agents?node-id=10-20
  agents: Lead Qualifier, Pipeline Analyst, Deal Desk Agent, Meeting Notetaker, Prospect Researcher
  style: carousel

/carousel-agent-animation
  I have SVGs in ~/Desktop/agents-svg — use floating style
```

## Outputs

| File | Description |
|---|---|
| `{name}.html` | Self-contained page; references `{name}.css`, `{name}.js`, `images/` |
| `{name}.css` | All styles — no external CSS dependencies |
| `{name}.js` | Vanilla JS loop — no framework, no bundler |
| `images/` | Downloaded PNGs or user-supplied SVGs |

## Dependencies

- No build tools or npm required
- Figma MCP (optional — falls back to REST API automatically)
- Figma Personal Access Token (only if Figma MCP not connected)
- Python 3 for local preview: `python3 -m http.server 8765`

## Key files

`SKILL.md` · `PROMPT.md` · `README.md`

## Registry

| Field | Value |
|---|---|
| **Folder** | [`skills/animations-and-motion-skills/carousel-agent-animation/`](.) |
| **Purpose** | Generate a looping HTML/CSS/JS agent-card animation (fan carousel or floating-cards scene) from a Figma file or user-supplied images |
| **Triggers** | "agent card animation", "carousel animation from Figma", "floating agent cards", "animate my agent cards", "card fan loop", "carousel-agent-animation" |
| **Outputs** | Self-contained `{name}.html` + `{name}.css` + `{name}.js` + `images/` |
| **Dependencies** | Figma MCP or Figma Personal Access Token (optional if images supplied) |
| **Owner** | Moshe Schvarcz |
| **Last updated by** | Moshe Schvarcz |
| **Last updated** | 2026-07-20 |

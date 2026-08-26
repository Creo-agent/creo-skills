# animation-to-webflow

A Claude skill for embedding a standalone HTML/CSS/JS animation prototype
into a live Webflow page headlessly, via the Webflow Data API — tab reveals,
section entrances, hero loops, modal payloads.

It exists because Webflow silently sanitizes HTML written through the Data
API (stripping `class` and `src` attributes) and collapses containers whose
visibility is toggled the naive way (`display:none`) — both cause an
animation to appear broken or invisible with no error message. This skill
documents the JS DOM-builder workaround and every other constraint
discovered wiring real animations into production.

## Layout

```
animation-to-webflow/
├── SKILL.md     # router + quick-reference checklist — the entry point Claude reads first
└── PROMPT.md    # phases 1–10, technical reference, applied examples, failure-modes table
```

## Install

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/animation-to-webflow
git checkout
cp -r skills/animation-to-webflow ~/.claude/skills/
```

## Requirements

- Webflow MCP (Data API tools) connected, with a site you own/are authorized on
- A standalone HTML/CSS/JS animation prototype (e.g. exported from a Figma
  motion frame) to embed
- For full Webflow tool/parameter lookup beyond this skill's own reference:
  [`../../knowledge/webflow-mcp/tools-index.md`](../../knowledge/webflow-mcp/tools-index.md)

## Related

- [`figma-to-webflow-section`](../figma-to-webflow-section/SKILL.md) — for
  building a Webflow section from a Figma design from scratch, instead of
  embedding an existing animation file into a section that already exists

## Scope

Build only into Webflow sites you own or are authorized on. Repos live under
the dapulse / mondaycom orgs.

## Owner

Elior Siegelwachs — last updated 2026-08-10

# figma-to-webflow-section

A Claude skill for building any Figma design section into a Webflow page
headlessly, via the Webflow Data API — heroes, feature grids, pricing,
testimonials, navs, footers, CTAs, and card rows.

It encodes the non-obvious Webflow Data API behavior that's expensive to
rediscover each run (silent breakpoint failures, longhand-only styles, the
freeform-code path for responsive CSS, the two-step S3 asset upload) plus a
vision-driven interaction pass that decides hover/focus/click/scroll/animation
behavior from the design itself.

## Layout

```
figma-to-webflow-section/
├── SKILL.md                        # router + context — the entry point Claude reads first
├── PROMPT.md                       # phases 1–8, the full run procedure
├── references/
│   ├── webflow-data-api.md         # envelope, tool signatures, action shapes
│   ├── api-gotchas.md              # silent failures + workarounds
│   ├── webflow-styles.md           # longhand-only, base-breakpoint-only rules
│   ├── responsive-patterns.md      # viewport fill, pill scroll, media queries
│   ├── interaction-patterns.md     # element archetype → interaction recipe
│   ├── webflow-active-states.md    # active/selected state patterns (tabs, pills, nav)
│   ├── section-types.md            # per-section-type guidance
│   └── asset-pipeline.md           # Figma download → Webflow upload
└── scripts/
    └── logo-fix.py                 # transparency transform for logos on opaque bg
```

## Install

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/figma-to-webflow-section
git checkout
cp -r skills/figma-to-webflow-section ~/.claude/skills/
```

The whole folder ships together — `SKILL.md` loads first, `PROMPT.md` is the
run procedure, and the reference files are pulled into context per-phase as
needed.

## Requirements

- Webflow MCP (Data API tools) connected, with a site you own/are authorized on
- Figma MCP connected
- Python 3 + Pillow (`pip install Pillow`) for `logo-fix.py`
- For full Webflow tool/parameter lookup beyond this skill's own cheat sheet:
  [`../../knowledge/webflow-mcp/tools-index.md`](../../knowledge/webflow-mcp/tools-index.md)

## Related

- [`animation-to-webflow`](../animation-to-webflow/SKILL.md) — for embedding a
  pre-built standalone HTML/CSS/JS animation prototype into an existing
  Webflow section, instead of building a section from a Figma design

## Scope

Build only into Webflow sites you own or are authorized on. Repos live under the
dapulse / mondaycom orgs.

## Owner

Elior Siegelwachs — last updated 2026-08-10

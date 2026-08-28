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
├── SKILL.md                        # phases 1–8; the entry point
├── references/
│   ├── webflow-data-api.md         # envelope, tool signatures, action shapes
│   ├── api-gotchas.md              # silent failures + workarounds
│   ├── webflow-styles.md           # longhand-only, base-breakpoint-only rules
│   ├── responsive-patterns.md      # viewport fill, pill scroll, media queries
│   ├── interaction-patterns.md     # element archetype → interaction recipe
│   ├── section-types.md            # per-section-type guidance
│   └── asset-pipeline.md           # Figma download → Webflow upload
└── scripts/
    └── logo-fix.py                 # transparency transform for logos on opaque bg
```

## Install

Clone into your Claude skills directory (or install via your skills tooling).
The whole folder ships together — SKILL.md loads first, and the reference files
are pulled into context per-phase as needed.

## Requirements

- Webflow MCP (Data API tools) connected, with a site you own/are authorized on
- Figma MCP connected
- Python 3 + Pillow (`pip install Pillow`) for `logo-fix.py`

## Scope

Build only into Webflow sites you own or are authorized on. Repos live under the
dapulse / mondaycom orgs.

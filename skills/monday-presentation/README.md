# marketing-presentations

A Claude Code skill for generating professional, self-contained monday.com branded HTML presentations. Invoke it with `/monday-presentation-v2` in any Claude Code session.

---

## What it does

Walk through a guided flow — pick a recipe, provide content (paste, file, or just a topic), optionally add charts/metrics, review the layout plan, and Claude generates a single `.html` file with all CSS, JS, icons, and logos inlined. No external dependencies. Open it in a browser and present.

---

## Installation

```bash
cd marketing-presentations
bash install.sh
```

Then in any Claude Code session:

```
/monday-presentation-v2
```

---

## Recipes

| Recipe | Slides | Best for |
|--------|--------|---------|
| Quick Update | 5–8 | Status updates, announcements |
| Product Launch | 10–15 | New features, launches |
| Team Review | 8–12 | Retrospectives, OKR reviews |
| Training | 15–20 | Workshops, education |

---

## Slide templates

19 layout classes in `design-system.css`. Open `slide-templates.html` in a browser to preview all of them.

---

## Design system

- **Colors:** Purple `#6164ff`, Green `#00c875`, Yellow `#ffcb00`, Red `#ff3d57`
- **Font:** Poppins (Regular 400 + SemiBold 600)
- **Themes:** Dark (default) and light via `data-theme="light"`
- **Icons:** 268 monday.com icons via embedded WOFF2 font (`icon-font.css`)

---

## Key files

| File | Purpose |
|------|---------|
| `SKILL.md` | Full workflow and generation rules (the Claude skill definition) |
| `RECIPES.md` | 5 presentation recipes with slide-by-slide structure |
| `DESIGN_SYSTEM.md` | Complete token, component, and template class reference |
| `ICON_FONT_REFERENCE.md` | All 268 icon names and HTML entities |
| `BRAND_ASSETS.md` | monday.com SVG logos (dark + light variants) |
| `design-system.css` | CSS tokens, components, and 19 template layout classes |
| `slide-templates.html` | Live previews of every template (open in browser) |
| `design-system-showcase.html` | Design token and component reference page |
| `icon-font.css` | Icon font with base64-embedded WOFF2 |
| `icon-font-package/` | Standalone icon font package with integration guide |
| `install.sh` | One-command install for Claude Code |
| `Logos/` | monday.com wordmark SVGs (white + black) |

---

## Navigation (in generated decks)

- **→ / Space** — next slide
- **←** — previous slide
- **Click slide counter** (bottom-right) — jump to any slide number
- **Swipe** — touch and mobile support

---

## Source

Maintained at [eliorsi-hash/monday-presentation-v2](https://github.com/eliorsi-hash/monday-presentation-v2).

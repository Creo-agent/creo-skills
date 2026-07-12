# monday-presentation-v2

Design-system-first HTML presentation builder with monday.com branding.

## Quick Start

Use the skill: `/monday-presentation-v2`

## Architecture

- **SKILL.md** — The skill definition (invoked via `/monday-presentation-v2`). Contains the phased workflow, inlined brand SVG, and navigation JS.
- **design-system.css** — CSS tokens, components, and 19 template classes. Inlined verbatim into every generated HTML. Supports dark (default) and light themes via `data-theme` attribute on `<html>`.
- **slide-templates.html** — Live previews of all 19 template classes and component combinations. The single source of truth for slide layouts.
- **design-system-showcase.html** — Design token and component reference page.
- **DESIGN_SYSTEM.md** — Agent reference for design-system.css: every token value, component HTML pattern, and template class.
- **icon-font.css** — `@font-face` with base64-embedded WOFF2 icon font (268 icons) + `.monday-icon` base class. Inlined FIRST into generated HTML.
- **ICON_FONT_REFERENCE.md** — Icon names, HTML entities, and semantic tags for icon selection.
- **Logos/** — monday.com wordmark SVGs (white + black variants).
- **RECIPES.md** — 5 presentation recipes (Product Launch, Team Review, Proposal, Training, Quick Update).

## Key Rules

- Generated presentations are single self-contained HTML files — zero external dependencies.
- All slides use CSS template classes (`tmpl-*`) from design-system.css — 19 available.
- All icons use the icon font: `<span class="monday-icon">&#xHHHH;</span>`. No inline SVGs for icons.
- Navigation uses class-based toggling (`slide-active`), never inline `style.display`.
- All slides lock to 16:9 aspect ratio using vmin units.
- Font: Poppins Regular (400) + SemiBold (600) only. No other weights.
- This directory is symlinked to `~/.claude/skills/monday-presentation-v2/`.

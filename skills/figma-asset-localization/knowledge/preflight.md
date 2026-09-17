# Preflight Checklist — Figma Asset Localization

Walk every item ✅ before starting a localization run. Hard gate — do not proceed if any item fails.

## Access & Auth
- [ ] monday.com API token (`.secrets/monday-main-account-token.md`) is accessible
- [ ] Figma MCP is connected (`claude mcp list` → figma: Connected). If expired, re-auth per `knowledge/figma-operations.md`
- [ ] Figma file is shared with nymeria-ai@monday.com with **Edit** access
- [ ] Figma REST API credential ("Figma API Michael") is accessible

## Board State
- [ ] Subitem has System Status = `Idle` (new run) or Review Status = `Re-run Requested` (re-run)
- [ ] Parent item has valid Figma File Key (`text_mm3ng2f6`) — not empty
- [ ] Parent item has valid Asset Frame Name (`text_mm3nbpfm`) — not empty
- [ ] Locale code in subitem `name` is one of: `de-DE`, `pt-BR`, `fr-FR`, `es-MX`, `ja-JP`

## Glossary & Translation
- [ ] Local glossary CSV exists at `glossaries/{locale}.csv` and has >0 entries
- [ ] Glossary freshness: file age <48h (warn if stale, but proceed)
- [ ] Style guide Doc ID is available for the locale (except ja-JP which has none)

## Figma State
- [ ] EN source page exists and contains the expected Asset Frame Name
- [ ] Frame node ID on source page matches Asset Frame Name (cross-check name property)
- [ ] Source page is NOT a loc page (safety — never write to source)

## Pipeline Readiness
- [ ] No orphan Claude Code processes from previous runs (`ps aux | grep claude`)
- [ ] EN screenshot cache checked (`scripts/runs/EN_{asset_name}.png`) — reuse if same asset
- [ ] `scripts/runs/` directory exists and is writable

## Re-run Only (skip for new runs)
- [ ] Feedback Notes (`long_text_mm3y8wdd`) contains valid JSON
- [ ] Original Screenshot (`file_mm3ndya6`) already exists — do NOT overwrite
- [ ] Previous loc page exists for this locale — do NOT create a new one

# Translation Rules — Figma Asset Localization

## Locales & Config

| Locale | Glossary Google Sheet ID | Style Guide Doc ID | Agent Role Descriptions | Reviewer | Text Expansion |
|---|---|---|---|---|---|
| `de-DE` | `1FUEDcQh3PAaL2fHOufqjCfb1Y1pHNQTbtJYMK5J1Cp4` | `1P9UrVZQkraTmNa5ecyFFW8ifJrfdYzxkVL9NQPbBOFo` | **keep_english** | germanisticat@gmail.com | +15-30% |
| `pt-BR` | `1FCt-Vy2fxQwTVCccAtHbE4PdksJ_qpdG-AsbN6Gcirg` | `1ggoNtfurot2JS36POKy9h6g9ghGvcvNO09OZJhD6GbI` | translate | nuritmgil@gmail.com | slightly longer |
| `fr-FR` | `1zf8uHkhof7m-x_7f5uSA8mG44N04xE5ytwRbgFQccF8` | `1Eggq0sjT1et17MuLPNDia8rRlRMmomEyLIrL3wPbWLA` | translate | ogushida@gmail.com | +15-20% |
| `es-MX` | `124N3_9D4oyeO6sm3sLJtMMhS51NhDVJETKdEvoq6ruM` | `1-ddycObbx5rfc1uherwhbem68exttncKAZYbwwgWyDY` | translate | danielanoelysegura@gmail.com | slightly longer |
| `ja-JP` | `1hAG0TsviTpKop9w50whPKYi8ydO0RWNu5dVC468zQr4` | (none) | translate | marinasaga@gmail.com | -15% (denser) |

**Locale-to-language mapping (for page naming):**
- `de-DE` → German
- `pt-BR` → Portuguese
- `fr-FR` → French
- `es-MX` → Spanish
- `ja-JP` → Japanese

**Glossary loading:** Load from local CSV files at `glossaries/{locale}.csv` (synced daily from Google Sheets). Each row maps English → target term. Format: `{en} -> {target} [Notes English] {target notes}` joined with ` | `. Drop rows where either English or target is empty. If load returns zero entries → hard error.

**Local glossary files:** `skills/figma-asset-localization/glossaries/{locale}.csv` - synced daily via `scripts/sync-glossaries.py` cron. Sync metadata in `glossaries/sync-meta.json`. If local files are stale (>48h), log a warning but still use them.

**Google Sheets access:** Sheets are shared with nymeria-ai@monday.com. OAuth token at `.secrets/google-sheets-token.json`.

---

## Translation Priority
1. **Exact glossary match** - glossary terms override everything
2. **Style guide rules** - locale-specific CTA conventions, typography, currency
3. **AI transcreation** - last resort, prefer native/punchy phrasing

## Brand Rules (all languages)
- `monday.com` - ALWAYS lowercase, NEVER translated, never capitalized at sentence start
- Product names stay English: monday CRM, monday dev, monday service, WorkForms, monday AI, Brain
- Agent CHARACTER names preserved: Alex, Anthony, Ace
- Competitor names preserved (Flowdesk, Taskly, etc.)

## Agent Role Descriptions
- `de-DE` (keep_english): "Scheduling Agent", "Performance Analyst" etc. MUST stay English
- All other locales (translate): May be naturally translated

## monday.com UI Labels (MUST translate)
The `keep_english` rule for de-DE applies ONLY to agent role descriptions. All standard monday.com UI labels MUST be translated per glossary:
- **Status indicators:** Active → Aktiv, Done → Erledigt, In progress → In Bearbeitung, Completed → Abgeschlossen
- **Column headers:** Owner → Zuständig, Status (stays same), Due date → Fälligkeitsdatum
- **View tabs:** Main table → Hauptansicht, Gantt (stays), Kanban (stays)
- **Group headers:** This month → Aktueller Monat, Next month → Nächster Monat
- **Board names:** Translate naturally (e.g. Campaign planning → Kampagnenplanung)

These are NOT product names — they are translatable UI copy. If in doubt, check the glossary.

## Unicode Line Break Preservation
Figma text nodes may use Unicode line separators (U+2028) or paragraph separators (U+2029) instead of regular `\n` for line breaks — especially in bullet lists, ⚠️ icon paragraphs, and multi-line labels. When setting translated text:
1. **Read the existing text first** and identify which break characters are used
2. **Preserve the exact break characters** — if the original uses U+2028, the translation must use U+2028 at the same positions
3. **Never replace U+2028/U+2029 with plain spaces or `\n`** — this will collapse lines or break visual formatting
4. If unsure, hex-dump the original text node content before writing

**Origin:** 2026-07-27 — Anthony DE ⚠️ icon line broke because U+2028 line separators were replaced with plain spaces.

## Font Validation (CJK + Cyrillic)
Before RU/KO/ZH: check `figma.listAvailableFontsAsync()` for Noto Sans variants. If Figtree/Poppins don't support the script, swap font family. JA fallback: Noto Sans JP.

## Per-Locale Rules
Full verbatim rules for each locale are in `references/agent-operations-manual.md` §6.8. Key highlights:

- **de-DE:** du-Form, German noun capitalization, "..." quotes, forbidden: "Stell dir vor", "sicherstellen", "ermöglichen"
- **pt-BR:** Você form, Brazilian NOT European Portuguese, forbidden: "utilizador", "telemóvel", "ecrã"
- **fr-FR:** Vouvoiement, INFINITIVE CTAs (NOT imperative), « » guillemets, thin non-breaking space before : ; ! ?
- **es-MX:** Tutear (tú/ustedes), LATAM NOT Spain vocabulary, forbidden: "ordenador", "vosotros"
- **ja-JP:** です・ます調, hiragana preferences (はじめる not 始める), no trailing period on titles/buttons, 「」quotes, half-width space between Latin and Japanese

---

## Translation LLM Prompt

The full verbatim system and user prompts are in `references/agent-operations-manual.md` §6.7-6.8. Key structure:

**System prompt components:**
1. Role (professional marketing translator / transcreator)
2. Brand rules (monday.com lowercase, product names English, agent names preserved)
3. Agent role description policy (keep_english for de-DE, translate for others)
4. Formatting preservation (no added bullets/numbering/indentation unless in source)
5. Output format (JSON only: `translations`, `glossaryDeviations`, `notes`)
6. Spatial awareness (prefer concise translations for `isSpaceConstrained` nodes)
7. Glossary usage (primary reference, report deviations with reason)
8. Per-locale rule layer (appended last)

**User prompt:** locale, asset name, text nodes to translate (grouped by translatable vs brand-only), glossary string, instructions.

**Output handling:** Strip markdown fences, parse JSON, require `translations` object, default arrays to `[]`. Verify coverage - pass through any skipped nodes unchanged.

---

## Re-run Feedback Schema (`long_text_mm3y8wdd`)
```json
{
  "label": "Translation quality | Design | Glossary",
  "english": "source EN text",
  "current": "current (wrong) localized text",
  "target": "the correction to apply",
  "reasoning": "why"
}
```

Apply by category:
- **Glossary** → treat `target` as authoritative glossary override (highest priority)
- **Translation quality** → re-translate `english`, honoring `target`/`reasoning`
- **Design** → layout/visual fix only, do NOT change translation

Also read designer hints: Review Items, Root Cause, Fix Applied, Fix Notes.

**Apply glossary/translation first, then a single layout pass - never interleave.**

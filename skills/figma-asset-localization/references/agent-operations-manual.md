# Figma Localization — Agent Operations Manual

> **Purpose:** This is the single source of truth for an AI agent that **replaces the entire n8n Figma localization pipeline**. It covers everything the current n8n flow does, for two entry points:
> - **PART A — NEW RUN**: a new subitem is created on the Figma subitem board (System Status = `Idle`).
> - **PART B — RE-RUN**: a reviewer flips Review Status to `Re-run Requested`.
>
> **Boards:** Figma **item** board `18412118203` · **subitem** board `18412118857` (one subitem per locale).
> **Figma file (Localization Agents LP):** key `usuebR1yX62QkOxSPxTFI3`.
> **Status model is split:** System Status = agent-owned · Review Status = human-owned (one exception below).
>
> This doc supersedes the operational parts of the n8n services but **aligns with and extends** `website/docs/figma-rerun-agent-contract.md`. It reproduces the rules in `website/CLAUDE.md` and the verbatim prompts extracted from the live n8n workflows.

---

## 1. Overview & Scope

The agent replaces this chain of n8n workflows (the plugin/webhook services that previously executed each stage):

| n8n workflow | ID | Role the agent now owns |
|---|---|---|
| Nymeria Figma Uploader — Monday Bridge | `MigBk6tJ55tFc8uy` | Creates parent items + per-locale subitems (`System = Idle`). **Still runs / can be kept** — it is the trigger source for a New Run. |
| Figma Localization — Translation Service | `4444GP2j0uYgK30k` | EN→target translation, glossary-first (Gemini agent). |
| Figma Localization — RPC Service | `uikyvXfK39XmofFy` | Overflow resolve (widen/rewrite/escalate) + paragraph restructure (OpenAI). |
| Figma Localization — Layout Action Planner | `dHwgC1Gd3boRx4GJ` | ActionPlan from NeighborhoodSnapshot + QA notes (Gemini). |
| Figma Localization — QA Service | `qncmfXpSfVh5ED71` | Layer 2 pixel diff + Layer 3 vision eval → confidence + terminal state (Gemini). |
| Figma Localization — Asset Complete | `g05w0hPEISOJPPmy` | Maps terminal state → Monday labels, uploads screenshots to board, gates Cloudinary, logs Postgres. |
| Figma Localization — Approval Trigger | `7WIuZsFYaoVXcxuK` | **INACTIVE (Jul 27 2026).** Was: on approval → re-export from Figma → Cloudinary upload → write URL. Now handled by the agent directly. |

**Core principle (locked):** translation and layout correction are **always separate, atomic passes**. Translate ALL text first, THEN run a single layout-correction pass. Never interleave.

**The agent processes ONE subitem (one locale) per trigger.**

---

## 2. How the System Works — End-to-End Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. REQUEST / ASSET ADDED                                                     │
│     Ops submits Figma frame(s) + target languages via the plugin/bridge.      │
│     Owner: Localization Ops (human) + Uploader workflow                        │
└───────────────────────────────┬───────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. UPLOADER CREATES SUBITEMS      (MigBk6tJ55tFc8uy)                          │
│     One parent item per frame (group = fileKey), one SUBITEM PER LOCALE.       │
│     Subitem created with  System Status = "Idle".                             │
│     Owner: Uploader workflow                                                   │
└───────────────────────────────┬───────────────────────────────────────────────┘
                                 ▼  (new subitem, System = Idle)  ── TRIGGER ──▶
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. AGENT — NEW RUN            (PART A)                                        │
│     System = Running → translate → layout pass → screenshot original+trans    │
│     → QA (L2 pixel + L3 vision) → write board.                                │
│     Owner: AGENT (this doc). Agent OWNS System Status the whole way.           │
└───────────────────────────────┬───────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. AGENT HANDS BACK                                                          │
│     System = Success | Success with notes | Editor Review Needed | Error       │
│     Review Status = "Pending Review"  (agent's ONLY allowed Review write)      │
│     + Screenshot, Original Screenshot, Figma Deep Link, QA Notes,             │
│       Layer 3 Confidence, Run Started/Completed, Execution Link                │
│     Owner: AGENT                                                              │
└───────────────────────────────┬───────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. HUMAN REVIEW (Vibe app)                                                   │
│     Reviewer sets Review Status: Approved | Needs Changes |                   │
│         Pass to Localization review | Re-run Requested                        │
│     Owner: Reviewer (human)                                                   │
└───────┬───────────────────────────────────────────────┬───────────────────────┘
        │ Re-run Requested ── TRIGGER ──▶                │ Approved
        ▼                                                ▼
┌──────────────────────────────┐          ┌─────────────────────────────────────┐
│  6. AGENT — RE-RUN  (PART B) │          │  7. PUBLISH TRACK (SEPARATE)         │
│     Read Feedback Notes JSON │          │     Approval Trigger (7WIuZsFYaoVXcxuK)│
│     apply glossary/translate/│          │     re-export frame → Cloudinary →   │
│     layout → screenshot → QA │          │     write Cloudinary URL.            │
│     → Review = Pending Review│          │     Owner: publish workflow / human. │
│     Owner: AGENT             │          │     NOT the localization agent.      │
└──────────┬───────────────────┘          └─────────────────────────────────────┘
           ▼
      back to (5) HUMAN REVIEW
```

### Stage table

| # | Stage | Trigger | Owner | Columns touched |
|---|-------|---------|-------|-----------------|
| 1 | Request / asset added | Ops submits frame + languages | Ops (human) | — (plugin payload) |
| 2 | Uploader creates subitems | Plugin `submit` webhook | Uploader `MigBk6tJ55tFc8uy` | Parent: `link_mm3npjax`, `text_mm3ng2f6`, `text_mm3nbpfm`, `color_mm3nw9me`. Subitem: `color_mm3nfga0` = `Idle` |
| 3 | **Agent — New Run** | New subitem created (`System = Idle`) | **Agent** | `color_mm3nfga0` = `Running`, `date_mm3n2gvy` |
| 4 | Agent hands back | (end of run) | **Agent** | `color_mm3nfga0` (terminal), `color_mm3nzc1r` = `Pending Review`, `file_mm3nszn1`, `file_mm3ndya6`, `link_mm3nwes`, `long_text_mm34j4w`, `long_text_mm43mr5c`, `numeric_mm3nyptd`, `date_mm3nzda6`, `link_mm34khv0` |
| 5 | Human review (Vibe app) | agent hand-back | Reviewer (human) | `color_mm3nzc1r` (Approved/Needs Changes/Pass to Localization review/Re-run Requested), `long_text_mm3y8wdd`, `dropdown_mm3yqke4`, `dropdown_mm3nejv8`, `dropdown_mm3nggk1`, `long_text_mm3n66bk`, `numeric_mm51aa70` |
| 6 | **Agent — Re-run** | `color_mm3nzc1r` = `Re-run Requested` | **Agent** | Same as stages 3–4; `color_mm3nzc1r` → `Pending Review` on success. Preserves `long_text_mm3y8wdd` |
| 7 | Publish (SEPARATE) | `color_mm3nzc1r` = `Approved` | Approval Trigger `7WIuZsFYaoVXcxuK` / human | `link_mm3nrhmp` (Cloudinary URL) |

---

## 3. Boards & Full Column Reference

Ownership legend: **[READ]** input the agent reads · **[WRITE]** agent sets during/after a run · **[NEVER]** agent must not touch.

### Subitem board `18412118857`

| Column | ID | Type | Ownership | Notes |
|---|---|---|---|---|
| Name | `name` | name | [READ] | Locale, e.g. `de-DE`. (Uploader names subitem by `langCode`.) |
| Item Name | `text_mm52bbyt` | text | [READ] | Asset name |
| **System Status** | `color_mm3nfga0` | status | **[WRITE]** | Agent-owned status column — labels below |
| Layer 3 Confidence | `numeric_mm3nyptd` | numbers | **[WRITE]** | Machine QA confidence 0.0–1.0 (calibrated) |
| QA Notes | `long_text_mm34j4w` | long_text | **[WRITE]** | QA reasoning for this run |
| Review Items | `long_text_mm43mr5c` | long_text | **[WRITE]** | AI-summarized actionable bullets |
| **Review Status** | `color_mm3nzc1r` | status | **[WRITE — "Pending Review" ONLY]** | Human-owned; agent's only allowed value is `Pending Review` |
| Feedback Type | `dropdown_mm3yqke4` | dropdown | [READ] (+ optional clear) | Category hint; may be cleared after consuming |
| **Feedback Notes** | `long_text_mm3y8wdd` | long_text | **[READ]** | JSON feedback to apply (re-run input). **Preserve as history; do not delete.** |
| Screenshot | `file_mm3nszn1` | file | **[WRITE]** | New **post-translation localized** PNG |
| Original Screenshot | `file_mm3ndya6` | file | **[WRITE on New Run / NEVER overwrite on Re-run]** | **Pre-translation EN** reference. On a New Run the agent uploads it once; on a Re-run treat as [NEVER] (do not overwrite the EN reference) |
| Figma Deep Link | `link_mm3nwes` | link | **[WRITE]** | Frame deep link (update if frame changed) |
| Cloudinary URL | `link_mm3nrhmp` | link | **[WRITE on Approved]** | Was owned by Approval Trigger (now inactive, Jul 27 2026). Agent writes after uploading approved asset to Cloudinary. Use folder `generators/localized/{locale}/{asset-name}` with metadata (figma_link, description, language, upload_time). |
| Localized Images | `file_mm343fyb` | file | [WRITE opt] | Legacy image column; optional |
| Execution Link | `link_mm34khv0` | link | **[WRITE]** | This run's execution/observation URL |
| Run Started | `date_mm3n2gvy` | date | **[WRITE]** | Set when the run starts |
| Run Completed | `date_mm3nzda6` | date | **[WRITE]** | Set on terminal state |
| Root Cause | `dropdown_mm3nejv8` | dropdown | [READ] | Designer hint on what was wrong |
| Fix Applied | `dropdown_mm3nggk1` | dropdown | [READ] | Designer hint on the fix |
| Fix Notes | `long_text_mm3n66bk` | long_text | [READ] | Designer free-text |
| Fix Duration | `numeric_mm3nxeg9` | numbers | [READ] | Minutes to fix |
| Reviewer | `text_mm45yjpc` | text | **[WRITE]** | Agent **auto-assigns by locale** on the New Run from the fixed map: `fr-FR`→ogushida@gmail.com · `de-DE`→germanisticat@gmail.com · `pt-BR`→nuritmgil@gmail.com · `es-MX`→danielanoelysegura@gmail.com · `ja-JP`→marinasaga@gmail.com (any other → empty). |
| Localization Score | `numeric_mm51aa70` | numbers | **[NEVER]** | Human 0–10 score |
| People | `multiple_person_mm52qyc0` | people | **[NEVER]** | Assignment column |

> No Version counter column on the Figma subitem board (unlike the image board).

### Parent item board `18412118203` — read-only inputs

| Column | ID | Type | Use |
|---|---|---|---|
| Figma File | `link_mm3npjax` | link | Source Figma file URL |
| Figma File Key | `text_mm3ng2f6` | text | File key for Figma API calls |
| Asset Frame Name | `text_mm3nbpfm` | text | Exact frame name in Figma |
| Asset Type | `color_mm3nw9me` | status | `banner` / `landing-page` (rule merging) |
| Cloudinary Folder | `text_mm40409q` | text | Upload path prefix (publish track) |
| Original images | `file_mm34fbvw` | file | Source assets |

Per-locale trigger columns on the parent (used by the older orchestrator; informational): PT-BR `color_mm34s3d9`, FR `color_mm342qtw`, ES `color_mm34gt92`, JA `color_mm347vas`, JP-JA `color_mm34m5zp`, DE `color_mm34nrem`.

**All parent columns are [READ] only for the agent.**

---

## 4. Status Model & Exact Labels

Use these strings **verbatim**. Include `create_labels_if_missing: true` on mutations as a safety net.

**System Status** (`color_mm3nfga0`) — agent-owned:
`Idle` · `Running` · `Success` · `Success with notes` · `Editor Review Needed` · `Error` · `Failed` · `Approved`

- Uploader sets initial **`Idle`**.
- Agent sets **`Running`** at start, then exactly one terminal:
  - **`Success`** — QA passed, high confidence, Layer 1 clean.
  - **`Success with notes`** — QA passed, high confidence, minor Layer 1 notes.
  - **`Editor Review Needed`** — medium/low confidence, hard-fail, or collision — needs a designer.
  - **`Error`** — pipeline/Layer 2 catastrophic failure.
- Do NOT use `Approved`/`Failed` (reserved/legacy) unless explicitly instructed.

Terminal-state → label map (from `Map Terminal State`, `g05w0hPEISOJPPmy`):
```
success             → Success
success-with-notes  → Success with notes
editor-review-needed→ Editor Review Needed
pipeline-error      → Error
```

**Review Status** (`color_mm3nzc1r`) — human-owned:
`Pending Review` · `In Review` · `Pass to Localization review` · `Needs Changes` · `Re-run Requested` · `Approved`

- Agent **consumes** `Re-run Requested` (trigger) and, on success, sets **`Pending Review`** (only when terminal ∈ {Success, Success with notes, Editor Review Needed}).
- Agent must **NEVER** write `In Review`, `Pass to Localization review`, `Needs Changes`, `Approved`, or re-set `Re-run Requested`.

---

## 5. Locales & Per-Locale Config

From `Locale Config` and `Locale Rules` (`4444GP2j0uYgK30k`) and the Asset Complete reviewer map (`g05w0hPEISOJPPmy`).

| Locale | Glossary Google Sheet ID | Target term col | Style-guide Doc ID | Agent-role descriptions | Reviewer (legacy map) | Text expansion |
|---|---|---|---|---|---|---|
| `de-DE` | `1FUEDcQh3PAaL2fHOufqjCfb1Y1pHNQTbtJYMK5J1Cp4` | Term German / Notes German | `1P9UrVZQkraTmNa5ecyFFW8ifJrfdYzxkVL9NQPbBOFo` | **keep_english** | germanisticat@gmail.com | +15–30% (widen ~15%) |
| `pt-BR` | `1FCt-Vy2fxQwTVCccAtHbE4PdksJ_qpdG-AsbN6Gcirg` | Term Portuguese / Notes Portuguese | `1ggoNtfurot2JS36POKy9h6g9ghGvcvNO09OZJhD6GbI` | translate | nuritmgil@gmail.com | slightly longer |
| `fr-FR` | `1zf8uHkhof7m-x_7f5uSA8mG44N04xE5ytwRbgFQccF8` | Term French / Notes French | `1Eggq0sjT1et17MuLPNDia8rRlRMmomEyLIrL3wPbWLA` | translate | ogushida@gmail.com | +15–20% |
| `es-MX` | `124N3_9D4oyeO6sm3sLJtMMhS51NhDVJETKdEvoq6ruM` | Term Spanish / Notes Spanish | `1-ddycObbx5rfc1uherwhbem68exttncKAZYbwwgWyDY` | translate | danielanoelysegura@gmail.com | slightly longer |
| `ja-JP` | `1hAG0TsviTpKop9w50whPKYi8ydO0RWNu5dVC468zQr4` | Term Japanese / Notes Japanese | (none) | translate | marinasaga@gmail.com | −15% (denser, shorter) |

Additional locales proven on the Figma LP (glossary files were POC-era, now in `website/glossaries/_archive/`; canonical is Google Sheets): PT-BR, IT, NL, SV, PL, TR done; **RU, KO, ZH pending font validation** (need Noto Sans Cyrillic / KR / SC).

**Text-expansion behavior (from `website/CLAUDE.md`):**

| Language | vs English | Action |
|----------|-----------|--------|
| IT, PL, TR, NL, RU | +15–30% longer | Proactively widen containers ~15% |
| SV | +10–15% longer | Minor widening may be needed |
| KO | −10–20% shorter | May need to narrow containers |
| ZH | −30–50% shorter | Significant narrowing likely |
| JA | −15% shorter | Compact phrasing; denser characters |

**Glossary loading:** load the full sheet at run time. Each row maps English → target term. Format each entry as
`{en} -> {target} [Notes English] {target notes}` joined with ` | `. Drop rows where either English or target is empty. If the load returns zero entries, that is a hard error (bad credentials / doc ID).

**Glossary files:** the runner never reads glossary files from disk — the Google Sheet is canonical and passed inline. `website/glossaries/_archive/` holds frozen POC-era per-locale files (pt-br, it-it, nl-nl, sv-se, pl-pl, tr-tr) for historical reference only.

---

## 6. Translation Rules

### 6.1 Workflow (from `website/CLAUDE.md`)

1. **Duplicate** the English page → rename to `{Language} ({CODE}) AI` (e.g. `German (de-DE) AI`).
2. **Extract** all visible, in-bounds text nodes via `use_figma`.
3. **Translate** using glossary-first approach (glossary terms override AI).
4. **Fix layout** — a SINGLE atomic layout-correction pass AFTER all translation.
5. **Visual QA** — screenshot every asset and compare against original.

### 6.2 Critical: separate translation from layout

NEVER mix text changes with layout fixes. Translate ALL text first, THEN run layout correction. Layout fixes assume final text is in place — interleaving causes position drift.

### 6.3 Glossary-first priority

1. Exact match from the glossary (Google Sheet / `website/glossaries/{lang}`).
2. Style-guide rules from the glossary header / locale rules.
3. AI translation (last resort).

### 6.4 Brand rules (all languages)

- `monday.com` — always lowercase, never translated, never capitalized at sentence start.
- Product names stay English: monday CRM, monday dev, monday service, WorkForms, monday AI, Brain.
  - **Exception:** When a product term is used as a generic UI label (e.g. "Brain" as a tab name describing agent capabilities, not the monday Brain product), translate it to the target language.
- Agent CHARACTER names preserved as-is: Alex, Anthony, Ace.
- Competitor names preserved (Flowdesk, Taskly, etc.).

### 6.5 Font validation (CJK + Cyrillic)

Before RU/KO/ZH:
```js
const fonts = await figma.listAvailableFontsAsync();
// Check for: Noto Sans KR, Noto Sans SC, Noto Sans (Cyrillic)
```
If Figtree/Poppins don't support the script, swap font family on the translated nodes. JA fallback: Noto Sans JP.

### 6.6 Asset-specific fixes

**Activity Log (`anthony-activity-log`) — mandatory 3-step fix** (0 component instances, hand-drawn):
1. Add 16px `itemSpacing` between columns (Trigger/Description/Status).
2. Widen Trigger column +50px, Description column +60px.
3. Widen white card to contain Status chips, center card in asset frame (60px padding).
Then verify: `card.x = (asset.width - card.width) / 2`.

**Knowledge Access (`anthony-knowledge-access`) — bullet formatting** (insights text node):
- Line 1: UNORDERED list, indentation 1 (bulleted)
- Lines 2–3: NONE list, indentation 2, leading 4 spaces (⚠️ sub-items)
- Line 4: UNORDERED list, indentation 1 (bulleted)
- Proactively widen text container +30px.

### 6.7 Translation LLM prompt (VERBATIM — `Build Prompt`, `4444GP2j0uYgK30k`)

Model: `Google Gemini Chat Model` (Gemini). The system prompt = `basePromptWithAgent` + injected locale rules layer (live-fetched Google Doc style guide if >100 chars, else the baked `localeRules` from §6.8).

**System prompt (`basePrompt` + agent-description rule + formatting/output/spatial/glossary blocks):**
```
You are a professional marketing translator specializing in SaaS product copy. Your task is to translate text nodes from Figma design assets.

## Role
You are a transcreator — not a literal translator. Your goal is to produce text that sounds native, punchy, and on-brand in the target language while preserving the original meaning and marketing intent.

## Brand Rules
- monday.com — ALWAYS lowercase, NEVER translated, NEVER capitalized at sentence start
- Product names stay English: monday CRM, monday dev, monday service, WorkForms, monday AI, Brain
  - **Exception:** When a product term is used as a generic UI label (e.g. "Brain" as a tab name describing agent capabilities), translate it.
- Agent CHARACTER names preserved as-is: Alex, Anthony, Ace
- Competitor names preserved
```
Then ONE of these two lines (per `agentDescriptionPolicy`):
```
- Agent ROLE DESCRIPTIONS (e.g., "Scheduling Agent", "Performance Analyst", "Creative Assets agent") MUST remain in English — do NOT translate these.
```
(policy = `keep_english`, i.e. de-DE) OR
```
- Agent role descriptions (e.g., "Scheduling Agent") may be naturally translated to the target language.
```
(policy = `translate`, all other locales). Then:
```
## Formatting Preservation
Do NOT add formatting that was not in the source text:
- Do not add bullet points (•, -, *, ▸) unless the source has them
- Do not add numbering (1., 2.) unless the source has it
- Do not add indentation spaces unless the source has them
- Keep the exact same number of lines (\n characters) as the source
Bullets and list styles are handled by Figma paragraph settings, not text characters.

## Output Format
Return ONLY valid JSON. No markdown code fences, no explanatory text.
The JSON must contain:
- translations: Record mapping nodeId → translated string
- glossaryDeviations: Array of objects with term, glossaryTranslation, used, reason
- notes: Array of strings

## Spatial Awareness
Some text nodes have an isSpaceConstrained: true flag and a containerWidth value. For these nodes:
- Prefer CONCISE translations that stay close to the original character count
- Use shorter synonyms, abbreviations, or restructured phrasing when possible WITHOUT losing meaning
- If a concise translation would sacrifice clarity or meaning, use the full natural translation anyway — layout fixes will handle it downstream
- Never truncate, abbreviate to the point of confusion, or drop important words just to save space
- Example: "Define key features" (19 chars) → prefer "Funktionen definieren" (21 chars) over "Wichtigste Funktionen definieren" (33 chars) — both are correct but the shorter one preserves spatial harmony

## Glossary Usage
1. The glossary is your PRIMARY reference — always prefer glossary translations
2. If you deviate, report it in glossaryDeviations with a non-empty reason
3. Partial glossary matches count
```
Then the locale-specific rules layer (§6.8) is appended.

**User prompt (VERBATIM):**
```
You are translating text nodes from a monday.com Figma asset from {sourceLocale} to {locale}.

Asset: {assetName}

## TEXT NODES TO TRANSLATE
{JSON of translatable nodes (isBrand=false)}

## BRAND-ONLY NODES (return unchanged)
{JSON of brand nodes (isBrand=true)}

## GLOSSARY ({glossaryTermCount} terms)
{glossaryString}

## INSTRUCTIONS
1. Read ALL nodes first for context
2. Translate each node's text to natural, fluent {locale}
3. Use glossary terms. Report deviations.
4. Return JSON only with translations, glossaryDeviations, notes
```

**Output handling:** strip markdown fences; parse JSON; require `translations` object; default `glossaryDeviations`/`notes` to `[]`. **Verify Coverage:** any translatable node the LLM skipped gets its source text passed through unchanged, and a note is appended listing the skipped nodeIds.

### 6.8 Per-locale rule layers (VERBATIM — `Locale Rules`, `4444GP2j0uYgK30k`)

<details><summary><b>de-DE</b></summary>

```
## LOCALE-SPECIFIC RULES: German (de-DE)

### VOICE & TONE
- du-Form: Always use informal "du" (not "Sie")
- German capitalization: All nouns capitalized per Rechtschreibung
- Quotation marks: „...“ (opening at bottom, closing at top)
- Keep it punchy: short, impactful headlines
- Active voice preferred

### CTA CONVENTIONS
- Marketing CTAs: imperative du-form ("Jetzt starten", "Mehr erfahren")
- UI/screenshot labels: infinitive acceptable ("Workflow erstellen")

### FORBIDDEN PHRASES
Never use: "Stell dir vor", "sicherstellen", "ermöglichen", "Hier kommt X ins Spiel", "Funktionalität", "zum Einsatz bringen", "Mehrwert"

### NUMBER & CURRENCY
- Decimal: comma (1.234,56) | Thousands: period (1.000)
- Currency: EUR after number (19,99 €) | Dates: DD.MM.YYYY | Time: 24h

### BRAND SPECIFICS
- monday.com = feminine as platform, products masculine ("der monday CRM")
- Never apostrophe-s: "die Features von monday.com"
- "monday AI" stays English (German market convention)
```
</details>

<details><summary><b>pt-BR</b></summary>

```
## LOCALE-SPECIFIC RULES: Brazilian Portuguese (pt-BR)

### VOICE & TONE
- Você form: informal, 2nd person singular when addressing reader
- Brazilian Portuguese — NEVER European Portuguese
- Conversational, direct, friendly
- Keep it punchy: same impact with fewer words

### CTA CONVENTIONS
- Marketing CTAs: imperative form ("Comece agora", "Saiba mais", "Teste grátis")
- UI/screenshot labels: infinitive acceptable ("Criar workflow")

### FORBIDDEN — European Portuguese markers
Never use: "utilizador" (use "usuário"), "telemóvel" (use "celular"), "ecrã" (use "tela"), "ficheiro" (use "arquivo")

### NUMBER & CURRENCY
- Decimal: comma (1.234,56) | Thousands: period (1.000)
- Currency: BRL — R$ before number (R$ 19,90) | Dates: DD/MM/YYYY | Time: 24h

### BRAND SPECIFICS
- monday.com always lowercase
- "monday AI" → "IA da monday" (AI → IA in Portuguese)
- Product names stay English: monday CRM, monday dev, WorkForms, Brain (exception: translate when used as generic UI label, e.g. "Brain" as tab name)
- Agent names stay English: Alex, Anthony, Ace

### TRANSCREATION NOTES
- Contextual compression valid: dropping contextually-established qualifiers is localization
- Idiomatic translations preferred: "run" (casual) → "fluir" or "funcionar"
- If two phrasings are equally natural, pick the shorter one
```
</details>

<details><summary><b>fr-FR</b></summary>

```
## LOCALE-SPECIFIC RULES: French (fr-FR)

### VOICE & TONE
- Vouvoiement (vous form) when addressing the reader
- Professional but warm — not stiff bureaucratic French
- Subjects and headlines demand aggressive transcreation — never literal
- Keep it punchy: compress, don't expand

### CTA CONVENTIONS
- Marketing CTAs: INFINITIVE form — NOT imperative
- Examples: "Découvrir nos agents", "Commencer maintenant", "Réserver maintenant"
- NEVER use imperative for marketing CTAs (confirmed by native reviewer)
- UI/screenshot labels: infinitive ("Connecter des boards", "Créer un workflow")

### FORBIDDEN PHRASES
Never translate English marketing idioms literally. Transcreate aggressively.

### NUMBER & CURRENCY
- Decimal: comma (1 234,56) | Thousands: non-breaking space (1 000)
- Currency: EUR — € after number with space (19,90 €) | Dates: DD/MM/YYYY | Time: 24h

### BRAND SPECIFICS
- monday.com always lowercase
- "monday AI" → "l'IA de monday" or "IA monday" (AI → IA in French)
- "Ops" → "Opérations"
- "place" (workspace context) → "espace"
- "rollout" → "déploiement" (never "lancement" in marketing contexts)
- Product names stay English: monday CRM, monday dev, WorkForms, Brain (exception: translate when used as generic UI label, e.g. "Brain" as tab name)
- Agent names stay English: Alex, Anthony, Ace

### PUNCTUATION
- Thin non-breaking space before : ; ! ?
- Quotation marks: « ... » (guillemets with non-breaking space inside)
```
</details>

<details><summary><b>es-MX</b></summary>

```
## LOCALE-SPECIFIC RULES: International Spanish — LATAM (es-MX)

### VOICE & TONE
- Tutear: always tú/ustedes — NEVER usted or vosotros
- LATAM Spanish — avoid Spain-specific vocabulary
- Direct, friendly, human — not overly formal
- Conversational: like talking to a tech-savvy colleague

### CTA CONVENTIONS
- Marketing CTAs: imperative form ("Empieza ahora", "Descubre más", "Prueba gratis")
- Single exception: "Get Started" → "Empezar ahora" (infinitive)
- UI/screenshot labels: infinitive acceptable ("Crear workflow")

### FORBIDDEN — Spain-specific vocabulary
Never use: "ordenador" (→ "computadora"), "móvil" (→ "celular"), "vosotros" (→ "ustedes"), Iberian decimal-comma for large numbers

### NUMBER & CURRENCY
- Decimal: period (1,000.50) | Thousands: comma (1,000)
- Currency: USD stays $ unless Mexico-specific → MXN | Dates: DD/MM/YYYY | Time: 24h

### BRAND SPECIFICS
- monday.com always lowercase — NEVER bare "monday" without ".com"
- "monday AI" → "IA de monday.com" (AI → IA in Spanish)
- Product names stay English: monday CRM, monday dev, WorkForms, Brain (exception: translate when used as generic UI label, e.g. "Brain" as tab name)
- Agent names stay English: Alex, Anthony, Ace

### TRANSCREATION NOTES
- Regional neutrality: avoid country-specific slang; aim for pan-LATAM clarity
- AI framings: avoid "robot", "machine" — use "inteligencia artificial", "automatización"
```
</details>

<details><summary><b>ja-JP</b></summary>

```
## LOCALE-SPECIFIC RULES: Japanese (ja-JP)

### VOICE & TONE
- です・ます調 (polite form). NEVER plain form (だ・である). Avoid excessive 敬語.
- Light, friendly, direct, approachable. Drop gratuitous `!`.
- Pronoun minimization: omit あなた, 私たち. Rephrase around task or benefit.

### CTA CONVENTIONS
- Marketing CTAs: plain-form verbs (今すぐはじめる, 詳細を見る, 無料で試してみる)
- NEVER 体言止め on email/marketing CTAs (NOT 今すぐ開始)
- UI/screenshot labels: 体言止め acceptable (設定, ボード作成)

### HIRAGANA PREFERENCES
Use hiragana over kanji: はじめる (not 始める), すべて (not 全て), さまざまな (not 様々な), たとえば (not 例えば), など (not 等), または (not 又は), ください (not 下さい)

### FORBIDDEN
Never use: あなた/私たち (pronoun sprinkling), AI の魔法, ボット (unless EN says bots), 働き方の未来, AI の時代

### NUMBER & CURRENCY
- Thousands: half-width comma (3,000ページ) | Magnitude: 万/億
- Currency: casual marketing → JPY (~100 JPY/USD, e.g. 6,500万円). UI pricing screenshots → keep source USD.
- No trailing period on titles/headings/buttons/labels

### TYPOGRAPHY
- 「 」 quotation marks (NOT ".."). 。 periods. 、 commas. Full-width ％. Full-width 〜 for ranges.
- Half-width space between Latin alphanumerics and Japanese (monday.com のプラットフォーム)

### BRAND SPECIFICS
- monday.com always lowercase m, always include .com. Half-width space between brand and Japanese.
- Products stay English: monday.com, monday sidekick, monday vibe, monday dev, monday CRM, monday service, Work OS, Canvas, WorkForms, monday workdocs
- Agent names: Alex, Anthony, Ace — keep English
- monday AI → AI (keep in context, no translation)

### TEXT LENGTH
- Japanese is SHORTER than English (−15%). Characters are denser — text may be fewer characters but similar visual weight.
- For constrained containers: prefer compact phrasing, 体言止め on labels (not buttons).

### FONT
- Fallback font for CJK: Noto Sans JP
```
</details>

---

## 7. Layout-Fix Rules

Layout is a **single atomic pass AFTER all translation**. Two mechanisms exist in the pipeline:

### 7.1 RPC Service — overflow resolution & paragraph restructure (`uikyvXfK39XmofFy`, OpenAI)

Routes on `op`: `resolve_overflow` or `restructure_paragraphs`.

**Overflow system prompt (VERBATIM — `Overflow Claude Call`):**
```
You are deciding how to resolve text overflow in a Figma asset being localized.

Three actions available:
1. WIDEN — increase container width. Only if maxAvailableWidth > currentWidth.
2. REWRITE — shorter translation preserving meaning. Must fit within currentWidth.
3. ESCALATE — neither is safe. Designer must fix.

Constraints:
- Never reduce font size.
- Never truncate.
- Rewrites use the glossary.
- If shortening loses meaning, escalate.

Return JSON only:
{"action": "widen" | "rewrite" | "escalate", "newWidth": number, "rewrittenText": string, "reasoning": "one-sentence"}
```
User message: `Node: {nodeId}\nAsset: {assetName}\nLocale: {locale}\nCurrent width: {currentWidth}px\nMax available: {maxAvailableWidth}px\nText: "{textContent}"` + optional filtered glossary block. (Glossary is pre-filtered to only terms whose English appears in the node text, longest-first.)

**Restructure system prompt (VERBATIM — `Restructure Claude Call`):**
```
You are restructuring a translated text node to match a target paragraph structure in a Figma asset.

Reorganize content to fit the target structure while preserving:
- All information
- Glossary fidelity
- Natural reading flow

listType must be: UNORDERED, ORDERED, or NONE

For NONE-type paragraphs needing visual indentation, include leading spaces (2 per indent level).

Return JSON only:
{"restructuredText": "full text with \n separators", "paragraphs": [{"text": "...", "listType": "UNORDERED", "indentation": 1}], "reasoning": "one-sentence"}
```
User message: `Locale: {locale}\nReason: {reason}\n\nCurrent text:\n"""\n{currentText}\n"""\n\nTarget structure ({n} paragraphs):\n{JSON}`. Output must match the requested paragraph count exactly or it errors.

### 7.2 Layout Action Planner (`dHwgC1Gd3boRx4GJ`, Gemini)

Consumes `neighborhoodSnapshots` + `qaNotes` + `assetRules` + `attemptNumber` (0–2). Returns an ActionPlan.

**System prompt (VERBATIM — `Build Planner Prompt`):**
```
You are an experienced monday.com brand designer reviewing localization QA feedback and proposing layout adjustments.

CONTEXT: The pipeline translated a Figma asset from English to a target locale. QA detected layout issues. Your job: propose specific, minimal layout adjustments.

You are NOT rewriting translations. Text stays as-is.

PRINCIPLES:
1. Minimal disturbance. Move/resize only what's necessary.
2. Use available slack from NeighborhoodSnapshot parent/sibling positions.
3. Coordinate when needed. Include all affected nodes.
4. Escalate honestly if fix requires opinionated judgment.
5. Respect assetRules constraints.

INTERACTIVE (isInteractive=true): buttons, chips, links. Don't move off-screen. Prefer widening containers.
DECORATIVE (isDecorative=true): illustrations, dividers. Can reposition but check hierarchy.

PLAN TYPES: "single" (one node), "coordinated" (multiple), "escalate" (needs designer).
ACTION TYPES: resize {targetNodeId, widthDelta, heightDelta, reasoning}, reposition {targetNodeId, xDelta, yDelta, reasoning}, redistribute {parentNodeId, strategy, reasoning}, no_action_possible {reasoning}.

For each failed node: What's the problem? What slack is available? Would fix affect neighbors? Mechanical or judgmental?

Output a single ActionPlan JSON with: planType, actions[], affectsNeighbors, reasoning, escalationReason (if escalate), confidenceInPlan (0-1).
```
User message: `ASSET: {assetName} | LOCALE: {locale} | ATTEMPT: {attemptNumber}/2` + QA notes + neighborhood snapshots + asset rules; "If attempt > 0 and previous fixes didn't resolve, consider more aggressive approach or escalate."

**Parse/validation:** planType ∈ {single, coordinated, escalate}; `confidenceInPlan` 0–1; action types normalized (Gemini emits `actionType`/`action`/`type` inconsistently) and validated ∈ {resize, reposition, redistribute, no_action_possible}; resize/reposition require `targetNodeId`, redistribute requires `parentNodeId`. Max 3 attempts (0,1,2), then escalate.

---

## 8. Visual QA

### 8.1 How QA scores (`qncmfXpSfVh5ED71`)

**Layer 2 — pixel diff (deterministic):** compares base64 of original vs translated screenshot. Size-ratio heuristic: if translated buffer is <0.3× or >3.0× the original → `overallDiffPct = 80` (catastrophic). Else `overallDiffPct = |1 - sizeRatio| * 100`. Status `fail` if `overallDiffPct > 60` (catastrophic threshold), else `pass`. On Layer 2 fail → respond early, no Layer 3.

**Layer 3 — vision eval (Gemini, two images):** original (EN) + translated. Six PASS/FAIL checks + layout integrity, returns `status`, `confidence` (0–1), `score` (0–10), `checks{}`, `humanReviewRecommended`, `reasoning`.

**Confidence calibration (`Aggregate Verdict`):** raw confidence capped by worst failing check —
`textCompleteness 0.60, brandRules 0.50, strayEnglish 0.55, visualHierarchy 0.70, calqueDetection 0.80, glossaryFidelity 0.75`. A text-scan fallback (only when ≥1 check failed) applies severity caps for overlap/overflow/critical/untranslated/brand-violation patterns. Stack penalty `(failCount-1)*0.05`. Floor 0.30.

**Terminal-state gating:**
- Layer 2 fail → `pipeline-error`.
- Hard fails (regardless of confidence): `brandRules` fail → `editor-review-needed` (brand_rule_violation); `strayEnglish` fail → `editor-review-needed` (untranslated_content); `textCompleteness` fail → `editor-review-needed` (layout_collision_or_overflow). (calqueDetection is informational only — glossary is authoritative, never a hard fail.)
- Layer 1 sibling collision → `editor-review-needed`.
- Layer 3 missing → `pipeline-error`.
- Else by calibrated confidence: `≥0.85 && layer1Clean` → **success**; `≥0.85 && !layer1Clean` → **success-with-notes**; `≥0.70` → **editor-review-needed** (medium); `<0.70` → **editor-review-needed** (low).

### 8.2 Layer 3 vision prompt (VERBATIM — `Layer 3 Vision Gemini`, `qncmfXpSfVh5ED71`)

**System message:**
```
You are a Senior Linguistic Quality Assurance specialist evaluating a localized Figma asset.

You will receive TWO images:
1. Original (English) — the source asset before translation
2. Translated (target locale) — the asset after localization

## CRITICAL COMPARISON RULE

Only flag issues that are NEW in the translated version. If truncation, clipping, or overflow exists in BOTH the original AND translated, it is intentional design — do NOT penalize it.

Examples to IGNORE (pre-existing in original):
- Column headers clipped at right edge of a board view
- Text partially hidden behind floating cards or avatar badges
- Content flowing off the visible frame boundary

## GLOSSARY AND BRAND AUTHORITY

The translation was produced using an approved glossary and brand guidelines. These are AUTHORITATIVE. Do NOT flag glossary-prescribed terms as errors, even if they seem grammatically unusual. If you notice a term that looks wrong but could be a glossary entry, mark calqueDetection as PASS and note it as possible glossary term.

Only flag calqueDetection as FAIL for translations that are clearly unnatural AND could not plausibly be a glossary/brand choice.

## Evaluation Criteria (each PASS or FAIL)

1. visualHierarchy: Headlines dominant, body subordinate, CTAs prominent
2. calqueDetection: Does translation read naturally? (PASS if follows glossary/brand terms, even if unusual)
3. glossaryFidelity: Key brand terms correct in output
4. brandRules: monday.com lowercase, agent CHARACTER names (Alex, Anthony, Ace) always untranslated, product names English. For agent ROLE descriptions (e.g., 'Scheduling Agent', 'Performance Analyst'): check the locale — if de-DE they MUST stay English (flag as fail if translated); for other locales (pt-BR, fr-FR, es-MX) they MAY be translated (do NOT flag as fail)
5. strayEnglish: All translatable TEXT NODES translated (except brand allow-list). IMPORTANT: English visible in RASTERIZED IMAGES, icons, or screenshots-within-screenshots is OUTSIDE pipeline scope — the pipeline can only translate text nodes listed above. Do NOT fail strayEnglish for image-based English. Instead mark as PASS and note which image elements would need designer-provided localized assets.
6. textCompleteness: No NEW text cut off, hidden, or overflowing compared to original

## LAYOUT INTEGRITY

Compare translated vs original. Flag only NEW layout failures:
1. Text-on-text overlap not present in original
2. Text-on-interactive overlap not present in original
3. Container overflow where original text fit cleanly
4. Hierarchy collision where elements were separate in original

If issue is NEW: fail textCompleteness, reduce confidence (0.5-0.7)
If issue exists in BOTH: do NOT penalize, note as pre-existing

Return JSON only:
{"status": "pass"|"fail", "confidence": 0.0-1.0, "score": 0-10, "checks": {"visualHierarchy": {"status": "pass"|"fail", "note": ""}, ...}, "humanReviewRecommended": boolean, "reasoning": "summary"}
```
**User message:**
```
Asset: {assetName} | Locale: {locale}

IMAGE 1 (Original English): [attached as first image]
IMAGE 2 (Translated {locale}): [attached as second image]

Layer 1 structural checks: {PASSED | N nodes flagged (overflow/collision)}
Layer 2 pixel diff: {overallDiffPct}%
Translated text node IDs (pipeline scope): {JSON, truncated to 500 chars}

Compare the two images. Only flag issues that are NEW in the translated version. If clipping/truncation exists in the original too, it is intentional — do not penalize.

Return JSON with: status (pass/fail), confidence (0-1), score (0-10), checks object, humanReviewRecommended (boolean), reasoning.
```

### 8.3 Visual QA checklist (from `website/CLAUDE.md`)

Before reporting done, screenshot each asset and verify:
- [ ] White card centered in orange frame
- [ ] Status chips inside white card (not overflowing)
- [ ] No column text overlap in activity log
- [ ] Card doesn't overflow asset frame
- [ ] Knowledge-access ⚠️ lines indented with 4 spaces + indent level 2
- [ ] All visible text translated (no stray English except brands)

### 8.4 Review Items summarizer (from `g05w0hPEISOJPPmy`)

QA notes are summarized into 2–4 action bullets for `Review Items` (`long_text_mm43mr5c`). Shortcuts: `Success` (no auto-fix) → `• No issues found — ready for upload`; `Success with notes` (no fail) → `• Passed with minor notes — review at your discretion`; else a Gemini Flash call turns QA notes into bullets:
```
You are a QA summarizer. Read the QA notes and produce EXACTLY 2-4 bullet points.

FORMAT:
• [Action verb] [specific issue] [where]

Rules: Start each with •. Use verbs: Check, Fix, Verify, Note. Max 15 words each. No jargon.

Asset: {assetName} | Locale: {locale} | Status: {status}

QA Notes:
{qaNotes (trimmed to 1500 chars)}

Bullet summary:
```

---

## 9. Figma Operations

The plugin/agent drives Figma directly. Operations, in pipeline order:

1. **Duplicate page** — copy the English source page, rename to `{Language} ({CODE}) AI` (e.g. `German (de-DE) AI`).
2. **Extract text nodes** — `use_figma`: collect all visible, in-bounds text nodes; flag `isBrand`, `isSpaceConstrained` + `containerWidth`, `isInteractive`, `isDecorative`.
3. **Set text** — apply `translations{nodeId → string}` to nodes. Preserve line count / formatting (bullets & lists via Figma paragraph settings, not text chars).
4. **Font validation/swap** — before RU/KO/ZH check `figma.listAvailableFontsAsync()`; swap to Noto Sans (KR/SC/JP/Cyrillic) if Figtree/Poppins lack the script.
5. **Layout pass (single, atomic)** — apply RPC overflow resolutions (widen/rewrite) and Layout Action Planner ActionPlan (resize/reposition/redistribute); asset-specific fixes (§6.6).
6. **Screenshot / export:**
   - **Original (EN)** screenshot BEFORE translation → board col **`file_mm3ndya6`** (Original Screenshot).
   - **Translated** screenshot AFTER layout → board col **`file_mm3nszn1`** (Screenshot).
   - QA uses both as base64 (`originalScreenshot`, `translatedScreenshot`).
   - Approval/publish re-export uses the Figma REST API:
     `GET https://api.figma.com/v1/images/{fileKey}?ids={nodeId}&format=png&scale=2` (HTTP Header Auth, credential "Figma API Michael" `WkMz2bZ8cx2lzgfJ`). `nodeId` is parsed from the Deep Link `node-id=([0-9]+-[0-9]+)`.
7. **Deep link** — build/read the Figma frame URL (`?node-id=...`) → board col **`link_mm3nwes`** (label "Open in Figma").

---

## PART A — NEW RUN

### Trigger
**Fires on a new subitem created on board `18412118857` with System Status = `Idle`.** The Uploader (`MigBk6tJ55tFc8uy`) creates one parent item per frame (group = fileKey, columns `link_mm3npjax`/`text_mm3ng2f6`/`text_mm3nbpfm`/`color_mm3nw9me`) and one subitem per locale, each with `{color_mm3nfga0: {label:"Idle"}}` and named by `langCode` (e.g. `de-DE`). The agent detects the new `Idle` subitem and **takes ownership of the status flow** (Idle → Running → terminal).

### Steps
1. **Claim the run:** set System Status = `Running` and Run Started = today.
   ```json
   { "color_mm3nfga0": {"label":"Running"}, "date_mm3n2gvy": {"date":"YYYY-MM-DD"} }
   ```
2. **Read parent asset context** (parent item of the subitem): `text_mm3ng2f6` (Figma File Key), `text_mm3nbpfm` (Asset Frame Name), `link_mm3npjax` (Figma File), `color_mm3nw9me` (Asset Type), `text_mm40409q` (Cloudinary Folder). Locale = subitem `name`.
3. **Load glossary + style guide** for the locale (§5). Duplicate the EN page, extract text nodes.
4. **Screenshot original (EN)** before any change → hold as base64 for QA and upload to `file_mm3ndya6`.
5. **Translate** all text nodes (§6.7) glossary-first; verify coverage (pass through skipped nodes).
6. **Set text** on the duplicated page; run **font validation** if RU/KO/ZH.
7. **Single layout pass** (§7): RPC overflow + Layout Action Planner + asset-specific fixes.
8. **Screenshot translated** → base64 for QA and upload to `file_mm3nszn1`.
9. **QA** (§8): Layer 2 pixel diff → Layer 3 vision → aggregate → terminal state + calibrated confidence + QA notes + Review Items bullets.
10. **Build Deep Link** for the localized frame → `link_mm3nwes`.
11. **Write terminal board state** (map terminal → System label; set Review Status = `Pending Review` if terminal ∈ {Success, Success with notes, Editor Review Needed}); set dates + Execution Link.

### Board-write payload (New Run success — board `18412118857`, `change_multiple_column_values`, `create_labels_if_missing:true`)
```json
{
  "color_mm3nfga0": {"label":"Success"},
  "color_mm3nzc1r": {"label":"Pending Review"},
  "text_mm45yjpc": "germanisticat@gmail.com",
  "numeric_mm3nyptd": "0.94",
  "long_text_mm34j4w": {"text":"…QA reasoning…"},
  "long_text_mm43mr5c": {"text":"• No issues found — ready for upload"},
  "link_mm3nwes": {"url":"https://www.figma.com/design/usuebR1yX62QkOxSPxTFI3/...?node-id=123-456","text":"Open in Figma"},
  "date_mm3n2gvy": {"date":"2026-07-08"},
  "date_mm3nzda6": {"date":"2026-07-08"},
  "link_mm34khv0": {"url":"https://n8n.bigbrain.me/executions/123","text":"Execution"}
}
```
Screenshots are uploaded via the file-upload endpoint (multipart `add_file_to_column`), NOT via `change_multiple_column_values`:
- `file_mm3nszn1` ← translated PNG (`{asset}_{locale}.png`)
- `file_mm3ndya6` ← original EN PNG (`{asset}_{locale}_original.png`)

`text_mm45yjpc` (Reviewer) is auto-assigned by locale on the New Run — see the §3 map.

`Editor Review Needed` / `Success with notes` use the same payload with the respective `color_mm3nfga0` label (still Review = `Pending Review`). On failure:
```json
{ "color_mm3nfga0": {"label":"Error"}, "long_text_mm34j4w": {"text":"pipeline error — …"}, "date_mm3nzda6": {"date":"2026-07-08"}, "link_mm34khv0": {"url":"…","text":"Execution"} }
```
(No Review Status write on Error.)

---

## PART B — RE-RUN

### Trigger
**Fires when a subitem's Review Status (`color_mm3nzc1r`) flips to `Re-run Requested`** (set by the reviewer in the Vibe app; a Monday automation → webhook). Processes one subitem/locale.

### How it differs from a New Run
- Reads and **applies `Feedback Notes` (`long_text_mm3y8wdd`) JSON** as the primary input.
- **Preserves feedback history** — never delete `Feedback Notes`. May optionally clear `Feedback Type`.
- **Never overwrites `Original Screenshot` (`file_mm3ndya6`)** — the EN reference is fixed.
- Everything else (layout pass, screenshot translated, QA, hand-back) is identical to a New Run.

### Feedback schema (`long_text_mm3y8wdd` — JSON array)
```json
{
  "label":    "Translation quality | Design | Glossary",
  "english":  "source EN text",
  "current":  "current (wrong) localized text",
  "target":   "the correction to apply",
  "reasoning":"why"
}
```
Apply by category:
- **Glossary** → treat `target` as an **authoritative glossary override** (highest priority; overrides AI and even sheet).
- **Translation quality** → re-translate `english`, honoring `target`/`reasoning` (tone/wording).
- **Design** → layout/visual fix (overflow, spacing, alignment) only — do NOT change the translation.

Also read designer hints: `Review Items` (`long_text_mm43mr5c`), `Root Cause` (`dropdown_mm3nejv8`), `Fix Applied` (`dropdown_mm3nggk1`), `Fix Notes` (`long_text_mm3n66bk`). **Apply glossary/translation first, then a single layout pass — never interleave.**

### Steps
1. Set System Status = `Running`, Run Started = today (payload as in Part A step 1).
2. Read `Feedback Notes` + designer hints + parent asset context.
3. Apply feedback: glossary overrides → re-translate flagged nodes → set text.
4. Single layout pass (Design feedback + asset-specific fixes).
5. Screenshot translated → `file_mm3nszn1` (do NOT touch `file_mm3ndya6`).
6. QA (§8) → new QA Notes + Layer 3 Confidence + terminal state.
7. Update Deep Link if the frame changed.
8. Hand back: terminal System Status + Review = `Pending Review` + dates + Execution Link.

### Board-write payload (Re-run success)
```json
{
  "color_mm3nfga0": {"label":"Success"},
  "color_mm3nzc1r": {"label":"Pending Review"},
  "numeric_mm3nyptd": "0.94",
  "long_text_mm34j4w": {"text":"…new QA reasoning…"},
  "date_mm3nzda6": {"date":"2026-07-08"},
  "link_mm34khv0": {"url":"https://n8n.bigbrain.me/executions/456","text":"Execution"}
}
```
On failure: `{"color_mm3nfga0":{"label":"Error"}, ...}` with Review Status left as-is. `long_text_mm3y8wdd` is never written by the agent.

---

## 10. State-Transition Diagrams

### New Run
```
Uploader:            System = Idle                         [subitem created]
Agent start:         System = Running, Run Started = today [TRIGGER: new subitem, System=Idle]
translate → layout → screenshot(original→file_mm3ndya6, translated→file_mm3nszn1) → QA
Agent (QA pass):     System = Success | Success with notes | Editor Review Needed
                     Review = Pending Review
                     + Screenshot, Original Screenshot, Deep Link, QA Notes,
                       Review Items, Layer 3 Confidence, Run Completed, Execution Link
Agent (failure):     System = Error   (Review Status untouched)
```

### Re-run
```
Reviewer (Vibe app): Review = Re-run Requested             [TRIGGER]
Agent start:         System = Running, Run Started = today
read Feedback Notes JSON → apply (Glossary override / re-translate / Design layout)
                     → screenshot(translated→file_mm3nszn1; NEVER touch file_mm3ndya6) → QA
Agent (QA pass):     System = Success | Success with notes | Editor Review Needed
                     Review = Pending Review
                     + Screenshot, (Deep Link), QA Notes, Layer 3 Confidence,
                       Run Completed, Execution Link   (Feedback Notes PRESERVED)
Agent (failure):     System = Error   (Review Status untouched)
```

---

## 11. Design Considerations (agent replaces the plugin + n8n flow)

**The agent is wired only to the Monday board — NOT to the Figma plugin.** In the current system the Figma *canvas* work lives in the plugin: Layer‑1 structural/geometry checks (overflow, sibling collision, text‑on‑text / text‑on‑interactive overlap), neighborhood‑snapshot construction, applying the Layout Action Planner / RPC decisions (resize / reposition / redistribute / widen / rewrite) onto the canvas, and the fix‑loop controller. The replacement agent drives Figma with its own tooling and must absorb these itself:

- **Fold structural checks into its Vision QA.** Rather than a separate Layer‑1 geometry engine, the agent detects overflow / overlap / collision by comparing the **original vs translated screenshots** in its own Vision QA (§8). The "only flag issues that are NEW vs the original" rule still governs.
- **Bounded fix loop — 1–3 attempts, then escalate.** After each layout/translation fix, re‑screenshot and re‑QA. If QA does **not improve across attempts (max 3)**, STOP and escalate: set System = `Editor Review Needed` and hand to human review. Never keep looping on an asset that isn't converging — don't exhaust the agent for no gain. (Mirrors the Layout Action Planner's `attemptNumber` 0–2 + escalate.)
- The Layout Action Planner / RPC **prompts (§7) remain the reference logic for _what_ fix to make** — the agent executes them via its own Figma tooling instead of calling the plugin services.

## 12. Remaining gaps (minor)

- **Screenshot upload mechanism.** Original / translated PNGs go to `file_mm3ndya6` / `file_mm3nszn1` via Monday's multipart `add_file_to_column` (the old flow used an "Upload Helper" sub‑workflow). The agent uploads directly to the board.
- **Postgres / observability (LOW data-loss risk).** The old services INSERT into one Postgres table `pipeline_events` (cred `Postgres — pipeline_events`) with three `event_type`s: `terminal_state` (Asset Complete: outcome, durationMs, confidence), `claude_rpc_planning` (Translation Service: model, translatable/brand node counts, deviationCount), `approval` (Approval Trigger: approver, timestamp, cloudinaryUrl). **All duplicate data already on the Monday board — none is source of truth.** The only board-absent bit is the translation *metrics* (node/deviation counts) — analytics, not state. Replicate these INSERTs only if you want to keep the audit trail. (Health note: the one-time `invalid input syntax for type json` error on `Log Terminal State` was a transient empty-item case on 2026-06-17; all recent runs log cleanly. Translation logger is `continueOnFail:true`.)
- **⚠️ Prompt-feedback structured log (MEDIUM risk — IMAGE flow only, not Figma).** The Image Re-run Trigger writes an n8n **DataTable** `prompt_feedback_log` (`5jvnKcOObCtSsli2`) with the LLM-normalized per-segment corrections (`source_text` / `current_translation` / `correction` / `note` / `version` / `reviewed`) that feed the **Prompt Evolution Engine**. That machine-readable breakdown lives nowhere else (raw feedback on the board is recoverable, the normalized form is not). The Figma flow has no equivalent today — but if/when an agent replaces the *image* re-run flow, it MUST write this or the improvement loop silently stops learning.

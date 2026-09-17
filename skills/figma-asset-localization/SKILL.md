---
name: figma-asset-localization
description: >
  End-to-end Figma asset localization pipeline — translates, layout-corrects, and QAs Figma banner
  assets for target locales (de-DE, pt-BR, fr-FR, es-MX, ja-JP). Triggers on board subitems
  (System Status = Idle or Review Status = Re-run Requested). Do not use for email localization
  (→ email-localization), landing page localization (→ lp-page-localization), or ad copy translation
  (→ meta-ad-localize).
required-files:
  - domains/localization/skills/figma-asset-localization/knowledge/board-schema.md
  - domains/localization/skills/figma-asset-localization/knowledge/translation-rules.md
  - domains/localization/skills/figma-asset-localization/knowledge/layout-methods.md
  - domains/localization/skills/figma-asset-localization/knowledge/qa-pipeline.md
  - domains/localization/skills/figma-asset-localization/knowledge/figma-operations.md
  - domains/localization/skills/figma-asset-localization/knowledge/performance.md
  - domains/localization/skills/figma-asset-localization/knowledge/lessons.md
  - domains/localization/skills/figma-asset-localization/knowledge/preflight.md
---

# Skill: Figma Asset Localization

**Domain:** localization
**Owner:** nymeria-ai@monday.com

Replaces the full n8n localization chain (translation, RPC, layout planner, QA, asset-complete).
Processes one subitem (one locale) per trigger. **NOT** the approval/publish track (Cloudinary).

> **Canonical reference:** `references/agent-operations-manual.md` — the full ops manual with
> verbatim prompts, per-locale rules, column IDs, and state diagrams. When in doubt, authoritative.

## When to use
- Polling detects System Status = `Idle` or Review Status = `Re-run Requested` on the subitem board
- User explicitly asks to localize/translate a Figma asset
- User asks to check the localization board for pending work

## Do NOT use when
- Localizing an **email** template → `email-localization`
- Localizing a **landing page** → `lp-page-localization`
- Translating **ad copy** for Meta/LinkedIn → `meta-ad-localize`
- **Publishing** an approved asset to Cloudinary (separate publish track)

## Routing examples
- **SHOULD:** "localize the Figma banner for de-DE" · "check the localization board" · "re-run es-MX"
- **SHOULD NOT:** "translate the email template" → email-localization · "localize the LP" → lp-page-localization

## Workflow

### Step 0 — Pre-flight (hard gate)
Read `knowledge/lessons.md`. Walk `knowledge/preflight.md` — every item ✅. Do not proceed on failure.

### Part A — New Run (System Status = Idle)
1. **Claim** — Set System Status = `Running`, Run Started = today. Read `knowledge/board-schema.md`.
2. **Context** — Read parent item (Figma File Key, Asset Frame Name, Asset Type). Locale = subitem name.
3. **Glossary + style guide** — Load per `knowledge/translation-rules.md`.
4. **Screenshot original** — Read `knowledge/performance.md` (EN reuse). Validate EN frame name. Export & upload.
4b. *(Optional)* EN source vision analysis for spatial context.
5. **Duplicate page** — Read `knowledge/figma-operations.md` (page naming, source protection, frame sizing/naming).
6. **Extract text** — Plugin API `findAll` (deep instances). Read `knowledge/figma-operations.md`.
7. **Translate** — Glossary-first. Read `knowledge/translation-rules.md`.
8. **Set text (batched)** — Read `knowledge/performance.md` (batch writes). Pre-write source page check.
9. **Layout pass** — Single atomic pass. Read `knowledge/layout-methods.md` + `knowledge/asset-specific-fixes.md`.
10. **Screenshot + upload (parallel)** — Read `knowledge/performance.md`.
11. **QA** — Layer 2 → Layer 3 → terminal state. Read `knowledge/qa-pipeline.md`.
12. **Fix loop** — Max 3 attempts, then escalate to `Editor Review Needed`.
13. **Deep link + reviewer** — Auto-assign by locale. Read `knowledge/board-schema.md`.
14. **Terminal board write** — System Status + Review Status + confidence + QA notes + screenshots.
15. **Housekeeping** — Read `knowledge/performance.md` (cleanup section).

### Part B — Re-run (Review Status = Re-run Requested)
Same as Part A except: reads Feedback Notes as input, NEVER overwrites Original Screenshot,
preserves feedback history. Feedback schema in `knowledge/translation-rules.md`.

## Tools / permissions
- **monday.com API** — read/write subitems on boards 18412118203 / 18412118857
- **Figma REST API** — read-only (metadata, screenshot export)
- **Figma MCP (use_figma)** — write (text, layout, pages) via Claude Code
- **Google Sheets** — read glossaries
- **Vision model** — QA comparison
- **WhatsApp** — escalation to Banners Localization POC group

## Failure & fallback
- **Grounding missing** (glossary empty, Figma file not shared): hard error → `Error` status, report.
- **Capability failure** (Figma MCP down, Claude Code timeout): re-auth per `knowledge/figma-operations.md`; if unrecoverable → `Error` + escalate to WhatsApp group.
- **User-input blocking** (ambiguous asset, unknown locale): ask ONE bounded question, then proceed.
- **Safety/quality gate** (source page write detected, brand rule fail): ABORT immediately → `Error` or `Editor Review Needed`, never suppress.

## Neighbouring skills / routing distinctions
- vs `localization-brain`: brain = method + doctrine + glossary routing; this = Figma-specific execution. Brain is a DEPENDENCY for glossary/style-guide loading, not a competitor.
- vs `email-localization`: emails use a 0-10 score gate; this uses 0.0-1.0 confidence. Different boards.
- vs `lp-page-localization`: LPs are Webflow/HTML; this is Figma frames.
- vs `meta-ad-localize`: ad copy translation for platform upload; this is visual asset localization.

## Pipeline scripts
See `knowledge/scripts.md` for dispatcher, timing instrumentation, and glossary sync.

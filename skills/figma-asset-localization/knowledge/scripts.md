# Pipeline Scripts — Figma Asset Localization

Automated dispatch and instrumentation scripts live in `scripts/`:

## `scripts/dispatcher.py`
Batch dispatcher that polls the board for Idle/Re-run subitems and spawns parallel OpenClaw sub-agents (workers). Each worker runs one locale through the full pipeline (translate → layout → QA → hand-back). Manages concurrency via `localization-state.json` (queue, active, completed tracking).

**Usage:** Called by the agent during batch runs. Reads board state, builds a work queue, spawns up to N workers in parallel, and tracks their lifecycle.

## `scripts/timing.py`
Per-block instrumentation wrapper. Wraps every pipeline stage with precise elapsed-time measurement:
`read_parent_context → glossary_load → style_guide_load → screenshot_original → figma_duplicate_page → figma_extract_text → translation → figma_set_text → layout_pass → screenshot_translated → upload_screenshots → qa_layer2 → qa_layer3 → board_handback`

Each run generates:
- Structured JSON timing data in `scripts/runs/{subitem}_{locale}_{timestamp}.json`
- Human-readable log in `scripts/runs/{subitem}_{locale}_{timestamp}.log`

Includes `retro_analysis_prompt()` - aggregates timing data across runs, identifies slowest blocks, and generates improvement suggestions for self-learning.

## `scripts/localization-state.json`
Persistent state file tracking queue, active workers, and completed jobs with status and confidence scores. Survives agent restarts.

## `scripts/sync-glossaries.py`
Daily cron job that syncs glossary CSVs from Google Sheets to `glossaries/{locale}.csv`. Metadata tracked in `glossaries/sync-meta.json`.

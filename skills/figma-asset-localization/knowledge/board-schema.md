# Board Schema — Figma Asset Localization

## Boards & Access

- **Parent item board:** `18412118203` - read-only inputs (Figma file, frame name, asset type)
- **Subitem board:** `18412118857` - agent reads and writes (one subitem = one locale)
- **API Token:** `.secrets/monday-main-account-token.md` (user: Nymeria-AI, id: 107169724, actid: 5)
  - NOT the Nova Ops plugin token - different account
- **Scope:** Process items from ALL groups on the board (existing and new). Auto-pick any subitem with System Status = `Idle` or Review Status = `Re-run Requested`, regardless of which group it belongs to.
- **Figma file key (Localization Agents LP):** `usuebR1yX62QkOxSPxTFI3`

## Subitem Column Reference (board 18412118857)

Ownership: **[WRITE]** = agent sets · **[READ]** = agent reads · **[NEVER]** = agent must not touch.

| Column | ID | Type | Ownership | Notes |
|---|---|---|---|---|
| Name | `name` | name | [READ] | Locale code (e.g. `de-DE`) |
| Item Name | `text_mm52bbyt` | text | [READ] | Asset name |
| **System Status** | `color_mm3nfga0` | status | **[WRITE]** | Agent-owned. Labels: Idle→Running→terminal |
| Layer 3 Confidence | `numeric_mm3nyptd` | numbers | **[WRITE]** | QA confidence 0.0-1.0 (calibrated) |
| QA Notes | `long_text_mm34j4w` | long_text | **[WRITE]** | QA reasoning |
| Review Items | `long_text_mm43mr5c` | long_text | **[WRITE]** | 2-4 actionable bullets |
| **Review Status** | `color_mm3nzc1r` | status | **[WRITE "Pending Review" ONLY]** | Human-owned; agent's ONLY allowed value = `Pending Review` |
| Feedback Type | `dropdown_mm3yqke4` | dropdown | [READ] | Category hint; may clear after consuming |
| **Feedback Notes** | `long_text_mm3y8wdd` | long_text | **[READ]** | JSON feedback for re-run. NEVER delete - preserve as history |
| Screenshot | `file_mm3nszn1` | file | **[WRITE]** | Post-translation localized PNG |
| Original Screenshot | `file_mm3ndya6` | file | **[WRITE on New Run / NEVER on Re-run]** | Pre-translation EN reference |
| Figma Deep Link | `link_mm3nwes` | link | **[WRITE]** | Frame deep link |
| Cloudinary URL | `link_mm3nrhmp` | link | **[NEVER]** | Publish track |
| Execution Link | `link_mm34khv0` | link | **[WRITE]** | OpenClaw session ID for traceability |
| Run Started | `date_mm3n2gvy` | date | **[WRITE]** | Set at run start |
| Run Completed | `date_mm3nzda6` | date | **[WRITE]** | Set at terminal state |
| Reviewer | `text_mm45yjpc` | text | **[WRITE]** | Auto-assign by locale on New Run |
| Root Cause | `dropdown_mm3nejv8` | dropdown | [READ] | Designer hint |
| Fix Applied | `dropdown_mm3nggk1` | dropdown | [READ] | Designer hint |
| Fix Notes | `long_text_mm3n66bk` | long_text | [READ] | Designer free-text |
| Fix Duration | `numeric_mm3nxeg9` | numbers | [READ] | Minutes to fix |
| Localization Score | `numeric_mm51aa70` | numbers | **[NEVER]** | Human 0-10 score |
| People | `multiple_person_mm52qyc0` | people | **[NEVER]** | Assignment column |

## Parent Item Columns (board 18412118203) - ALL [READ] only

| Column | ID | Type |
|---|---|---|
| Figma File | `link_mm3npjax` | link |
| Figma File Key | `text_mm3ng2f6` | text |
| Asset Frame Name | `text_mm3nbpfm` | text |
| Asset Type | `color_mm3nw9me` | status |
| Cloudinary Folder | `text_mm40409q` | text |

---

## Status Model - Exact Labels (verbatim, use `create_labels_if_missing: true`)

### System Status (`color_mm3nfga0`) - agent-owned
`Idle` · `Running` · `Success` · `Success with notes` · `Editor Review Needed` · `Error`

- Uploader sets `Idle`
- Agent sets `Running` at start, then exactly one terminal:
  - **`Success`** - QA passed, high confidence (≥0.85), Layer 1 clean
  - **`Success with notes`** - QA passed, high confidence (≥0.85), minor Layer 1 notes
  - **`Editor Review Needed`** - medium/low confidence, hard-fail check, or collision
  - **`Error`** - pipeline/catastrophic failure
- Do NOT use `Approved` / `Failed` (reserved/legacy)

Terminal-state mapping:
```
success              → Success
success-with-notes   → Success with notes
editor-review-needed → Editor Review Needed
pipeline-error       → Error
```

### Review Status (`color_mm3nzc1r`) - human-owned
`Pending Review` · `In Review` · `Pass to Localization review` · `Needs Changes` · `Re-run Requested` · `Approved`

- Agent ONLY writes `Pending Review` (on non-Error terminals)
- Agent NEVER writes: In Review, Pass to Localization review, Needs Changes, Approved, Re-run Requested

---

## Triggers & Polling

Poll the subitem board for items in the allowed groups ("Nymeria Test" and "Campaign Localization"):

1. **New Run:** System Status (`color_mm3nfga0`) = `Idle` → start Part A
2. **Re-run:** Review Status (`color_mm3nzc1r`) = `Re-run Requested` → start Part B

Process one subitem at a time (sequential) to avoid cross-language contamination.

---

## Board Write Payload (New Run success)

Board ID: `18412118857`, with `create_labels_if_missing: true`:
```json
{
  "color_mm3nfga0": {"label":"Success"},
  "color_mm3nzc1r": {"label":"Pending Review"},
  "text_mm45yjpc": "germanisticat@gmail.com",
  "numeric_mm3nyptd": "0.94",
  "long_text_mm34j4w": {"text":"...QA reasoning..."},
  "long_text_mm43mr5c": {"text":"• No issues found - ready for upload"},
  "link_mm3nwes": {"url":"https://www.figma.com/design/...?node-id=123-456","text":"Open in Figma"},
  "date_mm3n2gvy": {"date":"2026-07-09"},
  "date_mm3nzda6": {"date":"2026-07-09"},
  "link_mm34khv0": {"url":"openclaw-session-id","text":"Execution"}
}
```

Screenshots uploaded separately via `monday_add_file_to_column`.

On Error: `{"color_mm3nfga0":{"label":"Error"}, ...}` - NO Review Status write.

---

## Screenshot Upload

File columns CANNOT be set via `change_multiple_column_values`. Use `monday_add_file_to_column` tool:
1. Export from Figma REST API: `GET /v1/images/{fileKey}?ids={nodeId}&format=png&scale=2` → returns a temporary public URL
2. Upload via `monday_add_file_to_column(item_id, column_id, file_url)`
3. File naming: `{asset}_{locale}.png` (translated), `{asset}_{locale}_original.png` (original)

**Re-run screenshot replacement (mandatory):**
On re-runs, the Screenshot column (`file_mm3nszn1`) must contain ONLY the latest image. Before uploading:
1. Archive the old screenshot to an **update** on the item - include the date it was moved (e.g. "Previous screenshot from YYYY-MM-DD run, archived on YYYY-MM-DD")
2. **Clear** the file column entirely (`change_column_value` with `value: "{}"`)
3. Upload ONLY the new screenshot

This ensures reviewers always see the current version, not a stack of old + new.

### Reviewer Validation (mandatory)
After auto-assigning the reviewer (step 14), verify the Reviewer column (`text_mm45yjpc`) is non-empty before writing the terminal board state. If the reviewer lookup returns empty:
1. Force-write the reviewer from the locale mapping table (the locale → email mapping is deterministic)
2. Log a warning in QA Notes: `REVIEWER_WRITE_RETRY: locale={locale}, reviewer={email}`
3. **Complete the run normally** - do NOT set Error for a missing reviewer. The run itself succeeded.
4. If the locale is genuinely not in the mapping table, flag it in QA Notes but still complete the run.

Never let a reviewer write failure block or error-out a successful localization run.

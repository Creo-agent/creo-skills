# Visual QA Pipeline — Figma Asset Localization

## Quality Gate

**Quality gate is NOT the email 0-10 score.** This pipeline grades on **Layer 3 Confidence, 0.0-1.0**, with **≥0.85** as the pass bar (`System Status` → `Success` / `Success with notes`). The email pipeline (`../email-localization/SKILL.md`) grades on a **0-10 score with a ≥9 floor**. Different scale, different column, different pipeline — do not carry a threshold from one into the other.

## Layer 2 - Pixel Diff (deterministic)
Compare original vs translated screenshots. Size-ratio heuristic:
- Translated buffer <0.3× or >3.0× original → `overallDiffPct = 80` (catastrophic)
- Else `overallDiffPct = |1 - sizeRatio| * 100`
- `fail` if `overallDiffPct > 60`, else `pass`
- On Layer 2 fail → respond early with `pipeline-error`, no Layer 3

## Layer 3 - Vision Eval
Six PASS/FAIL checks: `visualHierarchy`, `calqueDetection`, `glossaryFidelity`, `brandRules`, `strayEnglish`, `textCompleteness`

**EN Source Analysis context:** If step 4b was run, load `scripts/runs/EN_{asset_name}_analysis.txt` as additional context for the vision comparison. This gives you a pre-built understanding of the original layout's tight spots, spatial relationships, and composition — making comparison more precise.

**Critical comparison rule:** Only flag issues that are NEW in the translated version. Pre-existing truncation/clipping in the original = intentional design → do NOT penalize.

**Stray English:** Only fail for text NODES. English in rasterized images/icons/screenshots-within-screenshots is OUTSIDE pipeline scope → PASS and note.

**calqueDetection:** Informational only - glossary is authoritative. Never a hard fail.

## Confidence Calibration
Raw confidence capped by worst failing check:
- `textCompleteness` → 0.60
- `brandRules` → 0.50
- `strayEnglish` → 0.55
- `visualHierarchy` → 0.70
- `calqueDetection` → 0.80
- `glossaryFidelity` → 0.75

Stack penalty: `(failCount - 1) * 0.05`. Floor: 0.30.

## Terminal State Gating
- Layer 2 fail → `pipeline-error`
- Hard fails (regardless of confidence):
  - `brandRules` fail → `editor-review-needed`
  - `strayEnglish` fail → `editor-review-needed`
  - `textCompleteness` fail → `editor-review-needed`
- Layer 1 sibling collision → `editor-review-needed`
- Layer 3 missing → `pipeline-error`
- By calibrated confidence:
  - `≥0.85 && layer1Clean` → **success**
  - `≥0.85 && !layer1Clean` → **success-with-notes**
  - `≥0.70` → **editor-review-needed** (medium confidence)
  - `<0.70` → **editor-review-needed** (low confidence)

## Review Items Summarizer
- `Success` (no auto-fix) → `• No issues found - ready for upload`
- `Success with notes` (no fail) → `• Passed with minor notes - review at your discretion`
- Otherwise → 2-4 action bullets: `• [Action verb] [specific issue] [where]` (Check/Fix/Verify/Note, max 15 words each)

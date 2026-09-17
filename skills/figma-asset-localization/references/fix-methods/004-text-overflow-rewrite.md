# Fix Method #4: Text Overflow Rewrite

## Trigger
QA vision detects that translated body text significantly overflows its container, causing:
- Text clipping/truncation at different points than the original
- Text wrapping to more lines, pushing content below out of view
- Important words/verbs cut mid-word where the original had clean truncation

## Diagnosis
Compare the text node height (DE vs EN). If DE height exceeds EN height by >20%, the translated text is too long for the container. Check if the text is mock/decorative content (document preview, report mock-up) vs. real UI text — mock content allows more rewriting freedom.

## Action Steps

### For mock/decorative content (document previews, report text in banners)
1. Identify the target height (match EN text node height)
2. Rewrite the translation more concisely while preserving:
   - Key terms and proper nouns (company names, product names)
   - The overall message/narrative
   - Paragraph structure (same number of line breaks)
3. Use compound nouns and abbreviations where natural in the target language (e.g. "APT-Erkennungsmodule" instead of "Module zur Erkennung von Advanced Persistent Threats")
4. Set the shortened text via Figma MCP
5. Verify height matches the original

### For real UI text
1. Check glossary for shorter alternatives
2. If no shorter glossary term exists, try rephrasing without removing meaning
3. If text cannot be shortened without losing meaning → escalate to Designer Review

## Constraints
- Preserve paragraph count (same number of \n as original)
- Keep proper nouns unchanged (Fortress Guard, SentioSec, etc.)
- Maintain the same tone (technical, casual, etc.)
- For mock content: prioritize visual match over translation precision
- For real UI text: prioritize translation accuracy over visual match
- Check for orphan words in the rewritten text (apply Method #3 if needed)

## Example
- **Asset:** AI_marketing_competitor_agent, de-DE (doc area)
- **Before:** 207px height (EN was 138px) — German text wrapped to 7+ lines vs EN's 4-5
- **Fix:** Rewrote "Module zur Erkennung von Advanced Persistent Threats (APT)" → "APT-Erkennungsmodule"; "einen bahnbrechenden, KI-gestützten" → "einen KI-gestützten"
- **Result:** Height dropped to 138px — exact match with EN

## Learned: 2026-07-19

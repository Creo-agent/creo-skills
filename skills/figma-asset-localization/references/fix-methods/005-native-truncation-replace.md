# Fix Method #5: Native Truncation Replace

## Trigger
QA detects a text node using manually typed "..." for truncation instead of Figma's native text truncation. The manual ellipsis causes the text + "..." to expand the container via HUG, pushing other elements.

## ⚠️ CRITICAL: Three Dots ≠ Always Truncation

Before applying this method, DETERMINE THE PURPOSE of the "...":

1. **Thinking/Loading animation** (e.g. "Sending to the team...", "Wird an das Team gesendet...") — The three dots represent an ongoing process/thinking state, like a loading spinner. These dots are INTENTIONAL and must be PRESERVED. Do NOT truncate the word before them. Do NOT apply native truncation.

2. **Actual truncation** (text was cut short because it doesn't fit) — The dots indicate content was shortened. This is where native truncation applies.

**How to distinguish:** Check the original EN source. If the EN text also has "..." in the same position AND the context is a status/progress message ("Sending...", "Processing...", "Thinking..."), it's a thinking animation → skip this method.

## Diagnosis
ONLY applies when: text node has trailing " ..." or "..." that represents truncated content (NOT thinking/loading animation), combined with `textTruncation: DISABLED` and `layoutSizingHorizontal: HUG`. The node is growing to fit ALL text including the manual ellipsis, rather than truncating at a fixed boundary.

## Action Steps
1. Remove the manual "..." (or " ...") from the text content
2. Enable Figma's native text truncation: set `textTruncation` to `ENDING` in Type properties
3. Set the text node to FIXED width (match the EN equivalent's width)
4. Figma will now auto-add "..." only when the text overflows the fixed boundary
5. Verify the parent HUG chain collapsed to a reasonable width

## Constraints
- Match the EN text node's width for the FIXED size
- Ensure the truncated text still shows enough of the message to be readable
- If the card containing this text has a sibling card, verify both cards maintain consistent dimensions after the fix
- The text node's `textAutoResize` will change to `TRUNCATE` — this is expected

## Example
- **Asset:** AI_marketing_competitor_agent, de-DE
- **Before:** "Wird an das Team gesendet ..." — 363px wide (HUG), expanding the card to 461px, overflowing toward the CTA button
- **Fix:** Removed manual "...", set textTruncation=ENDING, fixed width to 270px (matching EN "Sending to the team...")
- **Result:** Card inner frame shrank from 461→368px, text auto-truncates with native ellipsis

## Learned: 2026-07-19

# Fix Method #1: Card Dimension Restore

## Trigger
QA vision detects that a container/card frame has different dimensions from the original EN frame, causing child elements to displace (e.g. CTA moves below instead of beside text, text reflows excessively).

## Diagnosis
Compare `absoluteBoundingBox` width/height of the localized frame against the corresponding original EN frame. A width difference >10% or a height difference that changes the number of text lines indicates this fix is needed.

## Action Steps
1. Read the original EN frame dimensions (width, height) from the Figma REST API
2. Read the localized frame dimensions
3. Resize the localized frame to match the original width (height can stay HUG if auto-layout)
4. Check if FILL children auto-cascaded to the correct width — if not, resize them too
5. Verify auto-layout modes (FILL/HUG) are preserved on children

## Constraints
- Don't force FIXED on children that were FILL — let them cascade from parent width
- Slight expansion beyond original is allowed if needed to avoid orphan words (see global constraints)
- Height should be HUG/auto where possible — only fix width explicitly

## Example
- **Asset:** AI_marketing_competitor_agent, de-DE
- **Before:** Prompt box field was 402.6×311.0 (original: 621.0×262.0)
- **Fix:** Resized to 621.0 wide, children auto-cascaded via FILL
- **Result:** Text reflowed to 2 lines, CTA returned to correct position

## Learned: 2026-07-19

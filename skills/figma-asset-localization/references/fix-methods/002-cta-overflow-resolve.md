# Fix Method #2: CTA Overflow Resolve

## Trigger
QA vision detects that a button/CTA label is clipped, overflowing, or extending beyond the button container after translation.

## Diagnosis
Compare the text node width against its parent button frame width. If text width > button width (accounting for padding), the text is clipping.

## Action Steps (in priority order)

### Option A: Shorten text (preferred if possible)
1. Check the locale glossary for a shorter alternative
2. Verify the shorter text preserves the original meaning
3. If glossary-compliant and meaning preserved → apply shorter text directly
4. If meaning is slightly altered → apply but add a reviewer note

### Option B: Set button to HUG contents
1. Change the button frame's `layoutSizingHorizontal` from FIXED to HUG
2. The button will auto-expand to fit the translated text
3. Verify the expanded button doesn't overflow its parent container
4. If it overflows the parent → consider Option A or escalate

### Option C: Escalate
If neither shortening nor HUG resolves cleanly → escalate to Designer Review with a note explaining the overflow and attempted fixes.

## Constraints
- Always check glossary BEFORE shortening text
- Button must retain proper horizontal padding (match original padding ratio)
- Expanded button must not push other elements out of the card
- Never truncate text with ellipsis unless the original does the same

## Example
- **Asset:** AI_marketing_competitor_agent, de-DE
- **Before:** "Deinen Agenten erstellen" clipping in 238px button (EN "Build your agent" fit fine)
- **Fix:** Set button to HUG → auto-expanded to 350px
- **Result:** Full text visible with proper padding, no overflow

## Learned: 2026-07-19

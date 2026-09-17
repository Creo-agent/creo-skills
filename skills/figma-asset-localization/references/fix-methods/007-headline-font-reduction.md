# Fix Method #7: Headline Font Size Reduction

## Trigger
QA detects that a translated headline that was originally N sentences/lines in the EN source now overflows into more lines. The headline should retain its original line count.

## Diagnosis
Compare the translated headline's line count vs the original EN. If the EN headline is 2 lines (2 sentences) and the translated version wraps to 3+ lines, the text is too long for the current font size.

## Action Steps
1. Note the original EN headline's font size and line count
2. Reduce font size by **5 pixels** from the original
3. Check if the headline now fits in the original line count
4. If still overflowing → reduce by another **5 pixels** (total -10)
5. Repeat in 5px decrements until the headline fits in the original line count
6. **Maximum reduction:** 3 steps (15px). If still doesn't fit after -15px → escalate to `Editor Review Needed`

## Post-Reduction Repositioning
When the headline font size is reduced, other elements MUST be repositioned to maintain visual balance:
- **monday.com logo:** Move to vertical center of the composition, floating upward — away from the card/content below
- **Headline text block:** Reposition to maintain balanced spacing between logo above and content below
- **Spacing rule:** Elements should never feel "squeezed" — when text gets smaller, redistribute the freed vertical space evenly

## Constraints
- ONLY reduce headline font sizes — never body text, cards, or CTAs
- Reduce in exact 5px steps (not 3, not 7 — exactly 5)
- Preserve font family and weight — only change size
- After resizing, verify the headline still reads as 2 distinct sentences if that was the original intent
- The reduced font size applies ONLY to the localized version — never change the EN source

## Example
- **Asset:** Agents_builder_dark, de-DE
- **EN original:** "Your skills. Agents do the rest." — 2 lines, ~80px font
- **Problem:** German "Deine Skills. Agenten machen den Rest." was wrapping to 3 lines at 80px
- **Fix:** Reduced to 75px → fits in 2 lines. Repositioned monday.com logo to vertical center with more breathing room above.

## Learned: 2026-07-19

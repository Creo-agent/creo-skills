# Fix Method #9: Element Spacing & Overlap Resolution

## Trigger
QA detects that an element (card, text block, button) is touching or slightly overlapping another element (agent image, illustration, background shape) when it shouldn't be. The design intent is clear separation between UI cards and decorative/character elements.

## Diagnosis
After layout changes (card expansion, font reduction, repositioning), check for:
- Cards that are now touching or slightly overlapping the agent/character image
- Text blocks that are too close to illustrations
- UI elements that have lost their breathing room from the original design

## Rules
1. **Cards over images:** UI cards should be visually "over" (on top of, in z-order) or clearly separated from character/agent images. Never touching — always a visible gap.
2. **Match original spacing:** Compare the original EN's spacing between the card and character image. The localized version should have equal or greater spacing.
3. **When elements collide after expansion:**
   - **Option A:** Move the card away from the image (preferred if space allows)
   - **Option B:** Enlarge the character image slightly so the overlap becomes intentional overlap (the character is "behind" the card, not awkwardly touching the edge)
   - **Option C:** Reduce card padding slightly (last resort)

## Action Steps
1. Identify the overlapping/touching elements
2. Measure the gap (or lack of gap) between them
3. Compare with the original EN design's spacing
4. Apply the fix:
   - If the card expanded into the image's space → resize/reposition the agent image (make it larger so it sits confidently behind the card, not awkwardly touching)
   - If repositioning freed up space → move elements to restore original spacing ratios
5. Verify no new overlaps were created by the fix

## Constraints
- Cards must NEVER "just barely touch" the character image — it looks like a bug
- Either have clear separation (gap ≥5px) or intentional overlap (card clearly over the image)
- When enlarging the character image, maintain proportions (scale uniformly)
- The character image should feel deliberately placed, not squeezed or pushed by the card

## Example
- **Asset:** Agents_builder_dark, de-DE
- **Before:** After expanding the two notification cards, the card edge was slightly touching the agent character's arm
- **Fix:** Designer enlarged the agent image so the card sits confidently over part of the character (intentional overlap, not accidental touching)
- **Result:** Clean visual hierarchy — card clearly layered over the character image

## Learned: 2026-07-19

# Fix Method #8: Auto-Layout Paired Cards

## Trigger
QA detects that two sibling cards (e.g. notification cards, status cards) have mismatched dimensions after translation, when they were designed to be visually paired with matching sizes.

## Diagnosis
Two or more small cards in the same parent frame were designed with auto-layout so that if one expands (due to longer translated text), the other matches it. After translation, check if:
- One card expanded (text got longer) but the sibling didn't match
- Cards have different heights/widths when they should be uniform
- The parent frame uses auto-layout with children set to FILL on the cross-axis

## Action Steps
1. Identify the paired card group (they share a parent auto-layout frame)
2. Check the parent frame's auto-layout settings:
   - `layoutMode` should be VERTICAL or HORIZONTAL
   - Children should use `layoutSizingHorizontal: FILL` or `layoutSizingVertical: FILL` on the cross-axis
3. If auto-layout is broken or children are FIXED instead of FILL:
   - Set children to FILL on the cross-axis so they stretch together
   - Keep the primary axis sizing as-is (usually HUG for content)
4. If one card expanded due to longer text:
   - Verify the sibling card also expanded to match
   - If not, check if auto-layout was accidentally overridden — restore it
5. Verify both cards have consistent padding, border radius, and visual weight

## Constraints
- Paired cards MUST have matching dimensions when in the same visual group
- Prefer FILL sizing on auto-layout children over manual FIXED sizing
- Don't force exact pixel values — let auto-layout handle the coordination
- If expanding the cards causes overlap with other elements (e.g. agent image), see Method #9 for spacing rules
- The design intent is that paired cards behave as a unit — one changes, both change

## Example
- **Asset:** Agents_builder_dark, de-DE
- **Before:** "Bericht generieren" card was narrower than "Wird an das Team gesendet..." card after translation
- **Fix:** Set both cards to FILL width in their shared auto-layout parent → both expanded to match the wider card
- **Result:** Uniform card widths, consistent visual pairing

## Learned: 2026-07-19

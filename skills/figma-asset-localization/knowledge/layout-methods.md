# Layout Fix Methods — Figma Asset Localization

Layout is a SINGLE ATOMIC PASS after all translation.

## Design Philosophy
Keep the localized asset as close to the original design as possible. Only apply layout changes when translation genuinely overflows or breaks the design, without harming translation meaning and rules.

## Overflow Resolution
Six actions available (in priority order):
1. **Shorter glossary term** - Prefer a shorter glossary-appropriate translation first
2. **REWRITE** - Shorter translation preserving meaning (must fit within `currentWidth`)
3. **INCREMENTAL CONTAINER WIDEN** (Method #10) - When no shorter translation exists: widen the container by 5px, check for sibling collision + proportion preservation. Repeat up to 3× (max 15px). If still truncated or collision detected after 3 attempts → escalate.
4. **GENERAL WIDEN** - Increase container width beyond 15px (only if `maxAvailableWidth > currentWidth` and no sibling collision)
5. **HEADLINE FONT REDUCTION** (Method #7) - For headlines ONLY: reduce by 5px steps until it fits in the original line count. Max 3 steps (-15px). After reduction, reposition logo/text to maintain visual balance.
6. **ESCALATE** - None of the above is safe → designer must fix

Constraints: Never reduce body/card/CTA font sizes. Never truncate (except native Figma truncation where appropriate - NOT for thinking dots). Rewrites use the glossary. If shortening loses meaning, escalate.

## Layout Debugging Principles
When a visual issue persists after setting the "right" property:
1. **Compare working vs broken** — don't just set values blindly. Read the actual properties of BOTH the correct rows and the broken rows, then diff them.
2. **Check inherited sizing** — a frame with `counterAxisAlignItems=CENTER` still looks wrong if its CHILD has a FIXED height from a previous state (e.g. text was 2 lines, got shortened to 1, but frame height stayed at 28px). Set child to HUG.
3. **Preserve spacing rhythm** — when redistributing column widths, compare the result against the EN original's whitespace balance. Extra space on one side = redistribute between columns.
4. **Root cause > symptom** — alignment issues are usually sizing issues. Width/height mismatches cause visual misalignment even when alignment properties are correct.

## Post-Translation Style Validation (Method #6)
After setting translated text on ANY node, run style validation:
1. **Per-character bold/weight** - If the original has bold words (e.g. "Ace" in "Created by Ace"), verify the ENTIRE translated equivalent word is bold, not just the first character
2. **List types** - If the original node has mixed list styles (ORDERED/UNORDERED/NONE per line), verify they're preserved after text replacement
3. **Gradient/fill overrides** - Per-segment fill styles must be restored

## Headline Font Reduction (Method #7)
For headlines ONLY: reduce by 5px steps until it fits in the original line count. Max 3 steps (-15px). After reduction, reposition logo/text to maintain visual balance.

## Auto-Layout Paired Cards (Method #8)
When two or more sibling cards share a parent auto-layout frame, they MUST expand/contract together. After translation:
1. Verify paired cards have matching dimensions
2. If one expanded, check the sibling matched
3. If not → restore FILL sizing on the cross-axis

## Element Spacing (Method #9)
After any layout change, verify element spacing:
- Cards must NEVER "just barely touch" character/agent images
- Either clear separation (≥5px gap) or intentional overlap (card over image)
- If expanding a card causes touching → enlarge the character image to create intentional layering

## Incremental Container Widen (Method #10)
When no shorter glossary-compliant translation exists, widen the container by 5px up to 3× (max 15px). Check sibling collision and proportion preservation at each step. If still truncated or collision after 3 attempts → escalate.

## Bounded Fix Loop
After each layout/translation fix: re-screenshot and re-QA. Max 3 attempts (0, 1, 2). If QA doesn't improve across attempts → STOP and escalate to `Editor Review Needed`. Never keep looping on an asset that isn't converging.

## Frame Sizing (mandatory)
After any page duplication or frame creation, verify ALL outer frames are exactly 640×560. If `layoutSizingVertical` is `HUG`, change to `FIXED` and resize to 640×560.

## Frame Naming (mandatory)
All outer frames on locale pages MUST be named `{asset-name}_{LOCALE}` (e.g. `anthony-activity-log_DE`). Use 2-letter locale codes: DE, BR, FR, ES, JA. Apply during Step 5 (page duplication) immediately after creating the locale page.

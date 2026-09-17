# Fix Methods Library

Post-QA fixing strategies for localized Figma assets. Each method is a documented, reusable fix that the agent applies after vision QA detects differences between original and localized frames.

## Pipeline Position

After QA vision comparison → select matching fix method(s) → apply → re-screenshot → re-QA → hand-back

## Global Design Constraints

These apply to ALL fix methods:

1. **No orphan words:** A sentence must never end with a single word on its own line. If the last line has only one word, either:
   - Expand the container slightly to pull it up to the previous line
   - If expanding isn't feasible, apply best design effort and escalate to Designer Review
2. **Slight expansion allowed:** A card/container CAN be slightly wider or taller than the original if it preserves the overall design integrity. Don't force exact pixel match at the cost of breaking layout.
3. **Glossary first:** Always check the locale glossary before shortening or changing text. If text change is glossary-compliant and meaning is preserved → change directly. If not → change and add a reviewer note.
4. **Preserve auto-layout:** Prefer FILL/HUG on children over FIXED when the original uses auto-layout. Don't force FIXED sizing unless specifically needed.
5. **Never change design intent:** Only change text content and container dimensions. Don't alter colors, fonts, spacing ratios, or visual hierarchy.

## Methods Index

| # | Method | Trigger | File |
|---|--------|---------|------|
| 1 | card-dimension-restore | Container dimensions differ from original, causing child displacement | [001-card-dimension-restore.md](001-card-dimension-restore.md) |
| 2 | cta-overflow-resolve | Button/CTA text clips or overflows after translation | [002-cta-overflow-resolve.md](002-cta-overflow-resolve.md) |
| 3 | orphan-word-resolve | Single word alone on the last line of a sentence | [003-orphan-word-resolve.md](003-orphan-word-resolve.md) |
| 4 | text-overflow-rewrite | Body text significantly overflows container after translation | [004-text-overflow-rewrite.md](004-text-overflow-rewrite.md) |
| 5 | native-truncation-replace | Manual "..." causing HUG expansion; replace with Figma truncation (⚠️ NOT for thinking/loading dots) | [005-native-truncation-replace.md](005-native-truncation-replace.md) |
| 6 | mixed-style-text-restore | Per-character styles lost after text replacement (bold/regular/gradient/list types) | [006-mixed-style-text-restore.md](006-mixed-style-text-restore.md) |
| 7 | headline-font-reduction | Headline overflows original line count; reduce font by 5px steps + reposition | [007-headline-font-reduction.md](007-headline-font-reduction.md) |
| 8 | auto-layout-paired-cards | Paired sibling cards have mismatched dimensions; restore auto-layout coordination | [008-auto-layout-paired-cards.md](008-auto-layout-paired-cards.md) |
| 9 | element-spacing-overlap | Elements touching/overlapping character images; restore spacing or intentional layering | [009-element-spacing-overlap.md](009-element-spacing-overlap.md) |
| 10 | incremental-container-widen | Text truncation in fixed containers (pills/tags/badges) when no shorter translation exists; widen by 5px up to 3× with collision + proportion checks | [010-incremental-container-widen.md](010-incremental-container-widen.md) |

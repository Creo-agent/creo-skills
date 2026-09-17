# Asset-Specific Fixes — Figma Asset Localization

## Activity Log (`anthony-activity-log`)
- Add 16px itemSpacing between columns
- Widen Trigger +50px and Description +60px
- Widen white card to contain Status chips
- Center card in frame (60px padding)
- **Post-translation:** Apply text truncation (`textTruncation=ENDING`, `textAutoResize=TRUNCATE`, `layoutSizingHorizontal=FILL`) to Description column text nodes
- Ensure all Trigger column cells have `counterAxisAlignItems=CENTER`
- If Status pills overflow, redistribute column widths: narrow Description by ~40px, widen Status to ~140px FIXED, set pill Chips to `layoutSizingHorizontal=FILL`

## Knowledge Access (`anthony-knowledge-access`)
- Line 1: UNORDERED list indent 1
- Lines 2-3: NONE list indent 2 with 4 leading spaces
- Line 4: UNORDERED list indent 1
- Proactively widen text container +30px

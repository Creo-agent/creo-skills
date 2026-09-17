# Fix Method #6: Mixed Style Text Restore

## Trigger
QA detects that a text node with multiple styles (bold headline + regular body, gradient fills, etc.) has lost its per-character style overrides after a text content change. All text appears in the same style (usually the first character's style).

## Diagnosis
Compare the localized text node's visual appearance against the original EN. If the EN has a bold headline with regular body text (different fontWeight/fontFamily segments), but the DE shows everything in one style, the `characterStyleOverrides` and `styleOverrideTable` were lost during text replacement.

## Root Cause
When setting text content via Figma Plugin API (MCP), the existing per-character style overrides are cleared. The new text inherits the default style of the text node (usually the first character's style = bold headline). Body text that should be Regular becomes Bold.

## Action Steps
1. Read the original EN text node to understand the style segments:
   - Check `characterStyleOverrides` array (per-character style IDs)
   - Check `styleOverrideTable` (maps style IDs to font properties)
   - Note the character ranges for each style transition
   - **Map EVERY character** to its style — do not assume contiguous segments share a style
2. After setting the new localized text, apply style ranges using `setRangeFontName`:
   - Headline segment: fontName {family, style: 'Bold'}, fontWeight 700
   - Body segments: fontName {family, style: 'Regular'}, fontWeight 400
   - Special segments (gradient, dimmed): Also apply fill overrides
   - **Per-word bold:** If a word like "Ace" or "ACE" is bold in the original, the ENTIRE translated equivalent must be bold — not just the first character. When the translated text changes length, recalculate character ranges based on the new text positions.
3. Add any missing structural elements (numbered list markers "1.", "2.", etc.)
4. **Check for LIST styles** (see below)
5. Verify final height matches the target

## List Style Detection
A single text node can contain mixed list styles (bullets, numbered). When the original EN uses:
- **UNORDERED** list type (bullet points) on specific lines
- **ORDERED** list type (numbered "1.", "2.") on specific lines
- **NONE** list type (plain text, possibly indented) on other lines

After text replacement, verify and restore:
1. Read `listType` per line from the original EN node
2. After setting localized text, re-apply the same `listType` per line
3. Verify indent levels match (`listIndent` / `indentation`)
4. If the original has bullets on lines 1 and 4 but plain text on lines 2-3, replicate that exact pattern

## Constraints
- Must preserve ALL style segments from the original EN — **per character, not per segment**
- When a specific word is bold (e.g. "Ace" in "Created by Ace"), the FULL translated word must be bold (e.g. "Erstellt von **Ace**" — all 3 characters of Ace, not just "A")
- Pay attention to gradient fills on specific segments (e.g. preview/locked content effect)
- Numbered list markers must be restored if present in the original
- List types (ORDERED/UNORDERED/NONE) must match per-line from original
- Height after styling should still match the EN target
- Font family and size must remain unchanged

## Example
- **Asset:** AI_marketing_competitor_agent, de-DE (doc area)
- **Before:** All text was Bold after content replacement. Missing "1." / "2." numbering. No gradient on second item.
- **Fix:** Applied 3 style segments: Bold headline (chars 0-51), Regular body (chars 51-158), Regular+gradient (chars 158-226). Added "1." and "2." numbering.
- **Result:** Visual match with EN styling. Height stayed at 138px.

## Learned: 2026-07-19

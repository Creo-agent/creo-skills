# Fix Method #10: Incremental Container Widen

## Trigger
QA detects text truncation inside a fixed-width container (pill, tag, badge, card cell) where:
- A shorter glossary-compliant translation was NOT available (Method #4 attempted first)
- The container holds multiple sub-elements (e.g. avatar + text + status tag)
- One or more text elements are clipped with "..." or visually cut off

## Diagnosis
1. Confirm that Method #4 (shorter translation / rewrite) was already attempted and no glossary-compliant shorter term exists
2. Identify the container node and its current width
3. Identify sibling containers (elements sharing the same parent auto-layout frame or adjacent in the design)
4. Measure available space between the container's right edge and the nearest sibling or frame boundary

## Action Steps

### Step 1: Attempt shorter translation first (MANDATORY)
Before widening, always check:
- Is there a shorter glossary term? (e.g. "Erledigt" instead of "Abgeschlossen")
- Can the text be rewritten shorter without losing meaning?
- If yes → apply the shorter text. Done. Do NOT widen.

### Step 2: Incremental widen (fallback only)
If no shorter translation is available:

1. **Widen by 5px** — increase the container width by exactly 5px
2. **Check for sibling collision** — verify the widened container does not:
   - Overlap any sibling element
   - Push a sibling outside its parent frame
   - Break auto-layout spacing (gap between siblings must remain ≥ original gap)
3. **Check proportion preservation** — compare against the original EN layout:
   - The overall composition must still "read" the same
   - No element should appear disproportionately large or small
   - Padding ratios within the container should remain visually consistent
4. **Check truncation** — is the text now fully visible?
   - If YES → done, widen succeeded
   - If NO → repeat from step 1 (widen another 5px)

### Step 3: Max attempts
- Maximum 3 widen attempts (5px, 10px, 15px total)
- After 3 attempts, if text is still truncated OR any collision/proportion issue exists → ESCALATE to `Editor Review Needed`

## Constraints
- **ALWAYS attempt shorter translation first** — widening is a fallback, never the first option
- Maximum total widen: 15px (3 × 5px)
- Must not cause sibling collision at any step
- Must preserve overall composition/proportion compared to EN original
- If the container is inside an auto-layout parent, verify the parent can accommodate the extra width without cascading layout breaks
- If widening one container in a repeated pattern (e.g. list of pills), ALL instances of that container type should be widened consistently
- Never widen beyond the parent frame boundary

## Vision QA Integration
During Layer 3 vision QA, when a container was widened:
- Explicitly compare the widened area against the EN original
- Check that the composition / proportion of surrounding elements is preserved
- Flag if the widen made the element look visually out of balance

## Example
- **Asset:** Alex-briefing agent, de-DE
- **Issue:** Status pills truncating task names — "Kampagnenziel definier..." and "Wettbewerber analysier..."
- **Root cause:** German status labels ("Abgeschlossen" = 13 chars, "In Bearbeitung" = 14 chars) are wider than EN ("Completed" = 9, "In progress" = 11), squeezing the task name text
- **Step 1:** Checked glossary — "Abgeschlossen" can be replaced with "Erledigt" (glossary maps "Done" → "erledigt"). "In Bearbeitung" is glossary-locked (no shorter alternative).
- **Step 2:** After using "Erledigt", if the "In Bearbeitung" pill still truncates → widen by 5px, check siblings, verify proportions
- **Result:** "Erledigt" saved 5 chars on one pill; 5px widen on the other resolved remaining truncation without sibling collision

## Learned: 2026-07-26

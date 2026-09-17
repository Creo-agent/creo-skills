# Fix Method #3: Orphan Word Resolve

## Trigger
QA vision detects a single word alone on the last line of a sentence/headline (orphan word).

## Global Rule
A sentence must NEVER end with a single word on its own line.

## Action Steps (in priority order)

### Option A: Incremental container widen (Method #10)
1. Check how much room exists between the text container and its nearest sibling / parent boundary
2. Widen the container by 5px — check sibling collision + proportion preservation
3. Verify text reflows to eliminate the orphan
4. If orphan persists → widen another 5px (up to 3× / 15px max per Method #10)
5. If orphan persists at max widen OR collision detected → proceed to Option B

### Option B: Shorten text
1. Check glossary for shorter alternatives for the longest words in the sentence
2. Remove non-essential words (e.g. possessive "deine/your" if meaning is preserved)
3. Rephrase to achieve shorter line length
4. If text change is glossary-compliant and meaning preserved → apply directly
5. If meaning is slightly altered → apply but add a reviewer note

### Option C: Escalate
If neither expanding nor shortening resolves cleanly → escalate to Designer Review with note.

## Decision Tree
```
Orphan detected?
├── Incremental widen (Method #10): 5px → collision/proportion check → orphan gone? → Done ✅
│   └── Still orphan? → +5px (max 3×) → still orphan or collision? → Try shorten text
├── Text can be shortened (glossary-safe)? → Apply shorter text → Done ✅
│                                           └── Meaning harmed? → Apply + reviewer note
└── Neither works → Escalate to Designer Review
```

## Constraints
- Incremental widen follows Method #10 rules: 5px steps, max 3× (15px total), sibling collision + proportion check at each step
- Text changes must be checked against glossary FIRST
- Preserve the semantic intent of the original EN copy
- Multi-word last lines are acceptable (the rule is specifically about ONE word alone)

## Example A — Successful fix
- **Asset:** AI_marketing_competitor_agent, de-DE
- **Before:** "Beobachte deine Mitbewerber 24/7 – mit KI-Agenten" → 3 lines, "KI-Agenten" orphaned on line 3
- **Tried:** Expanded container from 980px → 1080px — still 3 lines (75pt text too wide)
- **Tried:** Multiple rephrasing options ("dank KI-Agenten", "rund um die Uhr") — all still 3 lines
- **Root cause:** At 75pt Poppins SemiBold, the compound word "KI-Agenten" always wraps as a unit; no text edit short of removing a word fixes it
- **Resolution:** Escalated to Designer Review — meaning preservation ("deine" = personal CTA) outweighs the orphan rule. Text restored to full translation with reviewer note.

## Key Learning
Dropping words to fix orphans CAN harm meaning — "Watch competitors" is impersonal vs "Watch YOUR competitors" is a direct CTA. When text shortening alters meaning, prefer escalation over silent meaning loss. Always add a reviewer note when escalating.

## Learned: 2026-07-19

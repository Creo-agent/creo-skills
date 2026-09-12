# Ask, Don't Guess

## Contents
- The rule
- Trigger conditions
- The dead-space case — compute it, don't recall it
- What to ask
- After the answer
- Explicitly forbidden

---

## The rule

**When the master doesn't contain the answer, ask — never invent.**

This skill clones and transforms. Everything in the output should trace back to something in the
master or to something the user asked for. The moment you find yourself deciding what a design
*should* contain, you have left the job and started designing, and nobody approved that.

The pressure to invent is highest in exactly one situation: a canvas with space the master has no
material for. It looks unfinished, and adding *something* feels like completing the work. It
isn't — it is shipping unreviewed design decisions inside what the user believes is a resize.

## Trigger conditions

Halt and ask when any of these is true:

1. **Space with no source material.** The composition doesn't fill the usable area and the master
   offers nothing to fill it with. See the next section — compute the actual figure first.
2. **An element's role is ambiguous.** `derived.logoCandidates` / `iconCandidates` in the baseline
   are *suggestions*. If it isn't clear which node is the logo, headline or hero visual, list the
   candidates with their sizes and positions and ask. Guessing wrong here corrupts every
   placement, because the role map is a session-level artifact.
3. **A CTA was requested but the master has none**, and label or colour wasn't specified. There is
   nothing to copy from, so there is nothing to infer.
4. **Content doesn't fit even after a uniform scale-down.** Report the numbers and ask whether to
   scale further, drop an element, or reflow — don't pick one silently.
5. **Text still overflows at a sensible minimum font size.** R12 permits reducing size, not
   reducing it without limit. Below roughly 60% of the master's size the hierarchy breaks, and
   that is a creative decision.
6. **An exclusion leaves a zone visibly empty.** Hiding the integration row may leave a gap that
   reads as a mistake. Say so before delivering it.
7. **A placement was asked for that this skill doesn't cover** — the DV sizes. Say plainly that
   the skill covers social placements now and ask whether to add it back, rather than improvising
   a layout from the removed rules.
8. **Placements need to differ and only one was briefed.** If the Story needs a CTA the feed sizes
   don't, confirm rather than assuming the brief carries across the set.
9. **Two applicable rules conflict.** (F6, Ad-Specific QA Checklist — Rachel.) E.g. keeping a
   header's proportions exactly as-is would push a resized CTA below its minimum touch size. Flag
   it to the user with the choice you made and the reasoning — don't silently pick a winner.
   Optionally duplicate the frame with the alternate rule applied, so the user can compare both
   rather than take your word for which is better.

## The dead-space case — compute it, don't recall it

**This number has moved twice already — recompute from `placements.json` every time, never from
a cached figure in this file or a previous session's summary.**

The Story usable area is currently **950 × 1180**, a ratio of **0.805** — noticeably portrait,
not square (superseded 2026-09-01; see `PLACEMENTS.md`'s STORY section for the full correction
history).

Fitting a master into that box:

| Master | Ratio | Fitted | Vertical slack | Horizontal slack |
|---|---|---|---|---|
| 4:5 | 0.800 | 944×1180 | **0** | 6 |
| 1:1 | 1.000 | 950×950 | **230** | 0 |
| 3:2 | 1.500 | 950×633 | 547 | 0 |
| 16:9 | 1.778 | 950×534 | 646 | 0 |

**Two prior conclusions from earlier sessions no longer hold and should not be repeated:**

- *"A 1:1 master leaves only 29px, essentially a clean fit."* That was true against the
  2026-08-31 usable area (950×979, ratio 0.970 — nearly square). The current usable area is
  meaningfully more portrait, and a 1:1 master now leaves **~230px** — well past this file's own
  "raise it with the user" threshold below.
- *"Converting a 1:1 master to 9:16 always creates ~400–450px of dead space."* Still wrong as a
  blanket claim for the same reason it was wrong before: that figure belongs to a **16:9** master
  (646px now, was 445px), not a 1:1 one.

The lesson generalizes past this specific number: **this table is a live computation against
`usableArea`, not a fact about Story.** Every time the safe zone changes, this table changes with
it, and whichever conclusion was true last time may not be true this time. Recompute; don't recall.

Do not open the four-options conversation reflexively on every Story — compute the slack against
the current `usableArea`, and raise it only when there is genuinely something to decide (roughly
150px+, per the threshold below). Raising it when the answer is 6px trains the user to ignore the
question; failing to raise it when the answer is 230px ships an unreviewed creative decision.

Note the visual is not the only thing in the usable area — logo, headline and any CTA take their
share, so the real slack is smaller than the table's. The table bounds the problem; it doesn't
solve it.

**When the slack is genuinely significant** (say, more than ~150px after everything is placed),
present it as a creative decision with these options, and let the user choose:

1. **CTA lockup** — a call-to-action button plus optional supporting text (needs copy).
2. **Brand bar** — logo with tagline or URL at the bottom of the usable zone.
3. **Background extension** — extend the master's existing background colour or gradient into the
   space, adding no new elements (R27 — master colours only).
4. **Leave it** — legitimate when the visual is strong enough to carry the format.

## What to ask

Ask once, concretely, with the numbers in hand. Not *"how should I handle the empty space?"* but:

> The 1:1 master fits the Story usable area at 950×950, leaving **230px** below the visual
> (usable band is y 200–1380 — the platform's own UI covers everything outside it). Four ways to
> handle it: a CTA lockup (I'd need the label), a brand bar with logo plus tagline or URL,
> extending the existing background gradient into the space, or leaving it. Which?

Batch related questions into one message. If three things are unclear about the same placement,
ask all three at once rather than stopping three times.

## After the answer

- **Record it.** If the answer applies to the whole set, carry it forward across placements and
  say that you did (`BATCH-WORKFLOW.md`).
- **If the answer adds an element**, it is now part of the brief — but it is still not in the
  master, so `no_invented_elements` (R13) will flag it. Log it as an **accepted gap with the user's
  instruction as the reason** (`ACCURACY-GATE.md`), so the report shows the element was requested
  rather than fabricated.
- **If the answer is "leave it"**, that is also a decision worth recording, so the next session
  doesn't re-raise it.

## Explicitly forbidden

Regardless of how good it would look:

- Inventing shapes, patterns, gradients, glows or textures to fill space (R13, R27).
- Adding a second logo, or duplicating any element, to balance a composition (R11).
- Writing CTA copy, headlines or taglines the user didn't supply (R12).
- Repeating or padding existing text to fill a container (R12).
- Cropping the visual so the composition looks intentional (R10).
- Substituting a Unicode glyph or emoji for a real icon (R16) — it passes every numeric check and
  disappears at frame zoom, which is precisely why it is tempting and precisely why it is banned.
- Deciding an ambiguous element's role and proceeding quietly.

# Design-File Gaps

## Contents
- Tab/carousel/accordion panels with no real content behind them
- A text placeholder must be styled exactly like the real text it replaces
- All-expanded as an authoring convenience
- "Already built" is not "current content matches"
- "Same as X page" sections — copy approved HTML, don't rebuild from scratch
- A text node's own color can fail contrast against its own background

Figma files are sometimes incomplete or left in a convenience state that doesn't match real UX
intent. This file covers what to do when the design source itself has a gap — distinct from
`ASK-DONT-GUESS.md`, which covers unspecified *behavior*; this file covers unspecified or
inconsistent *content*.

## Tab/carousel/accordion panels with no real content behind them

Figma will happily show a full tab bar or accordion list with only some panels actually
populated behind it — a confirmed real case: a 6-tab bar with only 1 built content panel, and a
3-item accordion with only the first item's answer text present. Nothing in the visual design
signals this; the label row looks complete.

**Before building any tab/carousel/accordion component, check `get_metadata`'s child list for
the actual number of populated panels** — don't assume every visible label has matching content
just because the tab bar itself looks finished.

**When a gap is found:**
- Wire the interaction fully (all tab buttons toggle their active visual state correctly).
- **Never fabricate content** for the missing panels.
- Flag it explicitly as a design-file gap in the delivery notes — this is not a build defect,
  it's an incomplete source file, and saying so clearly prevents it from being read as a bug in
  the build.

This is also an `ASK-DONT-GUESS.md` trigger if the missing content's *absence* makes the
section's overall interaction model ambiguous (e.g. is the empty panel meant to be static
forever, or is content coming later?) — ask rather than assume either answer.

## A text placeholder must be styled exactly like the real text it replaces

When a gap above is filled with placeholder copy (e.g. "Details coming soon."), the instinct is
to visually mark it as provisional — italicize it, mute the color, otherwise make it "look like
a placeholder." A confirmed real case: a first pass styled a placeholder accordion description
in italic, muted grey, and got corrected directly: *"text placeholders should always have the
style of the texts it should replace... here it is italic light or something different from the
paragraph styling."*

**Placeholder text must inherit the exact same font, weight, color, and style as the real
content it stands in for.** If the provisional nature needs to be signaled at all, do it through
the copy itself (wording like "...coming soon") or through a distinct *structural* treatment —
an abstract skeleton shape replacing prose entirely, the way a loading skeleton or a solid-grey
media fallback works — never by degrading real-looking typography. Restyled prose reads as a
rendering bug, not as an intentional placeholder state.

This is the typographic counterpart to `HARD-RULES.md` H16's item 3 (a placeholder must match a real
element's *size* structurally, e.g. `align-items: stretch`) — same principle, applied to text
styling instead of box dimensions.

## All-expanded as an authoring convenience

Design files sometimes show every accordion/FAQ item in its expanded state simultaneously — a
convenience for the designer to review all the copy at once, not the intended default runtime
state. A useful confirming signal: every item shows the "expanded" chevron/icon state at once,
which is not how a real accordion behaves for a user.

**Build to real UX intent** (single-open, default-collapsed for an accordion; whatever the
component's real interaction convention is) **rather than copying the literal all-expanded
visual state verbatim.** This is a judgment call about matching intent over literal appearance —
the same category of decision as inferring sensible defaults elsewhere in this skill. State the
deviation explicitly in the delivery notes so it's a documented choice, not a silent one.

## "Already built" is not "current content matches"

If a prior build of a similar/shared section exists (e.g. a component reused across multiple
pages of the same site), its existence does **not** mean the content is still current. A real
case: a previously-built 7-card carousel with placeholder tag copy turned out to have only 2
real cards with different, newer copy in the live Figma file by the time it was revisited.

**Always re-verify against live Figma content before reusing a prior build** — especially for
components likely shared or reused across multiple pages, which may have been customized
independently since the earlier build ran. The prior build's *structure* (CSS layout, JS
behavior, H9 flatten pattern for its visuals) is usually still valid and worth reusing — only
the content needs re-verification, not necessarily a full rebuild.

## "Same as X page" sections — copy approved HTML, don't rebuild from scratch

When a section is explicitly described as identical to one on an already-approved page (e.g.
"same hero as PMO," "logo bar identical to Marketing"), the instinct is to rebuild it from
Figma specs to match the reference visually. That instinct is wrong — and expensive.

Confirmed real case (Marketing page, Aug 2026): the customer stories section was rebuilt from
scratch 5+ times, each attempt producing a different failure (duplicate text layers from flat
images + HTML text, wrong flex behavior, opacity issues, injected PMO CSS breaking other
sections). When the literal approved HTML was copied from the source page and only the content
was swapped (heading text, body text, image URLs, alt text), the result was 9.5/10 immediately.
The logo bar had the same pattern — first attempt from scratch had wrong spacing/sizing; direct
copy was correct on the first pass.

**The rule:** when a section is confirmed identical to an approved, already-built section on
another page:
1. Extract the exact `<section>...</section>` block from the source page.
2. Extract only the CSS classes used by that section (grep for specific class names in the
   source page's `<style>` blocks).
3. Scope the CSS with unique prefixes if needed to avoid conflicts with the target page.
4. Swap ONLY: heading text, body text, image URLs, alt text, and any section-specific IDs.
5. Keep ALL class names, structure, nesting, and behavior identical.
6. Screenshot the source section vs. the target section side by side before shipping.

**When this does NOT apply:**
- The source section's CSS depends on an external bundle (see `GOTCHAS.md` — extracted
  live-site HTML with external CSS dependencies). In that case, rebuilding self-contained
  HTML/CSS from Figma is cheaper than patching external-dependency failures.
- The section has been modified since its last approval — always re-verify against live Figma
  content before reusing (see "Already built is not current content matches" below).
- The section needs structural changes (different number of cards, different layout) — at that
  point it's a new section, not a copy.

**Why this matters for this skill specifically:** `CLAY-INTEGRATION.md` covers resolving against
Clay's coded component library, and `SECTION-WORKFLOW.md` covers building from Figma. But
neither covers the case where a pixel-perfect, approved, self-contained HTML section already
exists from a prior build. That prior build is a stronger starting point than either Clay or
raw Figma — it's already been through QA, already has self-contained CSS, and already renders
correctly. Use it.

## A text node's own color can fail contrast against its own background

This is the one case where `CLAY-INTEGRATION.md`'s "Figma wins" principle has an explicit
exception (see its governing principle). A confirmed real case: a text node's extracted color
failed WCAG contrast against its own resolved background (~1:1, effectively invisible), while
every visually-similar sibling element in the same composite used a readable treatment —
strong evidence this is a source-file authoring bug, not a deliberate design choice.

**Correct to evident intent** (use the surrounding pattern — how visually-similar elements
elsewhere in the same composite handle the same relationship — as the signal for what that
intent was), and **log the deviation explicitly**: which value was overridden, and why. Never
silently ship the literal failing value ("Figma wins" doesn't apply to a genuine accessibility
floor violation), and never silently fix it without logging it either — a contrast override is
exactly the kind of deviation `ACCURACY-GATE.md`'s accepted-gap logging exists for.

# Ask, Don't Guess

## Contents
- The rule
- Trigger conditions (halt the build)
- What to ask
- After the answer
- Explicitly forbidden

## The rule

**When this skill doesn't know what a section should do, it stops and asks. It never invents
interactivity.** This is a hard gate, not a preference — guessing produces plausible-looking
output that silently diverges from intent, which is the most expensive failure mode because it
*passes* visual QA (it looks fine) while being wrong in a way nobody asked for.

## Trigger conditions (halt the build for that section)

Any one of these halts the section's build and requires a question before continuing:

- The section resolves to `ATOMS_ONLY` or `BORROWED` in `CLAY-INTEGRATION.md` — nothing in Clay
  covers it, so there's no coded behavior to inherit and no reference to copy from.
- Figma shows an interactive affordance (chevron, tab bar, arrows, dots) but the file contains
  no populated panels/slides behind it — the intended behavior is genuinely unspecified in the
  source (see `DESIGN-FILE-GAPS.md`).
- Figma shows a static state that clearly implies motion or transition, but nothing specifies
  the trigger, direction, duration, or easing. **A static frame is often the resting frame of a
  moving component — learn the tells and treat each as a positive detection, not a style choice:**
  - **Wide text clipped at / overflowing its frame edge** → a **marquee / scrolling ticker**, not
    a static centered headline. `section_spec.py textsize` surfaces this tell mechanically
    (`clipped`/`marquee_tell`). Confirmed real case: a persona page's agents headline shipped
    static and edge-clipped; it was a horizontal marquee in the reference, and the clip was the
    only tell.
  - **A horizontal strip of peer cards with one emphasized** → a **carousel or hover-expand**.
  - **Duplicated / frame-sliced repeating items** → a **looping track** (content duplicated for a
    seamless wrap).
  **Anti-rationalization clause: when a frame carries one of these signatures, the default
  hypothesis is motion.** Do not talk yourself into "it's a deliberate edge-clip / a designed
  static row" to avoid halting — that exact rationalization shipped a static marquee once already.
  See a tell, fire the trigger: the burden is on positive evidence to conclude "genuinely static."
  Even when the tell is clear, the trigger/direction/timing/mechanism are still unspecified, so
  this routes through the question below rather than a guessed implementation. Cross-ref
  `PRE-BUILD-VERIFICATION.md` item 21 — the visual-side counterpart of this list.
- A logo / brand mark is called for but no real vector exists anywhere — not in the Clay DS logo
  library and not exportable from the Figma node. **Halt; never recreate, trace, or approximate a
  logo** (see `HARD-RULES.md` H33). A hand-made wordmark passes every gate and still reads as
  broken.
- The section is a video placeholder, or otherwise marked as future/incomplete content.
- Multiple plausible interaction models fit equally well — e.g. auto-advancing vs. click-only
  carousel; single-open vs. multi-open accordion; Phase 1 in `CLAY-INTEGRATION.md` landed on
  `CLOSEST` or `BORROWED` and the specific adaptation isn't obvious from the reference alone.
- **The section has ≥2 controls that must share one piece of state** (tabs + dots + auto-cycle +
  a sliding carousel; a multi-step form; an accordion whose panels also drive a progress
  indicator). This is a distinct trigger from "behavior is unspecified" — Figma's *intent* may be
  perfectly clear here, but the sheer number of interdependent moving parts means a single wrong
  assumption about the state model (what drives what, what happens at an edge/loop, timing,
  pause/resume) compounds across every control and is expensive to unwind after the fact.
  Confirmed real case: a tabs+dots+carousel+auto-cycle section took 5+ rounds of reactive fixes
  because the state model (leading/trailing clones for a seamless loop, dot-to-slot index
  mapping, pause-then-resume timing) was designed incrementally instead of confirmed once up
  front. **Present a concrete plan before writing any code** — the proposed state model
  (single shared index or equivalent), what happens at each edge case (loop-around, out-of-range
  clicks), and the timing/pause behavior — and get it confirmed, the same way a content brief
  gets confirmed for unspecified behavior. See `PRE-BUILD-VERIFICATION.md` for the parallel
  checklist on the *visual* side of a complex section.

## What to ask

One batched `AskUserQuestion` per section (never a vague "what should this do?"):

1. **Interactivity brief** — what should it do on load, on hover, on click, on scroll? Any
   auto-advance? Any state that persists across interactions?
2. **Reference** — is there an existing live page, URL, Storybook story, competitor example, or
   prior build that demonstrates the intended behavior? A link is worth more than a description
   — ask for one explicitly, don't accept a text description alone as sufficient when a
   reference could exist.
3. **Fallback if unspecified** — should it ship static for now (flagged as such in the
   delivery), or is a documented best-guess acceptable? **If a best-guess is authorized, it must
   be explicitly labeled as a guess in the delivery notes** — never presented as if it were a
   confirmed match to the design intent.

## After the answer

- Record the answer in the session's trace file so it reaches the knowledge-capture step at the
  end of the build (a recurring pattern here is worth promoting into `DESIGN-FILE-GAPS.md` or
  `CLAY-INTEGRATION.md` for future builds).
- If a reference link was supplied, treat it as a secondary source of truth for **behavior
  only** — Figma still governs appearance. Don't let a reference page's visual style leak into
  the section; only its interaction model.
- If no user is available to answer (a fully unattended/automated run), the conservative default
  is static with an explicit flag — never silently pick an interaction model to keep the run
  moving.

## Explicitly forbidden

- Silently choosing an interaction model because it seems reasonable.
- Asking the user which Clay component to use when H28 already identified a Clay-Web library
  instance or a `connections.json` name match — look it up, don't ask.
- Copying a Clay component's default behavior onto a section Clay doesn't actually cover, just
  because it's nearby or similar-looking.
- Implementing motion whose timing/easing was never specified, beyond the baseline H5
  interactivity that's genuinely generic (scroll-reveal, sticky nav — see `HARD-RULES.md`).
- Shipping a fabricated content panel to fill an empty tab/accordion item — wire the toggle,
  leave the content gap visible and flagged (see `DESIGN-FILE-GAPS.md`).
- Recreating, retyping, tracing, or AI-generating a logo/brand mark when no real vector is
  available — use the real vector (Clay repo → Figma SVG export) or stop and ask (`HARD-RULES.md`
  H33). Never invent a placeholder logo.

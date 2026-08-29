# Pre-Build Verification — One Pass, Not Five Reactive Ones

## Contents
- Why this file exists
- Tier 0 — the mechanized pass (`tools/section_spec.py`)
- The checklist — run before writing any CSS
- How to check each item cheaply
- The batching rule — when a QA issue is found
- Logging — make "ran clean" distinguishable from "never ran"
- Cross-references

## Why this file exists

A single section (a tabs + dots + auto-cycling card carousel) took over a dozen rounds of
back-and-forth to get right. Read the sequence of what was wrong, in order: tab height (built at
Clay's default 54px, real value ~30px), active-tab fill color (guessed a token, real value was a
different token entirely), a border that doesn't exist in Figma, card overlap amount (built as a
positive gap, real Figma overlaps cards by ~59%), card padding (built edge-to-edge, real Figma
insets everything by 12px), the carousel's own mechanism (Clay's real component slides one card
at a time; Figma shows three simultaneously) — **every one of these was a property that could
have been checked against real Figma data in the first pass**, and every one was instead found
by the user pointing at a screenshot after the fact. None of these were hard to check — they were
just never checked *before* writing the CSS, only *after* someone noticed the result looked off.

**The rule going forward: run the checklist below once, before writing a single line of CSS for
any section with real visual complexity (a matched Clay component, overlapping elements, a
custom color, anything with a border/shadow/radius that matters). Verifying five properties in
one pass costs about the same as verifying one — the expensive part is the round-trip with the
user, not the extraction call itself.**

## Tier 0 — the mechanized pass. Run this FIRST, every section, no judgment involved.

This checklist grew from 10 items to 20 by reacting to bugs, and the items that kept escaping
were not the obscure ones — they were the ones where the rule said *what* to verify but not *the
command that produces the number*. "Verify the fill color" is a thing to remember; `bg ref.png`
is a thing to read. Four such classes are now mechanized in `tools/section_spec.py`. Run all four
before writing CSS and paste the output into the trace — they take one command each and they
cannot be "done from memory":

```bash
T=~/.claude/skills/figma-to-web/tools/section_spec.py

# 1. Section background vs. content-block fills. Reports the perimeter ring and the scanline
#    run structure SEPARATELY, so a card fill can never be read as the section background.
python3 $T bg /tmp/<slug>-figma-ref.png --orig-width <design-frame-width>

# 2. Font size for any text whose size you did not get as an explicit number. Divides the
#    screenshot's own scale factor out for you.
python3 $T textsize /tmp/<slug>-figma-ref.png --box X,Y,W,H --orig-width <design-frame-width>

# 3. How many text elements a body block needs. One TEXT node = one <p>.
python3 $T textnodes /tmp/<slug>-metadata.json --node-id <nodeId>

# 4. Background color BAKED INTO each exported asset vs. the fill it will sit on.
python3 $T assetbg output/<page>/images/<slug>/*.png --on '<container-fill-hex>'
```

`overlap` is the fifth subcommand and belongs earlier still — at manifest time, once per page,
not per section (see `FULL-PAGE-WORKFLOW.md` Step 2).

**Why these four and not others.** Each one is a question with a single correct answer that does
not depend on the design being built, and each one fails *silently* — the built section looks
plausible, so vision QA passes it:

| Class | The wrong answer still looks right because… |
|---|---|
| Section background vs. block fill | a sample taken inside a content block is a real color that is really in the design — just not the section's |
| Font size | a 20% size error on a single text element reads as a style choice, not a defect |
| Text-node count | one `<p>` with `<br><br>` and two `<p>`s can render identically and differ in every DOM assertion |
| Color baked into an exported asset | the art in the asset is correct; only its margins are wrong, and they're only wrong against *some* fills |

The general lesson underneath all four: **a wrong number doesn't just cause a bug, it supports a
plausible wrong theory** — and a confident wrong theory costs more to unwind than the defect it
was invented to explain. Any of these measured up front is one line of output; inferred and wrong,
it is a fix, a re-QA, and often a second defect introduced by the fix.

Everything below is Tier 1 — it needs eyes and judgment, which is exactly why it should not also
be carrying the four items above.

## The checklist — run before writing any CSS

For the section's root frame and every visually distinct sub-element (cards, tabs, pills,
badges — anything with its own fill/border/radius/spacing):

0. **H28 — Clay-Web instance or Clay name, before this list.** If `get_metadata` shows this
   section (or a child) is an INSTANCE from Clay Web (`LyYrDV2oALKuPoePY9aeJJ`) or the name
   matches `connections.json`, Phase 1 must already have an EXACT/CLOSEST coded Clay anchor.
   Do not run this visual checklist as a from-scratch pixel build that skipped that lookup.

1. **Size** — height and width, from `get_metadata`'s real coordinates. Never trust a matched
   Clay component's own default size (button size, tab height, card height) without checking.
2. **Fill color** — if it's not an obvious `black`/`white`/pure design-token gray, **sample real
   pixels** from a `get_screenshot` capture rather than eyeballing a color and picking the
   nearest-sounding token name. Two visually-similar light-purple tokens (e.g. iris-100 vs.
   iris-200) can look identical at a glance and still be wrong.
3. **Text color** — same rule. Don't assume a colored fill implies colored text (confirmed real
   case: a purple-filled active tab had plain black text, not purple).
4. **Border presence** — if an edge looks like it might be a border, sample a pixel line across
   it. A soft gradient into the background is a shadow; a hard-edged flat color is a border. They
   are not interchangeable and look different at a glance only if you're looking for it.
5. **Corner radius** — check against Clay's real radius tokens (`--clay-radius-sm/md/...`) but
   verify the *pairing* (which element gets which radius) rather than assuming every rounded
   thing uses the same one.
6. **Padding/inset** — measure the gap between a container's own bounds and its content's bounds
   via `get_metadata` coordinates (child x/y/width/height vs. parent's). Never assume content is
   edge-to-edge just because a matched Clay component's default renders that way.
7. **Overlap or gap between siblings** — if elements visually overlap or sit unusually close,
   compute the actual overlap from real x-coordinates (see `CLAY-INTEGRATION.md`'s worked
   example: two card x-positions minus a width, expressed as a fraction of card width) — don't
   default to a token-driven positive `gap`.
8. **Element order** — sort by real x/y position, not document/child order. A Figma group's
   children list is z-order or authoring order, not necessarily left-to-right/top-to-bottom (see
   `FIGMA-EXTRACTION.md`).
9. **Layout mechanism, not just values** — if a Clay component is the anchor, confirm its real
   coded behavior via **`renderSection()` static output or a rendered Storybook/Chromatic story**
   matches Figma's arrangement structurally, not just in color/spacing. Do not infer mechanism
   from `.tsx` or `.module.css` source. A "one item visible at a time" component and a "three
   items visible, center focused" composition are not the same mechanism even if they share a
   component name.
10. **What happens at scale/viewport extremes** — if a fix removes a width constraint (e.g. "make
    this full-bleed"), work through what that implies at the *widest* realistic viewport before
    shipping: does more content become visible than intended? Does clipping move to a different,
    equally-wrong boundary? Reason through the consequence once, rather than shipping the narrow
    fix and waiting for the next symptom to surface it.
11. **Live HTML overlaid on a scaling raster composite** — if any text/icon/badge sits on top of
    a flattened image or percentage/`aspect-ratio`-based composite (H9 assets, media-with-caption
    patterns), check whether that overlay needs to shrink in lockstep with the composite at
    narrow widths. A fixed-px or `vw`-sized overlay drifts out of proportion with the baked-in
    art (confirmed real case: a caption pill overlapped a card that was part of the same
    composite once the composite dropped below ~700px). Fix by giving the composite's own
    wrapper `container-type: inline-size` and sizing the overlay's font/padding/icon-size in
    `cqw` (relative to that wrapper, not the viewport), clamped between a legibility floor and
    the original Figma px value as the ceiling.

12. **Gap between the text block and the primary visual asset** — the gap from the bottom of the
    last text/CTA element to the top of the section's main visual (mockup, illustration,
    screenshot composite) is frequently wrong if derived from design-context code alone. The
    code uses absolute positions (`top: 374px`) not relative gaps, so derive the gap explicitly:
    gap = visual_top_y − text_block_bottom_y, both from `get_metadata` pixel coordinates. This
    single value is easy to miscalculate by 40–50px and is immediately visible in QA (confirmed:
    a 52px gap built as 3px, caught only by visual comparison against the Figma reference).
13. **Section padding-bottom formula** — when a content frame sits inside a larger background
    frame, `padding-bottom = bg_height − padding_top − content_frame_height`. Verify this
    arithmetic before writing CSS rather than guessing a round number. Over-estimating
    padding-bottom adds a large blank band of background color below the last element that is
    invisible in the Figma (confirmed: 167px used where 139px was correct, creating a visible
    blank-band artifact).
14. **Container max-width and side padding against the page's own established convention** —
    before using this section's own Figma frame width as its container's `max-width`, `grep`
    the page-in-progress for the convention every prior section already uses (a token like
    `--clay-layout-container-large`, or a hardcoded px value if no token exists). After
    `PAGE-STRUCTURE.md` is in the shell, that convention lives on `.container-large` /
    `.padding-global` — `grep` those classes first, then any leftover per-section max-width. A reused prior
    build's or a live-reference section's own literal frame width is not automatically the right
    value — two real sections on the same page each silently used their own instance's literal
    width (1120px, 1344px) instead of the shared 1440px container, and two others used the
    mobile-only padding token with no desktop override, all invisible until every section's real
    rendered width was measured side-by-side (`getBoundingClientRect()` on each section's inner
    container at the same viewport — see `HARD-RULES.md` H22). Check this for every section,
    not just visually-complex ones — a plain text/CTA section is just as likely to silently
    carry the wrong container width as a carousel.
    **And check the arithmetic, not just which number.** Under the near-universal
    `box-sizing: border-box`, padding lives *inside* `max-width`, so
    `max-width: <figma-content-width>` with any horizontal padding produces a content box narrower
    than Figma by the sum of both paddings. Two rules follow:
    - The value to **write** is `figma_content_width + padding_left + padding_right`.
    - The value to **verify** is `getBoundingClientRect().width − paddingLeft − paddingRight`,
      compared to the Figma content width, delta 0.
    Measuring the box width instead of the content width will confirm the bug as correct, which is
    why the verification is a subtraction and not a reading. This class of error is **systematic in
    cause but sporadic in occurrence** — it appears wherever the pattern was copied and not
    wherever it wasn't, so any single section can be right while most are wrong, and it only reads
    as a pattern when every section is measured in one pass (`ACCURACY-GATE.md` step 1b).
    It is also invisible to the eye by construction: the whole layout shrinks proportionally.
    Look for it in two places where it stops being invisible — a fixed+flexible column grid, where
    the entire shortfall is absorbed by the flexible column alone, and any asset whose natural
    width equals the container width, which then gets `object-fit`-cropped by the padding amount
    per side.

15. **Clay-default visual properties not present in Figma** — When a Clay component is the
    anchor for a section, its defaults (border-top/bottom dividers between list/accordion items,
    extra padding on triggers, default background fills, focus-ring styles, shadow tokens) are
    **not automatically correct for this Figma design**. Before shipping any Clay-anchored
    section, visually audit every Clay-added property against the Figma screenshot:
    - Accordion/tab triggers: Clay adds `border-top` dividers by default — if Figma shows none,
      remove them and switch to a `gap`-based spacing model on the parent.
    - List/card items: Clay may add `border`, `box-shadow`, or `background` defaults — verify
      each against a `get_screenshot` pixel sample before keeping.
    - Interactive states: Clay's hover/active fills may differ from Figma's intent — check via
      `get_variable_defs` for any token override.
    The rule is: **Figma is the truth, Clay defaults are a starting point**. Any Clay property
    that has no visual evidence in the Figma screenshot must be removed, not kept on the
    assumption that it "probably belongs there." (Confirmed real case: Clay accordion `border-top`
    dividers between items appeared in HTML but not in Figma — removed after user flagged them
    during QA; see session trace 2026-08-26.)
16. **Orientation of every flattened logo/icon/wordmark image** — a `get_design_context` React
    snippet sometimes wraps an image in `-scale-y-100` or `-scale-x-100` (Figma's own fix for an
    asset whose raw exported file is authored upside-down or mirrored). That wrapper is easy to
    drop when converting the snippet to a plain `<img>` — nothing else about the markup looks
    wrong, and a logo that's the right color/shape/size at a glance can still be upside-down
    (confirmed real case: a Gartner logo shipped inverted, caught only via a user screenshot,
    not by the per-section QA pass that had already run and "passed"). Before shipping any
    flattened brand logo/icon/wordmark:
    - Check whether the original design-context snippet wrapped it in `-scale-y-100` or
      `-scale-x-100`. If so, and there's no `rotate-180deg` on the *same* element canceling it
      out (see `HARD-RULES.md` H23 — the two combined net to identity), reproduce the flip in
      CSS (`transform: scaleY(-1)` / `scaleX(-1)`).
    - Look at the rendered result and ask specifically "is this upright and correctly mirrored,"
      not just "is this present and roughly the right size" — orientation is a distinct check
      from placement/sizing, and a quick glance at a familiar brand mark can miss an inversion
      that a deliberate look would catch immediately.

17. **Every leaf element's own centering, not just its wrapper's** — when centering a group
    (logo + heading + description, icon + label, etc.) via an ancestor's `text-align: center` or
    `align-items: center`, verify each visually distinct child's own `getBoundingClientRect()`
    center against the container's center individually — not just the outer wrapper's. An `<img>`
    is the highest-risk case: `text-align: center` only affects inline-level content, and a
    common `img { display: block }` reset (see `HARD-RULES.md` H24) silently turns every image
    into a block box that inherited `text-align` cannot center at all, with no visible error and
    no effect on any sibling `<p>`/text element in the same group. **This check applies just as
    much when *verifying a reported bug* as when building the first pass** — confirmed real case:
    a wrapper div measured as centered was wrongly reported back as "no bug" before someone
    measured the `<img>` inside it individually and found it 90px off-center. If a user reports
    something as "not centered," measure the specific element they're pointing at, not the
    nearest container that happens to wrap it.

18. **Section background color — sample the PERIMETER, never inside a content block.** A section's
    background is the color *surrounding* its content: the outer edge and the gutters between
    blocks. A pixel taken inside a card reports that card's fill, which is a real color in the
    design and the wrong answer to the question asked — and because it *is* a real color, the
    resulting build looks deliberate rather than broken. Mechanized: `section_spec.py bg` prints
    the perimeter ring and the whole-image histogram **separately** for this reason: the ring is
    the section background; the histogram is a cross-check that any full-bleed block can outrank.
    Two corollaries that decide real builds:
    - If a block's fill differs from the section's, the section keeps its own background and the
      block gets its own — never promote a block fill to the section.
    - If `bg` reports **no** block fill distinct from the section background, the blocks share the
      section's fill: give them no `background` rule at all. That is not the same finding as "the
      section is white."
    Getting this backwards has a characteristic signature worth recognizing: setting the section to
    a block's fill makes that block *disappear* into its own container, which looks like a new bug
    and invites a second wrong fix.

19. **Background color BAKED INTO every exported asset vs. the fill it will sit on.** **Figma
    composites a solo-exported node onto white, not onto its parent's fill.** Any node whose own
    background comes from an ancestor therefore exports with an opaque white slab in its margins.
    Placed on a non-white container, that slab covers the container's fill wherever the asset
    extends. Nothing about the asset looks wrong in isolation: the art is right, the size is right,
    only the margins are the wrong color. Mechanized:
    `section_spec.py assetbg *.png --on '<container-fill>'`.
    **Check every asset, not a sample of them** — this defect is present or absent per asset, and
    it is *invisible* on any asset whose container happens to be white or near-white. A set of
    assets where most containers are light will look entirely correct while carrying the same defect
    throughout; the one that shows up is the one whose container is a saturated or tinted fill, and
    it will read as a section-background problem rather than an asset problem.
    - **The fix is re-exporting, never post-processing.** Export the smallest **ancestor** node
      that contains both the parent fill and the art, and place it as the element's full-bleed
      background (`position: absolute; inset: 0; object-fit: cover`), keeping text/CTA as live
      HTML siblings above it.
    - **Do not flood-fill the baked color to transparent** — it cannot work in general, not just
      in practice. Real UI art usually contains white or near-white elements of its own (cards,
      bubbles, input fields, sheets), and any one of them that touches the baked margin is
      edge-connected to it with no boundary in between. Once Figma has baked one color for both the
      background and the artwork, no post-process can separate them: the fill either stops short of
      the real background or eats part of the art.
    - Re-run `assetbg` whenever a container's fill changes, and prefer assets with real
      transparency — they report `alpha: has transparency` and cannot cover anything.

20. **Number of TEXT nodes in a block = number of text elements in HTML.** Count the block's TEXT
    descendants before writing markup, rather than reading the rendered copy and deciding where the
    breaks belong. N Figma TEXT nodes are N elements with real spacing between them — never one
    element with `<br><br>`, and never the reverse (one wrapped TEXT node split into several
    elements because the copy reads like separate thoughts). The rendered result can be nearly
    identical while the DOM, the spacing model, the responsive reflow, and anything that consumes
    the markup are all wrong. Mechanized: `section_spec.py textnodes <metadata> --node-id <id>`
    prints the count and each node's characters. Cross-check against `textsize`'s band-gap output:
    a gap between ink bands that is much larger than the rest is a paragraph boundary; a uniform
    gap is line leading inside one node.

21. **Motion & interaction tell-list — a static Figma frame can be the *resting frame* of
    something that moves.** Figma exports one frozen state; a signature baked into that state is
    frequently the *only* evidence that the real component animates or reacts, and building the
    frozen frame verbatim ships a dead version of a live thing that then passes visual QA (it
    looks like the design, because it *is* one frame of the design). Treat each signature below as
    a **positive detection** that routes to `ASK-DONT-GUESS.md` (halt and confirm the interaction
    model) — not as a static style to reproduce:
    - **Wide text clipped at, or overflowing, its frame edge** (a headline cut mid-word, a line
      wider than its container that doesn't wrap) → almost always a **marquee / scrolling
      ticker**, not a centered static headline. Mechanized: `section_spec.py textsize` flags this
      as `clipped`/`marquee_tell` when a band's ink reaches both box edges. Confirmed real case: a
      persona page's agents headline shipped as a static edge-clipped centered line — it was a
      horizontal marquee in the live reference, and the edge-clip was the tell (it was even
      wrongly recorded in project memory as a deliberate edge-clip before being corrected).
    - **A horizontal strip of peer cards with one visually emphasized** (larger, filled, lifted,
      focused) → a **carousel or hover-expand**, not a static row.
    - **Duplicated or frame-sliced repeating items** (the same card/logo appearing twice, an item
      cut by the frame boundary) → a **looping track** whose content is duplicated for a seamless
      wrap.
    **The anti-rationalization rule:** when a static frame carries one of these signatures, the
    default hypothesis is *motion* — the burden is on positive evidence to conclude "genuinely
    static," never the reverse. Do not talk yourself into "it's a deliberate edge-clip / a
    designed static row" to avoid halting; that exact rationalization shipped a static marquee
    once already. A tell only establishes that motion is *likely* — it does not specify the
    trigger, direction, timing, or mechanism, all of which stay unspecified — so a detected tell
    still routes through `ASK-DONT-GUESS.md`'s question rather than licensing an invented
    interaction. See `HARD-RULES.md` H31 (the hard-rule form) and `ASK-DONT-GUESS.md` (the
    interactivity-side counterpart of this list).

## How to check each item cheaply

- **Coordinates/order/padding/overlap**: `get_metadata` on the section and its children — free,
  no image fetch, already the first call in every build.
- **Colors/borders**: one `get_screenshot` capture, then sample pixels with Python/Pillow
  (`im.getpixel((x, y))`) rather than reading them off a rendered thumbnail by eye. A few lines
  of `for x in range(...): print(im.getpixel((x, y)))` across a suspected edge tells you
  definitively whether it's a border or a shadow gradient.
- **Component mechanism**: run `renderSection()` for the matched component, or load its rendered
  Storybook/Chromatic story and inspect DOM + computed CSS — do this *before* writing the
  section's own CSS, not after a mismatch is reported. Never read `.module.css` or `.tsx` as the
  build input (`CLAY-INTEGRATION.md` rule 1).

## The batching rule — when a QA issue is found

If vision QA (or the user) flags one property as wrong on an element, **don't fix just that one
property and move on** — re-run the checklist above on that whole element before responding. The
carousel section above lost most of its round-trips to exactly this: a fix for the tab height
prompted "the active color's wrong too," which prompted "there's a border that shouldn't be
there," each found and fixed one at a time across separate turns. A single element rarely has
exactly one thing wrong with it if it was built without checking any of the above in the first
place — re-run Tier 0's four commands plus every Tier 1 item that applies to that element,
fix everything found, then move on.

## Logging — make "ran clean" distinguishable from "never ran"

Nothing in this checklist leaves a trace unless a bug is found — a section that shipped clean
because the checklist ran, and one that shipped clean because the checklist was skipped and
happened not to matter this time, produce identical trace output. That gap has made real build
history hard to reconstruct after the fact: several confirmed bugs in this file (button size,
heading font-size, tab height, active-tab color, logo sizing, container width) all trace back to
a section built from a matched component's default or a prior section's convention, with no way
to tell from the log alone whether this checklist was ever run against real Figma data before the
CSS was written. **Log a one-line `[PRE-BUILD-CHECK]` entry in the session trace for every
visually complex section**, the same tag convention used elsewhere (`[QA]`, `[BUG]`,
`[ACCEPTED-GAP]`) — and for Tier 0 log the *values it printed*, not that it ran, since a number
in the trace is checkable after the fact and "ran clean" is not:
```
[PRE-BUILD-CHECK] <slug>: Tier 0 — bg ring <hex>, N block fills <hex,hex>; textsize <el> <px>;
                  textnodes N in <block>; assetbg K/N MISMATCH (<file> bakes <hex> on <hex>).
                  Tier 1 items 1–17: no drift
[PRE-BUILD-CHECK] <slug>: Tier 0 clean (values above), items 1–17 no drift
[PRE-BUILD-CHECK] <slug>: skipped — reused prior section's CSS from memory
```
The last form is the one to write honestly when it happens rather than omit. The
second form is not a good outcome, but writing it down is strictly better than a silent skip that
stays invisible until the resulting bug gets found and fixed reactively, exactly as
`ACCURACY-GATE.md`'s own logging rule already requires for `tools/qa_gate.py` findings.

## Cross-references

- `CLAY-INTEGRATION.md` — the governing principle this checklist operationalizes ("Clay is the
  code basis, Figma is the value source," including at the layout-mechanism level).
- `HARD-RULES.md` H28 — Clay-Web instance or matching component name must already be a coded
  Clay anchor before this checklist runs as a from-scratch build.
- `HARD-RULES.md` H16 — its three merged cases (text-box width, sibling asset-sizing convention,
  placeholder sizing) that this checklist generalizes into a single upfront pass.
- `ASK-DONT-GUESS.md` — the parallel rule for *interactivity*: when a section has multiple
  interdependent controls, present a state-model plan before coding, the same way this file says
  to verify visual properties before coding.

# Figma → Webflow Section Builder — Run Procedure

Follow these phases in order. Each phase names the reference file to read
before starting it — see `SKILL.md`'s map table for the full list.

---

## Phase 1 — Pre-flight

Establish ground truth before touching anything. Skipping this is why fidelity
problems surface late instead of early.

1. Confirm the three Webflow IDs: `site_id`, `page_id`, and the **insertion
   parent element ID** (the container the new section appends into). If you
   don't have them, get them via `data_sites_tool` / `data_pages_tool` /
   `data_element_tool → get_all_elements`.
2. Confirm the Figma `fileKey` and `nodeId`. In a Figma URL the node id looks
   like `node-id=10-861` — convert the hyphen to a colon: `10:861`.
3. **Take a `get_screenshot` of the Figma node now.** This is your visual
   ground truth. You'll compare against it in Phase 7. Without it, you're
   relying on the user to catch regressions.
4. Run `get_metadata` on the node to understand the layer tree *before*
   `get_design_context`. On large frames, `get_design_context` can blow the 25K
   token response cap; metadata lets you target a smaller sub-frame instead.
5. **Scan the page for existing interactive sections before designing your own.**
   Run `get_all_elements` at depth 4 and look for sections that contain
   `HtmlEmbed` children — those are JS-driven interactions. If the page already
   has a working pattern similar to what you're building (tabs, pills, accordion),
   inspect its `HtmlEmbed` custom code and element `styleNames` before writing
   new code. Reusing a proven in-page pattern is faster and avoids
   preview-vs-published gaps.

---

## Phase 2 — Design analysis

Read `references/section-types.md` and classify the section first — hero,
feature grid, pricing, testimonials/carousel, nav/header, footer, CTA, card
row. The type determines what to watch for in every later phase (which
breakpoints matter, what collapses vs. hides on mobile, what assets exist).

Then extract, using `get_design_context` on the targeted sub-frame and
`get_variable_defs` for tokens:

- Background (color / gradient / image)
- Typography per text role: font family, size, weight, letter-spacing,
  line-height — heading, subhead, body, labels, buttons
- Color tokens: accents, CTA fills, borders
- **Decorative and layout positions as percentages, not pixels** — the frame
  width changes at breakpoints, so absolute px positions break. Convert from the
  Figma frame width (e.g. `500px / 1944px ≈ 26%`).
- Every asset that needs uploading: logos, photos, icons, illustrations.

Record all of this in a short working note — you'll reference it repeatedly.

---

## Phase 2.5 — Interaction audit (the "interaction brief")

Before writing any CSS, **look at the design and decide what every interactive
surface should do.** Don't ask the user to hand-spec it — earn the understanding
from the design itself, then let them correct a cheap plain-language brief
rather than finished code.

Read `references/interaction-patterns.md` for the archetype → recipe lookup.
Use both vision (the screenshot) and structure (`get_metadata` layer names like
`Button/Primary`, `Input/Search` are the strongest signal) to detect intent.

Produce an **Interaction Brief** — plain language, one entry per interactive
element, naming the class it will map to. Example:

```
Button  .section_btn-primary
  hover → lifts 2px, shadow intensifies (150ms ease)
Search bar  .section_search
  focus-within → border shifts to accent + soft glow ring (250ms ease)
Pills  .section_pill  (horizontally scrollable row)
  click → toggles active fill; hover → subtle opacity fade
Floating avatars  .section_avatar-*
  ambient → gentle vertical float, staggered, infinite
Content block (heading, subtitle, CTA)
  entrance → staggered fade-up on load (respects prefers-reduced-motion)
```

Show the brief to the user and let them correct it. Getting a mislabeled element
("that pill is actually a static label") fixed here costs one sentence; fixing
it after the `<style>` block is written costs a rebuild. The brief also becomes
a comment header inside the freeform code block, so future sessions understand
the intent.

---

## Phase 3 — Asset pipeline

Read `references/asset-pipeline.md` before uploading anything — the two-step
upload and the URL-expiry behavior are non-obvious and each will cost failed
calls if skipped.

Short version:
1. `download_assets` on each image node, then `curl` it to a local file **in the
   same step** — the Figma download URLs expire within seconds. Never store the
   URL to use later.
2. If a logo sits on a non-transparent background (sample the corner pixels to
   check), run `scripts/logo-fix.py` to produce a clean transparent version. A
   logo dropped onto a dark section will otherwise render as a visible box.
3. Upload via `data_assets_tool → create_asset` (two-step: request upload URL,
   then POST the bytes to S3 as multipart with **every** field from
   `uploadDetails`). Record each returned asset ID before moving on.

---

## Phase 4 — Style system

Read `references/webflow-styles.md` before creating styles.

Create **all** classes before building the DOM — adding a missed class after
elements exist is far more painful than defining them up front.

- Use `data_style_tool → create_style`. **Longhand properties only** — write
  `background-color`, not `background`; `border-width` / `border-style` /
  `border-color`, not `border`.
- Namespace every class as `section-name_element-name` (e.g.
  `agents-banner_heading`) to prevent collisions with the rest of the site.
- **Do not put responsive styles here.** `update_style` silently ignores its
  `breakpoint` parameter and writes to base — this is the #1 gotcha. All
  breakpoint styling goes through freeform code in Phase 6.

---

## Phase 5 — DOM construction

- Build the tree as a single nested `data_element_builder → create_element`
  call when you can — fewer roundtrips, and it's atomic.
- For any element that needs its own text (buttons, links, labels), create it as
  a **`TextLink`** — `set_text` fails on `DivBlock`/`Block` ("doesn't support
  text"). If you already have a DivBlock that needs text, fetch its child
  `String` node id via `get_all_elements` and `set_text` on that.
- Wire images with `data_element_tool → set_image_asset` using the asset IDs
  from Phase 3.
- Note: `set_attributes` for `alt` text is unreliable via the Data API (returns
  an internal error). See `api-gotchas.md` — set alt via the `use_figma`
  plugin path or flag it to the user rather than silently shipping without it.

---

## Phase 6 — Responsive + interactions

This is where the freeform-code path does all the work. Read
`references/responsive-patterns.md` and `references/interaction-patterns.md`.

### CSS → head freeform code (always)

Write **one consolidated `<style>` block** and deploy it with
`data_scripts_tool → set_page_freeform_code` (`location: "head"`). This is the
**only** reliable path for responsive CSS: it accepts full media queries and
`!important`, which `update_style` and `data_whtml_builder` do not.

The block should contain, in order:
1. A comment header with the Interaction Brief from Phase 2.5.
2. `@keyframes` for entrance and ambient animations.
3. Interaction rules (hover, focus-within, active) from the brief.
4. Media queries at `991px`, `767px`, `479px` — use the exact form
   `screen and (max-width: N)`.
5. A `@media (prefers-reduced-motion: reduce)` block that disables animation —
   always include this.

`responsive-patterns.md` has the tested recipes (viewport-fill hero, horizontal
pill scroll, decorative-hide, nav collapse). Reuse them rather than reinventing.

### JS → body HtmlEmbed (always — not the head)

**Never put interactive JavaScript in the head freeform block.** Head scripts
only run on the published page; Webflow preview skips them entirely (see
`api-gotchas.md` §9). Any section with click, hover-state toggling, or image
swapping must have its JS in a body-level `HtmlEmbed` element.

Create it as an `HtmlEmbed` appended to the section (last child), wrapping the
script in an IIFE. Because the embed sits below the section's elements in DOM
order, all targets are already available — no `DOMContentLoaded` needed:

```html
<script>
(function(){
  var tabs = document.querySelectorAll('.clay-hero_tab');
  tabs.forEach(function(t){ t.addEventListener('click', function(){ ... }); });
})();
</script>
```

The split in practice:
- `set_page_freeform_code` (head) → CSS only
- `data_element_builder → HtmlEmbed` (body, last child of section) → JS only

---

## Phase 7 — QA

**Test interactions in preview first, before screenshotting.** Open the Webflow
preview link and manually trigger every item from the Phase 2.5 Interaction
Brief — click each tab/pill, hover buttons, focus inputs. If interactions are
dead in preview but work on the published page, the JS is in the head freeform
block instead of a body `HtmlEmbed`; move it (see `api-gotchas.md` §9). This is
the most common QA failure mode and the cheapest point at which to catch it.

Then screenshot the live page at **1440, 1024, 768, 375**. Check against the Phase 1
Figma screenshot and verify, at each width:

- No horizontal overflow / scrollbar
- Heading and body sizes read well (not oversized on mobile)
- CTAs visible and tappable
- Section-type-specific behavior works (pills scroll, cards stack, nav
  collapses) — see `section-types.md`
- Decorative elements hidden or repositioned as intended, not overlapping text
- Interactions from the brief actually fire (hover, focus, click, entrance)

Fix issues by editing the freeform-code block and re-checking — don't chase them
through `update_style`.

---

## Phase 8 — Publish (only when asked)

Publish only if the user asks. Use `data_sites_tool → publish_site` and include
`site_id` **inside the action object**, not just at the envelope level — the
envelope-level id alone is not enough.

---

## The core principle

Most of what makes this hard isn't the design — it's that a few Webflow Data API
tools quietly do the wrong thing. The reference files exist so you spend your
effort on fidelity and interaction quality, not on rediscovering that
`update_style` ignores breakpoints or that Figma URLs expire. Read them; trust
them; keep them updated when you learn something new.

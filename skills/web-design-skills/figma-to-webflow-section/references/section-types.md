# Section types — per-type guidance and watch-outs

Classify the section in Phase 2 before extracting values. The type drives what
you watch for at each later phase — especially the mobile strategy and which
elements hide vs. restructure.

## Hero / banner
- **Layout:** full-width, often viewport-filling. Headline + subhead + CTA(s),
  frequently with decorative/floating elements and a background treatment.
- **Assets:** brand logo (check for opaque background → `logo-fix.py`), hero
  imagery, floating avatars/cards.
- **Mobile:** fill the viewport (`100svh`); center content with `margin:auto`;
  **hide** decoratives (glows, grids, floating cards) rather than reposition;
  step heading size down hard.
- **Interactions:** staggered entrance fade-up; ambient float on decoratives;
  button hover-lift; search focus ring if present.

## Feature grid / cards row
- **Layout:** N equal columns of icon+title+text cards.
- **Mobile:** collapse columns — 3→2 at 991, →1 at 767. Use gap tokens, not
  fixed margins.
- **Watch:** cards must stack cleanly without overflow; equalize heights if the
  design implies it.
- **Interactions:** card hover-elevate (see `interaction-patterns.md`).

## Pricing
- **Layout:** 2–4 plan columns, one often "featured" (raised/outlined).
- **Mobile:** stack columns; keep the featured plan visually distinct (don't
  lose the emphasis when it stacks). Consider ordering the featured plan first.
- **Watch:** feature-list alignment across columns; toggle (monthly/annual) is
  an interactive element — spec it in the brief.

## Testimonials / carousel
- **Layout:** quote cards, avatars, names/roles; may be a scrollable row.
- **Assets:** avatar photos (upload each).
- **Mobile:** horizontal scroll strip (see pill-scroll recipe, generalized to
  cards) or single-column stack.
- **Interactions:** scroll snap if it's a carousel; card hover-elevate.

## Nav / header
- **Layout:** logo + link row + CTA(s). No native Navbar type — build from
  DivBlock/LinkBlock + freeform CSS.
- **Mobile:** hide the desktop link row at ≤991px; drop secondary actions at
  ≤479px so only logo + primary CTA remain. (A true hamburger menu needs extra
  JS — spec it explicitly if the user wants one.)
- **Interactions:** nav-link hover fade; sticky positioning if the design
  implies it.

## Footer
- **Layout:** multi-column link groups + brand mark + legal row.
- **Mobile:** collapse columns to stacked groups (often an accordion on very
  small screens, but simple stacking is fine by default).
- **Watch:** brand logo transparency; legal row wrapping.

## CTA band
- **Layout:** short, full-width, headline + button on a contrasting background.
- **Mobile:** center; ensure the button is full-width or comfortably tappable.
- **Interactions:** button hover-lift; optional background gradient shift.

## Tabs / interactive panel

- **Layout:** a horizontal pill/tab row above a content area (illustration,
  screenshot, video) that changes when a tab is clicked. Common as a "use case"
  or "feature explorer" sub-section inside a hero or standalone section.
- **Assets:** one image per tab. Export all in Phase 3. If not all are ready,
  export the first one and use it as a shared placeholder for all tabs; keep the
  JS image-map as the single edit point for later swaps.
- **Active state:** requires a real Webflow class (e.g. `x_tab-active`) created
  via `create_style` in Phase 4. **Never use `w--current`** — it injects
  Webflow's own bold+underline styles regardless of your CSS (see
  `api-gotchas.md` §12). Apply the active class to the first tab's `style_names`
  at DOM build time so the Designer shows the correct initial state.
- **JS placement:** tab-switching and image-swap logic goes in a body-level
  `HtmlEmbed` as the last child of the section. **Not in the head freeform
  block** — head scripts are skipped entirely in Webflow preview (see
  `api-gotchas.md` §9).
- **Image swap + fade:** on click, update `img.src`, then remove and re-add
  `.is-swapping` to re-trigger the CSS cross-fade. Insert `void img.offsetWidth`
  between remove and add to force a DOM reflow (otherwise the browser skips
  re-animating an element that already has the class).
- **Mobile:** the pill row must scroll horizontally at ≤991px if there are
  more than 4–5 tabs. Use `flex-wrap:nowrap; overflow-x:auto; scrollbar-width:
  none` on the row and `flex:0 0 auto` on each tab (see pill-scroll recipe in
  `responsive-patterns.md`).
- **Interactions:** smooth background-color + color transition on each pill
  (150ms); cross-fade on the stage image (500ms ease); subtle hover on inactive
  tabs. See the tab-with-stage-image recipe in `interaction-patterns.md`.

---

**Common thread:** whatever the type, positions come out of Figma as
percentages, base styles go through `data_style_tool`, and everything responsive
or interactive goes through the freeform-code block. The type only changes
*which* recipes from `responsive-patterns.md` and `interaction-patterns.md` you
reach for.

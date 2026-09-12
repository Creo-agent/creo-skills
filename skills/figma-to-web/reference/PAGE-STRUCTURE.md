# Page Structure — Shared markup skeleton

## Contents
- What this file owns
- The tree
- HTML
- CSS — class names are fixed, values are not
- Rules to follow
- Header / footer vs content sections
- Cross-references

## What this file owns

Every page this skill writes uses the same wrapper / container / padding markup so max-width
and side padding are defined **once** (H22) instead of reinvented per section. This file is the
shell. Unique section content still comes from Figma + Clay (`CLAY-INTEGRATION.md`).

**Do not install `page-structure` as a second skill.** This file is that skill, folded in so
one engine owns both the look (Figma) and the skeleton (this tree).

## The tree

```
page-wrapper                      (div)
├── header                        — nav / global chrome (H25). Not inside main.
├── main.main-wrapper
│   └── section[data-section]     — one per content section
│       └── padding-global
│           └── container-large
│               └── padding-section-large
│                   └── ← unique section content goes here
│   └── <!-- SECTIONS_END -->     — immediately before </main> (H7)
└── footer                        — global chrome (H25). Not inside main.
```

`header` and `footer` are siblings of `main-wrapper`, both inside `page-wrapper`. Every content
`<section>` repeats the same three nested divs before any unique content.

## HTML

```html
<div class="page-wrapper">
  <header>
    <!-- site header / nav — filled when that Figma node is built; empty until then -->
  </header>

  <main class="main-wrapper">
    <section id="<section-slug>" data-section="<section-slug>" data-page="<page-slug>" class="section-<section-slug>">
      <div class="padding-global">
        <div class="container-large">
          <div class="padding-section-large">
            <!-- unique content for this section goes here -->
          </div>
        </div>
      </div>
    </section>

    <!-- SECTIONS_END -->
  </main>

  <footer>
    <!-- site footer — filled when that Figma node is built; empty until then -->
  </footer>
</div>
```

Keep `id` / `data-section` / `data-page` on `<section>` — `tools/qa_gate.py` keys off them.

## CSS — class names are fixed, values are not

Use these class names **exactly**: `page-wrapper`, `main-wrapper`, `padding-global`,
`container-large`, `padding-section-large`. Do not invent synonyms (`inner`, `wrap`, `max`,
`container`).

**Values follow H22.** On the first section of a page, establish one pair using this priority:

1. If Clay tokens are loaded, prefer `--clay-layout-container-large` and the
   `--clay-layout-section-padding-x` / `-x-mobile` pair.
2. Else use this section's Figma content width + padding (PRE-BUILD-VERIFICATION.md item 14).
3. Fall back to the standard page-structure defaults (aligned with the shared `page-structure`
   skill):

```css
/* Standard page-structure defaults — source of truth for all page builds */
.padding-global {
  padding: 0 var(--clay-layout-section-padding-x, 2.5rem);
}
@media screen and (max-width: 767px) {
  .padding-global {
    padding: 0 var(--clay-layout-section-padding-x-mobile, 1.5rem);
  }
}
.container-large {
  width: 100%;
  max-width: var(--clay-layout-container-large, 80rem); /* 80rem = 1280px */
  margin: 0 auto;
}
.padding-section-large {
  padding: clamp(4rem, 3.4286rem + 2.8571vw, 6rem) 0;
  /* Responsive vertical padding: 64px at 320px viewport → 96px at 1440px */
}
```

**These values match the shared `page-structure` skill exactly.** The `clamp()` for vertical
section padding is non-negotiable — it ensures consistent vertical rhythm across all sections
without per-section padding overrides. If a section needs different vertical spacing, add a
modifier class (`padding-section-small`, `padding-section-hero`) alongside
`padding-section-large`, never replace the base class.

Write those three rules **once** in the page shell (`SECTION-WORKFLOW.md` Step 7), not again
inside every section's scoped `<style>`. Later sections reuse the classes; they do not ship a
second `max-width`.

Full-bleed exceptions (carousel viewport, marquee track) are H22's named exceptions: put the
full-bleed background on `<section>`, keep unique *content* inside the three-div nest (or mark
the section `data-full-bleed` and still keep an inner `container-large` for any boxed copy).
Do not skip the nest silently.

**The exception covers only the specific full-bleed element, never the whole section (H27).**
Confirmed real case, twice: a section with one legitimately full-bleed element (a marquee track)
also had an ordinary boxed CTA button that skipped the nest too — going straight from
`container-large` to the button's own wrapper with no `padding-section-large` in between —
because the section's one real exception was read as license for irregular nesting anywhere
inside it. Every non-full-bleed content block in that same section (headings, CTA rows, badges)
still gets the complete nest, with no exception.

## Rules to follow

- Never put unique content directly inside `section`, `padding-global`, or `container-large` —
  it always goes inside the innermost `padding-section-large`. Those three outer elements exist
  only for spacing and max-width, and should never carry their own content-specific classes.
- Each content `<section>` gets its own fresh
  `padding-global > container-large > padding-section-large` nesting. Don't reuse one
  `container-large` across multiple sections.
- If a section needs a different *vertical* rhythm (hero larger, tight band smaller), keep the
  same three-div nesting and add a second class alongside `padding-section-large` (e.g.
  `padding-section-large padding-section-small`) rather than changing the structure.
- `header` and `footer` are **not** wrapped in `padding-global` / `container-large` by default —
  they are their own components (H25). Mark them `data-chrome="header"` / `data-chrome="footer"`
  so `qa_gate.py` does not require the three-div nest on them.
- Keep class names exactly as given so the structure is recognizable and H22's page-wide
  measurement has one inner container to measure: `.container-large`.

## Header / footer vs content sections

In `FULL-PAGE-WORKFLOW.md` Step 2, tag each manifest entry with `role`:

| `role` | Detection (name, Clay match, or H25 chrome) | Where it injects |
|---|---|---|
| `header` | nav / header / navbar / Clay `Navbar` | inside `<header>`, no three-div nest |
| `footer` | footer / Clay `Footer` / `Section/Footer` | inside `<footer>`, no three-div nest |
| `section` | everything else | inside `main`, before the sentinel, with the nest |

Standalone section mode still writes this full shell (empty `<header>` / `<footer>` until a
later run fills them). That way adding a second section never has to retrofit the tree.

## Cross-references

- **When to write this markup:** `SECTION-WORKFLOW.md` Steps 6–7 (block + shell) and Step 9
  (inject before `<!-- SECTIONS_END -->`, which sits immediately before `</main>`).
- **One max-width + padding pair:** `HARD-RULES.md` H22, `PRE-BUILD-VERIFICATION.md` item 14.
- **Global chrome lookup:** `HARD-RULES.md` H25, `CLAY-INTEGRATION.md`.
- **Enforced by:** H7 (sentinel before `</main>`), H27 (this tree), `tools/qa_gate.py`.

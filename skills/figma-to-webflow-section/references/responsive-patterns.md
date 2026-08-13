# Responsive patterns — tested recipes for the freeform-code block

All of this goes into the single `<style>` block deployed via
`data_scripts_tool → set_page_freeform_code`. Media queries use the exact form
`screen and (max-width: N)`. Webflow's breakpoints are 991 (tablet), 767
(mobile landscape), 479 (mobile portrait) — target those.

## Contents
- [Structure of the block](#structure-of-the-block)
- [Viewport-fill section](#viewport-fill-section)
- [Horizontal pill / chip scroll](#horizontal-pill--chip-scroll)
- [Hide decorative elements on mobile](#hide-decorative-elements-on-mobile)
- [Nav collapse](#nav-collapse)
- [Fluid typography down the breakpoints](#fluid-typography-down-the-breakpoints)
- [Reduced motion](#reduced-motion)

## Structure of the block

Order matters for readability and cascade:

```html
<style>
/* === INTERACTION BRIEF (from Phase 2.5) ===
   button → hover lift; search → focus ring; pills → click-active; ... */

/* 1. keyframes */
@keyframes ab-fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes ab-floatY{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}

/* 2. entrance + ambient (base) */
.section_heading{animation:ab-fadeUp .55s ease .22s both}
.section_avatar-left{animation:ab-floatY 6s ease-in-out infinite}

/* 3. interactions */
.section_btn-primary{transition:transform .15s ease,box-shadow .15s ease}
.section_btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(99,75,255,.45)}
.section_search{transition:border-color .25s ease,box-shadow .25s ease}
.section_search:focus-within{border-color:rgba(140,90,255,.8) !important;box-shadow:0 0 0 3px rgba(140,90,255,.18) !important}

/* 4. media queries: 991 → 767 → 479 */
@media screen and (max-width:991px){ /* ... */ }
@media screen and (max-width:767px){ /* ... */ }
@media screen and (max-width:479px){ /* ... */ }

/* 5. reduced motion */
@media (prefers-reduced-motion:reduce){ /* disable animations */ }
</style>
```

## Viewport-fill section

For a hero that should fill the screen on mobile. `svh` handles mobile browser
chrome; the `vh` line is a fallback for older browsers. `margin:auto` on the
content block centers it vertically between nav and bottom in a flex column.

```css
@media screen and (max-width:991px){
  .section_hero{min-height:100svh !important;min-height:100vh !important;padding-bottom:0 !important}
  .section_content{margin-top:auto !important;margin-bottom:auto !important;
    padding-top:2rem !important;padding-bottom:2.5rem !important}
}
```

## Horizontal pill / chip scroll

Multi-row pill clutter is the classic mobile problem. Turn the row into a single
horizontally-scrollable strip with hidden scrollbar. **Apply at ≤991px** — at
exactly 768px (tablet landscape) the pills still wrap if you only gate at
≤767px.

```css
@media screen and (max-width:991px){
  .section_pills{flex-wrap:nowrap !important;overflow-x:auto !important;
    justify-content:flex-start !important;-webkit-overflow-scrolling:touch;
    scrollbar-width:none !important;
    padding-left:1rem !important;padding-right:1rem !important;
    margin-left:-1rem !important;margin-right:-1rem !important}
  .section_pills::-webkit-scrollbar{display:none}
  .section_pill{flex-shrink:0 !important}
}
```

## Hide decorative elements on mobile

Floating cards, glows, background grids, and badges add clutter and overflow
risk on small screens. Hiding them reads better than trying to reposition each
one. Do it at ≤991px.

```css
@media screen and (max-width:991px){
  .section_glow-a,.section_glow-b,.section_grid,
  .section_avatar-left,.section_avatar-right,.section_badge{display:none !important}
}
```

## Nav collapse

No native Navbar type exists, so collapse manually. Hide the desktop link row at
≤991px; drop secondary actions (outline button, extra links) at ≤479px so only
the logo + primary CTA remain.

```css
@media screen and (max-width:991px){ .section_nav-links{display:none !important} }
@media screen and (max-width:479px){
  .section_nav{padding-left:1rem !important;padding-right:1rem !important}
  .section_btn-outline{display:none !important}
}
```

## Fluid typography down the breakpoints

Step heading and body sizes down at each breakpoint so nothing overflows or
dwarfs the mobile viewport. Tighten letter-spacing as size drops.

```css
@media screen and (max-width:991px){ .section_heading{font-size:2.5rem !important;letter-spacing:-.75px !important} }
@media screen and (max-width:767px){ .section_heading{font-size:2.125rem !important} .section_subtitle{font-size:1rem !important;line-height:1.65 !important} }
@media screen and (max-width:479px){ .section_heading{font-size:1.85rem !important;letter-spacing:-.25px !important} .section_subtitle{font-size:.9375rem !important;max-width:100% !important} }
```

## Reduced motion

Always include this — some users get motion sick, and it's an accessibility
expectation.

```css
@media (prefers-reduced-motion:reduce){
  .section_heading,.section_subtitle,.section_search,.section_pills,
  .section_avatar-left,.section_avatar-right,.section_badge{animation:none}
}
```

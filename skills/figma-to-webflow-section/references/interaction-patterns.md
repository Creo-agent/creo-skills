# Interaction patterns — element archetype → recipe

Use this in Phase 2.5 to turn a visual read of the design into an Interaction
Brief, and in Phase 6 to write the actual CSS/JS. The goal is that interactions
feel intentional and consistent, not invented fresh each time.

## How to detect what an element is

Combine **vision** (the Phase 1 screenshot) with **structure** (`get_metadata`
layer names — the strongest signal of intent):

| Signal | Likely archetype |
|---|---|
| Filled rounded shape with a short label | Button |
| Bordered box with placeholder text and/or an icon | Input / search bar |
| Row of small repeated labels/chips | Pill / tag group |
| Element visually layered or floating over the background | Ambient-animation candidate |
| Layer named `Button/*`, `Input/*`, `Card/*`, `Nav/*` | Trust the name over guesswork |
| Underlined or accent-colored inline text | Text link |
| Image/card in a repeating set | Grid/carousel item |

When a read is ambiguous, put your best guess in the brief and let the user
correct it — that's cheaper than guessing silently.

## Recipes

Timings and easings below are sensible defaults; adjust to the brand's feel.

### Button
```css
.x_btn{transition:transform .15s ease,box-shadow .15s ease}
.x_btn:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(0,0,0,.35)}
```
Secondary/outline variant: transition `background-color` + `color` instead of
lift.

### Button with inline icon (arrow / chevron)

Build the icon with `createElementNS` via JS — do **not** nest an `HtmlEmbed`
inside the button. An HtmlEmbed auto-receives Webflow's `w-embed` class which
sets `width:100%; display:block`, turning the button into a full-width oval
(see `api-gotchas.md` §11).

Inject from the section's body-level script:
```js
var btn = document.querySelector('.x_btn');
if(btn && !btn.querySelector('.x_btn-icon')){
  var wrap = document.createElement('span');
  wrap.className = 'x_btn-icon';
  var ns = 'http://www.w3.org/2000/svg';
  var svg = document.createElementNS(ns,'svg');
  svg.setAttribute('width','12'); svg.setAttribute('height','10');
  svg.setAttribute('viewBox','0 0 12 10'); svg.setAttribute('fill','none');
  var path = document.createElementNS(ns,'path');
  path.setAttribute('d','M7.2 0.2L11 5M11 5L7.2 9.8M11 5H1');
  path.setAttribute('stroke','currentColor');
  path.setAttribute('stroke-width','1.5');
  path.setAttribute('stroke-linecap','round');
  path.setAttribute('stroke-linejoin','round');
  svg.appendChild(path); wrap.appendChild(svg); btn.appendChild(wrap);
}
```

```css
.x_btn { gap: 8px }
.x_btn-icon { transition: transform 220ms cubic-bezier(.34,1.56,.64,1); display:flex }
.x_btn:hover .x_btn-icon { transform: translateX(4px) }
```

### Input / search bar
```css
.x_search{transition:border-color .25s ease,box-shadow .25s ease}
.x_search:focus-within{border-color:<accent> !important;
  box-shadow:0 0 0 3px <accent-at-18%> !important}
```
`focus-within` (not `focus`) so the ring appears when the inner `<input>` is
focused.

### Pills / tags (single-select)
Hover fade in CSS; click-to-activate needs a little JS. Toggle an
`x_pill-active` class:

```html
<!-- Body HtmlEmbed — last child of the section. NOT in the head freeform block
     (head scripts are skipped in Webflow preview). See api-gotchas.md §9. -->
<script>
(function(){
  var pills=document.querySelectorAll('.x_pill');
  pills.forEach(function(p){
    p.addEventListener('click',function(e){
      e.preventDefault();
      pills.forEach(function(o){o.classList.remove('x_pill-active')});
      this.classList.add('x_pill-active');
    });
  });
})();
</script>
```

> **`x_pill-active` must be a real Webflow class** created via `create_style`
> (not a freeform CSS selector) and applied to the initial active element via
> `style_names` at build time. See `webflow-active-states.md`.
```css
.x_pill{transition:background-color .15s ease,opacity .15s ease;cursor:pointer}
.x_pill:hover{opacity:.85}
.x_pill-active{background-color:<accent> !important;color:#fff !important}
```

### Tabs with stage image

A pill row where clicking a tab activates it and swaps a large illustration
below. The image swap uses a CSS cross-fade triggered by toggling a class.

**`x_tab-active` must be a real Webflow class** — create it via `create_style`
in Phase 4, apply it to the first tab via `style_names` at DOM build time, and
toggle it in the body-level script. See `webflow-active-states.md`.

**CSS (head freeform block):**
```css
.x_tab { transition: background-color 150ms cubic-bezier(0,0,.2,1),
                     color 150ms cubic-bezier(0,0,.2,1) }
.x_tab:not(.x_tab-active):hover { color: #000; background-color: rgba(0,0,0,.04) }

@keyframes x-fadeIn { from { opacity:0 } to { opacity:1 } }
.x_stage-img.is-swapping { animation: x-fadeIn 500ms ease }

@media screen and (max-width:991px){
  .x_tabs { flex-wrap:nowrap !important; overflow-x:auto !important;
            -webkit-overflow-scrolling:touch; scrollbar-width:none !important }
  .x_tabs::-webkit-scrollbar { display:none }
  .x_tab  { flex:0 0 auto !important }
}
```

**JS (body HtmlEmbed — last child of the section, NOT in the head):**
```html
<script>
(function(){
  /* SINGLE EDIT POINT — map each data-tab value to its image URL */
  var IMGS = {
    Tab1: 'https://cdn…/tab1.png',
    Tab2: 'https://cdn…/tab2.png'
  };
  var tabs = document.querySelectorAll('.x_tab');
  var img  = document.querySelector('.x_stage-img');
  tabs.forEach(function(t){
    t.addEventListener('click', function(e){
      e.preventDefault();
      tabs.forEach(function(x){ x.classList.remove('x_tab-active') });
      this.classList.add('x_tab-active');
      var url = IMGS[this.getAttribute('data-tab')];
      if(img && url){
        img.classList.remove('is-swapping');
        void img.offsetWidth; /* force reflow to re-trigger animation */
        if(img.getAttribute('src') !== url){ img.setAttribute('src', url) }
        img.classList.add('is-swapping');
      }
    });
  });
})();
</script>
```

**DOM shape** (Phase 5 build — `data_element_builder`):
```
div.x_tabs  (role="tablist")
  a.x_tab.x_tab-active  data-tab="Tab1"   ← first tab: both classes in style_names
  a.x_tab               data-tab="Tab2"
  …
div.x_stage
  img.x_stage-img  (src = first tab's image URL)
[section root]
  … content …
  HtmlEmbed  ← script goes here, last child of the section
```

### Entrance animation (content block)
Stagger fade-up so the eye lands top-to-bottom. Use `both` fill mode so elements
start hidden.
```css
@keyframes x-fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.x_eyebrow {animation:x-fadeUp .5s ease .10s both}
.x_heading {animation:x-fadeUp .55s ease .22s both}
.x_subtitle{animation:x-fadeUp .5s ease .38s both}
.x_cta     {animation:x-fadeUp .5s ease .50s both}
```

### Ambient float (decorative/floating elements)
Gentle, slow, infinite; stagger start times so multiple elements don't move in
lockstep.
```css
@keyframes x-floatY{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
.x_float-a{animation:x-floatY 6s ease-in-out infinite}
.x_float-b{animation:x-floatY 6s ease-in-out 2.5s infinite}
```

### Nav link
```css
.x_nav-link{transition:opacity .18s ease}
.x_nav-link:hover{opacity:.6}
```

### Card (hover-elevate, for grids/testimonials)
```css
.x_card{transition:transform .2s ease,box-shadow .2s ease}
.x_card:hover{transform:translateY(-4px);box-shadow:0 12px 32px rgba(0,0,0,.12)}
```

## Always pair motion with reduced-motion

Every animation added above must be disabled in the
`@media (prefers-reduced-motion:reduce)` block (see `responsive-patterns.md`).
Interactions triggered by real input (hover, focus, click) can stay.

## The brief is documentation

Drop the final brief in as a comment at the top of the freeform-code block. A
future session (or teammate) reading the page head should be able to understand
what every interaction was meant to do without reverse-engineering the CSS.

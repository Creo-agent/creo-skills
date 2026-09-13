# Animation → Webflow — Run Procedure

Follow these phases in order. See `SKILL.md`'s quick-reference checklist
before starting.

---

## Phase 1 — Analyze the prototype

Read the HTML file before doing anything else.

### 1.1 Extract the scene dimensions

Find the fixed canvas size in the CSS (e.g. `.product-scene { width: 1096px; height: 508px }`).
Record it — you'll use this in `scaleScene()`.

### 1.2 List every element

Make a table: element → CSS class → position (left/top/width/height) → animation role.

| Class | Position | Animation |
|---|---|---|
| `.bg` | left:0 top:99 w:1096 h:445 | fade in, delay 0 |
| `.left-group` | left:0 top:0 w:600 h:508 | slide from left, delay 0.1 |
| ... | | |

These are your ground truth. The Figma file will have the same positions —
cross-check if anything looks off.

### 1.3 Identify all image assets

List every `<img src="...">` and any `background-image: url(...)` in CSS.
These must be uploaded to Webflow CDN before you write the JS builder.

### 1.4 Identify the animation loop structure

- What triggers `play()`? (load, click, interval)
- Does it loop? How long is one cycle?
- Is there a typewriter or other JS-driven sub-animation?
- What state needs to be reset between loops?

### 1.5 Classify the trigger in Webflow

| Trigger | Where JS lives | Notes |
|---|---|---|
| Tab click | Head freeform code | `DOMContentLoaded`, select by `data-tab` attr |
| Scroll-into-view | Footer IIFE | Use `IntersectionObserver` |
| Page load | Footer IIFE | Auto-plays after a `setTimeout` |
| Modal open | Footer IIFE | Listen for a class toggle on the modal |
| Button click | Footer IIFE | Select button, add listener |

---

## Phase 2 — Upload assets to Webflow CDN

Assets **cannot** reference local paths or external URLs you don't control.
Everything must be on Webflow's CDN. Upload before writing JS.

### 2.1 Get MD5 hash for each file

```bash
# macOS
md5 -q path/to/file.svg

# Linux
md5sum path/to/file.svg | cut -d' ' -f1
```

### 2.2 Request upload credentials (step 1 of 2)

```
data_assets_tool → create_asset
  site_id:   "YOUR_SITE_ID"
  file_name: "descriptive-name.svg"   ← this becomes part of the CDN filename
  file_hash: "MD5_HEX"               ← MD5 in hex (not base64)
```

Returns an `uploadDetails` object with an S3 URL and several form fields.
**Record the full response** — you need every field.

### 2.3 POST the file to S3 (step 2 of 2)

```bash
curl -s -o /tmp/upload_out.txt -w "%{http_code}" \
  -F "key=FIELD_VALUE" \
  -F "Content-Type=image/svg+xml" \        ← use image/png for PNGs
  -F "policy=FIELD_VALUE" \
  -F "x-amz-credential=FIELD_VALUE" \
  -F "x-amz-algorithm=FIELD_VALUE" \
  -F "x-amz-date=FIELD_VALUE" \
  -F "x-amz-signature=FIELD_VALUE" \
  -F "file=@/absolute/path/to/file.svg" \
  "S3_UPLOAD_URL"
```

**Expected response: `201`**. Anything else is a failure — re-request
upload credentials and retry (credentials expire quickly).

### 2.4 Derive the CDN URL

```
https://cdn.prod.website-files.com/SITE_ID/ASSET_ID_descriptive-name.svg
```

The `ASSET_ID` comes from the `key` field in `uploadDetails` — it is the
path prefix before the filename. Extract it.

### 2.5 Record your CDN URL table

| Local file | CDN URL |
|---|---|
| `bg-card.svg` | `https://cdn.prod.website-files.com/.../ID_bg-card.svg` |
| `woman.png` | `https://cdn.prod.website-files.com/.../ID_woman.png` |

Keep this — you'll paste it into the JS builder.

---

## Phase 3 — Write the scoped CSS

### 3.1 The fundamental scoping rule

Every CSS rule must start with the animation root ID:

```css
/* WRONG — leaks into site CSS */
.left-group { position: absolute; ... }

/* CORRECT — scoped, collision-safe */
#product-anim .left-group { position: absolute; ... }
```

### 3.2 Prefix every class name

Choose a 2–4 character prefix. Use it on every class inside the animation.

```css
#product-anim .pa-scene { ... }
#product-anim .pa-bg { ... }
#product-anim .pa-left-group { ... }
```

In the JS builder you will set `.className = 'pa-scene'` — the prefix means
the CSS selector `#product-anim .pa-scene` still matches, and there's no
risk of clashing with `.scene` elsewhere on the page.

### 3.3 Prefix every `@keyframes` name

```css
/* WRONG — can collide with other animations */
@keyframes fadeIn { ... }

/* CORRECT */
@keyframes pa-fadeIn { ... }

/* Then reference it: */
#product-anim .pa-animating .pa-bg {
  animation: pa-fadeIn 0.5s 0s ease both;
}
```

### 3.4 Set transform-origin on the scene

The scene is fixed-pixel (e.g. 1096px wide). It scales down to fit a
smaller container via `transform: scale(ratio)`. Without `transform-origin:
top left` the scaled scene floats centered and clips wrong.

```css
#product-anim .pa-scene {
  position: relative;
  width: 1096px;
  height: 508px;
  overflow: hidden;
  transform-origin: top left;   ← REQUIRED
}
```

### 3.5 The animation container

```css
/* Sits on top of any sibling elements, fills the container */
/* Applied via ae.style.cssText in JS — not in the stylesheet */
display: none;
position: absolute;
inset: 0;
width: 100%;
height: 100%;
overflow: hidden;
```

### 3.6 Add a `prefers-reduced-motion` block

Always. Put it last in the CSS block.

```css
@media (prefers-reduced-motion: reduce) {
  #product-anim .pa-animating .pa-bg,
  #product-anim .pa-animating .pa-left-group,
  /* ... every animated element ... */
  { animation: none; }
}
```

### 3.7 Deploy CSS to page head

```
data_scripts_tool → set_page_freeform_code
  page_id:   "PAGE_ID"
  location:  "head"         ← the string "head", NOT "header"
  content:   "<style>...</style>"
```

**This replaces the entire head block.** Include all existing head CSS/JS plus
the new animation CSS. Never call it twice to "append" — each call overwrites.

---

## Phase 4 — Write the JS DOM builder

### The core constraint: Webflow strips all HTML

**Webflow sanitizes HTML in both `set_page_freeform_code (footer)` and
`data_whtml_builder` elements.** What gets stripped:

| What | Result |
|---|---|
| `class="my-class"` | becomes `class=""` — completely empty |
| `<img src="...">` | `src` is removed — image never loads |
| `id="my-id"` | **preserved** |
| `style="..."` | **preserved** |

There is no workaround that uses HTML markup. You cannot escape it or encode
it. **The only solution is to build the animation DOM entirely via
JavaScript.**

### 4.1 The builder helpers

```javascript
function el(tag, cls, id) {
  var e = document.createElement(tag);
  if (cls) e.className = cls;  // .className survives — it's a JS property, not HTML attr
  if (id)  e.id = id;
  return e;
}
function img(cls, filename) {
  var i = el('img', cls);
  i.src = CDN + filename;       // .src survives — same reason
  i.alt = '';
  return i;
}
```

These work because `.className` and `.src` are JavaScript object properties
set after parsing — they are not HTML attributes that the sanitizer sees.

### 4.2 The full IIFE template

```javascript
(function(){
  var CDN = 'https://cdn.prod.website-files.com/SITE_ID/';

  /* ── helpers ──────────────────────────────────────── */
  function el(tag, cls, id) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (id)  e.id = id;
    return e;
  }
  function img(cls, filename) {
    var i = el('img', cls);
    i.src = CDN + filename;
    i.alt = '';
    return i;
  }

  /* ── root container ───────────────────────────────── */
  var ae = el('div', '', 'product-anim');
  ae.style.cssText = 'display:none;position:absolute;inset:0;width:100%;height:100%;overflow:hidden;';

  /* ── scene (fixed Figma dimensions) ──────────────── */
  var scene = el('div', 'pa-scene');

  /* ── background (CSS-drawn) ───────────────────────── */
  scene.appendChild(el('div', 'pa-bg'));

  /* ── left group (slides in together) ─────────────── */
  var leftGroup = el('div', 'pa-left-group');

  /* text card with typewriter */
  var textCard       = el('div', 'pa-text-card');
  var textCardInner  = el('div', 'pa-text-card-inner');
  var typedText      = el('span', 'pa-typed-text', 'paTypedText');
  var typedCursor    = el('span', 'pa-typed-cursor', 'paTypedCursor');
  textCardInner.appendChild(typedText);
  textCardInner.appendChild(typedCursor);
  textCard.appendChild(textCardInner);
  leftGroup.appendChild(textCard);

  /* image assets */
  leftGroup.appendChild(img('pa-chip-img',   'ASSET_ID_chip.svg'));
  leftGroup.appendChild(img('pa-roadmap-img', 'ASSET_ID_roadmap.svg'));
  scene.appendChild(leftGroup);

  /* elements outside the left group */
  scene.appendChild(img('pa-woman-img', 'ASSET_ID_woman.png'));
  scene.appendChild(img('pa-chart-img', 'ASSET_ID_chart.svg'));
  ae.appendChild(scene);

  /* ── attach to the Webflow container ─────────────── */
  var stage = document.querySelector('.your-stage-class');
  if (stage) {
    stage.style.position = 'relative';  // needed if not already positioned
    stage.appendChild(ae);
  }

  /* ── typewriter ───────────────────────────────────── */
  var LINE1 = 'Your text line 1 ', LINE2 = 'line two here';
  var SPEED = 48, DELAY = 750;
  var twTimer = null;

  function runTypewriter() {
    clearTimeout(twTimer);
    var full = LINE1 + '\n' + LINE2, i = 0;
    typedText.textContent = '';
    typedCursor.style.display = 'inline-block';
    function tick() {
      if (i < full.length) {
        typedText.textContent += full[i++];
        twTimer = setTimeout(tick, SPEED);
      } else {
        setTimeout(function(){ typedCursor.style.display = 'none'; }, 600);
      }
    }
    twTimer = setTimeout(tick, DELAY);
  }

  /* ── play / loop ──────────────────────────────────── */
  var loopTimer = null;

  function play() {
    clearTimeout(twTimer);
    scene.classList.remove('pa-animating');
    typedText.textContent = '';
    typedCursor.style.display = 'none';
    void scene.offsetWidth;                   // force reflow to restart CSS animations
    scene.classList.add('pa-animating');
    runTypewriter();
  }

  /* ── responsive scale ─────────────────────────────── */
  function scaleScene() {
    if (!ae.offsetWidth) return;              // guard: don't scale when container is 0-wide
    scene.style.transform = 'scale(' + ae.offsetWidth / 1096 + ')';
  }
  window.addEventListener('resize', scaleScene);

  function stopLoop() {
    clearInterval(loopTimer);
    clearTimeout(twTimer);
  }

  /* ── public API (called by trigger JS in head) ────── */
  window.productAnimPlay = function() {
    stopLoop();
    scaleScene();
    play();
    loopTimer = setInterval(play, 5200);
  };
  window.productAnimStop = stopLoop;

})();
```

### 4.3 Deploy JS to page footer

```
data_scripts_tool → set_page_freeform_code
  page_id:  "PAGE_ID"
  location: "footer"
  content:  "<script>...</script>"
```

**This also replaces the entire footer block.** Include all existing footer
code plus the new animation IIFE.

---

## Phase 5 — The height collapse trap (critical)

This is the single most common reason an animation appears invisible.

### Why it happens

The Webflow stage element has **no explicit height CSS** — its height is
determined by its content (usually an `<img>`). When you want to show the
animation, the natural impulse is `img.style.display = 'none'`. But:

1. `display:none` removes the image from layout
2. The stage collapses to `height: 0`
3. The animation container has `height: 100%` → also 0
4. `scaleScene()` sees `ae.offsetWidth === 0` and returns early
5. No `transform: scale(...)` is applied → the 1096px scene hangs outside
   the viewport and is invisible

### The fix: `visibility:hidden`

```javascript
// WRONG — collapses the stage
if (img) img.style.display = 'none';

// CORRECT — image invisible but stays in layout; stage keeps its height
if (img) img.style.visibility = 'hidden';

// Restore when switching back
if (img) img.style.visibility = '';
```

**Rule of thumb**: if your animation container dimensions depend on a sibling
element's layout, you must keep that element in flow. Use `visibility:hidden`
or `opacity:0` — never `display:none`.

---

## Phase 6 — Wire the trigger

### 6.1 Tab click pattern (head JS)

Tab switch JS lives in head freeform code, wrapped in `DOMContentLoaded`.
The footer IIFE has already run by the time `DOMContentLoaded` fires, so
`getElementById('product-anim')` works.

```javascript
document.addEventListener('DOMContentLoaded', function() {
  var ANIM_TABS = { product: true, projects: true };  // extend for each anim tab
  var animEls = {
    product:  document.getElementById('product-anim'),
    projects: document.getElementById('pmo-anim')
  };
  var tabs = document.querySelectorAll('.section_tab');
  var img  = document.querySelector('.section_stage-img');

  tabs.forEach(function(t) {
    t.addEventListener('click', function(e) {
      e.preventDefault();
      tabs.forEach(function(x) { x.classList.remove('is-active'); });
      this.classList.add('is-active');
      var key = this.getAttribute('data-tab');

      if (ANIM_TABS[key]) {
        /* show animation, hide image */
        if (img) img.style.visibility = 'hidden';     // NOT display:none
        Object.keys(animEls).forEach(function(k) {
          var el = animEls[k];
          if (el) el.style.display = (k === key) ? 'block' : 'none';
        });
        /* play the active one, stop the others */
        if (key === 'product'  && window.productAnimPlay)  window.productAnimPlay();
        if (key === 'projects' && window.pmoAnimPlay)      window.pmoAnimPlay();
        window.productAnimStop && (key !== 'product')  && window.productAnimStop();
        window.pmoAnimStop     && (key !== 'projects') && window.pmoAnimStop();

      } else {
        /* non-anim tab: hide all anims, restore image */
        Object.keys(animEls).forEach(function(k) {
          var el = animEls[k]; if (el) el.style.display = 'none';
        });
        window.productAnimStop && window.productAnimStop();
        window.pmoAnimStop     && window.pmoAnimStop();
        if (img) img.style.visibility = '';
        /* swap image src if needed */
        var url = TAB_IMAGES[key];
        if (img && url) {
          img.classList.remove('is-swapping');
          void img.offsetWidth;
          if (img.getAttribute('src') !== url) img.setAttribute('src', url);
          img.classList.add('is-swapping');
        }
      }
    });
  });
});
```

### 6.2 Scroll-into-view pattern (footer IIFE)

```javascript
var observer = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      window.productAnimPlay && window.productAnimPlay();
    } else {
      window.productAnimStop && window.productAnimStop();
    }
  });
}, { threshold: 0.3 });

var stage = document.querySelector('.your-stage-class');
if (stage) observer.observe(stage);
```

### 6.3 Auto-play on load (footer IIFE)

```javascript
// Auto-start after the DOM has painted
setTimeout(function() {
  scaleScene();
  play();
  loopTimer = setInterval(play, 5200);
}, 400);
```

---

## Phase 7 — Multiple animations on one page

When more than one animation lives in the same Webflow stage:

1. **Give each a unique root ID**: `#product-anim`, `#pmo-anim`, `#hr-anim`
2. **Give each a unique CSS class prefix**: `pa-`, `pmo-`, `hr-`
3. **Give each unique `@keyframes` names**: `pa-fadeIn`, `pmo-fadeIn`, `hr-fadeIn`
4. **Give each its own `window.xyzPlay/xyzStop` pair**
5. **Keep all IIFEs inside one `<script>` block in the footer** — one call to
   `set_page_freeform_code` replaces everything; don't try to append

Layout of a multi-animation footer block:

```javascript
(function(){
  // shared CDN base + helpers
  var CDN = '...';
  function el(...) {...}
  function img(...) {...}

  // ── Animation A ───────────────────────────────────
  // ... build DOM A ...
  window.aAnimPlay = function(){ ... };
  window.aAnimStop = function(){ ... };

  // ── Animation B ───────────────────────────────────
  // ... build DOM B ...
  window.bAnimPlay = function(){ ... };
  window.bAnimStop = function(){ ... };

})();
```

---

## Phase 8 — Execution order & preview compatibility

### The two-script split

| What | Where | Why |
|---|---|---|
| CSS | Head freeform code | Needs to be available before paint |
| Animation DOM builder (JS) | Footer freeform code (IIFE) | Runs after all Webflow elements exist |
| Trigger JS (tab click, etc.) | Head freeform code (`DOMContentLoaded`) | Can reference elements by ID; ID capture happens at DOMContentLoaded which fires after footer IIFE |

### Preview vs published

Head `<script>` tags **do not run in Webflow preview** (the Designer's
preview mode). Footer freeform code IIFEs **do** run in both preview and
published.

This means:
- Animation DOM builder (footer IIFE) → works in preview ✓
- Trigger JS (head DOMContentLoaded) → only works on published page ✗

If you need tab switching to work in preview, move the trigger JS into a
**body `HtmlEmbed` element** created via `data_element_builder`. An HtmlEmbed
placed as the last child of the section runs in both preview and published.

For the typical production workflow (build → publish → test), keeping
trigger JS in head freeform code is fine and simpler.

### Execution order timeline

```
Footer IIFE runs synchronously
   ↓ (all animation DOM elements now exist in the page)
Page DOMContentLoaded fires
   ↓ (head DOMContentLoaded callback runs, getElementById finds animation elements)
User clicks tab
   ↓ (trigger JS sets display:block, calls window.xyzPlay)
window.xyzPlay() → scaleScene() + play() + setInterval
   ↓ (animation renders)
```

---

## Phase 9 — Responsive scaling

The scene has fixed Figma dimensions (e.g. 1096×508). On smaller containers
it would overflow. Use `transform: scale()` to shrink it proportionally.

```javascript
function scaleScene() {
  if (!ae.offsetWidth) return;              // guard when container is hidden
  var ratio = ae.offsetWidth / SCENE_WIDTH; // SCENE_WIDTH = Figma frame width
  scene.style.transform = 'scale(' + ratio + ')';
  // Note: scene height will visually be SCENE_HEIGHT * ratio,
  // but the DOM still reports SCENE_HEIGHT (transform doesn't affect layout flow).
  // If the container height needs to match, set it explicitly:
  // ae.style.height = (SCENE_HEIGHT * ratio) + 'px';
}
window.addEventListener('resize', scaleScene);
```

The container needs `overflow: hidden` so the unscaled scene edges (which
extend beyond the scaled visual bounds) don't bleed out.

---

## Phase 10 — Publish and test

### 10.1 Publish the site

The Webflow MCP applies changes to the **draft** version of the page. They
are not visible on the live URL until you publish.

```
Ask the user to publish from Webflow Designer
— OR —
data_sites_tool → publish_site  (site_id must be inside the action object, not only at envelope level)
```

### 10.2 Test checklist

- [ ] Animation tab: click it → animation appears and plays
- [ ] Animation loops at the expected interval (not stopping after one cycle)
- [ ] Other tabs: animation stops, placeholder image reappears
- [ ] Typewriter text completes and cursor disappears
- [ ] Resize the browser → animation scales, no overflow, no clipping
- [ ] Tab back to animation → replays cleanly (scene resets before re-adding class)
- [ ] Rapid clicking between tabs → no stuck state, no leftover timers
- [ ] `prefers-reduced-motion` set → animation is static (check via DevTools media emulation)

### 10.3 Debug: animation container is 0×0

Open browser DevTools console on the live page and run:

```javascript
var ae = document.getElementById('product-anim');
var stage = ae ? ae.parentElement : null;
console.log({
  aeWidth:   ae ? ae.offsetWidth : 'not found',
  aeHeight:  ae ? ae.offsetHeight : 'not found',
  stageW:    stage ? stage.offsetWidth : 'n/a',
  stageH:    stage ? stage.offsetHeight : 'n/a',
  imgVis:    document.querySelector('.stage-img') ? document.querySelector('.stage-img').style.visibility : 'no img',
  sceneClass: document.querySelector('.pa-scene') ? document.querySelector('.pa-scene').className : 'no scene',
  sceneTransform: document.querySelector('.pa-scene') ? document.querySelector('.pa-scene').style.transform : 'no scene'
});
```

If `aeHeight === 0` → check that the placeholder image is `visibility:hidden`
not `display:none`.

If `sceneTransform === ''` → `scaleScene()` either hasn't been called or was
called when the container was still 0-wide (the `if(!ae.offsetWidth)return`
guard fired).

---

## Technical reference — What Webflow does to your code

### HTML sanitization (the most important thing in this skill)

Webflow sanitizes HTML content in two places:
- `set_page_freeform_code` with `location: "footer"` — the `<script>` tag content
  is NOT sanitized (it's treated as script), but any **HTML markup** you put
  in the footer alongside the script IS sanitized
- `data_whtml_builder` — the `html` property is sanitized before the element
  is stored

**What the sanitizer removes:**
- `class` attributes on all HTML elements → becomes empty string
- `src` attributes on `<img>` elements → removed
- Some `data-*` attributes (inconsistent)
- Inline event handlers (`onclick`, `onload`, etc.)

**What the sanitizer preserves:**
- `id` attributes
- `style` attributes (inline CSS)
- `href` on `<a>` elements
- `<script>` tag content (script is parsed separately, not sanitized)

**Consequence**: you cannot write `<img class="pa-woman" src="...">` in any
Webflow-stored HTML. The class and src will be gone when the page renders.
Build your DOM with JavaScript.

### `set_page_freeform_code` behavior

- Always **replaces** the entire block for that location. Calling it twice
  for the same location keeps only the second call's content.
- Valid `location` values: `"head"` and `"footer"` (NOT `"header"`)
- Head code is injected into `<head>` — CSS and DOMContentLoaded-wrapped JS
- Footer code is injected just before `</body>` — IIFEs run immediately

### Script execution order on page load

1. Head `<script>` tags execute (including your CSS + tab-switch JS registration)
2. Page HTML parses (Webflow elements, HtmlEmbeds)
3. Footer `<script>` tags execute (your animation IIFE builds the DOM)
4. `DOMContentLoaded` fires (your tab-switch JS `getElementById` calls run)
5. `load` event fires (all images loaded)

### Head scripts in Webflow preview

Webflow's in-Designer preview mode does not execute `<script>` tags injected
via `set_page_freeform_code location: "head"`. The footer IIFE runs in both
preview and published. If interactions must work in preview, move JS into an
`HtmlEmbed` element placed inside the section's DOM tree.

### CDN URL format

```
https://cdn.prod.website-files.com/{site_id}/{asset_id}_{original_filename}
```

The `asset_id` is the UUID prefix from the upload's `key` field. Example:

```
https://cdn.prod.website-files.com/6a0183bc6fe692c9451f0726/6a69bd47378bca1cfb1b6f14_processing-chip.svg
```

### `transform` and layout flow

`transform: scale()` does **not** affect CSS layout — the element's margin,
padding, and offset still reflect the **pre-transform** size. A 1096px scene
scaled to 0.4 still occupies 1096px of layout flow. This is why the animation
container needs `overflow: hidden`, and why the Webflow stage container may
need an explicit height set equal to `sceneHeight * ratio` if the stage's
natural height shouldn't be driven by the full 508px.

---

## Applied examples (clay-hero, AI Agents page)

Site `6a0183bc6fe692c9451f0726` · Page `6a0183c26fe692c9451f07d0`

| Tab (`data-tab`) | Anim root ID | CSS prefix | Window API | Typewriter text |
|---|---|---|---|---|
| `product` | `#clay-product-anim` | `cpa-` | `clayProductPlay/Stop` | "Prioritize 250 / feature requests" |
| `projects` | `#clay-pmo-anim` | `pmo-` | `clayPmoPlay/Stop` | "Escalate 140 / project blockers" |

Stage container: `.clay-hero_stage`
Placeholder image: `.clay-hero_stage-img`
Background colors: yellow `#fff8da` (product), stone `#f7f3ea` (PMO)
Scene size: 1096 × 508 px (both)

---

## Extending to new tabs — the minimal diff

To add a new animation tab (e.g. HR, `data-tab="hr"`):

1. **Upload assets** → get CDN URLs
2. **Add CSS block to head** scoped to `#clay-hr-anim .hr-*` with `@keyframes hr-*`
3. **Update head tab JS**:
   - Add `hr: true` to `ANIM_TABS`
   - Add `hr: document.getElementById('clay-hr-anim')` to `animEls`
   - Add `if(key==='hr'&&window.clayHrPlay)window.clayHrPlay();`
   - Add `window.clayHrStop&&key!=='hr'&&window.clayHrStop();`
4. **Extend footer IIFE** with a new DOM-builder block inside the existing IIFE:
   ```javascript
   // ── HR animation ───────────────────────────────────
   var hrEl = el('div','','clay-hr-anim');
   // ... build DOM ...
   if(stage) stage.appendChild(hrEl);
   window.clayHrPlay  = function(){ ... };
   window.clayHrStop  = function(){ ... };
   ```
5. **Publish and test**

---

## Common failure modes

| Symptom | Root cause | Fix |
|---|---|---|
| Animation container is blank / images missing | Webflow stripped `class` and `src` from markup | Rebuild DOM via `document.createElement` + `.className` + `.src` |
| Animation is completely invisible (no elements visible) | Stage collapsed to 0×0 due to `display:none` on placeholder image | Use `visibility:hidden` instead |
| Animation shows once then disappears on resize | `scaleScene()` fired while container was 0-wide; transform never set | Guard `if(!ae.offsetWidth)return`; call `scaleScene()` inside `play()` after `display:block` |
| CSS animation doesn't restart on second play | `classList.remove('animating')` needs a reflow before re-adding | Add `void scene.offsetWidth` between remove and add |
| Typewriter timer persists after tab switch | `clearTimeout` / `clearInterval` not called in stop function | Ensure `stopLoop()` clears both `loopTimer` and `twTimer` |
| Works on published page but not in Webflow preview | Trigger JS is in head freeform code | Move trigger to footer IIFE or body `HtmlEmbed` |
| Upload returns 403 | Policy string corrupted (copy-paste introduced extra char) | Re-request upload credentials, re-upload |
| `data_scripts_tool` fails with "invalid location" | Used `"header"` instead of `"head"` | Use `"head"` |
| Second `set_page_freeform_code` call wiped the first | Each call replaces the entire block | Combine all head CSS/JS into one call; all footer JS into one call |


# Marquee carousel (endless horizontal scroll)

A row that scrolls forever without a visible jump. The whole trick is **duplicated content +
wrap**: translate the track by exactly one copy-width and modulo-wrap, so a second identical
copy slides into the spot the first just left.

## 1. Structure — track holds ≥2 identical groups
```html
<div class="row">                 <!-- clips at the stage edge (overflow:hidden on stage) -->
  <div class="track">             <!-- flex; width:max-content; this is what translates -->
    <div class="group">…items…</div>   <!-- copy 1 -->
    <div class="group">…items…</div>   <!-- copy 2 (identical) -->
  </div>
</div>
```
```css
.track, .group { display: flex; gap: 26px; }
.track { width: max-content; will-change: transform; }
.group { flex: none; }
```
Build the item **once** (a component) and fill each group from a content array; rotate the
array order per row so columns don't line up. Duplicate enough groups to overflow the
viewport at least twice.

## 2. The scroll tween (seamless wrap)
Measure one group's width **after fonts + images load** (widths depend on both), then run an
always-on tween per row:
```js
const copyW = group.offsetWidth + gapPx;         // one group + the trailing gap
const wrap  = gsap.utils.wrap(-copyW, 0);
gsap.set(track, { x: dir > 0 ? -copyW : 0 });     // dir +1 → scroll right, -1 → left
gsap.to(track, {
  x: (dir > 0 ? '+=' : '-=') + copyW,
  duration: copyW / speedPxPerSec,
  ease: 'none', repeat: -1,
  modifiers: { x: v => wrap(parseFloat(v)) + 'px' },  // ← keeps it seamless
});
```
Gate measurement:
```js
Promise.all([
  ...imgs.filter(i => !i.complete).map(i => new Promise(r => (i.onload = i.onerror = r))),
  document.fonts?.ready ?? Promise.resolve(),
]).then(start);
```

## 3. Multiple rows = parallax
Run each row as its **own** tween with a different direction and speed — e.g. top→right @70,
middle→left @62, bottom→right @78 px/s. Slightly different speeds read as depth/organic
motion rather than a rigid block.

## 4. Moving gradient-stroke "reflection" (optional shimmer)
Give each pill a gradient **border** via the mask-composite trick, then loop its
`background-position` so a light band sweeps the edge:
```css
.pill::before {
  content:""; position:absolute; inset:0; border-radius:inherit; padding:1px;
  background: linear-gradient(115deg, rgba(255,255,255,.06), rgba(255,255,255,.55) 22%,
                                      rgba(255,255,255,.16) 46%, rgba(255,255,255,.06));
  background-size: 240% 100%;
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
          mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  animation: shine 3.6s linear infinite;
  animation-delay: var(--shine-delay, 0s);      /* set per pill so they don't sync */
}
@keyframes shine { to { background-position: -240% 0; } }
```
Set `--shine-delay` inline per item (e.g. `-(i*0.5)s`) so the highlights are offset.

## 5. As a layer inside a bigger loop
The carousel usually lives inside a `motion` forward-reset loop: the rows fade/scale
in, scroll while visible (~2s), then fade/scale out. Keep the scroll tweens **independent**
of the master timeline (they just run forever); the master only animates the rows' opacity /
transform for enter/exit. Because the rows are invisible at the loop boundary, the scroll
position there is irrelevant.

## 6. Porting to Remotion (GIF/MP4)
Frame-math replaces the tween: `x = -offset + dir * speed * (frame / fps)`. Since the rows
are invisible at the loop boundary, **skip the wrap** — a plain linear translate never shows
a seam. Give enough group copies + a deep start `offset` (e.g. `-2 * copyW`) that the screen
stays filled across the whole scroll range. Load the font via `@remotion/google-fonts` and
rebuild the `::before` reflection as a real overlay `<div>` (pseudo-elements can't be
frame-styled). See `export-as-gif`.

## Verify
- Sample the track transform across a couple of real seconds — it should advance smoothly;
  headless snapshots can look frozen because `requestAnimationFrame` is throttled while not
  rendering, so also check `gsap.getTweensOf(track)[0].paused() === false` and its `progress()`.
- Watch one full wrap: the moment `x` hits `-copyW` must look identical to `x = 0` (no gap,
  no jump). If it seams, `copyW` was measured before fonts/images settled.
- Two more measurement traps: (1) `getBoundingClientRect().width` can return 0/null right after navigate/reload — wait for stable layout and assert the value is sane before using it. (2) If the marquee lives on a `transform: scale()` stage (common for Figma-ported fixed banners), `getBoundingClientRect` returns *scaled* px while `offsetWidth` is transform-invariant — measure `copyW` with `offsetWidth` (as above), and divide a getBCR by the scaler factor only for elements *inside* the scaled subtree (see `frame-building`). Magnitude-check widths (~50px/char at a 96px font, not ~95) to catch a ~1.9× scale inflation. In the Remotion port, prefer measuring text at render time (`measuring-text`) over baking in the measured px.

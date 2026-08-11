# Word ticker (vertical slot-machine text)

One word in a line swaps to the next on a timer, rolling vertically like a slot reel while
the surrounding text stays put and centered. The whole trick is a **fixed-height clip with
two stacked word slots** whose vertical offset and container width animate together.

## Structure
```
line:  "grows your " + <clip>
<clip>  inline-block; overflow:hidden; height:1.3em; position:relative; width:<curW>
  <slot A>  position:absolute; left:0; top:0   ← outgoing word
  <slot B>  position:absolute; left:0; top:0   ← incoming word
```
- The clip's `height` is `1.3em` (or `fontSize × lineHeight`) — **derive it from font metrics,
  never from `getBoundingClientRect`**; a measured height drags in transform/scale bugs.
- Both slots sit at `left:0` inside the clip; only their `translateY` differs.
- The word color/weight lives on the slot; the clip just masks the overflow.

## The wipe (one step)
Over a short `WIPE` window, roll the reel up by one line-height and morph the clip width:
- outgoing slot: `translateY 0 → −LINE_H`
- incoming slot: `translateY +LINE_H → 0`
- clip width: `curW → nextW`  (ease `power2.inOut` / `Easing.inOut(Easing.cubic)`)

Then hold the new word for `HOLD` before the next step. Per-word period `P = HOLD + WIPE`.

### GSAP (live HTML)
```js
function step() {
  cur = (cur + 1) % WORDS.length;
  const next = mkSlot(WORDS[cur]); gsap.set(next, { y: LINE_H }); clip.appendChild(next);
  const nextW = measureWord(WORDS[cur]);           // see "Measure widths safely"
  const tl = gsap.timeline({ onComplete: () => { active.remove(); active = next;
                                                 gsap.delayedCall(HOLD, step); } });
  tl.to(active, { y: -LINE_H, duration: WIPE, ease: 'power2.inOut' }, 0)
    .to(next,   { y: 0,       duration: WIPE, ease: 'power2.inOut' }, 0)
    .to(clip,   { width: nextW, duration: WIPE, ease: 'power2.inOut' }, 0);
}
gsap.delayedCall(HOLD, step);
```

### Remotion (frame-based export)
Everything is `f(useCurrentFrame())` — no timers, no CSS transitions:
```ts
const k = Math.min(WORDS.length - 1, Math.floor(s / P));   // current word index
const localT = s - k * P;
const cur = WORDS[k % WORDS.length], next = WORDS[(k + 1) % WORDS.length];
let clipW = W[cur], outY = 0, inY = LINE_H;                 // HOLD phase
if (localT >= HOLD) {                                       // WIPE phase
  const wp = interpolate(localT, [HOLD, P], [0, 1],
    { easing: Easing.inOut(Easing.cubic), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  clipW = interpolate(wp, [0, 1], [W[cur], W[next]]);
  outY = -LINE_H * wp; inY = LINE_H * (1 - wp);
}
```
Render two spans at `translateY(outY)` / `translateY(inY)` inside a `width: clipW` clip.

## Keep the headline centered (do this, it bites)
The word changes width every step. Center each line with a **fixed full-width block**, so it
sits on the stage midline no matter how wide the current word is:
```css
.headline { position:absolute; left:0; width:STAGE_W; text-align:center; white-space:nowrap; }
```
Do **not** use `left:50%` + `translateX(-50%)` shrink-to-fit around the fixed-width clip: if
the clip is even slightly mis-sized the line overflows and decenters. And because the slots
hug `left:0`, an over-wide clip leaves empty space to the word's right and shifts the visible
(centered) text left — so **a wrong clip width decenters the headline even with perfect
centering CSS**. If a centering tweak doesn't fix the drift, the widths are wrong — fix those.

## Measure widths safely (the #1 bug here)
Wrong `W[word]` values are what break this ticker. Get them right:
- **Best:** derive at render time — Remotion `measureText` (see `measuring-text`), or in the
  browser size the clip to its content — instead of hardcoding px.
- **If you must hardcode:** measure a probe span at the real `font-size` / `font-weight` /
  `letter-spacing`. On a `transform: scale()` stage, divide a `getBoundingClientRect()` by the
  scaler factor **only** for elements *inside* the scaled subtree — a probe on `document.body`
  is already at scale 1 and reports true px; dividing it inflates the value by `1/scale`
  (~1.875× at a 720px-tall viewport) and decenters everything. `offsetWidth` is
  scale-invariant. (Full trap in `frame-building`.)
- **Sanity-check:** Latin text at 96px is ≈ 50px/char, not ~95 — a ~1.9× deviation is a
  scale-inflation bug; catch it before baking the number in.

## Seamless loop
Make the ticker the clock for the whole loop: `L = WORDS.length × P`. Choose `HOLD`/`WIPE` so
`L` lands on a whole frame count (e.g. 5 × (1.5 + 0.3) = 9.0s = 270f @30fps — note a live
`WIPE` of 0.32 may need nudging to 0.30 for the export). At `t=L` the reel has completed the
last→first wipe, so the first word is fully shown again — identical to `t=0`. If other looped
motion shares the stage, snap their periods to divisors of `L` too (see `export-as-gif`'s
period-snapping) and prove `value` **and** `velocity` match at the seam.

## Tunables
Expose `WORDS`, `HOLD`, `WIPE`, `LINE_H`, and the per-word `W` map as named constants at the
top so cadence and copy are trivially editable and the loop length stays derivable.

## Verify
- Screenshot the rest frame (word fully shown, centered), a mid-wipe frame (both words
  visible, reel mid-roll), and the widest word (e.g. "accounts") — confirm it stays centered
  and unclipped.
- Confirm the boundary: the last rendered frame's incoming word == the first word at `t=0`,
  same width, `translateY(0)` — no jump.

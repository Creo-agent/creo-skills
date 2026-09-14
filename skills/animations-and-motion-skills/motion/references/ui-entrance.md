
# GSAP UI Entrance (yoyo orchestration)

Add an orchestrated multi-beat entrance to a DOM card inside an existing GSAP yoyo
timeline. The key insight: **author the entrance on the forward pass as a leave
(visible → hidden)**. The yoyo reversal plays it back as hidden → visible automatically,
with correct hold states at both ends — no extra tweens, no onComplete callbacks.

## The core principle

In a yoyo timeline, a tween at time `T` on the forward pass plays at time `(total − T)` on
the reverse. So the entrance **order** is controlled by the forward **position**:
- **Latest** forward position → plays **earliest** on the reverse = **first** to enter
- **Earliest** forward position → plays **latest** on the reverse = **last** to enter

To get **box → text → rows** (box enters first), author the forward leave in the opposite order:

| Beat | Forward position | Forward action | Reverse (entrance) |
|---|---|---|---|
| Box | `BASE + 1.00` (latest) | bg fades out, scaleY collapses | bg scales in, fades in — **1st** |
| Text | `BASE + 0.62` (mid) | lines fade out, slide down | lines rise in, stagger — **2nd** |
| Rows | `BASE + 0.00` (earliest) | rows fade out, slide up | rows cascade in — **3rd** |

> **Not on a yoyo loop?** If the outer loop is a *forward-reset* (it has a distinct
> end-screen, so it can't yoyo — see `motion`), don't use the reverse-leave trick.
> Author an explicit **enter** tween and an explicit **exit** tween, and set each stagger's
> `from` independently to lead from either end: e.g. enter `from:'start'` (top leads out),
> exit `from:'end'` (bottom leads back in). You write two tweens instead of one, but the
> ordering is direct and you don't have to think in reverse.

## 0. Prerequisites

The card must already be built as separate animatable layers (from `frame-building`):
- `.card-bg` — the background box (position:absolute, inset:0)
- `.card-content` with `.card-title-line` spans and `.card-row` elements

The outer loop must use `yoyo: true`:
```js
const tl = gsap.timeline({ repeat: -1, yoyo: true, repeatDelay: HOLD });
```

## 1. Exclude the card from the generic collapse

If the other cards all fly to a center point together, **exclude this card** from that batch
so it assembles in place with its own orchestration instead of also flying somewhere:

```js
// All items except the one with the UI entrance:
const collapseItems = Array.from(
  document.querySelectorAll('.floating-item')
).filter(el => !el.classList.contains('is-cc'));

tl.to(collapseItems, { /* fly-to-center tween */ }, 0);
// The CC card doesn't move — its inner elements animate instead.
```

## 2. Define timing constants at the top

```js
const CC_BASE        = 0.80;   // anchor — how far into the timeline this card's action starts

const CC_BOX_AT      = CC_BASE + 1.00;  // LATEST forward ⇒ FIRST to enter on reverse
const CC_BOX_DUR     = 0.42;

const CC_TXT_AT      = CC_BASE + 0.62;  // MIDDLE beat
const CC_TXT_DUR     = 0.30;
const CC_TXT_STAGGER = 0.12;   // gap between the two title lines

const CC_ROW_AT      = CC_BASE + 0.00;  // EARLIEST forward ⇒ LAST to enter on reverse
const CC_ROW_DUR     = 0.42;
const CC_ROW_STAGGER = 0.07;   // gap between rows (email→meeting→call→message)
```

Keep all beats as `CC_BASE + offset`. Bumping `CC_BASE` shifts the whole sequence
on the timeline without changing the orchestration.

## 3. Add the three forward-leave tweens

All three use `power2.in` — on the reverse this becomes `power2.out`, which is the
same easing family the rest of the animation uses (so everything reads as one motion).

```js
const ccBg    = document.querySelector('.is-cc .cc-bg');
const ccLines = document.querySelectorAll('.is-cc .cc-title-line');
const ccRows  = document.querySelectorAll('.is-cc .cc-row');

/* ── Rows: earliest on the leave ⇒ LAST on the entrance (cascade in) ── */
tl.to(ccRows, {
  autoAlpha: 0,
  y: -7,                         /* slide up slightly as they leave */
  scale: 0.92,
  transformOrigin: 'left center',
  ease: 'power2.in',
  duration: CC_ROW_DUR,
  stagger: {
    each: CC_ROW_STAGGER,
    from: 'end',                 /* from:'end' on leave → first row enters FIRST on reverse */
  },
}, CC_ROW_AT);

/* ── Title lines: middle beat ── */
tl.to(ccLines, {
  autoAlpha: 0,
  y: 10,                         /* slide down slightly as they leave */
  ease: 'power2.in',
  duration: CC_TXT_DUR,
  stagger: {
    each: CC_TXT_STAGGER,
    from: 'end',                 /* from:'end' → line 1 enters first on reverse */
  },
}, CC_TXT_AT);

/* ── Box: latest on the leave ⇒ FIRST on the entrance ── */
tl.to(ccBg, {
  scaleY: 0.4,                   /* collapses vertically to a thin bar */
  autoAlpha: 0,
  transformOrigin: 'center center', /* grows from center → feels natural */
  ease: 'power2.in',
  duration: CC_BOX_DUR,
}, CC_BOX_AT);
```

## 4. Stagger direction explained

`from: 'end'` on the **forward** leave means the bottom row disappears first, then up.
On the **reverse**, this replays bottom-up → reads as top-down entrance (row 1, then 2, then 3, then 4).
Use `from: 'start'` if you want the reverse entrance to go bottom-up.

Same logic applies to title lines: `from: 'end'` on leave means line 2 exits first →
line 1 enters first on the reverse entrance.

## 5. Verify by scrubbing the timeline

Don't eyeball a playing animation. Pause and sample states:

```js
const tl = gsap.globalTimeline.getChildren(false, false, true)[0];
const totalDur = tl.totalDuration();   // forward + repeatDelay + reverse

// Forward pass: box/text/rows should all be HIDDEN at the "collapsed" end
tl.totalTime(totalDur / 2 - 0.01, true);
// Read: ccBg.style.opacity, ccLines[0].style.opacity, ccRows[0].style.opacity — should all be 0

// Reverse pass checkpoints (sample 3 points):
const rev = (frac) => tl.totalTime(totalDur / 2 + (totalDur / 2) * frac, true);

rev(0.15);   // box should be mid-scale, text/rows hidden
rev(0.40);   // box fully in; title lines mid-entrance (autoAlpha > 0), rows still hidden
rev(0.65);   // box in, both lines fully visible, rows cascading in

// Home state: everything fully assembled
tl.totalTime(0, true);
// All elements should be at autoAlpha: 1, y: 0, scale: 1, scaleY: 1
```

Fix any beat that's wrong (usually an off-by-one on `_AT` or a flipped `from` direction).

## 6. Tuning the feel

| Want | Change |
|---|---|
| Box entrance slower / more dramatic | Increase `CC_BOX_DUR` (e.g. 0.55) |
| Bigger overlap between box and text | Decrease `CC_TXT_AT` offset (closer to `CC_BOX_AT`) |
| Rows cascade faster | Decrease `CC_ROW_STAGGER` (e.g. 0.04) |
| Entire sequence shifted earlier | Decrease `CC_BASE` |
| Rows slide in from a bigger distance | Increase `y` value in the rows tween (e.g. `y: -14`) |
| Text slides in from below (not above) | Rows use `y: -7`; for a rise-from-below feel use positive `y` for text |

## 7. Easing rule

All leave tweens use `power2.in`. On the yoyo reverse this becomes `power2.out`.
Do NOT mix eases across beats — keep everything `power2.*` so the whole sequence
reads as one unified family. If the outer loop uses `power2.in` for the card flyaway,
the UI entrance will automatically feel consistent.

## Hand off

Once verified:
- Pass to `export-as-gif` for a rendered loop
- Pass to `motion` for timing adjustments to the outer loop
- Copy the `CC_*` constants to `frame-building` notes so the next rebuild knows the beat map


# Loop animator

Build an auto-playing, seamless loop out of a resting composition. The most common
pitfall is a **jump cut** at the loop boundary; the patterns below avoid it. Consult
the `gsap` skill for library specifics; this skill is about the *looping structure*.

## Decide the loop shape first
- **Yoyo (recommended for reveals):** play forward → hold → play in **reverse** → hold →
  repeat. Because the reverse is an exact mirror and both ends rest at the same frame,
  it loops with zero discontinuity. Use for "reveal then gracefully undo".
- **Restart:** forward → hold → hard-reset to frame 0 → replay. Only when a hard cut is
  actually wanted; otherwise it reads as a glitch.
- **Continuous:** endless motion with no start/end state (drifting, rotating). Just
  `repeat: -1` on looping tweens. For endless *horizontal* scroll (message tickers, logo
  strips, card carousels) see the `marquee-carousel` skill.
- **Forward-reset (when yoyo is WRONG):** if the loop contains a distinct *sequential
  phase* that must not run backwards — a second "screen"/state that appears after the
  reveal (a panel of messages, a results view, a CTA) — yoyo rewinds that whole phase in
  reverse, which reads as broken. Instead build a `repeat: -1` **forward** timeline and
  engineer its **end state to equal its start** with explicit "undo" tweens. You lose the
  free reverse but gain full control of exit timing and ordering (see below).

## Core GSAP structure (yoyo)
```js
const tl = gsap.timeline({
  repeat: -1,
  yoyo: true,          // smooth reverse back to the first frame — no cut
  repeatDelay: HOLD,   // linger at the revealed frame (and at frame 0) before turning
  defaults: { ease: 'none' },
});
```
Drive everything off this one timeline so the whole scene reverses coherently.

## Core GSAP structure (forward-reset)
When a distinct end-screen rules out yoyo, run one forward timeline and *undo* at the end:
```js
const tl = gsap.timeline({ repeat: -1, defaults: { ease: 'none' } });
tl.to(cards,    { /* collapse in */ }, 0);
tl.to(colorImg, { autoAlpha: 1 }, COLOR_AT);          // line-art → color
tl.to(screen,   { autoAlpha: 1, scale: 1 }, ENTER_AT);// the new screen appears…
tl.to(screen,   { autoAlpha: 0, scale: 0.1 }, EXIT_AT);// …then undo everything so the
tl.to(colorImg, { autoAlpha: 0 }, EXIT_AT);            //    last frame == the first frame
tl.to(cards,    { x: 0, y: 0, scale: 1, opacity: 1 }, EXIT_AT + 0.15);
tl.to({}, { duration: HOLD });                         // linger on frame 1 before repeat
```
The loop is seamless **only if the end state equals the initial DOM state** (cards at rest,
color hidden, screen scaled back to 0). Verify that equality explicitly (see below) — it's
the whole trick.

## Patterns

### Ramping-up stagger (sequenced, not all-at-once)
Give each item its own start time with **shrinking gaps** so the sequence accelerates,
while each item's own duration is longer than the gap so flights overlap:
```js
tl.to(items, {
  /* ...target props... */
  duration: ITEM_DURATION,
  stagger: { each: STAGGER, from: 'start', ease: 'power2.out' }, // power2.out → gaps shrink → ramps up
});
```
`power2.out` on the *stagger* accelerates the cadence; `power2.in` decelerates it.

### Collapse / converge to a point
To fly elements into a focal point (e.g. a central figure), compute the delta from each
element's live center to the target center — so it keeps working if layout or assets
change:
```js
x: () => { const i = el.getBoundingClientRect(), a = target.getBoundingClientRect();
           return a.left + a.width/2 - (i.left + i.width/2); },
// same for y; pair with scale→0.1, opacity→0
```
Scaling uses the default transform-origin (center), so translate + scale keeps the
center landing on the target.

### Layer cross-fade (e.g. line-art → color)
Stack two images; fade one `autoAlpha` 0→1 and the other 1→0 over an overlapping window.
`autoAlpha` also toggles `visibility`, which is cleaner than `opacity` alone.

### Emerge from a point (the inverse of collapse) + directional lead
To make elements *grow out of* a focal figure (the reverse of collapse-to-a-point), anchor
each element's `transformOrigin` at that figure's center **in the element's own local
coords**, then scale `0.1 → 1`. Measure the center in stage space, undoing the preview
scaler so the origin is correct at any display size:
```js
const st = stage.getBoundingClientRect(), sc = st.width / STAGE_PX;   // scaler factor
const a  = hero.getBoundingClientRect();
const cx = (a.left + a.width  / 2 - st.left) / sc;   // stage-local px
const cy = (a.top  + a.height / 2 - st.top ) / sc;
rows.forEach(r => gsap.set(r, { transformOrigin: `${cx}px ${cy - r.offsetTop}px`, scale: 0.1 }));
// enter → scale:1  (grows out of the hero) ;  exit → scale:0.1  (collapses back in)
```
**Directional lead:** control which item leads with the stagger's `from`. On a *forward-reset*
loop you set enter and exit independently — `from:'start'` on the entrance (top leads out)
and `from:'end'` on the exit (bottom leads back in) gives opposite orders for appearing vs
disappearing, no yoyo reverse needed. (On a yoyo loop you'd instead flip `from` on a single
authored pass — see `gsap-ui-entrance`.)

### Export-ready fixed stage
(If you're starting from nothing, `animation-scaffold` emits this whole setup ready to go.)
For a canvas destined for video/social, use a fixed-size stage (e.g. 1080×1080) and a
JS scaler that only *visually* fits it to the viewport — never change the true render
size. Center via `position: fixed; top/left: 50%` + `transform: translate(-50%,-50%) scale(s)`
(CSS `scale(calc(100vw/1080))` is invalid — `scale()` needs a unitless number, so set it in JS).

## Verify deterministically
Headless screenshots of a live `scrub`/playing timeline lag. Grab the timeline and seek:
```js
const tl = gsap.globalTimeline.getChildren(true,false,true)[0];
tl.pause(0);              // or tl.progress(0.5,true) — screenshot the exact state
```
Confirm: the first frame (rest), a mid frame (motion), the revealed frame, and — for
yoyo — that a reverse frame mirrors a forward frame. Sample `tl.time()` over a few real
seconds to prove it rises then falls (reverse) with no jump to 0 (no cut).

**For a forward-reset loop**, seek to `tl.duration()` and confirm every element matches its
frame-0 state (transform identity, exit-scale back to its start, layers hidden/shown as at
start) — that equality is what proves the loop won't cut. When other tweens exist (e.g.
always-on `marquee-carousel` scrollers), `getChildren()[0]` may not be the master; select it
explicitly: `getChildren(true,false,true).filter(c => c instanceof gsap.core.Timeline).find(t => t.duration() > 4)`.

## Tunables to expose
Group timing as named constants at the top (durations, stagger, hold, delays, ease
choices) so they're trivially editable. This makes handoff to `export-as-gif` and
`resize-animation` clean.

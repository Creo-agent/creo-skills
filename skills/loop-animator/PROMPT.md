
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
  `repeat: -1` on looping tweens.

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

### Export-ready fixed stage
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

## Tunables to expose
Group timing as named constants at the top (durations, stagger, hold, delays, ease
choices) so they're trivially editable. This makes handoff to `export-as-gif` and
`resize-animation` clean.

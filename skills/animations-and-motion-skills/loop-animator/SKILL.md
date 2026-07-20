---
name: loop-animator
description: >-
  Turn a static composition or a scroll/hover-triggered web animation into a smooth, auto-playing looping animation in HTML/CSS/JS with GSAP. Go-to skill whenever the user wants motion to loop / auto-play / play on its own / repeat / run continuously, or to convert a scroll- or hover-triggered effect into a hands-free loop — e.g. "make these cards loop", "it should reveal then reset smoothly without a jump cut", "run continuously on a kiosk screen". Covers seamless looping (no hard cut), staggered/ramping reveals, collapse-to-a-point motion, and cross-fades. Prefer this over the extract, gif-export, figma, and resize skills whenever the deliverable is a running looping animation rather than a file on disk. Do NOT use for: grabbing an animation off a website, rendering to gif/mp4, writing for-loops in code, matching a Figma layout, or resizing to a new format.
---

# Loop Animator

Build an auto-playing, seamless loop out of a resting composition or a scroll-driven
animation. The signature pitfall is a **jump cut** at the loop boundary; this skill's
patterns avoid it. Consult the `gsap` skill for library specifics — this skill is about
the *looping structure*.

## When This Skill Activates

- "Make these cards animate in a loop instead of on scroll"
- "It should reveal, hold, then reset smoothly and repeat — no hard cut"
- "Turn this hover effect into an auto-playing loop for a kiosk"
- "Add a seamless breathing loop to this banner"

Keywords: `loop`, `auto-play`, `repeat`, `run continuously`, `seamless`, `yoyo`,
`stagger`, `no jump cut`, `autoplay`.

## What This Skill Does

- Chooses the loop shape (yoyo / restart / continuous) — yoyo for clean reveals.
- Builds one GSAP timeline with `repeat: -1`, `yoyo`, `repeatDelay`.
- Adds ramping-up stagger, collapse-to-a-point motion, and layer cross-fades.
- Uses a fixed export-ready stage + JS scaler when destined for video/social.
- Verifies deterministically by seeking timeline states and sampling `.time()`.

---

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

### Organic float wiggle (y + rotation — not just y-bob)

A plain vertical y-bob looks mechanical. Upgrade to `y + rotation` for organic, breathing motion:

```js
// Bubble floats up and tilts slightly — one unified gesture
gsap.to('#bubble', {
  y: -5,
  rotation: 1.8,                     // degrees; use negative for the opposite bubble
  transformOrigin: '50% 50%',        // rotate around the element's own center
  duration: 1.2,
  ease: 'sine.inOut',
  yoyo: true,
  repeat: 1,                         // one yoyo = up→hold→down, total 2.4s
});
```

**Group the cursor inside the bubble container.** If the cursor image is a child of the bubble element, it rotates and translates with the parent automatically — one organic motion rather than two separate competing animations. Do not animate the cursor separately with its own float; put it inside the parent and let it ride along.

**Rotation sign:** alternate between positive (+) and negative (−) rotation for elements that sit on different sides of the screen. This makes the floats feel independent rather than synchronized.

### Float period must divide loop duration evenly

If the main loop duration is `LOOP` seconds, every ambient float period must divide `LOOP` evenly — otherwise the float ends mid-cycle at the loop boundary, causing a jump cut.

**Example (LOOP = 6.0s):**
- `duration: 1.0, yoyo: true, repeat: 1` → total period = 2.0s ✓ (6 / 2 = 3, no remainder)
- `duration: 1.2, yoyo: true, repeat: 1` → total period = 2.4s ✗ (6 / 2.4 = 2.5 — not exact! Will cut)
- Safe choice: `duration: 1.5, yoyo: true, repeat: 1` → 3.0s ✓

Check: `LOOP % (duration * 2) === 0` (for yoyo/repeat:1). Adjust duration until this holds.

## Tunables to expose
Group timing as named constants at the top (durations, stagger, hold, delays, ease
choices) so they're trivially editable. This makes handoff to `export-as-gif` and
`resize-animation` clean.

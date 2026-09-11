# Easings

Complete easing reference for motion and animation work — all 30 functions from
[easings.net](https://easings.net). Use this to pick the right feel, then copy the JS body
or CSS `cubic-bezier()` directly into your animation code.

## Direction rule

| Direction | Pattern | When to use |
|-----------|---------|-------------|
| **easeOut** | Fast start → slow end | Entrances — something arriving |
| **easeIn** | Slow start → fast end | Exits — something leaving |
| **easeInOut** | Slow → fast → slow | State changes — A to B, stays on screen |

## Family intensity

From gentlest to most dramatic:

```
Sine < Quad < Cubic < Quart < Quint < Expo / Circ
```

Back / Elastic / Bounce are in their own category — they exceed the 0–1 range and produce
overshoot or oscillation. Use intentionally; avoid in tight UI loops.

## Pick by use-case

| You want… | Best pick | Why |
|-----------|-----------|-----|
| Card / panel sliding in | `easeOutQuart` | Arrives fast, settles cleanly |
| Card / panel sliding out | `easeInQuart` | Leaves quickly, no hesitation |
| Modal or drawer opening | `easeOutCubic` | Smooth arrival, not overdramatic |
| Tooltip / small popover | `easeOutQuad` | Gentle, unobtrusive |
| Hero element entering viewport | `easeOutExpo` | Dramatic fast-start, long deceleration tail |
| Text / stagger entrance | `easeOutCubic` or `easeOutQuart` | Polished, readable |
| Snapping into place | `easeOutBack` | Slight overshoot gives it physicality |
| Button press / click feedback | `easeInOutQuad` | Symmetrical, subtle |
| Loading spinner / loop | `easeInOutSine` | Smooth acceleration both ways |
| Scroll / parallax | `easeInOutCubic` | Comfortable, no jarring edges |
| Number counter | `easeOutExpo` | Rushes early, ticks slowly at the end |
| Progress bar | `easeInOutQuad` | Natural, no drama |
| Logo / brand reveal | `easeOutExpo` or `easeOutBack` | Premium feel, confident landing |
| Something being dismissed | `easeInCubic` | Accelerates away — intentional |
| Playful pop / scale-up | `easeOutBack` | Tiny overshoot reads as "alive" |
| Playful bounce (game-like) | `easeOutBounce` | Literal bounce — use sparingly |
| Rubber-band / spring effect | `easeOutElastic` | Oscillates past end — very playful |
| Smooth scene transition | `easeInOutSine` | Invisible curve |
| Marquee / continuous scroll | `linear` | Constant speed, no rhythm disruption |
| Organic / breathing motion | `easeInOutSine` | Mirrors natural breath cycle |
| Cinematic camera move | `easeInOutCubic` or `easeInOutQuart` | Smooth ramp up and down |

## CSS cubic-bezier cheat-sheet

```
linear              —  linear
easeInSine          —  cubic-bezier(0.12, 0, 0.39, 0)
easeOutSine         —  cubic-bezier(0.61, 1, 0.88, 1)
easeInOutSine       —  cubic-bezier(0.37, 0, 0.63, 1)
easeInQuad          —  cubic-bezier(0.11, 0, 0.5, 0)
easeOutQuad         —  cubic-bezier(0.5, 1, 0.89, 1)
easeInOutQuad       —  cubic-bezier(0.45, 0, 0.55, 1)
easeInCubic         —  cubic-bezier(0.32, 0, 0.67, 0)
easeOutCubic        —  cubic-bezier(0.33, 1, 0.68, 1)
easeInOutCubic      —  cubic-bezier(0.65, 0, 0.35, 1)
easeInQuart         —  cubic-bezier(0.5, 0, 0.75, 0)
easeOutQuart        —  cubic-bezier(0.25, 1, 0.5, 1)
easeInOutQuart      —  cubic-bezier(0.76, 0, 0.24, 1)
easeInQuint         —  cubic-bezier(0.64, 0, 0.78, 0)
easeOutQuint        —  cubic-bezier(0.22, 1, 0.36, 1)
easeInOutQuint      —  cubic-bezier(0.83, 0, 0.17, 1)
easeInExpo          —  cubic-bezier(0.7, 0, 0.84, 0)
easeOutExpo         —  cubic-bezier(0.16, 1, 0.3, 1)
easeInOutExpo       —  cubic-bezier(0.87, 0, 0.13, 1)
easeInCirc          —  cubic-bezier(0.55, 0, 1, 0.45)
easeOutCirc         —  cubic-bezier(0, 0.55, 0.45, 1)
easeInOutCirc       —  cubic-bezier(0.85, 0, 0.15, 1)
easeInBack          —  cubic-bezier(0.36, 0, 0.66, -0.56)
easeOutBack         —  cubic-bezier(0.34, 1.56, 0.64, 1)
easeInOutBack       —  cubic-bezier(0.68, -0.6, 0.32, 1.6)
easeInElastic       —  no CSS equivalent
easeOutElastic      —  no CSS equivalent
easeInOutElastic    —  no CSS equivalent
easeInBounce        —  no CSS equivalent
easeOutBounce       —  no CSS equivalent
easeInOutBounce     —  no CSS equivalent
```

## GSAP ease string shorthands

```
"power1.in/out/inOut"  ≈  Quad family
"power2.in/out/inOut"  ≈  Cubic family
"power3.in/out/inOut"  ≈  Quart family
"power4.in/out/inOut"  ≈  Quint family
"expo.in/out/inOut"    ≈  Expo family
"circ.in/out/inOut"    ≈  Circ family
"sine.in/out/inOut"    ≈  Sine family
"back.in/out/inOut"    ≈  Back family  (default overshoot 1.7)
"elastic.in/out/inOut" ≈  Elastic family
"bounce.in/out/inOut"  ≈  Bounce family
"none" / "linear"      ≈  linear
```

For Remotion and CSS, use the cubic-bezier values above directly.

## Full JS function bodies

See `references/functions.md` for every function body (self-contained, no imports needed).

---
name: easings
description: |
  WHAT: Complete easing function reference — all 30 easings from easings.net. Each entry has its JS function body, CSS cubic-bezier value (where available), and a plain-English feel description. Covers Sine, Quad, Cubic, Quart, Quint, Expo, Circ, Back, Elastic, Bounce — each in easeIn / easeOut / easeInOut variants, plus linear.
  TRIGGERS: picking or naming an easing for a tween/animation ("which ease for a spring feel?", "what cubic-bezier is easeInOutQuart?", "I need something bouncy at the end"); converting between JS function and CSS cubic-bezier; understanding the character of an ease; any question containing "ease", "easing", "cubic-bezier", or a specific easing name.
  NOT FOR: writing the GSAP tween itself → use gsap/. Motion recipes (loops, entrances) → use motion/. Full animation pipeline → use figma-to-animation/.

  WHEN TO REACH FOR THIS SKILL — decision tree:
  1. Is the question about WHICH easing to use, or WHAT a named easing looks/feels like? → YES: use this skill.
  2. Does the prompt contain any of these words: ease, easing, cubic-bezier, bouncy, springy, snappy, smooth, overshoot, elastic, linear, acceleration, deceleration, curve, feel, natural motion? → YES: use this skill.
  3. Is code being written that includes an `ease:` prop, a `transition-timing-function`, or a cubic-bezier() call and no value has been chosen yet? → YES: use this skill to pick the right one before writing.
  4. Is someone asking to convert between a JS easing function and its CSS equivalent (or vice versa)? → YES: use this skill.
  5. Is the task writing the full tween/timeline logic, building a motion recipe, or exporting a video? → NO: this skill is not the primary — use gsap/, motion/, or figma-to-animation/ instead, but still consult this skill if an ease needs to be chosen within that task.
---

# Easings

All 30 easing functions from [easings.net](https://easings.net) (source: github.com/ai/easings.net).
Use this as a lookup — pick the right feel, then copy the JS function or CSS cubic-bezier into your animation.

## When to use this skill

Reach for this skill whenever:
- Someone asks **which easing** to use, or describes a desired feel in plain language (e.g. "snappy", "springy", "bouncy", "smooth", "natural").
- A named easing appears in the conversation and you need its **cubic-bezier value or JS body**.
- Code is being written with an `ease:` property or `transition-timing-function` and **no value has been decided yet** — pick one here first.
- Someone asks to **convert** between a JS function and its CSS equivalent.
- Any word in the message is: `ease`, `easing`, `cubic-bezier`, `overshoot`, `elastic`, `bounce`, `linear`, `acceleration`, `deceleration`, `curve`, `feel`.

Do **not** use this as the primary skill when the task is writing tween/timeline logic → `gsap/`, motion recipes → `motion/`, or full pipeline → `figma-to-animation/`. But still consult it inside those tasks whenever an ease value needs to be chosen.

## How to read this

- **easeIn** — slow start, fast end. Good for exits (something leaving the screen).
- **easeOut** — fast start, slow end. Good for entrances (something arriving).
- **easeInOut** — slow at both ends, fast in the middle. Good for between-state transitions.

Each family has a different *shape*:

| Family | Character |
|--------|-----------|
| Sine | Gentlest curve — barely noticeable acceleration |
| Quad | Mild — default "polished" feel |
| Cubic | Slightly more pronounced than Quad |
| Quart | Snappy — good for UI cards/panels |
| Quint | More snappy than Quart |
| Expo | Very snappy start or end — dramatic |
| Circ | Similar to Expo, based on a circle arc |
| Back | Overshoots slightly — feels springy/playful |
| Elastic | Oscillates like a rubber band — use sparingly |
| Bounce | Bounces at the endpoint — playful/cartoonish |

---

## Pick by use-case

Use this table when you know what something should *feel* like but not which easing to reach for.

| You want… | Best pick | Why |
|-----------|-----------|-----|
| A card / panel sliding in | `easeOutQuart` | Arrives fast, settles cleanly — feels responsive |
| A card / panel sliding out | `easeInQuart` | Leaves quickly, no hesitation |
| A modal or drawer opening | `easeOutCubic` | Smooth arrival, not overdramatic |
| A tooltip or small popover | `easeOutQuad` | Gentle, unobtrusive |
| A hero element entering the viewport | `easeOutExpo` | Dramatic fast-start, long deceleration tail |
| Text / stagger entrance | `easeOutCubic` or `easeOutQuart` | Polished, readable |
| Something snapping into place | `easeOutBack` | Slight overshoot gives it physicality |
| A button press / click feedback | `easeInOutQuad` | Symmetrical, subtle |
| A loading spinner or loop | `easeInOutSine` | Smooth acceleration both ways, feels organic |
| Scrolling / parallax | `easeInOutCubic` | Comfortable, no jarring edges |
| A number counter | `easeOutExpo` | Rushes early, ticks slowly at the end — feels satisfying |
| A progress bar | `easeInOutQuad` | Natural, no drama |
| A logo or brand reveal | `easeOutExpo` or `easeOutBack` | Premium feel with a confident landing |
| Something being dismissed / closing | `easeInCubic` | Accelerates away — feels intentional |
| A playful pop / scale-up | `easeOutBack` | Tiny overshoot reads as "alive" |
| A very playful bounce (game-like) | `easeOutBounce` | Literal bounce — cartoonish, use sparingly |
| A rubber-band / spring effect | `easeOutElastic` | Oscillates past the end — very playful, use sparingly |
| Smooth scene transition (fade, crossfade) | `easeInOutSine` | Invisible curve — viewer never notices |
| A marquee / continuous scroll | `linear` | Constant speed, no rhythm disruption |
| Organic / breathing motion | `easeInOutSine` | Mirrors natural breath cycle |
| Cinematic camera move | `easeInOutCubic` or `easeInOutQuart` | Smooth ramp up and down |
| UI element following cursor | `easeOutQuad` | Responsive but not jittery |

### Direction rule of thumb
- **Entrance** (something arriving) → always **easeOut** — fast start, soft landing.
- **Exit** (something leaving) → always **easeIn** — slow start, accelerates away.
- **State change** (A → B, staying on screen) → **easeInOut** — smooth on both ends.

### Intensity guide
When in doubt, pick **Cubic** or **Quart** for everyday UI. Step up to **Expo** for hero moments. Reserve **Back**, **Elastic**, **Bounce** for intentionally playful interactions.

---

## Reference

Load `references/functions.md` for the complete JS functions + CSS values.

### Quick cheat-sheet (CSS cubic-bezier)

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

### GSAP ease names

GSAP accepts these as string shorthand (no import needed):
```
"power1.in"   ≈ easeInQuad
"power1.out"  ≈ easeOutQuad
"power1.inOut"≈ easeInOutQuad
"power2"      ≈ Cubic family
"power3"      ≈ Quart family
"power4"      ≈ Quint family
"expo"        ≈ Expo family
"circ"        ≈ Circ family
"back"        ≈ Back family   (overshoot ~1.7)
"elastic"     ≈ Elastic family
"bounce"      ≈ Bounce family
"sine"        ≈ Sine family
```

For Remotion / CSS animations, use the cubic-bezier values above directly.

## Entry Point

For the full JS function bodies read `references/functions.md`.

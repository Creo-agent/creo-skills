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

- Chooses the loop shape (yoyo / restart / continuous / **forward-reset**) — yoyo for clean
  reveals; forward-reset when a distinct end-screen must NOT play in reverse.
- Builds one GSAP timeline (`repeat: -1`, `yoyo`/`repeatDelay`, or a forward timeline whose
  end state is engineered to equal its start).
- Adds ramping-up stagger, collapse-to-a-point (and its inverse, **emerge-from-a-point**),
  directional stagger lead, and layer cross-fades.
- Uses a fixed export-ready stage + JS scaler when destined for video/social.
- Verifies deterministically by seeking timeline states and sampling `.time()`.

## Entry Point

Load **PROMPT.md** for the loop shapes, the core GSAP structure, the motion patterns,
and the deterministic verification recipe.

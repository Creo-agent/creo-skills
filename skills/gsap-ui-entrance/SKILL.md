---
name: gsap-ui-entrance
description: >-
  Add a staggered, orchestrated UI entrance animation to a DOM card that lives inside a GSAP loop. Go-to skill whenever the user wants product UI to "come alive" as it enters — "the box should scale in first, then the text, then the rows", "animate the inner elements when the card scales up", "orchestrated entrance with overlaps", "all objects working as one unified timeline". On a yoyo loop it uses the reverse trick (author the entrance once on the forward pass as a leave); on a forward-reset loop it authors explicit enter/exit tweens with independent stagger direction. Pairs naturally with figma-1to1-card (build first, then animate). Do NOT use for: building the card's visual (figma-1to1-card), building the outer loop itself (loop-animator), or simple single-element fades with no orchestration.
---

# GSAP UI Entrance (orchestrated multi-beat)

Add an orchestrated multi-beat entrance to a DOM card inside a GSAP loop — box scales in,
then text, then rows, as one unified timeline. On a **yoyo** loop the key trick is to author
the entrance on the forward pass *as a leave* (visible → hidden); the reversal plays it back
as hidden → visible for free. On a **forward-reset** loop you instead author explicit enter
and exit tweens with independent stagger direction.

## When This Skill Activates

- "The box should scale in first, then the title, then the rows cascade"
- "Animate the card's inner elements as it scales up — orchestrated, with overlaps"
- "All the objects should feel like one unified entrance timeline"
- "Make this product-UI card come alive as it enters the loop"

Keywords: `entrance`, `orchestrated`, `stagger`, `come alive`, `box then text then rows`,
`unified timeline`, `scale in`, `cascade`.

## What This Skill Does

- On a yoyo loop: authors the entrance as a **forward leave** so the reverse replays it as an
  entrance — order is set by forward position (latest forward ⇒ first to enter).
- On a forward-reset loop: authors explicit **enter** and **exit** tweens, setting each
  stagger's `from` independently (e.g. enter `from:'start'`, exit `from:'end'`).
- Excludes the orchestrated card from any generic collapse so it assembles in place.
- Keeps all beats as `BASE + offset` constants and one easing family, and verifies by
  scrubbing timeline states.

## Entry Point

Load **PROMPT.md** for the core principle, the beat map, the leave/enter tweens, the
stagger-direction rules (yoyo vs forward-reset), the tuning table, and verification.

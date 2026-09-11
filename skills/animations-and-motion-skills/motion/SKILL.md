---
name: motion
description: |
  WHAT: Add GSAP motion to a web animation — the "make it move, on a seamless loop" stage. Four recipes: LOOPS (seamless yoyo / continuous / forward-reset, no jump cut), ENTRANCE (orchestrated stagger: box → text → rows as one timeline), MARQUEE/carousel (endless horizontal scroll, per-row parallax), WORD-TICKER (slot-machine vertical roll + width morph on a cycling headline word).
  TRIGGERS: "loop / auto-play / run continuously", "reveal then reset with no hard cut", "cards/text come alive as they enter", "a row scrolling sideways like a ticker / marquee", "a word that cycles: leads → deals → sales", adding GSAP motion to an already-built static frame.
  SUB-SKILL: figma-to-animation orchestrator routes here for its animate stage. Usable standalone when you specifically need GSAP motion on an already-built frame.
  NOT FOR: building the static visual first → use frame-building/. Native-CSS section motion in DS stories → use ds-section-animations/. Rendering to GIF/MP4 → use export-as-gif/. Resizing → use resize-animation/. Full pipeline → use figma-to-animation/.
---

# Motion (GSAP loops, entrances, marquees, tickers)

The stage that makes a built frame move — and loop **seamlessly** (the recurring pitfall is a jump cut
at the loop boundary; these recipes avoid it). Build the static frame first with
[`../frame-building/`](../frame-building/); this skill is about the *motion*. For GSAP API specifics see
[`../gsap/`](../gsap/); for porting motion to a deterministic video render see
[`../export-as-gif/`](../export-as-gif/) + [`../remotion-best-practices/`](../remotion-best-practices/).

## Pick the recipe

| You want… | Load |
|---|---|
| A hands-free seamless loop (reveal → hold → reset, breathing, cross-fades) | [`references/loops.md`](references/loops.md) |
| Inner UI to enter in orchestrated beats (box, then text, then rows) inside a loop | [`references/ui-entrance.md`](references/ui-entrance.md) |
| A row (pills/logos/chips/cards) scrolling sideways forever, optionally multi-row parallax | [`references/marquee.md`](references/marquee.md) |
| A headline word that swaps on a timer (vertical roll + width morph) | [`references/word-ticker.md`](references/word-ticker.md) |

They compose: an **entrance** or **marquee** or **word-ticker** typically lives *inside* a **loop** —
build the outer loop with `references/loops.md` and slot the others in as layers.

## Cross-cutting rules (see ../figma-to-animation/references/knowledge.md for the why)
- **Prove seamless loops.** Snap every oscillator's period to an integer divisor of the loop length
  `L`; prove value AND velocity match at the boundary; render boundary stills. Never assert "it loops."
- **Element reuse.** A shared element that spans states is one continuous DOM node — duplicates cause
  flashing/misalignment.
- **Named-constant timing + one easing family.** Keep beats as `BASE + offset` constants; smooth
  `sine.inOut`/`power2.inOut`, never linear/abrupt. Motion roles/heuristics:
  [`../figma-to-animation/references/animation-knowledge.md`](../figma-to-animation/references/animation-knowledge.md).
- **Measure widths in the right coordinate space** (the word-ticker's #1 bug) — see
  `references/word-ticker.md`.

## Entry point
Load the recipe doc for what you're building (above). For a full Figma→animation job, start from
[`../figma-to-animation/`](../figma-to-animation/) — it orchestrates this skill and the rest.

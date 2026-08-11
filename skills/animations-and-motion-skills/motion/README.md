# motion

GSAP motion creation — the animate stage of the pipeline. Consolidates four former skills into one, as
recipe reference docs:

| Recipe | Reference doc | Was skill |
|---|---|---|
| Seamless auto-playing loops | `references/loops.md` | `loop-animator` |
| Orchestrated staggered UI entrance | `references/ui-entrance.md` | `gsap-ui-entrance` |
| Endless horizontal marquee/carousel | `references/marquee.md` | `marquee-carousel` |
| Slot-machine word ticker | `references/word-ticker.md` | `word-ticker` |

- **Entry:** `SKILL.md` (router) → `PROMPT.md` (recipe routing + non-negotiables) → the recipe doc.
- **Part of** the [`figma-to-animation`](../figma-to-animation/) pipeline (animate stage); usable
  standalone to add motion to a built frame.
- **Builds on** [`../frame-building/`](../frame-building/) (static frame first) and
  [`../gsap/`](../gsap/) (library API); **hands off to** [`../export-as-gif/`](../export-as-gif/).

> Consolidated from `loop-animator` + `gsap-ui-entrance` + `marquee-carousel` + `word-ticker` by Elior
> Siegelwachs, 2026-07-14. The former skill names are retired; references now point at `motion`.

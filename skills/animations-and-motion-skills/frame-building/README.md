# frame-building

Static Figma → pixel-accurate HTML/CSS — the build stage of the animation pipeline. Consolidates three
former skills into one, as mode reference docs:

| Mode | Reference doc | Was skill |
|---|---|---|
| Fresh fixed-stage scaffold | `references/scaffold.md` | `animation-scaffold` |
| Whole-frame layout / scatter | `references/layout.md` (+ `references/figma-notes.md`) | `precise-figma-composition` |
| Single component 1:1 (card) | `references/card.md` | `figma-1to1-card` |

- **Entry:** `SKILL.md` (router) → `PROMPT.md` (mode routing + shared conventions) → the mode doc.
- **Part of** the [`figma-to-animation`](../figma-to-animation/) pipeline (build stage); usable
  standalone for a static Figma→HTML job.
- **Hands off to** [`../motion/`](../motion/) (animate) and [`../export-as-gif/`](../export-as-gif/)
  (render).

> Consolidated from `animation-scaffold` + `precise-figma-composition` + `figma-1to1-card` by Elior
> Siegelwachs, 2026-07-14. The former skill names are retired; references now point at `frame-building`.

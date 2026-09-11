---
name: figma-to-animation-product-animations
description: |
  WHAT: Master orchestrator for product-UI animation demos. Turns a Figma product design into a fully animated HTML/CSS/JS prototype with a realistic animated mouse cursor. Parallel pipeline to figma-to-animation, purpose-built for product/UI-heavy demos where pixel accuracy against a design system is non-negotiable.
  TRIGGERS: "animate this product design", "make a product demo with cursor", "turn this UI screen into an animated prototype", "animate this monday.com UI with cursor movement", any Figma product UI → animated demo request.
  PIPELINE (strict order): product-animation-planning → product-design-recreation → product-design-QA (≥95, Workflow loop) → product-animation + cursor-animation (synchronized, shared GSAP timeline) → product-animation-QA (Workflow loop) → export (separate skill).
  ROUTES TO: product-animation-planning, product-design-recreation, product-design-qa, product-animation, cursor-animation, product-animation-qa (all are nested subskills). Shares env with figma-to-animation: frame-building, motion, gsap, remotion-best-practices, export-as-gif.
  NOT FOR: marketing banner animations without cursor → use figma-to-animation. Static Figma-to-HTML only → use frame-building. GSAP motion only → use motion. Export only → use export-as-gif.
---

# Figma to Animation — Product Animations (Orchestration)

## Overview

This is the master skill for the product animation pipeline. It does not do design, animation, or QA work itself — it coordinates the six task subskills that do, in the correct order, passing the right artifacts between them and re-running steps when QA gates fail. The executable run procedure is in `PROMPT.md`; read `references/knowledge.md` and `references/timeline-clock.md` once before a run.

This skill exists specifically for **product** animations, where visual accuracy against an existing design system is non-negotiable (this is a real product, not a reinterpretation) and interactions need to look natural and human, including a realistic animated cursor.

## Subskills Coordinated

1. `product-animation-planning` — analyzes the design, produces a timestamped timeline plan.
2. `product-design-recreation` — builds pixel-accurate HTML/CSS from Figma.
3. `product-design-qa` — validates ≥95% visual accuracy against Figma.
4. `product-animation` — implements UI motion/transitions per the timeline.
5. `cursor-animation` — implements realistic cursor movement/clicks per the timeline.
6. `product-animation-qa` — validates the final animated result against the timeline plan.

(Export uses an existing, separate skill — not part of this pipeline's scope.)

## Engine Registry (reference these siblings — don't reinvent)

Like `../figma-to-animation/`, this pipeline does technique by **referencing existing engine skills**
at `../<name>/` (single source of truth), never by copying them. The task subskills route to:

| Stage | Engine skill | Provides |
|---|---|---|
| Design recreation + fixed stage | `../frame-building/` | Figma→code: `figmaValue × scale` extraction, `getBoundingClientRect().width === figmaWidth × scale` verification, two-layer DOM, the `.stage-scaler` fit + scale-inflation `getBCR`-vs-`offsetWidth` discipline, gradient-stroke / `preserveAspectRatio` traps |
| UI motion (pop-in / expand / cascade / sequential flows) | `../motion/` | beat maps, `power2.*` unified easing family, `autoAlpha`, `scaleY` box pop, stagger direction; forward-reset loops for flows that must not reverse |
| Cursor follow / easing / reduced-motion | `../gsap/` | `quickTo()`, timeline **position parameters** (`"<"`, `"<0.2"`, labels), `gsap.matchMedia()` for `prefers-reduced-motion` |
| Export | `../export-as-gif/` | Remotion render interface; reuses an existing `remotion/` project; Node ≥18 |
| Rendered visual critique | `design-critique` skill | systematic UI polish / alignment / hierarchy pass, feeding the QA rubric |

The deterministic gates themselves live in `workflows/` (`design-qa-loop.js`, `animation-qa-loop.js`)
and score against `references/rubric.md` (design) and `references/timing-rubric.md` (animation).

## Pipeline Sequence

```
1. product-animation-planning
        ↓
2. product-design-recreation
        ↓
3. product-design-qa ──(FAIL)──→ back to step 2
        │
      (PASS)
        ↓
4. product-animation  ⇄ synchronized, shared timeline ⇄  cursor-animation
   (run together / in parallel — both consume the SAME timeline plan
    and MUST use identical timestamps for any shared event)
        ↓
5. product-animation-qa ──(FAIL)──→ back to step 4 (one or both subskills)
        │
      (PASS)
        ↓
6. Export (existing skill, outside this pipeline)
```

## Orchestration Rules

- **Step order is strict for 1 → 2 → 3.** Do not begin design recreation before a timeline plan exists. Do not begin animation before design QA passes.
- **Step 4 is a synchronized pair, not two independent tasks.** `product-animation` and `cursor-animation` compile their tweens onto the **same shared GSAP master timeline** at shared labels (`references/timeline-clock.md`) — a cursor click and its UI state change sit on one label, so they fire on one clock. Sync is structural, not a matter of two skills agreeing on a number. Any event authored with a second time source (`setTimeout`, a second timeline, `animation-delay` off page load) is a bug, not a stylistic difference. This step runs via `workflows/animation-qa-loop.js`.
- **QA gates are hard stops.** If `product-design-qa` or `product-animation-qa` returns FAIL, do not proceed to the next step — loop back, fix, and re-run the QA skill before continuing.
- **Escalation after repeated failures.** If the same QA gate (`product-design-qa` or `product-animation-qa`) fails **three times in a row** on the same artifact, stop looping automatically. Summarize what's been tried, what's still failing, and ask the user for direction rather than continuing to retry silently.
- **Re-planning triggers a full re-run.** If the Figma source design changes materially after planning has started, re-run from `product-animation-planning`.
- **Keep artifacts between steps.** Each skill's output (timeline plan, HTML/CSS, manifest, QA reports, implementation logs) should be preserved and passed forward — later skills and QA steps depend on earlier artifacts, not just the final state.

## Shared Conventions (apply across all subskills)

- **Shared animation env.** This is a *parallel* pipeline to `figma-to-animation` that shares the
  `skills/animations-and-motion-skills/` group's reference layer — prefer these over re-deriving conventions:
  [`../figma-to-animation/references/setup.md`](../figma-to-animation/references/setup.md) (tools/
  prereqs — Node ≥18, Remotion, FFmpeg + doctor check),
  [`../figma-to-animation/references/animation-knowledge.md`](../figma-to-animation/references/animation-knowledge.md)
  (motion roles, timing/easing heuristics, a11y, monday brand motion), and
  [`../figma-to-animation/references/knowledge.md`](../figma-to-animation/references/knowledge.md)
  (measurement discipline, Figma fidelity). Library specifics: [`../gsap/`](../gsap/) and
  [`../remotion-best-practices/`](../remotion-best-practices/).
- **Shared clock / animation library.** Motion runs on a **single shared GSAP master timeline** — both `product-animation` and `cursor-animation` compile their tweens onto one `gsap.timeline()` at shared labels drawn from the planning table. This is the mechanism that makes cursor↔UI sync structural rather than reviewed; the full contract is in `references/timeline-clock.md`. GSAP is the default (house standard, CDN, no install, ports to Remotion for export). A project may override the library via an optional `animation-library.md` at the project root, but the shared-clock discipline (one timeline, labels from the plan, both skills on it — never a second timer) applies whatever the library.
- **Rendering viewport.** All steps that render or measure the HTML/CSS output (`product-design-recreation`, `product-design-qa`, `cursor-animation`, `product-animation-qa`) must render at the same fixed viewport size, documented at the top of the timeline plan (default: 1440×900 unless the Figma frame specifies otherwise). Coordinate extraction for the cursor is only valid if every step used this same viewport.
- **Multi-flow designs.** If a design requires more than one animated flow (e.g., two different user journeys through the same screen), `product-animation-planning` outputs one timeline file per flow, named `timeline-1.md`, `timeline-2.md`, etc., each with its own Flow Summary. Every downstream skill then runs once per timeline file, and outputs are kept in matching per-flow subfolders (e.g., `flow-1/`, `flow-2/`) so artifacts don't overwrite each other.
- **Output versioning.** Each full pipeline run writes to a timestamped output folder (e.g., `output/2026-07-14-1/`) rather than overwriting the previous run. This keeps prior QA-passed prototypes intact if a design is re-run later.
- **Export skill dependency.** Export is a separate, existing skill: [`../export-as-gif/`](../export-as-gif/) (Remotion — asks output spec first, reuses an existing `remotion/` project, needs Node ≥18). Before running step 6, confirm that sibling exists; if it can't be found, stop and ask the user rather than assuming its interface. Do not build a new export skill here. The `master` timeline ports to Remotion as `master.seek(frame / fps)` → `f(useCurrentFrame())`.

## When to Deviate From Full Orchestration

- If the user explicitly asks to run a single subskill in isolation (e.g., "just re-run the cursor animation"), do so directly without re-running the full pipeline — but flag if doing so risks breaking sync with a step that wasn't re-run.
- If the user already has a timeline plan or QA-passed static design from a prior session, skip directly to the relevant step rather than restarting from step 1.

## Inputs Required to Start

- Figma design (link, export, or screenshots) for the product UI to animate.
- Design system reference (spacing/color/typography/stroke tokens), if not already available to the design subskill.
- Selected UI animation library/tooling for implementation (connected separately by the user).

## Final Output

A finished, QA-validated animated HTML/CSS/JS product prototype — visually accurate to the source design and with UI motion and cursor movement synchronized to a single, coherent timeline — ready for the export step.

---
name: figma-to-animation
description: |
  WHAT: THE master orchestrator for any Figma→animation job. Turns a Figma frame or multi-frame storyboard into a polished HTML/CSS/JS + GSAP web animation, and on request exports it to MP4/GIF via Remotion. Does NOT do the work itself — sequences and gates sub-skills.
  TRIGGERS: "animate this Figma", "turn these frames into an animation", "build motion / transitions between these designs", "make a looping animation from this storyboard", "Figma → video / gif / mp4", any full Figma-to-animation pipeline request.
  PIPELINE: index → analyze → build each frame → static QA (Workflow loop, ≥95 score, per frame) → stitch → animate each frame → animation QA (Workflow loop, per frame) → connect flow → export → final validate.
  ROUTES TO: frame-building (static build stage), motion (GSAP animate stage), export-as-gif (render stage), extract-animation-from-web (reference a live site), resize-animation (reflow to new sizes).
  NOT FOR: static Figma-to-HTML with no motion → use frame-building. Capturing animation off a live website → use extract-animation-from-web. Resizing an existing animation → use resize-animation. Product-UI demo with animated cursor → use figma-to-animation-product-animations.
---

# Figma-to-Animation pipeline (master orchestrator)

You are the **controller**. You don't build or animate — you sequence the sub-skills, track
per-frame state, run the two QA loops as deterministic workflows, route fix-prompts (never
rebuilds), and enforce the cross-cutting rules. Read `references/knowledge.md` once at the start
of a run — it carries the hard-won *mechanical* lessons (measurement, seamless-loop math, Figma
fidelity) this pipeline depends on — and `references/animation-knowledge.md` once for the *semantic*
layer (motion roles, timing/easing heuristics, best-practices/a11y, monday brand motion). The scoring
rubric is `references/rubric.md`; each pipeline stage is documented in `pipeline/`.

**Prerequisites — check before a run.** The tools this pipeline needs (Node ≥18, Remotion, FFmpeg,
GSAP, optional numpy) and how to install/verify them live in `references/setup.md`. Run its doctor
check first: a missing or too-old tool (most often Node < 18) fails silently until the slow export
stage. Don't hardcode machine-specific paths — `setup.md` shows the portable way to select a Node ≥18.

## Pipeline (run in this order)

```
1  index          →  pipeline/01-index.md
2  analyze        →  pipeline/02-analyze.md          (vision-first → brief → per-frame prompts)
   ├─ asset-download / svg-extract  (conditional, parallel; pipeline/sub-asset-download.md, sub-svg-extract.md)
   └─ video-gen                     (conditional, per flagged image; pipeline/sub-video-gen.md)
── LOOP A ──  workflows/static-qa-loop.js   (per frame: 3 build ⇄ 4 QA until score ≥ 95; barrier: ALL frames pass)
5  stitch         →  pipeline/05-stitch.md            (mechanical concat of approved frames)
── LOOP B ──  workflows/animation-qa-loop.js (per frame: 6a animate ⇄ 6b QA until pass; barrier: ALL frames pass)
6c flow-connect   →  pipeline/06c-flow.md             (connect frames; verify transitions + loop restart + no dup elements)
7  export         →  pipeline/07-export.md            (format decision → Remotion → Export QA + retry)
8  final-validate →  pipeline/08-final-validation.md  (delivered vs Figma + intent; route drift back)
                     DELIVERED
```

## The two QA loops are Workflows, not agent guesswork

Invoke them with the Workflow tool by `scriptPath` (they live in this skill's `workflows/`).
They own the mechanical parts you must not eyeball:
- **Loop A — `workflows/static-qa-loop.js`**: per frame, build → static-QA(score) → while `score<95 && iters<MAX`: fix-prompt → rebuild → re-QA. Returns `[{idx, score, pass, buildPath, fixHistory[]}]`. **Do not run stitch (5) until every frame is ≥95.** Non-convergence after MAX → stop and surface to the user.
- **Loop B — `workflows/animation-qa-loop.js`**: per frame, animate → anim-QA(4 checks) → fix→re-animate until pass. Returns per-frame anim state + fix history. **Do not run flow-connect (6c) until every frame passes.**

Everything else (linear sequencing, gathering export prefs, routing a Final-Validation discrepancy back to the right stage) you do directly as the orchestrator.

## Sub-skill registry (engine skills the orchestrator routes to; each usable standalone for its task)

**Pipeline stages** (this skill's `pipeline/*.md`): `01-index`, `02-analyze`, `03-build-frame`,
`04-static-qa`, `05-stitch`, `06a-animate`, `06b-anim-qa`, `06c-flow`, `07-export`,
`08-final-validation`; sub-skills `sub-asset-download`, `sub-svg-extract`, `sub-video-gen`.

**Engine skills** — the real workhorses. They are **sibling skills in this same `animation/` group**
(one source of truth — this master references them, it does not copy them). Reference each at
`../<name>/` and load its `SKILL.md`→`PROMPT.md` as needed.
| Role | Engine skill(s) — siblings in `../` |
|---|---|
| Static frame build — scaffold · Figma layout · 1:1 card · asset/SVG download | [`../frame-building/`](../frame-building/) (+ external `figma:figma-design-to-code`) |
| Motion — seamless loops · UI entrance · marquee · word ticker | [`../motion/`](../motion/), [`../gsap/`](../gsap/) |
| Section motion (native APIs) | [`../ds-section-animations/`](../ds-section-animations/) |
| Reference motion off a live site | [`../extract-animation-from-web/`](../extract-animation-from-web/) |
| Reflow to new sizes/aspect | [`../resize-animation/`](../resize-animation/) |
| Export to MP4/GIF | [`../export-as-gif/`](../export-as-gif/), [`../remotion-best-practices/`](../remotion-best-practices/) |
| Rendered visual/design QA | `design-critique` (external plugin skill) |

**External skills** the pipeline may call opportunistically (not bundled; live outside):
`figma:figma-design-to-code`, `design-critique`, `figma-mcp-detector`, `figma-modify` /
`figma-resize` (edit the source in Figma).

**Asset extraction** — use [`figma-export-assets`](../../figma-export-assets/) (top-level skill)
for all Figma asset downloads: raster PNG/JPG at any scale (`sub-asset-download`) and true-vector
SVG via `SVG_STRING` (`sub-svg-extract`). It owns the full export primitive — Vector Quality Check,
`colorProfile: 'SRGB'`, `useAbsoluteBounds: true`, smart naming, and visual integrity verification —
so neither sub-skill needs to reinvent that logic. Load it by name: `figma-export-assets`.

## State the orchestrator tracks (first-class, per run)
```jsonc
run = {
  figmaSource, outputFormat, exportPrefs:{formats[],loop},   // 01 or surfaced at 07
  brief, transitionDeltas, sequenceClass, loopRestartLogic,  // from 02 → carried to 6a/6b/6c/8
                                                              // transitionDeltas = per-transition before→after element changes (what to animate)
  frames:[ { idx,id, prompt, assets:{raster[],svg[]}, videoReplacements[],
             build:{path,qaScore,qaPass,fixHistory[]},        // Loop A
             anim:{applied,qaPass,fixHistory[]} } ],          // Loop B
  stitchedDoc, connectedFlow, exports[], validation
}
```
Persist to `<project>/.f2a/run.json` so a long run survives context compaction.

## Cross-cutting rules (enforce these — see references/knowledge.md for the why)
- **Fix-prompt, not rebuild.** Every QA stage emits `element + property + current→expected`; route to the builder for a targeted fix. Preserve fix history so repeat failures are visible.
- **Per-frame gating.** No stitch until all frames ≥95; no flow-connect until all animations pass.
- **Element reuse, not duplication.** A logo/product/text block that spans frames is ONE continuous node. Checked in 6a and again in 6c.
- **Prove seamless loops.** Snap oscillator periods to integer divisors of the loop length; prove value AND velocity match at the boundary; render boundary stills. Never assert "it loops."
- **Measurement discipline.** On a scaled stage, divide `getBoundingClientRect` by the scaler factor only for elements inside the scaled subtree; `offsetWidth` is scale-invariant; magnitude-check px; prefer measuring at render time over hardcoding.
- **Vision-first analysis** in stage 2 (look before leaning on Figma MCP); **MCP-required** in 4 and 8.
- **Precision over approximation.** Never relax the ≥95 gate or Final-Validation intent-matching to escape a loop.

## Failure handling
- A per-frame loop that won't converge after MAX iterations → surface to the user; the fix-prompts aren't addressing the real issue.
- Export QA fails → retry/adjust the Remotion conversion before blaming upstream motion.
- Final Validation flags a mismatch → route the specific discrepancy to the responsible stage (composition→6c, static fidelity→4, timing→6a) — never restart the whole pipeline.

## Standalone use
Each `pipeline/*.md` and each engine skill is self-contained: a user can invoke just
`04-static-qa` on a built frame, just `06c-flow` on assembled animations, etc. The orchestrator
is the entry point for the *whole* Figma→animation job; the parts are the entry points for the
individual jobs.

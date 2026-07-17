# figma-to-animation — run procedure

You are the **orchestrator**. Sequence and gate the sub-skills; don't do their work yourself.
Read `references/knowledge.md` once before starting. Track per-run state (see the state model in
`SKILL.md`) and persist it to `<project>/.f2a/run.json` so a long run survives compaction.

## Steps

0. **Preflight** — confirm the tools in `references/setup.md` are present, especially **Node ≥18**
   (run its doctor check). Skipping this lets a long run proceed all the way to the export stage
   before dying on `EBADENGINE`. Don't hardcode a personal nvm path — use setup.md's portable Node
   selection.
1. **Index** — follow `pipeline/01-index.md`. Fix output format + motion baseline; capture export
   prefs now if known.
2. **Analyze** — follow `pipeline/02-analyze.md`. Vision-first; produce the general brief, the
   **before→after per-transition deltas**, per-frame prompts, sequence class + loop-restart logic.
3. **Assets (conditional, parallel)** — if a frame has rasters/vectors, run
   `pipeline/sub-asset-download.md` and `pipeline/sub-svg-extract.md`; run `pipeline/sub-video-gen.md`
   only for images explicitly flagged (provider stubbed — see `references/providers.md`).
4. **Loop A — static build ⇄ QA (deterministic).** Invoke the workflow:
   `Workflow({ scriptPath: "<this skill>/workflows/static-qa-loop.js", args: { skillDir, projectDir, frames, maxIters } })`.
   It builds each frame (`pipeline/03-build-frame.md`) and scores it against Figma with the ≥95
   rubric (`pipeline/04-static-qa.md` + `references/rubric.md`), looping targeted fixes per frame.
   **Do not proceed until `allPass` is true.** If it reports failures after MAX iters, stop and
   surface them to the user.
5. **Stitch** — follow `pipeline/05-stitch.md`. Concatenate the approved frames into one document.
6. **Loop B — animate ⇄ QA (deterministic).** Invoke:
   `Workflow({ scriptPath: "<this skill>/workflows/animation-qa-loop.js", args: { skillDir, projectDir, stitchedDocPath, brief, frames /* each with its delta */, maxIters } })`.
   It animates each frame (`pipeline/06a-animate.md`, using the engine siblings) and QAs it
   (`pipeline/06b-anim-qa.md`), looping fixes. **Do not proceed until `allPass` is true.**
7. **Flow-connect** — follow `pipeline/06c-flow.md`. Connect frames into one flow; verify
   transitions realize the deltas, the loop restart is seamless (value + velocity), and no
   duplicate/overlapping elements.
8. **Export** — follow `pipeline/07-export.md`. Gather format + looping; Remotion for video/GIF via
   the `../export-as-gif/` sibling; run Export QA; retry conversion on failure.
9. **Final validation** — follow `pipeline/08-final-validation.md`. Compare the delivered artifact
   vs the original Figma + intent; route any discrepancy back to the responsible stage. If clean →
   **DELIVERED**.

## Non-negotiables (enforce throughout)
- Fix-prompt, not rebuild. Per-frame gating (all frames pass before advancing). Element reuse (one
  continuous node across frames). Prove loops seamless. Measurement discipline. Never relax the ≥95
  gate or Final-Validation intent-matching.

## Engine skills
All motion/build/export engines are **sibling skills in `../`** (see the registry table in
`SKILL.md`) — reference them, don't copy. `gsap` and `remotion-best-practices` are vendored siblings
too, so the whole pipeline is self-contained in this group.

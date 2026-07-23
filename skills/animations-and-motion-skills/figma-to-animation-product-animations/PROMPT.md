# figma-to-animation-product-animations — run procedure

You are the **orchestrator**. Sequence and gate the sub-skills; don't do their work yourself.
Read `references/knowledge.md` and `references/timeline-clock.md` once before starting. Keep every
step's artifacts (timeline plan, static build, manifest, QA reports, the `master` timeline) in a
timestamped output folder (`output/<date>-N/`); later steps depend on earlier artifacts.

## Steps

0. **Preflight** — confirm the tools in `references/setup.md` (GSAP reachable, Figma MCP responding,
   a static server; Node ≥18 only if you'll export). Run its doctor check.

1. **Plan** — follow `product-animation-planning/skill.md`. Produce the timeline document(s): one
   `## Timeline` table per flow, each row carrying a stable **Label** (e.g. `click-row-3`) that
   becomes a GSAP label. Multi-flow → `timeline-1.md`, `timeline-2.md`, …, with per-flow output
   subfolders. Fix the viewport at the top of the plan.

2. **Loop 1 — recreate ⇄ design-QA (deterministic).** Invoke the workflow:
   `Workflow({ scriptPath: "<this skill>/workflows/design-qa-loop.js", args: { skillDir, projectDir, screens, maxIters } })`.
   It recreates each screen (`product-design-recreation`, via `../frame-building/`) and scores it
   against Figma with the ≥95 rubric (`product-design-qa` + `references/rubric.md`), looping
   targeted fixes per screen.
   **Do not proceed until `allPass` is true.** If it reports failures after MAX iters (default 4),
   stop and surface them to the user — do not relax the gate.

3. **Scaffold the shared clock** — create `timeline.js` exporting one `master = gsap.timeline({
   paused: true })` with a label per timeline-table row at its `Time (s)` (see
   `references/timeline-clock.md`). This is the single time source both motion skills compile onto.

4. **Loop 2 — animate + cursor ⇄ animation-QA (deterministic).** Invoke:
   `Workflow({ scriptPath: "<this skill>/workflows/animation-qa-loop.js", args: { skillDir, projectDir, flows, maxIters } })`.
   For each flow it authors **both** UI motion (`product-animation`) and cursor motion
   (`cursor-animation`) onto the shared `master` at shared labels, then QAs timing/sync by reading
   actual times off `master` (`product-animation-qa` + `references/timing-rubric.md`), looping
   targeted fixes. **Do not proceed until `allPass` is true.**

5. **Export (separate skill).** On pass, hand the QA-approved prototype to
   [`../export-as-gif/`](../export-as-gif/) (Remotion; asks output spec first; reuses an existing
   `remotion/` project; Node ≥18). The `master` timeline ports as `master.seek(frame / fps)` →
   `f(useCurrentFrame())`. Export is **not** built here — confirm the sibling exists, then forward.

## Gates & escalation
- The two `allPass` barriers are hard stops: no animation before design-QA passes; no export before
  animation-QA passes.
- If the same gate fails **three times in a row** on the same artifact, stop looping — summarize what
  was tried and what's still failing, and ask the user for direction.
- If the Figma source changes materially after planning, re-run from step 1.

## Non-negotiables (enforce throughout)
- **One shared clock.** All timeline-table motion lives on the single `master`; never a second timer
  (`setTimeout` / a second `gsap.timeline()` / `animation-delay` off page load). Cursor click and its
  UI reaction share one label.
- **Fix-prompt, not rebuild.** Every QA failure returns `element + property + current→expected`;
  route a targeted edit, preserve fix history.
- **Measurement discipline.** Extract cursor targets at the timeline viewport after fonts+images
  load; verify `offset==figma×scale`; never `scaleX(-1)` the cursor asset (chirality).
- **Never relax the ≥95 design gate or the timing/sync checks.**

## Engine skills
All build/motion/export engines are **sibling skills in `../`** (see the registry table in
`skill.md`) — reference them, don't copy: `../frame-building/`, `../gsap/`, `../motion/`,
`../export-as-gif/`, and the `design-critique` skill.

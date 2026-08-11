export const meta = {
  name: 'pa-animation-qa-loop',
  description: 'Per-flow animate+cursor ⇄ animation-QA loop until all timing/sync checks pass; barrier over all flows',
  phases: [
    { title: 'Animate' },
    { title: 'AnimQA' },
  ],
}

/* Loop 2 of the figma-to-animation-product-animations pipeline (the timing & sync gate).
   Adapts figma-to-animation/workflows/animation-qa-loop.js. Runs SEQUENTIALLY per flow because
   both UI motion and cursor motion are authored into the SAME shared master timeline in one
   document (parallel edits to one doc would collide).

   In this pipeline product-animation and cursor-animation are not two independent tasks — they both
   compile tweens onto ONE gsap master timeline at shared labels (references/timeline-clock.md). So a
   single Animate stage applies BOTH, and a single QA stage measures timing/sync off `master`. A
   returned fixPrompt can target either the UI tween or the cursor tween.

   args = {
     skillDir, projectDir,
     flows: [ { idx, id, docPath, timelinePath, viewport } ],  // docPath = the QA-passed static
                                                               // build for this flow; timelinePath =
                                                               // the planning timeline.md (labels).
     maxIters?                       // default 4
   }
   Returns { flows: [ { idx, pass, fixHistory[] } ], allPass, failed }; allPass gates export. */

const A = args || {}
const SKILL = A.skillDir
if (!SKILL) throw new Error('skillDir is required — pass the absolute path to the figma-to-animation-product-animations skill (see PROMPT.md step 4)')
const FLOWS = Array.isArray(A.flows) ? A.flows : []
const MAX = A.maxIters || 4

const ANIM_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['applied', 'notes'],
  properties: { applied: { type: 'boolean' }, notes: { type: 'string' } },
}
const ANIMQA_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['pass', 'fixPrompt', 'checks'],
  properties: {
    pass: { type: 'boolean', description: 'all checks true AND no hard-fail' },
    fixPrompt: { type: 'string', description: 'targeted fix for the UI or cursor tween; empty if pass' },
    checks: {
      type: 'object', additionalProperties: false,
      required: ['eventsComplete', 'timingAccurate', 'cursorUiSynced', 'easingFaithful', 'dependenciesOrdered', 'coherent'],
      properties: {
        eventsComplete: { type: 'boolean' },
        timingAccurate: { type: 'boolean', description: 'each startTime within ±50ms of plan' },
        cursorUiSynced: { type: 'boolean', description: 'coincident cursor/UI tweens share a label, 0ms offset' },
        easingFaithful: { type: 'boolean' },
        dependenciesOrdered: { type: 'boolean' },
        coherent: { type: 'boolean' },
      },
    },
  },
}

const animPrompt = (f, fix) =>
  `You are the combined product-animation + cursor-animation stage of the figma-to-animation-product-animations pipeline.\n` +
  `Read ${SKILL}/product-animation/skill.md, ${SKILL}/cursor-animation/skill.md, ${SKILL}/references/timeline-clock.md and ${SKILL}/references/knowledge.md first.\n` +
  `Flow idx=${f.idx} (id=${f.id}). QA-passed static build: ${f.docPath}. Timeline plan: ${f.timelinePath}. Viewport: ${f.viewport || '(from the plan)'}.\n\n` +
  `Author ALL motion for this flow onto ONE shared gsap master timeline (timeline.js, master = gsap.timeline({paused:true})). ` +
  `Add a label per timeline-table row at its Time (s). Add every UI tween AND every cursor tween to THIS master AT ITS LABEL — never a setTimeout, never a second timeline, never CSS animation-delay off page load. ` +
  `A cursor click press and its UI state-change tween MUST share the same label (0ms offset by construction). ` +
  `Extract cursor targets from the rendered build after fonts+images load; move with power2.inOut (no teleports); click press = scale ~0.88 over ~0.05s yoyo; never scaleX(-1) the cursor asset (chirality). ` +
  `Route pop-in/expand/cascade and sequential-flow loops to motion patterns; use gsap easing families / position parameters.\n` +
  (fix ? `\nApply this animation-QA fix as a TARGETED edit (to the UI tween or the cursor tween as named), not a rebuild:\n${fix}\n` : '') +
  `Write the motion into ${f.docPath}. Return {applied, notes}.`

const qaPrompt = (f) =>
  `You are the product-animation-qa stage of the figma-to-animation-product-animations pipeline.\n` +
  `Read ${SKILL}/product-animation-qa/skill.md, ${SKILL}/references/timing-rubric.md and ${SKILL}/references/timeline-clock.md first.\n` +
  `Validate the animated flow in ${f.docPath} against the timeline plan ${f.timelinePath}. Obtain ACTUAL times off the shared master (master.labels, each tween's startTime()/duration()/vars.ease) — do NOT trust any written log. Seek master to each coincident label and screenshot to confirm cursor and UI states line up.\n` +
  `The six checks: (1) eventsComplete — every plan row has exactly one tween, no extras; (2) timingAccurate — each startTime within ±50ms of plan; (3) cursorUiSynced — coincident cursor/UI tweens share a label at 0ms offset; (4) easingFaithful — ease matches plan intent; (5) dependenciesOrdered — Depends-On events start at/after prerequisite ends; (6) coherent — scrubs as one natural interaction. Hard-fail on any second time source (grep for setTimeout / a second timeline(), or animation-delay off page load), a teleporting cursor, or a nonzero cursor↔UI offset.\n` +
  `Return {pass (all six true AND no hard-fail), fixPrompt (targeted, name the tween + observed vs planned + labelled fix; empty if pass), checks}.`

// Sequential per-flow loop (shared master doc → no parallel edits)
const out = []
for (const f of FLOWS) {
  phase('Animate')
  await agent(animPrompt(f, null), { label: `animate:f${f.idx}`, phase: 'Animate', schema: ANIM_SCHEMA })
  phase('AnimQA')
  let qa = await agent(qaPrompt(f), { label: `animqa:f${f.idx}#0`, phase: 'AnimQA', schema: ANIMQA_SCHEMA })
  const fixHistory = []
  let iters = 0
  while (qa && !qa.pass && iters < MAX) {
    fixHistory.push({ iter: iters, fixPrompt: qa.fixPrompt, checks: qa.checks })
    await agent(animPrompt(f, qa.fixPrompt), { label: `animfix:f${f.idx}#${iters + 1}`, phase: 'Animate', schema: ANIM_SCHEMA })
    qa = await agent(qaPrompt(f), { label: `animqa:f${f.idx}#${iters + 1}`, phase: 'AnimQA', schema: ANIMQA_SCHEMA })
    iters++
  }
  out.push({ idx: f.idx, pass: !!(qa && qa.pass), fixHistory })
}

const failed = out.filter((r) => !r.pass)
if (failed.length) {
  log(`⚠ ${failed.length}/${out.length} flows did NOT pass after ${MAX} iters: ${failed.map((r) => `f${r.idx}`).join(', ')} — surface to user, do NOT export.`)
} else {
  log(`✓ all ${out.length} flows passed timing/sync — cleared for export (../export-as-gif)`)
}
return { flows: out, allPass: failed.length === 0, failed }

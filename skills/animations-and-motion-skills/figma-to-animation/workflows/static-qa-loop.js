export const meta = {
  name: 'f2a-static-qa-loop',
  description: 'Per-frame build ⇄ static-QA loop until score ≥ 95; barrier — reports pass state for every frame',
  phases: [
    { title: 'Build' },
    { title: 'StaticQA' },
  ],
}

/* Loop A of the figma-to-animation pipeline.
   args = {
     skillDir,                       // abs path to the figma-to-animation skill
     projectDir,                     // abs path to the run's working dir (holds .f2a/)
     frames: [ { idx, id, prompt, figmaRef, assetsDir, buildPath } ],
     maxIters?                       // default 4
   }
   Returns [ { idx, score, pass, buildPath, fixHistory[] } ] and refuses to green-light
   the batch unless EVERY frame is pass=true (the orchestrator must not stitch otherwise). */

const A = args || {}
const SKILL = A.skillDir
if (!SKILL) throw new Error('skillDir is required — pass the absolute path to the figma-to-animation skill (see PROMPT.md step 4)')
const FRAMES = Array.isArray(A.frames) ? A.frames : []
const MAX = A.maxIters || 4

const BUILD_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['buildPath', 'notes'],
  properties: { buildPath: { type: 'string' }, notes: { type: 'string' } },
}
const QA_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['score', 'pass', 'fixPrompt'],
  properties: {
    score: { type: 'number' },
    pass: { type: 'boolean' },
    fixPrompt: { type: 'string', description: 'element+property+current→expected; empty if pass' },
    dimensionScores: { type: 'object', additionalProperties: true },
  },
}

const buildPrompt = (f, fix) =>
  `You are stage 03-build-frame of the figma-to-animation pipeline.\n` +
  `Read ${SKILL}/pipeline/03-build-frame.md and ${SKILL}/references/knowledge.md first.\n` +
  `Frame idx=${f.idx} (id=${f.id}). Figma source: ${f.figmaRef}. Local assets: ${f.assetsDir}.\n` +
  `Per-frame prompt:\n${f.prompt}\n\n` +
  (fix
    ? `A static-QA fix-prompt was returned — apply it as a TARGETED edit to the EXISTING build at ${f.buildPath}. Do NOT rebuild from scratch. Fix:\n${fix}\n`
    : `Build the frame as STATIC HTML/CSS (no animation). Use the downloaded assets/SVGs as-is; do not re-derive them.\n`) +
  `Write the build to ${f.buildPath}. Use frame-building techniques and the measurement discipline in knowledge.md. Return {buildPath, notes}.`

const qaPrompt = (f) =>
  `You are stage 04-static-qa of the figma-to-animation pipeline.\n` +
  `Read ${SKILL}/pipeline/04-static-qa.md, ${SKILL}/references/rubric.md, ${SKILL}/references/knowledge.md first.\n` +
  `Score the build at ${f.buildPath} against Figma frame ${f.figmaRef} using the weighted rubric: Figma MCP (get_metadata / get_variable_defs / get_design_context) for structured data, a screenshot overlay (get_screenshot vs the built frame), and the design-critique method. Apply the hard-fail overrides.\n` +
  `Return {score (0-100), pass (score>=95 AND no hard-fail), fixPrompt (element+property+current→expected, empty if pass), dimensionScores}.`

phase('Build')
const results = await parallel(FRAMES.map((f) => async () => {
  const fixHistory = []
  // initial build
  await agent(buildPrompt(f, null), { label: `build:f${f.idx}`, phase: 'Build', schema: BUILD_SCHEMA })
  // build ⇄ QA loop
  let qa = await agent(qaPrompt(f), { label: `qa:f${f.idx}#0`, phase: 'StaticQA', schema: QA_SCHEMA })
  let iters = 0
  while (qa && !qa.pass && iters < MAX) {
    fixHistory.push({ iter: iters, score: qa.score, fixPrompt: qa.fixPrompt })
    await agent(buildPrompt(f, qa.fixPrompt), { label: `fix:f${f.idx}#${iters + 1}`, phase: 'Build', schema: BUILD_SCHEMA })
    qa = await agent(qaPrompt(f), { label: `qa:f${f.idx}#${iters + 1}`, phase: 'StaticQA', schema: QA_SCHEMA })
    iters++
  }
  return { idx: f.idx, score: qa ? qa.score : 0, pass: !!(qa && qa.pass), buildPath: f.buildPath, fixHistory }
}))

const clean = results.filter(Boolean)
const failed = clean.filter((r) => !r.pass)
if (failed.length) {
  log(`⚠ ${failed.length}/${clean.length} frames did NOT reach 95 after ${MAX} iters: ${failed.map((r) => `f${r.idx}(${r.score})`).join(', ')} — surface to user, do NOT stitch.`)
} else {
  log(`✓ all ${clean.length} frames ≥95 — cleared for stitching`)
}
return { frames: clean, allPass: failed.length === 0, failed }

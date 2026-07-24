export const meta = {
  name: 'pa-design-qa-loop',
  description: 'Per-screen recreate ⇄ design-QA loop until score ≥ 95; barrier — reports pass state for every screen',
  phases: [
    { title: 'Recreate' },
    { title: 'DesignQA' },
  ],
}

/* Loop 1 of the figma-to-animation-product-animations pipeline (the design gate).
   Adapts figma-to-animation/workflows/static-qa-loop.js for product UIs.
   args = {
     skillDir,                       // abs path to the figma-to-animation-product-animations skill
     projectDir,                     // abs path to the run's working dir (holds output/)
     screens: [ { idx, id, figmaRef, viewport, timelinePath, buildPath, assetsDir } ],
                                     // one entry per screen/flow being recreated; timelinePath
                                     // points at the planning timeline.md so the build knows which
                                     // elements need data-anim-id hooks.
     maxIters?                       // default 4
   }
   Returns { screens: [ { idx, score, pass, buildPath, fixHistory[] } ], allPass, failed }
   and refuses to green-light the batch unless EVERY screen is pass=true (the orchestrator must not
   start animation otherwise — animation has nothing accurate to attach to). */

const A = args || {}
const SKILL = A.skillDir
if (!SKILL) throw new Error('skillDir is required — pass the absolute path to the figma-to-animation-product-animations skill (see PROMPT.md step 2)')
const SCREENS = Array.isArray(A.screens) ? A.screens : []
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
    score: { type: 'number', description: '0-100 weighted rubric total' },
    pass: { type: 'boolean', description: 'score>=95 AND no hard-fail override' },
    fixPrompt: { type: 'string', description: 'element+property+current→expected; empty if pass' },
    dimensionScores: { type: 'object', additionalProperties: true },
  },
}

const buildPrompt = (s, fix) =>
  `You are the product-design-recreation stage of the figma-to-animation-product-animations pipeline.\n` +
  `Read ${SKILL}/product-design-recreation/skill.md and ${SKILL}/references/knowledge.md first.\n` +
  `Screen idx=${s.idx} (id=${s.id}). Figma source: ${s.figmaRef}. Viewport: ${s.viewport || 'per timeline plan'}. ` +
  `Timeline plan (for the list of interactive elements that need stable data-anim-id hooks): ${s.timelinePath}. ` +
  `Local assets: ${s.assetsDir || '(none downloaded)'}.\n\n` +
  (fix
    ? `A design-QA fix-prompt was returned — apply it as a TARGETED edit to the EXISTING build at ${s.buildPath}. Do NOT rebuild from scratch. Fix:\n${fix}\n`
    : `Recreate the screen as pixel-accurate STATIC HTML/CSS (no animation, no motion). Build at the timeline viewport. Use frame-building techniques (build at natural size + one outer transform:scale(N); node geometry = figmaValue × scale) on its fixed stage-scaler. Give every timeline-interactive element a stable data-anim-id. Extract tokens from Figma — do not estimate.\n`) +
  `Write the build to ${s.buildPath}. Return {buildPath, notes}.`

const qaPrompt = (s) =>
  `You are the product-design-qa stage of the figma-to-animation-product-animations pipeline.\n` +
  `Read ${SKILL}/product-design-qa/skill.md, ${SKILL}/references/rubric.md, and ${SKILL}/references/knowledge.md first.\n` +
  `Score the build at ${s.buildPath} against Figma frame ${s.figmaRef} at viewport ${s.viewport || '(from the timeline plan)'} using the weighted rubric: Figma MCP (get_metadata / get_variable_defs / get_design_context) for structured data, offset==figma×scale measurement, a get_screenshot overlay, and the design-critique method. Apply the hard-fail overrides (missing/extra element, >16px misposition, wrong prominent color, broken asset, or a MISSING data-anim-id hook a timeline event needs).\n` +
  `Return {score (0-100), pass (score>=95 AND no hard-fail), fixPrompt (element+property+current→expected, empty if pass), dimensionScores}.`

phase('Recreate')
const results = await parallel(SCREENS.map((s) => async () => {
  const fixHistory = []
  // initial recreation
  await agent(buildPrompt(s, null), { label: `recreate:s${s.idx}`, phase: 'Recreate', schema: BUILD_SCHEMA })
  // recreate ⇄ QA loop
  let qa = await agent(qaPrompt(s), { label: `qa:s${s.idx}#0`, phase: 'DesignQA', schema: QA_SCHEMA })
  let iters = 0
  while (qa && !qa.pass && iters < MAX) {
    fixHistory.push({ iter: iters, score: qa.score, fixPrompt: qa.fixPrompt })
    await agent(buildPrompt(s, qa.fixPrompt), { label: `fix:s${s.idx}#${iters + 1}`, phase: 'Recreate', schema: BUILD_SCHEMA })
    qa = await agent(qaPrompt(s), { label: `qa:s${s.idx}#${iters + 1}`, phase: 'DesignQA', schema: QA_SCHEMA })
    iters++
  }
  return { idx: s.idx, score: qa ? qa.score : 0, pass: !!(qa && qa.pass), buildPath: s.buildPath, fixHistory }
}))

const clean = results.filter(Boolean)
const failed = clean.filter((r) => !r.pass)
if (failed.length) {
  log(`⚠ ${failed.length}/${clean.length} screens did NOT reach 95 after ${MAX} iters: ${failed.map((r) => `s${r.idx}(${r.score})`).join(', ')} — surface to user, do NOT start animation.`)
} else {
  log(`✓ all ${clean.length} screens ≥95 — cleared for animation + cursor`)
}
return { screens: clean, allPass: failed.length === 0, failed }

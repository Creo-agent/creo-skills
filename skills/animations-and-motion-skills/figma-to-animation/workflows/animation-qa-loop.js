export const meta = {
  name: 'f2a-animation-qa-loop',
  description: 'Per-frame animate ⇄ animation-QA loop until passing; sequential (shared stitched doc); barrier over all frames',
  phases: [
    { title: 'Animate' },
    { title: 'AnimQA' },
  ],
}

/* Loop B of the figma-to-animation pipeline. Runs SEQUENTIALLY per frame because every frame's
   motion is authored into the single shared stitched document (parallel edits would collide).
   args = {
     skillDir, projectDir,
     stitchedDocPath,                // the one HTML/CSS doc from stage 05
     brief,                          // general animation brief (from stage 02)
     frames: [ { idx, id, prompt, delta } ],   // delta = before→after transition change list (02)
     maxIters?                       // default 4
   }
   Returns per-frame { idx, pass, fixHistory[] }; allPass gates stage 06c. */

const A = args || {}
const SKILL = A.skillDir
if (!SKILL) throw new Error('skillDir is required — pass the absolute path to the figma-to-animation skill (see PROMPT.md step 6)')
const DOC = A.stitchedDocPath
const BRIEF = A.brief || '(no brief provided)'
const FRAMES = Array.isArray(A.frames) ? A.frames : []
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
    pass: { type: 'boolean' },
    fixPrompt: { type: 'string', description: 'targeted fix for 06a; empty if pass' },
    checks: {
      type: 'object', additionalProperties: false,
      required: ['matchesIntent', 'easingSmooth', 'timingReasonable', 'nothingBroken'],
      properties: {
        matchesIntent: { type: 'boolean' }, easingSmooth: { type: 'boolean' },
        timingReasonable: { type: 'boolean' }, nothingBroken: { type: 'boolean' },
      },
    },
  },
}

const animPrompt = (f, fix) =>
  `You are stage 06a-animate of the figma-to-animation pipeline.\n` +
  `Read ${SKILL}/pipeline/06a-animate.md and ${SKILL}/references/knowledge.md first; use motion (+ gsap) techniques as fits the motion.\n` +
  `General brief:\n${BRIEF}\n\nFrame idx=${f.idx} per-frame prompt:\n${f.prompt}\n\n` +
  (f.delta ? `Before→after transition delta (the source of truth for what to animate):\n${typeof f.delta === 'string' ? f.delta : JSON.stringify(f.delta)}\n\n` : '') +
  `Add this frame's animation (GSAP/CSS/JS) INTO the shared stitched document at ${DOC}. ` +
  `Enforce ELEMENT REUSE: a logo/product/text block shared with other frames must be the SAME continuous node, not a per-frame duplicate. Lean toward restraint. Prove any loop is seamless (value+velocity; period divides loop length).\n` +
  (fix ? `Apply this animation-QA fix as a TARGETED edit, not a rebuild:\n${fix}\n` : '') +
  `Return {applied, notes}.`

const qaPrompt = (f) =>
  `You are stage 06b-anim-qa of the figma-to-animation pipeline.\n` +
  `Read ${SKILL}/pipeline/06b-anim-qa.md and ${SKILL}/references/knowledge.md first.\n` +
  `Review frame idx=${f.idx}'s animation in ${DOC}. Primary method: code-level review (read the GSAP timeline / CSS keyframes / JS — check easing values, durations, sequencing, element reuse). Secondary: snapshot a handful of frames apart and sanity-check the motion.\n` +
  `The four checks: (1) matches the per-frame prompt's intent (what moves/stays/transition direction), (2) easing smooth & consistent with motion principles, (3) timing reasonable (not too fast/slow), (4) nothing broken/misaligned/duplicated.\n` +
  `Return {pass (all four true), fixPrompt (targeted, empty if pass), checks}.`

// Sequential per-frame loop (shared doc → no parallel edits)
const out = []
for (const f of FRAMES) {
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
  log(`⚠ ${failed.length}/${out.length} frame animations did NOT pass after ${MAX} iters: ${failed.map((r) => `f${r.idx}`).join(', ')} — surface to user, do NOT flow-connect.`)
} else {
  log(`✓ all ${out.length} frame animations passed — cleared for 06c flow-connect`)
}
return { frames: out, allPass: failed.length === 0, failed }

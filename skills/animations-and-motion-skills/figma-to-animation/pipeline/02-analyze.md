# 02 · Analysis & Prompt Generation

**Role:** turn the frames into the animation blueprint — a deep visual understanding plus the
structured prompts that drive every downstream stage. Analysis and prompt generation are one skill
because they're tightly coupled.

**Inputs:** the context package from 01.

**Do (in order):**
1. **Vision-first analysis (hard rule).** Look at the rendered frame images *first*. Only use the
   Figma MCP as secondary confirmation, never as the primary source of understanding. Cover:
   - **Elements** — what's present per frame.
   - **Typography** — fonts/sizes/weights, and whether text animates across frames.
   - **Composition** — layout, spacing, visual-weight shifts between frames.
   - **Sequence logic** — classify **linear | loop | parallel-independent**. For a loop, identify
     exactly how the last frame connects back to the first (the restart).
   - With many frames, explain **each** frame, not just the sequence.

1b. **Per-transition delta (before → after) — this is what actually gets animated.** The animation
   *is* the set of changes between consecutive frames, so analyze each pair explicitly, not each frame
   in isolation. For every transition **frame N → frame N+1** (and, for a loop, **last → first**),
   put the two frames side by side and enumerate, per element, exactly what changes:
   - **Appears / disappears** — new elements entering, elements leaving (and from/to where).
   - **Moves** — position deltas (direction + distance); is it a slide, drift, or path?
   - **Resizes / scales** — size deltas (grow/shrink, from which origin).
   - **Restyles** — color, opacity, blur, corner-radius, shadow, typography changes.
   - **Reorders / re-parents** — z-order or containment shifts.
   - **Persists unchanged** — elements that stay put (these must be *reused*, not re-animated — see
     the element-reuse rule).
   From each delta, infer the **intended motion**: what moves, in which direction, and the implied
   timing/easing (e.g. "logo slides up 40px and fades in over ~0.4s ease-out; headline word swaps").
   An element that is identical in both frames but was flagged as moving is a red flag — re-check.
   This before/after diff is the primary input to the per-frame prompts (Step 3).
2. **General animation brief** — one distinct artifact describing the overall concept and flow
   (e.g. "product reveal → interaction → loop"). It is the consistency baseline and is referenced by
   6a/6b/6c/08, so it must exist explicitly, not be implied.
3. **Per-frame prompts** — one per frame, derived from the brief **and the Step 1b before/after
   delta** (not written in isolation). Each prompt states, grounded in the diff: what animates *in*
   (the exact changes from the previous frame — what moves/appears/resizes/restyles, with direction
   and distance), what **stays static / is reused unchanged**, the timing/easing intent implied by
   the delta, and the forward connection to the next frame (which of this frame's elements carry into
   the next transition). Cite the specific element deltas so stage 06a animates the real change, not
   a guess.

**Output / handoff:** `{brief, perFramePrompts[], transitionDeltas[], sequenceClass, loopRestartLogic}`
→ the asset/SVG/video sub-skills, then stage 03. `brief`, `transitionDeltas`, `sequenceClass`,
`loopRestartLogic` are carried forward to 6a (drives the actual motion), 6b/6c (verify the delta was
realized), and 08. Each `transitionDeltas[i]` = the per-element before→after change list for
transition frame i→i+1 (last→first for a loop).

**QA:** none (produces analysis + prompts). **Standalone:** yes — use it to get a brief + per-frame
prompts for any storyboard.

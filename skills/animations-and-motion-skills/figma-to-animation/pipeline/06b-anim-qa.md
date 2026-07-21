# 06b · Animation Building QA

**Role:** verify each frame's animation matches intent, timing, and easing before frames are
connected. Loops with 06a per frame until passing.

**Inputs:** the animated frame (06a) + its per-frame prompt + general brief (02).

**Method:**
- **Primary — code-level review.** Read the actual animation code (GSAP timeline, CSS keyframes, JS):
  check easing values, durations, sequencing, and that shared elements are reused (one node), not
  duplicated. No rendering required.
- **Secondary — snapshot review.** Capture screenshots a handful of frames apart (seek the
  timeline / `tl.pause(t)` — headless live capture lags) and sanity-check the motion visually.

**The four checks (all must be true to pass):**
1. Matches the per-frame prompt's intent — what moves, what stays static, transition direction.
2. Easing is smooth and consistent with the motion baseline.
3. Timing is reasonable — not too fast, not needlessly long.
4. Nothing appears broken, misaligned, or duplicated (per code logic and snapshots).

**Routing:** on fail, emit a **specific** fix-prompt (which tween/element/value) → stage 06a; never a
vague note or full rebuild. On pass, hold the frame until all frames pass (Loop B barrier).

**Output / handoff:** `{pass, fixPrompt, checks}`. **Standalone:** yes — QA one frame's animation.

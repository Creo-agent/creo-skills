# 06c · Animation Flow Connector

**Role:** connect all individually-approved frame animations into one continuous end-to-end flow, and
verify the whole sequence works together — not just each frame in isolation. The last build-side
checkpoint before export.

**Precondition:** every frame animation has passed 06b.

**Inputs:** all approved frame animations (in the stitched doc); the general brief + sequence class +
loop-restart logic (02).

**Verify (three checks):**
1. **Transitions** — every frame-to-frame handoff reads naturally (no visual jump, pop, or
   discontinuity) **and realizes the intended before→after delta from 02** — the elements that were
   supposed to move/appear/resize/restyle actually do, in the right direction, and the ones marked
   "persists unchanged" don't jump.
2. **Loop restart** — if the sequence loops, the last-frame → first-frame restart must be as smooth
   as any other transition. **Prove it** (this session's method): snap oscillator periods to integer
   divisors of the loop length, confirm `value(0)==value(L)` AND `velocity(0)==velocity(L)` for every
   oscillator, confirm discrete cyclers return to their t=0 state, and render boundary stills
   (frame 0 vs frame N−1). Don't assert seamlessness — show it. (See `motion`.)
3. **No duplicate/overlapping elements** — full-sequence audit that shared elements are one continuous
   node, not duplicated per frame (the 06a reuse rule, re-checked where duplication is most visible).

**Routing:** a bad transition / broken loop / duplicate element routes back to the **specific frame's
06a** as a targeted fix — never a full-sequence rebuild.

**Output / handoff:** one fully connected animation → stage 07. **Standalone:** yes — connect a set of
built animations into a flow and verify the seams.

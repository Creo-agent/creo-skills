# Batch Workflow — Several Placements in One Session

## Contents
- What this is
- Session-level artifacts
- Selecting and ordering placements
- The loop
- What batch adds: cross-placement consistency
- The closing pass
- Failure handling

---

## What this is

**A thin loop around `RESIZE-WORKFLOW.md` — not a second implementation.** Building three
placements is running the same ten-step engine three times. Every hard rule, every gate layer and
every approval checkpoint applies identically whether you build one placement or all three.

There is exactly one behavioural addition, at the end: a cross-placement consistency pass that no
single placement can perform on itself.

The temptation this file exists to resist is batching — running two or three placements inside
one `use_figma` call because they seem similar. Don't. `use_figma` is atomic per call, so one
error partway through discards the placements that had already succeeded, and a batched result
gives no signal about which step produced which defect. It also removes the user's chance to
correct a wrong interpretation on placement one instead of discovering it on placement three.

## Session-level artifacts

Three things are created **once** and shared by every placement:

| Artifact | Created at | Reused by |
|---|---|---|
| `measure-master.json` | first placement's Step 2 | every placement's Step 9b |
| `Generated Ad Sizes N` container | first placement's Step 4 | every subsequent clone |
| The confirmed element-role map (which node is logo / headline / visual / CTA) | first placement's Step 3 | every subsequent plan |

Re-deriving any of these per placement is waste at best. Re-measuring the master mid-session is
worse than waste: if the master was edited in between, the baseline moves and earlier placements
were gated against a different reference than later ones. See `PRE-RESIZE-MEASUREMENT.md`.

## Selecting and ordering placements

Present the three and ask which are wanted. **Never assume "all sizes"** — it is the single most
expensive assumption available here, since each unwanted placement costs a full gate cycle.

Then propose an order and confirm it. A reasonable default is **hardest first**: Story
(1080×1920) before the feed sizes, because a 1:1 or portrait master reaching 9:16 is the largest
aspect-ratio change and surfaces element-role and dead-space questions earliest. Answering those
on placement one makes the feed sizes near-mechanical.

State the order explicitly — "I'll start with Story; once you approve it I'll move to LinkedIn,
then Facebook" — so the user can reorder before any work happens.

## The loop

For each placement, in the agreed order:

1. Run `RESIZE-WORKFLOW.md` Steps 0–10 in full.
2. Deliver, and **wait for explicit approval** (R29).
3. Only then start the next.

Carry forward what the user has already decided rather than re-asking: CTA label and colour,
exclusions, and any placement-independent preference they expressed. State what you carried so
they can correct it — "carrying forward the white CTA reading *Get started free*" — rather than
silently reusing it.

If the user changes an answer mid-session (a different CTA label from placement two onward),
note that earlier placements were built with the previous answer and ask whether to update them.
Leaving a set half-updated is a defect that only shows up when someone views all three together.

## What batch adds: cross-placement consistency

A single placement is verified against the master. It cannot check whether it agrees with its
siblings — and a set of creatives is judged as a set.

After every placement is built and individually approved, check across the outputs:

| Check | Why it can only be seen across placements |
|---|---|
| **CTA label identical** | Each placement's label is individually correct; only side by side does it show that one says "Get started" and another "Get started free" |
| **CTA colour and style identical** | A per-placement colour answer given twice can drift |
| **Logo treatment consistent** | Same relative scale and same corner across the set, unless a placement's layout order deliberately differs |
| **Exclusions deliberate** | An element excluded from one placement and kept in another should be a decision, not an accident of which brief was answered when |
| **Type hierarchy reads consistently** | Headline reduced to fit on one placement can leave that size looking like a different campaign |
| **All built from the same baseline** | Every output's `meta` should trace to the same `measure-master.json` |

Anything inconsistent here is reported to the user as a set-level finding, with the specific
placements named. Do not silently normalise them — the difference may be intentional.

## The closing pass

Capture all outputs together — the container frame holds them side by side, so one
`get_screenshot` on the container gives the whole set — and look at them as a group.

This pass is for **set coherence only**: do they read as one campaign, is the visual weight
comparable, does one placement look like it came from a different design. It is not a substitute
for anything in the per-placement gate, and specifically it cannot see anything small — a
container screenshot of three large frames is heavily downscaled, which is exactly the condition
under which squashed avatars and glyph-substituted icons hide. Those belong to the per-placement
element-zoom layer (`ACCURACY-GATE.md` §9c) and are already done by this point.

Then deliver the set: the container screenshot, each placement's individual QA verdict, and a
consolidated list of accepted gaps across the set.

## Failure handling

If a placement fails its gate twice, stop and ask (per `RESIZE-WORKFLOW.md` Step 9) — but do not
let it block the rest of the batch. Offer to park it, continue with the remaining placements, and
return to it afterwards with a different approach.

If the same rule fails on **every** placement, that is not three defects — it is one cause
upstream, usually in the geometry pass or a wrong value read from the spec. Fix the cause and
re-gate the set rather than patching each output.

# Placements — Reasoning, Layout Order, Size-Unique Rules

## Contents
- How to use this file
- Where the numbers come from
- Two operation types: resize vs. crop
- STORY — 1080×1920 Story / Reel
- FB — 1080×1350 Facebook Feed
- LI — 1200×1200 LinkedIn Feed
- REDDIT_COMMENT — 1440×1080 Reddit Comment-Style
- On hold — not implemented
- Placement comparison

---

## How to use this file

**`placements.json` holds every number. This file holds the reasoning.** Read both at Step 0:
the JSON so you build against current values, this file so you understand what the values are
protecting against.

Nothing here restates a pixel figure that lives in the JSON, on purpose — a number written twice
is a number that will disagree with itself after the first edit.

## Where the numbers come from

Every safe zone carries a `safeZoneSource` in the JSON, and the distinction matters when you are
deciding whether a violation is negotiable:

| Source | Meaning | Negotiable? |
|---|---|---|
| `platform` | The platform publishes it, and its UI physically occupies that space | **No.** Violating it hides content on a real device. |
| `internal-tested` | The team's own tested/observed real-device figure — can supersede `platform` | **No**, for the same reason as `platform`: it protects against real UI coverage. Update only with new testing, not per-job preference. |
| `derived-house` | Derived from a documented platform behaviour, not published as a safe zone | Rarely — the derivation states what breaks. |
| `house` | Creo convention for consistency; no platform requirement | Yes, with a stated reason. |
| `n-a` | No safe zone applies — e.g. a crop-only placement with no composed layout | N/A |

`safeZonePct` is the source of truth; pixel values are derived from it by ceiling, so the zones
stay correct if a canvas size ever changes.

**Verified against the platforms' own documentation on 2026-08-31.** Third-party "ad spec sheet"
articles are unreliable here — several assert Story-style safe zones for Feed placements, which
conflates two genuinely different situations. Only Stories and Reels have UI overlaying the
creative.

**Superseded in part on 2026-09-01.** Story's safe zone now uses the team's own tested figures
(`internal-tested`, sourced from the Ad-Specific QA Checklist) rather than Meta's published
guidance, because the two differ meaningfully and the team's own measured figure was chosen as
the operating default. This is not a claim that platform docs are unreliable in general — FB and
LI's `derived-house`/`house` reasoning, verified the same day, stands unchanged. It is a specific
case where an internal test produced a different, trusted number for one specific placement.

## Two operation types: resize vs. crop

Every placement carries an `operationType` in `placements.json`. The two types are genuinely
different engines — check this before doing anything else with a placement:

- **`resize`** (STORY, FB, LI) — clone the whole master composition, transform it, keep every
  element. Runs the ten-step engine in `RESIZE-WORKFLOW.md`.
- **`crop`** (REDDIT_COMMENT) — extract a single fragment of one element from the master and
  discard everything else. Runs the distinct workflow in `REDDIT-COMMENT-WORKFLOW.md`. Most of
  `HARD-RULES.md` (logo integrity, text preservation, CTA rules) does not apply to a crop
  placement, because a crop placement isn't supposed to have a logo, text or a CTA at all.

Never run a `resize` placement through the crop workflow or vice versa — the two have almost
nothing in common beyond "start from the same master."

---

## STORY — 1080×1920 Story / Reel

**Safe zone source: `internal-tested`. Not negotiable.** Top 200px (10.4%), bottom 540px (28.1%),
sides 65px (6%) each.

These figures come from the team's own Ad-Specific QA Checklist (Rachel), sourced from tested,
real-device coverage rather than read off a platform spec page. The reason the zone exists is the
same as any platform-published safe zone: **the platform's own UI physically occupies those
pixels.** Content in the top band sits behind the profile chip and handle. Content in the bottom
band sits behind the CTA and the platform's own controls. A frame that violates it looks perfect
in Figma and is broken on a phone — which is precisely why the value has to come from the spec
file rather than from a designer's or a model's sense of proportion.

**⚠️ Two corrections, not one — read the full history before trusting any number you remember
from an earlier session.**

- **2026-08-31:** the skill's bottom reserve was `21%` (403px); Meta's own published guidance
  specifies `35%` (672px). Corrected to match Meta's guide. Top already matched Meta at `14%`
  (269px), so this touched bottom only.
- **2026-09-01:** superseded again, on **both axes**, by the team's tested figures — top `10.4%`
  (200px), bottom `28.1%` (540px). This is not a further refinement of the same number; it's a
  switch of *source*, from the platform's published (conservative) recommendation to the team's
  own measured real-device coverage. Team decision: use the tested figure as the operating
  default. **Sides are unchanged** at 65px/6% — the doc that supplied the new top/bottom figures
  doesn't address side margins at all, so the Meta-derived side value is carried forward
  deliberately, not by oversight.
- **The old "recommended starting y for the visual group" hints are retired, again.** Any such
  number calibrated against a prior usable-area boundary is stale the moment that boundary moves.
  Derive the visual's position from `usableArea` in the JSON — never from a cached pixel value.

**Layout order:** Logo → Headline → Visual → CTA (if included), top to bottom within the usable
area. The visual should carry at least the `visualMinShareOfUsableHeight` share of usable height —
a Story whose hero element is small reads as a repurposed feed post rather than a Story.

**Hero visual placement.** Centre the hero visual horizontally within the usable area. (Early
docs specified a "visual focal zone" tiling the usable width into left/centre/right bands and
directed the hero into "the center 25%" — a fractional strip that was never a usable instruction.
The intent was horizontal centring; that is what survives.)

**The structural dead space — recomputed, and the conclusion changed materially.** The usable
area is now **950×1180**, a ratio of **0.805** — noticeably portrait, not square. That single
fact determines how much dead space exists. See `ASK-DONT-GUESS.md`'s fit table for the exact
numbers per master aspect ratio: the short version is that even a **1:1 master now leaves ~230px**
of vertical slack — enough to clear the "raise it with the user" threshold, where under the
2026-08-31 numbers it barely did (29px). Do not carry forward the earlier session's conclusion
that "a square master is close to a clean fit" — recompute against the current `usableArea`
every time, because this number has already moved twice.

---

## FB — 1080×1350 Facebook Feed

**Safe zone source: `derived-house`.**

**Meta publishes no safe zone for Feed placements.** Feed creatives render in full inside the post
container, and the headline and CTA are rendered *below* the image, not over it. There is no
overlay to dodge.

So why a margin at all? Because there is a real **crop** risk that has nothing to do with
overlays: a 4:5 creative delivered to a carousel placement is cropped to 1:1, which removes 10%
from the top and 10% from the bottom. The margin here is the centre-crop survival zone — key
content inside it survives that crop intact. Sides match STORY's 6% for visual consistency across
the set.

That derivation is worth keeping in mind when a layout wants to break the margin: the question is
not "will Meta cover this?" but "will this survive being re-delivered as a square?" If the
creative will only ever run as a 4:5 single image, the top/bottom margin is genuinely negotiable —
state that as the reason.

**Layout order:** Logo → Headline → Visual → CTA (if included). Headline can run larger than in
the master for feed presence.

**On resolution:** Meta's recommended resolution for 4:5 Feed is higher than the canvas this skill
uses. The skill's canvas is the same aspect ratio and comfortably above Meta's minimum, and was
kept deliberately (decision 2026-08-31) so frame names and layout figures stay stable. If output
quality ever becomes the constraint, changing it is a one-line edit to `placements.json` — the
percentage-based safe zones recompute themselves.

---

## LI — 1200×1200 LinkedIn Feed

**Safe zone source: `house`. Negotiable with a stated reason.**

**LinkedIn publishes no safe zone.** Its ads guide specifies dimensions, aspect ratios and file
limits only. Headline and CTA render below the image in the feed card, nothing overlays the
creative, and there is no cross-placement crop within LinkedIn. The margin here is a Creo
convention for consistency with the other two placements — it is not protecting against anything
the platform does.

1200×1200 *is* LinkedIn's own recommended square size, so the canvas needs no qualification.

**Layout order:** centred, balanced composition. Logo top or top-left, matching the master's logo
position intent; visual prominently scaled in the centre; CTA lower with proper spacing.

**Size-unique rule — no empty corners.** A square canvas is unforgiving about a portrait
composition dropped into it: the result reads as letterboxed rather than designed. The composition
should fill the square, which usually means scaling the visual up rather than preserving the
master's proportional placement exactly. The `geometry_position_redistributed` soft rule
(R3) is the mechanical version of this check.

Text can carry more weight here than in the feed placements — LinkedIn creatives are viewed at a
larger relative size in-feed.

---

## REDDIT_COMMENT — 1440×1080 Reddit Comment-Style

**Operation type: `crop`, not `resize`.** This is the skill's first placement that doesn't clone
and transform a whole composition — full reasoning and step-by-step process in
[`REDDIT-COMMENT-WORKFLOW.md`](REDDIT-COMMENT-WORKFLOW.md). This section covers only what makes
the placement itself distinct.

**What belongs in the output:** a single eye-catching crop pulled from the **master's original
full-size visual** — not a downscaled visual already used in another placement, and not the
whole visual squeezed to fit. **What does not belong:** logo, headline, subheadline, CTA. None
of them. This runs next to platform-rendered comment text, so the image is the entire creative.

**No safe zone.** There's no platform UI overlaying the image itself — `safeZoneSource: "n-a"`.

**The one rule that matters most here:** the subject's focal point stays visible and centred in
the new crop — "visible" is necessary but not sufficient; a crop that keeps the subject fully
in-frame but pushed to a corner still fails this.

**Maturity note.** Every other placement in this skill has been built and reasoned through in
depth; this one has not yet run against a real master. Treat its workflow as a documented first
pass, not as battle-tested as STORY/FB/LI — flag anything that turns out wrong rather than
assuming the gap is yours.

## On hold — not implemented

Two siblings from the same source spec are explicitly on hold and are **not** built here — noted
so they aren't silently forgotten if priorities change:

- **Reddit feed** — 1:1, 1200×1200 (same canvas as LI).
- **Google DV360** — TBD, 5 sizes.

---

## Placement comparison

Useful when planning a batch, because the differences drive the order to build in
(`BATCH-WORKFLOW.md` defaults to hardest first):

| | STORY | FB | LI | REDDIT_COMMENT |
|---|---|---|---|---|
| Operation type | `resize` | `resize` | `resize` | **`crop`** |
| Aspect ratio | 9:16 | 4:5 | 1:1 | 4:3 |
| Safe zone source | `internal-tested` | `derived-house` | `house` | `n-a` |
| What the zone protects | Real platform UI physically covering content | surviving a 1:1 carousel crop | consistency only | — |
| Overlay risk | **yes** | no | no | no |
| Usable share of canvas | smallest, and portrait-shaped (0.805) | middle | largest | — (not a composed layout) |
| Typical difficulty | hardest of the resize placements — biggest ratio change, real dead space even for square masters | easiest — often same or near ratio | middling — square needs filling | different in kind, not degree — see workflow |

Read the exact figures from `placements.json`.

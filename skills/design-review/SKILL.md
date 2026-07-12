# Design Review

A structured brand and creative review for marketing assets — ads, banners, landing pages, social posts, emails, OOH, and motion assets. Reviews against brand standards: color, typography, composition, visual hierarchy, voice & tone, and accessibility.

The source of truth for approved tokens and brand rules is `skills/tokens.md` (extracted from the Clay design system at `Creative Operations/clay-design-system`).

> **Read-only rule:** This skill NEVER modifies Figma. Do not call `use_figma`, `create_new_file`, `generate_figma_design`, `upload_assets`, or any other write tool — on any Figma MCP server, for any reason. Only `get_screenshot` and `get_design_context` are permitted. If the user asks you to fix something in Figma, reply that this skill is review-only and suggest they apply the fixes themselves or use a different workflow.

---

## How to invoke

`/design-review [Figma URL | image description | "is this on-brand?"]`

The text after the command is the ask — typically a Figma URL, a question about a specific asset, or a Slack-attached image.

---

## Step 1: Gather context

Use whichever inputs are available:

| Source | How to get it | What it gives you |
|--------|---------------|-------------------|
| Figma URL — screenshot | `get_screenshot` (figma-write) | Visual rendering — use for composition, hierarchy, visual judgment |
| Figma URL — layer data | `get_design_context` (figma-write) | Exact font sizes, colors, spacing, token names — use for precise compliance checks |
| Slack attachment / image | Read the file from `.slack-uploads/` | Visual state when no Figma URL is given |
| Campaign brief / description | Provided in the ask text | Audience, goal, surface type |

**Before reviewing any asset, read `skills/tokens.md`** — this gives you exact hex values, font sizes, spacing values, and token names from the Clay design system to compare against Figma layer data. Do not estimate values that are listed there.

**When a Figma URL is provided:** always call **both** `get_screenshot` and `get_design_context` — never just one. The screenshot tells you what it looks like; the layer data tells you what the values actually are (font sizes, hex codes, token names). A finding backed by layer data ("Headline is 14px — minimum is 16px") is a precise finding, not a visual estimate.

If the URL points to a Figma page (not a specific frame), list available frames via `get_design_context` and either ask which frame in the Slack reply, or review all frames on the page.

**State what you have before reviewing:**
> "Reviewing: Figma screenshot + layer data (2 frames). No campaign brief — evaluating against design system defaults."

---

## Step 2: Detect surface type

Identify the asset type — this determines which standards apply:

- **Banner ad / display** → brand color, logo usage, composition, visual hierarchy, CTA, typography, safe zones
- **Social post (static)** → brand color, typography, composition, message hierarchy, visual-to-copy balance
- **Social content (motion/video)** → motion compliance, composition, captions, message hierarchy
- **Landing page** → brand color, typography, composition, visual hierarchy, message hierarchy, voice & tone, imagery style, contrast
- **OOH / print** → logo usage, typography, composition, safe zones, color-independent readability
- **Email** → brand color, typography, message hierarchy, CTA, voice & tone

---

## Step 3: Review

Evaluate against the standards below. When layer data is available, use exact values — don't estimate.

**Severity:**
- 🔴 **Critical** — brand violation or unpublishable
- 🟠 **Major** — confusing, weakens brand or message significantly
- 🟡 **Minor** — noticeable but unlikely to fail alone
- ⚪ **Polish** — nice-to-have refinement

**Always check (regardless of surface):**

- **Composition** — Is visual weight balanced? Is whitespace intentional (macro between sections, micro between elements)? Spacing from the scale? Related elements grouped by proximity (gestalt)?
- **Visual hierarchy** — Single dominant entry point? Eye flows naturally to the CTA? Size differentials ≥1.5× between levels? Exactly one primary emphasis zone?
- **Brand consistency** — Colors, typefaces, and logo match the design system? Visual language (photo style, illustrations) matches brand personality? Copy tone matches voice guidelines? Token names used in layers, not hardcoded hex values?
- **Color** — Palette limited to approved tokens? Color not the sole indicator of meaning? No unintended vibrancy or noise between adjacent elements?
- **Accessibility** — WCAG AA contrast (4.5:1 body, 3:1 large text) for digital; readable in grayscale for OOH/print; motion assets have captions?

**Full standards reference (for deeper evaluation):**

*Brand Identity*
- **Brand color compliance** — Only token values; no arbitrary hex or off-brand tints; neutrals/primaries/accents in correct roles; color not sole indicator of meaning.
- **Typography compliance** — Defined scale steps only; body ≥16px desktop / ≥14px mobile; line-height 1.4–1.6 body, 1.1–1.3 headings; line length 45–75 chars for body; consistent treatment across equivalent elements; no hardcoded font values.
- **Logo / lockup usage** — Correct variant (full, icon, wordmark); clear-space rules respected; no distortion or recoloring.
- **Voice & tone** — Matches brand tone; no forbidden vocabulary; CTA labels specific and action-oriented; consistent register across headline, body, disclaimer.
- **Imagery & illustration style** — Photo style, illustration, iconography match brand personality; no tonally-off elements; motion uses approved easing/timing.

*Visual Craft*
- **Composition** — Balance (clear center of gravity), whitespace (macro + micro consistent), rhythm (spacing from scale), gestalt (proximity, figure/ground, continuity).
- **Visual hierarchy** — Single entry point, F/Z eye flow, ≥1.5× size differentials, one emphasis zone.
- **Color: palette & contrast** — Token values only; no visual noise; WCAG AA ratios met.

*Messaging & Conversion*
- **Message hierarchy** — Primary claim above fold; supporting copy subordinate; no buried critical info; scannable chunks, not dense prose.
- **CTA placement & clarity** — Single dominant CTA; filled/solid primary, ghost/text secondary; specific action label; placed where the decision is made.
- **Visual-to-copy balance** — Copy doesn't crowd the visual; white space is intentional.
- **Safe zone & bleed** — Key elements inside safe zone; background extends to bleed where required.

---

## Step 4: Output (Slack format)

Keep it readable in a Slack thread. Lead with the verdict, then the findings, then the overview.

```
*Design Review: [Asset or Campaign Name]*
Reviewed: [what inputs were used, confidence level]

*Verdict: PASS / WARN / FAIL*
Threshold: Critical | [n] Critical · [n] Major · [n] Minor · [n] Polish

*Findings*
🔴 [Standard] — [Location]: [What's wrong and specific fix]
🟠 [Standard] — [Location]: [What's wrong and specific fix]
🟡 [Standard] — [Location]: [What's wrong and specific fix]

*Overview*
[One short paragraph: what's solid, what needs the most attention, single most important thing to fix. Colleague tone.]
```

**Location:** use frame + layer name for Figma ("300×250 / Headline"), element position for images ("bottom-right CTA"), or "—" for text-only.

**If there are many findings:** group by severity, not by standard. Lead with Critical/Major, then Minor/Polish in a collapsed section if Slack supports it.

**Saving the review:** if the person wants a permanent record, write a copy to `Creative Operations/<person>/[project]/design-review-v<NN>.md` using the standard naming convention (see `skills/file-naming-and-versioning.md`).

---

## What not to do

- **Never modify Figma.** Do not call `use_figma`, `create_new_file`, `generate_figma_design`, `upload_assets`, or any write tool. Read-only: `get_screenshot` and `get_design_context` only. If asked to fix something in Figma, decline and explain this skill is review-only.
- Don't flag things you can't point to specifically — no "the layout feels off."
- Don't apply product interaction heuristics (keyboard nav, loading states, empty states) to static marketing assets.
- Don't estimate a value that layer data can confirm — look it up.
- Don't flag purely subjective preferences unless they violate a documented brand standard.
- Don't expand the review to frames or assets that weren't asked about.

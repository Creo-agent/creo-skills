# How to Give Claude Feedback When Using figma-to-web

This is a short guide for anyone using this skill to build pages/sections from Figma. Following
it makes builds faster and more accurate — Claude works from what you give it, not from what you
meant.

## 1. Always give the exact Figma link, with `node-id`

Not "the hero section" or "the page we discussed" — paste the actual URL from the Figma tab's
address bar, pointing at the specific frame/section you mean:

```
https://figma.com/design/ABC123/my-file?node-id=47-1515
```

If you're pointing at a sub-section inside a bigger frame, select that layer in Figma first so
the URL's `node-id` reflects it — don't make Claude guess which child you mean from a screenshot.

## 2. When reporting a bug, say what's wrong and what it should be — not "it's not good"

Claude cannot act on "the header looks off" or "this isn't right." It can act on a concrete
before → after:

| Don't write | Write instead |
|---|---|
| "the spacing is off" | "there's too much gap between the title and the button — in Figma they're 16px apart, in the build it looks like ~40px" |
| "the button looks wrong" | "the button should be the primary green CTA style, not the outline one" |
| "this section is broken" | "the tabs don't switch content when clicked — clicking 'Features' still shows the 'Pricing' panel" |
| "fix the colors" | "the card background is white, it should be the light-gray `surface/secondary` token" |

If you're not sure of the exact value, that's fine — describe the symptom precisely (what you see
vs. what you expected) rather than passing a vague verdict.

## 3. Point at the exact component, don't make Claude search for it

The fastest way to identify a component precisely:

- **Screenshot** — crop a screenshot of just the problem area (in Figma or in the browser build)
  and attach it. A picture pinpoints "this exact element" far better than a text description.
- **Layer/component name from Figma** — select the node in Figma and copy its name (e.g.
  `CardContainer/Testimonial-02`) instead of describing it in your own words.
- **Class or element name from the browser inspector** — if you're looking at the built HTML page,
  right-click → Inspect, and copy the class name or `id` of the element you mean (e.g.
  `.testimonial-card__quote`). Paste that alongside your feedback.
- **Section name used during the build** — Claude names each section as it builds
  (`hero`, `pricing-cards`, `logo-marquee`, etc.) and reports scores per section — reuse that name.

Combining two of these (e.g. a screenshot + the section name) is ideal for anything visually
subtle.

## 4. When you want something remembered for next time, say so explicitly

If a mistake is a one-off for this page, a normal fix instruction is enough. If it's a pattern
that should never happen again on *any* future build with this skill, say so directly and name
where it belongs:

- "Add this to the skill's GOTCHAS.md: next time, always check X before doing Y."
- "This should become a hard rule — never do Z, always do W instead."
- "Remember this as a general rule for future Clay component matches, not just this page."

Claude will not silently update the skill's shared reference files on its own — it always asks
for confirmation before writing a new rule or lesson (see "Closing step: knowledge capture" in
`SKILL.md`). Being explicit about "remember this for next time" up front makes sure the lesson
actually gets proposed at the end of the build instead of getting lost.

## Quick checklist before sending feedback

- [ ] Figma link included, with `node-id`, pointing at the right node
- [ ] What's wrong AND what it should look like instead (not just "bad")
- [ ] A way to pinpoint the exact element — screenshot, Figma layer name, or browser inspector class/id
- [ ] If this should be remembered permanently — said explicitly, with where it should go

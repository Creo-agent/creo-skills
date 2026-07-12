# Gotchas when extracting web sections

## Blank / tiny HTML from curl
The response is a stub shell (JS-rendered site). Fixes, in order:
1. Add full browser headers (UA + `Accept` + `--compressed`) — see SKILL step 1.
2. Try the site's real render subdomain if it's Webflow (`<sub>.webflow.io` / the
   `data-wf-domain` value in the `<html>` tag).
3. Fall back to reading the live DOM through the browser tools.

## Unstyled section
You missed CSS. Causes:
- The site splits CSS across multiple bundles (a shared one + a page one) — download all.
- Utility classes (grid helpers, `text-size-*`, button classes) live outside the
  section's own prefix. Add those class names to the extractor keyword list.
- CSS custom properties (`:root { --x }`) referenced by the rules — always include `:root`.

## Images missing / blank
- `loading="lazy"` + a pinned/transformed ancestor can keep images from ever entering the
  viewport in an isolated file. Drop `loading="lazy"` for the isolated version.
- Only `srcset` is set (no usable `src`), or the `src` is a tiny placeholder — resolve the
  largest `srcset` candidate.
- CDN blocks hotlinking → download locally rather than referencing the CDN URL.

## Motion doesn't run
- The library CDN tag is missing or a different major version — pin the site's version.
- `ScrollTrigger` needs scroll room; an isolated section may have none. Either add spacer
  height, or (better) hand off to `loop-animator` to convert it to an auto-playing loop.
- `backdrop-filter` renders nothing on a plain background — harmless, but don't chase it.

## Verifying motion in a headless preview
Scrubbed/`scrub` GSAP timelines lag in headless screenshots. Seek deterministically:
`gsap.globalTimeline.getChildren(true,false,true)[0]` to grab the timeline, then
`.pause(t)` or `.progress(p, true)` and screenshot.

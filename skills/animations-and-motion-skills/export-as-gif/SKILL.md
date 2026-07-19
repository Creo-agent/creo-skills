---
name: export-as-gif
description: |
  WHAT: Render an animation into a real saved file — GIF, MP4, or WebM — via Remotion (frame-based, deterministic). Asks for target size/resolution/format/size-limit first, then rebuilds the motion in Remotion and outputs the file.
  TRIGGERS: "export / render / convert / turn this into a gif or mp4", making a GIF, rendering animation to video, getting a downloadable clip of a CSS/HTML/GSAP animation, stitching frames into a gif, producing a file sized for Slack/social/ads/deck (e.g. under 5mb, 15fps).
  SUB-SKILL: figma-to-animation orchestrator routes here for its export stage. Usable standalone whenever the deliverable is an actual video/GIF file on disk (not a live web animation).
  NOT FOR: capturing an animation off a live website → use extract-animation-from-web/. Editing/trimming an existing video clip. Resizing or reorienting → use resize-animation/. Generating static images. Building slide decks. Remotion code questions → use remotion-best-practices/.
---

# Export as GIF (via Remotion)

Render an animation to a real GIF/MP4/WebM by rebuilding it in Remotion, where every frame
is a pure function of time — so renders are deterministic and loops are seamless. Load the
`remotion-best-practices` skill for library rules; this skill is the porting + render recipe.

## When This Skill Activates

- "Turn this html animation into a gif for Slack, under 5mb"
- "Render my gsap loop as an mp4"
- "Make a looping gif of the square animation, 1080×1080"
- "Get me a downloadable webm of this motion"

Keywords: `gif`, `mp4`, `webm`, `render`, `export`, `video file`, `downloadable`,
`shareable clip`, `stitch frames`.

## What This Skill Does

1. **Asks for the output spec first** — dimensions/resolution, fps, format, and any hard
   size limit — because these drive the composition and render flags. (If a `remotion/`
   project already exists for this animation, skip the questions and scaffold: just re-sync
   the changed source constants and re-render — see PROMPT.md §0.5.)
2. Scaffolds a Remotion project and ports the motion to frame-based (`useCurrentFrame`),
   loading web fonts via `@remotion/google-fonts` and rebuilding pseudo-elements as real divs.
3. Reproduces seamless loops via a triangle-wave timeline — or a **forward-loop with
   enter/exit envelopes** when a distinct phase must not play in reverse.
4. Verifies with still renders, then renders GIF/MP4 and tunes `--scale` / `--every-nth-frame`
   to hit the size target. A render is already one seamless cycle, so when asked to "make it
   loop," clarify before baking in repeated copies — GIFs loop natively and MP4 looping is a
   player setting (PROMPT.md §6).

## Entry Point

Load **PROMPT.md** for the output-spec questions, project scaffold, GSAP→Remotion easing
cheat-sheet, the triangle-wave *and* forward-loop recipes, font/pseudo-element gotchas, and
the GIF size-tradeoff levers.

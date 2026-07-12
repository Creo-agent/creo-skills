---
name: export-as-gif
description: >-
  Use this whenever the user wants a real, saved file — a GIF, MP4, or WebM — out of an animation or motion effect. Go-to skill for any "export / render / convert / turn this into a gif or mp4" request: making a GIF, rendering an animation to video, getting a downloadable or shareable clip of a CSS, HTML, or GSAP animation or loop, stitching frames into a gif, or producing something sized for Slack, social, ads, or a deck (e.g. under 5mb, at 15fps). The source can be an existing animation, a finished loop, or just a motion idea — what matters is the user wants a rendered file on disk, not a live web animation. It first asks for the target size/resolution/format and any size limit, then rebuilds the motion in Remotion (deterministic frame-based rendering) and outputs the file. Prefer this over the extract, loop, resize, and figma skills whenever the deliverable is an actual video or GIF file. Do NOT use for: capturing an animation off a website, editing an existing video clip (trim/crop), resizing or reorienting, generating static images, or building slide decks.
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
   size limit — because these drive the composition and render flags.
2. Scaffolds a Remotion project and ports the motion to frame-based (`useCurrentFrame`).
3. Reproduces seamless loops via a triangle-wave timeline.
4. Verifies with still renders, then renders GIF/MP4 and tunes `--scale` / `--every-nth-frame`
   to hit the size target.

## Entry Point

Load **PROMPT.md** for the output-spec questions, project scaffold, GSAP→Remotion easing
cheat-sheet, the triangle-wave loop, and the GIF size-tradeoff levers.

---
name: extract-animation-from-web
description: |
  WHAT: Extract a specific animated section from a live website into a single, self-contained HTML file — its markup, styles, JavaScript (GSAP/ScrollTrigger/Splide/etc.), and all images.
  TRIGGERS: user points at a URL or live page and wants to "grab / rip / isolate / copy / reproduce / extract" a section, hero, or on-page animation into a standalone or offline file — even without the word "animation" (e.g. "pull the floating-cards thing off monday.com/crm", "rip Linear's hero into one html").
  SUB-SKILL: figma-to-animation orchestrator routes here to reference motion off a live site. Usable standalone whenever the source is a live website and the goal is to capture what's already there.
  NOT FOR: making an existing animation loop → use motion/. Rendering to gif/mp4 → use export-as-gif/. Matching a Figma layout → use frame-building/. Resizing → use resize-animation/. Scraping data/text/prices. Building something new from scratch.
---

# Extract Animation from Web

Turn one section of a live site into a **standalone HTML file** that renders and animates
identically on its own, with assets available locally. First stage of the animation
pipeline — pairs with `motion`, `export-as-gif`, and `resize-animation`.

## When This Skill Activates

- "Pull the floating-cards animation off monday.com/crm into its own file"
- "Rip Linear's hero section — css and the js motion — into one standalone html"
- "Grab this section including the images and gsap so it runs offline"
- "Reproduce the scroll animation from this URL as an isolated page"

Keywords: `extract`, `grab`, `rip`, `isolate`, `reproduce`, `standalone`, `offline copy`,
`section`, `hero`, `animation from a site`.

## What This Skill Does

1. Fetches the **real rendered HTML** (defeating JS-stub responses).
2. Locates CSS/JS bundles and extracts **only** the rules + animation config for the section.
3. Downloads images (incl. `srcset`) and rewires them to local paths.
4. Assembles one self-contained `.html` with CSS + JS inlined.
5. Verifies in a browser preview (screenshots, image-load, motion states).

## Requirements

- A URL (or a live page open in the browser tools). If none is given, ask for it first.

## Entry Point

Load **PROMPT.md** for the full step-by-step workflow. Consult **references/gotchas.md**
when a section renders blank/unstyled, and use **scripts/extract_css.py** to pull the
matching CSS rule blocks.

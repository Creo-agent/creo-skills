---
name: precise-figma-composition
description: >-
  Reproduce a Figma frame's layout pixel-accurately in code by pulling each node's exact coordinates from Figma and scaling them to a target canvas — instead of eyeballing positions from a screenshot. Go-to skill whenever the user shares a figma.com link or node and wants a composition "matched exactly", "like in the figma", "pixel perfect", "the right positions", or wants a scattered/layered arrangement (cards, badges, floating elements around a hero) placed precisely — especially when a prior eyeballed layout was "close but wrong" and they point to Figma as source of truth. Prefer this over figma-design-to-code specifically for getting a scatter/overlay layout's geometry right. Do NOT use for: building a full Figma screen as a component, grabbing an animation off a website, animating/looping, rendering to gif/mp4, resizing, or exporting a Figma frame to png.
---

# Precise Figma Composition

When a layout must match a Figma design *exactly* — positions, sizes, overlaps — don't
estimate from a screenshot. Read the real coordinates from Figma and transform them once.
This is how you nail a scattered composition (cards floating around a central figure) that
eyeballing always gets subtly wrong.

## When This Skill Activates

- "Match this composition exactly to my figma <link> — the cards are in the wrong spots"
- "Place these floating elements pixel-perfect like in the figma frame"
- "My eyeballed positions are off — pull the real coords from figma and apply them"
- "The figma shows this card tucked behind that one; match the stacking"

Keywords: `figma`, `pixel perfect`, `match the figma`, `exact positions`, `scatter layout`,
`overlap`, `source of truth`, `right coordinates`.

## What This Skill Does

1. Pulls exact `x/y/w/h` per node via the Figma MCP `get_metadata`.
2. Computes a scale factor (target canvas ÷ Figma frame) and maps every node to absolute px.
3. Preserves draw-order stacking (intentional overlaps).
4. Emits absolute-positioned HTML/CSS or a coordinates array for Remotion.
5. Verifies element-by-element against a `get_screenshot`.

## Requirements

- A Figma design URL (path `/design/`) pointing at the frame/node. Ask for it if missing.

## Entry Point

Load **PROMPT.md** for the full workflow, and **references/figma-notes.md** for reading the
metadata correctly (image-fill hero rects, hidden nodes, frame vs silhouette bounds).

# Setup & prerequisites (product-animations pipeline)

This pipeline shares the `skills/animations-and-motion-skills/` group's tooling. **The full tool table + doctor check +
the Node-version trap live in the sibling doc — use it, don't duplicate it:**
[`../../figma-to-animation/references/setup.md`](../../figma-to-animation/references/setup.md)
(Node ≥18, Remotion, FFmpeg, GSAP, Figma access, the portable `nvm which 18` recipe).

Below is only what differs for **product** animations.

## What this pipeline actually needs

It builds a **live HTML/CSS/JS + GSAP** prototype; export to video/GIF is a separate handoff to
[`../../export-as-gif/`](../../export-as-gif/), and only then do Node/Remotion matter.

| Need | When | Note |
|---|---|---|
| **GSAP** (CDN) | always | The motion engine and the shared `master` timeline (`timeline-clock.md`). No install. |
| **Figma MCP** | plan / recreate / design-QA | Read the design through it — Dev Mode (local) or plugin transport. See the sibling's *Figma access* section. |
| **A static server** | always | Serve the prototype over `http://` (`python3 -m http.server 8753`); `file://` breaks font loading and some measurement. |
| **Node ≥18 + Remotion** | **export only** | Not needed for the live prototype — only when handing off to `export-as-gif`. Watch the sibling's `EBADENGINE` Node-version trap. |

**Not needed** (unlike the general pipeline): gifski, ImageMagick (Remotion's own GIF encoder), or any
video-generation provider.

## Quick doctor check

```bash
# live prototype (always):
python3 -c "import http.server" && echo "static server OK"
# GSAP is CDN — confirm the page's gsap <script> resolves (network reachable)

# export only (handing off to export-as-gif): run the sibling setup.md doctor block (Node ≥18 + a
# single `remotion still` render) before the slow export stage.
```

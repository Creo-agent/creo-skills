# Setup & prerequisites (tools to install)

The single source of truth for **what must be installed to run this pipeline** and reproduce its
results on any machine. Run the [doctor check](#doctor-check) once before a run — a missing/too-old
tool otherwise fails silently upstream and only surfaces at the export stage (the slowest one).

This covers the `figma-to-animation` pipeline and its engine siblings. It deliberately does **not**
cover the separate HyperFrames video toolkit.

## Required tools

| Tool | Why the pipeline needs it | Install | Verify |
|---|---|---|---|
| **Node.js ≥18** | Remotion 4 (the export engine) requires Node ≥18. Everything else (`npx`, `npm`) rides on it. | Via nvm — see the trap below. | `node --version` → must be ≥18 |
| **Remotion + @remotion/cli + react** | Frame-based export to MP4/GIF/WebM (`../export-as-gif/`). Not global — scaffolded **per project**. | `npm install` in the scaffolded `remotion/` dir; add-ons via `npx remotion add …` | `npx remotion versions` |
| **FFmpeg / ffprobe** | **Bundled with Remotion** (`npx remotion ffmpeg …`) — *not* required just to export. Only needed for the optional `../gsap/` audio-reactive script and manual re-encodes (e.g. `-stream_loop`). | `brew install ffmpeg` | `ffmpeg -version` |
| **GSAP** | Motion engine for the live HTML animation (`../gsap/`, `../motion/`). | No install — loaded via CDN (`cdn.jsdelivr.net/npm/gsap@3.x`) or authored inline. | n/a |
| **Python + numpy** *(optional)* | Only for `../gsap/scripts/extract-audio-data.py` (audio-reactive builds). Skip unless you do audio-reactive work. | `pip install numpy` | `python3 -c "import numpy"` |

**Not needed** (common assumptions that are wrong here): **gifski** and **ImageMagick** — the export
path uses Remotion's own GIF encoder, so neither is used anywhere in the pipeline.

### The Node version trap (read this — #1 cause of a failed export)

The default login-shell Node is often **older than 18** (e.g. v16), so `npm`/`remotion` throw
`EBADENGINE` and the export dies. **Do not hardcode a personal nvm path** (e.g.
`/Users/<you>/.nvm/versions/node/v20.x/bin`) — it won't exist on another machine. Instead, discover a
node ≥18 at runtime and prefix `PATH` **per command**:

```bash
# 1. Confirm what the shell default is (this is the thing that bites you):
node --version

# 2. If it's < 18, install/select one via nvm and prefix PATH for each remotion command:
nvm install 18            # once, if not already present
NODE18="$(dirname "$(nvm which 18)")"    # portable: resolves to that node's bin dir
PATH="$NODE18:$PATH" npm install
PATH="$NODE18:$PATH" npx tsc --noEmit
PATH="$NODE18:$PATH" ./node_modules/.bin/remotion render <CompId> out/anim.mp4
```

`nvm which 18` prints the node binary path for the latest installed v18.x; `dirname` gives its `bin/`
dir. Any node ≥18 works — 18/20/22 are all fine for Remotion 4.

## Figma access

The build/QA stages read the design through a **Figma MCP server**. On a fresh machine you need one of:

- **Local Figma desktop MCP** (`mcp__Figma__*`) — requires **Dev Mode enabled** in the Figma desktop
  app; fails otherwise.
- **Hosted/plugin transport** (server ids are per-machine, e.g. `mcp__<hash>__*` or
  `mcp__plugin_figma_figma__*`) — use whichever is connected. `figma-mcp-detector` routes a raw
  figma.com link into the available MCP.

Reusable transport lessons (so you don't rediscover them per machine):

- **Heavy calls can time out.** `get_design_context` / `get_metadata` on a *whole* card/frame node can
  time out (payload too big). `get_screenshot` and `get_variable_defs` on any node stay reliable.
- **Fall back by transport, not by eyeballing.** If one server times out on the full node, the
  alternate plugin transport (`mcp__plugin_figma_figma__*`) often succeeds — `get_metadata` returns the
  child node-id tree and `get_design_context` on the full card returns the complete 1:1 spec (px,
  colors, radii, fonts, per-node styling). On the hosted server, `get_design_context` works on
  individual **leaf** nodes (avatar/icon/glyph) and returns real asset URLs.
- Asset-extraction gotchas (also in `references/knowledge.md` → Figma fidelity): gradient strokes are
  often dropped from generated CSS; Figma SVGs carry `preserveAspectRatio="none"`, so give the `<img>`
  explicit width **and** height matching the viewBox aspect or it stretches; `get_screenshot` renders
  vectors at natural size only (no upscaling) — pull true asset URLs via `get_design_context` per leaf
  node instead.

## Optional environment variables

- `GEMINI_API_KEY` / `GOOGLE_API_KEY` — only if you invoke a sibling that calls the Gemini API. **Not
  required** for the core Figma→animation→export pipeline.

## Doctor check

Copy-paste this before a run; it catches the traps above in a few seconds:

```bash
# --- environment ---
node --version                 # must be >= 18 (if not, use the nvm prefix from the trap section)
ffmpeg -version | head -1      # optional; Remotion bundles its own, only needed for the gsap audio script

# --- per project, once a remotion/ project is scaffolded ---
cd remotion
PATH="$(dirname "$(nvm which 18)"):$PATH" npx tsc --noEmit          # types compile
PATH="$(dirname "$(nvm which 18)"):$PATH" ./node_modules/.bin/remotion still <CompId> out/frame-000.png --frame=0   # one still renders
```

If the still renders and `tsc` is clean, a full `remotion render` will work. If `node --version` is
< 18 and you skipped the `PATH` prefix, expect `EBADENGINE` — that's this doc's #1 trap, not a real bug.

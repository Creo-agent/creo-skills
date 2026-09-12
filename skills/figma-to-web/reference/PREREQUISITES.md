# Prerequisites — Mandatory Toolchain

## Contents
- One-time setup (user runs before first use)
- The five hard-required tools
- Optional: Storybook
- Known install bugs and patches
- Preflight procedure (agent runs before any Figma extraction)

## One-time setup (user runs before first use)

**Do not start a build until setup passes.** After copying this skill into your skills directory,
run the setup script once from the skill root:

```bash
cd path/to/figma-to-web
python3 tools/setup_dependencies.py
```

That script:

1. Installs **Pillow** and **Playwright + Chromium** if they are missing.
2. Verifies **Python 3.9+**, **Node ≥ 24**, and **pnpm** are on your PATH.
3. Searches for a **Clay design-system checkout** (or reads `CLAY_DESIGN_SYSTEM_PATH`).
4. Writes `.f2w-setup.json` with a pass/fail report the agent can read on later sessions.

Re-run the same command whenever a check starts failing (new machine, OS update, cleared caches).

**You must complete these manual steps yourself** — the script cannot do them for you:

| Step | Action |
|---|---|
| **Clay checkout** | Clone and build Clay (see fix text from the script if not found). Set `CLAY_DESIGN_SYSTEM_PATH` if it lives outside the default search paths. |
| **Figma MCP** | Enable the official Figma MCP in Cursor or Claude Code and sign in with a Figma account that can open your target files. |
| **Node ≥ 24** | Install or switch via nvm/fnm/volta if the script reports an old Node. |

Only after `python3 tools/setup_dependencies.py` exits **0** (every `FAIL` resolved) should you
ask the agent to convert a Figma frame. The agent still verifies Figma MCP auth on the first
real `get_metadata` call — setup alone is not enough if MCP is disconnected.

To verify without installing anything (e.g. in CI):

```bash
python3 tools/setup_dependencies.py --check
```

## Why this gate exists

Every tool below actually runs inside this skill's per-section loop — that is the bar for being on
this list at all. **Installing them upfront** (not mid-build) prevents half-finished pages, silent
QA failures, and "works on my machine" surprises when someone else uses this skill.

Three third-party tools that used to be prerequisites were removed in the 2026-08-26 efficiency
uplift; their checks are now in `tools/qa_gate.py` or tagged `owner: vision` in
`web-design-rules.csv` / `HARD-RULES.md` (see `ACCURACY-GATE.md`).

## The five hard-required tools

| Tool | Why mandatory | Check | If missing |
|---|---|---|---|
| **Clay design system** (local checkout) | Source of real component code, CSS, and tokens — without it, section resolution has nothing real to build from | `tools/setup_dependencies.py` discovers the path (see `CLAY-INTEGRATION.md` — never assume a fixed path); confirms `packages/react/src/figma/connections.json` and `packages/tokens/dist/tokens.css` both exist | **Halt.** User must clone/build Clay and set `CLAY_DESIGN_SYSTEM_PATH` if needed. Do not fall back to guessing CSS from Figma pixel values. |
| **Figma MCP** (official — remote server or `plugin:figma:figma`) | Bulk programmatic extraction: `get_metadata`, `get_design_context`, `download_assets`, `get_screenshot` | Agent calls `get_metadata` on the target node during preflight | **Halt.** User must connect and authenticate Figma MCP in their editor. |
| **Python 3.9+ + Pillow** | Image compression (`SECTION-WORKFLOW.md` Step 8) and `tools/section_spec.py` | `python3 -c "import PIL"` | Run `python3 tools/setup_dependencies.py` — installs Pillow automatically. |
| **Playwright + Chromium** | QA screenshots (`SECTION-WORKFLOW.md` Step 10), `tools/qa_gate.py`, `ACCURACY-GATE.md` | Playwright import + headless Chromium launch | Run `python3 tools/setup_dependencies.py` — installs both automatically. |
| **Node ≥ 24 + pnpm** | Clay/Storybook workflows, reliable `npx` for tooling | `node --version`, `pnpm --version` | User installs/switches Node and pnpm (see setup script fix text). Agent uses the fully-qualified Node path after activation — never bare `npx` when version drift is possible. |

## Optional: Storybook

Local Storybook (`pnpm storybook`, serving `localhost:6006`) is a faster render target for real
Clay components than Chromatic, but it is **not** mandatory — `CLAY-INTEGRATION.md` falls back to
Chromatic when `localhost:6006` does not respond. Warn only; never halt.

## Known install bugs and patches

Each of these was a real, reproducible bug hit during development — apply immediately rather
than rediscovering.

**Node/`npx` version drift**: `npx`'s shebang resolution can silently pick an old Node install
(e.g. v16) lacking modern ESM/`fetch` support instead of the intended modern version (e.g. v24),
with no obvious error — commands just fail as if a dependency were missing. Patch: never rely on
bare `npx`/`node` in `.mcp.json` or any script invocation that must be reliable; use the fully
qualified path to the correct Node binary (`command -v node` after activating the right version,
or the equivalent for whatever version manager is in use).

## Preflight procedure (agent runs before any Figma extraction)

**Hard stop:** if the user asks to build and setup has never passed on this machine, run
`python3 tools/setup_dependencies.py` first and halt with the script's fix text until exit 0.
Do not scout, extract, or write HTML on a partial toolchain.

**Run every check below in order** at the start of a build session (or whenever a check that
previously passed suddenly fails):

1. Run `python3 tools/setup_dependencies.py --check`. If it exits non-zero, print the FAIL items
   and their fix text — **do not proceed.** If packages are missing and the user has not run
   setup yet, run `python3 tools/setup_dependencies.py` (with install) once, then re-check.
2. Read `.f2w-setup.json` if present; confirm `"ok": true` and Clay path is recorded.
3. Discover the Clay repo path per `CLAY-INTEGRATION.md` — confirm the two required marker files
   exist. Halt and ask if not found.
4. Call `get_metadata` on the **actual target node** (or a small node in the same file) via Figma
   MCP. Halt and ask the user to fix auth if both available server backends fail.
5. Optionally check `localhost:6006` for Storybook; if absent, note Chromatic fallback and
   continue.
6. **If more than one Figma MCP connection is available**, try the one that responds to a real
   call and use it consistently for the rest of the build. Flag discrepancies between backends —
   do not silently pick one.
7. **Once per session, not per section** — cache the preflight result (`.f2w-setup.json` plus a
   session note in the output dir). Re-running every check per section was one of the largest
   confirmed fixed costs in this skill's build traces.
8. **Check whether the output directory is covered by `.gitignore`** — run
   `git check-ignore -v <output-dir>` (or `git status` on a throwaway file written there) once,
   before the first section is built. Confirmed real case, twice independently in the same
   repo (Sep 2026): a full page build plus a follow-up fix session both ran to completion —
   edits, QA, delivery — inside a directory excluded by a repo-root `.gitignore` rule, and this
   was only discovered when the user said "commit this" at the very end, forcing a stop-and-ask
   about force-adding vs. adjusting `.gitignore` after the work was already done. **If the
   output path is gitignored, say so up front** ("this output directory is excluded by
   `.gitignore:<line>` — let me know if you want me to force-add on commit, or adjust the
   ignore rule") rather than letting it surface as a surprise at commit time.
9. Only after every hard-required check passes, proceed to `CLAY-INTEGRATION.md`'s resolution
   process.

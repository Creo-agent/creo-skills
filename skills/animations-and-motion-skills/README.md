# Animations and Motion Skills

The **single source of truth** for monday.com's animation work — every skill for turning a Figma
design into a polished, exportable web animation, gathered in one place. Each skill lives in its own
subfolder as a `SKILL.md` (router) + `PROMPT.md` (detail) + `README.md` triad.

The set is organized as **one shared library of task skills** driven by **orchestrators**:
- [`figma-to-animation`](./figma-to-animation/) — the master marketing pipeline (Figma → looping web
  animation → MP4/GIF). This is the entry point for most jobs; it routes to the task skills on demand.
- [`figma-to-animation-product-animations`](./figma-to-animation-product-animations/) — a **parallel**
  pipeline for product-UI-heavy demos with a realistic animated cursor. It shares this group's
  knowledge/tools (setup, animation-knowledge, gsap, remotion) but keeps its own nested subskills.

The task skills (`frame-building`, `motion`, `export-as-gif`, `extract-animation-from-web`,
`resize-animation`) are each usable **standalone** for their narrow task, but auto-trigger on their own
only for that task — for a full job, start from an orchestrator.

> Two skills — `gsap` and `remotion-best-practices` — are **vendored** third-party references
> (pinned snapshots; upstream noted in their `NOTICE`). Everything else is owned by the design team.

---

## Skills Index (ordered by pipeline role)

**1 · Build**
1. **frame-building** — static Figma → pixel-accurate HTML/CSS: fixed-stage scaffold · whole-frame layout · single-component 1:1 card · Figma asset/SVG download. *Consolidates the former `animation-scaffold` + `precise-figma-composition` + `figma-1to1-card`.*

**2 · Motion**
2. **motion** — GSAP motion: seamless loops · orchestrated UI entrance · marquee/carousel · word ticker. *Consolidates the former `loop-animator` + `gsap-ui-entrance` + `marquee-carousel` + `word-ticker`.*
3. **gsap** — GSAP API + motion reference (tweens, easing, stagger, timelines) · *vendored*
4. **easings** — all 30 easing functions (Sine → Bounce families): JS bodies · CSS cubic-bezier values · pick-by-use-case table · GSAP shorthands
5. **ds-section-animations** — native-API section motion (mouse/scroll parallax, marquee) for design-system stories (not GSAP; niche)

**3 · Capture / transform**
6. **extract-animation-from-web** — extract an animated section from a live site into one self-contained HTML
7. **resize-animation** — reflow an existing animation to new sizes/aspect ratios; swap images

**4 · Export**
8. **export-as-gif** — render an animation to GIF/MP4/WebM via Remotion (frame-based, deterministic)
9. **remotion-best-practices** — Remotion domain rules (fonts, timing, measuring-text, gifs, sequencing…) · *vendored*

**5 · Orchestrators**
10. **figma-to-animation** — master marketing pipeline: index → analyze → build → static QA (≥95) → stitch → animate → animation QA → connect → export → validate
11. **figma-to-animation-product-animations** — parallel product-UI pipeline (planning → recreation → design QA → animation ⇄ cursor → animation QA); nested subskills, shares this group's knowledge/tools

---

## Registry

| Skill | Purpose | Key files | Owner | Last updated |
|---|---|---|---|---|
| [`frame-building`](./frame-building/) | Static Figma → pixel-accurate HTML/CSS (scaffold · layout · 1:1 card · assets). *Was animation-scaffold + precise-figma-composition + figma-1to1-card.* | SKILL.md · PROMPT.md · README.md · references/ (scaffold · layout · card · figma-notes) | Elior Siegelwachs | 2026-07-14 |
| [`motion`](./motion/) | GSAP motion (loops · UI entrance · marquee · word ticker). *Was loop-animator + gsap-ui-entrance + marquee-carousel + word-ticker.* | SKILL.md · PROMPT.md · README.md · references/ (loops · ui-entrance · marquee · word-ticker) | Elior Siegelwachs | 2026-07-14 |
| [`gsap`](./gsap/) | GSAP API + motion reference. *Vendored (heygen-com/hyperframes).* | SKILL.md · PROMPT.md · README.md · NOTICE | Elior Siegelwachs | 2026-07-14 |
| [`easings`](./easings/) | All 30 easing functions (Sine · Quad · Cubic · Quart · Quint · Expo · Circ · Back · Elastic · Bounce) — JS bodies · CSS cubic-bezier values · pick-by-use-case table · GSAP shorthands · decision tree for when to use this skill. Source: easings.net. | SKILL.md · PROMPT.md · README.md · references/functions.md | Elior Siegelwachs | 2026-07-15 |
| [`ds-section-animations`](./ds-section-animations/) | Native-API section motion (parallax, marquee) for DS stories. | SKILL.md · PROMPT.md · README.md | Elior Siegelwachs | 2026-07-14 |
| [`extract-animation-from-web`](./extract-animation-from-web/) | Extract an animated section from a live site into one self-contained HTML. | SKILL.md · PROMPT.md · README.md · references/ · scripts/ | Elior Siegelwachs | 2026-07-14 |
| [`resize-animation`](./resize-animation/) | Reflow an animation to new sizes/aspect ratios; swap images. | SKILL.md · PROMPT.md · README.md | Elior Siegelwachs | 2026-07-14 |
| [`export-as-gif`](./export-as-gif/) | Render to GIF/MP4/WebM via Remotion (frame-based, deterministic). | SKILL.md · PROMPT.md · README.md | Elior Siegelwachs | 2026-07-14 |
| [`remotion-best-practices`](./remotion-best-practices/) | Remotion domain rules. *Vendored (remotion-dev/skills).* | SKILL.md · PROMPT.md · README.md · rules/ · NOTICE | Elior Siegelwachs | 2026-07-14 |
| [`figma-to-animation`](./figma-to-animation/) | Master marketing pipeline orchestrator (per-frame QA gates, deterministic loops). Tools/prereqs: `references/setup.md`; motion knowledge: `references/animation-knowledge.md`. | SKILL.md · PROMPT.md · README.md · pipeline/ · references/ (knowledge · animation-knowledge · rubric · providers · setup) · workflows/ | Elior Siegelwachs | 2026-07-14 |
| [`figma-to-animation-product-animations`](./figma-to-animation-product-animations/) | Parallel product-UI orchestrator with realistic cursor; nested subskills, shares this group's env. | SKILL.md · 6 nested subskills | Elior Siegelwachs | 2026-07-14 |

---

## Prerequisites

### Tools (Node, Remotion, FFmpeg, GSAP…)

Before running the pipeline (or any Remotion export), check the tools it needs — Node ≥18, Remotion,
FFmpeg, GSAP, optional numpy — and their install/verify commands in
[`figma-to-animation/references/setup.md`](./figma-to-animation/references/setup.md). The most common
failure is a shell Node < 18 (`EBADENGINE` at export); setup.md shows the portable fix.

### Figma skills (install these — mandatory for MCP + design reading)

Several skills in this group use the **Figma MCP** to read designs. Two external skill packages
dramatically improve how the MCP reads and implements your designs — install them alongside this
group:

| Skill package | What it adds | Install from |
|---|---|---|
| **figma-implement-design** | Guides the LLM to faithfully implement Figma designs — correct extraction of layout, spacing, typography, component hierarchy | [openai/skills → .curated/figma-implement-design](https://github.com/openai/skills/tree/main/skills/.curated/figma-implement-design) |
| **Figma MCP server guide skills** | Official Figma-authored skill set for working with the Figma MCP server — correct tool usage, reading design context, handling tokens | [figma/mcp-server-guide → skills/](https://github.com/figma/mcp-server-guide/tree/main/skills) |

These are **not optional** when you need pixel-accurate output. Without them the LLM may misread
spacing, lose component context, or skip design tokens.

### Figma file quality (design your files for better LLM output)

The quality of the LLM's output is directly proportional to the quality of the Figma file it reads.
These four practices have the highest impact — each one makes a measurable difference in the
`frame-building` and product-recreation stages:

#### Auto-layout
Use auto-layout on every frame and component. Auto-layout exposes **gap, padding, alignment, and
direction** as named properties the MCP can read precisely. Without it the LLM sees only absolute
`x/y` coordinates and has to reverse-engineer spacing — resulting in brittle CSS that breaks on
slight size changes.

**Do:** nest groups inside auto-layout frames, set explicit gap/padding values.  
**Don't:** use free-form frames with manually positioned elements when a layout relationship exists.

#### Style variables (design tokens)
Bind colors, font sizes, spacing, radii, and opacity to **Figma variables** (or legacy styles).
When they're bound, the MCP returns named tokens (e.g. `color/brand/blue-600`) that map cleanly to
CSS custom properties or a design system. When they're raw values, every hex and px number looks
arbitrary and the LLM can't tell intentional values from accidental ones.

**Do:** use a variable collection for all color, spacing, and typography decisions.  
**Don't:** hand-enter `#1F76C2` directly when `color/brand/primary` exists.

#### Variants
Group component states (default, hover, active, disabled, loading, error) as **Figma variants** on
a component set. Variants let the LLM understand the full state model of a component — critical for
the `product-animation` stage, where the cursor interacts with UI elements that change state. Without
variants, animated states must be inferred from separate frames with no structural relationship.

**Do:** use a single component set with a `State` property for all interactive states.  
**Don't:** create separate components named `Button-hover`, `Button-active` without a variant
structure — they look like unrelated components to the MCP.

#### Assets (images, icons, SVGs)
Export assets from Figma with **descriptive names** and at the correct scale. The MCP can download
assets by node — but only if it can identify the right node. Unnamed or poorly named layers (e.g.
`Rectangle 47`) produce ambiguous results. Named assets (`hero-background`, `icon-checkmark`)
resolve directly.

**Do:** name every image/icon layer clearly; mark exportable assets with an export setting in Figma;
use SVG for icons and vector art (not PNG).  
**Don't:** leave Figma's auto-generated layer names on assets the pipeline will download.

## Install

Each skill installs independently (sparse checkout of its folder):

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/animations-and-motion-skills/<skill-name>
git checkout
cp -r skills/animations-and-motion-skills/<skill-name> ~/.claude/skills/
```

To install the whole pipeline at once, `git sparse-checkout set skills/animations-and-motion-skills` and copy every
subfolder. The master `figma-to-animation` references its engine skills as siblings, so install them
together (or the whole `animations-and-motion-skills/` group) for the full pipeline.

## Entry point
For a full Figma→animation job: load [`figma-to-animation/SKILL.md`](./figma-to-animation/SKILL.md),
then follow its `PROMPT.md`. For a single task, load that skill's `SKILL.md` → `PROMPT.md`.

> To add or edit a skill here: keep the `SKILL.md`+`PROMPT.md`+`README.md` triad, update this
> registry and the top-level `skills/README.md`, set your name as Owner / Last updated by, and commit
> with `Update skill registry: animations-and-motion-skills/<skill-name> — <action> by <name>`.

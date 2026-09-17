# Design Team Skills

This folder contains Claude Code skills built by and for the monday.com marketing design team.  
Each skill lives in its own named subfolder and is self-contained.

---

## Agent: How to Use This Page

> **Read this section if a user says anything like:**  
> "Install the skills in this repo", "Which skills are available?", "Set up a skill", "Install a skill from this page"

When triggered, follow these steps exactly:

### Step 1 — Show the available skills

Present the user with the list of skills from the Skills Index below. Show each skill's name and one-sentence purpose. Ask:

> "Here are the available skills in this repo. Which one(s) would you like to install?
>
> 1. **monday-presentation** — Generate branded monday.com HTML slide decks (zero dependencies)
> 2. **figma-resize** — Resize a Figma Master KV into standard ad and social media formats
> 3. **figma-modify** — Modify, tweak, and adapt existing Figma designs via the Figma MCP
> 4. **extract-animation-from-web** — Extract an animated section from a live website into one self-contained HTML file
> 5. **loop-animator** — Turn a static/scroll animation into a smooth auto-playing loop (GSAP)
> 6. **export-as-gif** — Render an animation to GIF/MP4/WebM via Remotion (asks for size/format/limit first)
> 7. **precise-figma-composition** — Reproduce a Figma frame's layout pixel-accurately from its real coordinates
> 8. **resize-animation** — Reframe an existing animation to new sizes/aspect ratios and swap its images
>
> Type a number, a name, or 'all' to install everything."

### Step 2 — Ask for the owner name

Before installing, ask:

> "What's your name? I'll register you as the owner of this skill installation."

### Step 3 — Install the skill

For each selected skill, run:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Sparse-clone only the requested skill folder
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/<skill-name>
git checkout

# Copy to Claude skills directory
cp -r skills/<skill-name> ~/.claude/skills/
echo "✓ Installed <skill-name> to ~/.claude/skills/<skill-name>"
```

Replace `<skill-name>` with the actual folder name (e.g. `figma-resize`).

### Step 4 — Confirm and update the registry

After installing, tell the user:

> "Done! **<skill-name>** is installed. You can use it by typing `/<skill-name>` in Claude Code, or by describing what you want in natural language — see the Triggers in the index below."

Then update this README file (skills/README.md) in the repo:
- Set **Owner** for the skill to the name the user gave in Step 2 (only if Owner is currently blank or "—")
- Set **Last updated by** and **Last updated** to the user's name and today's date

---

## Ownership Rules (for Agents)

When a skill is **first installed** by a user: set the **Owner** field to their name.  
When a skill's files are **updated** (SKILL.md, PROMPT.md, or any other file changed): update **Last updated by** and **Last updated** to the person making the change.  
Owner only changes if the original owner explicitly asks to transfer ownership.  
Always commit the README change with the message: `Update skill registry: <skill-name> — <action> by <name>`

---

## Skills Index

---

### `monday-presentation`

| Field | Value |
|---|---|
| **Folder** | [`skills/monday-presentation/`](./monday-presentation/) |
| **Purpose** | Generates professional, single-file monday.com branded HTML presentations with zero external dependencies — responsive 16:9 slides with keyboard navigation, dark/light themes, and official monday design tokens. |
| **Triggers** | "Create a presentation", "Build slides", "Make a deck", "Generate a slide deck", "Create monday-branded slides", "Make a presentation about..." |
| **Keywords** | `presentation`, `slides`, `deck`, `slide deck`, `keynote`, `HTML slides`, `monday branded`, `monday presentation` |
| **Outputs** | A single self-contained `.html` file with inline CSS/JS. Supports dark (default) and light themes via `data-theme`. No external scripts or assets required. |
| **Dependencies** | No external services required. Works in Claude Code CLI/Desktop (full features), claude.ai Projects (falls back to text questions), and Claude API (user saves code block manually). |
| **Key files** | `SKILL.md` · `PROMPT.md` · `RECIPES.md` · `DESIGN_SYSTEM.md` · `slide-templates.html` |
| **Entry point** | Load `SKILL.md`, then follow `PROMPT.md` |
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-02 |

---

### `figma-resize`

| Field | Value |
|---|---|
| **Folder** | [`skills/figma-resize/`](./figma-resize/) |
| **Purpose** | Takes a Master Key Visual (KV) frame in Figma and produces native frame variants at standard ad and social media sizes, following the layout rules of the Resizing Nano Banana plugin. |
| **Triggers** | "Resize this KV to all banner sizes", "Create the DV sizes from this master", "Make the story format", "Generate all ad formats", "Resize to 300×250", "Adapt this to social sizes" |
| **Keywords** | `resize`, `KV`, `master`, `banner sizes`, `ad formats`, `DV`, `story`, `social sizes`, `all sizes`, `create variants` |
| **Outputs** | Native Figma frames at: Billboard (970×250), Leaderboard (728×90), Medium Rectangle (300×250), Half Page (300×600), Skyscraper (160×600), Story/Reel (1080×1920), Facebook Feed (1080×1350), LinkedIn Feed (1200×1200) |
| **Dependencies** | Figma MCP plugin connected · `figma:figma-use` skill installed · A Figma URL pointing to the Master KV frame |
| **Entry point** | Load `SKILL.md`, then follow `PROMPT.md` |
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-02 |

---

### `figma-modify`

| Field | Value |
|---|---|
| **Folder** | [`skills/figma-modify/`](./figma-modify/) |
| **Purpose** | Modify, tweak, and adapt existing Figma designs — text edits, color updates, layout restructuring, resizing to new formats, adding/removing elements. |
| **Triggers** | "Change [something] in this frame", "Modify this design", "Tweak the colors", "Update the text", "Resize this to mobile", "Adapt this layout", "Fix the spacing", "Move this element", "Swap the background" |
| **Keywords** | `change`, `modify`, `tweak`, `adjust`, `resize`, `adapt`, `update`, `edit`, `fix`, `move`, `swap`, `replace`, `reformat` |
| **Outputs** | Modified Figma frames in-place or as duplicates, with visual screenshots for approval at each step |
| **Dependencies** | Figma MCP plugin connected · Figma OAuth authenticated · `figma:figma-use` skill loaded before every `use_figma` call |
| **Entry point** | Load `SKILL.md`, then follow `PROMPT.md` |
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-02 |

---

### `extract-animation-from-web`

| Field | Value |
|---|---|
| **Folder** | [`skills/extract-animation-from-web/`](./extract-animation-from-web/) |
| **Purpose** | Extracts a single animated section from a live website into one self-contained HTML file — its markup, the CSS that styles it, the JS that animates it (GSAP/ScrollTrigger/Splide), and all its images. First stage of the animation pipeline. |
| **Triggers** | "Pull the floating-cards animation off monday.com/crm into its own file", "Rip Linear's hero into one html", "Grab this section incl. images and gsap so it runs offline", "Reproduce the scroll animation from this URL as an isolated page" |
| **Keywords** | `extract`, `grab`, `rip`, `isolate`, `reproduce`, `standalone`, `offline copy`, `section`, `hero`, `animation from a site` |
| **Outputs** | A single self-contained `.html` (+ local `images/`) reproducing the section's look and motion. |
| **Dependencies** | `curl` and `python3` (for `scripts/extract_css.py`); browser tools for live-DOM fallback. Library (e.g. GSAP) loaded from CDN in the output. |
| **Key files** | `SKILL.md` · `PROMPT.md` · `references/gotchas.md` · `scripts/extract_css.py` |
| **Entry point** | Load `SKILL.md`, then follow `PROMPT.md` |
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-12 |

---

### `loop-animator`

| Field | Value |
|---|---|
| **Folder** | [`skills/loop-animator/`](./loop-animator/) |
| **Purpose** | Turns a static composition or a scroll/hover-triggered web animation into a smooth, auto-playing looping animation in HTML/CSS/JS with GSAP — with no jump cut at the loop boundary. |
| **Triggers** | "Make these cards loop instead of on scroll", "Reveal, hold, then reset smoothly and repeat — no hard cut", "Turn this hover effect into an autoplay loop for a kiosk", "Add a seamless breathing loop" |
| **Keywords** | `loop`, `auto-play`, `repeat`, `run continuously`, `seamless`, `yoyo`, `stagger`, `no jump cut`, `autoplay` |
| **Outputs** | An HTML/CSS/JS animation on a single GSAP timeline (`repeat: -1`, `yoyo`), with ramping stagger, collapse-to-point, and cross-fades. |
| **Dependencies** | GSAP (from CDN). Pairs with the `gsap` skill. |
| **Key files** | `SKILL.md` · `PROMPT.md` |
| **Entry point** | Load `SKILL.md`, then follow `PROMPT.md` |
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-12 |

---

### `export-as-gif`

| Field | Value |
|---|---|
| **Folder** | [`skills/export-as-gif/`](./export-as-gif/) |
| **Purpose** | Renders an animation into a real GIF / MP4 / WebM by rebuilding it in Remotion (frame-based, deterministic). Asks for the target size, resolution, format, and any size limit first, then hits it. |
| **Triggers** | "Turn this html animation into a gif for Slack under 5mb", "Render my gsap loop as an mp4", "Make a looping gif of this, 1080×1080", "Get me a downloadable webm of this motion" |
| **Keywords** | `gif`, `mp4`, `webm`, `render`, `export`, `video file`, `downloadable`, `shareable clip`, `stitch frames` |
| **Outputs** | A Remotion project plus the rendered `.gif`/`.mp4`/`.webm` at the requested dimensions, fps, and size. |
| **Dependencies** | Node.js + npm (Remotion installs its own headless renderer). Pairs with the `remotion-best-practices` skill. |
| **Key files** | `SKILL.md` · `PROMPT.md` |
| **Entry point** | Load `SKILL.md`, then follow `PROMPT.md` |
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-12 |

---

### `precise-figma-composition`

| Field | Value |
|---|---|
| **Folder** | [`skills/precise-figma-composition/`](./precise-figma-composition/) |
| **Purpose** | Reproduces a Figma frame's layout pixel-accurately in code by pulling each node's exact coordinates from Figma and scaling them to the target canvas — instead of eyeballing from a screenshot. Best for scatter/overlay layouts. |
| **Triggers** | "Match this composition exactly to my figma <link>", "Place these floating elements pixel-perfect like the figma", "My eyeballed positions are off — pull the real coords from figma", "Match the card stacking from figma" |
| **Keywords** | `figma`, `pixel perfect`, `match the figma`, `exact positions`, `scatter layout`, `overlap`, `source of truth`, `right coordinates` |
| **Outputs** | Absolute-positioned HTML/CSS, or a coordinates array for Remotion, whose geometry equals the Figma frame scaled to the target. |
| **Dependencies** | Figma MCP connected · a Figma design URL (path `/design/`) pointing at the frame/node. |
| **Key files** | `SKILL.md` · `PROMPT.md` · `references/figma-notes.md` |
| **Entry point** | Load `SKILL.md`, then follow `PROMPT.md` |
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-12 |

---

### `resize-animation`

| Field | Value |
|---|---|
| **Folder** | [`skills/resize-animation/`](./resize-animation/) |
| **Purpose** | Adapts an existing animation to a different canvas size / aspect ratio — and/or swaps its images — to produce format variants (square, portrait, landscape, banner, story) without rebuilding the motion. Asks for the target size(s) first. |
| **Triggers** | "Make a portrait 1080×1920 version for stories", "Reframe this square animation to landscape", "I need story, feed, and reel versions", "Swap the images in this animated layout and adjust the sizes" |
| **Keywords** | `resize`, `reframe`, `reflow`, `portrait`, `square`, `vertical`, `9:16`, `1080x1920`, `story`, `reel`, `ad size`, `variants`, `swap images` |
| **Outputs** | The same animation re-placed for the new frame(s) — one or several format variants — with the motion preserved and re-verified. |
| **Dependencies** | An existing animation (HTML/GSAP or a Remotion composition). Pairs with `precise-figma-composition` and `export-as-gif`. |
| **Key files** | `SKILL.md` · `PROMPT.md` |
| **Entry point** | Load `SKILL.md`, then follow `PROMPT.md` |
| **Owner** | Elior Siegelwachs |
| **Last updated by** | Elior Siegelwachs |
| **Last updated** | 2026-07-12 |

### `figma-asset-localization`

| Field | Value |
|---|---|
| **Folder** | [`skills/figma-asset-localization/`](./figma-asset-localization/) |
| **Purpose** | End-to-end Figma asset localization pipeline — translates, layout-corrects, and QAs Figma banner assets for target locales (de-DE, pt-BR, fr-FR, es-MX, ja-JP). Ships with per-locale glossaries and fix-method references. |
| **Triggers** | Board subitems where System Status = Idle or Review Status = Re-run Requested. Do not use for email/landing-page/ad-copy localization. |
| **Keywords** | `localization`, `localize`, `translate`, `de-DE`, `pt-BR`, `fr-FR`, `es-MX`, `ja-JP`, `glossary`, `layout fix` |
| **Dependencies** | Runs inside its origin hub (n8n board triggers + `domains/localization/…` knowledge/required-files). **Cataloged as reference/external — not wired to run inside Creo.** |
| **Key files** | `SKILL.md` · `glossaries/` (5 locales, md+csv) · `references/fix-methods/` |
| **Entry point** | Load `SKILL.md` |
| **Owner** | Localization team (origin hub) |
| **Status** | Reference / external — documented here, not Creo-runnable |
| **Last updated** | 2026-09-17 |

---

### `campaign-variant-generator`

| Field | Value |
|---|---|
| **Folder** | [`skills/campaign-variant-generator/`](./campaign-variant-generator/) |
| **Purpose** | Reference for the Campaign Variant Generator Figma plugin (Figma plugin → n8n → Claude → 7 variant sets → in-plugin pixel-fit → CM picks/applies). Documents the architecture, not an executable pipeline. |
| **Triggers** | Questions about how variant generation works, the plugin→n8n→Claude flow, or debugging variant generation. |
| **Keywords** | `variant`, `campaign variant`, `headline`, `CTA`, `n8n`, `HMAC`, `pixel-fit`, `Figma plugin` |
| **Dependencies** | Runs via the Figma plugin — **not directly executable.** Cataloged as reference. |
| **Key files** | `SKILL.md` |
| **Entry point** | Load `SKILL.md` |
| **Owner** | michael@monday.com (Michael Eizenstat) |
| **Status** | Reference — plugin-hosted, not Creo-runnable |
| **Last updated** | 2026-09-17 |

---

> To add a new skill: create a subfolder with `SKILL.md` + `PROMPT.md` + `README.md`, add a row to this index with your name as Owner, and commit with message `Update skill registry: <skill-name> — added by <name>`.

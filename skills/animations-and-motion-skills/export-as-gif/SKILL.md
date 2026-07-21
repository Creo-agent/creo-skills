---
name: export-as-gif
description: |
  WHAT: Render an animation into a real saved file — GIF, MP4, or WebM. Two pipelines: (1) Remotion (frame-based React, best for complex motion with components), or (2) Playwright frame-capture (simpler, best for self-contained HTML/CSS/GSAP animations). Asks for target size/resolution/format/size-limit first.
  TRIGGERS: "export / render / convert / turn this into a gif or mp4", making a GIF, rendering animation to video, getting a downloadable clip of a CSS/HTML/GSAP animation, stitching frames into a gif, producing a file sized for Slack/social/ads/deck (e.g. under 5mb, 15fps).
  SUB-SKILL: figma-to-animation orchestrator routes here for its export stage. Usable standalone whenever the deliverable is an actual video/GIF file on disk (not a live web animation).
  NOT FOR: capturing an animation off a live website → use extract-animation-from-web/. Editing/trimming an existing video clip. Resizing or reorienting → use resize-animation/. Generating static images. Building slide decks. Remotion code questions → use remotion-best-practices/.
---

# Export as GIF / MP4

Two capture pipelines — pick the right one:

| | Remotion | Playwright frame-capture |
|---|---|---|
| **Source** | React components | Self-contained HTML/CSS/GSAP |
| **When to use** | Complex motion, component reuse, server render | Quick iteration on a single HTML file |
| **Font requirement** | `@remotion/google-fonts` | Embed fonts as base64 (see `animation-scaffold` §7) |
| **Setup** | npm project scaffold | `playwright` + `ffmpeg` only |

## Pipeline A — Remotion

Render an animation to a real GIF/MP4/WebM by rebuilding it in Remotion, where every frame
is a pure function of time — so renders are deterministic and loops are seamless. Load the
`remotion-best-practices` skill for library rules; this skill is the porting + render recipe.

### When This Activates

- "Turn this html animation into a gif for Slack, under 5mb"
- "Render my gsap loop as an mp4"
- "Make a looping gif of the square animation, 1080×1080"
- "Get me a downloadable webm of this motion"

Keywords: `gif`, `mp4`, `webm`, `render`, `export`, `video file`, `downloadable`,
`shareable clip`, `stitch frames`.

### What Remotion Does

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

### Entry Point

Load **PROMPT.md** for the output-spec questions, project scaffold, GSAP→Remotion easing
cheat-sheet, the triangle-wave *and* forward-loop recipes, font/pseudo-element gotchas, and
the GIF size-tradeoff levers.

---

## Pipeline B — Playwright frame-capture (HTML/GSAP)

For a self-contained HTML/CSS/GSAP animation, skip Remotion entirely. This pipeline is
simpler, faster to iterate on, and requires no React.

**Prerequisites:** `npm install playwright` (in the project folder) + `ffmpeg` on PATH.

### Capture script template (`capture.mjs`)

```js
/**
 * capture.mjs — Record animation.html → PNG frames → MP4 + GIF
 * Node ≥18; run: node capture.mjs
 */
import { chromium } from 'playwright';
import { execSync } from 'child_process';
import { mkdirSync, rmSync, existsSync, createReadStream, statSync, readFileSync } from 'fs';
import { createServer } from 'http';
import { extname, join, resolve } from 'path';

const __dirname = decodeURIComponent(new URL('.', import.meta.url).pathname);
const PROJ_DIR   = resolve(__dirname);
const FRAMES_DIR = join(PROJ_DIR, 'frames');
const HTML_FILE  = 'animation.html';   // ← set this per-project

const LOOP_DURATION = 6.0;             // seconds — match your mainTl duration
const FPS           = 30;
const TOTAL_FRAMES  = Math.round(LOOP_DURATION * FPS);
const CANVAS_SIZE   = 1200;            // px — match your HTML stage size

const MIME = {
  '.html':'text/html', '.js':'application/javascript', '.css':'text/css',
  '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg',
  '.gif':'image/gif', '.svg':'image/svg+xml', '.woff2':'font/woff2',
};

// 1. Local HTTP server (file:// is often blocked in headless)
const server = createServer((req, res) => {
  const filePath = join(PROJ_DIR, decodeURIComponent(req.url.split('?')[0].replace(/^\//,'')));
  try {
    const stat = statSync(filePath);
    const mime = MIME[extname(filePath).toLowerCase()] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': mime, 'Content-Length': stat.size,
      'Access-Control-Allow-Origin': '*' });
    createReadStream(filePath).pipe(res);
  } catch { res.writeHead(404); res.end('Not found'); }
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const PORT = server.address().port;
const BASE = `http://127.0.0.1:${PORT}`;

// 2. Inline GSAP from local file (avoids CDN dependency in headless)
let html = readFileSync(join(PROJ_DIR, HTML_FILE), 'utf8');
const gsapSrc = readFileSync(join(PROJ_DIR, 'assets', 'gsap.min.js'), 'utf8');
html = html.replace('<script src="assets/gsap.min.js"></script>', `<script>${gsapSrc}</script>`);
html = html.replace(/src="assets\//g, `src="${BASE}/assets/`);

// 3. Launch browser
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const ctx = await browser.newContext({
  viewport: { width: CANVAS_SIZE, height: CANVAS_SIZE },
  deviceScaleFactor: 1, baseURL: BASE,
});
const page = await ctx.newPage();
page.on('pageerror', e => console.warn('page error:', e.message));

await page.setContent(html, { waitUntil: 'domcontentloaded', timeout: 30000 });
await page.waitForTimeout(2500);   // let fonts/images settle

// 4. Wait for timeline (animation-scaffold §8 pattern)
await page.waitForFunction(() => window.mainTl !== null, { timeout: 10000 });
console.log('mainTl ready, duration:', await page.evaluate(() => window.mainTl.duration()));

// 5. QA stills before full capture
for (const t of [1.5, 3.0, 5.0]) {
  await page.evaluate(t => { window.mainTl.pause(); window.mainTl.seek(t, true); }, t);
  await page.screenshot({ path: join(PROJ_DIR, `qa-t${t}s.png`),
    clip: { x:0, y:0, width: CANVAS_SIZE, height: CANVAS_SIZE } });
}

// 6. Frame-by-frame capture
if (existsSync(FRAMES_DIR)) rmSync(FRAMES_DIR, { recursive: true });
mkdirSync(FRAMES_DIR, { recursive: true });

for (let f = 0; f < TOTAL_FRAMES; f++) {
  await page.evaluate(t => {
    window.mainTl.pause();
    window.mainTl.seek(t, true);
  }, f / FPS);
  await page.screenshot({
    path: join(FRAMES_DIR, `frame-${String(f).padStart(4,'0')}.png`),
    clip: { x:0, y:0, width: CANVAS_SIZE, height: CANVAS_SIZE },
  });
  if (f % 30 === 0) console.log(`  frame ${f}/${TOTAL_FRAMES}`);
}

await browser.close();
server.close();

// 7. MP4 (h264, high quality)
execSync(
  `ffmpeg -y -framerate ${FPS} -i "${FRAMES_DIR}/frame-%04d.png" ` +
  `-vf "scale=${CANVAS_SIZE}:${CANVAS_SIZE},format=yuv420p" ` +
  `-c:v libx264 -crf 18 -preset slow -movflags +faststart animation.mp4`,
  { stdio: 'inherit' }
);

// 8. GIF (15fps, 720px wide, lanczos + palette dithering)
execSync(
  `ffmpeg -y -framerate ${FPS} -i "${FRAMES_DIR}/frame-%04d.png" ` +
  `-vf "fps=15,scale=720:-1:flags=lanczos,` +
    `split[s0][s1];[s0]palettegen=max_colors=128[p];` +
    `[s1][p]paletteuse=dither=bayer:bayer_scale=5" ` +
  `animation.gif`,
  { stdio: 'inherit' }
);
```

### GIF quality levers

| Want | Adjustment |
|---|---|
| Smaller file | Lower `max_colors` (64), raise `fps` to 10 |
| Better color depth | Raise `max_colors` (256), use `dither=floyd_steinberg` |
| Larger canvas | Change `scale=1080:-1` (but expect bigger file) |
| Smooth dark gradients | `dither=sierra2_4a` instead of `bayer` |

### Font FOUT in headless — embed fonts as base64

If the first few frames show the wrong font then snap to the correct one, the browser is racing with font HTTP requests. Fix: embed fonts as inline `@font-face` base64 data URIs with `font-display: block` — see `animation-scaffold` §7 for the full recipe. This is **mandatory** for any animation that uses Google Fonts or external font URLs.

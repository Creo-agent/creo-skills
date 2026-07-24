---
name: animation-scaffold
description: >-
  Scaffold a fresh HTML/CSS/JS animation project from scratch — the export-ready starting point for a social/marketing/kiosk motion piece. Go-to skill at the very START of a new animation, whenever the user says "start a new animation", "set up the HTML/CSS/JS from scratch", "blank canvas / stage to animate on", "a new 1080 square (or portrait/landscape) animation", "let's do another project like this one", or has nothing yet and wants the boilerplate to build on. Produces a single self-contained index.html with a fixed pixel-exact stage (e.g. 1080×1080), a JS viewport-fit scaler that never changes the true render size, GSAP loaded, a fonts+images load-gate before measuring, and an empty build() hook. Then hands off to the placement/animation/render skills. Do NOT use when a stage already exists (skip straight to precise-figma-composition / loop-animator), for grabbing an animation off a website (extract-animation-from-web), or for React/Remotion-first work (export-as-gif scaffolds that).
---

# Animation Scaffold (fixed stage + scaler + GSAP)

The reliable starting point for an export-bound web animation: a **fixed, pixel-exact
stage** (so the render is deterministic at any screen size) plus everything the follow-on
skills expect — GSAP, a fonts+images load-gate, and a `build()` hook. Get this right once
and every later skill slots in cleanly.

## When This Skill Activates

- "Start a new animation from scratch — a 1080 square"
- "Set up the HTML/CSS/JS so I have a stage to animate on"
- "Let's do another project like the CRM one"
- "Give me the blank canvas / boilerplate for a portrait story animation"

Keywords: `new animation`, `from scratch`, `scaffold`, `boilerplate`, `blank stage`,
`1080 square`, `portrait`, `landscape`, `starting point`.

## What This Skill Does

1. Asks for (or infers) the canvas — square 1080², portrait 1080×1920, landscape, custom —
   and sets `STAGE_W`/`STAGE_H` up front.
2. Emits one self-contained `index.html`: a fixed pixel-exact `.stage`, a JS scaler that
   only *visually* fits it to the viewport (never changing the true render size), GSAP from
   CDN, a fonts+images load-gate, and an empty `build()` hook.
3. Explains converting `getBoundingClientRect` back to stage-local coords (undo the scaler).
4. Verifies over a local HTTP server (`file://` is blocked in preview) by seeking the timeline.
5. Hands off: `precise-figma-composition` (place) → `loop-animator` (animate) →
   `marquee-carousel` / `gsap-ui-entrance` → `export-as-gif` → `resize-animation`.

---

# Animation scaffold (fixed stage + scaler + GSAP)

The reliable starting point for an export-bound web animation: a **fixed, pixel-exact
stage** (so the render is deterministic at any screen size) plus everything the follow-on
skills expect — GSAP, a load-gate, and a `build()` hook. Get this right once and every later
skill (`precise-figma-composition`, `loop-animator`, `marquee-carousel`, `export-as-gif`)
slots in cleanly.

## 0. Pick the canvas first
Ask (or infer) the target so the stage size is right from the start — it drives everything
downstream and is annoying to change later:
- **Square 1080×1080** (feed posts), **Portrait 1080×1920** (stories/reels), **Landscape
  1920×1080**, or a custom size.
Set `STAGE_W` / `STAGE_H` accordingly. Keep the true render at these exact pixels; the
scaler only *fits it to the screen for preview* — it must never alter the real size.

## 1. The scaffold — one self-contained file
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Animation</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; }
    body { font-family: 'Figtree', sans-serif; background: #111; min-height: 100vh; overflow: hidden; }
    img { max-width: 100%; display: block; }

    /* View-only scaler: fits the fixed stage to the viewport. Does NOT change the
       true render size. scale() needs a unitless number, so JS sets it (below). */
    .stage-scaler {
      width: var(--stage-w); height: var(--stage-h);
      position: fixed; top: 50%; left: 50%;
      transform-origin: center center;
      transform: translate(-50%, -50%) scale(1);
    }
    /* The pixel-exact stage — everything animates inside here. */
    .stage {
      width: var(--stage-w); height: var(--stage-h);
      position: relative; overflow: hidden; background: #000;
    }
    :root { --stage-w: 1080px; --stage-h: 1080px; }  /* ← set your canvas */
  </style>
</head>
<body>
  <div class="stage-scaler">
    <div class="stage">
      <!-- placement goes here (see precise-figma-composition) -->
    </div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <script>
    const STAGE_W = 1080, STAGE_H = 1080;  // keep in sync with --stage-w/h

    /* Fit the fixed stage into any viewport (preview only). */
    (function () {
      const scaler = document.querySelector('.stage-scaler');
      const fit = () => {
        const s = Math.min(1, window.innerWidth / STAGE_W, window.innerHeight / STAGE_H);
        scaler.style.transform = `translate(-50%, -50%) scale(${s})`;
      };
      fit();
      window.addEventListener('resize', fit);
    })();

    window.addEventListener('DOMContentLoaded', () => {
      const stage = document.querySelector('.stage');
      if (!stage) return;

      /* Timing tunables live here as named constants (loop-animator fills these in). */

      const build = () => {
        // Build the GSAP timeline here once layout is settled.
        // → loop-animator (reveal loop) / marquee-carousel (scrolling rows).
      };

      /* Load-gate: measure only AFTER images + fonts settle, or getBoundingClientRect
         and text widths are wrong. */
      Promise.all([
        ...Array.from(stage.querySelectorAll('img'))
          .filter(img => !img.complete)
          .map(img => new Promise(res => { img.onload = img.onerror = res; })),
        document.fonts?.ready ?? Promise.resolve(),
      ]).then(build);
    });
  </script>
</body>
</html>
```

## 2. Why the fixed stage matters
Absolute positions/sizes inside `.stage` are in true render pixels — so what you preview is
exactly what `export-as-gif` renders. The scaler only shrinks the *view*; because it wraps
the stage, `getBoundingClientRect` returns scaled screen px — divide by the scaler factor
(`stageRect.width / STAGE_W`) whenever you need stage-local coordinates (e.g. anchoring a
transform-origin — see `loop-animator`'s emerge-from-point).

## 3. Serve & verify
`file://` is often blocked in the in-app preview, and the folder may contain spaces — serve
over HTTP:
```bash
python3 -m http.server 8753    # then open http://localhost:8753/index.html
```
Verify deterministically by grabbing the timeline and seeking, not by screenshotting a live
play (headless capture lags):
```js
const tl = gsap.globalTimeline.getChildren(true,false,true).find(c => c instanceof gsap.core.Timeline);
tl.pause(3.6);   // screenshot the exact state you want
```

## 4. Slack delivery — always self-contained

**Any HTML destined for Slack must embed all assets as base64 data URIs inside the file.** Relative `src="assets/..."` paths only work when the assets folder is alongside the HTML on the same filesystem. When the HTML is downloaded from Slack on its own, those paths break.

### Embed images as base64 — conversion snippet
```python
import base64, sys
with open(sys.argv[1], 'rb') as f:
    data = base64.b64encode(f.read()).decode()
ext = sys.argv[1].rsplit('.',1)[-1]  # png, jpg, svg, etc.
mime = {'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg','svg':'image/svg+xml','gif':'image/gif'}.get(ext,'application/octet-stream')
print(f'data:{mime};base64,{data}')
```
Use `img.src = <data-uri>` or inline it in your `<img src="...">` tags. For 5MB+ PNGs, resize to 2× display size first (ImageMagick: `convert input.png -resize 544x544 -quality 90 output.png`) to keep the final HTML under ~2MB.

### Check image aspect ratio before embedding
Never force an image into a square container without checking its intrinsic dimensions first:
```bash
file_info=$(python3 -c "from PIL import Image; im=Image.open('$IMG'); print(im.width, im.height)")
# If landscape (w > h), scale to target height then center-crop to target square
convert input.png -resize x272 -gravity center -extent 272x272 output.png
```
A landscape PNG (e.g. 1192×896) stuffed into a 272×272 `<img>` will squash unless `object-fit: cover` or a crop/resize is applied first.

## 5. Figma PNG cleanup — transparent backgrounds

Figma sometimes exports PNGs with fully opaque white pixels (`255,255,255,255`) baked into the corners — especially for elements that had a white artboard background. When you apply `filter: drop-shadow` to these, the shadow traces the entire bounding rectangle (a white box), not the visible shape.

**Check and fix before embedding:**
```python
from PIL import Image
img = Image.open('char.png').convert('RGBA')
px = img.load()
w, h = img.size
# Flood-fill from corners to find the white background region
from collections import deque
def flood(x0,y0):
    q = deque([(x0,y0)])
    seen = set()
    while q:
        x,y = q.popleft()
        if (x,y) in seen or not (0<=x<w and 0<=y<h): continue
        seen.add((x,y))
        r,g,b,a = px[x,y]
        if a > 0 and (r,g,b) == (255,255,255):
            px[x,y] = (0,0,0,0)
            for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]: q.append((x+dx,y+dy))

for cx,cy in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]:
    flood(cx,cy)
img.save('char-nobg.png')
```

## 6. Slot machine — always use dynamic width

**Never pre-size the slot wrapper to the widest word.** If you do, shorter words like "leads" leave a visible blank gap: "grows your   leads".

Use two spans that swap with a vertical wipe, and GSAP-morph the slot wrapper width to match each word's measured width:
```js
function sc(displayPx) {
  // Convert display px back to stage px (undo the viewport scaler)
  const scaler = document.querySelector('.stage-scaler');
  const factor = scaler.getBoundingClientRect().width / STAGE_W;
  return displayPx / factor;
}

function measureWord(word) {
  const probe = document.createElement('span');
  probe.style.cssText = 'position:absolute;visibility:hidden;font:400 96px/1 "Monday Pop",Poppins,sans-serif';
  probe.textContent = word;
  document.body.appendChild(probe);
  const w = sc(probe.getBoundingClientRect().width);
  probe.remove();
  return w;
}

function swapWord(newWord) {
  // curEl = outgoing span, nextEl = incoming span (pre-loaded with newWord)
  const targetW = measureWord(newWord) + 8; // 8px letter-spacing buffer
  gsap.to(slotWrap, { width: targetW, duration: 0.3, ease: 'power2.inOut' });
  gsap.to(curEl, { y: '100%', duration: 0.3, ease: 'power2.in', onComplete: () => { /* park below */ } });
  gsap.fromTo(nextEl, { y: '-100%' }, { y: '0%', duration: 0.3, ease: 'power2.out' });
}
```

## 7. Headless-capture font fix — eliminate FOUT in GIF/MP4 first frames

**Problem:** When fonts are loaded from Google Fonts (or any external CDN), headless Playwright captures frames before the browser has finished the HTTP font request. The result: the first N frames of your GIF/MP4 show the wrong fallback font, then the correct font suddenly snaps in — a visible, ugly flash.

**Fix: embed every font as an inline `@font-face` base64 data URI** with `font-display: block`. The font bytes are part of the HTML; zero HTTP round-trips; available at `t=0`.

```css
/* In <style> — before any font is used */
@font-face {
  font-family: 'Poppins';
  font-weight: 400;
  font-style: normal;
  font-display: block;          /* ← block rendering until font is ready */
  src: url('data:font/woff2;base64,<BASE64_BYTES_HERE>') format('woff2');
}
```

**How to get the base64:** download the `.woff2` file from Google Fonts (or wherever), then:
```bash
python3 -c "import base64,sys; print(base64.b64encode(open(sys.argv[1],'rb').read()).decode())" font.woff2
```
Paste the output in place of `<BASE64_BYTES_HERE>`. Repeat for every weight/variant you use — a missing weight will fall back and still FOUT.

**Which fonts to embed for a typical monday.com animation:**
- Poppins 400, 500, 600 (label text)
- Figtree 400, 500 (body / status text)

The embedded font inflates the HTML file significantly (150–300KB per font). That's fine for a self-contained deliverable or headless render — just don't ship it to production.

## 8. Expose `window.mainTl` for the capture script

Always assign the main GSAP timeline to a global `window.mainTl` so the Playwright capture script can wait for it and seek it frame-by-frame:

```js
window.mainTl = null;   // ← declare at module scope (before the build function)

window.addEventListener('DOMContentLoaded', () => {
  // ...
  Promise.all([...fonts+images...]).then(() => {
    window.mainTl = buildTimeline();
    window.mainTl.play();
  });
});
```

The capture script then does:
```js
// Wait for the timeline to be ready before seeking
await page.waitForFunction(() => window.mainTl !== null, { timeout: 10000 });

// Deterministic per-frame seek
for (let f = 0; f < TOTAL_FRAMES; f++) {
  await page.evaluate(t => {
    window.mainTl.pause();
    window.mainTl.seek(t, true);
  }, f / FPS);
  await page.screenshot({ path: framePath, clip: { ... } });
}
```

If `window.mainTl` is not exposed, the capture script has no reliable way to know when the timeline exists — and `waitForTimeout(N)` is fragile.

## Hand off (typical build order)
1. **`precise-figma-composition`** — place elements inside `.stage` at Figma-exact geometry.
2. **`loop-animator`** — turn the composition into a seamless loop (fill in `build()`).
3. **`marquee-carousel`** / **`gsap-ui-entrance`** — add scrolling rows or orchestrated
   element entrances as needed.
4. **`export-as-gif`** — re-build in Remotion and render the GIF/MP4; or use the Playwright
   frame-capture pipeline (see `export-as-gif` skill for both paths).
5. **`resize-animation`** — reflow to other aspect ratios (portrait/landscape) for variants.

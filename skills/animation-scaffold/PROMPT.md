
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

## Hand off (typical build order)
1. **`precise-figma-composition`** — place elements inside `.stage` at Figma-exact geometry.
2. **`loop-animator`** — turn the composition into a seamless loop (fill in `build()`).
3. **`marquee-carousel`** / **`gsap-ui-entrance`** — add scrolling rows or orchestrated
   element entrances as needed.
4. **`export-as-gif`** — re-build in Remotion and render the GIF/MP4.
5. **`resize-animation`** — reflow to other aspect ratios (portrait/landscape) for variants.

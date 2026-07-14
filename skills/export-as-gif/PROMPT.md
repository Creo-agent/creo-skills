
# Export as GIF (via Remotion)

Render an animation to a real GIF/MP4 by rebuilding it in Remotion, where every frame
is a pure function of time — so renders are deterministic and loops are seamless. Load
the `remotion-best-practices` skill for library rules; this skill is the porting +
render recipe.

## 0. Ask for the output spec FIRST
Before scaffolding or rendering, confirm what the final file must be — these choices
change the composition dimensions and the render flags, so getting them up front avoids
re-rendering (renders are slow). If the user hasn't already said, ask for:
- **Dimensions / resolution** — e.g. 1080×1080, 1080×1920, 800×800. (Drives `width`/`height`.)
- **Frame rate** — smoothness vs size (GIF often looks fine at 12–15fps).
- **Format** — GIF vs MP4/WebM. (GIF = universal but heavy; MP4/WebM = far smaller at
  higher quality. If they want "small + crisp", steer toward MP4/WebM.)
- **A hard size limit or compression target** — e.g. "under 5 MB for Slack", "email-safe".
  This is the key constraint: pick `--scale`, fps (`--every-nth-frame`), and format to hit it.

Then map the answers to render settings (see §5) and, if needed, iterate: render, check the
actual file size, and adjust `--scale` / fps until it's under the limit. Report the final
dimensions, fps, and size so the user can confirm the tradeoff.

## When the source is a GSAP/HTML loop
You're translating a *timeline* into *frame math*. The mindset shift: instead of a
playing timeline, compute each element's state from `useCurrentFrame()`.

## 1. Scaffold the project
```
remotion/
├── package.json        # remotion + @remotion/cli + react
├── tsconfig.json
├── remotion.config.ts  # Config.setVideoImageFormat("jpeg"); Config.setOverwriteOutput(true)
├── public/             # assets, referenced via staticFile()
└── src/
    ├── index.ts        # registerRoot(RemotionRoot)
    ├── Root.tsx        # <Composition> — id, component, durationInFrames, fps, width, height
    └── <Anim>.tsx      # the animation
```
`npm install` then verify with `npx tsc --noEmit` and a still render before doing video.

## 2. Port to frame-based
- Everything is `f(useCurrentFrame())`. **CSS transitions/animations are forbidden** —
  they don't render. Use `interpolate` / `spring` / `Easing`.
- Write timing in **seconds × fps**.
- **GSAP-ease → Remotion `Easing` cheat-sheet** (GSAP powerN: 1=Quad,2=Cubic,3=Quart):
  - `power2.in`  → `Easing.in(Easing.cubic)`
  - `power2.out` → `Easing.out(Easing.cubic)`
  - `power1.inOut` → `Easing.inOut(Easing.quad)`
  - `'none'` → linear (default)
- Reference assets with `staticFile("name.avif")`; use `<Img>` (waits for load).
- **Fonts must be loaded**, or text renders in a fallback (wrong metrics *and* wrong look —
  which also breaks any width-dependent layout like a marquee). Use the google-fonts helper,
  which blocks the render until ready: `import { loadFont } from "@remotion/google-fonts/Figtree";
  const { fontFamily } = loadFont("normal", { weights: ["400"], subsets: ["latin"], ignoreTooManyRequestsWarning: true });`
  (limit weights/subsets — the default loads dozens and warns).
- **Pseudo-elements don't render** here the way you'd style them per-frame: `::before`/`::after`
  can't take frame-driven inline styles. Rebuild such layers as real child `<div>`s (e.g. a
  gradient-stroke overlay becomes a positioned div whose `backgroundPositionX` you compute
  from the frame).

## 3. Seamless loop = triangle-wave timeline
Reproduce a GSAP yoyo loop by mapping frame → a local time that goes up then down, so the
composition's last frame equals its first (no cut when it loops):
```ts
let t;
if (frame < FORWARD) t = frame;                                   // forward
else if (frame < FORWARD + HOLD) t = FORWARD;                     // hold
else if (frame < 2*FORWARD + HOLD) t = FORWARD - (frame - (FORWARD+HOLD)); // reverse
else t = 0;                                                       // hold at start
const ts = t / fps;   // drive all interpolations off ts
```
Set `durationInFrames = (FORWARD + HOLD + FORWARD + HOLD) * fps` and export it so Root
stays in sync.

### …or a forward-loop with envelopes (when a phase must NOT reverse)
The triangle-wave replays the middle backwards — wrong when the source has a distinct
sequential phase (a second screen that appears, then leaves). Mirror the HTML *forward-reset*
loop instead: drive everything off real time `s = frame / fps` and give each element an
**enter/exit envelope** so it rises then falls on its own, engineering the total duration so
the last frame equals the first:
```ts
const enterP = interpolate(s, [inStart, inStart + IN_DUR], [0, 1], { extrapolateLeft:"clamp", extrapolateRight:"clamp", easing });
const exitP  = interpolate(s, [outStart, outStart + OUT_DUR], [0, 1], { extrapolateLeft:"clamp", extrapolateRight:"clamp", easing });
const base   = enterP * (1 - exitP);          // 0 → 1 → 0
const scale  = interpolate(base, [0, 1], [0.1, 1]);   // e.g. grow-out / collapse-back
```
Reverse a stagger's lead direction by indexing the start time backwards
(`outStart = EXIT_AT + (n - 1 - i) * STAG`) rather than forwards. Confirm the last frame
== frame 0 by rendering both stills.

### Marquee / endless scroll → frame math
A GSAP marquee becomes `x = -offset + dir * speed * s`. Because the scrolling layer is
usually invisible at the loop boundary (faded/scaled out), you can skip seamless wrap
entirely — a plain linear translate never shows a seam. Full technique: `marquee-carousel`.

## 4. Verify before rendering video
Render stills at key frames (start / mid-motion / revealed) and view them:
```bash
./node_modules/.bin/remotion still <CompId> out/frame-000.png --frame=0
```
(Invoke the local binary directly — `npx remotion still ... --frame=N` can mis-parse the
flag.)

## 5. Render GIF / MP4
```bash
# MP4
./node_modules/.bin/remotion render <CompId> out/anim.mp4
# GIF (detected by extension; halve fps for size)
./node_modules/.bin/remotion render <CompId> out/anim.gif --codec=gif --every-nth-frame=2
```
Add these as `render` / `gif` scripts in package.json for reuse.

### GIF size tradeoffs (important)
A 1080² GIF of photographic/3D content is large (GIF is 256-color, no real compression).
Levers, in order of impact:
- `--scale=0.5` → half dimensions (~¼ the bytes) — usually the biggest win.
- `--every-nth-frame=2` (→ half fps) or `3` (→ third) — fewer frames.
- Shorter loop / fewer held frames.
State the resulting size and offer a lighter variant; if they need small + high quality,
suggest MP4/WebM over GIF.

## Output
The Remotion project (reusable, tweakable via top-of-file constants) plus the rendered
`out/anim.gif` (and/or `.mp4`). Report dimensions, fps, loop length, and file size.

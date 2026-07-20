
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

## 0.5 If a Remotion project already exists, don't re-scaffold or re-ask
A common follow-up is "re-export, I tweaked the source." Before scaffolding, check for an
existing `remotion/` next to the source. If one is there, it *is* the spec — skip §0's
questions and §1's scaffold. The job is just to **re-sync the changed constants** from the
source into the ported component (e.g. amplitude/period/delay arrays) and re-render. Keep any
loop-preserving transform intact: if the port snapped oscillator periods to divisors of the
loop length, re-snap the new values too (§3) instead of copying the raw source numbers, or the
seam breaks. Only fall back to full scaffolding if no project exists.

If the existing project holds a *different* animation, don't clobber or re-scaffold it — add a
new `<Composition>` to `Root.tsx` (return a fragment listing all comps) plus a new `<Anim>.tsx`,
reuse the installed `node_modules`/config, and copy this animation's assets into `public/`.

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

**Node ≥18 required.** Remotion 4 needs Node ≥18; if the system default is older (e.g. v16), `npm`'s shebang points at it and every command throws `EBADENGINE`. Prefix `PATH` with an nvm node ≥18 bin dir for *each* command (`PATH=/Users/<you>/.nvm/versions/node/v20.x/bin:$PATH ./node_modules/.bin/remotion ...`) rather than assuming the shell default is compatible — check `node --version` first.

## 2. Port to frame-based
- Everything is `f(useCurrentFrame())`. **CSS transitions/animations are forbidden** —
  they don't render. Use `interpolate` / `spring` / `Easing`.
- Write timing in **seconds × fps**.
- **GSAP-ease → Remotion `Easing` cheat-sheet** (GSAP `powerN` = exponent N+1: power1=quad², power2=cubic³, power3=quart⁴, power4=quint⁵):
  - `power1.in|out|inOut` → `Easing.[in|out|inOut](Easing.quad)`
  - `power2.in|out|inOut` → `Easing.[…](Easing.cubic)`
  - `power3.in|out|inOut` → `Easing.[…](Easing.poly(4))`
  - `'none'` / `Linear` → linear (default)
  - ⚠️ Remotion's `Easing` has `quad` and `cubic` but **no `quart`/`quint`** — writing
    `Easing.quart` throws `Property 'quart' does not exist on type 'typeof Easing'` at `tsc`.
    Use `Easing.poly(4)` (quartic), `Easing.poly(5)` (quintic), etc.
- Reference assets with `staticFile("name.avif")`; use `<Img>` (waits for load).
- **Fonts must be loaded**, or text renders in a fallback (wrong metrics *and* wrong look —
  which also breaks any width-dependent layout like a marquee). Use the google-fonts helper,
  which blocks the render until ready: `import { loadFont } from "@remotion/google-fonts/Figtree";
  const { fontFamily } = loadFont("normal", { weights: ["400"], subsets: ["latin"], ignoreTooManyRequestsWarning: true });`
  (limit weights/subsets — the default loads dozens and warns).
- **Pseudo-elements don't render** here the way you'd style them per-frame: `::before`/`::after`
  can't take frame-driven inline styles. Rebuild such layers as real child `<div>`s (e.g. a
  gradient-stroke overlay becomes a positioned div whose `backgroundPositionX` you compute
  from the frame). The same applies to a gradient **stroke** animated via a registered custom
  property (`@property --angle` + `@keyframes`) or `border-image` — a registered-property CSS
  animation is still a CSS animation, so it won't render. Compute the angle/offset from the
  frame and inline it: e.g. `conic-gradient(from ${angle}deg, …)` on an `inset:0` border div
  with `padding` + `WebkitMaskComposite:'xor'` (mask-out the center so only the ring shows).
  Stagger per element by phase-offsetting the angle.
- **GSAP transform-origin of a zero-size wrapper.** A `position:absolute; left:0; top:0` wrapper holding only absolutely-positioned children is a 0×0 box, so its transform-origin resolves to `0px 0px` — GSAP rotates/scales it about the **stage origin (0,0)**, not the visual center. Replicate exactly in the port: set `transformOrigin: '0px 0px'` and apply `transform: translate(x,y) rotate(rot)` (translate *before* rotate). Don't let it default to a centered origin.
- **Figma SVGs with CSS-var fills render their fallback.** Exported SVGs use `fill="var(--fill-0, #COLOR)"` / `stroke="var(--stroke-0, white)"`. Loaded via `<Img src={staticFile(...)}>` no CSS var is in scope, so the fallback color renders — identical to the browser, no patching needed. Copy every asset into `remotion/public` and reference via `staticFile()`.
- **If you hardcode measured source widths, watch the coordinate space.** When you measure widths on a live CSS-scaled stage, divide a `getBoundingClientRect()` by the scale factor *only* for elements inside the scaled subtree — a probe on `document.body` is already at scale 1 and reports true px, so dividing inflates it (~1.875×) and decenters the result (see `frame-building`). Better: measure at render time or size the clip to content instead of baking in brittle px (see `measuring-text`). Center a headline containing a variable-width ticker with `left:0; width:STAGE_W; text-align:center`, never `left:50%`+`translateX(-50%)` shrink-to-fit (see `text-animations`).

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

### …or period-snapping for multiple non-commensurate oscillators
When several independent GSAP yoyo tweens (different periods + phase delays) plus a discrete cycler (e.g. a word ticker) must loop *together*:
1. Pick the loop length `L` from the discrete element (e.g. 5 words × (HOLD 1.5 + WIPE 0.3) = 9.0s = 270f @30fps).
2. **Snap every oscillator's period to an exact integer divisor of `L`** (`L / period ∈ ℤ`; e.g. 3.0 / 4.5 into 9.0).
3. Model each `sine.inOut` yoyo (rest→amp→rest, duration = half-period) as the exact closed form `osc(t) = amp * (1 − cos(2π(t − delay) / period)) / 2` — keep the GSAP `delay` as a pure phase offset.

Because each period divides `L`, both `osc(0)==osc(L)` **and** `osc'(0)==osc'(L)`: position *and* velocity are continuous across the seam (C1). Caveat: the delay becomes a phase, not a startup hold, so frame 0 of the export won't match the live page's very first moments — only its steady-state cycle (correct for a loop). You may also need to nudge a live duration slightly (e.g. live WIPE `0.32` → export `0.30`) so `L` lands on a clean frame count.

**Prove seamlessness before claiming it.** Don't assert "loops seamlessly" from design intent (the user will catch it). Verify: (1) `L/period ∈ ℤ` for *every* oscillator, (2) the closed form and its derivative are periodic (value AND velocity), (3) every discrete element (ticker index/state) returns to its `t=0` state at `t=L`, and (4) render the boundary stills (frame 0 vs frame N−1). Prove it for all groups' position AND rotation AND the ticker — not just the one you eyeballed. Fast check for a forward-reset loop that returns to a static start state: the frame-0 and frame-(N−1) PNG stills should be **byte-identical** (same size/hash).

### Marquee / endless scroll → frame math
A GSAP marquee becomes `x = -offset + dir * speed * s`. Because the scrolling layer is
usually invisible at the loop boundary (faded/scaled out), you can skip seamless wrap
entirely — a plain linear translate never shows a seam. Full technique: `motion`.

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
Real data point (1080×1350, 15fps, 9s loop, photographic avatars): full-res GIF ≈ 9.3 MB,
`--scale=0.5` ≈ 3.5 MB, MP4 ≈ 1.7 MB. So default the GIF to `--scale=0.5` unless the user
explicitly asks for full/"best" resolution, and always name the size so they can judge.

## 6. "Make it loop" — clarify what kind of loop before baking copies
This bites: a Remotion render is **already one seamless cycle** (last frame ≈ first, if §3 was
done right). "Looping" is a *playback* property, not a file property, and the two formats differ:
- **GIF** loops forever by default in virtually every viewer. When the user wants it to
  **play once and stop** ("loop 1 time", "don't loop"), pass Remotion's
  `--number-of-gif-loops=0` (0 = play once / no repeat; `N` = loop N extra times; omit =
  infinite). Cleaner than any post-processing — no re-encode. (Confirm the `0` vs `1`
  semantic against your installed Remotion version.)
- **MP4** has no universally-honored intrinsic loop flag. Whether it repeats depends on the
  player (`<video loop>`, QuickTime "Loop", Slack autoplay repeats, etc.).

So when a user says "make the mp4 loop," do **not** immediately concatenate N copies — that
produces a longer file, not a truer loop, and they'll likely bounce it back ("loop only once").
Default to delivering the single seamless cycle and note that the player controls repetition.
Only physically repeat cycles when they explicitly want the repetitions baked into the file
(e.g. a platform that plays once). To repeat with no re-encode:
```bash
# N+1 total plays: -stream_loop 2 → 3 cycles. -stream_loop 0 (or omit) → single cycle.
ffmpeg -stream_loop 2 -i out/anim.mp4 -c copy out/anim-loop.mp4 -y
```

## Output
The Remotion project (reusable, tweakable via top-of-file constants) plus the rendered
`out/anim.gif` (and/or `.mp4`). Report dimensions, fps, loop length, and file size.

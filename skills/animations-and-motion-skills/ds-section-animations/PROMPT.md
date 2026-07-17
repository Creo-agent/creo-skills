# DS Section Animations

Add interactivity and motion to Clay DS section stories. The DS does not use Framer Motion — all animations use native browser APIs (CSS + vanilla JS).

## When to Use

- User shares Relume HTML or React reference code and asks to "add this animation" to a section
- User asks for mouse parallax, scroll parallax, or entrance animations on a section story
- User asks to "make the media interactive" or "make the images move"

## Step 1 — Identify the Animation Type from Reference Code

Relume components use Framer Motion. Read the imports and hooks to identify what kind of animation is intended:

| Framer Motion code | Animation type | Clay DS equivalent |
|---|---|---|
| `useScroll` + `useTransform` on `scrollYProgress` | Scroll-driven parallax (elements move as page scrolls) | **JS scroll listener** (Step 3) — *not* CSS `animation-timeline` |
| `useMotionValue` + `useSpring` on mouse `clientX/Y` | Mouse-move parallax (elements shift as cursor moves) | CSS custom props `--mx/--my` + `mousemove` listener (Step 2) |
| `initial`/`animate`/`whileInView` | Entrance animation (fade/slide in on scroll) | CSS `@keyframes` + `animation-timeline: view()` |
| `motion.div` with `drag` | Draggable interaction | Pointer events in React |
| Tailwind `animate-loop-vertically` / `animate-loop-horizontally` (no Framer hook) | Continuous auto-scroll marquee (columns/rows loop forever) | CSS `@keyframes` translate + `infinite linear` (Step 3b) |

**Do not assume scroll = scroll.** `useScroll` in a header section often means scroll-driven background parallax, but monday.com production pages frequently use **mouse-move** parallax on hero backgrounds. Always look at the mounted element and what the transform is applied to.

**Which approach when the reference IS genuinely scroll-driven:**
- If the user is happy with a cursor-driven feel → use **mouse-move parallax** (Step 2). It animates in an isolated story without any scroll range and is the most robust.
- If the user explicitly wants the **scroll** behavior (drift tied to scrolling) → use the **JS scroll listener** (Step 3). Do **not** reach for CSS `animation-timeline: scroll()` — it is unreliable in this codebase's environments (see Step 3's "Why not CSS scroll-timeline").

## Step 2 — Mouse-Move Parallax (Most Common for Hero Sections)

### Pattern

Use CSS custom properties `--mx` and `--my` updated via JS — zero React re-renders, 60fps smooth.

```tsx
import { useEffect, useRef } from 'react'

function ParallaxMedia() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const c = containerRef.current
      if (!c) return
      // Normalize mouse position relative to the section (-0.5 … +0.5)
      const section = c.closest('section')
      const rect = section
        ? section.getBoundingClientRect()
        : { left: 0, top: 0, width: window.innerWidth, height: window.innerHeight }
      const x = (e.clientX - rect.left) / rect.width - 0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5
      c.style.setProperty('--mx', x.toFixed(4))
      c.style.setProperty('--my', y.toFixed(4))
    }
    window.addEventListener('mousemove', onMove, { passive: true })
    return () => window.removeEventListener('mousemove', onMove)
  }, [])

  // depth = max displacement in px when cursor is at edge (mouse at ±0.5)
  // Negative multiplier → element moves opposite to cursor (parallax feel)
  const tf = (depth: number): React.CSSProperties => ({
    transform: `translate(calc(var(--mx) * ${-depth}px), calc(var(--my) * ${-depth}px))`,
    transition: 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    willChange: 'transform',
  })

  return (
    <div
      ref={containerRef}
      style={{
        position: 'relative', width: '100%', height: '100%',
        '--mx': '0', '--my': '0',
      } as React.CSSProperties}
    >
      {/* Each element gets a different depth: higher = "closer to camera" = more movement */}
      <div style={{ position: 'absolute', top: '5%', left: '10%', width: '20%', ...tf(20) }}>
        <MediaSlot placeholder style={{ width: '100%', height: '100%' }} radius="none" />
      </div>
      <div style={{ position: 'absolute', top: '20%', right: '5%', width: '15%', ...tf(40) }}>
        <MediaSlot placeholder style={{ width: '100%', height: '100%' }} radius="none" />
      </div>
    </div>
  )
}
```

### Depth Scale Guidelines

| Depth value | Feel | Use for |
|---|---|---|
| 10–15px | Very subtle | Background / furthest layer |
| 20–25px | Medium | Mid-ground elements |
| 30–40px | Pronounced | Foreground / "closest" elements |

Use 3–4 distinct depth levels across elements for a convincing parallax effect.

### Where to Put This Code

- **In the story file** (`.stories.tsx`) as a local helper component, passed to the section's `media` prop — not in the component itself. The section component stays stateless and animation-agnostic.
- Example: `FloatingScatteredMedia` in `HeaderSection.stories.tsx` passed as `media={<FloatingScatteredMedia />}`.

```tsx
export const FloatingScattered: Story = {
  args: {
    layout: 'floating-scattered',
    // ...heading, description, actions...
    media: <FloatingScatteredMedia />,
  },
}
```

### Initial CSS Variable Declaration

Always initialize `--mx` and `--my` on the container element's style so the `calc()` expressions in child `transform`s don't resolve to `calc(0 * Npx)` before first mouse move. Pass them as part of the inline `style` object:

```tsx
style={{ '--mx': '0', '--my': '0' } as React.CSSProperties}
```

## Step 3 — Scroll-Driven Parallax (JS scroll listener — PREFERRED)

When the reference uses `useScroll` + `useTransform` and the user wants the **scroll** behavior, replicate Framer's `scrollYProgress` → `translate` mapping with a plain `scroll` listener. This is reliable, verifiable, and works in every environment. **Do not use CSS `animation-timeline: scroll()`** (see "Why not CSS scroll-timeline" below — it cost a full debugging cycle).

### The decision that matters most: what drives "progress"?

Framer's bare `useScroll()` tracks **whole-page** scroll progress (0 at page top → 1 at page bottom). Naively porting that has two problems:

1. **An isolated story has no scroll range** (`scrollHeight === clientHeight`, `scrollable: 0`), so whole-page progress is always 0 and nothing moves. You'd need a tall spacer just to demo it.
2. **A hero sits at the top of the page**, so it's already fully in view at load — whole-page progress 0 keeps it at the "start" offsets, but viewport-entry progress (`(vh - rect.top) / (vh + rect.height)`) is already ~0.5 at rest, so half the animation has happened before the user scrolls.

**Fix: anchor progress to the section's own position** — `p = clamp01(-rect.top / rect.height)`. This is 0 when the section is at rest (its top aligned with the viewport top → full start offsets), and reaches 1 once it has scrolled one section-height up and out of view. The hero starts at the reference's start offsets and drifts to "settled" as it scrolls away. **No spacer needed on a real page** — the sections below the hero provide the scroll. The section keeps its natural height.

### Pattern

```tsx
import { useEffect, useRef } from 'react'

function ScrollParallaxMedia() {
  const rootRef = useRef<HTMLDivElement>(null)
  const aRef = useRef<HTMLDivElement>(null)
  const bRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return

    const lerp = (a: number, b: number, t: number) => a + (b - a) * t
    const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)

    const apply = () => {
      const section = rootRef.current?.closest('section')
      if (!section) return
      const rect = section.getBoundingClientRect()
      // 0 at rest (section top at viewport top); 1 after scrolling one section-height out
      const p = clamp01(-rect.top / rect.height)
      // Map progress to the reference's translate ranges. Sub-ranges (e.g. [0, 0.5])
      // are done with clamp01(p / 0.5).
      if (aRef.current) aRef.current.style.transform = `translateY(${lerp(15.333, 0, p).toFixed(3)}%)`
      if (bRef.current) bRef.current.style.transform = `translateY(${lerp(11.333, -20, clamp01(p / 0.5)).toFixed(3)}%)`
    }
    apply() // set initial frame
    window.addEventListener('scroll', apply, { passive: true })
    window.addEventListener('resize', apply, { passive: true })
    return () => {
      window.removeEventListener('scroll', apply)
      window.removeEventListener('resize', apply)
    }
  }, [])

  return (
    <div ref={rootRef} style={{ position: 'relative', width: '100%', paddingBottom: '62%' }}>
      <div ref={aRef} style={{ position: 'absolute', /* … */ willChange: 'transform' }}>
        <MediaSlot placeholder style={{ width: '100%', height: '100%' }} radius="none" />
      </div>
      <div ref={bRef} style={{ position: 'absolute', /* … */ willChange: 'transform' }}>
        <MediaSlot placeholder style={{ width: '100%', height: '100%' }} radius="none" />
      </div>
    </div>
  )
}
```

### Critical pitfalls (each cost a debugging cycle)

1. **Do NOT batch with `requestAnimationFrame`.** rAF callbacks are throttled/paused in hidden or backgrounded tabs and **do not fire at all in Claude's headless Electron preview** (a double-rAF eval there times out). If you schedule `apply` via rAF, the initial frame runs once and then the parallax freezes. Write transforms **directly in the scroll handler** — it's cheap for a handful of elements and is what makes it both work everywhere and be verifiable.

2. **Map the reference ranges exactly.** Read each `useTransform(scrollYProgress, [inStart, inEnd], [outStart, outEnd])` and reproduce it with `lerp` + a clamped sub-progress. Example from Relume Header140: left `[-15.444% → 0%]` over `[0,1]`, center `[15.333% → 0%]` over `[0,1]`, right `[11.333% → -20%]` over `[0, 0.5]` (→ `clamp01(p / 0.5)`).

3. **`prefers-reduced-motion`** — bail out of the effect entirely (leave elements at their CSS rest position) when reduce is set.

4. **Demoing in an isolated story needs scroll range.** Add a Storybook-only spacer via the story's `decorators` (NOT a component prop) — see "Spacer / decorator" below. On a real page no spacer is needed because section-anchored progress only requires the page to scroll past the hero.

### Spacer / decorator — and why it never leaks into pages

To see section-anchored parallax in an isolated story, the hero needs to be able to scroll up through the viewport. Add a spacer **in the story's `decorators`**:

```tsx
export const FloatingLeft: Story = {
  decorators: [
    (Story) => (
      <>
        <Story />
        <div style={{ height: '100vh' }} aria-hidden />
      </>
    ),
  ],
  args: { /* … */ media: <ScrollParallaxMedia /> },
}
```

**Reassurance to give the user:** decorators are a **Storybook-only** mechanism. Generated pages compose the `HeaderSection` *component* directly — they never import stories or their decorators — so the spacer produces **zero extra height in generated pages**. If a user worries the spacer will bloat their pages, this is the answer: it can't.

### How to verify a JS scroll listener in the preview

Unlike CSS scroll-timeline (which can't be driven programmatically here), a JS listener IS testable — set `scrollTop`, dispatch a `scroll` event, wait a tick, read the inline transform:

```js
const se = document.scrollingElement
const wraps = [...document.querySelectorAll('section [class*="media"] > div > div')]
se.scrollTop = (se.scrollHeight - se.clientHeight) * 0.5
window.dispatchEvent(new Event('scroll'))
await new Promise(r => setTimeout(r, 60))
wraps.map(w => w.style.transform) // → assert against expected lerp values
```

Confirm `atRest` shows the reference start offsets and the values interpolate toward "settled" as `scrollTop` increases.

### Why NOT CSS scroll-timeline (`animation-timeline: scroll()`)

It looks clean but is unreliable here, and the failure is silent — the animation reports `playState: 'running'` with a `ScrollTimeline` attached, yet `timeline.currentTime` is `null` (the timeline is **inactive**) so the computed `transform` stays `none` and nothing moves. Observed even with valid scroll range and keyframes correctly placed outside `@layer`. It also can't be driven by programmatic `scrollTop` in the preview, so you can't verify it. Prefer the JS listener. (If you ever must use it: keyframes go **outside** `@layer`, use `scroll(root)` not `scroll(nearest)`, `animation-fill-mode: both`, and accept it's only testable in a real browser.)

## Step 3b — Continuous Marquee Loop (auto-scroll)

For references with Relume's `animate-loop-vertically` / `animate-loop-horizontally` (a Tailwind keyframe class, **no** Framer hook): columns or rows of media scroll forever in one direction. This is a time-based CSS `@keyframes` loop, not scroll- or cursor-driven.

### The one thing that makes it seamless

Duplicate the item set inside each track, then animate `translateY(0 → -50%)` `infinite`. At `-50%` the second copy sits exactly where the first started → no visible jump. **Critical:** one copy must be *exactly* half the track height. With flex `gap`, the gap pattern between the two copies breaks that (`-50%` lands half a gap off and the seam jumps). **Use `margin-bottom` on every item instead of `gap`** so each item contributes `itemHeight + margin` uniformly and `N` items = exactly half of `2N`.

```tsx
const GAP = 16, ITEMS = 4
function MarqueeMedia() {
  const Track = ({ delay }: { delay: string }) => (
    <div className="clay-marquee-track" style={{ animationDelay: delay }}>
      {Array.from({ length: ITEMS * 2 }).map((_, i) => ( // set duplicated for seamless loop
        <MediaSlot key={i} placeholder radius="small"
          style={{ width: '100%', aspectRatio: '1 / 1.05', marginBottom: GAP, flex: 'none' }} />
      ))}
    </div>
  )
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden', display: 'flex', gap: GAP, alignItems: 'flex-start' }}>
      <style>{`
        .clay-marquee-track { display:flex; flex-direction:column; flex:1; min-width:0;
          will-change: transform; animation: clay-marquee-loop 40s linear infinite; }
        @keyframes clay-marquee-loop { from { transform: translateY(0); } to { transform: translateY(-50%); } }
        @media (prefers-reduced-motion: reduce) { .clay-marquee-track { animation: none; } }
      `}</style>
      <Track delay="0s" />
      <Track delay="-20s" />  {/* negative delay → second column visually offset (out of phase) */}
    </div>
  )
}
```

Notes:
- **Self-contain the clipping** (`overflow: hidden` on the marquee root) so it doesn't depend on the section's `.media` overflow (which may be `visible` at some breakpoints).
- **Stagger columns** with a negative `animation-delay` (e.g. half the duration) — same effect as the reference's margin offset, without breaking the loop.
- **`@keyframes` via injected `<style>` in the story** is fine here (keeps the animation story-local, per the "animation lives in the story" rule). Use a unique class prefix.
- **Reduced motion:** pause via `@media (prefers-reduced-motion: reduce) { animation: none }` in the injected style.

### Verifying in the preview (and the limitation)

The preview's `DocumentTimeline` is frozen (it doesn't tick when the iframe isn't producing frames), so the marquee won't visibly advance and `animation.currentTime` stays `0` — same class of limitation as rAF and scroll-timeline. You can still verify:
- **Config:** `getComputedStyle(track).animationName / animationDuration / animationIterationCount` and `track.getAnimations()[0].playState === 'running'`.
- **Seamless math (drive time manually):** set `track.getAnimations()[0].currentTime = duration` (100%) and assert the computed `translateY` pixels ≈ **half the track's measured height**. Remember the keyframe runs `0 → -50%` over the *full* duration, so 50% progress is `-25%`, not `-50%` — check at 100%.

Motion itself must be confirmed in a real browser.

Reference implementation: **`MosaicLoopMedia`** (`SplitMosaic` story) in `HeaderSection.stories.tsx`.

## Step 4 — Accessibility

- Always disable or reduce parallax under reduced motion. For **mouse-move** (Step 2): add `@media (prefers-reduced-motion: reduce)`. For **JS scroll** (Step 3): early-`return` from the `useEffect` when `matchMedia('(prefers-reduced-motion: reduce)').matches`, so the elements stay at their CSS rest position.
- For mouse parallax: the `transition` already smooths abrupt motion; no extra work needed.
- For JS scroll parallax: no `transition` — the transform is recomputed every scroll event, so it tracks the scroll directly (a transition would add lag).

## Checklist Before Finishing

- [ ] Animation is in the story file, not the component (section stays stateless/animation-agnostic)
- [ ] No Framer Motion imports added (not in the DS)
- [ ] `prefers-reduced-motion` handled (mouse: `@media`; JS scroll: early-`return`)
- [ ] No inline hardcoded colors or spacing — tokens only
- [ ] `willChange: 'transform'` on each animated element (promotes to compositor layer)
- [ ] **Mouse-move:** `--mx`/`--my` initialized to `'0'` on the container
- [ ] **JS scroll:** progress is **section-anchored** (`-rect.top / rect.height`), NOT whole-page or viewport-entry; transforms written **directly** in the handler (no rAF); reference `useTransform` ranges reproduced exactly
- [ ] **JS scroll demo:** spacer added via story `decorators` only (never a component prop); confirmed it does not affect generated pages
- [ ] Avoided CSS `animation-timeline: scroll()` for scroll parallax (use the JS listener)
- [ ] **Marquee loop:** items duplicated; trailing space via `margin-bottom` (not flex `gap`) so `translateY(-50%)` is exactly one copy; clips internally; columns staggered via negative `animation-delay`

## Reference Implementations (in this codebase)

`packages/react/src/web/HeaderSection/HeaderSection.stories.tsx`:

- **`FloatingScatteredMedia`** — canonical **mouse-move** parallax. 10 scattered images across depth levels (15–40px), `0.4s` ease-out transition, CSS custom props (`--mx/--my`) pattern.
- **`FloatingLeftMedia`** (`FloatingLeft` story) — canonical **JS scroll** parallax for a hero. Section-anchored progress (`-rect.top / rect.height`), direct writes (no rAF), reproduces Relume Header140's ranges (left `-15.444→0`, center `15.333→0`, right `11.333→-20` over `[0,0.5]`). The `FloatingLeft` story uses a Storybook-only `100vh` spacer decorator to make the scroll visible in isolation.

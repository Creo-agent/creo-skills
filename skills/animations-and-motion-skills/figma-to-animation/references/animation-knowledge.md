# Animation knowledge base (roles · timing · best practices · brand)

The **semantic layer** the pipeline leans on: *what* good motion is and *when* to use which tool — the
"why" behind the motion baseline that `knowledge.md` only names in one line. Read alongside
`knowledge.md` (which owns the *mechanical* lessons: measurement, seamless-loop math, Figma fidelity,
GSAP→Remotion port). This doc links to the engine skills rather than restating them:
`../gsap/PROMPT.md` (easing/timeline API), `../remotion-best-practices/rules/timing.md` (spring
configs), `../motion/` (loop shapes + recipes).

## 1. Motion roles (what each kind of motion is *for*)

Every animation beat plays one role. Name the role first, then pick easing + duration to match — don't
reach for an ease at random.

| Role | Purpose | Easing family | Typical duration |
|---|---|---|---|
| **Entrance** | Bring an element on-screen; establish hierarchy via stagger | ease-**out** (`power2.out`, `back.out` for a little life) | 300–500ms |
| **Emphasis** | Draw attention to something already present (pulse, nudge, count-up) | `sine.inOut` / `power1.inOut` (symmetric) | 200–600ms, often looped |
| **Exit** | Remove an element; reverse of entrance | ease-**in** (`power2.in`) | 200–400ms (faster than entrance) |
| **Transition** | Move between two states/frames (the pipeline's per-transition delta) | ease-**inOut** (`power2.inOut`, `sine.inOut`) | 400–700ms |
| **Ambient / loop** | Continuous life with no start/end (marquee, breathing, motion) | `sine.inOut` yoyo or linear (marquee) | period snapped to the loop length `L` |

Rules of thumb: **out** for things arriving (fast then settle), **in** for things leaving, **inOut**
for things travelling between states. Reserve overshoot (`back`, `elastic`) for playful entrances/
emphasis — never for exits or precise UI transitions.

## 2. Timing & easing heuristics

- **Duration by scale of change:** micro-interaction (hover/press) **100–200ms**; small pop-in/expand
  **200–400ms**; entrance/reveal **300–500ms**; frame-to-frame transition **400–700ms**; a deliberate
  hero reveal can go longer but rarely past ~1s for a single beat.
- **Stagger:** 40–80ms between sibling items reads as one orchestrated wave; >150ms starts to feel
  like separate events. Lead direction encodes meaning (top-down for a list arriving, edges-in for a
  cluster assembling). GSAP `stagger` API → `../gsap/PROMPT.md`.
- **Easing → intent cheat-sheet** (GSAP live): entrance `power2.out`/`back.out(1.4)`; exit
  `power2.in`; transition `power2.inOut`; ambient `sine.inOut`. GSAP→Remotion easing map (power N =
  `Easing.poly(N+1)`; no `quart`/`quint`) is in `../export-as-gif/PROMPT.md`.
- **Springs (Remotion export):** prefer named configs over hand-tuned damping — `smooth {damping:200}`
  for settling, `snappy {damping:20, stiffness:200}` for UI, `bouncy {damping:8}` for playful. Details
  + curves in `../remotion-best-practices/rules/timing.md`.
- **Loop timing:** for anything looped, the period must divide the loop length `L` exactly (value AND
  velocity continuous) — the seam-proof recipe is in `knowledge.md` (Motion & seamless loops) and
  `../motion/references/loops.md`.

## 3. Best practices & accessibility

- **Respect `prefers-reduced-motion`.** Gate non-essential motion (parallax, large movement,
  autoplay loops) behind it; fall back to a cross-fade or a static state. GSAP `matchMedia` handles
  this — see `../gsap/PROMPT.md`.
- **Don't animate everything.** Motion is hierarchy: if everything moves, nothing reads. Animate the
  1–3 elements that carry the story; let the rest hold. (Enforced loosely in `pipeline/06a-animate.md`.)
- **Anticipation & overshoot, sparingly.** A small overshoot (`back.out`) adds life to an entrance;
  overuse makes UI feel toy-like and is wrong for precise product transitions.
- **Performance = compositor-friendly props.** Animate `transform` and `opacity`, not `top/left/width`
  or `box-shadow`; use `will-change`/`quickTo` for hot paths. Layout-affecting animation drops frames.
- **Prove, don't assert.** For looped/timed/measured motion, show the check (boundary stills,
  value/velocity equality) — the QA philosophy in `knowledge.md` and the rubric.

## 4. monday brand motion

*(Design-team-owned — the one brand-specific layer. Fill in with monday.com's canonical values as they
are formalized; until then, follow the baseline below and flag brand decisions to the design team.)*

- **Baseline feel:** confident and smooth, never frantic — restraint over excess. Default eases stay in
  the `power2`/`sine` families; avoid harsh linear or heavy bounce in marketing pieces.
- **Signature transitions / brand curves:** _TBD — capture the approved cubic-beziers and signature
  reveal here._
- **Marketing-motion do/don'ts:** _TBD — e.g. hold times for social loops, logo treatment, when a word
  ticker vs a marquee is on-brand._

> Keep this section the single home for brand-specific motion so the vendored `gsap` /
> `remotion-best-practices` snapshots stay generic and swappable.

# Design System — monday-presentation-v2

Agent reference for `design-system.css`. Every token, class, and component below matches the CSS exactly. When generating a slide, inline `icon-font.css` first (icon font + base class), then `design-system.css` into `<style>` — all classes listed here are then available with no extra CSS needed.

---

## Font

```
@import 'Poppins:wght@400;600'
```

**Only two weights exist in this system.** Poppins Regular (400) and SemiBold (600). All four weight tokens collapse onto these two:

| Token | Value | Use |
|-------|-------|-----|
| `--weight-light` | `400` | Body text, secondary content |
| `--weight-regular` | `400` | Default — most text |
| `--weight-medium` | `600` | Same as semibold (no 500 loaded) |
| `--weight-semibold` | `600` | Headlines, emphasis |

**Rule:** Never load or reference weights 300, 500, or 700. All emphasis is achieved through color (`.highlight`) or SemiBold (`.highlight--bold`) — never both on the same element.

---

## Typography Scale

All sizes use `vmin` units — scale proportionally at any screen size, no media queries needed. Since slides are wider than tall (16:9), `1vmin ≈ 1vh`.

| Token | Value | Typical use |
|-------|-------|-------------|
| `--text-display` | `10.5vmin` | Hero cover headlines |
| `--text-h1` | `8vmin` | Primary slide headlines |
| `--text-h2` | `6vmin` | Section headings |
| `--text-h3` | `4vmin` | Subsection titles |
| `--text-h4` | `3vmin` | Labels, card headers |
| `--text-body` | `2.2vmin` | Main body copy |
| `--text-body-sm` | `1.8vmin` | Secondary body, captions |
| `--text-caption` | `1.4vmin` | Chart labels, meta info |

**Line heights:**

| Token | Value | Use |
|-------|-------|-----|
| `--leading-tight` | `1.1` | Display & h1 headlines |
| `--leading-snug` | `1.3` | h2, h3 headings |
| `--leading-normal` | `1.5` | Body copy |
| `--leading-relaxed` | `1.7` | Long-form, accessible text |

**Letter spacing:** All three tracking tokens resolve to `0`. Poppins ships at the correct optical tracking — never add custom `letter-spacing` to slides. The lockdown block enforces this.

### Typography utility classes

Apply directly to any HTML element:

```html
<h1 class="text-display">Big hero text</h1>
<h1 class="text-h1">Slide headline</h1>
<h2 class="text-h2">Section heading</h2>
<h3 class="text-h3">Card title</h3>
<p class="text-body">Body copy</p>
<p class="text-body-sm">Small text</p>
<p class="text-caption">Chart label</p>
```

### Weight modifier classes

```html
<span class="font-semibold">Bold emphasis</span>
<span class="font-regular">Normal weight</span>
```

(`font-light`, `font-medium`, `font-bold` also exist but all resolve to 400 or 600.)

### Headline highlight — one rule per headline

```html
<!-- Color emphasis (yellow on dark, purple on light) -->
<h1>Build with <span class="highlight">monday</span> AI</h1>

<!-- Weight emphasis (semibold, no color change) -->
<h1>Ship <span class="highlight--bold">10× faster</span> today</h1>
```

Never apply both classes to the same span. Pick color OR weight, never both.

---

## Colors

### Dark theme (default)

| Token | Value | Use |
|-------|-------|-----|
| `--color-bg` | `#000000` | Slide background |
| `--color-surface` | `#232427` | Cards, panels, table rows |
| `--color-surface-alt` | `#2D3035` | Nested surfaces, icon backgrounds |
| `--color-text` | `#ffffff` | Primary text |
| `--color-text-secondary` | `#c3ced8` | Body copy, descriptions |
| `--color-text-muted` | `#a0a0a0` | Captions, placeholders, labels |
| `--color-border` | `rgba(255,255,255,0.15)` | Subtle borders, grid lines |
| `--color-border-strong` | `rgba(255,255,255,0.8)` | Prominent borders |

### Brand accent colors (unchanged across themes)

| Token | Value | Use |
|-------|-------|-----|
| `--color-purple` | `#6164ff` | Primary brand, highlights, links |
| `--color-purple-light` | `#8A99FF` | Secondary purple, chart bar pair |
| `--color-red` | `#ff3d57` | Alert, negative, urgent |
| `--color-yellow` | `#ffcb00` | Warning, `.highlight` color on dark |
| `--color-green` | `#00c875` | Success, positive, growth |

### Light theme

Set `data-theme="light"` on `<html>` — all color tokens cascade automatically to:

| Token | Light value |
|-------|-------------|
| `--color-bg` | `#FFFFFF` |
| `--color-surface` | `#F0F2F5` |
| `--color-surface-alt` | `#E3E6EE` |
| `--color-text` | `#1F2D3D` |
| `--color-text-secondary` | `#455A73` |
| `--color-text-muted` | `#8FA0B3` |
| `--color-border` | `rgba(0,0,0,0.10)` |
| `--color-border-strong` | `rgba(0,0,0,0.65)` |

In light theme, `.highlight` automatically switches from yellow to `--color-purple`. Icons with `.ds-icon-white` automatically invert to dark. No HTML changes required.

### Color utility classes

```html
<div class="bg-surface">Card</div>
<div class="bg-purple">Purple fill</div>
<p class="text-secondary">Secondary text</p>
<p class="text-purple">Purple accent</p>
<p class="text-yellow">Yellow highlight</p>
<p class="text-green">Green success</p>
```

---

## Spacing

All spacing tokens use `vmin`:

| Token | Value |
|-------|-------|
| `--space-1` | `0.5vmin` |
| `--space-2` | `1vmin` |
| `--space-3` | `1.5vmin` |
| `--space-4` | `2vmin` |
| `--space-5` | `3vmin` |
| `--space-6` | `4vmin` |
| `--space-7` | `5vmin` |
| `--space-8` | `6vmin` |
| `--space-9` | `8vmin` |
| `--space-10` | `10vmin` |

Use `var(--space-N)` for all gaps, margins, and paddings. Never hardcode `px` values for spacing.

---

## Border Radius

| Token | Value | Use |
|-------|-------|-----|
| `--radius-xs` | `0.5vmin` | Bar chart tops, small chips |
| `--radius-sm` | `1vmin` | Table rows |
| `--radius-md` | `2vmin` | Cards, chart containers |
| `--radius-lg` | `3vmin` | Image placeholders, large panels |
| `--radius-xl` | `4vmin` | Large surface panels |
| `--radius-full` | `999px` | Pills, badges |

---

## Slide Layout

```
--slide-padding-y: 8vmin
--slide-padding-x: 10vmin
```

Every slide is a `.slide-container` div locked to 16:9 via:

```css
width: 100vw;
height: 56.25vw;
max-height: 100vh;
max-width: 177.78vh;
```

Add `position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%)` inline in the generated `<style>` to center it in the viewport.

---

## Slide Template Classes

19 layout classes. Apply one to each `.slide-container` with the `slide-active` class pattern. See `slide-templates.html` for live previews of every template.

```html
<div class="slide-container tmpl-cover slide-1" data-slide-index="0">...</div>
<div class="slide-container tmpl-twocol slide-2" data-slide-index="1">...</div>
```

Always include in `<style>`:
```css
.slide-container:not(.slide-active) { display: none !important; }
```

| Class | Display when active | Grid/flex spec | Best for |
|-------|--------------------|--------------------|---------|
| `.tmpl-cover` | `flex` column center | `justify-content: center; align-items: center` | Cover slide, closing / thank you |
| `.tmpl-cover-split` | `flex` column | `gap: var(--space-4)` | Alternative cover: bordered top + colored bottom bar |
| `.tmpl-cover-image` | `flex` row | `align-items: center; position: relative` | Cover with hero image: left text + right oversized image placeholder |
| `.tmpl-cover-gallery` | `grid` | `0.9fr 1.1fr; rows: 1fr 1fr; gap: --space-4` | Cover with gallery: bordered title left + 2 photo slots + info card right |
| `.tmpl-cover-speaker` | `flex` column | `gap: var(--space-3)` | Cover with single presenter: bordered top card + portrait + info card |
| `.tmpl-cover-speakers` | `flex` column | `gap: var(--space-3)` | Cover with two presenters: bordered top card + 2 portrait groups |
| `.tmpl-speaker` | `grid` | `1.1fr 0.9fr; align: center` | Speaker detail: intro text + hero name + bio left, large portrait right |
| `.tmpl-center` | `flex` column center | + `gap: var(--space-6)` | Pull quote, stat hero, section break |
| `.tmpl-twocol` | `grid` | `1fr 1fr; gap: --space-9; align: center` | Title + bullets, problem + solution |
| `.tmpl-compare` | `grid` | `1fr 1fr; gap: --space-5; align: stretch` | Before/after, challenge/solution, pros/cons |
| `.tmpl-features` | `grid` | `0.6fr 1.4fr; gap: --space-9; align: center` | Narrow title left + 2×2 feature grid right |
| `.tmpl-content-img` | `grid` | `1fr 1fr; gap: --space-9; align: center` | Text + bullets left, image/visual right |
| `.tmpl-quote` | `flex` | `justify-content: center; align-items: stretch` | Full-width testimonial / quote box |
| `.tmpl-stats` | `flex` column | `justify-content: center; gap: --space-7` | Full-slide KPIs, metrics overview |
| `.tmpl-steps` | `flex` column | `justify-content: center; gap: --space-6` | Process flow, numbered workflow |
| `.tmpl-timeline` | `flex` column | `justify-content: center; gap: --space-10` | Horizontal timeline with point markers |
| `.tmpl-3col` | `flex` column | `gap: var(--space-5)` | Title + 3 equal-width cards (with optional icons) |
| `.tmpl-4col` | `flex` column | `gap: var(--space-5)` | Title + 4 equal-width cards or colored tiles |
| `.tmpl-image-cards` | `flex` column | `gap: var(--space-5)` | Title + 3 cards with image headers |

### Card styling modes

Multi-card templates (`tmpl-3col`, `tmpl-4col`, `tmpl-compare`, `tmpl-steps`) support three visual approaches:

1. **Grey surface** (default) — all cards use `background: var(--color-surface)`
2. **Brand colors** — each card gets a different full brand color (`--color-purple`, `--color-green`, `--color-yellow`, etc.). Use full colors, never transparency.
3. **Highlight one** — most cards stay grey, one important card uses a brand color to draw focus (e.g. the "solution" panel in a challenge/solution comparison)

---

## Icons (Icon Font)

268 monday.com icons as a single WOFF2 icon font embedded in `icon-font.css`. The `@font-face` and `.monday-icon` base class are defined in `icon-font.css` — inline that file before `design-system.css`. Look up icons by semantic tags in [ICON_FONT_REFERENCE.md](ICON_FONT_REFERENCE.md).

**Alignment:** Icons inherit `text-align` from their parent — no `text-align: center` on `.monday-icon`. When text is left-aligned, icons are left-aligned; when centered, icons center automatically.

**Font override:** If using a Poppins font-family lockdown on `.slide-container *`, add `.slide-container .monday-icon { font-family: "MondayIcons" !important; font-style: normal !important; }` after it so icon glyphs render correctly.

**Quote icon:** `&#xf00e;` — double quotation mark for testimonial slides. Use with `.quote-mark` class which sets `font-size: 7vmin`. Renders in the font's default purple (no palette override needed).

**HTML pattern:**
```html
<span class="monday-icon ds-icon-md ds-icon-white">&#xf096;</span>
```

Size classes:

| Class | Token | Size |
|-------|-------|------|
| `.ds-icon-xs` | `--icon-xs` | `3vmin` |
| `.ds-icon-sm` | `--icon-sm` | `5vmin` |
| `.ds-icon-md` | `--icon-md` | `7vmin` (default) |
| `.ds-icon-lg` | `--icon-lg` | `10vmin` |
| `.ds-icon-xl` | `--icon-xl` | `15vmin` |

Color modifiers (monochrome font — glyphs inherit CSS `color`):
- `.ds-icon-white` — white. In light theme, automatically switches to dark.
- `.ds-icon-dark` — forces dark color (#323338).
- `.ds-icon-brand` — monday.com purple (`--color-purple`).
- `.ds-icon-muted` — 60% opacity.
- No class — inherits `currentColor` from parent.

```html
<span class="monday-icon ds-icon-lg ds-icon-white">&#xf098;</span>  <!-- Lightbulb, large, white -->
<span class="monday-icon ds-icon-sm ds-icon-brand">&#xf096;</span>  <!-- Checkmark, small, purple -->
<span class="monday-icon ds-icon-md">&#xf064;</span>                <!-- Users, medium, inherits color -->
```

---

## Components

### Bar Chart

Full structure — every class needed:

```html
<div class="chart-container">
  <div class="chart-title">Monthly Deployments</div>
  <div class="chart-body">
    <div class="y-axis">
      <span>120</span><span>90</span><span>60</span><span>30</span><span>0</span>
    </div>
    <div class="chart-plot">
      <div class="grid-lines">
        <div class="grid-line"></div>
        <div class="grid-line"></div>
        <div class="grid-line"></div>
        <div class="grid-line"></div>
      </div>
      <div class="bars-row">
        <!-- Each category = one .bar-group -->
        <div class="bar-group">
          <div class="bar-group-bars">
            <div class="bar-wrap">
              <div class="bar-top-label">72</div>
              <div class="bar bar-purple" style="height:60%"></div>
            </div>
            <div class="bar-wrap">
              <div class="bar-top-label">85</div>
              <div class="bar bar-purple-light" style="height:71%"></div>
            </div>
          </div>
          <div class="bar-x-label">Q1</div>
        </div>
        <!-- repeat for Q2, Q3, Q4 -->
      </div>
    </div>
  </div>
  <div class="chart-legend">
    <div class="legend-item">
      <div class="legend-dot" style="background:var(--color-purple)"></div>
      Actual
    </div>
    <div class="legend-item">
      <div class="legend-dot" style="background:var(--color-purple-light)"></div>
      Target
    </div>
  </div>
</div>
```

Bar fill colors: `.bar-purple`, `.bar-purple-light`, `.bar-green`, `.bar-yellow`, `.bar-red`

Bar height is a percentage string set inline (e.g. `style="height:60%"`). Calculate: `value / max_value × 100`.

Stagger animation is built in for up to 8 `.bar-group` elements (0.10s → 0.66s delay).

---

### Pie Chart

```html
<div class="pie-wrap">
  <!-- The chart: set conic-gradient inline. Formula: percent × 3.6 = degrees -->
  <div class="pie-chart" style="
    width: 20vmin; height: 20vmin;
    background: conic-gradient(
      var(--color-purple) 0deg 162deg,
      var(--color-green)  162deg 281deg,
      var(--color-yellow) 281deg 360deg
    );
  "></div>
  <div class="pie-legend">
    <div class="pie-legend-item">
      <div class="pie-legend-dot" style="background:var(--color-purple)"></div>
      <span class="pie-legend-label">Enterprise</span>
      <span class="pie-legend-value">45%</span>
    </div>
    <!-- repeat per segment -->
  </div>
</div>
```

---

### Donut Chart

Same as pie, but wrap in `.donut-wrap` and use `.donut-chart` (adds CSS mask for hole):

```html
<div class="pie-wrap">
  <div class="donut-wrap">
    <div class="donut-chart" style="
      width: 20vmin; height: 20vmin;
      background: conic-gradient(
        var(--color-purple) 0% 62%,
        var(--color-yellow) 62% 86%,
        var(--color-green)  86% 100%
      );
    "></div>
    <div class="donut-center">
      <div class="donut-center-value" style="color:var(--color-purple)">62%</div>
      <div class="donut-center-label">Core</div>
    </div>
  </div>
  <div class="pie-legend">...</div>
</div>
```

Donut hole = 54% transparent center via CSS `mask: radial-gradient(closest-side, transparent 54%, black 55%)`.

---

### Stat Block

```html
<!-- Single stat — place 3–4 in a grid for a metrics slide -->
<div class="stat-block">
  <div class="stat-value" style="color:var(--color-purple)">47K</div>
  <div class="stat-label">Active users</div>
</div>

<!-- Hero stat — single dominant number on a tmpl-center slide -->
<div class="stat-value-hero" style="color:var(--color-green)">98%</div>
<div class="stat-label">Platform uptime</div>
```

`stat-value` = `--text-h1` (8vmin) · `stat-value-hero` = `15vmin`

---

### Step Cards

```html
<!-- Arrange N cards in a grid row -->
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:var(--space-5);">
  <div class="step-card">
    <div class="step-number">1<span class="dot-purple">.</span></div>
    <div class="step-text">Define workflow and connect data sources</div>
  </div>
  <div class="step-card">
    <div class="step-number">2<span class="dot-yellow">.</span></div>
    <div class="step-text">Build automations with the no-code editor</div>
  </div>
  <div class="step-card">
    <div class="step-number">3<span class="dot-green">.</span></div>
    <div class="step-text">Ship and monitor in real time</div>
  </div>
</div>
```

Dot colors: `.dot-purple`, `.dot-yellow`, `.dot-green`, `.dot-red` (`.dot-blue` is an alias for purple).

---

### Chapter / Agenda Cards

```html
<!-- Use inside tmpl-features or tmpl-twocol for agenda slides -->
<div class="chapter-card">
  <div class="number-circle">1</div>
  <div class="chapter-text">Introduction <span>— Opening remarks</span></div>
</div>
<div class="chapter-card">
  <div class="number-circle">2</div>
  <div class="chapter-text">Product Demo <span>— Live walkthrough</span></div>
</div>
```

`.number-circle` = 7vmin purple circle with centered number. `.chapter-text span` renders in secondary color for subtitles.

---

### Speaker / Presenter

```html
<!-- Single speaker cover (tmpl-cover-speaker) -->
<div class="speaker-top-card">
  <svg class="monday-logo"><!-- inline logo --></svg>
  <h1 class="text-display">The <span class="highlight--bold">speaker</span> opening slide.</h1>
</div>
<div class="speaker-bottom">
  <div class="profile-circle profile-circle-lg">
    <!-- inline portrait placeholder SVG or <img> -->
  </div>
  <div class="speaker-info-card">
    <span class="speaker-name">Jane Smith</span>
    <span class="speaker-role">Product Manager</span>
  </div>
</div>

<!-- Two speakers cover (tmpl-cover-speakers) -->
<div class="speaker-top-card"><!-- same as above --></div>
<div class="speaker-bottom-grid">
  <div class="speaker-group">
    <div class="profile-circle profile-circle-md"><!-- portrait --></div>
    <div class="speaker-info-card">
      <span class="speaker-name">Jane Smith</span>
      <span class="speaker-role">Product Manager</span>
    </div>
  </div>
  <div class="speaker-group">
    <div class="profile-circle profile-circle-md"><!-- portrait --></div>
    <div class="speaker-info-card">
      <span class="speaker-name">John Smith</span>
      <span class="speaker-role">Engineering Lead</span>
    </div>
  </div>
</div>

<!-- Speaker detail slide (tmpl-speaker) -->
<div class="speaker-detail-text">
  <p class="speaker-intro">Hi, I'm</p>
  <h1 class="speaker-name-hero">Jane Smith</h1>
  <p class="speaker-bio">Role description, experience, or fun fact</p>
</div>
<div class="speaker-portrait">
  <div class="profile-circle profile-circle-xl"><!-- large portrait --></div>
</div>
```

Profile circle sizes: `.profile-circle-md` (22vmin), `.profile-circle-lg` (28vmin), `.profile-circle-xl` (72vmin). `.speaker-info-card` uses `--color-purple` background. `.speaker-name-hero` = 15vmin for dramatic name display.

---

### Quote / Testimonial

```html
<!-- Use with tmpl-quote template -->
<div class="quote-box">
  <span class="monday-icon quote-mark">&#xf00e;</span>
  <p class="quote-text">
    With monday.com, we're 30% more efficient at delivering
    hundreds of campaigns seen by millions of customers.
  </p>
  <div class="attribution">
    <span class="person-name">Tye Rapley-Hawkins</span>
    <span class="person-title">Head of Delivery</span>
    <div class="company">
      <span class="company-name">Telefonica</span>
    </div>
  </div>
</div>
```

`.quote-mark` is positioned absolute, colored `--color-purple` via `currentColor`. `.quote-text` uses `--text-h2` at semibold weight.

---

### Timeline

```html
<!-- Use with tmpl-timeline template -->
<h1>Product Roadmap</h1>
<div class="timeline-container">
  <div class="timeline-line"></div>
  <div class="timeline-point point-active">
    <div class="point-circle"></div>
    <div class="point-label">Q1 2025</div>
  </div>
  <div class="timeline-point">
    <div class="point-circle"></div>
    <div class="point-label">Q2 2025</div>
  </div>
  <!-- repeat for each milestone -->
</div>
```

`.timeline-line` = horizontal bar across full width. `.point-circle` = small circle on the line (border matches line width at 0.3vmin). `.point-active` adds a subtle glow behind the active point. `.point-label` is absolutely positioned below each dot.

---

### Data Table

```html
<div class="table-container">
  <!-- Header row — set same grid-template-columns as data rows -->
  <div class="table-row header-row" style="grid-template-columns: 2.5fr repeat(3, 1fr)">
    <div class="cell">Feature</div>
    <div class="cell">Q1</div>
    <div class="cell">Q2</div>
    <div class="cell">Q3</div>
  </div>
  <div class="data-rows-wrapper">
    <div class="table-row data-row" style="grid-template-columns: 2.5fr repeat(3, 1fr)">
      <div class="cell">AI Builder</div>
      <div class="cell" style="color:var(--color-green)">Done</div>
      <div class="cell" style="color:var(--color-purple)">In progress</div>
      <div class="cell" style="color:var(--color-text-muted)">—</div>
    </div>
    <!-- repeat rows -->
  </div>
</div>
```

Odd data rows receive `--color-surface` background automatically via `:nth-child(odd)`. Always set `grid-template-columns` inline on every `.table-row` (both header and data). Stagger entrance animation built in for up to 8 rows.

---

### Image Placeholder

Use `.img-placeholder` for any visual slot (screenshot, photo, illustration). Size it via the layout container:

```html
<div style="height:100%">
  <div class="img-placeholder" style="height:100%">
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" stroke-width="1.2">
      <rect x="2" y="3" width="20" height="14" rx="2"/>
      <line x1="8" y1="21" x2="16" y2="21"/>
      <line x1="12" y1="17" x2="12" y2="21"/>
    </svg>
    <span class="placeholder-label">[Product Screenshot]</span>
  </div>
</div>
```

Background is `--color-surface`, icon opacity is 40%, radius is `--radius-lg`. Light theme compatible — no changes needed.

> There is also a legacy `[data-image-placeholder]` attribute pattern in the CSS (auto-shows a faint icon via `::after`). Use `.img-placeholder` for new slides — it's explicit and works consistently.

---

### Code Block

```html
<div class="code-block">
  <pre><span class="code-comment"># Section heading</span>
<span class="code-key">key:</span> <span class="code-value">value</span>
<span class="code-heading">- item one</span></pre>
</div>
```

Use for technical slides, prompt previews, config examples. Monospace font (SF Mono / Fira Code), `--color-surface` background. Color spans: `.code-comment` (muted), `.code-key` (purple-light), `.code-value` (yellow), `.code-heading` (green).

---

### Other Text Components

```html
<!-- Pull quote -->
<p class="quote-text">"The platform <span class="em">every team</span> actually uses."</p>

<!-- Section tracker (top-left corner, absolute position) -->
<span class="part-label">PART 2 — SOLUTION</span>

<!-- Spectrum / progression bar -->
<div class="spectrum-bar">
  <div class="spectrum-segment" style="background:var(--color-surface)">Low</div>
  <div class="spectrum-segment" style="background:var(--color-purple)">Medium</div>
  <div class="spectrum-segment" style="background:var(--color-green)">High</div>
</div>

<!-- Code inside comparison panel -->
<div class="panel-code">const api = monday.init();</div>
```

---

## Animations

Four keyframes available in every generated deck:

| Keyframe | Effect | Used by |
|----------|--------|---------|
| `revealUp` | Fade in + rise 1.5vmin | General content entrance |
| `revealFade` | Fade in only | Subtle background elements |
| `chartBarGrow` | Scale from bottom | `.bar` elements (automatic) |
| `chartScaleIn` | Scale from center | `.pie-chart`, `.donut-chart` (automatic) |
| `chartFadeUp` | Fade in + rise | `.data-row` elements (automatic) |

Chart and table animations trigger automatically — no extra CSS needed. For general content, apply `revealUp` manually:

```css
.my-element { animation: revealUp 0.5s ease-out both; }
```

`prefers-reduced-motion` is respected — all animations collapse to instant when set.

---

## Design Rules (enforced by CSS lockdown blocks)

These rules are hard-enforced by the CSS. Violating them in HTML is overridden at render time:

1. **Font family** — `font-family: 'Poppins', sans-serif !important` applied to every element. Only `code`, `pre`, `.mono` use monospace.
2. **Letter spacing** — `letter-spacing: normal !important` on all `.slide-container *`. Never add custom tracking.
3. **No italics** — `em, i, .italic, [style*="italic"]` all render upright (`font-style: normal !important`).
4. **Headline tracking** — `letter-spacing: 0 !important; word-spacing: normal !important` on all heading elements and stat values.
5. **Two weights only** — weight tokens resolve to 400 or 600. There is no 300, 500, or 700 in this system.
6. **One highlight per headline** — `.highlight` = color only (never bold). `.highlight--bold` = weight only (never color). Never combine both on one span.
7. **No uppercase** — `text-transform: uppercase` is never used. Title Case or Sentence case only.
8. **No divider lines** — Never use `<div>` as a visual separator. Use `gap` for whitespace between elements.

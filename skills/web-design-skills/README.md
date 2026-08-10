# Web Design Skills

Skills for turning Figma designs into live, responsive, interactive web pages —
built headlessly through platform APIs, no manual canvas work required.

- [`figma-to-webflow-section`](./figma-to-webflow-section/) — build any Figma
  section (hero, feature grid, pricing, testimonials, nav, footer, CTA, card
  row) into a Webflow page via the Webflow Data API. Handles the full pipeline:
  reading the design, extracting tokens, uploading assets, creating styles,
  building the DOM, and adding responsive behavior plus vision-driven
  interactions (hover, focus, click, scroll, entrance/ambient animation). It
  encodes the non-obvious Webflow Data API behavior — silent breakpoint
  failures, longhand-only styles, the freeform-code path for responsive CSS, the
  two-step S3 asset upload — that otherwise costs many failed calls to
  rediscover.

Each skill lives in its own subfolder as a `SKILL.md` (the entry point) plus
`references/` (knowledge loaded on demand per phase) and any `scripts/`.

# 01 · Index (context-setting)

**Role:** first stage. Establish the shared ground rules for the whole run before any analysis or
building. Context only — no analysis, no code.

**Inputs:** the Figma source (single frame or multi-frame storyboard); any known preferences
(output format, looping, resolution). If the source is a raw figma.com link, route it through
`figma-mcp-detector` to reach the Figma MCP.

**Do:**
- Fix the **output format**: HTML/CSS/JS (GSAP allowed) is the default deliverable; MP4/GIF is an
  export concern (stage 07). If format/looping are already known, capture them into `run.exportPrefs`
  now; otherwise defer to stage 07 (don't silently assume).
- Set the **motion baseline** (the "motion-principles" binding): smooth `sine.inOut`/`power2.inOut`
  easing — never linear or abrupt; motion should make the product read as *grabbable and
  understandable*; restraint over excess. Detail lives in `gsap` + `motion` — point to them,
  don't restate.
- If a fixed stage is needed, note the target canvas so `frame-building` can emit it later.

**Output / handoff:** a context package `{figmaSource, outputFormat, motionBaseline→gsap+motion,
knownExportPrefs?}` → stage 02.

**QA:** none. **Standalone:** yes — use it to set up context for a hand-built animation.

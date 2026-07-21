# 07 · Export

**Role:** produce the final deliverable in the requested format(s) — raw HTML/CSS/JS, MP4, and/or GIF
— using Remotion for any video/GIF conversion, with a mandatory Export QA.

**Inputs:** the connected animation (06c); export preferences (format + looping). If not captured at
01, gather them now — do not assume silently.

**Do:**
- **A · Format decision.** HTML/MP4/GIF/multiple. If the user wants HTML/CSS/JS only, **stop here** —
  no conversion. Build the looping mechanism into the output if looping is requested.
  - **Single-file portable HTML (offer when the HTML is the deliverable).** Inline *everything* into
    one `.html` so it runs offline / double-clicked / pasted anywhere: base64-encode every asset into
    `data:` URIs, embed the substitute font via `@font-face` (base64 `woff2`), and inline the GSAP
    library and animation JS. No CDN, no relative asset paths. This is the shareable artifact; keep the
    multi-file source alongside it for editing.
- **B · Convert (video/GIF).** Rebuild in Remotion via `export-as-gif` (+ `remotion-best-practices`):
  ask/confirm dimensions/fps/format/size-limit; port the timeline to frame-based `f(useCurrentFrame())`
  (CSS transitions don't render); Node ≥18; assets in `remotion/public` via `staticFile()`; verify
  boundary/key stills before rendering video. Offer `--scale`/`--every-nth-frame` (or steer to MP4)
  if a GIF is too heavy.
- **C · Export QA (not optional).** Verify the exported output still matches the source animation —
  nothing dropped, corrupted, mistimed, or visually broken by conversion (compare boundary/key frames
  and the loop seam). On fail, **retry/adjust the conversion** (Remotion config) before assuming the
  upstream animation is at fault.

**Output / handoff:** the deliverable file(s) → stage 08. **Standalone:** yes — this is essentially
`export-as-gif` with an Export-QA wrapper; use it to render any finished animation.

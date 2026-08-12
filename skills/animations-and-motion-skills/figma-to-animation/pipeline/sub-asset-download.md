# Sub · Asset Download from Figma

**Role (conditional, parallel with SVG extraction; runs after 02, before 03):** download raster
assets (photos, icons, logos) from Figma so the animation is self-contained — not dependent on live
Figma links. Skip entirely if a frame has no raster assets.

**Inputs:** the frame analysis (02), which identifies which raster assets exist.

**Method:** use the **`figma-export-assets`** skill (top-level skill at `../../figma-export-assets/`)
— it is the canonical Figma asset extraction primitive and handles `colorProfile: 'SRGB'`,
`useAbsoluteBounds: true`, URL-expiry (curl immediately), naming, and visual integrity check
automatically. Call it with the raster format and scale that matches the asset's render size in the
animation (see key rules below). Refer to `frame-building` §4c only as supplementary context for
placement logic; all *download* work goes through `figma-export-assets`. Key rules:
- Download each asset **at the exact size it appears** in the animation — not an arbitrary export
  size — and **preserve its original aspect ratio** (no squash/stretch).
- **Detect the real format** (`file`): Figma frequently returns SVG bytes at a `.png` URL — rename
  to `.svg` or an `<img>` breaks silently. (Vectors should generally go through `sub-svg-extract`.)
- Downscale oversized source illustrations to the render size (a 4K image at ~120px is wasteful).
- Store locally in the project's asset folder, organized per frame.

**QA:** every asset downloaded (no broken/missing files), correct dimensions for its placement,
original aspect ratio preserved. A distorted/recreated asset causes stage-04 failures and needless
fix loops — get it right here.

**Output / handoff:** local asset folder → stage 03. **Standalone:** yes.

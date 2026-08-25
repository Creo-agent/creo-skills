# Sub · Video Generation from Images

**Role (optional, nested, conditional; runs around stage 03):** replace a qualifying static image
(a person, illustration, landscape, etc.) with a short generated video via an image-to-video API,
matched to the original placement. **Off by default** — runs only when a user explicitly flags an
image AND a provider is configured.

**Status:** provider is **stubbed / configurable** — see `references/providers.md`. No default
provider or credentials are wired (project decision: "leave it for now").

**Inputs:** the source image (already downloaded by `sub-asset-download` at correct size/aspect);
the configured provider block.

**Method:**
1. Interpret the image's actual content and write a generation prompt from it.
2. Send `{imagePath, prompt, aspectRatio: match-source, durationSec, fps}` to the configured provider
   adapter (Veo / Omni / custom HTTP) — provider chosen by config, **never hardcoded**; API key from
   an env var, never inline.
3. Embed the returned video in place of the image, occupying the layout box **exactly** as the image
   did — no distortion, no letterboxing.

**QA (lightweight):** confirm the returned video matches the intended content and the aspect ratio
before it replaces the image.

**Output / handoff:** the frame with its image swapped for a video → continues stage 03.
**Standalone:** yes — swap one image for a generated video at matching aspect ratio.

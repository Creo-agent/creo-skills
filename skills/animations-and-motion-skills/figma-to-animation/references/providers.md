# Video-generation providers (sub-video-gen) — configurable, currently stubbed

The `sub-video-gen` sub-skill sends a qualifying static image + a generated prompt to an
image-to-video API and swaps the image for the returned video at the **exact same aspect ratio and
placement** (no distortion, no letterboxing). The provider is a **configuration choice, not
hardcoded** — switching providers must not require rewriting the sub-skill.

> **Status: stubbed.** No default provider or credentials are wired yet (per project decision:
> "leave it for now"). The sub-skill is disabled by default and only runs when a user explicitly
> flags an image for video generation AND a provider block below is filled in.

## Config shape
Set the active provider in the run config (`<project>/.f2a/run.json` → `videoGen`):
```jsonc
videoGen: {
  enabled: false,              // must be true AND an image flagged to run
  provider: "veo",             // key into the table below
  apiKeyEnv: "VIDEO_GEN_API_KEY", // env var name holding the key — never inline the key
  defaults: { aspectRatio: "match-source", durationSec: 4, fps: 30 }
}
```

## Provider adapters (fill in when adopting one)
| key | provider | endpoint / SDK | notes |
|---|---|---|---|
| `veo` | Google Veo | *(TBD)* | text+image→video; confirm aspect-ratio control |
| `omni` | Google Omni | *(TBD)* | *(TBD)* |
| `custom` | any HTTP API | `POST` `{image, prompt, aspectRatio, durationSec}` → `{videoUrl}` | generic adapter |

Each adapter must accept `{imagePath, prompt, aspectRatio, durationSec, fps}` and return a local
video path. Aspect ratio defaults to the source image's exact ratio.

## Hard requirements (regardless of provider)
- **Aspect ratio preserved exactly** — the video occupies the layout box exactly as the image did.
- **Content matches intent** — the generation prompt is derived from the image's actual content;
  the returned video is sanity-checked (content + aspect) before it replaces the image.
- **Credentials via env var only** — never inline an API key in the skill or run config; the user
  supplies the key and the provider through their own configuration.

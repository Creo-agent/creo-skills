# Skill: nano-banana-image-gen

Generate images using Google's Nano Banana / Gemini image generation API.

## When to use this skill
- Someone asks Creo to generate, create, or produce an image from a text description
- Image editing is needed: modifying an existing image via a text instruction
- Creative asset generation (ads, mockups, product shots, illustrations)
- Multi-turn iterative image editing (e.g. "now make it darker", "add a logo")

---

## Model Reference

| Model | API ID | Best for | Resolution | Cost/img |
|-------|--------|----------|------------|----------|
| **Nano Banana 2 Lite** | `gemini-3.1-flash-lite-image` | Speed & scale, bulk generation | 1K | ~$0.034 |
| **Nano Banana 2** | `gemini-3.1-flash-image` | General use, 4K, search grounding | 512px–4K | ~$0.045–$0.151 |
| **Nano Banana Pro** | `gemini-3-pro-image` | Complex visual tasks, professional assets | 1K–4K | ~$0.134 |

**Default choice:** `gemini-3.1-flash-image` (Nano Banana 2) — best balance of quality, speed, and cost.
Use `gemini-3-pro-image` (Nano Banana Pro) when the requester needs a high-fidelity production asset or the prompt is complex/detailed.

---

## Authentication

`GEMINI_API_KEY` is already in `slack-claude-agent/.env`. It's available as `process.env.GEMINI_API_KEY` at runtime.

**Never include the API key value in a Slack reply.**

---

## API: The Interactions Endpoint (Recommended)

All Nano Banana models use the new **Interactions API**, not the legacy `generateContent` endpoint.

### Endpoint
```
POST https://generativelanguage.googleapis.com/v1beta/interactions
```

### Authentication header
```
x-goog-api-key: $GEMINI_API_KEY
```

---

## Code Examples

### Text-to-Image — Node.js (SDK)

```javascript
import { GoogleGenAI } from "@google/genai";
import { writeFileSync } from "fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const interaction = await ai.interactions.create({
  model: "gemini-3.1-flash-image",
  input: "A clean product photo of a wooden desk lamp against a white background",
  response_format: {
    type: "image",
    mime_type: "image/png",
    aspect_ratio: "1:1",
    image_size: "2K"
  }
});

const buffer = Buffer.from(interaction.output_image.data, "base64");
writeFileSync("output.png", buffer);
```

### Text-to-Image — REST (curl)

```bash
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-flash-image",
    "input": [
      {"type": "text", "text": "A clean product photo of a wooden desk lamp"}
    ],
    "response_format": {
      "type": "image",
      "mime_type": "image/png",
      "aspect_ratio": "1:1",
      "image_size": "2K"
    }
  }'
```

### Image Editing — Node.js (existing image + instruction)

```javascript
import { readFileSync, writeFileSync } from "fs";

const imageBytes = readFileSync("source.png");
const base64Image = imageBytes.toString("base64");

const interaction = await ai.interactions.create({
  model: "gemini-3.1-flash-image",
  input: [
    { type: "text", text: "Remove the background and make it transparent" },
    { type: "image", data: base64Image, mime_type: "image/png" }
  ]
});

const buffer = Buffer.from(interaction.output_image.data, "base64");
writeFileSync("output.png", buffer);
```

### Multi-Turn Editing (chained edits)

```javascript
// First edit
const interaction1 = await ai.interactions.create({
  model: "gemini-3.1-flash-image",
  input: "Generate a minimalist monday.com banner, dark blue background",
  response_format: { type: "image", aspect_ratio: "16:9", image_size: "2K" }
});

// Second edit referencing the first
const interaction2 = await ai.interactions.create({
  model: "gemini-3.1-flash-image",
  input: "Add the text 'Work OS' in large white letters at the top",
  previous_interaction_id: interaction1.id,
  response_format: { type: "image", aspect_ratio: "16:9", image_size: "2K" }
});

const buffer = Buffer.from(interaction2.output_image.data, "base64");
writeFileSync("banner-final.png", buffer);
```

### Nano Banana Pro — High-Quality Asset

```javascript
const interaction = await ai.interactions.create({
  model: "gemini-3-pro-image",
  input: "Professional ad banner for a B2B SaaS product. Clean layout, monday.com brand colors (dark navy, vibrant coral), tagline 'Work smarter together', 16:9 format",
  response_format: {
    type: "image",
    mime_type: "image/png",
    aspect_ratio: "16:9",
    image_size: "4K"
  }
});
```

---

## Response Handling

```javascript
// Standard output
const base64Data = interaction.output_image.data;
const buffer = Buffer.from(base64Data, "base64");

// For interleaved content (multiple text + images in one response)
for (const step of interaction.steps) {
  if (step.type === "model_output") {
    for (const block of step.content) {
      if (block.type === "image") {
        const img = Buffer.from(block.data, "base64");
        // save img...
      }
    }
  }
}
```

---

## Key Parameters

### `response_format`
| Parameter | Options | Notes |
|-----------|---------|-------|
| `type` | `"image"` | Always "image" for image gen |
| `mime_type` | `"image/png"`, `"image/jpeg"` | PNG preferred for transparency |
| `aspect_ratio` | `"1:1"`, `"16:9"`, `"9:16"`, `"4:3"`, `"3:4"`, `"3:2"`, `"2:3"`, `"4:5"`, `"5:4"`, `"21:9"` | Use string exactly |
| `image_size` | `"512px"`, `"1K"`, `"2K"`, `"4K"` | **Must be uppercase K** (lowercase rejected) |

### Ad/Social Media format mapping
| Format | aspect_ratio | image_size |
|--------|-------------|------------|
| Square (1080×1080) | `"1:1"` | `"1K"` or `"2K"` |
| Landscape banner (1920×1080) | `"16:9"` | `"2K"` |
| Vertical story (1080×1920) | `"9:16"` | `"2K"` |
| Leaderboard (728×90) | `"21:9"` | `"1K"` |
| Portrait (4:5) | `"4:5"` | `"1K"` |

---

## Advanced Features

### Google Search Grounding (Nano Banana 2 only)
```javascript
const interaction = await ai.interactions.create({
  model: "gemini-3.1-flash-image",
  input: "Visualize the latest design trends in B2B SaaS dashboards",
  tools: [{ type: "google_search" }]
});
```

### Reference Images (up to 14 images for style consistency)
```javascript
input: [
  { type: "text", text: "Create a new image in the same visual style" },
  { type: "image", data: base64Ref1, mime_type: "image/jpeg" },
  { type: "image", data: base64Ref2, mime_type: "image/jpeg" }
]
```

### Thinking Level (Nano Banana 2 only)
```javascript
generation_config: { thinking_level: "high" }  // or "minimal" (default, faster)
```

---

## Saving Files — Creo Convention

Generated images follow the same file-naming-and-versioning convention as all deliverables:
- **Durable copy** → `Creative Operations/<Person>/<Project>/<description>-v<NN>.png`
- **Slack reply copy** → `.slack-outputs/<description>-v<NN>.png` (auto-uploaded, wiped next task)

```javascript
const path = require("path");
const deliverableDir = "/Users/creativeagent/Creative Operations/<Person>/<Project>";
const fileName = "banner-v01.png"; // check existing files for next version number

writeFileSync(path.join(deliverableDir, fileName), buffer);
writeFileSync(path.join(projectDir, ".slack-outputs", fileName), buffer); // copy for Slack
```

---

## Error Handling

```javascript
try {
  const interaction = await ai.interactions.create({ ... });
  // ...
} catch (err) {
  if (err.status === 429) {
    // Rate limit — retry with backoff
  } else if (err.status === 400) {
    // Policy violation — prompt was rejected, rephrase
  } else if (err.status === 503) {
    // Service outage — retry later
  }
}
```

---

## Prompt Engineering Tips

1. **Be specific:** Subject + style + lighting + composition in one sentence.  
   ✅ "Minimalist product photo, white background, soft studio lighting, shallow depth of field"  
   ❌ "Nice photo of a product"

2. **State the format:** Include desired dimensions/use in the prompt (e.g. "16:9 banner", "square social post").

3. **Reference brand:** For monday.com work, include color cues: "dark navy (#1F1F3B), vibrant coral (#FF7575), clean sans-serif typography".

4. **Avoid negatives:** Describe what you want, not what to avoid — negative phrasing often backfires.

5. **Iterate:** Use `previous_interaction_id` for targeted refinements rather than rewriting the full prompt each time.

---

## SDK Installation

```bash
# Node.js (already in slack-claude-agent)
npm install @google/genai

# Python (if needed for scripting)
pip install google-genai Pillow
```

SDK minimum versions: `@google/genai >= 0.21.0` (Node) | `google-genai >= 0.8.0` (Python)

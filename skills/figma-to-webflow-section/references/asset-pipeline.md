# Asset pipeline — Figma download → Webflow upload

Every section with a logo, photo, icon, or illustration goes through this. Two
things bite people: Figma download URLs expire almost immediately, and the
Webflow upload is a two-step S3 flow.

## Step 1 — Pull the asset out of Figma

Use `download_assets` scoped to the image node. It returns a **presigned URL
that expires within seconds.** `curl` it to a local file in the *same step* —
never store the URL to fetch "later."

```bash
curl -sL -o "/tmp/asset-name.png" "<presigned-url-from-download_assets>"
```

If you need multiple assets, download and curl each immediately rather than
collecting URLs first.

## Step 2 — Fix logos on non-transparent backgrounds

Brand logos often ship on an opaque background (e.g. a light gray card). Dropped
onto a dark section, they render as a visible box.

Check first: sample the corner pixels. If they aren't transparent, the logo
needs processing.

Run the bundled script — it maps neutral (near-background) pixels to transparent
white while preserving the colored parts of the mark:

```bash
python scripts/logo-fix.py /tmp/logo.png /tmp/logo-white.png
```

See `scripts/logo-fix.py` for the saturation-gate approach (colored pixels kept;
neutral pixels turned white with alpha proportional to brightness above the
background). Tune the thresholds in the script if a specific logo needs it.

## Step 3 — Upload to Webflow (two-step S3)

`data_assets_tool → create_asset` does not take bytes directly. It's two steps:

1. Call `create_asset` with `site_id`, `file_name`, and `file_hash` (the MD5 of
   the file, hex). It returns an `uploadUrl` and an `uploadDetails` object.

   ```bash
   md5 -q /tmp/logo-white.png   # macOS; use md5sum on Linux
   ```

2. POST the file bytes to `uploadUrl` as a **multipart form** that includes
   **every field** from `uploadDetails` (they're the S3 signed-POST fields),
   with the file part last:

   ```bash
   curl -X POST "<uploadUrl>" \
     -F "key=<uploadDetails.key>" \
     -F "...=<each uploadDetails field>" \
     -F "file=@/tmp/logo-white.png"
   ```

Record the returned **asset id** — you'll pass it to
`data_element_tool → set_image_asset` in Phase 5.

## Reminders

- Alt text via `set_attributes` is unreliable (see `api-gotchas.md` #4) — set it
  via the `use_figma` plugin path or flag it to the user.
- Webflow `upload_assets` (the Figma-side plugin tool) does **not** accept SVG.
  For SVG use `use_figma` with `figma.createNodeFromSvg()`, or rebuild the mark
  as CSS.

#!/usr/bin/env python3
"""
visual_diff.py — Pixel-level visual diff between a Figma reference screenshot and a built HTML screenshot.

Produces:
  1. Side-by-side image with red bounding boxes around diff regions (always)
  2. Overlay blend at 50% opacity (only when diff > threshold)
  3. Delta heatmap — white = identical, red = different (only when diff > threshold)
  4. Structured JSON fix brief mapping diff regions to DOM areas

Usage
-----
  python3 visual_diff.py \\
    --figma  /path/to/figma-screenshot.png \\
    --html   /path/to/html-screenshot.png \\
    --output /path/to/output-dir/ \\
    [--threshold 5.0] \\
    [--section-name hero] \\
    [--dom-map /path/to/dom-map.json] \\
    [--json]

The --dom-map file (optional) is a JSON array of {selector, label, x, y, width, height} objects
describing the bounding boxes of key DOM elements in the HTML screenshot. When provided, diff
regions are mapped to the closest DOM element, so the fix brief says "CTA button area" instead
of just "pixels at x:900, y:50". Generate it with Playwright before running this tool:

  page.evaluate('''() => [...document.querySelectorAll('[data-section] *')].map(el => {
    const r = el.getBoundingClientRect();
    return { selector: el.tagName + (el.className ? '.' + [...el.classList].join('.') : ''),
             label: el.getAttribute('aria-label') || el.textContent?.trim().slice(0,30) || '',
             x: Math.round(r.x), y: Math.round(r.y),
             width: Math.round(r.width), height: Math.round(r.height) };
  }).filter(d => d.width > 10 && d.height > 10)''')

Exit codes: 0 = diff within threshold, 1 = diff exceeds threshold, 2 = error.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

try:
    from skimage.metrics import structural_similarity as ssim
    HAS_SSIM = True
except ImportError:
    HAS_SSIM = False


# ---------------------------------------------------------------------------  helpers

def load_and_normalize(path_a: str, path_b: str):
    """Load two images and resize the smaller to match the larger's dimensions."""
    img_a = Image.open(path_a).convert("RGB")
    img_b = Image.open(path_b).convert("RGB")

    # If sizes differ, resize img_b (HTML) to match img_a (Figma = source of truth)
    if img_a.size != img_b.size:
        img_b = img_b.resize(img_a.size, Image.LANCZOS)

    return img_a, img_b


def compute_diff_mask(img_a: Image.Image, img_b: Image.Image, blur_radius: int = 2,
                      sensitivity: int = 30) -> Image.Image:
    """Compute a binary diff mask. Blur to suppress anti-aliasing noise.
    sensitivity: per-channel threshold (0-255) — pixels with diff < sensitivity are considered identical."""
    diff = ImageChops.difference(img_a, img_b)
    # Convert to grayscale for thresholding
    gray = diff.convert("L")
    # Blur to suppress anti-aliasing edge noise
    if blur_radius > 0:
        gray = gray.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    # Threshold: anything above sensitivity is a real diff
    mask = gray.point(lambda p: 255 if p > sensitivity else 0, mode="1")
    return mask


def find_diff_regions(mask: Image.Image, min_area: int = 100):
    """Find contiguous diff regions using connected component labeling.
    Returns list of (x, y, w, h) bounding boxes."""
    arr = np.array(mask, dtype=np.uint8)
    if arr.max() == 0:
        return []

    # Simple flood-fill connected components
    from scipy import ndimage
    labeled, num_features = ndimage.label(arr)

    regions = []
    for i in range(1, num_features + 1):
        ys, xs = np.where(labeled == i)
        area = len(xs)
        if area < min_area:
            continue
        x_min, x_max = int(xs.min()), int(xs.max())
        y_min, y_max = int(ys.min()), int(ys.max())
        regions.append({
            "x": x_min, "y": y_min,
            "width": x_max - x_min + 1,
            "height": y_max - y_min + 1,
            "area_px": area,
        })

    # Sort by area descending (biggest diffs first)
    regions.sort(key=lambda r: r["area_px"], reverse=True)
    return regions


def compute_ssim_score(img_a: Image.Image, img_b: Image.Image) -> float:
    """Compute structural similarity index (0-100%). Requires scikit-image."""
    if not HAS_SSIM:
        return -1.0
    a = np.array(img_a)
    b = np.array(img_b)
    # Use multichannel for RGB
    score, _ = ssim(a, b, full=True, channel_axis=2)
    return round(score * 100, 2)


def compute_pixel_diff_pct(mask: Image.Image) -> float:
    """Percentage of pixels that differ."""
    arr = np.array(mask, dtype=np.uint8)
    total = arr.size
    diff_count = np.count_nonzero(arr)
    return round(diff_count / total * 100, 2)


# ---------------------------------------------------------------------------  outputs

def make_side_by_side(img_a: Image.Image, img_b: Image.Image, regions: list,
                      padding: int = 20) -> Image.Image:
    """Figma left, HTML right, red boxes on diff regions (drawn on both sides)."""
    w, h = img_a.size
    canvas = Image.new("RGB", (w * 2 + padding, h), (40, 40, 40))
    canvas.paste(img_a, (0, 0))
    canvas.paste(img_b, (w + padding, 0))

    draw = ImageDraw.Draw(canvas)

    # Labels
    draw.rectangle([(0, 0), (120, 28)], fill=(0, 0, 0, 180))
    draw.text((8, 6), "FIGMA REF", fill=(255, 255, 255))
    draw.rectangle([(w + padding, 0), (w + padding + 120, 28)], fill=(0, 0, 0, 180))
    draw.text((w + padding + 8, 6), "BUILT HTML", fill=(255, 255, 255))

    for r in regions:
        x, y, rw, rh = r["x"], r["y"], r["width"], r["height"]
        # Draw on Figma side
        draw.rectangle([(x - 2, y - 2), (x + rw + 2, y + rh + 2)],
                       outline=(255, 40, 40), width=3)
        # Draw on HTML side
        draw.rectangle([(w + padding + x - 2, y - 2), (w + padding + x + rw + 2, y + rh + 2)],
                       outline=(255, 40, 40), width=3)

    return canvas


def make_overlay_blend(img_a: Image.Image, img_b: Image.Image) -> Image.Image:
    """50% opacity merge of both images."""
    return Image.blend(img_a, img_b, alpha=0.5)


def make_heatmap(mask: Image.Image, img_b: Image.Image) -> Image.Image:
    """Delta heatmap: base image dimmed, diff regions highlighted in red."""
    # Dim the HTML screenshot
    base = img_b.copy()
    base = Image.blend(base, Image.new("RGB", base.size, (0, 0, 0)), alpha=0.6)

    # Convert mask to proper 0-255 range (mode "1" gives 0/1, need 0/255)
    mask_arr = np.array(mask.convert("L"), dtype=np.uint8)
    mask_arr = (mask_arr > 0).astype(np.uint8) * 255

    # Create red overlay
    red = np.zeros((*mask_arr.shape, 3), dtype=np.uint8)
    red[mask_arr > 0] = [255, 60, 60]
    red_img = Image.fromarray(red)

    # Use full-opacity mask for compositing
    alpha_mask = Image.fromarray(mask_arr)

    # Composite: red regions at full visibility on top of dimmed base
    result = base.copy()
    result.paste(red_img, mask=alpha_mask)
    return result


# ---------------------------------------------------------------------------  DOM mapping

def map_regions_to_dom(regions: list, dom_map: list) -> list:
    """For each diff region, find the best-matching DOM element from the dom_map."""
    if not dom_map:
        return regions

    for region in regions:
        rx, ry = region["x"] + region["width"] / 2, region["y"] + region["height"] / 2
        best = None
        best_area = float("inf")

        for elem in dom_map:
            ex, ey = elem["x"], elem["y"]
            ew, eh = elem["width"], elem["height"]

            # Check if region center falls inside this element
            if ex <= rx <= ex + ew and ey <= ry <= ey + eh:
                area = ew * eh
                # Prefer the smallest containing element (most specific)
                if area < best_area:
                    best = elem
                    best_area = area

        if best:
            region["dom_selector"] = best.get("selector", "")
            region["dom_label"] = best.get("label", "")
        else:
            region["dom_selector"] = "(no match)"
            region["dom_label"] = ""

    return regions


def classify_diff_type(img_a: Image.Image, img_b: Image.Image, region: dict) -> str:
    """Basic classification of what type of difference a region represents."""
    x, y, w, h = region["x"], region["y"], region["width"], region["height"]

    crop_a = np.array(img_a.crop((x, y, x + w, y + h)), dtype=np.float64)
    crop_b = np.array(img_b.crop((x, y, x + w, y + h)), dtype=np.float64)

    # Check if it's primarily a color shift (same structure, different colors)
    # Compare luminance patterns
    lum_a = 0.299 * crop_a[:, :, 0] + 0.587 * crop_a[:, :, 1] + 0.114 * crop_a[:, :, 2]
    lum_b = 0.299 * crop_b[:, :, 0] + 0.587 * crop_b[:, :, 1] + 0.114 * crop_b[:, :, 2]

    lum_diff = np.mean(np.abs(lum_a - lum_b))
    color_diff = np.mean(np.abs(crop_a - crop_b))

    # If luminance is similar but color differs → color shift
    if lum_diff < 15 and color_diff > 20:
        return "color"

    # If the region is tall and narrow or wide and short → likely spacing/alignment
    aspect = w / max(h, 1)
    if aspect > 5 or aspect < 0.2:
        return "spacing"

    # If one side is mostly empty (white/bg) and the other has content → missing element
    mean_a = np.mean(crop_a)
    mean_b = np.mean(crop_b)
    if abs(mean_a - mean_b) > 100:
        return "missing_element"

    # Default: size/layout mismatch
    return "layout"


# ---------------------------------------------------------------------------  fix brief

def build_fix_brief(regions: list, section_name: str, ssim_score: float,
                    pixel_diff_pct: float, threshold: float) -> dict:
    """Build the structured fix brief that the build agent uses to know what to fix."""
    status = "PASS" if pixel_diff_pct <= threshold else "NEEDS_FIX"

    brief = {
        "section": section_name,
        "ssim_score": ssim_score,
        "pixel_diff_pct": pixel_diff_pct,
        "threshold_pct": threshold,
        "status": status,
        "regions": [],
    }

    for i, r in enumerate(regions, 1):
        entry = {
            "id": i,
            "bounds": {"x": r["x"], "y": r["y"], "w": r["width"], "h": r["height"]},
            "area_px": r["area_px"],
            "diff_type": r.get("diff_type", "unknown"),
        }
        if "dom_selector" in r:
            entry["dom_element"] = r["dom_selector"]
            entry["dom_label"] = r["dom_label"]
        brief["regions"].append(entry)

    return brief


# ---------------------------------------------------------------------------  main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--figma", required=True, help="Path to the Figma reference screenshot")
    ap.add_argument("--html", required=True, help="Path to the built HTML screenshot")
    ap.add_argument("--output", required=True, help="Output directory for diff images + report")
    ap.add_argument("--threshold", type=float, default=5.0,
                    help="Pixel diff %% threshold — above this triggers overlay + heatmap (default: 5.0)")
    ap.add_argument("--section-name", default="section",
                    help="Section name for the fix brief (default: 'section')")
    ap.add_argument("--dom-map", help="Optional JSON file with DOM element bounding boxes")
    ap.add_argument("--sensitivity", type=int, default=30,
                    help="Per-channel pixel sensitivity threshold 0-255 (default: 30, "
                         "higher = more tolerant of anti-aliasing)")
    ap.add_argument("--min-region-area", type=int, default=100,
                    help="Minimum pixel area for a diff region to be reported (default: 100)")
    ap.add_argument("--json", action="store_true", help="Print fix brief as JSON to stdout")

    args = ap.parse_args()
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Validate inputs
    for p, label in [(args.figma, "Figma"), (args.html, "HTML")]:
        if not Path(p).exists():
            print(f"error: {label} screenshot not found: {p}", file=sys.stderr)
            sys.exit(2)

    # Load + normalize
    img_figma, img_html = load_and_normalize(args.figma, args.html)

    # Compute diff mask
    mask = compute_diff_mask(img_figma, img_html, sensitivity=args.sensitivity)

    # Metrics
    pixel_diff_pct = compute_pixel_diff_pct(mask)
    ssim_score = compute_ssim_score(img_figma, img_html)

    # Find regions
    try:
        regions = find_diff_regions(mask, min_area=args.min_region_area)
    except ImportError:
        print("warning: scipy not installed — skipping region detection, reporting global diff only",
              file=sys.stderr)
        regions = []

    # Classify each region
    for r in regions:
        r["diff_type"] = classify_diff_type(img_figma, img_html, r)

    # Map to DOM if available
    dom_map = None
    if args.dom_map:
        with open(args.dom_map) as f:
            dom_map = json.load(f)
        regions = map_regions_to_dom(regions, dom_map)

    # Always: side-by-side
    sbs = make_side_by_side(img_figma, img_html, regions)
    sbs_path = out_dir / f"{args.section_name}-diff-side-by-side.png"
    sbs.save(sbs_path)

    outputs = [str(sbs_path)]

    # If diff exceeds threshold: also overlay + heatmap
    exceeds = pixel_diff_pct > args.threshold
    if exceeds:
        overlay = make_overlay_blend(img_figma, img_html)
        overlay_path = out_dir / f"{args.section_name}-diff-overlay.png"
        overlay.save(overlay_path)
        outputs.append(str(overlay_path))

        heatmap = make_heatmap(mask, img_html)
        heatmap_path = out_dir / f"{args.section_name}-diff-heatmap.png"
        heatmap.save(heatmap_path)
        outputs.append(str(heatmap_path))

    # Build fix brief
    brief = build_fix_brief(regions, args.section_name, ssim_score, pixel_diff_pct, args.threshold)
    brief["outputs"] = outputs

    brief_path = out_dir / f"{args.section_name}-diff-report.json"
    with open(brief_path, "w") as f:
        json.dump(brief, f, indent=2)

    # Output
    if args.json:
        print(json.dumps(brief, indent=2))
    else:
        print(f"# Visual Diff: {args.section_name}")
        print(f"  SSIM Score:     {ssim_score}%")
        print(f"  Pixel Diff:     {pixel_diff_pct}%")
        print(f"  Threshold:      {args.threshold}%")
        print(f"  Status:         {brief['status']}")
        print(f"  Diff Regions:   {len(regions)}")
        print()
        if regions:
            print("  Regions:")
            for i, r in enumerate(regions, 1):
                dom = f" → {r.get('dom_selector', '?')} ({r.get('dom_label', '')[:30]})" if dom_map else ""
                print(f"    {i}. [{r['diff_type']}] x:{r['x']} y:{r['y']} "
                      f"{r['width']}×{r['height']} ({r['area_px']}px){dom}")
        print()
        print(f"  Outputs: {', '.join(outputs)}")
        print(f"  Report:  {brief_path}")

    sys.exit(1 if exceeds else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
logo-fix.py — make a logo transparent for placement on a dark (or any) section.

Brand logos often ship on an opaque near-white/gray card. Dropped onto a dark
Webflow section, that card renders as a visible box around the mark. This script
removes the flat background while preserving the colored parts of the logo, and
turns the neutral (wordmark/near-background) pixels into white with alpha
proportional to how far above the background luminance they sit — so a white
wordmark stays crisp instead of being erased along with the background.

Approach (saturation gate):
  - High-saturation pixels (the colored icon) are kept as-is, fully opaque.
  - Neutral pixels are mapped to white, alpha = how far their brightness rises
    above the background luminance. Background-level pixels become transparent;
    bright wordmark pixels stay near-opaque white.

Usage:
    python logo-fix.py input.png output.png
    python logo-fix.py input.png output.png --bg 245 --sat 30 --span 10

Tunables:
    --bg    background luminance to treat as "empty" (default 245, i.e. #f5f5f5)
    --sat   saturation threshold; >= this is treated as colored/kept (default 30)
    --span  brightness range above --bg mapped from 0..255 alpha (default 10)

Requires Pillow:  pip install Pillow
"""
import argparse
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required. Install with: pip install Pillow")


def fix_logo(in_path, out_path, bg=245, sat_thresh=30, span=10):
    im = Image.open(in_path).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            sat = max(r, g, b) - min(r, g, b)
            if sat >= sat_thresh:
                # Colored pixel — part of the mark. Keep it opaque.
                px[x, y] = (r, g, b, 255)
            else:
                # Neutral pixel — map brightness above bg to white w/ alpha.
                v = (r + g + b) / 3
                alpha = int(round(max(0, min(255, (v - bg) / span * 255))))
                px[x, y] = (255, 255, 255, alpha)
    im.save(out_path)
    print(f"Wrote {out_path} ({w}x{h})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Make a logo transparent for dark sections.")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--bg", type=float, default=245)
    ap.add_argument("--sat", type=int, default=30)
    ap.add_argument("--span", type=float, default=10)
    args = ap.parse_args()
    fix_logo(args.input, args.output, bg=args.bg, sat_thresh=args.sat, span=args.span)

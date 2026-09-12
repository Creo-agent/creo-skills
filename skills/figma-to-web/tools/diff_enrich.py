#!/usr/bin/env python3
"""
diff_enrich.py — Enrich a visual_diff report with Figma-vs-HTML property comparisons.

Takes the diff report JSON from visual_diff.py and for each flagged region:
  1. Extracts the ACTUAL computed CSS from the built HTML (via Playwright)
  2. Extracts the EXPECTED values from the Figma API (node properties)
  3. Compares them and adds a "fixes" array to each region

The enriched report gives agents an actionable fix list:
  "Region 3 → .section-hero-btn: padding is 12px, Figma says 16px. Fix: padding: 16px."

Usage
-----
  python3 diff_enrich.py \\
    --report /path/to/hero-diff-report.json \\
    --url http://localhost:PORT/index.html \\
    --selector '[data-section="hero"]' \\
    --figma-file MzNZ4wipvZsdKDoxDU4spV \\
    --figma-node 1246:58821 \\
    [--figma-token TOKEN] \\
    [--json]

If --figma-token is omitted, reads from the FIGMA_TOKEN environment variable.

Exit codes: 0 = success, 1 = enrichment found actionable fixes, 2 = error.
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


# ---------------------------------------------------------------------------  Figma token

def get_figma_token(explicit_token=None):
    """Resolve Figma token from explicit arg or env var."""
    if explicit_token:
        return explicit_token

    env_token = os.environ.get("FIGMA_TOKEN")
    if env_token:
        return env_token

    return None


# ---------------------------------------------------------------------------  Figma API

def fetch_figma_node_properties(file_key, node_id, token):
    """Fetch a Figma node and its children with full properties."""
    import urllib.request

    url = f"https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}&depth=10"
    req = urllib.request.Request(url, headers={"X-Figma-Token": token})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"warning: Figma API call failed: {e}", file=sys.stderr)
        return None

    if "err" in data and data["err"]:
        print(f"warning: Figma API error: {data}", file=sys.stderr)
        return None

    # Get the node document
    node_key = node_id.replace("-", ":")
    if node_key not in data.get("nodes", {}):
        # Try with the original format
        for k in data.get("nodes", {}):
            if k.replace(":", "-") == node_id.replace(":", "-"):
                node_key = k
                break

    node_data = data.get("nodes", {}).get(node_key)
    if not node_data:
        print(f"warning: node {node_id} not found in Figma response", file=sys.stderr)
        return None

    return node_data["document"]


def flatten_figma_nodes(node, parent_bb=None):
    """Recursively flatten a Figma node tree into a list of {name, type, bb, styles}."""
    results = []
    bb = node.get("absoluteBoundingBox")
    if not bb:
        bb = node.get("absoluteRenderBounds")

    entry = {
        "name": node.get("name", ""),
        "type": node.get("type", ""),
        "id": node.get("id", ""),
    }

    if bb:
        # Convert to relative coordinates (relative to parent/section origin)
        entry["x"] = bb.get("x", 0)
        entry["y"] = bb.get("y", 0)
        entry["width"] = bb.get("width", 0)
        entry["height"] = bb.get("height", 0)

    # Extract style properties
    style = node.get("style", {})
    if style:
        entry["figma_styles"] = {
            "font_family": style.get("fontFamily"),
            "font_size": style.get("fontSize"),
            "font_weight": style.get("fontWeight"),
            "line_height_px": style.get("lineHeightPx"),
            "letter_spacing": style.get("letterSpacing"),
            "text_align": style.get("textAlignHorizontal"),
        }
        # Remove None values
        entry["figma_styles"] = {k: v for k, v in entry["figma_styles"].items() if v is not None}

    # Fills (colors)
    fills = node.get("fills", [])
    if fills:
        solid_fills = [f for f in fills if f.get("type") == "SOLID" and f.get("visible", True)]
        if solid_fills:
            c = solid_fills[0].get("color", {})
            r, g, b = int(c.get("r", 0) * 255), int(c.get("g", 0) * 255), int(c.get("b", 0) * 255)
            entry.setdefault("figma_styles", {})["color"] = f"rgb({r}, {g}, {b})"

    # Background fills (for frames)
    bg = node.get("backgroundColor")
    if bg:
        r, g, b = int(bg.get("r", 0) * 255), int(bg.get("g", 0) * 255), int(bg.get("b", 0) * 255)
        a = bg.get("a", 1)
        if a > 0.01:
            entry.setdefault("figma_styles", {})["background_color"] = f"rgb({r}, {g}, {b})"

    # Padding (from layout)
    for pad_key in ("paddingTop", "paddingRight", "paddingBottom", "paddingLeft"):
        val = node.get(pad_key)
        if val is not None and val > 0:
            entry.setdefault("figma_styles", {})[pad_key] = val

    # Item spacing (gap)
    gap = node.get("itemSpacing")
    if gap is not None and gap > 0:
        entry.setdefault("figma_styles", {})["gap"] = gap

    # Corner radius
    cr = node.get("cornerRadius")
    if cr is not None and cr > 0:
        entry.setdefault("figma_styles", {})["border_radius"] = cr

    results.append(entry)

    for child in node.get("children", []):
        results.extend(flatten_figma_nodes(child, bb))

    return results


def make_figma_coords_relative(nodes, section_node):
    """Convert absolute Figma coordinates to section-relative."""
    bb = section_node.get("absoluteBoundingBox") or section_node.get("absoluteRenderBounds", {})
    origin_x = bb.get("x", 0)
    origin_y = bb.get("y", 0)

    for node in nodes:
        if "x" in node:
            node["x"] = round(node["x"] - origin_x)
            node["y"] = round(node["y"] - origin_y)
            node["width"] = round(node["width"])
            node["height"] = round(node["height"])

    return nodes


# ---------------------------------------------------------------------------  HTML CSS extraction

def extract_computed_css(page, selector, section_selector):
    """Extract computed CSS for key elements in the section."""
    js = f"""() => {{
        const section = document.querySelector({json.dumps(section_selector)});
        if (!section) return [];
        const sRect = section.getBoundingClientRect();

        return [...section.querySelectorAll('*')].map(el => {{
            const r = el.getBoundingClientRect();
            if (r.width < 5 || r.height < 5) return null;

            const cs = window.getComputedStyle(el);
            return {{
                selector: el.tagName + (el.className ? '.' + [...el.classList].join('.') : ''),
                x: Math.round(r.x - sRect.x),
                y: Math.round(r.y - sRect.y),
                width: Math.round(r.width),
                height: Math.round(r.height),
                css: {{
                    font_family: cs.fontFamily?.split(',')[0]?.replace(/['"]/g, '').trim(),
                    font_size: cs.fontSize,
                    font_weight: cs.fontWeight,
                    line_height: cs.lineHeight,
                    letter_spacing: cs.letterSpacing,
                    color: cs.color,
                    background_color: cs.backgroundColor,
                    padding_top: cs.paddingTop,
                    padding_right: cs.paddingRight,
                    padding_bottom: cs.paddingBottom,
                    padding_left: cs.paddingLeft,
                    gap: cs.gap,
                    border_radius: cs.borderRadius,
                    text_align: cs.textAlign,
                }},
                text: el.textContent?.trim().slice(0, 40) || ''
            }};
        }}).filter(Boolean);
    }}"""
    return page.evaluate(js)


# ---------------------------------------------------------------------------  matching + comparison

def match_figma_to_dom(figma_nodes, html_elements, region):
    """Find the best Figma node and HTML element for a diff region."""
    rx = region["bounds"]["x"]
    ry = region["bounds"]["y"]
    rw = region["bounds"]["w"]
    rh = region["bounds"]["h"]
    rcx, rcy = rx + rw / 2, ry + rh / 2

    # Find closest Figma node by center overlap
    best_figma = None
    best_figma_area = float("inf")
    for fn in figma_nodes:
        if "x" not in fn or fn.get("width", 0) < 5:
            continue
        fx, fy, fw, fh = fn["x"], fn["y"], fn["width"], fn["height"]
        if fx <= rcx <= fx + fw and fy <= rcy <= fy + fh:
            area = fw * fh
            if area < best_figma_area:
                best_figma = fn
                best_figma_area = area

    # Find closest HTML element
    best_html = None
    best_html_area = float("inf")
    for he in html_elements:
        hx, hy, hw, hh = he["x"], he["y"], he["width"], he["height"]
        if hx <= rcx <= hx + hw and hy <= rcy <= hy + hh:
            area = hw * hh
            if area < best_html_area:
                best_html = he
                best_html_area = area

    return best_figma, best_html


def _normalize_px(val):
    """Normalize pixel values for comparison: '32px' == '32.0px' == 32."""
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in ('normal', 'none', 'auto', ''):
        return s
    # Extract numeric part
    import re
    m = re.match(r'^([\d.]+)\s*px$', s)
    if m:
        return round(float(m.group(1)), 1)
    try:
        return round(float(s), 1)
    except (ValueError, TypeError):
        return s


def _px_equal(a, b, tolerance=1.5):
    """Check if two pixel values are close enough."""
    na, nb = _normalize_px(a), _normalize_px(b)
    if na is None or nb is None:
        return False
    if isinstance(na, (int, float)) and isinstance(nb, (int, float)):
        return abs(na - nb) <= tolerance
    return str(na) == str(nb)


def compare_properties(figma_node, html_element):
    """Compare Figma properties vs computed CSS and return a list of differences."""
    diffs = []
    figma_styles = figma_node.get("figma_styles", {})
    html_css = html_element.get("css", {})

    # Font size
    if "font_size" in figma_styles:
        expected = f"{figma_styles['font_size']}px"
        actual = html_css.get("font_size", "")
        if not _px_equal(expected, actual):
            diffs.append({
                "property": "font-size",
                "expected": expected,
                "actual": actual,
                "fix": f"font-size: {expected};"
            })

    # Font weight
    if "font_weight" in figma_styles:
        expected = str(int(figma_styles["font_weight"]))
        actual = html_css.get("font_weight", "")
        if expected != actual:
            diffs.append({
                "property": "font-weight",
                "expected": expected,
                "actual": actual,
                "fix": f"font-weight: {expected};"
            })

    # Font family
    if "font_family" in figma_styles:
        expected = figma_styles["font_family"]
        actual = html_css.get("font_family", "")
        if expected.lower() not in actual.lower():
            diffs.append({
                "property": "font-family",
                "expected": expected,
                "actual": actual,
                "fix": f"font-family: '{expected}', sans-serif;"
            })

    # Line height
    if "line_height_px" in figma_styles:
        expected = f"{round(figma_styles['line_height_px'])}px"
        actual = html_css.get("line_height", "")
        if not _px_equal(expected, actual) and actual != "normal":
            diffs.append({
                "property": "line-height",
                "expected": expected,
                "actual": actual,
                "fix": f"line-height: {expected};"
            })

    # Letter spacing
    if "letter_spacing" in figma_styles:
        val = figma_styles["letter_spacing"]
        expected = f"{val}px" if val != 0 else "normal"
        actual = html_css.get("letter_spacing", "normal")
        if expected != actual and not (val == 0 and actual == "normal"):
            diffs.append({
                "property": "letter-spacing",
                "expected": expected,
                "actual": actual,
                "fix": f"letter-spacing: {expected};"
            })

    # Color
    if "color" in figma_styles:
        expected = figma_styles["color"]
        actual = html_css.get("color", "")
        if not _colors_close(expected, actual):
            diffs.append({
                "property": "color",
                "expected": expected,
                "actual": actual,
                "fix": f"color: {expected};"
            })

    # Padding
    for side in ("top", "right", "bottom", "left"):
        figma_key = f"padding{side.capitalize()}"
        css_key = f"padding_{side}"
        if figma_key in figma_styles:
            expected = f"{figma_styles[figma_key]}px"
            actual = html_css.get(css_key, "0px")
            if not _px_equal(expected, actual):
                diffs.append({
                    "property": f"padding-{side}",
                    "expected": expected,
                    "actual": actual,
                    "fix": f"padding-{side}: {expected};"
                })

    # Gap
    if "gap" in figma_styles:
        expected = f"{figma_styles['gap']}px"
        actual = html_css.get("gap", "normal")
        if not _px_equal(expected, actual):
            diffs.append({
                "property": "gap",
                "expected": expected,
                "actual": actual,
                "fix": f"gap: {expected};"
            })

    # Border radius
    if "border_radius" in figma_styles:
        expected = f"{figma_styles['border_radius']}px"
        actual = html_css.get("border_radius", "0px")
        if not _px_equal(expected, actual):
            diffs.append({
                "property": "border-radius",
                "expected": expected,
                "actual": actual,
                "fix": f"border-radius: {expected};"
            })

    # Dimensions (width/height from bounding box)
    figma_w = figma_node.get("width", 0)
    html_w = html_element.get("width", 0)
    if figma_w > 0 and html_w > 0 and abs(figma_w - html_w) > 5:
        diffs.append({
            "property": "width",
            "expected": f"{figma_w}px",
            "actual": f"{html_w}px",
            "fix": f"width: {figma_w}px; /* or check container constraints */"
        })

    figma_h = figma_node.get("height", 0)
    html_h = html_element.get("height", 0)
    if figma_h > 0 and html_h > 0 and abs(figma_h - html_h) > 5:
        diffs.append({
            "property": "height",
            "expected": f"{figma_h}px",
            "actual": f"{html_h}px",
            "fix": f"/* height diff: Figma {figma_h}px vs HTML {html_h}px — check padding/content */"
        })

    return diffs


def _colors_close(c1, c2, threshold=10):
    """Check if two CSS color strings are close enough."""
    import re
    def parse_rgb(s):
        m = re.search(r'(\d+)\D+(\d+)\D+(\d+)', s)
        return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None

    rgb1, rgb2 = parse_rgb(c1), parse_rgb(c2)
    if not rgb1 or not rgb2:
        return c1 == c2

    return all(abs(a - b) <= threshold for a, b in zip(rgb1, rgb2))


# ---------------------------------------------------------------------------  main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", required=True, help="Path to visual_diff report JSON")
    ap.add_argument("--url", required=True, help="Running page URL (http://localhost:PORT/...)")
    ap.add_argument("--selector", required=True, help="CSS selector for the section")
    ap.add_argument("--figma-file", required=True, help="Figma file key")
    ap.add_argument("--figma-node", required=True, help="Figma node ID for the section")
    ap.add_argument("--figma-token", help="Figma API token (or use FIGMA_TOKEN env)")
    ap.add_argument("--json", action="store_true", help="Print enriched report as JSON")

    args = ap.parse_args()

    # Load diff report
    with open(args.report) as f:
        report = json.load(f)

    if report["status"] == "PASS":
        print("Diff report status is PASS — nothing to enrich.")
        sys.exit(0)

    # Get Figma token
    token = get_figma_token(args.figma_token)
    if not token:
        print("error: no Figma token found (--figma-token or FIGMA_TOKEN env)",
              file=sys.stderr)
        sys.exit(2)

    # Fetch Figma node properties
    print(f"Fetching Figma node {args.figma_node}...", file=sys.stderr)
    figma_doc = fetch_figma_node_properties(args.figma_file, args.figma_node, token)
    if not figma_doc:
        print("error: could not fetch Figma node", file=sys.stderr)
        sys.exit(2)

    figma_nodes = flatten_figma_nodes(figma_doc)
    figma_nodes = make_figma_coords_relative(figma_nodes, figma_doc)
    print(f"  → {len(figma_nodes)} Figma nodes extracted", file=sys.stderr)

    # Extract computed CSS from HTML
    if not HAS_PLAYWRIGHT:
        print("error: playwright not installed", file=sys.stderr)
        sys.exit(2)

    print(f"Extracting computed CSS from {args.url}...", file=sys.stderr)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(args.url)
        page.wait_for_load_state("networkidle")

        html_elements = extract_computed_css(page, args.selector, args.selector)
        browser.close()

    print(f"  → {len(html_elements)} HTML elements extracted", file=sys.stderr)

    # Enrich each region
    total_fixes = 0
    for region in report["regions"]:
        figma_match, html_match = match_figma_to_dom(figma_nodes, html_elements, region)

        if figma_match and html_match:
            fixes = compare_properties(figma_match, html_match)
            region["figma_element"] = {
                "name": figma_match.get("name", ""),
                "type": figma_match.get("type", ""),
                "id": figma_match.get("id", ""),
                "styles": figma_match.get("figma_styles", {}),
            }
            region["html_element"] = {
                "selector": html_match.get("selector", ""),
                "text": html_match.get("text", ""),
                "css": html_match.get("css", {}),
            }
            region["fixes"] = fixes
            total_fixes += len(fixes)
        else:
            region["fixes"] = []
            if not figma_match:
                region["note"] = "No matching Figma node found for this region"
            if not html_match:
                region["note"] = "No matching HTML element found for this region"

    # Deduplicate: group fixes by DOM selector, keep unique property fixes only
    seen_fixes = {}  # selector -> set of (property, expected)
    for region in report["regions"]:
        selector = region.get("html_element", {}).get("selector", region.get("dom_element", ""))
        if selector not in seen_fixes:
            seen_fixes[selector] = set()
        unique_fixes = []
        for fix in region.get("fixes", []):
            key = (fix["property"], str(fix["expected"]))
            if key not in seen_fixes[selector]:
                seen_fixes[selector].add(key)
                unique_fixes.append(fix)
        region["fixes"] = unique_fixes

    # Recount after dedup
    total_fixes = sum(len(r.get("fixes", [])) for r in report["regions"])

    report["total_fixes"] = total_fixes
    report["enriched"] = True

    # Save enriched report
    out_path = Path(args.report).with_suffix(".enriched.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    # Output
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n# Enriched Diff Report: {report['section']}")
        print(f"  Total actionable fixes: {total_fixes}")
        print()
        for region in report["regions"]:
            if not region.get("fixes"):
                continue
            rid = region["id"]
            dom = region.get("dom_element", region.get("html_element", {}).get("selector", "?"))
            figma_name = region.get("figma_element", {}).get("name", "?")
            print(f"  Region {rid}: {dom} (Figma: {figma_name})")
            for fix in region["fixes"]:
                print(f"    ❌ {fix['property']}: {fix['actual']} → should be {fix['expected']}")
                print(f"       Fix: {fix['fix']}")
            print()

    print(f"\nEnriched report saved: {out_path}", file=sys.stderr)
    sys.exit(1 if total_fixes > 0 else 0)


if __name__ == "__main__":
    main()

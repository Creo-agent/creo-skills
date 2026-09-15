#!/usr/bin/env python3
"""
section_spec.py — deterministic pre-build measurement for a Figma section.

Why this exists
---------------
PRE-BUILD-VERIFICATION.md is a prose checklist applied by judgment at build time. Prose is the
right medium for the items that need eyes ("does this mechanism match?", "is this logo upright?")
and the wrong medium for the items that are just a measurement. Those get skipped, or done from
memory, or answered with an inference that looks right — and the resulting defects are the ones
that survive visual QA, because two renderings can look identical and differ in every number.

Everything this script computes is a number with one correct answer, independent of which page is
being built: what color surrounds a section's content, what size a glyph actually is, how many
text nodes a block contains, whether two sections overlap, what color an export baked into its
margins. Run it BEFORE writing CSS. Its output is a spec you build against, not a report you skim.

Subcommands
-----------
  bg        Section background vs. content-block fills, from a Figma reference PNG.
            Implements PRE-BUILD-VERIFICATION item 18 (sample BETWEEN blocks, not inside them)
            by construction — it reports the perimeter color and the scanline run structure
            separately, so a card fill can never be mistaken for the section background.

  textsize  Cap-height -> design-px font size for one text line, with the screenshot's own
            scale factor divided out (the arithmetic slip that shipped 24px where 20px was
            correct). `--family` picks one font family instead of printing all four candidates.
            Also flags a MARQUEE tell: if a band's ink reaches both the left and right box
            edges the line is wider than its frame (clipped/overflowing) — the static signature
            of a scrolling marquee, not a centered headline (see item 21 / H31). Reported as
            `clipped`/`marquee_tell` in --json and a `!! MARQUEE TELL` note in prose.

  textnodes Count TEXT descendants of a node from a get_metadata dump (XML or JSON — see the
            note above cmd_textnodes). Tells you how many text elements a block needs before you
            write the markup.

  overlap   Adjacent-section gap/overlap arithmetic from the section manifest. Run at manifest
            time, not after an overlapping section covers its neighbour. Exits 1 if any pair
            overlaps.

  assetbg   For each exported asset, report the background color Figma BAKED INTO it, and
            compare against the fill of the element it will sit on. Figma composites a
            solo-exported node onto WHITE; if that node sits on a non-white parent fill in the
            design, the export carries an opaque white slab that covers the parent's fill.
            This is invisible whenever the two colors happen to agree, so eyeballing the asset
            does not catch it. Exits 1 if any asset mismatches `--on`.

  spec      Consolidate bg + textnodes + textsize into one JSON file for a section, from a small
            request file — this is what `qa_gate.py` diffs the built page against. Does not cover
            assetbg (that needs exported images, which don't exist yet at spec time).

            Request file schema (only "slug" is required; every other key is optional and
            controls which pieces of the output get computed):
              {
                "slug": "hero",
                "figma_ref": "/tmp/hero-figma-ref.png",
                "orig_width": 2960,
                "bg_rows": 6,
                "metadata": "/tmp/hero-metadata.json",
                "node_id": "7:8089",
                "text_boxes": [
                  {"name": "heading", "box": [120, 80, 600, 120], "family": "Poppins",
                   "selector": ".section-hero-heading"}
                ],
                "container": {"content_width": 2800, "selector": ".section-hero-inner"}
              }
            "selector" (on a text_box or on "container") is never used by this script — it is
            pass-through, carried into the output verbatim so `qa_gate.py` knows which built DOM
            element each measured value corresponds to. Omit it and that field is simply not
            diffed against the built page.

Usage
-----
  python3 section_spec.py bg        ref.png [--orig-width <design-px>] [--rows 6] [--json]
  python3 section_spec.py textsize  ref.png --box X,Y,W,H --orig-width <design-px>
                                     [--family Poppins] [--json]
  python3 section_spec.py textnodes metadata.{json,xml} [--node-id <id>] [--json]
  python3 section_spec.py overlap   manifest.json [--json]
  python3 section_spec.py assetbg   images/<slug>/*.png --on "#RRGGBB" [--json]
  python3 section_spec.py spec      spec-request.json --out /tmp/<slug>-spec.json

--orig-width is get_screenshot's `original_width`, NOT the PNG's width: the PNG is scaled, and
every measurement off it is wrong by that ratio until divided out.

--json (on bg/textsize/textnodes/overlap/assetbg) prints the same computed values as one JSON
object to stdout instead of the prose report — for scripts (`qa_gate.py`, CI) that need to parse
the result rather than read it. Human output is unchanged when --json is absent.

Requires: Pillow (bg/textsize/spec only). stdlib only for textnodes/overlap/assetbg-parsing.
"""

import argparse
import json
import sys
from collections import Counter


# --------------------------------------------------------------------------- helpers

try:
    from PIL import Image
except ImportError:
    Image = None


def _load(path):
    if Image is None:
        sys.exit("error: Pillow required for this subcommand (pip install Pillow)")
    return Image.open(path).convert("RGB")


def _hexof(rgb):
    return "#%02x%02x%02x" % rgb


def _quant(rgb, step=6):
    """Group near-identical colors so anti-aliasing noise doesn't fragment the histogram."""
    return tuple(min(255, (c // step) * step) for c in rgb)


def _runs(row, step=6, min_run=8):
    """Run-length encode a pixel row into (hex, start_x, width) spans of flat color."""
    out = []
    cur, start = None, 0
    for x, px in enumerate(row):
        q = _quant(px, step)
        if q != cur:
            if cur is not None and x - start >= min_run:
                out.append((_hexof(cur), start, x - start))
            cur, start = q, x
    if cur is not None and len(row) - start >= min_run:
        out.append((_hexof(cur), start, len(row) - start))
    return out


# --------------------------------------------------------------------------- bg

def compute_bg(png_path, orig_width, rows):
    """Pure computation for `bg` — returns raw values, reused verbatim by both the human
    print path and the --json/spec paths, so neither can drift from the other."""
    im = _load(png_path)
    w, h = im.size
    px = im.load()
    scale = (orig_width / w) if orig_width else 1.0

    ring = []
    for x in range(0, w, max(1, w // 200)):
        ring += [px[x, 2], px[x, h - 3]]
    for y in range(0, h, max(1, h // 200)):
        ring += [px[2, y], px[w - 3, y]]
    ring_hist = Counter(_quant(p) for p in ring).most_common(4)

    full = Counter(_quant(px[x, y])
                   for y in range(0, h, max(1, h // 300))
                   for x in range(0, w, max(1, w // 300)))
    full_total = sum(full.values())

    section_bg = _hexof(ring_hist[0][0])

    step_y = max(1, h // (rows + 1))
    xs = list(range(0, w, max(1, w // 400)))
    distinct_block_fills = Counter()
    scanlines = []
    for i in range(1, rows + 1):
        y = min(h - 1, i * step_y)
        runs = [r for r in _runs([px[x, y] for x in xs]) if r[2] >= 6]
        desc = []
        for chex, start, width in runs:
            x0 = int(start * (w / len(xs)) * scale)
            wpx = int(width * (w / len(xs)) * scale)
            tag = "bg" if chex == section_bg else "BLOCK"
            if tag == "BLOCK":
                distinct_block_fills[chex] += 1
            desc.append(f"{tag}:{chex}@{x0}+{wpx}")
        scanlines.append((int(y * scale), desc))

    return {
        "w": w, "h": h, "scale": scale, "ring_hist": ring_hist, "ring_len": len(ring),
        "full": full, "full_total": full_total, "section_bg": section_bg,
        "scanlines": scanlines, "distinct_block_fills": distinct_block_fills,
    }


def bg_to_json(png_path, orig_width, spec):
    """JSON-safe view of a compute_bg() result."""
    return {
        "png": png_path, "w": spec["w"], "h": spec["h"], "orig_width": orig_width,
        "scale": spec["scale"], "section_bg": spec["section_bg"],
        "ring_histogram": [[_hexof(c), round(100 * n / spec["ring_len"], 1)]
                            for c, n in spec["ring_hist"]],
        "area_histogram": [[_hexof(c), round(100 * n / spec["full_total"], 1)]
                            for c, n in spec["full"].most_common(5)],
        "block_fills": [[chex, n] for chex, n in spec["distinct_block_fills"].most_common()],
    }


def cmd_bg(args):
    spec = compute_bg(args.png, args.orig_width, args.rows)
    if args.json:
        print(json.dumps(bg_to_json(args.png, args.orig_width, spec)))
        return

    w, h, scale = spec["w"], spec["h"], spec["scale"]
    ring_hist, ring_len = spec["ring_hist"], spec["ring_len"]
    full, full_total = spec["full"], spec["full_total"]
    section_bg = spec["section_bg"]
    distinct_block_fills = spec["distinct_block_fills"]

    print(f"# bg spec — {args.png}  ({w}x{h} png"
          + (f", {args.orig_width}px design width, scale {scale:.4f}" if args.orig_width else "")
          + ")\n")

    print("## perimeter ring (2px inset) — THIS is the section background")
    for c, n in ring_hist:
        print(f"   {_hexof(c):9s}  {100 * n / ring_len:5.1f}% of ring")
    print(f"\n   -> section background = {section_bg}\n")

    print("## whole-image area histogram (cross-check only — a full-bleed card can top this)")
    for c, n in full.most_common(5):
        flag = "  <- same as ring" if _hexof(c) == section_bg else ""
        print(f"   {_hexof(c):9s}  {100 * n / full_total:5.1f}% of area{flag}")

    print("\n## scanline run structure (bg vs. content blocks — item 18)")
    print("   Any run whose color != section bg is a content block. A block whose fill EQUALS")
    print("   the section bg does not appear here at all — that means the block needs no")
    print("   background rule, NOT that the section takes the block's color.\n")
    for y_design, desc in spec["scanlines"]:
        print(f"   y={y_design:5d}  " + "  ".join(desc[:8]))

    if distinct_block_fills:
        print("\n## distinct content-block fills found (each needs its own CSS value)")
        for chex, n in distinct_block_fills.most_common():
            print(f"   {chex}   seen on {n} scanline(s)")
    else:
        print("\n## no content-block fills distinct from the section bg were found.")
        print("   Either the section is genuinely flat, or every block shares the section fill")
        print("   (in which case: do NOT give the blocks a background, and do NOT assume the")
        print("    section is white).")


# --------------------------------------------------------------------------- textsize

# Cap-height / em ratios. Poppins is the default for this skill's builds.
CAP_RATIOS = {"Poppins": 0.700, "Inter": 0.727, "Figtree": 0.714, "generic-sans": 0.715}


def compute_textsize(png_path, box, orig_width, threshold, min_ink):
    im = _load(png_path)
    w, h = im.size
    px = im.load()
    scale = (orig_width / w) if orig_width else 1.0

    x0, y0, bw, bh = box
    x1, y1 = min(w, x0 + bw), min(h, y0 + bh)
    if x0 >= x1 or y0 >= y1:
        sys.exit("error: --box lies outside the image")

    crop = [px[x, y] for y in range(y0, y1) for x in range(x0, x1)]
    bg = Counter(_quant(p) for p in crop).most_common(1)[0][0]

    def is_ink(p):
        return sum(abs(a - b) for a, b in zip(p, bg)) > threshold

    ink_rows = [y for y in range(y0, y1)
                if sum(is_ink(px[x, y]) for x in range(x0, x1)) >= min_ink]
    if not ink_rows:
        sys.exit("error: no ink found in box — widen it, or lower --threshold")

    bands, start, prev = [], ink_rows[0], ink_rows[0]
    for y in ink_rows[1:]:
        if y - prev > 1:
            bands.append((start, prev))
            start = y
        prev = y
    bands.append((start, prev))

    gaps = []
    if len(bands) > 1:
        gaps = [(bands[i + 1][0] - bands[i][1] - 1) * scale for i in range(len(bands) - 1)]

    # Edge-clip detection (a MARQUEE tell). Text whose ink reaches BOTH the left and right box
    # edges is wider than its frame — clipped or overflowing — which is the static signature of a
    # horizontally scrolling marquee, not a centered static headline (PRE-BUILD-VERIFICATION item
    # 21 / HARD-RULES H31). We can only observe this when --box is the visible/clipped frame; a box
    # drawn with generous slack around a short line will (correctly) not trip it.
    edge_margin = max(2, int((x1 - x0) * 0.01))
    band_clips = []
    for (a, b) in bands:
        xs_ink = [x for x in range(x0, x1)
                  if any(is_ink(px[x, y]) for y in range(a, b + 1))]
        if not xs_ink:
            band_clips.append({"left": False, "right": False})
            continue
        band_clips.append({
            "left": (min(xs_ink) - x0) <= edge_margin,
            "right": (x1 - 1 - max(xs_ink)) <= edge_margin,
        })
    clipped_both = any(c["left"] and c["right"] for c in band_clips)

    return {"w": w, "h": h, "scale": scale, "box": (x0, y0, bw, bh), "bg": bg,
            "bands": bands, "gaps": gaps, "band_clips": band_clips,
            "clipped_both": clipped_both, "edge_margin": edge_margin}


def _families_for(family):
    """Full CAP_RATIOS dict (default) or a single-entry dict when --family is given —
    same dict-iteration order either way, so default output is unaffected by this feature."""
    if not family:
        return CAP_RATIOS
    return {family: CAP_RATIOS[family]}


def textsize_to_json(png_path, spec, family):
    x0, y0, bw, bh = spec["box"]
    families = _families_for(family)
    band_clips = spec.get("band_clips") or [{} for _ in spec["bands"]]
    bands_json = []
    for i, (a, b) in enumerate(spec["bands"]):
        ink_h = (b - a + 1) * spec["scale"]
        sizes = {name: round(ink_h / ratio, 1) for name, ratio in families.items()}
        entry = {"y0": int(a * spec["scale"]), "y1": int(b * spec["scale"]),
                 "ink_height_px": round(ink_h, 1),
                 "clipped_left": bool(band_clips[i].get("left")),
                 "clipped_right": bool(band_clips[i].get("right"))}
        if family:
            entry["font_size_px"] = sizes[family]
        else:
            entry["font_size_by_family"] = sizes
        bands_json.append(entry)
    return {
        "png": png_path, "box": [x0, y0, bw, bh], "scale": spec["scale"],
        "crop_bg": _hexof(spec["bg"]), "bands": bands_json,
        "gaps_px": [round(g, 1) for g in spec["gaps"]],
        "clipped": bool(spec.get("clipped_both")),
        "marquee_tell": bool(spec.get("clipped_both")),
    }


def cmd_textsize(args):
    spec = compute_textsize(args.png, args.box, args.orig_width, args.threshold, args.min_ink)
    if args.json:
        print(json.dumps(textsize_to_json(args.png, spec, args.family)))
        return

    w, h, scale = spec["w"], spec["h"], spec["scale"]
    x0, y0, bw, bh = spec["box"]
    bg, bands, gaps = spec["bg"], spec["bands"], spec["gaps"]

    if not args.orig_width:
        print("warning: --orig-width not given; sizes below are PNG px, NOT design px.\n"
              "         Forgetting this factor is how 20px shipped as 24px.\n", file=sys.stderr)

    print(f"# textsize — {args.png} box=({x0},{y0},{bw},{bh})"
          + (f"  scale {scale:.4f}" if args.orig_width else "") + "\n")
    print(f"   crop background {_hexof(bg)},  {len(bands)} ink band(s) found\n")
    print("   NOTE: a band's ink height is cap height ONLY if the line has no descender")
    print("         (g j p q y) and no ascender-above-cap glyph. Prefer a line of caps or")
    print("         x-height+cap letters; verify against the band count you expected.\n")

    families = _families_for(args.family)
    for i, (a, b) in enumerate(bands, 1):
        ink_h = (b - a + 1) * scale
        print(f"   band {i}: y {int(a*scale)}..{int(b*scale)}  ink height {ink_h:.1f}px")
        for name, ratio in families.items():
            print(f"            if cap-height -> {name:13s} font-size ~= {ink_h / ratio:5.1f}px")
        print()

    if len(bands) > 1:
        print("   band-to-band gaps (leading, design px): "
              + ", ".join(f"{g:.1f}" for g in gaps))
        print("   line-height ~= ink_height + gap. Multiple bands with a LARGE gap relative to")
        print("   the others = separate paragraphs, not wrapped lines: cross-check with")
        print("   `textnodes` and give each its own <p> (see item 20).")

    if spec.get("clipped_both"):
        print("\n   !! MARQUEE TELL — ink reaches BOTH box edges (left and right) on at least one")
        print("      band: this line is wider than its frame (clipped/overflowing). A static,")
        print("      edge-clipped headline is the resting frame of a scrolling MARQUEE far more")
        print("      often than a deliberate crop. Do NOT build it as a static centered line —")
        print("      halt and confirm the interaction model (ASK-DONT-GUESS.md; PRE-BUILD-")
        print("      VERIFICATION.md item 21; HARD-RULES.md H31) before writing CSS.")


# --------------------------------------------------------------------------- textnodes

def _walk(node, depth=0):
    yield depth, node
    for c in (node.get("children") or []):
        yield from _walk(c, depth + 1)


def _find(node, node_id):
    for _, n in _walk(node):
        if n.get("id") == node_id:
            return n
    return None


# get_metadata does NOT return the node tree as JSON — it returns an XML-ish tree
# (<frame id=".." name=".." x=".."><text id=".." name="the copy" /></frame>), usually wrapped
# in an MCP JSON envelope of [{"type": "text", "text": "<frame ...>"}]. Feeding that straight
# into json.load() "works" and prints nonsense: every envelope entry has type "text", so the
# wrapper itself gets counted as a TEXT node. Both formats are accepted here on purpose,
# because the XML one is what the tool actually emits.

def _unwrap(raw):
    """Return the metadata payload as a string, unwrapping an MCP JSON envelope if present."""
    stripped = raw.lstrip()
    if not stripped.startswith(("{", "[")):
        return raw                                    # already raw XML
    try:
        data = json.loads(raw)
    except ValueError:
        return raw
    entries = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(entries, list):
        texts = [e.get("text", "") for e in entries
                 if isinstance(e, dict) and isinstance(e.get("text"), str)]
        if texts and texts[0].lstrip().startswith("<"):
            return "\n".join(texts)
    return raw                                        # a real JSON node tree; caller re-parses


def _xml_tree(payload):
    """Parse the metadata XML into ElementTree, tolerating multiple roots and bare '&'."""
    import re
    import xml.etree.ElementTree as ET
    body = "<__root__>" + payload + "</__root__>"
    try:
        return ET.fromstring(body)
    except ET.ParseError:
        # Figma layer names legitimately contain bare & and stray < — escape and retry.
        body = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", body)
        return ET.fromstring(body)


def _xml_to_node(el):
    """Convert an XML element into the same dict shape the JSON path uses."""
    return {"id": el.attrib.get("id"),
            "name": el.attrib.get("name", "?"),
            "type": el.tag.upper(),                   # <text> -> "TEXT"
            "characters": el.attrib.get("characters") or el.attrib.get("name"),
            "children": [_xml_to_node(c) for c in el]}


def _texts_in(node):
    return [n for _, n in _walk(node) if str(n.get("type", "")).upper() == "TEXT"]


def compute_textnodes(metadata_path, node_id=None):
    raw = open(metadata_path, encoding="utf-8").read()
    payload = _unwrap(raw)

    if payload.lstrip().startswith("<"):
        roots = [_xml_to_node(el) for el in _xml_tree(payload)]
        root = roots[0] if len(roots) == 1 else {"name": "(multiple roots)", "children": roots}
        fmt = "XML (get_metadata native)"
    else:
        data = json.loads(payload)
        root = data if isinstance(data, dict) else {"children": data}
        fmt = "JSON node tree"

    if node_id:
        found = _find(root, node_id)
        if not found:
            sys.exit(f"error: node {node_id} not present in {metadata_path}")
        root = found

    groups = [c for c in (root.get("children") or [])
              if str(c.get("type", "")).upper() != "TEXT" and _texts_in(c)]

    return {"root": root, "groups": groups, "fmt": fmt}


def textnodes_to_json(metadata_path, node_id, spec):
    root, groups, fmt = spec["root"], spec["groups"], spec["fmt"]
    total = _texts_in(root)

    def _tnode(t):
        return {"chars": (t.get("characters") or "")}

    out = {
        "metadata": metadata_path, "node_id": node_id, "format": fmt,
        "root_name": root.get("name", "?"), "total_text_nodes": len(total),
        "texts": [_tnode(t) for t in total],
    }
    if len(groups) > 1:
        out["groups"] = [{"name": g.get("name", "?"), "count": len(_texts_in(g)),
                           "texts": [_tnode(t) for t in _texts_in(g)]} for g in groups]
    return out


def cmd_textnodes(args):
    spec = compute_textnodes(args.metadata, args.node_id)
    if args.json:
        print(json.dumps(textnodes_to_json(args.metadata, args.node_id, spec)))
        return

    root, groups, fmt = spec["root"], spec["groups"], spec["fmt"]

    print(f"# textnodes — {args.metadata}"
          + (f" node={args.node_id}" if args.node_id else "") + f"  [{fmt}]\n")
    print("   One TEXT node in Figma = one text element in HTML. A body block with 2 TEXT")
    print("   children needs two <p>, not one <p> with <br><br> (item 20).\n")

    def _report(node, label=None, indent="   "):
        texts = _texts_in(node)
        name = label or node.get("name", "?")
        width = max(10, 52 - (len(indent) - 3))
        print(f"{indent}{name[:width]:{width}s}  {len(texts)} TEXT node(s)")
        for t in texts:
            chars = (t.get("characters") or "").replace("\n", " / ")
            print(f"{indent}     - {chars[:74]}")
        if len(texts) > 1:
            print(f"{indent}     => build as {len(texts)} separate text elements")
        print()
        return texts

    total = _report(root)
    if not total:
        print("   (no TEXT nodes in this subtree — check the node id, or the block is icon-only)")
        return

    if len(groups) > 1:
        print("   breakdown by sub-block:\n")
        for child in groups:
            _report(child, indent="      ")


# --------------------------------------------------------------------------- overlap

def compute_overlap(manifest_path):
    with open(manifest_path) as f:
        data = json.load(f)
    secs = data.get("sections", data) if isinstance(data, dict) else data
    secs = sorted(secs, key=lambda s: s["y"])

    pairs = []
    for a, b in zip(secs, secs[1:]):
        a_end = a["y"] + a["h"]
        delta = b["y"] - a_end
        pairs.append({"a": a["slug"], "b": b["slug"], "delta": delta, "overlap": delta < 0})
    return pairs


def cmd_overlap(args):
    pairs = compute_overlap(args.manifest)
    any_overlap = any(p["overlap"] for p in pairs)

    if args.json:
        print(json.dumps({"manifest": args.manifest, "pairs": pairs,
                           "any_overlap": any_overlap}))
    else:
        print(f"# overlap — {args.manifest}\n")
        print("   Run this at MANIFEST time. An overlapping section must have its background")
        print("   decided before any CSS is written: a full-width opaque background on the")
        print("   overlapping section will cover the neighbour's content.\n")

        for p in pairs:
            if p["overlap"]:
                delta = p["delta"]
                print(f"   !! OVERLAP  {p['a']} -> {p['b']}: {-delta}px")
                print(f"      {p['b']} must use:  margin-top: {delta}px; position: relative;"
                      f" z-index: 2; background: transparent;")
                print(f"      and pointer-events: none on the wrapper, auto on its own content,")
                print(f"      so the bottom {-delta}px of {p['a']} stays visible AND clickable.\n")
            elif p["delta"] == 0:
                print(f"   -- flush     {p['a']} -> {p['b']}")
            else:
                print(f"   ok gap {p['delta']:5d}px  {p['a']} -> {p['b']}")

        if not any_overlap:
            print("\n   No overlapping pairs. No transparent-background requirement in this page.")

    if any_overlap:
        sys.exit(1)


# --------------------------------------------------------------------------- assetbg

def compute_assetbg(pngs, on, tolerance):
    expect = on.lower().lstrip("#") if on else None
    if expect and len(expect) == 3:
        expect = "".join(c * 2 for c in expect)

    results = []
    for path in pngs:
        try:
            im = _load(path)
        except SystemExit:
            raise
        except Exception as e:
            results.append({"path": path, "error": str(e)})
            continue
        w, h = im.size
        px = im.load()

        try:
            alpha = Image.open(path).convert("RGBA").split()[-1].getextrema()
        except Exception:
            alpha = None

        ring = []
        for x in range(0, w, max(1, w // 150)):
            ring += [px[x, 1], px[x, h - 2]]
        for y in range(0, h, max(1, h // 150)):
            ring += [px[1, y], px[w - 2, y]]
        hist = Counter(ring)
        baked, n = hist.most_common(1)[0]
        baked_hex = _hexof(baked)
        pct = 100 * n / len(ring)
        transparent = alpha is not None and alpha[0] == 0

        entry = {"path": path, "w": w, "h": h, "baked": baked_hex, "ring_pct": round(pct, 1),
                  "transparent": transparent, "match": None, "delta": None}
        if not transparent and expect:
            want = tuple(int(expect[i:i + 2], 16) for i in (0, 2, 4))
            dist = max(abs(a - b) for a, b in zip(baked, want))
            entry["delta"] = dist
            entry["match"] = dist <= tolerance
        results.append(entry)

    bad = sum(1 for r in results if r.get("match") is False)
    return {"expect": expect, "results": results, "bad": bad}


def cmd_assetbg(args):
    spec = compute_assetbg(args.pngs, args.on, args.tolerance)
    expect, results, bad = spec["expect"], spec["results"], spec["bad"]

    if args.json:
        print(json.dumps({"on": args.on, "tolerance": args.tolerance,
                           "results": results, "bad": bad, "total": len(args.pngs)}))
    else:
        print("# assetbg — background color BAKED INTO each exported asset\n")
        print("   Figma composites a solo-exported node onto WHITE. If the node sits on a")
        print("   non-white parent fill in the design, the export carries an opaque slab of the")
        print("   WRONG color and covers that fill wherever the asset is placed.\n")
        print("   Fix is never post-processing the PNG: flood-filling the baked color to transparent")
        print("   also eats any UI of that same color *inside* the art — a white card/bubble/sheet")
        print("   touching the white margin is edge-connected to it with no boundary to stop at.")
        print("   Re-export the smallest ANCESTOR node containing both the art and the parent fill,")
        print("   and place that as the full-bleed background of the element.\n")

        for r in results:
            if "error" in r:
                print(f"   {r['path']}: unreadable ({r['error']})")
                continue
            print(f"   {r['path'].split('/')[-1]:34s} {r['w']}x{r['h']}  edge={r['baked']} "
                  f"({r['ring_pct']:.0f}% of ring)"
                  + ("  alpha: has transparency" if r["transparent"] else "  alpha: fully opaque"))
            if r["transparent"]:
                print("        OK — transparent edges, will not cover anything.")
            elif expect:
                if r["match"]:
                    print(f"        OK — baked edge matches #{expect} (max channel delta {r['delta']}).")
                else:
                    print(f"        MISMATCH — sits on #{expect} but bakes {r['baked']} "
                          f"(max channel delta {r['delta']}).")
                    print(f"        A {r['baked']} rectangle will cover the #{expect} fill.")
                    print( "        -> re-export the ancestor node that includes the fill.")
            else:
                print("        pass --on '#rrggbb' (the container's fill) to check for a mismatch.")
            print()

        if expect:
            print(f"   {bad} mismatch(es) out of {len(args.pngs)} asset(s).")
            if bad == 0:
                print("   NOTE: agreement here is often luck — Figma bakes white, and some cards")
                print("         are white. Re-run whenever a container's fill changes.")

    if expect and bad > 0:
        sys.exit(1)


# --------------------------------------------------------------------------- spec (consolidated)

def cmd_spec(args):
    with open(args.request) as f:
        req = json.load(f)

    out = {"slug": req["slug"]}

    if req.get("figma_ref"):
        bg_spec = compute_bg(req["figma_ref"], req.get("orig_width"), req.get("bg_rows", 6))
        out["bg"] = bg_to_json(req["figma_ref"], req.get("orig_width"), bg_spec)

    if req.get("metadata"):
        tn_spec = compute_textnodes(req["metadata"], req.get("node_id"))
        out["textnodes"] = textnodes_to_json(req["metadata"], req.get("node_id"), tn_spec)

    text_boxes = req.get("text_boxes") or []
    if text_boxes:
        ref = req.get("figma_ref")
        if not ref:
            sys.exit("error: text_boxes given but no figma_ref to measure them against")
        out["textsize"] = {}
        for tb in text_boxes:
            ts_spec = compute_textsize(ref, tb["box"], req.get("orig_width"),
                                        tb.get("threshold", 90), tb.get("min_ink", 2))
            entry = textsize_to_json(ref, ts_spec, tb.get("family"))
            if tb.get("selector"):
                entry["selector"] = tb["selector"]
            out["textsize"][tb["name"]] = entry

    if req.get("container"):
        out["container"] = req["container"]

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    parts = [k for k in ("bg", "textnodes", "textsize", "container") if k in out]
    print(f"wrote spec for '{req['slug']}' -> {args.out} ({', '.join(parts) or 'empty'})",
          file=sys.stderr)


# --------------------------------------------------------------------------- main

def _box(s):
    parts = [int(v) for v in s.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("--box wants X,Y,W,H")
    return parts


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("bg", help="section background vs. content-block fills")
    p.add_argument("png")
    p.add_argument("--orig-width", type=int, help="design-px width of the frame (for scaling)")
    p.add_argument("--rows", type=int, default=6, help="how many scanlines (default 6)")
    p.add_argument("--json", action="store_true", help="print one JSON object instead of prose")
    p.set_defaults(fn=cmd_bg)

    p = sub.add_parser("textsize", help="cap height -> design-px font size")
    p.add_argument("png")
    p.add_argument("--box", type=_box, required=True, metavar="X,Y,W,H")
    p.add_argument("--orig-width", type=int)
    p.add_argument("--threshold", type=int, default=90, help="ink/bg distance (default 90)")
    p.add_argument("--min-ink", type=int, default=2, help="min ink px per row (default 2)")
    p.add_argument("--family", choices=list(CAP_RATIOS),
                   help="print/return one font size instead of all four candidates")
    p.add_argument("--json", action="store_true", help="print one JSON object instead of prose")
    p.set_defaults(fn=cmd_textsize)

    p = sub.add_parser("textnodes", help="TEXT node count per child from get_metadata JSON")
    p.add_argument("metadata")
    p.add_argument("--node-id")
    p.add_argument("--json", action="store_true", help="print one JSON object instead of prose")
    p.set_defaults(fn=cmd_textnodes)

    p = sub.add_parser("overlap", help="adjacent-section gap/overlap from the manifest")
    p.add_argument("manifest", help='JSON list of {"slug","y","h"}')
    p.add_argument("--json", action="store_true", help="print one JSON object instead of prose")
    p.set_defaults(fn=cmd_overlap)

    p = sub.add_parser("assetbg", help="background color baked into each exported asset")
    p.add_argument("pngs", nargs="+")
    p.add_argument("--on", help="hex fill of the element the assets will sit on, e.g. '#RRGGBB'")
    p.add_argument("--tolerance", type=int, default=6,
                   help="max per-channel delta still counted as a match (default 6)")
    p.add_argument("--json", action="store_true", help="print one JSON object instead of prose")
    p.set_defaults(fn=cmd_assetbg)

    p = sub.add_parser("spec", help="consolidate bg+textnodes+textsize into one JSON spec file")
    p.add_argument("request", help="JSON request file — see module docstring for the schema")
    p.add_argument("--out", required=True, help="path to write the consolidated spec JSON")
    p.set_defaults(fn=cmd_spec)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

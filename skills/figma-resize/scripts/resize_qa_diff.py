#!/usr/bin/env python3
"""resize_qa_diff.py — gate layer 9b, the measurement diff.

Diffs a resized output frame against the recorded master baseline and the placement spec, and
prints every script-owned rule in reference/resize-rules.csv with an expected/measured pair.

Usage:
    python3 scripts/resize_qa_diff.py \\
        --baseline  <deliverables>/measure-master.json \\
        --output    <deliverables>/measure-STORY-v01.json \\
        --placement STORY \\
        --spec      reference/placements.json \\
        --rules     reference/resize-rules.csv

Exit codes:  0 = zero hard failures   1 = one or more hard failures   2 = could not run

Three outcomes per check — PASS, FAIL, UNAVAILABLE — and never a silent pass. A check whose input
data is missing reports UNAVAILABLE with the reason, because "couldn't check" recorded as "passed"
is how a whole category of defect goes unexamined while the report looks clean.

Stdlib only, by design: this has to run wherever the skill runs, with no install step.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict

# ---------------------------------------------------------------- tolerances

TOL_ASPECT      = 0.01   # 1% — R1/R2/R9
TOL_ROTATION    = 0.5    # degrees — R9
TOL_OPACITY     = 0.01   # R20
TOL_CROP        = 0.01   # 1% between imageTransform X and Y — R8
TOL_MASK_PX     = 5.0    # R7's documented threshold
TOL_DIM_PX      = 0.5    # R23 — effectively exact
TOL_GAP_PX      = 2.0    # R26 repeated-item gap uniformity
TOL_GAP_RATIO   = 0.15   # R26 proportional spacing, 15% of expected ratio
MIN_MATCH_RATE  = 0.80   # below this, structure diverged — warn loudly

MIN_MICROCOPY_PX = 28    # R32 — Ad-Specific QA Checklist S2, @1x export
MIN_CTA_TEXT_PX  = 36    # R33 — S3
MIN_H2_PX        = 45    # R34 — S5
LARGE_TEXT_PX    = 24    # WCAG large-text threshold (regular weight)
LARGE_TEXT_BOLD_PX = 19  # WCAG large-text threshold (bold) — approximated as weight name check
WCAG_LARGE_RATIO = 3.0
WCAG_NORMAL_RATIO = 4.5

PASS, FAIL, UNAVAIL = "PASS", "FAIL", "UNAVAIL"


class Result:
    def __init__(self, status, detail=None, rows=None):
        self.status = status
        self.detail = detail or ""
        self.rows = rows or []        # (path, name, expected, measured)


# ---------------------------------------------------------------- helpers

def load_json(path, label):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(f"ERROR: {label} not found: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"ERROR: {label} is not valid JSON ({path}): {exc}")


def index_by_path(doc):
    return {n["path"]: n for n in doc.get("nodes", [])}


def parent_path(path):
    return path.rsplit("/", 1)[0] if "/" in path else None


def aspect(node):
    loc = node.get("local") or {}
    w, h = loc.get("width"), loc.get("height")
    if not w or not h:
        return None
    return w / h


def visible(node):
    return node.get("visible", True)


def fills_signature(node):
    f = node.get("fills")
    if f == "MIXED":
        return "MIXED"
    if not isinstance(f, list):
        return []
    out = []
    for p in f:
        if p.get("type") == "SOLID":
            out.append(("SOLID", p.get("hex"), p.get("opacity")))
        elif str(p.get("type", "")).startswith("GRADIENT"):
            out.append(("GRAD", p.get("type")))
        elif p.get("type") == "IMAGE":
            out.append(("IMAGE", p.get("imageHash")))
    return out


def gradient_signature(node):
    f = node.get("fills")
    if not isinstance(f, list):
        return []
    out = []
    for p in f:
        if str(p.get("type", "")).startswith("GRADIENT"):
            out.append((
                p.get("type"),
                json.dumps(p.get("gradientTransform"), sort_keys=True),
                json.dumps(p.get("stops"), sort_keys=True),
            ))
    return out


def effects_signature(node):
    return json.dumps(node.get("effects", []), sort_keys=True)


def type_signature(node):
    t = node.get("text") or {}
    # fontSize deliberately excluded — R12 permits reducing it to fit (R22 states this)
    return (
        t.get("fontFamily"), t.get("fontStyle"),
        json.dumps(t.get("letterSpacing"), sort_keys=True),
        json.dumps(t.get("lineHeight"), sort_keys=True),
    )


def frame_relative(node, frame_abs):
    """Node bounds relative to the frame origin, or None when unmeasurable."""
    a, f = node.get("abs"), frame_abs
    if not a or not f:
        return None
    return {
        "left": a["x"] - f["x"], "top": a["y"] - f["y"],
        "right": a["x"] - f["x"] + a["width"],
        "bottom": a["y"] - f["y"] + a["height"],
        "width": a["width"], "height": a["height"],
    }


# ---------------------------------------------------------------- checks

def check_aspect_ratio(pairs):
    # The root frame's aspect ratio is supposed to change — that is the resize. Comparing it
    # reports the intended canvas change as a defect, so root is excluded here.
    #
    # TEXT nodes are excluded too (found via testing, 2026-09-01): a text box's own width/height
    # ratio is governed by its content and fontSize, not by uniform-scale geometry — it changes
    # shape naturally when a line wraps differently or R12 reduces fontSize to fit, with no
    # squashing defect having occurred. R1/R2/R9 police shapes, images and groups; a text node's
    # bounding box was never the thing they were meant to protect.
    rows = []
    for path, m, o in pairs:
        if path == "0" or m.get("type") == "TEXT":
            continue
        am, ao = aspect(m), aspect(o)
        if not am or not ao:
            continue
        delta = ao / am
        if abs(delta - 1.0) > TOL_ASPECT:
            rows.append((path, o["name"], "1.000",
                         f"{delta:.3f} ({(delta - 1) * 100:+.1f}%)"))
    text_excluded = sum(1 for _, m, _ in pairs if m.get("type") == "TEXT")
    return Result(FAIL if rows else PASS,
                  f"{len(pairs) - 1 - text_excluded} nodes compared (root + {text_excluded} text nodes excluded)",
                  rows)


def check_rotation(pairs):
    rows = []
    for path, m, o in pairs:
        rm, ro = m.get("rotation") or 0, o.get("rotation") or 0
        if abs(ro - rm) > TOL_ROTATION:
            rows.append((path, o["name"], f"{rm}°", f"{ro}°"))
    return Result(FAIL if rows else PASS, "", rows)


def check_crop_uniform(out_nodes):
    rows, checked = [], 0
    for n in out_nodes.values():
        img = n.get("image")
        if not img or img.get("scaleMode") != "CROP":
            continue
        sx, sy = img.get("transformScaleX"), img.get("transformScaleY")
        if sx is None or sy is None:
            rows.append((n["path"], n["name"], "X≈Y", "imageTransform missing"))
            continue
        checked += 1
        if abs(sx - sy) > TOL_CROP:
            rows.append((n["path"], n["name"], "X≈Y", f"X {sx} / Y {sy}"))
    if not checked and not rows:
        return Result(PASS, "no CROP fills in this frame")
    return Result(FAIL if rows else PASS, f"{checked} CROP fills checked", rows)


def check_mask_alignment(out_doc):
    groups = (out_doc.get("derived") or {}).get("maskGroups")
    if groups is None:
        return Result(UNAVAIL, "derived.maskGroups absent — probe did not record masks; R7 unverifiable")
    rows = []
    for g in groups:
        d = g.get("absDelta")
        if d is None:
            rows.append((g.get("imagePath", "?"), "mask group", f"|Δ| ≤ {TOL_MASK_PX}px",
                         "absoluteBoundingBox missing"))
            continue
        worst = max(abs(d.get("x", 0)), abs(d.get("y", 0)))
        if worst > TOL_MASK_PX:
            rows.append((g.get("imagePath", "?"), "mask group", f"|Δ| ≤ {TOL_MASK_PX}px",
                         f"Δx {d.get('x')} / Δy {d.get('y')}"))
    return Result(FAIL if rows else PASS, f"{len(groups)} mask groups", rows)


def check_text_verbatim(pairs):
    rows, checked = [], 0
    for path, m, o in pairs:
        if m.get("type") != "TEXT":
            continue
        tm, to = (m.get("text") or {}).get("characters"), (o.get("text") or {}).get("characters")
        if tm is None or to is None:
            continue
        checked += 1
        if tm != to:
            rows.append((path, o["name"], repr(tm[:60]), repr(to[:60])))
    return Result(FAIL if rows else PASS, f"{checked} text nodes compared", rows)


def check_typography(pairs):
    rows, checked = [], 0
    for path, m, o in pairs:
        if m.get("type") != "TEXT":
            continue
        sm, so = type_signature(m), type_signature(o)
        checked += 1
        if sm != so:
            rows.append((path, o["name"],
                         f"{sm[0]} {sm[1]}", f"{so[0]} {so[1]}"))
    return Result(FAIL if rows else PASS, f"{checked} text nodes (fontSize excluded per R22)", rows)


def check_text_fits(out_nodes, frame_abs, spec):
    if not frame_abs:
        return Result(UNAVAIL, "output frameAbs missing")
    w = spec.get("width") or frame_abs["width"]
    h = spec.get("height") or frame_abs["height"]
    rows = []
    for n in out_nodes.values():
        if n.get("type") != "TEXT" or not visible(n):
            continue
        r = frame_relative(n, frame_abs)
        if not r:
            continue
        if r["left"] < -TOL_DIM_PX or r["top"] < -TOL_DIM_PX or \
           r["right"] > w + TOL_DIM_PX or r["bottom"] > h + TOL_DIM_PX:
            rows.append((n["path"], n["name"], f"within 0–{w:.0f} × 0–{h:.0f}",
                         f"{r['left']:.0f},{r['top']:.0f} → {r['right']:.0f},{r['bottom']:.0f}"))
    return Result(FAIL if rows else PASS, "", rows)


def check_offcanvas(out_nodes, frame_abs, spec):
    if not frame_abs:
        return Result(UNAVAIL, "output frameAbs missing")
    w = spec.get("width") or frame_abs["width"]
    h = spec.get("height") or frame_abs["height"]
    rows, checked = [], 0
    for n in out_nodes.values():
        if n["path"] == "0" or not visible(n):
            continue
        r = frame_relative(n, frame_abs)
        if not r:
            continue
        checked += 1
        if r["left"] < -TOL_DIM_PX or r["top"] < -TOL_DIM_PX or \
           r["right"] > w + TOL_DIM_PX or r["bottom"] > h + TOL_DIM_PX:
            rows.append((n["path"], n["name"], "inside canvas",
                         f"{r['left']:.0f},{r['top']:.0f} → {r['right']:.0f},{r['bottom']:.0f}"))
    return Result(FAIL if rows else PASS, f"{checked} visible nodes swept", rows)


def check_safe_zone(out_nodes, frame_abs, spec):
    sz = spec.get("safeZone")
    if sz is None:
        return Result(UNAVAIL, "placements.json has no safeZone for this placement "
                               "(pending research) — R24 unverifiable, do not assume pass")
    if not frame_abs:
        return Result(UNAVAIL, "output frameAbs missing")
    w = spec.get("width") or frame_abs["width"]
    h = spec.get("height") or frame_abs["height"]
    top, bottom = sz.get("top", 0), sz.get("bottom", 0)
    left, right = sz.get("left", 0), sz.get("right", 0)
    rows = []
    for n in out_nodes.values():
        if n["path"] == "0" or not visible(n):
            continue
        if n.get("type") not in ("TEXT", "RECTANGLE", "FRAME", "GROUP",
                                 "INSTANCE", "COMPONENT", "VECTOR", "ELLIPSE"):
            continue
        r = frame_relative(n, frame_abs)
        if not r:
            continue
        if r["top"] < top or r["bottom"] > h - bottom or \
           r["left"] < left or r["right"] > w - right:
            rows.append((n["path"], n["name"],
                         f"y {top}–{h - bottom}, x {left}–{w - right}",
                         f"y {r['top']:.0f}–{r['bottom']:.0f}, x {r['left']:.0f}–{r['right']:.0f}"))
    return Result(FAIL if rows else PASS,
                  f"zone top {top} bottom {bottom} left {left} right {right}", rows)


def check_dimensions(out_doc, spec):
    fa = (out_doc.get("meta") or {}).get("frameAbs")
    if not fa:
        return Result(UNAVAIL, "output frameAbs missing")
    ew, eh = spec.get("width"), spec.get("height")
    if not ew or not eh:
        return Result(UNAVAIL, "placements.json has no width/height for this placement")
    ok = abs(fa["width"] - ew) <= TOL_DIM_PX and abs(fa["height"] - eh) <= TOL_DIM_PX
    return Result(PASS if ok else FAIL,
                  f"{ew}×{eh}" if ok else "",
                  [] if ok else [("0", out_doc["meta"].get("frameName", "frame"),
                                  f"{ew}×{eh}", f"{fa['width']}×{fa['height']}")])


def check_frame_named_parented(out_doc, spec):
    meta = out_doc.get("meta") or {}
    expected_name = spec.get("frameName")
    rows = []
    if not expected_name:
        return Result(UNAVAIL, "placements.json has no frameName for this placement")
    if meta.get("frameName") != expected_name:
        rows.append(("0", "frame name", expected_name, meta.get("frameName")))
    parent = meta.get("parentName")
    if parent is None:
        rows.append(("0", "parent", "Generated Ad Sizes N", "not recorded by probe"))
    elif not str(parent).startswith("Generated Ad Sizes"):
        rows.append(("0", "parent", "Generated Ad Sizes N", parent))
    return Result(FAIL if rows else PASS, "", rows)


def _count_by_candidates(doc, key):
    return (doc.get("derived") or {}).get(key) or []


def check_role_count(base_doc, out_doc, out_nodes, key, label):
    """Counts a candidate role, distinguishing deliberate hiding from deletion.

    A hidden node is an exclusion the user asked for (RESIZE-WORKFLOW.md Step 4 hides rather
    than deletes). A missing node is a defect. Those are different findings, so they are
    reported differently rather than collapsed into one count mismatch.
    """
    base_paths = _count_by_candidates(base_doc, key)
    out_paths = _count_by_candidates(out_doc, key)
    if not base_paths and not out_paths:
        return Result(PASS, f"no {label} candidates in either frame")
    present = [p for p in base_paths if p in out_nodes]
    hidden = [p for p in present if not visible(out_nodes[p])]
    missing = [p for p in base_paths if p not in out_nodes]
    rows = [(p, base_doc and "—", "present", "MISSING from output") for p in missing]
    detail = (f"master {len(base_paths)} · output present {len(present)}"
              f" · hidden {len(hidden)} · missing {len(missing)}")
    if hidden:
        detail += f"  (hidden = deliberate exclusion: {', '.join(hidden)})"
    return Result(FAIL if missing else PASS, detail, rows)


def check_logo_proportional(base_nodes, out_nodes, base_doc):
    paths = _count_by_candidates(base_doc, "logoCandidates")
    if not paths:
        return Result(UNAVAIL, "no logo candidates identified in the baseline")
    rows = []
    for p in paths:
        m, o = base_nodes.get(p), out_nodes.get(p)
        if not m or not o:
            continue
        am, ao = aspect(m), aspect(o)
        if not am or not ao:
            continue
        d = ao / am
        if abs(d - 1.0) > TOL_ASPECT:
            rows.append((p, o["name"], "1.000", f"{d:.3f} ({(d - 1) * 100:+.1f}%)"))
    return Result(FAIL if rows else PASS, f"{len(paths)} logo node(s)", rows)


def _sig_check(pairs, fn, label, skip_invisible=True):
    rows = []
    for path, m, o in pairs:
        if skip_invisible and not visible(o):
            continue
        sm, so = fn(m), fn(o)
        if sm != so:
            rows.append((path, o["name"], str(sm)[:70], str(so)[:70]))
    return Result(FAIL if rows else PASS, label, rows)


def check_opacity(pairs):
    rows = []
    for path, m, o in pairs:
        om = m.get("opacity", 1) or 1
        oo = o.get("opacity", 1) or 1
        if abs(oo - om) > TOL_OPACITY:
            rows.append((path, o["name"], f"{om}", f"{oo}"))
    return Result(FAIL if rows else PASS, "", rows)


def check_position_redistributed(out_nodes, frame_abs, spec):
    """Soft: does the composition actually use the new canvas, or cluster in a corner?"""
    if not frame_abs:
        return Result(UNAVAIL, "output frameAbs missing")
    w = spec.get("width") or frame_abs["width"]
    h = spec.get("height") or frame_abs["height"]
    boxes = [frame_relative(n, frame_abs) for n in out_nodes.values()
             if n["path"] != "0" and visible(n)]
    boxes = [b for b in boxes if b]
    if not boxes:
        return Result(UNAVAIL, "no measurable visible children")
    used_w = max(b["right"] for b in boxes) - min(b["left"] for b in boxes)
    used_h = max(b["bottom"] for b in boxes) - min(b["top"] for b in boxes)
    cov_w, cov_h = used_w / w, used_h / h
    ok = cov_w >= 0.60 and cov_h >= 0.60
    return Result(PASS if ok else FAIL,
                  f"content spans {cov_w:.0%} × {cov_h:.0%} of canvas",
                  [] if ok else [("0", "composition", "≥60% × ≥60%",
                                  f"{cov_w:.0%} × {cov_h:.0%}")])


def check_repeated_gaps(out_nodes, frame_abs):
    """Hard: within any group of 3+ same-type siblings, consecutive gaps must be uniform."""
    if not frame_abs:
        return Result(UNAVAIL, "output frameAbs missing")
    families = defaultdict(list)
    for n in out_nodes.values():
        pp = parent_path(n["path"])
        if pp is None or not visible(n):
            continue
        families[(pp, n.get("type"))].append(n)

    # Same parent + same type is not enough to mean "a repeated group": a logo and three list
    # rows are all FRAMEs, and treating them as one family produces a nonsense gap between the
    # logo and the first row. A real repeated group is CONTIGUOUS in index order and SIMILAR in
    # size, so runs are cut wherever either condition breaks.
    def runs(sibs):
        sibs = sorted(sibs, key=lambda n: int(n["path"].rsplit("/", 1)[1]))
        out, cur = [], []
        for n in sibs:
            idx = int(n["path"].rsplit("/", 1)[1])
            if cur:
                prev = cur[-1]
                prev_idx = int(prev["path"].rsplit("/", 1)[1])
                pw, ph = prev["local"]["width"] or 1, prev["local"]["height"] or 1
                nw, nh = n["local"]["width"] or 1, n["local"]["height"] or 1
                similar = (abs(nw - pw) / max(pw, 1) <= 0.10 and
                           abs(nh - ph) / max(ph, 1) <= 0.10)
                if idx != prev_idx + 1 or not similar:
                    out.append(cur); cur = []
            cur.append(n)
        out.append(cur)
        return [r for r in out if len(r) >= 3]

    rows, groups_checked = [], 0
    for (pp, _t), sibs in families.items():
      for run in runs(sibs):
        boxes = [(n, frame_relative(n, frame_abs)) for n in run]
        boxes = [(n, b) for n, b in boxes if b]
        if len(boxes) < 3:
            continue
        for axis, lo, hi in (("y", "top", "bottom"), ("x", "left", "right")):
            ordered = sorted(boxes, key=lambda nb: nb[1][lo])
            gaps = [ordered[i + 1][1][lo] - ordered[i][1][hi] for i in range(len(ordered) - 1)]
            spread = ordered[-1][1][lo] - ordered[0][1][lo]
            if spread < 1:
                continue
            groups_checked += 1
            if not gaps or max(gaps) - min(gaps) <= TOL_GAP_PX:
                break
            rows.append((pp, f"{len(ordered)}× {_t or 'node'} ({axis})",
                         "uniform gaps",
                         "gaps " + ", ".join(f"{g:.0f}" for g in gaps)))
            break
    return Result(FAIL if rows else PASS,
                  f"{groups_checked} repeated group(s) found", rows)


def check_spacing_proportional(base_nodes, out_nodes, base_doc, base_frame, out_frame):
    """Soft: key vertical gaps should scale with the frame, not collapse or balloon."""
    logos = _count_by_candidates(base_doc, "logoCandidates")
    if not logos or not base_frame or not out_frame:
        return Result(UNAVAIL, "needs a logo candidate plus both frameAbs to derive gap ratios")
    texts = [p for p, n in base_nodes.items() if n.get("type") == "TEXT" and visible(n)]
    if not texts:
        return Result(UNAVAIL, "no visible text nodes in the baseline to measure against")

    def gap(nodes, frame, a_path, b_path):
        ra = frame_relative(nodes[a_path], frame) if a_path in nodes else None
        rb = frame_relative(nodes[b_path], frame) if b_path in nodes else None
        if not ra or not rb:
            return None
        return rb["top"] - ra["bottom"]

    logo_p = logos[0]
    first_text = sorted(texts, key=lambda p: frame_relative(base_nodes[p], base_frame)["top"]
                        if frame_relative(base_nodes[p], base_frame) else 0)[0]
    gm = gap(base_nodes, base_frame, logo_p, first_text)
    go = gap(out_nodes, out_frame, logo_p, first_text)
    if gm is None or go is None or gm == 0:
        return Result(UNAVAIL, "logo→headline gap not measurable in both frames")
    # R2's geometric mean — elements were scaled by uScale, so their gaps should follow uScale,
    # not the raw height ratio. Using height alone over-expects on any placement that adds
    # canvas without adding content (1:1 → 9:16 most of all).
    sx = out_frame["width"] / base_frame["width"]
    sy = out_frame["height"] / base_frame["height"]
    expected = (sx * sy) ** 0.5
    actual = go / gm
    ok = abs(actual - expected) <= TOL_GAP_RATIO * max(expected, 1e-6)
    return Result(PASS if ok else FAIL,
                  f"logo→headline gap {gm:.0f}px → {go:.0f}px",
                  [] if ok else [(logo_p, "logo→headline",
                                  f"≈{expected:.2f}×", f"{actual:.2f}×")])


# ---------------------------------------------------------------- Ad-Specific QA Checklist checks
# Added 2026-09-01, sourced from Rachel's Ad-Specific QA Checklist. R-numbers reference
# HARD-RULES.md's "Ad-Specific QA Checklist alignment" and "Crop operations" sections.

def _cand(doc, key):
    return (doc.get("derived") or {}).get(key) or []


def _first_solid_hex(node):
    fills = node.get("fills")
    if not isinstance(fills, list):
        return None
    for f in fills:
        if f.get("type") == "SOLID" and f.get("hex"):
            return f["hex"]
    return None


def _is_bold(text):
    style = (text or {}).get("fontStyle") or ""
    return "bold" in style.lower()


def _srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _relative_luminance(hex_color):
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return None
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _srgb_to_linear(r) + 0.7152 * _srgb_to_linear(g) + 0.0722 * _srgb_to_linear(b)


def _contrast_ratio(hex_a, hex_b):
    la, lb = _relative_luminance(hex_a), _relative_luminance(hex_b)
    if la is None or lb is None:
        return None
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def _nearest_ancestor_fill(path, nodes_by_path):
    """Walk up the tree from path (exclusive) looking for a solid fill. This is an approximation
    of "what's visually behind this text" via ancestry, not true z-order/occlusion — see R40's
    stated limitation in HARD-RULES.md. Returns (hex, ancestor_path) or (None, None)."""
    cur = parent_path(path)
    while cur is not None:
        node = nodes_by_path.get(cur)
        if node:
            hex_ = _first_solid_hex(node)
            if hex_:
                return hex_, cur
        cur = parent_path(cur)
    return None, None


def check_microcopy_min_size(out_nodes, out_cand_doc):
    """R32 — every visible TEXT node that is neither the headline nor the CTA label."""
    headline = set(_cand(out_cand_doc, "headlineCandidates"))
    cta_label = set(_cand(out_cand_doc, "ctaLabelCandidates"))
    rows, checked = [], 0
    for n in out_nodes.values():
        if n.get("type") != "TEXT" or not visible(n):
            continue
        if n["path"] in headline or n["path"] in cta_label:
            continue
        fs = (n.get("text") or {}).get("fontSize")
        if not isinstance(fs, (int, float)):
            continue
        checked += 1
        if fs < MIN_MICROCOPY_PX:
            rows.append((n["path"], n["name"], f"≥{MIN_MICROCOPY_PX}px", f"{fs}px"))
    return Result(FAIL if rows else PASS, f"{checked} microcopy node(s) checked", rows)


def check_cta_text_min_size(out_nodes, out_cand_doc, spec):
    if spec.get("ctaRule") == "never":
        return Result(PASS, "ctaRule is 'never' for this placement — no CTA expected")
    labels = [p for p in _cand(out_cand_doc, "ctaLabelCandidates") if p in out_nodes]
    if not labels:
        return Result(UNAVAIL, "no CTA label candidate identified in the output")
    rows = []
    for p in labels:
        n = out_nodes[p]
        if not visible(n):
            continue
        fs = (n.get("text") or {}).get("fontSize")
        if isinstance(fs, (int, float)) and fs < MIN_CTA_TEXT_PX:
            rows.append((p, n["name"], f"≥{MIN_CTA_TEXT_PX}px", f"{fs}px"))
    return Result(FAIL if rows else PASS, f"{len(labels)} CTA label(s) checked", rows)


def check_h2_min_size(out_nodes):
    """R34 (size half only — line-count caps are vision-owned, see message_hierarchy_line_cap)."""
    rows, found = [], 0
    for n in out_nodes.values():
        if n.get("type") != "TEXT" or not visible(n):
            continue
        name = (n.get("name") or "").lower()
        if not any(k in name for k in ("subheadline", "sub-headline", "subhead", "h2")):
            continue
        found += 1
        fs = (n.get("text") or {}).get("fontSize")
        if isinstance(fs, (int, float)) and fs < MIN_H2_PX:
            rows.append((n["path"], n["name"], f"≥{MIN_H2_PX}px", f"{fs}px"))
    if not found:
        return Result(PASS, "no H2/subheadline node identified — rule is conditional on one existing")
    return Result(FAIL if rows else PASS, f"{found} H2/subheadline node(s) checked", rows)


def check_new_text_font_family(base_nodes, out_nodes):
    """R37 — a node with no matching baseline path is new, not modified."""
    new_text = [n for p, n in out_nodes.items()
                if n.get("type") == "TEXT" and p not in base_nodes and visible(n)]
    if not new_text:
        return Result(PASS, "no newly added text nodes")
    rows = []
    for n in new_text:
        family = (n.get("text") or {}).get("fontFamily")
        if family != "Poppins":
            rows.append((n["path"], n["name"], "Poppins", str(family)))
    return Result(FAIL if rows else PASS, f"{len(new_text)} new text node(s) checked", rows)


def check_cta_matches_master(base_doc, out_doc, base_nodes, out_nodes, spec):
    """R38 — CTA inclusion follows the master, except a hard 'never' platform exception."""
    rule = spec.get("ctaRule")
    if rule not in ("never", "follows-master"):
        return Result(UNAVAIL, "placement spec has no ctaRule ('never' or 'follows-master')")

    def has_visible_cta(nodes, cand_doc):
        for p in _cand(cand_doc, "ctaCandidates"):
            n = nodes.get(p)
            if n and visible(n):
                return True
        return False

    output_has_cta = has_visible_cta(out_nodes, out_doc)
    if rule == "never":
        if output_has_cta:
            return Result(FAIL, "", [("—", "CTA", "no CTA (ctaRule: never)", "CTA present")])
        return Result(PASS, "ctaRule: never — confirmed no visible CTA")

    master_has_cta = has_visible_cta(base_nodes, base_doc)
    if master_has_cta == output_has_cta:
        return Result(PASS, f"master has CTA: {master_has_cta} · output has CTA: {output_has_cta}")
    return Result(FAIL, "", [("—", "CTA", f"master has CTA: {master_has_cta}",
                              f"output has CTA: {output_has_cta}")])


def _visual_candidate_path(nodes):
    """No dedicated derived field for 'the visual' yet — approximate as the largest IMAGE fill
    by local area. Used only by R40 (contrast) and R42 (clearance) as a supporting signal, not
    as an authoritative role assignment — RESIZE-WORKFLOW.md Step 3 still confirms with the user."""
    best_path, best_area = None, 0
    for n in nodes.values():
        if n.get("image"):
            area = (n["local"]["width"] or 0) * (n["local"]["height"] or 0)
            if area > best_area:
                best_area, best_path = area, n["path"]
    return best_path


def check_contrast_wcag(out_nodes):
    """R40 — consolidates F3/F4/F5. See HARD-RULES.md R40 for the stated limitation: 'background'
    here is the nearest ancestor with a solid fill, not true occlusion/z-order analysis."""
    rows, checked, skipped = [], 0, 0
    for n in out_nodes.values():
        if n.get("type") != "TEXT" or not visible(n):
            continue
        fg = _first_solid_hex(n)
        if not fg:
            skipped += 1
            continue
        bg, bg_path = _nearest_ancestor_fill(n["path"], out_nodes)
        if not bg:
            skipped += 1
            continue
        ratio = _contrast_ratio(fg, bg)
        if ratio is None:
            skipped += 1
            continue
        checked += 1
        text = n.get("text") or {}
        fs = text.get("fontSize") or 0
        large = fs >= LARGE_TEXT_PX or (fs >= LARGE_TEXT_BOLD_PX and _is_bold(text))
        threshold = WCAG_LARGE_RATIO if large else WCAG_NORMAL_RATIO
        if ratio < threshold:
            rows.append((n["path"], n["name"], f"≥{threshold}:1 vs {bg} ({bg_path})",
                         f"{ratio:.2f}:1"))
    detail = f"{checked} text node(s) checked"
    if skipped:
        detail += f", {skipped} skipped (no solid fg/bg fill found — see limitation note)"
    return Result(FAIL if rows else PASS, detail, rows)


def check_min_clearance_floor(out_nodes, out_frame, spec, out_cand_doc):
    """R42 — absolute pixel floors from placements.json's minGaps, independent of R26's
    proportionality check. Numbers are the skill's own pre-existing minGaps, not sourced from
    the QA Checklist doc — see HARD-RULES.md R42."""
    min_gaps = spec.get("minGaps")
    if not min_gaps or not out_frame:
        return Result(UNAVAIL, "placement spec has no minGaps, or output frameAbs missing")

    logo = next((p for p in _cand(out_cand_doc, "logoCandidates") if p in out_nodes), None)
    headline = next((p for p in _cand(out_cand_doc, "headlineCandidates") if p in out_nodes), None)
    cta = next((p for p in _cand(out_cand_doc, "ctaCandidates") if p in out_nodes), None)
    visual = _visual_candidate_path(out_nodes)

    def gap_between(a_path, b_path):
        if not a_path or not b_path or a_path == b_path:
            return None
        ra = frame_relative(out_nodes[a_path], out_frame) if a_path in out_nodes else None
        rb = frame_relative(out_nodes[b_path], out_frame) if b_path in out_nodes else None
        if not ra or not rb:
            return None
        # vertical gap if they don't overlap in y, else horizontal
        if rb["top"] >= ra["bottom"]:
            return rb["top"] - ra["bottom"]
        if ra["top"] >= rb["bottom"]:
            return ra["top"] - rb["bottom"]
        return max(rb["left"] - ra["right"], ra["left"] - rb["right"], 0)

    pairs_to_check = [
        ("logoToHeadline", logo, headline),
        ("textToVisual", headline, visual),
        ("anyToCta", visual or headline, cta),
    ]
    rows, checked = [], 0
    for key, a, b in pairs_to_check:
        floor = min_gaps.get(key)
        if floor is None:
            continue
        gap = gap_between(a, b)
        if gap is None:
            continue
        checked += 1
        if gap < floor:
            rows.append((f"{a}↔{b}", key, f"≥{floor}px", f"{gap:.0f}px"))
    if not checked:
        return Result(UNAVAIL, "no role-candidate pair was measurable (logo/headline/CTA/visual)")
    return Result(FAIL if rows else PASS, f"{checked} element-pair gap(s) checked", rows)


def check_crop_composition_purity(out_nodes, out_doc):
    """R43 — a crop placement has no visible text, logo, or CTA node. Only meaningful when
    operationType is 'crop'; the runner only calls this for crop placements."""
    rows = []
    text_count = sum(1 for n in out_nodes.values()
                     if n["path"] != "0" and n.get("type") == "TEXT" and visible(n))
    if text_count:
        rows.append(("—", "TEXT nodes", "0", str(text_count)))
    for key, label in (("logoCandidates", "logo"), ("ctaCandidates", "CTA")):
        present = [p for p in _cand(out_doc, key) if p in out_nodes and visible(out_nodes[p])]
        if present:
            rows.append(("—", label, "0", str(len(present))))
    return Result(FAIL if rows else PASS, "checked for text/logo/CTA nodes", rows)


# ---------------------------------------------------------------- runner

def main():
    ap = argparse.ArgumentParser(description="Gate layer 9b — measurement diff")
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--placement", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--rules", required=True)
    args = ap.parse_args()

    base = load_json(args.baseline, "baseline")
    out = load_json(args.output, "output measurement")

    # Comparing two outputs, or a master against itself, is a quiet way to produce a clean
    # report that means nothing. Refuse rather than proceed.
    if (base.get("meta") or {}).get("role") != "master":
        sys.exit("ERROR: --baseline meta.role is not 'master'. Re-measure the master frame "
                 "before any clone exists (PRE-RESIZE-MEASUREMENT.md).")
    if (out.get("meta") or {}).get("role") != "output":
        sys.exit("ERROR: --output meta.role is not 'output'.")

    try:
        with open(args.spec, encoding="utf-8") as fh:
            spec_all = json.load(fh)
        spec = (spec_all.get("placements") or spec_all).get(args.placement) or {}
        spec_note = "" if spec else f"placement '{args.placement}' not found in {args.spec}"
    except FileNotFoundError:
        spec, spec_note = {}, f"{args.spec} not found — spec-dependent checks unavailable"

    try:
        with open(args.rules, encoding="utf-8") as fh:
            rules = {r["id"]: r for r in csv.DictReader(fh)}
    except FileNotFoundError:
        sys.exit(f"ERROR: rules file not found: {args.rules}")

    base_nodes, out_nodes = index_by_path(base), index_by_path(out)
    base_frame = (base.get("meta") or {}).get("frameAbs")
    out_frame = (out.get("meta") or {}).get("frameAbs")

    pairs, unmatched, renamed = [], [], []
    for path, m in base_nodes.items():
        o = out_nodes.get(path)
        if o is None:
            unmatched.append((path, m.get("name")))
            continue
        if path != "0" and m.get("name") != o.get("name"):
            renamed.append((path, m.get("name"), o.get("name")))
        pairs.append((path, m, o))

    match_rate = len(pairs) / len(base_nodes) if base_nodes else 0
    op_type = spec.get("operationType", "resize")

    # Checks that apply regardless of operation type.
    results = {
        "exact_dimensions":         check_dimensions(out, spec),
        "no_offcanvas_elements":    check_offcanvas(out_nodes, out_frame, spec),
        "frame_named_and_parented": check_frame_named_parented(out, spec),
    }
    skipped_for_op_type = []

    if op_type == "resize":
        results.update({
            "geometry_aspect_ratio_preserved": check_aspect_ratio(pairs),
            "geometry_position_redistributed": check_position_redistributed(out_nodes, out_frame, spec),
            "mask_image_aligned":              check_mask_alignment(out),
            "crop_transform_uniform":          check_crop_uniform(out_nodes),
            "no_rotation_applied":             check_rotation(pairs),
            "logo_count_matches":              check_role_count(base, out, out_nodes, "logoCandidates", "logo"),
            "logo_proportional_only":          check_logo_proportional(base_nodes, out_nodes, base),
            "text_content_verbatim":           check_text_verbatim(pairs),
            "text_fits_bounds":                check_text_fits(out_nodes, out_frame, spec),
            "icon_count_matches":              check_role_count(base, out, out_nodes, "iconCandidates", "icon"),
            "fill_colors_unchanged":           _sig_check(pairs, fills_signature, "fills compared"),
            "gradient_preserved":              _sig_check(pairs, gradient_signature, "gradient fills compared"),
            "effects_preserved":               _sig_check(pairs, effects_signature, "effect stacks compared"),
            "opacity_preserved":               check_opacity(pairs),
            "typography_preserved":            check_typography(pairs),
            "safe_zone_respected":             check_safe_zone(out_nodes, out_frame, spec),
            "spacing_proportional":            check_spacing_proportional(base_nodes, out_nodes, base,
                                                                         base_frame, out_frame),
            "repeated_gaps_uniform":           check_repeated_gaps(out_nodes, out_frame),
            # Ad-Specific QA Checklist alignment (2026-09-01) — resize-only.
            "microcopy_min_size":       check_microcopy_min_size(out_nodes, out),
            "cta_text_min_size":        check_cta_text_min_size(out_nodes, out, spec),
            "h2_min_size":              check_h2_min_size(out_nodes),
            "new_text_font_family":     check_new_text_font_family(base_nodes, out_nodes),
            "cta_matches_master_rule":  check_cta_matches_master(base, out, base_nodes, out_nodes, spec),
            "contrast_meets_wcag":      check_contrast_wcag(out_nodes),
            "min_clearance_floor":      check_min_clearance_floor(out_nodes, out_frame, spec, out),
        })
        skipped_for_op_type = ["crop_composition_purity (crop-only, not applicable to a resize placement)"]
    elif op_type == "crop":
        results["crop_composition_purity"] = check_crop_composition_purity(out_nodes, out)
        skipped_for_op_type = [
            "every resize-composition rule — logo/text/icon/CTA preservation, geometry, spacing, "
            "typography — is not applicable to a crop placement (HARD-RULES.md, 'Crop operations')"
        ]
    else:
        skipped_for_op_type = [f"unknown operationType '{op_type}' — only resize-only checks ran"]

    # ------------------------------------------------------------ report

    bm, om = base.get("meta", {}), out.get("meta", {})
    print(f"RESIZE QA — {om.get('frameName', '?')}  [operationType: {op_type}]")
    print(f"baseline: {args.baseline} ({bm.get('frameAbs', {}).get('width')}×"
          f"{bm.get('frameAbs', {}).get('height')})    output: {args.output}")
    print(f"nodes matched: {len(pairs)}/{len(base_nodes)}", end="")
    print(f"   placement: {args.placement}")
    if spec_note:
        print(f"  ! {spec_note}")
    for note in skipped_for_op_type:
        print(f"  · not applicable here: {note}")

    # A crop placement is SUPPOSED to look nothing like the master structurally — it discards
    # almost everything on purpose. These warnings exist to catch structural drift in a resize
    # placement, where the tree should stay intact; on a crop placement they'd just be noise
    # reporting the design working as intended, so they're skipped entirely rather than printed
    # and then explained away.
    if op_type == "resize":
        if match_rate < MIN_MATCH_RATE:
            print(f"  ! STRUCTURAL WARNING: only {match_rate:.0%} of baseline paths matched. "
                  f"Structure diverged — investigate before trusting anything below.")
        if unmatched:
            print(f"  ! {len(unmatched)} baseline path(s) absent from output: "
                  + ", ".join(f"{p} ({n})" for p, n in unmatched[:5])
                  + (" …" if len(unmatched) > 5 else ""))
        if renamed:
            print(f"  ! {len(renamed)} node(s) renamed (geometry still valid): "
                  + ", ".join(f"{p}" for p, _a, _b in renamed[:5]))

    script_rules = {rid: r for rid, r in rules.items() if r.get("owner") == "script"}
    vision_rules = [rid for rid, r in rules.items() if r.get("owner") != "script"]

    def emit(section, wanted_sev):
        printed = False
        ordered = sorted(script_rules.items(),
                         key=lambda kv: -float(kv[1].get("weight") or 0))
        for rid, meta in ordered:
            if meta.get("severity") != wanted_sev:
                continue
            res = results.get(rid)
            if res is None:
                continue
            if not printed:
                print(f"\n{section}")
                printed = True
            mark = {PASS: "✓", FAIL: "✗", UNAVAIL: "?"}[res.status]
            ref = meta.get("rule_ref", "")
            head = f"  {mark} {rid:<34} {ref:<12}"
            print(head + (f" {res.detail}" if res.detail else ""))
            for path, name, exp, got in res.rows[:8]:
                print(f"      {path:<10} {str(name)[:22]:<22} expected {exp:<24} measured {got}")
            if len(res.rows) > 8:
                print(f"      … {len(res.rows) - 8} more")
        return printed

    emit("HARD RULES", "hard")
    emit("SOFT FINDINGS", "soft")

    # Read live from the CSV's owner column — this is what stops a clean script run from
    # being mistaken for a complete QA (R31 / ACCURACY-GATE.md).
    print(f"\nVISION-OWNED — NOT CHECKED HERE ({len(vision_rules)} rules)")
    for i in range(0, len(vision_rules), 3):
        print("  " + " · ".join(vision_rules[i:i + 3]))

    hard_fail = [rid for rid, r in results.items()
                 if r.status == FAIL and script_rules.get(rid, {}).get("severity") == "hard"]
    unavail = [rid for rid, r in results.items() if r.status == UNAVAIL]

    print()
    if unavail:
        print(f"UNVERIFIABLE ({len(unavail)}): " + ", ".join(sorted(unavail)))
        print("  These are not passes. Resolve the missing input or check them by hand.")
    if hard_fail:
        print(f"VERDICT: NOT DONE — {len(hard_fail)} hard rule(s) failing: "
              + ", ".join(sorted(hard_fail)))
    else:
        print("VERDICT: mechanizable half clean — 0 hard rules failing.")
        print("  Not 'QA complete' (R31). Layers 9a and 9c still apply.")

    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())

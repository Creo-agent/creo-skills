#!/usr/bin/env python3
"""
qa_gate.py — one mechanized check per section or page, after build, before the vision look.

Why this exists
----------------
Before this script, every check below existed only as a loose JS snippet inside
ACCURACY-GATE.md §1b prose — something a model had to remember to paste, every section, by hand.
That is exactly why a systematic 48px container-width error survived 8 per-section vision passes
plus a full-page pass: the one check that would have caught it (border-box CONTENT-width
arithmetic, not box width) was prose, not a command. This script makes "is this section done" an
exit code instead of a memory exercise.

**This is strictly additive to vision QA, never a replacement for it** (see SKILL.md's
non-negotiable #1). The `vision_owned` key in every result is load-bearing: it lists exactly which
`web-design-rules.csv` rules and HARD-RULES.md H-rules this script does NOT check, so a clean
`exit 0` can never be misread as "QA complete." Ownership for every rule is read live from
`reference/web-design-rules.csv`'s `owner` column and `reference/HARD-RULES.md`'s `**Owner:**`
lines — not hardcoded here — so `vision_owned`/`pre_build_owned` can never drift from Phase 4's
tagging. On startup, this script also asserts the reverse: every rule tagged `owner: script`
resolves to a handler registered below (SCRIPT_RULE_HANDLERS / SCRIPT_HRULE_HANDLERS) — a rule
tagged mechanized with no real check is exactly the failure mode Phase 4 exists to close, so this
refuses to run rather than silently skip it.

Usage
-----
  python3 qa_gate.py section --url http://localhost:PORT/index.html --selector '[data-section=X]' \\
                     [--spec /tmp/X-spec.json] [--json]
  python3 qa_gate.py page    --url http://localhost:PORT/index.html [--json]

`section` scopes every applicable check to `--selector` (the section's own root element) and adds
the numeric re-diff against `--spec` (written by `section_spec.py spec`) when given. `page` scopes
to the whole document and adds the checks no single section owns: nav_links_functional, the a11y/
seo/perf page-level groups, H6/H7/H8/H27 (page-structure rules), H21/H22 (page-wide consistency),
and the 3-width overflow scan (1440/820/390 — responsive_intermediate_viewports).

Output: with --json, one JSON object to stdout ({scope, url, hard_failures, soft_findings,
passed, vision_owned, pre_build_owned}) and a one-line summary to stderr. Without --json, the full
human report goes to stdout. Exit 1 on any hard failure (either mode). Requires Playwright with a
Chromium binary already installed (PREREQUISITES.md) — never open a bare file:// URL (GOTCHAS.md).
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference"
CSV_PATH = REFERENCE_DIR / "web-design-rules.csv"
HARD_RULES_PATH = REFERENCE_DIR / "HARD-RULES.md"

VALID_OWNERS = {"pre-build", "script", "vision", "n-a"}


# --------------------------------------------------------------------------- rule ownership

def load_rule_owners():
    """Read the live owner tag for every CSV rule and every H-rule. Never hardcode this list —
    it must read the same source Phase 4 tags, or vision_owned/pre_build_owned can drift from
    what HARD-RULES.md and web-design-rules.csv actually say."""
    owners = {}

    if CSV_PATH.exists():
        import csv
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rid, owner = row.get("id"), (row.get("owner") or "").strip()
                if rid:
                    owners[rid] = owner or None

    if HARD_RULES_PATH.exists():
        text = HARD_RULES_PATH.read_text(encoding="utf-8")
        # "## H4 — <title>" followed eventually by "**Owner:** script" before the next "## H".
        for m in re.finditer(r"^## (H\d+)\b.*$", text, re.MULTILINE):
            hid = m.group(1)
            tail = text[m.end():]
            nxt = re.search(r"^## H\d+\b", tail, re.MULTILINE)
            block = tail[:nxt.start()] if nxt else tail
            om = re.search(r"\*\*Owner:\*\*\s*(\S+)", block)
            owners[hid] = om.group(1).strip() if om else None

    return owners


def self_check(owners, script_rule_handlers, script_hrule_handlers):
    missing = []
    for rid, owner in owners.items():
        if owner is None:
            missing.append(f"{rid}: no owner tag found")
            continue
        if owner not in VALID_OWNERS:
            missing.append(f"{rid}: invalid owner '{owner}' (want one of {sorted(VALID_OWNERS)})")
            continue
        if owner != "script":
            continue
        registry = script_hrule_handlers if rid.startswith("H") else script_rule_handlers
        if rid not in registry:
            missing.append(f"unimplemented rule: {rid} (tagged owner:script, no handler)")
    if missing:
        sys.exit("qa_gate.py self-check failed — fix before running:\n  "
                  + "\n  ".join(missing))


# --------------------------------------------------------------------------- check registry
#
# Every CSV rule / H-rule tagged `owner: script` in web-design-rules.csv / HARD-RULES.md MUST
# appear as a key here, mapped to the function that actually implements it. This is Phase 4's
# anti-drift mechanism: self_check() above refuses to run if a tag and a handler disagree.

SCRIPT_RULE_HANDLERS = {
    "responsive_no_horizontal_scroll": "check_overflow",
    "responsive_intermediate_viewports": "check_overflow",
    "layout_repeated_items_wrap": "check_overflow",
    "responsive_touch_targets": "check_touch_targets",
    "color_contrast_accessibility": "check_contrast",
    "image_alt_text": "check_image_alt",
    "image_aspect_ratio": "check_image_aspect_ratio",
    "text_no_placeholder_content": "check_placeholder_text",
    "a11y_disclosure_state": "check_disclosure_aria",
    "a11y_semantic_structure": "check_heading_structure",
    "seo_heading_structure": "check_heading_structure",
    "seo_meta_tags_present": "check_seo_meta",
    "perf_no_layout_shift": "check_layout_shift_attrs",
    "nav_links_functional": "check_nav_links",
    "font_family_consistency": "check_font_family_consistency",
    "text_no_truncation": "check_text_truncation",
    "image_resolution_quality": "check_image_resolution",
    "interactive_states_present": "check_interactive_states",
    "perf_image_optimization": "check_image_resolution",
    "a11y_keyboard_navigation": "check_keyboard_navigation",
    "responsive_actions_full_width": "check_cta_mobile_width",
    "ds_component_reuse_check_placeholder": "n/a",  # never registered — see note below
}
# ds_component_reuse_check is owner:pre-build, not owner:script — the line above is intentionally
# never looked up; it exists only so a reviewer scanning this dict doesn't wonder where it went.
del SCRIPT_RULE_HANDLERS["ds_component_reuse_check_placeholder"]

SCRIPT_HRULE_HANDLERS = {
    "H2": "check_h2_no_clay_names",
    "H4": "check_h4_no_base64",
    "H5": "check_h5_interactivity",
    "H6": "check_h6_duplicate_sections",
    "H7": "check_h7_sentinel",
    "H8": "check_h8_duplicate_head",
    "H10": "check_image_aspect_ratio",
    "H11": "check_image_alt",
    "H12": "check_layout_shift_attrs",
    "H13": "check_lazy_load_sliders",
    "H14": "check_heading_font_weight",
    "H16": "check_text_max_width",
    "H20": "check_state_variant_consistency",
    "H21": "check_cta_consistency",
    "H22": "check_container_consistency",
    "H24": "check_leaf_centering",
    "H27": "check_h27_page_structure",
    "H29": "check_image_blank",
    "H30": "check_icon_glyph_placeholder",
}


# --------------------------------------------------------------------------- finding helper

def finding(rid, severity, message, expected=None, measured=None, scope="section"):
    return {"id": rid, "severity": severity, "message": message,
            "expected": expected, "measured": measured, "scope": scope}


# --------------------------------------------------------------------------- checks — shared JS

def _eval_in_scope(page, selector, js_body):
    """Run js_body with `root` bound to document.querySelector(selector) (or document.body when
    selector is None/'body'). js_body must be a JS function body returning its result."""
    root_expr = "document.body" if not selector or selector == "body" else \
        f"document.querySelector({json.dumps(selector)})"
    return page.evaluate(f"() => {{ const root = {root_expr}; if (!root) return null; {js_body} }}")


def check_overflow(page, selector, scope):
    widths = [1440, 820, 390]
    results = []
    for w in widths:
        page.set_viewport_size({"width": w, "height": 900})
        overflow = page.evaluate(
            "document.documentElement.scrollWidth > document.documentElement.clientWidth")
        results.append((w, overflow))
    page.set_viewport_size({"width": 1440, "height": 900})
    bad = [w for w, o in results if o]
    findings = []
    if bad:
        for rid in ("responsive_no_horizontal_scroll", "responsive_intermediate_viewports",
                    "layout_repeated_items_wrap"):
            findings.append(finding(rid, "hard",
                f"horizontal overflow at {', '.join(str(w) for w in bad)}px",
                expected="no horizontal scroll at 1440/820/390px",
                measured=f"overflow at {bad}", scope="page"))
    return findings


def check_image_alt(page, selector, scope):
    bad = _eval_in_scope(page, selector, """
      return [...root.querySelectorAll('img')]
        .filter(img => !img.hasAttribute('alt') || img.getAttribute('alt') === null)
        .map(img => img.src.split('/').pop());
    """) or []
    if not bad:
        return []
    return [finding("image_alt_text", "hard", f"{len(bad)} <img> missing alt attribute",
                     expected="every <img> has alt", measured=bad, scope=scope)]


def check_image_loaded(page, selector, scope):
    bad = _eval_in_scope(page, selector, """
      return [...root.querySelectorAll('img')]
        .filter(img => !img.complete || img.naturalWidth === 0)
        .map(img => img.src.split('/').pop());
    """) or []
    if not bad:
        return []
    return [finding("img_loaded", "hard", f"{len(bad)} <img> never loaded (naturalWidth 0)",
                     expected="img.complete && naturalWidth > 0 for every image",
                     measured=bad, scope=scope)]


def check_image_blank(page, selector, scope):
    # H29. `naturalWidth > 0` only proves the file decoded, not that it contains artwork. A Figma
    # asset URL can hand back a correctly-dimensioned but fully transparent PNG (real case: 3 of 4
    # certification badges), which passes img_loaded, passes aspect-ratio, passes resolution, and
    # renders as nothing. Read the actual pixels back through a canvas. Same-origin only, which is
    # already guaranteed — this script refuses file:// and the assets are served beside the page.
    # SVGs are skipped: they're vector, drawing one whose root has no intrinsic width/height
    # rasterizes at the browser's 300x150 fallback and would measure the wrong thing.
    bad = _eval_in_scope(page, selector, """
      const out = [];
      for (const img of [...root.querySelectorAll('img')]) {
        if (!img.complete || !img.naturalWidth) continue;
        if (/\\.svg($|\\?)/i.test(img.src)) continue;
        const w = Math.min(img.naturalWidth, 64), h = Math.min(img.naturalHeight, 64);
        const c = document.createElement('canvas');
        c.width = w; c.height = h;
        const ctx = c.getContext('2d', {willReadFrequently: true});
        let data;
        try { ctx.drawImage(img, 0, 0, w, h); data = ctx.getImageData(0, 0, w, h).data; }
        catch (e) { continue; }
        let opaque = 0, uniform = true;
        for (let i = 0; i < data.length; i += 4) {
          if (data[i + 3] > 8) opaque++;
          if (data[i] !== data[0] || data[i+1] !== data[1] ||
              data[i+2] !== data[2] || data[i+3] !== data[3]) uniform = false;
        }
        const name = img.src.split('/').pop();
        if (opaque === 0) out.push({src: name, why: 'fully transparent'});
        else if (uniform && data[3] === 255 &&
                 ((data[0] === 255 && data[1] === 255 && data[2] === 255) ||
                  (data[0] === 0 && data[1] === 0 && data[2] === 0)))
          out.push({src: name, why: 'single flat colour, no artwork'});
      }
      return out;
    """) or []
    findings = []
    for b in bad:
        findings.append(finding("H29", "hard",
            f"{b['src']} decodes but contains no artwork ({b['why']})",
            expected="asset has visible pixels", measured=b["why"], scope=scope))
    return findings


def check_icon_glyph_placeholder(page, selector, scope):
    # H30. A Unicode glyph standing in for a real Figma icon renders as *something*, so it trips
    # no broken-image, contrast, or alt check, and it's too small to notice in a scaled-down
    # full-page vision capture. Real case: `<span class="app-dot">M</span>` shipped in place of
    # the Slack/Gmail/monday app logos through a full mechanized pass AND a full-page vision pass.
    # Detect the shape of the mistake: an icon-sized/icon-named leaf holding a bare symbol
    # character instead of an <img>/<svg>/background-image.
    bad = _eval_in_scope(page, selector, """
      const SYMBOL = /[\\u2190-\\u2BFF\\u2E00-\\u2E7F\\u{1F000}-\\u{1FAFF}\\uFE0F]/u;
      const ICONISH = /icon|logo|app-|app_|badge|chip|dot|mark|avatar|arrow|glyph/i;
      const out = [];
      for (const el of root.querySelectorAll('*')) {
        if (el.childElementCount) continue;
        // Opt-out for the one legitimate case: Figma's own layer is a TEXT node holding this
        // character. Must be declared explicitly per element so it stays auditable — a silent
        // allowlist here would re-open exactly the hole this rule closes.
        if (el.hasAttribute('data-figma-text-glyph')) continue;
        const text = (el.textContent || '').trim();
        if (!text || [...text].length > 2 || !SYMBOL.test(text)) continue;
        const cs = getComputedStyle(el);
        if (cs.backgroundImage && cs.backgroundImage !== 'none') continue;
        const r = el.getBoundingClientRect();
        const named = ICONISH.test(el.className + ' ' + el.id);
        const sized = r.width >= 12 && r.width <= 64 && r.height >= 12 && r.height <= 64 &&
                      Math.max(r.width, r.height) / Math.max(1, Math.min(r.width, r.height)) < 1.6;
        if (!named && !sized) continue;
        out.push({text, cls: el.className || el.tagName.toLowerCase(),
                  box: Math.round(r.width) + 'x' + Math.round(r.height)});
      }
      return out;
    """) or []
    findings = []
    for b in bad:
        findings.append(finding("H30", "hard",
            f"icon slot .{b['cls']} ({b['box']}) holds the glyph {b['text']!r} instead of a real asset",
            expected="<img>/<svg> exported from the Figma node",
            measured=b["text"], scope=scope))
    return findings


def check_image_aspect_ratio(page, selector, scope):
    # img.naturalWidth/naturalHeight is UNRELIABLE for <img src="*.svg"> unless the SVG's own
    # root element declares numeric width/height — an SVG with only a viewBox (the common case
    # for an exported icon/logo, confirmed against real output) reports the browser's generic
    # SVG fallback intrinsic size (300x150, ratio exactly 2.0) instead of its real shape. Fetch
    # the SVG text (same-origin, already being served for the page itself) and read viewBox
    # directly instead of trusting naturalWidth/Height for any .svg source.
    bad = _eval_in_scope(page, selector, """
      const out = [];
      const imgs = [...root.querySelectorAll('img')];
      return (async () => {
        for (const img of imgs) {
          const rendered = img.getBoundingClientRect();
          if (!rendered.width || !rendered.height) continue;
          const renRatio = rendered.width / rendered.height;
          let natRatio = null;
          if (/\\.svg($|\\?)/i.test(img.src)) {
            try {
              const text = await (await fetch(img.src)).text();
              const m = text.match(/viewBox=["']\\s*[\\d.+-]+\\s+[\\d.+-]+\\s+([\\d.]+)\\s+([\\d.]+)/i);
              if (m) natRatio = parseFloat(m[1]) / parseFloat(m[2]);
              else {
                const wm = text.match(/<svg[^>]*\\bwidth=["']([\\d.]+)/i);
                const hm = text.match(/<svg[^>]*\\bheight=["']([\\d.]+)/i);
                if (wm && hm) natRatio = parseFloat(wm[1]) / parseFloat(hm[1]);
              }
            } catch (e) {}
          } else if (img.naturalWidth && img.naturalHeight) {
            natRatio = img.naturalWidth / img.naturalHeight;
          }
          if (!natRatio) continue;
          const delta = Math.abs(natRatio - renRatio) / natRatio;
          if (delta > 0.03) out.push({src: img.src.split('/').pop(),
                                       natural: natRatio.toFixed(3), rendered: renRatio.toFixed(3)});
        }
        return out;
      })();
    """) or []
    findings = []
    for b in bad:
        findings.append(finding("image_aspect_ratio", "hard",
            f"{b['src']} rendered aspect ratio drifted from its natural ratio",
            expected=b["natural"], measured=b["rendered"], scope=scope))
        findings.append(finding("H10", "hard",
            f"{b['src']} not sized from its own intrinsic aspect-ratio",
            expected=b["natural"], measured=b["rendered"], scope=scope))
    return findings


def check_image_resolution(page, selector, scope):
    # Vector graphics (.svg) don't blur when displayed larger than their viewBox — that's the
    # point of a vector format — so "resolution" isn't a meaningful concept for them and they're
    # excluded here entirely, not just measured unreliably (see check_image_aspect_ratio's own
    # note on why naturalWidth/Height can't be trusted for an <img src="*.svg"> either way).
    findings = []
    upscaled = _eval_in_scope(page, selector, """
      const out = [];
      for (const img of root.querySelectorAll('img')) {
        if (!img.naturalWidth || /\\.svg($|\\?)/i.test(img.src)) continue;
        const rendered = img.getBoundingClientRect().width * (window.devicePixelRatio || 1);
        if (rendered > img.naturalWidth * 1.15) {
          out.push({src: img.src.split('/').pop(), natural: img.naturalWidth,
                     rendered: Math.round(rendered)});
        }
      }
      return out;
    """) or []
    for u in upscaled:
        findings.append(finding("image_resolution_quality", "hard",
            f"{u['src']} displayed larger than its natural resolution (upscaled/blurry)",
            expected=f">= {u['rendered']}px natural", measured=f"{u['natural']}px natural",
            scope=scope))
    return findings


def check_leaf_centering(page, selector, scope):
    # H24 is specifically about a VERTICALLY STACKED group (logo above heading above
    # description) where text-align: center correctly centers the text but silently fails to
    # center a block-level <img> sibling. It does NOT apply to a horizontal row of side-by-side
    # items (icons, logos) — those are supposed to spread across the container, so each one's own
    # center legitimately differs from the group's center. Detect row-vs-stack by whether
    # children's vertical (Y) extents overlap: overlapping Y = a row (skip), mostly disjoint Y =
    # a stack (apply the check). Guessing this wrong is exactly how a real check turns into noise.
    bad = _eval_in_scope(page, selector, """
      const out = [];
      const groups = [...root.querySelectorAll('*')].filter(el => {
        const cs = getComputedStyle(el);
        return cs.textAlign === 'center' && el.children.length >= 2;
      });
      for (const g of groups) {
        const gr = g.getBoundingClientRect();
        if (!gr.width) continue;
        const kids = [...g.children].map(c => ({ el: c, r: c.getBoundingClientRect() }))
                                     .filter(k => k.r.width > 0);
        if (kids.length < 2) continue;
        let overlapPairs = 0;
        for (let i = 1; i < kids.length; i++) {
          const a = kids[i - 1].r, b = kids[i].r;
          if (a.top < b.bottom && b.top < a.bottom) overlapPairs++;
        }
        if (overlapPairs >= (kids.length - 1) / 2) continue; // row-like — not H24's failure mode
        const gCenter = gr.left + gr.width / 2;
        for (const k of kids) {
          const off = (k.r.left + k.r.width / 2) - gCenter;
          if (Math.abs(off) > 4) {
            out.push({tag: k.el.tagName, cls: k.el.className || '', offCenterPx: Math.round(off)});
          }
        }
      }
      return out;
    """) or []
    if not bad:
        return []
    return [finding("H24", "hard",
                     f"{len(bad)} leaf element(s) not centered despite a centered ancestor",
                     expected="offCenterPx ~= 0", measured=bad, scope=scope)]


def check_disclosure_aria(page, selector, scope):
    bad = _eval_in_scope(page, selector, """
      return [...root.querySelectorAll(
        '[role="tab"], .tab-btn, .accordion-trigger, .faq-question')]
        .filter(el => !el.hasAttribute('aria-selected') && !el.hasAttribute('aria-expanded'))
        .map(el => el.textContent.trim().slice(0, 40));
    """) or []
    if not bad:
        return []
    return [finding("a11y_disclosure_state", "hard",
                     f"{len(bad)} disclosure control(s) with no live aria-selected/aria-expanded",
                     expected="aria-selected or aria-expanded present", measured=bad, scope=scope)]


def check_contrast(page, selector, scope):
    bad = _eval_in_scope(page, selector, """
      function toRgb(str) {
        const m = str.match(/rgba?\\(([\\d.]+),\\s*([\\d.]+),\\s*([\\d.]+)/);
        return m ? [parseFloat(m[1]), parseFloat(m[2]), parseFloat(m[3])] : null;
      }
      function luminance([r, g, b]) {
        const f = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
      }
      function bgOf(el) {
        let n = el;
        while (n) {
          const c = getComputedStyle(n).backgroundColor;
          if (c && !c.startsWith('rgba(0, 0, 0, 0)') && c !== 'transparent') return c;
          n = n.parentElement;
        }
        return 'rgb(255,255,255)';
      }
      const out = [];
      const texty = [...root.querySelectorAll('p,h1,h2,h3,h4,h5,h6,a,span,button,li')]
        .filter(el => el.textContent.trim().length > 0 && el.children.length === 0);
      for (const el of texty) {
        const fg = toRgb(getComputedStyle(el).color);
        const bg = toRgb(bgOf(el));
        if (!fg || !bg) continue;
        const L1 = luminance(fg), L2 = luminance(bg);
        const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
        const fontPx = parseFloat(getComputedStyle(el).fontSize);
        const weight = parseInt(getComputedStyle(el).fontWeight, 10) || 400;
        const large = fontPx >= 24 || (fontPx >= 18.66 && weight >= 700);
        const minRatio = large ? 3 : 4.5;
        if (ratio < minRatio) {
          out.push({text: el.textContent.trim().slice(0, 30), ratio: ratio.toFixed(2),
                     min: minRatio});
        }
      }
      return out.slice(0, 20);
    """) or []
    if not bad:
        return []
    return [finding("color_contrast_accessibility", "hard",
                     f"{len(bad)} text element(s) below WCAG AA contrast ratio",
                     expected=">=3:1 (large text) or >=4.5:1", measured=bad, scope=scope)]


def check_placeholder_text(page, selector, scope):
    bad = _eval_in_scope(page, selector, """
      const re = /lorem ipsum|\\[.*?placeholder.*?\\]|\\btodo\\b|\\btbd\\b/i;
      return [...root.querySelectorAll('*')]
        .filter(el => el.children.length === 0 && re.test(el.textContent))
        .map(el => el.textContent.trim().slice(0, 60));
    """) or []
    if not bad:
        return []
    return [finding("text_no_placeholder_content", "hard",
                     f"{len(bad)} element(s) contain placeholder-looking copy",
                     expected="real Figma copy only", measured=bad, scope=scope)]


def check_text_truncation(page, selector, scope):
    bad = _eval_in_scope(page, selector, """
      return [...root.querySelectorAll('*')].filter(el => {
        const cs = getComputedStyle(el);
        if (cs.textOverflow !== 'ellipsis') return false;
        if (cs.display && cs.display.includes('-webkit-box')) return false; // line-clamp, intentional
        return el.scrollWidth > el.clientWidth + 1;
      }).map(el => el.textContent.trim().slice(0, 40));
    """) or []
    if not bad:
        return []
    return [finding("text_no_truncation", "hard",
                     f"{len(bad)} element(s) truncating text via ellipsis (not a line-clamp)",
                     expected="no unintended truncation", measured=bad, scope=scope)]


def check_heading_structure(page, selector, scope):
    data = page.evaluate("""
      () => {
        const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')]
          .map(h => parseInt(h.tagName[1], 10));
        const h1Count = hs.filter(n => n === 1).length;
        let skipped = false;
        for (let i = 1; i < hs.length; i++) if (hs[i] - hs[i - 1] > 1) skipped = true;
        return { h1Count, skipped, hasNav: !!document.querySelector('nav'),
                 hasMain: !!document.querySelector('main'),
                 hasHeader: !!document.querySelector('header') };
      }
    """)
    findings = []
    if data["h1Count"] != 1:
        findings.append(finding("seo_heading_structure", "soft",
            f"page has {data['h1Count']} <h1> elements (want exactly 1)",
            expected=1, measured=data["h1Count"], scope="page"))
    if data["skipped"]:
        findings.append(finding("a11y_semantic_structure", "hard",
            "heading levels skip a level (e.g. h2 -> h4)", expected="no skipped levels",
            measured="skip detected", scope="page"))
    if not (data["hasNav"] or data["hasMain"] or data["hasHeader"]):
        findings.append(finding("a11y_semantic_structure", "hard",
            "no <nav>/<main>/<header> landmark found on the page",
            expected="at least one semantic landmark", measured="none", scope="page"))
    return findings


def check_seo_meta(page, selector, scope):
    data = page.evaluate("""
      () => ({
        title: !!document.querySelector('title')?.textContent?.trim(),
        description: !!document.querySelector('meta[name="description"]')?.content,
      })
    """)
    findings = []
    if not data["title"]:
        findings.append(finding("seo_meta_tags_present", "soft", "no non-empty <title>",
                                 expected="<title>", measured="missing", scope="page"))
    if not data["description"]:
        findings.append(finding("seo_meta_tags_present", "soft",
            "no <meta name=\"description\">", expected="present", measured="missing",
            scope="page"))
    return findings


def check_layout_shift_attrs(page, selector, scope):
    bad = _eval_in_scope(page, selector, """
      return [...root.querySelectorAll('img')]
        .filter(img => !(img.hasAttribute('width') && img.hasAttribute('height'))
                      && !getComputedStyle(img).aspectRatio.includes('/'))
        .map(img => img.src.split('/').pop());
    """) or []
    if not bad:
        return []
    findings = [finding("perf_no_layout_shift", "soft",
                         f"{len(bad)} <img> with no width/height attrs and no CSS aspect-ratio",
                         expected="width+height attrs or aspect-ratio", measured=bad, scope=scope)]
    findings.append(finding("H12", "hard", f"{len(bad)} <img> missing explicit width/height",
                             expected="explicit width+height attributes", measured=bad,
                             scope=scope))
    return findings


def check_nav_links(page, selector, scope):
    bad = page.evaluate("""
      () => [...document.querySelectorAll('nav a, header a')]
        .filter(a => { const h = a.getAttribute('href');
                       return !h || h === '#' || h.trim() === '' || h === 'javascript:void(0)'; })
        .map(a => a.textContent.trim().slice(0, 30))
    """) or []
    if not bad:
        return []
    return [finding("nav_links_functional", "hard",
                     f"{len(bad)} nav link(s) with an empty/#/void href",
                     expected="real href on every nav link", measured=bad, scope="page")]


def check_font_family_consistency(page, selector, scope):
    families = page.evaluate("""
      () => [...new Set([...document.querySelectorAll('*')]
        .map(el => getComputedStyle(el).fontFamily))]
    """) or []
    if len(families) <= 4:
        return []
    return [finding("font_family_consistency", "hard",
                     f"{len(families)} distinct font-family stacks in use (expected a small,"
                     " consistent set)", expected="<=4 stacks", measured=len(families),
                     scope="page")]


def check_interactive_states(page, selector, scope):
    data = page.evaluate("""
      () => {
        let hoverFocus = 0;
        for (const s of document.styleSheets) {
          try {
            for (const r of s.cssRules) {
              if (r.selectorText && /:hover|:focus/.test(r.selectorText)) hoverFocus++;
            }
          } catch (e) {}
        }
        const interactive = document.querySelectorAll('button, a, .tab-btn, [role="tab"]').length;
        return { hoverFocus, interactive };
      }
    """)
    if data["interactive"] > 0 and data["hoverFocus"] == 0:
        return [finding("interactive_states_present", "hard",
            "interactive elements exist but no :hover/:focus rule found in any stylesheet",
            expected=">=1 :hover/:focus rule", measured=0, scope="page")]
    return []


def check_touch_targets(page, selector, scope):
    page.set_viewport_size({"width": 390, "height": 844})
    bad = _eval_in_scope(page, selector, """
      return [...root.querySelectorAll('button, a, [role="button"], .tab-btn')]
        .map(el => el.getBoundingClientRect())
        .filter(r => r.width > 0 && (r.width < 24 || r.height < 24))
        .map(r => ({ w: Math.round(r.width), h: Math.round(r.height) }));
    """) or []
    page.set_viewport_size({"width": 1440, "height": 900})
    if not bad:
        return []
    return [finding("responsive_touch_targets", "hard",
                     f"{len(bad)} tappable element(s) under 24px on a side at mobile width",
                     expected=">=24px per side", measured=bad, scope=scope)]


def check_keyboard_navigation(page, selector, scope):
    bad = _eval_in_scope(page, selector, """
      return [...root.querySelectorAll('[onclick]')]
        .filter(el => !['A','BUTTON','INPUT','SELECT','TEXTAREA'].includes(el.tagName)
                      && !el.hasAttribute('tabindex'))
        .map(el => el.tagName);
    """) or []
    if not bad:
        return []
    return [finding("a11y_keyboard_navigation", "hard",
                     f"{len(bad)} clickable non-focusable element(s) with no tabindex",
                     expected="tabindex on any non-native clickable", measured=bad, scope=scope)]


def check_cta_mobile_width(page, selector, scope):
    page.set_viewport_size({"width": 390, "height": 844})
    data = _eval_in_scope(page, selector, """
      const btns = [...root.querySelectorAll('.btn, [class*="cta"]')];
      if (!btns.length) return null;
      const vw = window.innerWidth;
      return btns.map(b => b.getBoundingClientRect().width / vw);
    """)
    page.set_viewport_size({"width": 1440, "height": 900})
    if not data:
        return []
    narrow = [round(r, 2) for r in data if r < 0.7]
    if not narrow:
        return []
    return [finding("responsive_actions_full_width", "soft",
                     f"{len(narrow)} primary action(s) under 70% viewport width on mobile",
                     expected=">=70% width", measured=narrow, scope=scope)]


def check_heading_font_weight(page, selector, scope):
    bad = page.evaluate("""
      () => {
        const out = [];
        for (const s of document.styleSheets) {
          try {
            for (const r of s.cssRules) {
              if (r.selectorText && /\\bh[1-6]\\b/i.test(r.selectorText)
                  && !/font-weight/.test(r.cssText)) out.push(r.selectorText);
            }
          } catch (e) {}
        }
        return out;
      }
    """) or []
    if not bad:
        return []
    return [finding("H14", "hard",
                     f"{len(bad)} heading rule(s) with no explicit font-weight",
                     expected="font-weight set on every h1-h6 rule", measured=bad, scope="page")]


def check_lazy_load_sliders(page, selector, scope):
    bad = _eval_in_scope(page, selector, """
      return [...root.querySelectorAll('img[loading="lazy"]')]
        .filter(img => img.closest(
          '[class*="slider"],[class*="carousel"],[class*="marquee"],'
          + '[style*="position: sticky"],[class*="sticky"]'))
        .map(img => img.src.split('/').pop());
    """) or []
    if not bad:
        return []
    return [finding("H13", "hard",
                     f"{len(bad)} lazy-loaded image(s) inside a slider/sticky ancestor",
                     expected="no loading=lazy inside slider/sticky containers", measured=bad,
                     scope=scope)]


def check_state_variant_consistency(page, selector, scope):
    bad = page.evaluate("""
      () => {
        const out = [];
        const groups = {};
        for (const el of document.querySelectorAll('[class]')) {
          const key = [...el.classList].find(c => document.querySelectorAll('.' + c).length > 1);
          if (!key) continue;
          (groups[key] ||= []).push(el);
        }
        for (const [cls, els] of Object.entries(groups)) {
          if (els.length < 2) continue;
          const active = els.filter(e => e.getAttribute('data-active') === 'true'
                                        || e.getAttribute('aria-expanded') === 'true');
          const inactive = els.filter(e => !active.includes(e));
          if (!active.length || !inactive.length) continue;
          const aH = active[0].getBoundingClientRect().height;
          const iH = inactive[0].getBoundingClientRect().height;
          if (Math.abs(aH - iH) > 4) {
            out.push({ cls, activeHeight: Math.round(aH), inactiveHeight: Math.round(iH) });
          }
        }
        return out;
      }
    """) or []
    if not bad:
        return []
    return [finding("H20", "hard",
                     f"{len(bad)} state-variant group(s) with mismatched active/inactive height "
                     "at this viewport", expected="equal height", measured=bad, scope="page")]


def check_cta_consistency(page, selector, scope):
    data = page.evaluate("""
      () => [...document.querySelectorAll('.btn')].map(b => {
        const cs = getComputedStyle(b);
        return { cls: b.className, height: Math.round(b.getBoundingClientRect().height),
                 fontSize: cs.fontSize, padding: cs.padding };
      })
    """) or []
    if len(data) < 2:
        return []
    first = data[0]
    bad = [d for d in data[1:] if d["height"] != first["height"] or d["fontSize"] != first["fontSize"]]
    if not bad:
        return []
    return [finding("H21", "hard",
                     f"{len(bad)} CTA button(s) don't match the page's first .btn size/style",
                     expected=f"height={first['height']} fontSize={first['fontSize']}",
                     measured=bad, scope="page")]


def check_container_consistency(page, selector, scope, exempt=None):
    # Prefer the documented `.section-<slug>-inner` convention (SECTION-WORKFLOW.md Step 6)
    # exactly, when a section follows it. In practice, real sections often don't (confirmed
    # against persona-mini-sites-hr's shipped output: 0 of 12 sections use that exact class) —
    # so the fallback is the section's WIDEST direct child, not its first one. "First child" is
    # unsafe (a heading or text column is frequently first and narrower than the real content
    # wrapper); "widest child" is a real, structural signal — the element holding the section's
    # main content is normally the one that spans closest to the container's own width, whereas a
    # narrower sibling (a centered heading, a text column beside a media column) reports smaller.
    # A section with no direct child reaching even half its own width is reported as unmeasurable
    # (soft), not silently guessed at with a low-confidence pick.
    data = page.evaluate("""
      () => [...document.querySelectorAll('[data-section]')].map(s => {
        const slug = s.getAttribute('data-section');
        let inner = s.querySelector(':scope > .section-' + slug + '-inner');
        if (!inner) {
          const sw = s.getBoundingClientRect().width;
          const children = [...s.children]
            .map(c => ({ el: c, w: c.getBoundingClientRect().width }))
            .sort((a, b) => b.w - a.w);
          inner = (children[0] && children[0].w >= sw * 0.5) ? children[0].el : null;
        }
        if (!inner) return { slug, contentWidth: null };
        const cs = getComputedStyle(inner);
        const r = inner.getBoundingClientRect();
        const contentWidth = r.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
        return { slug, contentWidth: Math.round(contentWidth) };
      })
    """) or []

    exempt = set(exempt or [])
    unmeasurable = [d["slug"] for d in data if d["contentWidth"] is None and d["slug"] not in exempt]
    measured = [d for d in data if d["contentWidth"] is not None and d["slug"] not in exempt]

    findings = []
    if unmeasurable:
        findings.append(finding("H22", "soft",
            f"{len(unmeasurable)} section(s) have no direct child reaching half the section's "
            "own width (and don't use .section-<slug>-inner), so container-width consistency "
            "couldn't be measured for them",
            expected=".section-<slug>-inner, or a direct child >=50% section width",
            measured=unmeasurable, scope="page"))

    if len(measured) >= 2:
        counts = Counter(d["contentWidth"] for d in measured)
        common_width, _ = counts.most_common(1)[0]
        bad = [d for d in measured if abs(d["contentWidth"] - common_width) > 4]
        if bad:
            findings.append(finding("H22", "hard",
                f"{len(bad)} section(s) with a content width that doesn't match the page's "
                "established container convention. If any of these is a deliberate full-bleed "
                "carousel/marquee (H22's own named exception), pass its slug to --width-exempt "
                "rather than treating this as a false positive.",
                expected=f"{common_width}px content width", measured=bad, scope="page"))
    return findings


def check_h2_no_clay_names(html_text, scope):
    # H2 bans Clay component names as HTML class names/IDs/structural labels — it explicitly does
    # NOT ban a CSS comment crediting which real Clay component the CSS/structure was ported from
    # (CLAY-INTEGRATION.md's own resolution process expects exactly that comment). Scan only
    # class="..."/id="..." attribute VALUES, never the whole HTML text (which includes comments).
    known = ("HeaderSection", "CardGrid", "FeaturesSection", "FooterSection", "HeroSection")
    attr_values = re.findall(r'(?:class|id)="([^"]*)"', html_text)
    bad = sorted({n for n in known for v in attr_values if n in v})
    if not bad:
        return []
    return [finding("H2", "hard", f"Clay component name(s) found in a class/id attribute: {bad}",
                     expected="no Clay React component names in class/id output", measured=bad,
                     scope=scope)]


def check_h4_no_base64(html_text, scope):
    count = html_text.count("data:image/")
    if not count:
        return []
    return [finding("H4", "hard",
                     f"{count} base64 data:image/ URI(s) in the primary linked-file deliverable",
                     expected="0 (real linked files, base64 only in the optional variant)",
                     measured=count, scope=scope)]


def check_h5_interactivity(html_text, scope):
    signals = ("ScrollTrigger", "gsap", "setInterval", "@keyframes marquee",
               "IntersectionObserver", "position: sticky")
    found = [s for s in signals if s in html_text]
    if len(found) >= 1:
        return []
    return [finding("H5", "hard", "no baseline interactivity signal found in a full-page build",
                     expected="at least one of " + ", ".join(signals), measured="none",
                     scope=scope)]


def check_h6_duplicate_sections(html_text, scope):
    slugs = re.findall(r'data-section="([^"]+)"', html_text)
    dupes = [s for s, n in Counter(slugs).items() if n > 1]
    if not dupes:
        return []
    return [finding("H6", "hard", f"section(s) duplicated in the page file: {dupes}",
                     expected="each data-section slug appears once", measured=dupes, scope=scope)]


def check_h7_sentinel(html_text, scope):
    if re.search(r"<!--\s*SECTIONS_END\s*-->\s*</main>", html_text, re.IGNORECASE):
        return []
    where = "present, but not immediately before </main>" if "<!-- SECTIONS_END -->" in html_text else "missing"
    return [finding("H7", "hard", "sentinel <!-- SECTIONS_END --> missing immediately before </main>",
                     expected="<!-- SECTIONS_END --> immediately before </main>", measured=where,
                     scope=scope)]


def check_h27_page_structure(page, selector, scope):
    """PAGE-STRUCTURE.md: one page-wrapper shell; each content section has the three-div nest.
    Header/footer chrome (data-chrome, or living inside header/footer) is exempt from the nest."""
    findings = []
    shell = page.evaluate("""() => {
      const wrap = document.querySelector('.page-wrapper');
      const main = document.querySelector('main.main-wrapper');
      const header = wrap ? wrap.querySelector(':scope > header') : null;
      const footer = wrap ? wrap.querySelector(':scope > footer') : null;
      return {
        wrap: !!wrap,
        main: !!main,
        header: !!header,
        footer: !!footer,
        headerInsideMain: !!(main && main.querySelector(':scope > header')),
        footerInsideMain: !!(main && main.querySelector(':scope > footer')),
      };
    }""")
    if not shell["wrap"]:
        findings.append(finding("H27", "hard", "missing .page-wrapper root",
                                 expected="div.page-wrapper wrapping header + main + footer",
                                 measured="absent", scope=scope))
    if not shell["main"]:
        findings.append(finding("H27", "hard", "missing main.main-wrapper",
                                 expected="main.main-wrapper inside .page-wrapper",
                                 measured="absent", scope=scope))
    if not shell["header"]:
        findings.append(finding("H27", "hard", "missing header as a direct child of .page-wrapper",
                                 expected=".page-wrapper > header", measured="absent",
                                 scope=scope))
    if not shell["footer"]:
        findings.append(finding("H27", "hard", "missing footer as a direct child of .page-wrapper",
                                 expected=".page-wrapper > footer", measured="absent",
                                 scope=scope))
    if shell["headerInsideMain"] or shell["footerInsideMain"]:
        findings.append(finding("H27", "hard",
                                 "header/footer must sit beside main, not inside it",
                                 expected="header and footer as siblings of main.main-wrapper",
                                 measured="chrome found inside main", scope=scope))

    nest_sel = selector if selector else "[data-section]"
    bad = page.evaluate("""(sel) => {
      const els = [...document.querySelectorAll(sel)];
      return els.filter(el => {
        if (el.closest('header, footer')) return false;
        if (el.getAttribute('data-chrome')) return false;
        const pg = el.querySelector(':scope > .padding-global');
        const cl = pg && pg.querySelector(':scope > .container-large');
        const psl = cl && cl.querySelector(':scope > .padding-section-large');
        return !(pg && cl && psl);
      }).map(el => el.getAttribute('data-section') || el.id || '(unnamed)');
    }""", nest_sel)
    if bad:
        findings.append(finding("H27", "hard",
            "content section(s) missing padding-global > container-large > padding-section-large",
            expected="three-div nest as direct descendants (PAGE-STRUCTURE.md)",
            measured=bad, scope=scope))
    return findings


def check_h8_duplicate_head(html_text, scope):
    head_match = re.search(r"<head\b.*?</head>", html_text, re.DOTALL | re.IGNORECASE)
    head = head_match.group(0) if head_match else ""
    srcs = re.findall(r'<script[^>]*\bsrc="([^"]+)"', head)
    hrefs = re.findall(r'<link[^>]*\bhref="([^"]+)"', head)
    dupes = [s for s, n in Counter(srcs + hrefs).items() if n > 1]
    if not dupes:
        return []
    return [finding("H8", "hard", f"duplicate <head> dependency: {dupes}",
                     expected="each script/link src/href appears once", measured=dupes,
                     scope=scope)]


def check_text_max_width(page, selector, scope, spec):
    if not spec or "textsize" not in spec:
        return []
    findings = []
    for name, tb in spec["textsize"].items():
        sel = tb.get("selector")
        if not sel:
            continue
        w = page.evaluate(f"""
          () => {{ const el = document.querySelector({json.dumps(sel)});
                    if (!el) return null; return getComputedStyle(el).maxWidth; }}
        """)
        if w is None or w in ("none", ""):
            findings.append(finding("H16", "hard",
                f"text element '{name}' ({sel}) has no explicit max-width",
                expected="max-width set from the authored text-box width", measured=w or "none",
                scope=scope))
    return findings


def check_spec_diff(page, selector, scope, spec):
    """The numeric re-diff (ACCURACY-GATE.md §1b) — compares the built page against the spec
    section_spec.py measured BEFORE the CSS existed. Not tied to a single CSV/H id; it is the
    check the whole gate exists to run per section instead of post-delivery."""
    if not spec:
        return []
    findings = []

    if "bg" in spec:
        measured = _eval_in_scope(page, selector, "return getComputedStyle(root).backgroundColor;")
        expected_hex = spec["bg"]["section_bg"]
        if measured:
            m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", measured)
            if m:
                measured_hex = "#%02x%02x%02x" % tuple(int(x) for x in m.groups())
                if measured_hex.lower() != expected_hex.lower():
                    findings.append(finding("numeric_rediff_bg", "hard",
                        "built section background doesn't match the pre-build spec",
                        expected=expected_hex, measured=measured_hex, scope=scope))

    if "container" in spec and spec["container"].get("selector"):
        sel = spec["container"]["selector"]
        expected_w = spec["container"].get("content_width")
        if expected_w:
            measured_w = page.evaluate(f"""
              () => {{ const el = document.querySelector({json.dumps(sel)});
                        if (!el) return null;
                        const cs = getComputedStyle(el), r = el.getBoundingClientRect();
                        return r.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
                      }}
            """)
            if measured_w is not None and abs(measured_w - expected_w) > 2:
                findings.append(finding("numeric_rediff_container_width", "hard",
                    "built content width doesn't match the pre-build spec (border-box arithmetic)",
                    expected=expected_w, measured=round(measured_w, 1), scope=scope))

    return findings


# --------------------------------------------------------------------------- runners

SECTION_CHECKS = [
    check_image_alt, check_image_loaded, check_image_blank, check_image_aspect_ratio,
    check_image_resolution, check_icon_glyph_placeholder,
    check_leaf_centering, check_disclosure_aria, check_contrast, check_placeholder_text,
    check_text_truncation, check_layout_shift_attrs, check_touch_targets,
    check_keyboard_navigation, check_cta_mobile_width, check_lazy_load_sliders,
    check_h27_page_structure,
]

PAGE_ONLY_CHECKS = [
    check_nav_links, check_heading_structure, check_seo_meta, check_font_family_consistency,
    check_interactive_states, check_heading_font_weight, check_state_variant_consistency,
    check_cta_consistency, check_container_consistency,
]

TEXT_CHECKS_PAGE = [check_h2_no_clay_names, check_h4_no_base64, check_h5_interactivity,
                    check_h6_duplicate_sections, check_h7_sentinel, check_h8_duplicate_head]


def run_section(page, selector, spec):
    findings = check_overflow(page, selector, "section")
    for fn in SECTION_CHECKS:
        findings += fn(page, selector, "section")
    if spec:
        findings += check_text_max_width(page, selector, "section", spec)
        findings += check_spec_diff(page, selector, "section", spec)
    return findings


def run_page(page, html_text, width_exempt=None):
    findings = check_overflow(page, None, "page")
    for fn in SECTION_CHECKS:
        findings += fn(page, None, "page")
    for fn in PAGE_ONLY_CHECKS:
        if fn is check_container_consistency:
            findings += fn(page, None, "page", exempt=width_exempt)
        else:
            findings += fn(page, None, "page")
    for fn in TEXT_CHECKS_PAGE:
        findings += fn(html_text, "page")
    return findings


# --------------------------------------------------------------------------- main

def build_result(scope, url, selector, findings, owners):
    hard = [f for f in findings if f["severity"] == "hard"]
    soft = [f for f in findings if f["severity"] == "soft"]
    return {
        "scope": scope, "url": url, "selector": selector,
        "hard_failures": hard, "soft_findings": soft, "passed": len(hard) == 0,
        "vision_owned": sorted(k for k, v in owners.items() if v == "vision"),
        "pre_build_owned": sorted(k for k, v in owners.items() if v == "pre-build"),
    }


def print_human(result):
    scope, sel = result["scope"], result["selector"]
    print(f"# qa_gate {scope} — {result['url']}" + (f"  selector={sel}" if sel else ""))
    print()
    if result["hard_failures"]:
        print(f"## HARD FAILURES ({len(result['hard_failures'])}) — not done")
        for f in result["hard_failures"]:
            print(f"   [{f['id']}] {f['message']}")
            print(f"        expected={f['expected']!r}  measured={f['measured']!r}")
    else:
        print("## HARD FAILURES: none")
    print()
    if result["soft_findings"]:
        print(f"## SOFT FINDINGS ({len(result['soft_findings'])}) — logged, not blocking")
        for f in result["soft_findings"]:
            print(f"   [{f['id']}] {f['message']}")
    else:
        print("## SOFT FINDINGS: none")
    print()
    print(f"## vision_owned ({len(result['vision_owned'])} rules this script does NOT check —"
          " still requires a real look):")
    print("   " + ", ".join(result["vision_owned"]))
    print(f"## pre_build_owned ({len(result['pre_build_owned'])} rules checked before CSS is"
          " written, not here):")
    print("   " + ", ".join(result["pre_build_owned"]))
    print()
    print(f"RESULT: {'PASSED' if result['passed'] else 'NOT DONE'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("section", help="run every applicable check scoped to one section")
    p.add_argument("--url", required=True, help="http://localhost:PORT/... — never file://")
    p.add_argument("--selector", required=True, help="CSS selector for the section's root element")
    p.add_argument("--spec", help="spec JSON written by `section_spec.py spec`")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("page", help="run every page-scoped check across the whole document")
    p.add_argument("--url", required=True, help="http://localhost:PORT/... — never file://")
    p.add_argument("--manifest", help="(reserved) section manifest JSON — most page checks query"
                                       " [data-section] directly and don't need it")
    p.add_argument("--width-exempt", default="",
                   help="comma-separated data-section slugs that are a deliberate full-bleed "
                        "carousel/marquee exception to H22 (name them, per H22's own text, "
                        "rather than letting the check guess)")
    p.add_argument("--json", action="store_true")

    args = ap.parse_args()

    if args.url.startswith("file://"):
        sys.exit("error: never open a bare file:// URL for qa_gate — serve over http://localhost "
                  "(GOTCHAS.md's file:// asset-loading gotcha). Images will silently read as "
                  "loaded=false and every check downstream of that will be wrong.")

    owners = load_rule_owners()
    self_check(owners, SCRIPT_RULE_HANDLERS, SCRIPT_HRULE_HANDLERS)

    if sync_playwright is None:
        sys.exit("error: playwright not installed — pip3 install --user playwright && "
                  "python3 -m playwright install chromium")

    spec = None
    if args.cmd == "section" and args.spec:
        with open(args.spec) as f:
            spec = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(args.url)
        page.wait_for_load_state("networkidle")

        if args.cmd == "section":
            findings = run_section(page, args.selector, spec)
            result = build_result("section", args.url, args.selector, findings, owners)
        else:
            html_text = page.content()
            exempt = [s.strip() for s in args.width_exempt.split(",") if s.strip()]
            findings = run_page(page, html_text, width_exempt=exempt)
            result = build_result("page", args.url, None, findings, owners)

        browser.close()

    if args.json:
        print(json.dumps(result))
        print(f"{result['scope']} {args.url}: {len(result['hard_failures'])} hard failure(s), "
              f"{len(result['soft_findings'])} soft finding(s) — "
              f"{'PASSED' if result['passed'] else 'NOT DONE'}", file=sys.stderr)
    else:
        print_human(result)

    sys.exit(1 if not result["passed"] else 0)


if __name__ == "__main__":
    main()

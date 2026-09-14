#!/usr/bin/env python3
"""
derive_family_fingerprints.py

Derives structural fingerprints for Clay's web section components — NOT hand-written.
Reads the real TypeScript source in a local clay-design-system checkout and Clay's own
generated wiki-index.json, and emits a JSON table mapping each section family to:

  - itemFields:      the field names (+ optionality) of its repeating-item type, e.g.
                      FeatureItem -> ["heading","description","media?","topic?","icon?",
                      "bullets?","cta?","cta2?"]
  - hasRepeatingItems: whether the section takes an `items: X[]` prop at all (CTA/Contact
                      don't — they're single-instance sections, not repeating)
  - activeIndexProp: the prop name that drives a single-active-item pattern (tabs/accordion),
                      or null if the section has no such state (e.g. FaqSection has none in
                      props — active state is local/uncontrolled, see note below)
  - minItems:         best-effort, scraped from the component's Storybook docs description
                      ("Minimum N items...") — null if not documented
  - tags / variants / category / storyPath: passed through from Clay's own wiki-index.json,
                      unchanged (never invented — Clay's own generator already derived these)

Used by `structural_signature()` in the Clay Section Decision Tree (see
CLAY-SECTION-DECISION-TREE.md) to identify a Figma section's family when its layer names give
no signal at all. This script never edits anything in clay-design-system — read-only.

Usage:
    python3 derive_family_fingerprints.py [--clay-root /path/to/clay-design-system]

Outputs (next to this script's parent project dir):
    clay-family-fingerprints.json   machine-readable table
    clay-family-fingerprints.md     human-readable rollup, for review
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict


def find_matching_brace(text, open_idx):
    """Given the index of an opening '{', return the index of its matching '}'."""
    depth = 0
    i = open_idx
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unbalanced braces")


def extract_interface_body(source, interface_name):
    """Return the raw body (between { }) of `export interface <interface_name> { ... }`,
    or `export type <interface_name> = { ... }`. None if not found in this source."""
    pattern = re.compile(
        r"export\s+(?:interface\s+" + re.escape(interface_name) + r"\b[^{]*"
        r"|type\s+" + re.escape(interface_name) + r"\s*=\s*)\{"
    )
    m = pattern.search(source)
    if not m:
        return None
    open_idx = m.end() - 1  # position of the '{'
    close_idx = find_matching_brace(source, open_idx)
    return source[open_idx + 1 : close_idx]


def parse_top_level_fields(body):
    """Parse top-level `name?: Type` / `name: Type` field declarations from an interface
    body, ignoring nested braces (e.g. `cta?: { label: string; ... }` counts as ONE field
    named `cta?`, not three) and JSDoc comment lines."""
    fields = []
    depth = 0
    i = 0
    n = len(body)
    line_start = 0
    # Walk char by char, tracking brace depth; a field declaration starts a new "statement"
    # at depth 0 on a line matching `^\s*(\/\*\*.*?\*\/\s*)?(\w+)\??\s*:`
    # Simplify: strip block comments first, then split on top-level separators (; or newline)
    body_no_comments = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
    body_no_comments = re.sub(r"//.*", "", body_no_comments)

    buf = ""
    for ch in body_no_comments:
        if ch == "{":
            depth += 1
            buf += ch
        elif ch == "}":
            depth -= 1
            buf += ch
        elif ch in ";\n" and depth == 0:
            stmt = buf.strip()
            if stmt:
                fields.append(stmt)
            buf = ""
        else:
            buf += ch
    stmt = buf.strip()
    if stmt:
        fields.append(stmt)

    out = []
    for stmt in fields:
        m = re.match(r"^(\w+)(\?)?\s*:", stmt)
        if m:
            name, optional = m.group(1), m.group(2)
            out.append(name + ("?" if optional else ""))
    return out


def find_props_interface_name(source, section_name):
    candidates = [f"{section_name}Props"]
    for c in candidates:
        if re.search(r"\binterface\s+" + re.escape(c) + r"\b", source):
            return c
    # fallback: any interface ending in "Props" defined in this file
    m = re.search(r"export\s+interface\s+(\w*Props)\b", source)
    return m.group(1) if m else None


GENERIC_ARRAY_TYPES = {"string", "number", "boolean", "ReactNode"}


def find_array_props(props_body):
    """Return every top-level `name?: TypeName[]` prop in a Props interface body, as
    (propName, typeName) pairs — NOT just one literally named `items`. Real Clay sections use
    variant-specific names (CardsSection: cards/revealCards/valueCards/..., FooterSection:
    columns, Integrations: items, TestimonialsSection: cards/carouselCards/...). Skips arrays
    of primitives (string[], etc.) since those aren't repeating-item shapes worth fingerprinting."""
    out = []
    for stmt in re.split(r"[;\n]", props_body):
        m = re.match(r"^\s*(\w+)\??\s*:\s*(\w+)\[\]", stmt)
        if m and m.group(2) not in GENERIC_ARRAY_TYPES:
            out.append((m.group(1), m.group(2)))
    return out


def find_active_index_prop(props_body):
    for stmt in re.split(r"[;\n]", props_body):
        m = re.match(r"^\s*(\w*[Aa]ctive\w*)\??\s*:", stmt)
        if m:
            return m.group(1)
    return None


def find_min_items(stories_source):
    if not stories_source:
        return None
    m = re.search(r"[Mm]inimum\s+(\d+)\s+items?", stories_source)
    return int(m.group(1)) if m else None


def derive(clay_root):
    wiki_path = clay_root / "packages/react/src/wiki/wiki-index.json"
    if not wiki_path.exists():
        print(f"ERROR: wiki-index.json not found at {wiki_path}", file=sys.stderr)
        sys.exit(1)
    wiki = json.loads(wiki_path.read_text())
    section_entries = [e for e in wiki["entries"] if e["kind"] == "section"]

    results = []
    seen_sources = set()
    for entry in section_entries:
        source_rel = entry.get("source")  # e.g. "packages/react/src/web/FeaturesSection"
        if not source_rel:
            results.append(dict(base_fingerprint(entry), warning="no source path in wiki"))
            continue
        if source_rel in seen_sources:
            continue  # duplicate wiki entry for the same source (e.g. TrustSection variants)
        seen_sources.add(source_rel)

        # Use the source directory's own basename for file lookups — entry["name"] can carry
        # a display suffix like 'TrustSection (layout="bento")' that isn't a real filename.
        section_name = Path(source_rel).name  # e.g. "FeaturesSection"
        section_dir = clay_root / source_rel
        tsx_path = section_dir / f"{section_name}.tsx"
        stories_path = section_dir / f"{section_name}.stories.tsx"

        if not tsx_path.exists():
            results.append(dict(base_fingerprint(entry), warning="%s not found" % tsx_path))
            continue

        source = tsx_path.read_text()
        props_name = find_props_interface_name(source, section_name)
        props_body = extract_interface_body(source, props_name) if props_name else None
        active_index_prop = find_active_index_prop(props_body) if props_body else None
        array_props = find_array_props(props_body) if props_body else []

        # One shape per array-typed prop — a single section can offer several
        # variant-specific repeating collections (CardsSection: cards/revealCards/...).
        item_shapes = []
        for prop_name, item_type in array_props:
            item_body = extract_interface_body(source, item_type)
            if item_body is None:
                item_shapes.append(
                    {"prop": prop_name, "itemTypeName": item_type, "itemFields": None,
                     "warning": f"type '{item_type}' not found in {tsx_path.name}"}
                )
                continue
            item_shapes.append(
                {"prop": prop_name, "itemTypeName": item_type,
                 "itemFields": parse_top_level_fields(item_body)}
            )

        stories_source = stories_path.read_text() if stories_path.exists() else None
        min_items = find_min_items(stories_source)

        fp = base_fingerprint(entry)
        fp.update(
            {
                "hasRepeatingItems": bool(item_shapes),
                "itemShapes": item_shapes,
                "activeIndexProp": active_index_prop,
                "minItems": min_items,
            }
        )
        results.append(fp)

    return {
        "generatedBy": "tools/derive_family_fingerprints.py (reads clay-design-system source; never edits it)",
        "clayRoot": str(clay_root),
        "note": (
            "itemFields/activeIndexProp/minItems are derived by parsing the real .tsx source "
            "each run — never hand-maintained. category/tags/variants/storyPath pass through "
            "unchanged from Clay's own generated wiki-index.json. Re-run this script whenever "
            "clay-design-system is updated; do not hand-edit the output."
        ),
        "sections": results,
    }


def base_fingerprint(entry):
    return {
        "family": entry["category"],
        "component": entry["name"],
        "tags": entry.get("tags", []),
        "variants": entry.get("variants", []),
        "storyPath": entry.get("storyPath"),
    }


def to_markdown(data):
    lines = [
        "# Clay Family Fingerprints (derived)",
        "",
        f"Generated from: `{data['clayRoot']}`",
        "",
        data["note"],
        "",
        "Used by `structural_signature()` in the Clay Section Decision Tree to guess a Figma "
        "section's family when no `/`-named layer exists anywhere in it.",
        "",
    ]
    for s in data["sections"]:
        lines.append(f"## {s['family']} — `{s['component']}`")
        lines.append("")
        if s.get("warning"):
            lines.append(f"> ⚠ {s['warning']}")
            lines.append("")
            continue
        if s["hasRepeatingItems"]:
            lines.append(f"- **Repeating item shapes:** {len(s['itemShapes'])}")
            for shape in s["itemShapes"]:
                if shape.get("warning"):
                    lines.append(f"  - `{shape['prop']}: {shape['itemTypeName']}[]` — ⚠ {shape['warning']}")
                else:
                    lines.append(f"  - `{shape['prop']}: {shape['itemTypeName']}[]` → `{', '.join(shape['itemFields'])}`")
        else:
            lines.append("- **Repeating items:** no (single-instance section)")
        lines.append(f"- **Active-index prop:** `{s['activeIndexProp']}`" if s["activeIndexProp"] else "- **Active-index prop:** none found in props (may be internal/uncontrolled state)")
        lines.append(f"- **Min items (documented):** {s['minItems']}" if s["minItems"] else "- **Min items (documented):** not found")
        lines.append(f"- **Storybook variants:** {', '.join(s['variants']) if s['variants'] else '—'}")
        lines.append(f"- **Tags:** {', '.join(s['tags'])}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--clay-root",
        required=True,
        help="Path to a local Clay design system checkout (never assume a fixed location — "
             "discover it per CLAY-INTEGRATION.md, or ask the user for it).",
    )
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parent.parent),
        help="Where to write clay-family-fingerprints.json/.md (default: project root)",
    )
    args = parser.parse_args()

    clay_root = Path(args.clay_root)
    if not clay_root.exists():
        print(f"ERROR: clay root not found: {clay_root}", file=sys.stderr)
        sys.exit(1)

    data = derive(clay_root)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "clay-family-fingerprints.json"
    md_path = out_dir / "clay-family-fingerprints.md"
    json_path.write_text(json.dumps(data, indent=2))
    md_path.write_text(to_markdown(data))

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Sections processed: {len(data['sections'])}")
    warnings = [s for s in data["sections"] if s.get("warning")]
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for w in warnings:
            print(f"  - {w['component']}: {w['warning']}")


if __name__ == "__main__":
    main()

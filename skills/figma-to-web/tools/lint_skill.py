#!/usr/bin/env python3
"""
lint_skill.py — checks this skill's own internal consistency. Exit 0 or exit 1.

Why this exists
----------------
Every check below exists because a real defect of that shape was found in the 2026-08-26
efficiency-uplift audit — none is speculative. The drift alone (six separate small factual errors
across SKILL.md/PREREQUISITES.md — "four subcommands" when there were five, "H1-H19" when the
live set already ran past H19, etc.) accumulated in a skill that no tool had ever checked. This
is what stops that coming back: run it on every commit (wire it as a git pre-commit hook), not
just once during the uplift.

Pure text/AST checks, stdlib only — no Playwright, no browser, no network. Runs in under a second.
A check that's slow or needs a served page is a check that gets skipped.

Usage
-----
  python3 lint_skill.py            # human summary
  python3 lint_skill.py --json     # machine-readable, same checks
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCE_DIR = SKILL_DIR / "reference"
TOOLS_DIR = SKILL_DIR / "tools"
SELF_PATH = Path(__file__).resolve()

# Files this linter checks. Explicitly enumerated (not an unbounded glob of the whole repo) so a
# stray file elsewhere on disk (e.g. the sibling "Figma to web tests/" workspace, gitignored and
# outside this skill) never gets pulled into a check by accident.
MD_FILES = sorted(REFERENCE_DIR.glob("*.md")) + [SKILL_DIR / "SKILL.md", SKILL_DIR / "README.md"]
PY_FILES = [p for p in sorted(TOOLS_DIR.glob("*.py")) if p != SELF_PATH]
CSV_PATH = REFERENCE_DIR / "web-design-rules.csv"
HARD_RULES_PATH = REFERENCE_DIR / "HARD-RULES.md"
SECTION_SPEC_PATH = TOOLS_DIR / "section_spec.py"
QA_GATE_PATH = TOOLS_DIR / "qa_gate.py"

VALID_OWNERS = {"pre-build", "script", "vision", "n-a"}


def _read(path):
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- L1

def check_L1_no_removed_tools():
    """No occurrence of canicode/memi/figwright anywhere in the skill (this linter excluded —
    it necessarily names them to check for their absence)."""
    failures = []
    pattern = re.compile(r"\b(canicode|memi|figwright)\b", re.IGNORECASE)
    for path in MD_FILES + PY_FILES:
        if not path.exists() or path == SELF_PATH:
            continue
        for lineno, line in enumerate(_read(path).splitlines(), 1):
            m = pattern.search(line)
            if m:
                failures.append(f"{path.relative_to(SKILL_DIR)}:{lineno}: found '{m.group(1)}' "
                                 "— removed tool, should not be referenced")
    return failures


# --------------------------------------------------------------------------- L2

def _defined_h_rules():
    if not HARD_RULES_PATH.exists():
        return set()
    text = _read(HARD_RULES_PATH)
    return set(re.findall(r"^## (H\d+)\b", text, re.MULTILINE))


def check_L2_h_rule_references_resolve():
    """Every H<n> referenced in any file resolves to a heading defined in HARD-RULES.md."""
    defined = _defined_h_rules()
    failures = []
    if not defined:
        return [f"HARD-RULES.md: no H-rule headings found at all — is the file empty or moved?"]
    for path in MD_FILES + PY_FILES:
        if not path.exists() or path == SELF_PATH:
            continue
        for lineno, line in enumerate(_read(path).splitlines(), 1):
            for m in re.finditer(r"\bH(\d+)\b", line):
                token = f"H{m.group(1)}"
                if token not in defined:
                    failures.append(f"{path.relative_to(SKILL_DIR)}:{lineno}: reference to "
                                     f"'{token}' has no matching heading in HARD-RULES.md")
    return failures


# --------------------------------------------------------------------------- L3

def check_L3_prose_counts_match_reality():
    """Concrete, real assertions — not a generic NLP count-extractor. Each one mirrors a drift
    item actually found in the audit."""
    failures = []
    defined = _defined_h_rules()
    if defined:
        real_max = max(int(h[1:]) for h in defined)
        for path in MD_FILES:
            if not path.exists():
                continue
            for lineno, line in enumerate(_read(path).splitlines(), 1):
                for m in re.finditer(r"H1[–-]H(\d+)\b", line):
                    claimed = int(m.group(1))
                    if claimed != real_max:
                        failures.append(
                            f"{path.relative_to(SKILL_DIR)}:{lineno}: claims 'H1-H{claimed}' but "
                            f"HARD-RULES.md's real max heading is H{real_max}")

    prereq_path = REFERENCE_DIR / "PREREQUISITES.md"
    if prereq_path.exists():
        text = _read(prereq_path)
        m = re.search(r"^## The (\w+) hard-required tools", text, re.MULTILINE)
        if m:
            words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                     "eight": 8}
            claimed = words.get(m.group(1).lower())
            table = re.search(r"\| Tool \|.*?\n((?:\|.*\n)+)", text)
            row_count = len(re.findall(r"^\| \*\*", table.group(1), re.MULTILINE)) if table else 0
            if claimed is not None and claimed != row_count:
                failures.append(
                    f"reference/PREREQUISITES.md: heading says '{m.group(1)} hard-required "
                    f"tools' ({claimed}) but the table below it has {row_count} rows")

    return failures


# --------------------------------------------------------------------------- L4

def _argparse_flags(path):
    if not path.exists():
        return set()
    return set(re.findall(r"add_argument\(\s*[\"'](--[\w-]+)", _read(path)))


def _argparse_subcommands(path):
    if not path.exists():
        return set()
    return set(re.findall(r"add_parser\(\s*[\"'](\w[\w-]*)", _read(path)))


def _fenced_code_blocks(text):
    """Yield (start_lineno, block_text) for each ```-fenced block — real invocations live here,
    not in prose/table cells that merely mention a script's name alongside an unrelated command
    (pip install --user, playwright install --with-deps)."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("```"):
            start = i
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            yield start + 1, "\n".join(body)
        i += 1


def check_L4_documented_flags_exist_in_code():
    """Every --flag documented inside a fenced code block that also mentions section_spec.py or
    qa_gate.py by name must exist in that script's real argparse. Scoped to code blocks (real
    invocations) rather than prose/table cells, so an unrelated command mentioned in the same
    sentence or table row (pip install --user, playwright install --with-deps) is never mistaken
    for one of this script's own flags. The failure mode this guards against is a documented flag
    that was never built (e.g. --family, documented before it existed), not a naming-convention
    nit."""
    real_flags = _argparse_flags(SECTION_SPEC_PATH) | _argparse_flags(QA_GATE_PATH)
    failures = []
    for path in MD_FILES:
        if not path.exists():
            continue
        for start, block in _fenced_code_blocks(_read(path)):
            if not re.search(r"\b(section_spec\.py|qa_gate\.py)\b", block):
                continue
            for fm in re.finditer(r"--[a-z][a-z-]+", block):
                flag = fm.group(0)
                if flag not in real_flags:
                    failures.append(f"{path.relative_to(SKILL_DIR)}:{start}: code block "
                                     f"documents flag '{flag}' but it isn't a real argparse "
                                     "argument in either script")
    return list(dict.fromkeys(failures))  # de-dupe, preserve order


def check_L4_documented_subcommands_exist_in_code():
    """SKILL.md's own reference-table row for section_spec.py names its subcommands in backticks
    — every one of those must be a real subparser, and every real subparser must be named there."""
    failures = []
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists() or not SECTION_SPEC_PATH.exists():
        return failures
    text = _read(skill_md)
    # Match the reference-TABLE row specifically ("| [`tools/section_spec.py`]...") — not just
    # any prose mention of the script's name elsewhere in the file (e.g. non-negotiable #3).
    m = re.search(r"^\|.*\[`tools/section_spec\.py`\].*$", text, re.MULTILINE)
    if not m:
        return [f"SKILL.md: no reference-table row found for tools/section_spec.py"]
    row = m.group(0)
    documented = set(re.findall(r"`(\w[\w-]*)`", row)) & _argparse_subcommands(SECTION_SPEC_PATH)
    real = _argparse_subcommands(SECTION_SPEC_PATH)
    missing_from_docs = real - documented
    if missing_from_docs:
        failures.append(f"SKILL.md: tools/section_spec.py row doesn't name subcommand(s) "
                         f"{sorted(missing_from_docs)}, which exist in the real code")
    return failures


# --------------------------------------------------------------------------- L5

def check_L5_reference_table_matches_disk():
    """Every file in reference/ appears in SKILL.md's reference table, and every row points at a
    file that exists."""
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        return [f"SKILL.md: not found"]
    text = _read(skill_md)
    linked = set(re.findall(r"\(reference/([\w.-]+)\)", text))
    on_disk = {p.name for p in REFERENCE_DIR.glob("*") if p.suffix in (".md", ".csv")}

    failures = []
    for missing in sorted(on_disk - linked):
        failures.append(f"SKILL.md: reference/{missing} exists on disk but isn't linked in the "
                         "reference-file table")
    for dangling in sorted(linked - on_disk):
        failures.append(f"SKILL.md: reference table links reference/{dangling}, which doesn't "
                         "exist on disk")
    return failures


# --------------------------------------------------------------------------- L6

def _csv_owners():
    if not CSV_PATH.exists():
        return {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return {row["id"]: (row.get("owner") or "").strip() for row in csv.DictReader(f)
                if row.get("id")}


def _h_rule_owners():
    if not HARD_RULES_PATH.exists():
        return {}
    text = _read(HARD_RULES_PATH)
    owners = {}
    for m in re.finditer(r"^## (H\d+)\b.*$", text, re.MULTILINE):
        hid = m.group(1)
        tail = text[m.end():]
        nxt = re.search(r"^## H\d+\b", tail, re.MULTILINE)
        block = tail[:nxt.start()] if nxt else tail
        om = re.search(r"\*\*Owner:\*\*\s*(\S+)", block)
        owners[hid] = om.group(1).strip() if om else ""
    return owners


def _qa_gate_handler_keys(dict_name):
    if not QA_GATE_PATH.exists():
        return set()
    text = _read(QA_GATE_PATH)
    m = re.search(rf"{dict_name}\s*=\s*\{{(.*?)\n\}}", text, re.DOTALL)
    if not m:
        return set()
    return set(re.findall(r'["\'](\S+?)["\']\s*:', m.group(1)))


def check_L6_every_rule_has_one_valid_owner():
    """Every CSV rule and every H-rule has exactly one valid owner tag, and every owner:script
    rule resolves to a registered qa_gate.py handler — the reverse of qa_gate.py's own runtime
    self-check, done here statically so it doesn't need Playwright installed to run."""
    failures = []
    csv_owners = _csv_owners()
    h_owners = _h_rule_owners()
    script_rule_handlers = _qa_gate_handler_keys("SCRIPT_RULE_HANDLERS")
    script_hrule_handlers = _qa_gate_handler_keys("SCRIPT_HRULE_HANDLERS")

    if not csv_owners:
        failures.append("reference/web-design-rules.csv: no rows found, or no 'owner' column")
    for rid, owner in csv_owners.items():
        if not owner:
            failures.append(f"reference/web-design-rules.csv: rule '{rid}' has no owner")
        elif owner not in VALID_OWNERS:
            failures.append(f"reference/web-design-rules.csv: rule '{rid}' has invalid owner "
                             f"'{owner}' (want one of {sorted(VALID_OWNERS)})")
        elif owner == "script" and rid not in script_rule_handlers:
            failures.append(f"reference/web-design-rules.csv: rule '{rid}' is owner:script but "
                             "has no matching key in qa_gate.py's SCRIPT_RULE_HANDLERS")

    if not h_owners:
        failures.append("reference/HARD-RULES.md: no H-rule headings found")
    for hid, owner in h_owners.items():
        if not owner:
            failures.append(f"reference/HARD-RULES.md: {hid} has no **Owner:** line")
        elif owner not in VALID_OWNERS:
            failures.append(f"reference/HARD-RULES.md: {hid} has invalid owner '{owner}' "
                             f"(want one of {sorted(VALID_OWNERS)})")
        elif owner == "script" and hid not in script_hrule_handlers:
            failures.append(f"reference/HARD-RULES.md: {hid} is owner:script but has no matching "
                             "key in qa_gate.py's SCRIPT_HRULE_HANDLERS")
    return failures


# --------------------------------------------------------------------------- L7

def check_L7_no_file_urls_or_absolute_paths():
    """No file:// URL used as an actual value, anywhere. Prose/comments that merely MENTION the
    bare word `file://` to warn against it (this skill's docs do that deliberately, at the point
    of relevance, not only in GOTCHAS.md) are not a violation — only `file://` followed by more
    URL-shaped characters (an actual path, a variable interpolation) is: that's the signature of
    real usage as opposed to a warning about it."""
    failures = []
    real_usage = re.compile(r"file://[^\s`]")
    for path in MD_FILES:
        if not path.exists():
            continue
        for lineno, line in enumerate(_read(path).splitlines(), 1):
            if real_usage.search(line):
                failures.append(f"{path.relative_to(SKILL_DIR)}:{lineno}: uses a file:// URL as "
                                 "a value — serve over http://localhost instead (GOTCHAS.md)")
    for path in MD_FILES + PY_FILES:
        if not path.exists() or path == SELF_PATH:
            continue
        for lineno, line in enumerate(_read(path).splitlines(), 1):
            if re.search(r"/Users/[\w.-]+/|/home/[\w.-]+/", line):
                failures.append(f"{path.relative_to(SKILL_DIR)}:{lineno}: contains a "
                                 "machine-specific absolute path")
    return failures


# --------------------------------------------------------------------------- L8

def _strip_fenced_code_blocks(text):
    """Blank out fenced code blocks (keeping line count intact) so a code sample's own syntax —
    e.g. a Python regex literal that happens to contain ']('  — is never mistaken for a real
    markdown link."""
    lines = text.splitlines()
    out, in_fence = [], False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append("")
        else:
            out.append("" if in_fence else line)
    return "\n".join(out)


def check_L8_relative_links_resolve():
    """Every relative markdown link resolves to a real file."""
    failures = []
    for path in MD_FILES:
        if not path.exists():
            continue
        for lineno, line in enumerate(_strip_fenced_code_blocks(_read(path)).splitlines(), 1):
            for m in re.finditer(r"\]\(([^)]+)\)", line):
                target = m.group(1)
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    failures.append(f"{path.relative_to(SKILL_DIR)}:{lineno}: link to "
                                     f"'{target}' does not resolve to a real file")
    return failures


# --------------------------------------------------------------------------- main

CHECKS = [
    ("L1", "No removed-tool references (canicode/memi/figwright)", check_L1_no_removed_tools),
    ("L2", "Every H<n> reference resolves to a HARD-RULES.md heading",
     check_L2_h_rule_references_resolve),
    ("L3", "Prose counts match reality", check_L3_prose_counts_match_reality),
    ("L4a", "Documented flags exist in the real argparse", check_L4_documented_flags_exist_in_code),
    ("L4b", "Documented subcommands match the real argparse",
     check_L4_documented_subcommands_exist_in_code),
    ("L5", "reference/ files <-> SKILL.md's reference table", check_L5_reference_table_matches_disk),
    ("L6", "Every rule has exactly one valid owner, every script rule has a handler",
     check_L6_every_rule_has_one_valid_owner),
    ("L7", "No file:// URLs, no machine-specific absolute paths",
     check_L7_no_file_urls_or_absolute_paths),
    ("L8", "Every relative markdown link resolves", check_L8_relative_links_resolve),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = []
    for check_id, description, fn in CHECKS:
        failures = fn()
        results.append({"id": check_id, "description": description, "failures": failures,
                         "passed": len(failures) == 0})

    total_failures = sum(len(r["failures"]) for r in results)

    if args.json:
        print(json.dumps({"results": results, "passed": total_failures == 0}))
    else:
        for r in results:
            status = "PASS" if r["passed"] else f"FAIL ({len(r['failures'])})"
            print(f"[{status:9s}] {r['id']:4s} {r['description']}")
            for f in r["failures"]:
                print(f"             - {f}")
        print()
        print(f"RESULT: {'PASSED' if total_failures == 0 else f'{total_failures} failure(s)'}")

    sys.exit(1 if total_failures else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Extract CSS rule blocks that match a section's class-name keywords.

Usage:
    python extract_css.py <css_file> [<css_file> ...] --keywords hp-agents agents-context m_container

Prints every top-level rule block (including matching @media blocks) whose text
contains any of the given keywords. Dedupes while preserving order. Piped output
can be pasted straight into the standalone file's <style>.
"""
import argparse
import re


def extract_rules(css: str, keywords: list[str]) -> list[str]:
    results, i, n = [], 0, len(css)
    while i < n:
        brace = css.find("{", i)
        if brace == -1:
            break
        rule_start = css.rfind("}", i, brace)
        rule_start = i if rule_start == -1 else rule_start + 1
        # depth-match the closing brace (handles @media / nested)
        depth, j = 0, brace
        while j < n:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        block = css[rule_start : j + 1].strip()
        if any(k in block for k in keywords):
            results.append(block)
        i = j + 1
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("css_files", nargs="+")
    ap.add_argument("--keywords", nargs="+", required=True)
    args = ap.parse_args()

    combined = "\n".join(open(f, encoding="utf-8").read() for f in args.css_files)

    # Always keep :root variable declarations — rules reference them.
    root = re.findall(r":root\s*\{[^}]*\}", combined)

    rules = extract_rules(combined, args.keywords)
    seen, unique = set(), []
    for r in root + rules:
        if r not in seen:
            seen.add(r)
            unique.append(r)

    print(f"/* {len(unique)} rule blocks matched {args.keywords} */\n")
    for r in unique:
        print(r, "\n")


if __name__ == "__main__":
    main()

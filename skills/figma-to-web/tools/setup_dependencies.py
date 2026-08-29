#!/usr/bin/env python3
"""
setup_dependencies.py — install and verify the figma-to-web toolchain before first use.

Run this once after copying the skill, and again whenever a check starts failing.
The skill refuses to start any Figma extraction until every hard-required check here passes
(Figma MCP auth is verified separately by the agent — see PREREQUISITES.md).

Usage
-----
  python3 tools/setup_dependencies.py           # install missing packages + verify all checks
  python3 tools/setup_dependencies.py --check   # verify only, do not install
  python3 tools/setup_dependencies.py --json    # machine-readable report

Exit 0 when every automatable check passes and Clay is discoverable.
Exit 1 when anything hard-required is still missing after install attempts.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

SKILL_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = SKILL_DIR / ".f2w-setup.json"
MIN_NODE_MAJOR = 24

CLAY_MARKERS = (
    "packages/react/src/figma/connections.json",
    "packages/tokens/dist/tokens.css",
)
CLAY_SEARCH_ROOTS = (
    Path.home() / "Development",
    Path.home() / "development",
    Path.home() / "Projects",
    Path.home() / "projects",
    Path.home() / "code",
    Path.home() / "src",
)


@dataclass
class CheckResult:
    id: str
    status: Literal["pass", "fail", "warn"]
    message: str
    fix: str | None = None


def _run(cmd: list[str], *, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _python() -> str:
    return sys.executable or "python3"


def _major_version(raw: str) -> int | None:
    m = re.search(r"(\d+)", raw.strip())
    return int(m.group(1)) if m else None


def _check_python() -> CheckResult:
    major = sys.version_info.major
    minor = sys.version_info.minor
    if major < 3 or (major == 3 and minor < 9):
        return CheckResult(
            "python",
            "fail",
            f"Python {major}.{minor} is too old (need 3.9+).",
            "Install Python 3.9+ from python.org or your package manager, then re-run this script.",
        )
    return CheckResult("python", "pass", f"Python {major}.{minor} ({_python()})")


def _ensure_pillow(*, install: bool) -> CheckResult:
    try:
        import PIL  # noqa: F401

        return CheckResult("pillow", "pass", "Pillow import OK")
    except ImportError:
        if not install:
            return CheckResult(
                "pillow",
                "fail",
                "Pillow is not installed.",
                f"{_python()} -m pip install --user Pillow",
            )
        proc = _run([_python(), "-m", "pip", "install", "--user", "Pillow"])
        if proc.returncode != 0:
            return CheckResult(
                "pillow",
                "fail",
                "Pillow install failed.",
                f"{_python()} -m pip install --user Pillow\n{proc.stderr.strip()}",
            )
        try:
            import PIL  # noqa: F401

            return CheckResult("pillow", "pass", "Pillow installed and import OK")
        except ImportError:
            return CheckResult(
                "pillow",
                "fail",
                "Pillow install reported success but import still fails.",
                f"{_python()} -m pip install --user Pillow",
            )


def _ensure_playwright(*, install: bool) -> CheckResult:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401

        return CheckResult("playwright", "pass", "Playwright Python package OK")
    except ImportError:
        if not install:
            return CheckResult(
                "playwright",
                "fail",
                "Playwright Python package is not installed.",
                f"{_python()} -m pip install --user playwright",
            )
        proc = _run([_python(), "-m", "pip", "install", "--user", "playwright"])
        if proc.returncode != 0:
            return CheckResult(
                "playwright",
                "fail",
                "Playwright install failed.",
                f"{_python()} -m pip install --user playwright\n{proc.stderr.strip()}",
            )
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401

            return CheckResult("playwright", "pass", "Playwright installed and import OK")
        except ImportError:
            return CheckResult(
                "playwright",
                "fail",
                "Playwright install reported success but import still fails.",
                f"{_python()} -m pip install --user playwright",
            )


def _ensure_chromium(*, install: bool) -> CheckResult:
    dry = _run([_python(), "-m", "playwright", "install", "--dry-run", "chromium"])
    if dry.returncode == 0 and "chromium" in dry.stdout.lower():
        # Dry-run prints what would be downloaded when missing; when installed it still exits 0.
        pass
    if install:
        proc = _run([_python(), "-m", "playwright", "install", "chromium"])
        if proc.returncode != 0:
            return CheckResult(
                "chromium",
                "fail",
                "Chromium install via Playwright failed.",
                f"{_python()} -m playwright install chromium\n{proc.stderr.strip()}",
            )
    # Best-effort: launch sync_playwright and ask for chromium path.
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return CheckResult("chromium", "pass", "Chromium launches via Playwright")
    except Exception as exc:  # noqa: BLE001 — surface the real launch error to the user
        return CheckResult(
            "chromium",
            "fail",
            f"Chromium is not usable yet ({exc}).",
            f"{_python()} -m playwright install chromium",
        )


def _check_node() -> CheckResult:
    node = shutil.which("node")
    if not node:
        return CheckResult(
            "node",
            "fail",
            "Node.js is not on PATH.",
            f"Install Node {MIN_NODE_MAJOR}+ (nvm/fnm/volta or nodejs.org), then re-run this script.",
        )
    proc = _run([node, "--version"])
    major = _major_version(proc.stdout or proc.stderr)
    if major is None or major < MIN_NODE_MAJOR:
        return CheckResult(
            "node",
            "fail",
            f"Node {proc.stdout.strip()} is too old (need >={MIN_NODE_MAJOR}).",
            f"Switch to Node {MIN_NODE_MAJOR}+ with nvm/fnm/volta, then re-run this script.",
        )
    return CheckResult("node", "pass", f"Node {proc.stdout.strip()} ({node})")


def _check_pnpm() -> CheckResult:
    pnpm = shutil.which("pnpm")
    if not pnpm:
        return CheckResult(
            "pnpm",
            "fail",
            "pnpm is not on PATH (needed for Clay/Storybook workflows).",
            "npm install -g pnpm   # or: corepack enable && corepack prepare pnpm@latest --activate",
        )
    proc = _run([pnpm, "--version"])
    if proc.returncode != 0:
        return CheckResult(
            "pnpm",
            "fail",
            "pnpm is present but --version failed.",
            "Re-install pnpm: npm install -g pnpm",
        )
    return CheckResult("pnpm", "pass", f"pnpm {proc.stdout.strip()} ({pnpm})")


def _valid_clay_root(root: Path) -> bool:
    return all((root / rel).is_file() for rel in CLAY_MARKERS)


def _discover_clay() -> Path | None:
    env = os.environ.get("CLAY_DESIGN_SYSTEM_PATH") or os.environ.get("CLAY_REPO")
    if env:
        candidate = Path(env).expanduser().resolve()
        if _valid_clay_root(candidate):
            return candidate

    for search_root in CLAY_SEARCH_ROOTS:
        if not search_root.is_dir():
            continue
        direct = search_root / "clay-design-system"
        if _valid_clay_root(direct):
            return direct.resolve()
        try:
            for child in search_root.iterdir():
                if not child.is_dir():
                    continue
                if _valid_clay_root(child):
                    return child.resolve()
                nested = child / "clay-design-system"
                if _valid_clay_root(nested):
                    return nested.resolve()
        except OSError:
            continue
    return None


def _check_clay() -> CheckResult:
    root = _discover_clay()
    if root:
        return CheckResult("clay", "pass", f"Clay checkout found at {root}")
    return CheckResult(
        "clay",
        "fail",
        "No Clay design-system checkout found.",
        "\n".join(
            [
                "Clone the Clay repo, then set CLAY_DESIGN_SYSTEM_PATH or re-run:",
                "  git clone https://github.com/eliorsi-hash/clay-design-system ~/Development/clay-design-system",
                "  cd ~/Development/clay-design-system && pnpm install && pnpm build",
                "  export CLAY_DESIGN_SYSTEM_PATH=~/Development/clay-design-system",
                "Required files:",
                *[f"  - {m}" for m in CLAY_MARKERS],
            ]
        ),
    )


def _check_figma_mcp() -> CheckResult:
    return CheckResult(
        "figma_mcp",
        "warn",
        "Figma MCP cannot be verified from this script — the agent checks it at session start.",
        "\n".join(
            [
                "Before your first build:",
                "  1. Enable the official Figma MCP in your editor (Cursor / Claude Code).",
                "  2. Sign in with a Figma account that can open the target files.",
                "  3. Ask the agent to run preflight — it will call get_metadata to confirm auth.",
            ]
        ),
    )


def run_setup(*, install: bool) -> list[CheckResult]:
    results: list[CheckResult] = []
    results.append(_check_python())
    results.append(_check_node())
    results.append(_check_pnpm())
    results.append(_ensure_pillow(install=install))
    results.append(_ensure_playwright(install=install))
    results.append(_ensure_chromium(install=install))
    results.append(_check_clay())
    results.append(_check_figma_mcp())
    return results


def _write_state(results: list[CheckResult]) -> None:
    hard_fail = any(r.status == "fail" for r in results if r.id != "figma_mcp")
    payload = {
        "ok": not hard_fail,
        "skill_dir": str(SKILL_DIR),
        "checks": [asdict(r) for r in results],
    }
    STATE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _print_human(results: list[CheckResult]) -> None:
    print("figma-to-web dependency setup\n")
    for r in results:
        label = {"pass": "PASS", "fail": "FAIL", "warn": "WARN"}[r.status]
        print(f"[{label}] {r.id}: {r.message}")
        if r.status != "pass" and r.fix:
            print(f"       fix: {r.fix}\n")
    hard_fail = [r for r in results if r.status == "fail"]
    if hard_fail:
        print("\nSetup incomplete — fix the FAIL items above, then re-run:")
        print(f"  {_python()} {Path(__file__).relative_to(SKILL_DIR)}")
        print("\nDo not start a figma-to-web build until every FAIL is resolved.")
    else:
        print("\nAutomated setup complete.")
        print("Connect Figma MCP in your editor, then start your first build.")
        print(f"State written to {STATE_PATH.relative_to(SKILL_DIR)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify only — do not pip/playwright install missing packages.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout.")
    args = parser.parse_args()

    results = run_setup(install=not args.check)
    _write_state(results)

    hard_fail = any(r.status == "fail" for r in results)
    if args.json:
        print(json.dumps({"ok": not hard_fail, "checks": [asdict(r) for r in results]}, indent=2))
    else:
        _print_human(results)
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())

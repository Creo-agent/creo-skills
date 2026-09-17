#!/usr/bin/env python3
"""
Timing & Tracing module for localization workers.
Tracks elapsed time per block, logs all operations, and stores run data for retro analysis.
"""

import json
import time
import os
import traceback
from datetime import datetime, timezone, timedelta

RUNS_DIR = os.path.join(os.path.dirname(__file__), "runs")
RETRO_FILE = os.path.join(os.path.dirname(__file__), "retro-learnings.json")

os.makedirs(RUNS_DIR, exist_ok=True)


class RunTimer:
    """Tracks timing for each block of a localization run."""

    def __init__(self, subitem_id: str, locale: str, parent_name: str, trigger: str = "new_run"):
        self.subitem_id = subitem_id
        self.locale = locale
        self.parent_name = parent_name
        self.trigger = trigger
        self.run_id = f"{subitem_id}_{locale}_{int(time.time())}"
        self.start_time = time.time()
        self.blocks = []
        self.current_block = None
        self.logs = []
        self.errors = []
        self.metadata = {}

    def start_block(self, name: str, details: str = ""):
        """Start timing a named block."""
        if self.current_block:
            self._end_current_block()
        self.current_block = {
            "name": name,
            "start": time.time(),
            "details": details,
            "logs": [],
        }
        self.log(f"▶ START: {name}" + (f" — {details}" if details else ""))

    def end_block(self, result: str = "ok", notes: str = ""):
        """End the current block with a result."""
        if not self.current_block:
            return
        self.current_block["result"] = result
        self.current_block["notes"] = notes
        self._end_current_block()

    def _end_current_block(self):
        block = self.current_block
        block["end"] = time.time()
        block["elapsed_s"] = round(block["end"] - block["start"], 2)
        self.log(f"◼ END: {block['name']} — {block['elapsed_s']}s ({block.get('result', 'ok')})")
        self.blocks.append(block)
        self.current_block = None

    def log(self, message: str, level: str = "info"):
        """Add a log entry."""
        entry = {
            "ts": datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M:%S"),
            "elapsed": round(time.time() - self.start_time, 2),
            "level": level,
            "msg": message,
        }
        self.logs.append(entry)
        if self.current_block:
            self.current_block["logs"].append(entry)

    def log_error(self, message: str, exc: Exception = None):
        """Log an error with optional traceback."""
        self.log(f"❌ ERROR: {message}", level="error")
        error_entry = {"message": message, "elapsed": round(time.time() - self.start_time, 2)}
        if exc:
            error_entry["traceback"] = traceback.format_exc()
        self.errors.append(error_entry)

    def set_metadata(self, key: str, value):
        """Set metadata for the run (e.g., text_node_count, glossary_size)."""
        self.metadata[key] = value

    def finish(self, terminal_status: str, confidence: float = 0.0):
        """Finalize the run and save to disk."""
        if self.current_block:
            self._end_current_block()

        total_elapsed = round(time.time() - self.start_time, 2)

        run_data = {
            "run_id": self.run_id,
            "subitem_id": self.subitem_id,
            "locale": self.locale,
            "parent_name": self.parent_name,
            "trigger": self.trigger,
            "terminal_status": terminal_status,
            "confidence": confidence,
            "total_elapsed_s": total_elapsed,
            "started_at": datetime.fromtimestamp(self.start_time, timezone(timedelta(hours=3))).isoformat(),
            "finished_at": datetime.now(timezone(timedelta(hours=3))).isoformat(),
            "blocks": [{
                "name": b["name"],
                "elapsed_s": b["elapsed_s"],
                "result": b.get("result", "ok"),
                "notes": b.get("notes", ""),
                "details": b.get("details", ""),
            } for b in self.blocks],
            "block_summary": {b["name"]: b["elapsed_s"] for b in self.blocks},
            "errors": self.errors,
            "metadata": self.metadata,
            "log_count": len(self.logs),
        }

        # Save run file
        run_file = os.path.join(RUNS_DIR, f"{self.run_id}.json")
        with open(run_file, "w") as f:
            json.dump(run_data, f, indent=2)

        # Save full log
        log_file = os.path.join(RUNS_DIR, f"{self.run_id}.log")
        with open(log_file, "w") as f:
            for entry in self.logs:
                f.write(f"[{entry['ts']}] [{entry['elapsed']:>7.2f}s] [{entry['level'].upper():>5}] {entry['msg']}\n")

        return run_data

    def summary(self) -> str:
        """Return a human-readable timing summary."""
        total = round(time.time() - self.start_time, 2)
        lines = [f"⏱️ TIMING REPORT — {self.parent_name} / {self.locale}"]
        lines.append(f"{'Block':<35} {'Time':>8} {'%':>6}")
        lines.append("-" * 52)
        for b in self.blocks:
            pct = round(b["elapsed_s"] / total * 100, 1) if total > 0 else 0
            lines.append(f"{b['name']:<35} {b['elapsed_s']:>7.1f}s {pct:>5.1f}%")
        lines.append("-" * 52)
        lines.append(f"{'TOTAL':<35} {total:>7.1f}s {'100.0':>5}%")
        if self.errors:
            lines.append(f"\n⚠️ {len(self.errors)} error(s) during run")
        return "\n".join(lines)


def load_retro_learnings():
    """Load accumulated retro learnings."""
    try:
        with open(RETRO_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"learnings": [], "improvements_applied": [], "run_count": 0}


def save_retro_learnings(data):
    with open(RETRO_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_recent_runs(n: int = 10) -> list:
    """Load the N most recent run data files."""
    runs = []
    if not os.path.exists(RUNS_DIR):
        return runs
    files = sorted(
        [f for f in os.listdir(RUNS_DIR) if f.endswith(".json")],
        reverse=True
    )
    for fname in files[:n]:
        with open(os.path.join(RUNS_DIR, fname)) as f:
            runs.append(json.load(f))
    return runs


def retro_analysis_prompt(runs: list) -> str:
    """Generate a retro analysis prompt from recent runs."""
    if not runs:
        return "No runs to analyze."

    lines = ["Analyze these localization run timings and suggest improvements:\n"]
    for run in runs:
        lines.append(f"## {run['parent_name']} / {run['locale']} — {run['terminal_status']} ({run['total_elapsed_s']}s total)")
        for block_name, elapsed in run.get("block_summary", {}).items():
            lines.append(f"  - {block_name}: {elapsed}s")
        if run.get("errors"):
            lines.append(f"  - ERRORS: {len(run['errors'])}")
            for err in run["errors"][:3]:
                lines.append(f"    → {err['message']}")
        lines.append("")

    avg_total = sum(r["total_elapsed_s"] for r in runs) / len(runs)
    lines.append(f"Average total time: {avg_total:.1f}s across {len(runs)} runs")

    # Find slowest blocks
    block_times = {}
    for run in runs:
        for name, elapsed in run.get("block_summary", {}).items():
            block_times.setdefault(name, []).append(elapsed)

    lines.append("\nAverage time per block:")
    for name, times in sorted(block_times.items(), key=lambda x: -sum(x[1])/len(x[1])):
        avg = sum(times) / len(times)
        lines.append(f"  {name}: {avg:.1f}s avg (min={min(times):.1f}s, max={max(times):.1f}s)")

    return "\n".join(lines)


if __name__ == "__main__":
    # Quick test
    t = RunTimer("test_123", "de-DE", "Test Asset")
    t.start_block("glossary_load", "Loading de-DE glossary")
    time.sleep(0.1)
    t.end_block("ok", "721 terms loaded")
    t.start_block("translation", "5 text nodes")
    time.sleep(0.2)
    t.end_block("ok")
    t.set_metadata("text_node_count", 5)
    result = t.finish("success", 0.95)
    print(t.summary())
    print(f"\nRun saved to: runs/{t.run_id}.json")

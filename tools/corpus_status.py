#!/usr/bin/env python3
"""Short census for the 1-hour status snapshot."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "data/questions"
HELD = ROOT / "data/held_questions_summary.json"


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except subprocess.CalledProcessError:
        return ""


def census() -> dict:
    by = Counter()
    n = 0
    n_parts = 0
    n_tikz = 0
    for path in sorted(QDIR.glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for it in rows:
            n += 1
            by[(it.get("subject"), it.get("item_type"))] += 1
            if it.get("parts"):
                n_parts += 1
            if it.get("tikz"):
                n_tikz += 1
    held = {}
    if HELD.is_file():
        held = json.loads(HELD.read_text(encoding="utf-8"))
    remote = ""
    try:
        remote = subprocess.check_output(
            ["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True
        ).split()[0]
    except Exception as e:
        remote = f"unavailable:{e}"
    return {
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_packed": n,
        "n_with_parts": n_parts,
        "n_tikz": n_tikz,
        "by_subject_type": {f"{s}:{t}": c for (s, t), c in sorted(by.items())},
        "held": held,
        "git_head": git_sha(),
        "origin_main": remote,
    }


def main() -> int:
    doc = census()
    text = json.dumps(doc, indent=2)
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(str(out))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

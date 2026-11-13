#!/usr/bin/env python3
"""Optional: list kickoff-style project candidates under folders YOU name (read-only, never run automatically).

Usage: python export_registry.py ROOT [ROOT ...] [--depth 3] [--out projects.json]
Looks only inside the given roots (no symlinks/junctions, noisy folders skipped). A folder is a candidate
if it has PROJECT_STATUS.md or .git. Prints/writes JSON candidates for a tool such as
a project viewer to review; nothing is registered, moved or modified. Writes a file only with --out.
"""
import json
import os
import sys
from pathlib import Path

SKIP = {".git", "node_modules", "target", "dist", "build", "Library", "Temp", "Logs", "obj", "bin",
        "__pycache__", ".venv", "venv", "vendor", "_inbox", "Packages"}
a = sys.argv[1:]


def opt(name, default=None):
    return a[a.index(name) + 1] if name in a else default


depth = int(opt("--depth", 3))
out = opt("--out")
roots = [Path(x) for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--depth", "--out"))]
if not roots:
    sys.exit(__doc__)


def candidate(d):
    why = [m for m, ok in (("PROJECT_STATUS.md", (d / "PROJECT_STATUS.md").is_file()),
                           (".git", (d / ".git").exists())) if ok]
    if not why:
        return None
    try:
        tier = json.loads((d / ".kickoff" / "fields.json").read_text(encoding="utf-8")).get("tier", "none")
    except Exception:
        tier = "none"
    return {"path": str(d.resolve()), "name": d.name, "found_by": why, "fields_tier": tier}


found = []
for root in roots:
    if not root.is_dir():
        print(f"skip (not a folder): {root}", file=sys.stderr)
        continue
    base = len(root.resolve().parts)
    for cur, dirs, _ in os.walk(root, followlinks=False):
        c = Path(cur)
        if len(c.resolve().parts) - base >= depth:
            dirs[:] = []
        dirs[:] = [d for d in dirs if d not in SKIP and not (c / d).is_symlink()]
        hit = candidate(c)
        if hit:
            found.append(hit)

text = json.dumps({"contract": 1, "candidates": found}, indent=2)
if out:
    Path(out).write_text(text + "\n", encoding="utf-8")
    print(f"{len(found)} candidate(s) written to {out}")
else:
    print(text)

#!/usr/bin/env python3
"""Undo what /kickoff created (stdlib only). Dry run unless --apply. Never uses recursive delete.

Usage: python undo.py [project_root] --snapshot   before bootstrap: save the list of existing files (.kickoff/before.json)
       python undo.py [project_root] --record     after bootstrap: save new files and their hashes (.kickoff/manifest.json)
       python undo.py [project_root] [--apply]    remove recorded files that are still unchanged; keep edited ones
Files that existed before and were only changed (CLAUDE.md, .gitignore, settings) are reported, not reverted: use git for those.
Empty folders left behind are removed one by one with rmdir; the .kickoff folder is removed last, only if it is empty."""
import hashlib
import json
import os
import sys
from datetime import date
from pathlib import Path

a = sys.argv[1:]
pos = [x for x in a if not x.startswith("--")]
root = Path(pos[0]).resolve() if pos else Path.cwd()
K = root / ".kickoff"
SKIP = {".git", "node_modules", "__pycache__", ".venv"}


def sha(p):
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def files():
    out = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            p = Path(dp) / f
            rel = p.relative_to(root).as_posix()
            if rel not in (".kickoff/before.json", ".kickoff/manifest.json"):
                out[rel] = sha(p)
    return out


def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


if "--snapshot" in a:
    K.mkdir(exist_ok=True)
    (K / "before.json").write_text(json.dumps(files(), indent=1) + "\n", encoding="utf-8")
    print(f"snapshot saved: {len(files())} existing file(s)")
elif "--record" in a:
    before = load(K / "before.json")
    if before is None:
        sys.exit("no .kickoff/before.json: run --snapshot before bootstrap (nothing recorded)")
    now = files()
    created = {p: h for p, h in now.items() if p not in before}
    changed = sorted(p for p, h in now.items() if p in before and before[p] != h)
    (K / "manifest.json").write_text(json.dumps({"date": date.today().isoformat(), "created": created, "changed": changed}, indent=1) + "\n", encoding="utf-8")
    print(f"recorded {len(created)} created file(s); {len(changed)} existing file(s) were changed (restore those with git)")
else:
    m = load(K / "manifest.json")
    if m is None:
        sys.exit("no .kickoff/manifest.json: nothing recorded to undo")
    apply = "--apply" in a
    removed, kept = [], []
    for rel, h in sorted(m["created"].items()):
        p = root / rel
        if not p.exists():
            continue
        if sha(p) == h:
            removed.append(rel)
            if apply:
                p.unlink()
        else:
            kept.append(rel)
    for rel in removed:
        print(("removed " if apply else "would remove ") + rel)
    for rel in kept:
        print(f"kept (edited since): {rel}")
    for rel in m.get("changed", []):
        print(f"not reverted (existed before, was changed): {rel}  -> git diff / git checkout")
    if apply:
        for d in sorted({str(Path(r).parent) for r in removed}, key=len, reverse=True):
            q = root / d
            while q != root and q.exists() and not any(q.iterdir()):
                q.rmdir()
                q = q.parent
        for f in ("before.json", "manifest.json"):
            if not kept and (K / f).exists():
                (K / f).unlink()
        if K.exists() and not any(K.iterdir()):
            K.rmdir()
    else:
        print(f"\ndry run: {len(removed)} file(s) would be removed, {len(kept)} kept. Re-run with --apply.")

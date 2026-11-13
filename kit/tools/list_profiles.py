#!/usr/bin/env python3
"""List the kit's profiles as families (stdlib only, read-only). Usage: python list_profiles.py [--kit DIR] [--json]

Main profiles first, each followed by the secondaries that extend it, then aliases. Shows the one-line summary,
the number of VS Code extensions and companion plugins a profile adds (including those inherited from its main)."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import profile_lib  # noqa: E402

KIT = Path(sys.argv[sys.argv.index("--kit") + 1]).resolve() if "--kit" in sys.argv else HERE.parent
rows = {}
for f in sorted(p for p in (KIT / "profiles").glob("*.md") if p.stem != "INDEX"):
    text = f.read_text(encoding="utf-8")
    m = re.search(r"^summary:\s*(.+)$", text, re.M)
    rows[f.stem] = {"name": f.stem, "extends": profile_lib.parent_of(f), "summary": (m.group(1).strip() if m else "UNKNOWN")}


def counts(name):
    paths = [p for _, p in profile_lib.lineage(name, Path("/nonexistent-root"), [KIT])]
    ext = profile_lib.bullets(profile_lib.subsection(profile_lib.section(paths, "VS Code"), "Extensions"))
    return len(ext), len(profile_lib.bullets(profile_lib.section(paths, "Companion plugins")))


out = []
for name, r in rows.items():
    r["extensions"], r["companions"] = counts(name)
    out.append(r)
mains = [r for r in out if not r["extends"]]
if "--json" in sys.argv:
    print(json.dumps({"profiles": out, "aliases": profile_lib.ALIASES}, indent=2))
    sys.exit(0)
for m in mains:
    print(f"{m['name']}: {m['summary']}  [VS Code {m['extensions']}, companions {m['companions']}]")
    for s in (r for r in out if r["extends"] == m["name"]):
        print(f"  - {s['name']} (extends {m['name']}): {s['summary']}  [VS Code {s['extensions']}, companions {s['companions']}]")
for old, new in profile_lib.ALIASES.items():
    print(f"alias: {old} -> {new}")
print("\nStart with: /kickoff:kickoff <profile>   (a secondary includes everything its main profile has)")

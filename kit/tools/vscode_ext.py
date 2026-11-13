#!/usr/bin/env python3
"""Build .vscode/extensions.json from a profile's VS Code section (stdlib only). Dry run unless --apply.

Usage: python vscode_ext.py [project_root] --profile NAME [--apply] [--include-unverified]
Reads '## VS Code' / '### Extensions' of the profile and, for a secondary, of the main profile it extends (profile_lib).
Merges into an existing file: existing recommendations are kept, only missing ids are added; nothing is overwritten.
Lines marked 'unverified' (an extension id that was not confirmed) are skipped unless --include-unverified.
Never installs anything: VS Code shows the recommendations and the user chooses. Settings are listed, never written."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import profile_lib  # noqa: E402

a = sys.argv[1:]
apply, unverified = "--apply" in a, "--include-unverified" in a
profile = a[a.index("--profile") + 1] if "--profile" in a else None
pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] != "--profile")]
root = Path(pos[0]).resolve() if pos else Path.cwd()
if not profile:
    sys.exit("give --profile NAME")

kits = [HERE.parent]
paths = [p for _, p in profile_lib.lineage(profile, root, kits)]
if not paths:
    sys.exit(f"profile '{profile}' not found")
text = profile_lib.section(paths, "VS Code")
exts, skipped, settings = [], [], []
for line in profile_lib.bullets(profile_lib.subsection(text, "Extensions")):
    ident = line.split(":")[0].strip()
    if "unverified" in line and not unverified:
        skipped.append(ident)
    elif ident not in exts:
        exts.append(ident)
for line in profile_lib.bullets(profile_lib.subsection(text, "Settings")):
    settings.append(line)

target = root / ".vscode" / "extensions.json"
current = {}
if target.exists():
    try:
        current = json.loads(target.read_text(encoding="utf-8"))
    except ValueError:
        sys.exit(f"{target} is not valid JSON (comments?); not touching it. Add these by hand: {', '.join(exts)}")
have = list(current.get("recommendations", []))
new = [e for e in exts if e not in have]
print(f"profile {profile}: {len(exts)} recommended extension(s), {len(new)} new for {target.relative_to(root)}")
for e in new:
    print(f"  + {e}")
for e in skipped:
    print(f"  (skipped, id not verified: {e})")
for s in settings:
    print(f"  setting to consider (not written): {s}")
if new and apply:
    current["recommendations"] = have + new
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    print("written")
elif new:
    print("dry run: re-run with --apply to write")

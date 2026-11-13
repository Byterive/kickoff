#!/usr/bin/env python3
"""Check the kit's profiles (stdlib only). Usage: python check_profiles.py [--kit DIR]   (exit 1 on any failure)

For every kit/profiles/<name>.md: frontmatter fields, the required sections (after resolving `extends`), a valid
`extends` target without cycles, a preset and gitignore for every main profile, a VS Code Extensions list with valid ids,
and alias targets that exist. The custom profile only needs frontmatter and Default phases."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import profile_lib  # noqa: E402

KIT = Path(sys.argv[sys.argv.index("--kit") + 1]).resolve() if "--kit" in sys.argv else HERE.parent
FIELDS = ("title", "summary", "keywords", "status", "updated")
REQUIRED = ("Folder skeleton", "Extra frontmatter", "PROJECT_STATUS.md tables", "Default phases", "Never do", "Wrap-up additions", "VS Code")
EXT_ID = re.compile(r"^[a-z0-9][a-z0-9-]*\.[a-z0-9][a-z0-9.-]*$", re.I)
fails = []


def check(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else f" :: {detail}"))
    if not ok:
        fails.append(label)


profiles = sorted(p.stem for p in (KIT / "profiles").glob("*.md") if p.stem != "INDEX")
for name in profiles:
    path = KIT / "profiles" / f"{name}.md"
    text = path.read_text(encoding="utf-8")
    fm = profile_lib.EXTENDS.match(text)
    body = fm.group(1) if fm else ""
    missing = [f for f in FIELDS if not re.search(rf"^{f}[ \t]*:[ \t]*\S", body, re.M)]
    check(f"{name}: frontmatter fields", not missing, "missing " + ", ".join(missing))
    parent = profile_lib.parent_of(path)
    chain, cur, seen = [], name, set()  # kit files only: a user-level or project profile of the same name must not hide a kit defect
    while cur and cur not in seen and (KIT / "profiles" / f"{cur}.md").exists():
        seen.add(cur)
        chain.insert(0, (cur, KIT / "profiles" / f"{cur}.md"))
        cur = profile_lib.parent_of(chain[0][1])
    if parent:
        check(f"{name}: extends {parent} resolves", len(chain) >= 2 and chain[0][0] == profile_lib.canonical(parent), f"lineage {[n for n, _ in chain]}")
    paths = [p for _, p in chain]
    if name == "custom":
        check("custom: Default phases", bool(profile_lib.section(paths, "Default phases")))
        continue
    for sec in REQUIRED:
        check(f"{name}: section {sec}", bool(profile_lib.section(paths, sec)))
    ext = profile_lib.section(paths, "VS Code")
    ids = [b.split(":")[0].strip() for b in profile_lib.bullets(profile_lib.subsection(ext, "Extensions"))]
    check(f"{name}: VS Code extension ids valid", all(EXT_ID.match(i) for i in ids), ", ".join(i for i in ids if not EXT_ID.match(i)))
    for line in profile_lib.bullets(profile_lib.section(paths, "Companion plugins")):
        check(f"{name}: companion line has a plugin name only", re.match(r"^[a-z0-9][a-z0-9-]*:", line) is not None and "@" not in line.split(" | ")[0], line)
    if not parent:
        check(f"{name}: preset exists", (KIT / "presets" / f"{name}.json").exists())
        check(f"{name}: gitignore exists", (KIT / "gitignore" / f"{name}.gitignore").exists())
    for kind, f in (("preset", KIT / "presets" / f"{name}.json"),):
        if f.exists():
            try:
                json.loads(f.read_text(encoding="utf-8"))
                ok = True
            except ValueError:
                ok = False
            check(f"{name}: {kind} is valid JSON", ok)

for old, new in profile_lib.ALIASES.items():
    check(f"alias {old} -> {new} exists", new in profiles and old not in profiles)

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)

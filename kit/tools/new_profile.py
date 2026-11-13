#!/usr/bin/env python3
"""Draft a reusable kickoff profile from a finished project (stdlib only). Prints the draft; writes only with --write.

Usage: python new_profile.py [project_root] --name NAME [--extends MAIN] [--write]
Reads: top-level folders, PROJECT_STATUS.md table headings, the 'Never do' and 'How to verify' parts of CLAUDE.md,
frontmatter keys used in the docs, and the Default phases of .kickoff/plan.json when present. Anything it cannot find is
written as UNKNOWN for you to fill in. --write saves ~/.claude/kickoff/profiles/<NAME>/profile.md (never overwrites).
Add the profile to the kit by hand (kit/profiles/, a preset, a gitignore, the docs) once you have reviewed it."""
import json
import re
import sys
from datetime import date
from pathlib import Path

a = sys.argv[1:]
name = a[a.index("--name") + 1] if "--name" in a else None
main = a[a.index("--extends") + 1] if "--extends" in a else None
pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--name", "--extends"))]
root = Path(pos[0]).resolve() if pos else Path.cwd()
if not name or not re.match(r"^[a-z0-9][a-z0-9-]*$", name):
    sys.exit("give --name NAME (lowercase letters, digits, hyphens)")
SKIP = {".git", ".kickoff", ".claude", "node_modules", "_audit", "__pycache__", ".vscode", "tools"}


def read(p):
    try:
        return (root / p).read_text(encoding="utf-8")
    except OSError:
        return ""


def block(text, pattern):
    m = re.search(rf"^#+[ \t]+{pattern}.*?\n(.*?)(?=^#+[ \t]|\Z)", text, re.S | re.M | re.I)
    return m.group(1).strip() if m else ""


folders = sorted(d.name + "/" for d in root.iterdir() if d.is_dir() and d.name not in SKIP and not d.name.startswith("."))
status, claude = read("PROJECT_STATUS.md"), read("CLAUDE.md")
tables = [h.strip() for h in re.findall(r"^##[ \t]+(.+)$", status, re.M) if h.strip().lower() not in ("where we are",)]
keys = sorted({k for f in root.glob("docs/**/*.md") for k in re.findall(r"^([a-z_]+):", (re.match(r"\A---\n(.*?)\n---", f.read_text(encoding="utf-8"), re.S) or [None, ""])[1], re.M)} - {"title", "summary", "keywords", "status", "updated"})
never = block(claude, "never do") or block(read(".kickoff/profile.md"), "never do")
verify = block(claude, "how to verify")
phases = []
try:
    phases = [p["name"] for p in json.loads(read(".kickoff/plan.json")).get("phases", [])]
except ValueError:
    pass

fm = f"---\ntitle: {name} profile\nsummary: UNKNOWN: one specific sentence about what this profile is for.\nkeywords: [{name}]\nstatus: draft\nupdated: {date.today().isoformat()}\n" + (f"extends: {main}\n" if main else "") + "---\n"
body = f"""
# Profile: {name}

## Folder skeleton
{' | '.join(folders) if folders else 'UNKNOWN'}

## Extra frontmatter
{', '.join(keys) if keys else 'UNKNOWN'}

## PROJECT_STATUS.md tables
{chr(10).join('- ' + t for t in tables) if tables else 'UNKNOWN'}

## Default phases
{chr(10).join('- ' + p for p in phases) if phases else '- UNKNOWN'}

## Never do
{never or '- UNKNOWN'}

## How to verify
{verify or 'UNKNOWN'}

## Wrap-up additions
UNKNOWN

## VS Code
### Extensions
- UNKNOWN.id: reason (unverified id)
"""
draft = fm + body
print(draft)
if "--write" in a:
    out = Path.home() / ".claude" / "kickoff" / "profiles" / name / "profile.md"
    if out.exists():
        sys.exit(f"{out} exists; not overwritten")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(draft, encoding="utf-8")
    print(f"written: {out}")

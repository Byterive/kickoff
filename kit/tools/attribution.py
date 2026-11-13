#!/usr/bin/env python3
"""Claude contribution line option (stdlib only).

Usage: python attribution.py <project_root> [--set yes|no] [--dry-run]
Without --set it prints the current choice. --set writes .kickoff/attribution.json and rewrites the "Git:" rule
in CLAUDE.md (never touches other lines). yes = commits end with the Co-Authored-By: Claude trailer and PR
descriptions with the Generated-with-Claude-Code line; no (default) = neither. No git hook is installed.
The kickoff co-author hook reads the same file (hooks/block_claude_coauthor.py).
"""
import json
import re
import sys
from pathlib import Path

NO = "- Git: never add `Co-Authored-By: Claude` or any Claude attribution to commits or PRs."
YES = ("- Git: end commit messages with the `Co-Authored-By: Claude` trailer and pull request descriptions with the "
       "`Generated with Claude Code` line, exactly as the session's attribution reminder gives them (chosen at setup).")
GIT_RULE = re.compile(r"^- Git: .*$", re.M)


def allowed(root):
    try:
        return json.loads((Path(root) / ".kickoff" / "attribution.json").read_text(encoding="utf-8")).get("claude_contribution") is True
    except (OSError, ValueError, AttributeError):
        return False


def apply(root, yes, dry=False):
    root, out = Path(root), []
    f = root / ".kickoff" / "attribution.json"
    out.append(f"{f.relative_to(root)}: claude_contribution = {str(yes).lower()}")
    cm = root / "CLAUDE.md"
    if cm.exists():
        raw = cm.read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in raw else "\n"
        text = raw.replace("\r\n", "\n")
        new, n = GIT_RULE.subn(lambda m: YES if yes else NO, text, count=1)
        if n:
            out.append("CLAUDE.md: Git rule " + ("allows" if yes else "forbids") + " the Claude contribution line")
        else:
            out.append("CLAUDE.md: no '- Git:' rule found, left unchanged (add the rule by hand)")
        if not dry and new != text:
            cm.write_bytes(new.replace("\n", nl).encode("utf-8"))
    else:
        out.append("CLAUDE.md: not found, only the setting file is written")
    if not dry:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"claude_contribution": yes}, indent=2) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    root = Path(a[0]) if a else Path.cwd()
    if "--set" in sys.argv:
        v = sys.argv[sys.argv.index("--set") + 1].lower()
        if v not in ("yes", "no"):
            sys.exit("--set takes yes or no")
        print("\n".join(apply(root, v == "yes", "--dry-run" in sys.argv)))
    else:
        print("Claude contribution line: " + ("allowed" if allowed(root) else "not allowed (default)"))

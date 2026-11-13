#!/usr/bin/env python3
"""PreToolUse(Bash) hook: block git commit / gh pr commands that add Claude attribution.

Reads the hook JSON on stdin. Exit 2 (with a message on stderr) blocks the call so Claude
retries without the trailer. Otherwise exit 0.
"""
import os as _os
import sys as _sys
if "coauthor" in _os.environ.get("KICKOFF_DISABLED_HOOKS", "").split(","):
    _sys.exit(0)
import json
import re
import sys

from pathlib import Path

try:
    data = json.load(sys.stdin)
    cmd = data.get("tool_input", {}).get("command", "")
except Exception:
    sys.exit(0)


def allowed_here():
    """True when the project chose the Claude contribution line (.kickoff/attribution.json, written by tools/attribution.py)."""
    start = Path(data.get("cwd") or ".").resolve()
    for d in [start, *start.parents]:
        f = d / ".kickoff" / "attribution.json"
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8")).get("claude_contribution") is True
            except (OSError, ValueError, AttributeError):
                return False
    return False


is_git = re.search(r"\bgit\s+commit\b|\bgh\s+pr\s+(create|edit)\b", cmd)
bad = re.search(r"co-authored-by:\s*claude|generated with \[?claude", cmd, re.I)
if is_git and bad and not allowed_here():
    sys.stderr.write("Blocked: do not add Claude as co-author or any Claude attribution. "
                     "Re-run without the Co-Authored-By / Generated-with line.\n")
    sys.exit(2)
sys.exit(0)

#!/usr/bin/env python3
"""Stop hook: regenerate INDEX.md files, only in kickoff projects.

The project root is the first folder, walking up from the current folder, that holds PROJECT_STATUS.md (the walk
stops at the repository top or the drive root). Uses the project's own tools/build_index.py, else the copy bundled with the plugin.
Never blocks Claude.
"""
import os as _os
import sys as _sys
if "reindex" in _os.environ.get("KICKOFF_DISABLED_HOOKS", "").split(","):
    _sys.exit(0)
import os
import subprocess
import sys


def find_root(start):
    cur = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(cur, "PROJECT_STATUS.md")):
            return cur
        if os.path.exists(os.path.join(cur, ".git")):
            return None  # reached the repository top without a status file: not a kickoff project
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


root = find_root(os.getcwd())
if root:
    local = os.path.join(root, "tools", "build_index.py")
    bundled = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit", "tools", "build_index.py")
    script = local if os.path.exists(local) else bundled
    try:
        subprocess.run([sys.executable, script, root], timeout=60, capture_output=True)
    except Exception:
        pass
sys.exit(0)

#!/usr/bin/env python3
"""Tests for the kickoff hooks (stdlib only). Usage: python test_hooks.py   (exit 1 on any failure).

block_rm_rf.py: real recursive forced deletes exit 2; text that only mentions them exits 0.
block_claude_coauthor.py: attribution in git commit / gh pr commands exits 2 (bash and PowerShell forms).
reindex_if_project.py: finds the project root from a subfolder.
hooks.json: the co-author and delete hooks are registered for both Bash and PowerShell.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent.parent / "hooks"
fails = []


def run_hook(name, command, env_extra=None, cwd=None):
    env = dict(os.environ, **(env_extra or {}))
    env.pop("KICKOFF_DISABLED_HOOKS", None) if not env_extra else None
    payload = json.dumps({"tool_input": {"command": command}, "cwd": str(cwd or os.getcwd())})
    return subprocess.run([sys.executable, str(HOOKS / name)], input=payload, capture_output=True, text=True,
                          env=env, cwd=cwd).returncode


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


BLOCK = [
    "rm -rf build",
    "rm -fr build",
    "rm -r -f build",
    "rm -Rf build",
    "rm --recursive --force build",
    "cd build && rm -rf out",
    "ls; rm -rf out",
    "echo done | xargs rm -rf",
    "find . -name '*.tmp' -exec rm -rf {} +",
    "sudo rm -rf /",
    "sudo -u root rm -rf /var/x",
    'bash -c "rm -rf build"',
    "sh -c 'cd x && rm -rf y'",
    "eval 'rm -rf build'",
    'echo "$(rm -rf build)"',
    "Remove-Item -Recurse -Force C:\\temp\\x",
    "Remove-Item C:\\temp\\x -Force -Recurse",
    "Remove-Item -Path x -Recurse -Force",
    "ri -r -fo x",
    "rm -Recurse -Force x",
    'powershell -Command "Remove-Item x -Recurse -Force"',
    "if true; then rm -rf out; fi",
    "A=1 rm -rf out",
    "rm -rf 'unbalanced",  # cannot be parsed: old behaviour still blocks
]
PASS = [
    'echo "rm -rf build"',
    "echo 'Remove-Item -Recurse -Force x'",
    'git commit -m "mention rm -rf in the docs"',
    "git commit -m 'Block Remove-Item -Recurse -Force in the hook'",
    "grep -rn 'rm -rf' .",
    'python -c "print(\'rm -rf x\')"',
    "cat <<'EOF' > note.txt\nrm -rf build\nRemove-Item -Recurse -Force x\nEOF",
    "cat <<EOF\nrm -rf build\nEOF\nls",
    "git commit -m @'\nExplain why rm -rf and Remove-Item -Recurse -Force are blocked\n'@",
    "git commit -m @\"\nrm -rf in text\n\"@",
    "rm file.txt",
    "rm -f file.txt",
    "rm -r emptydir",
    "Remove-Item x",
    "Remove-Item x -Force",
    "Remove-Item x -Recurse",
    "ls -rf",
    "npm run rm-rf-clean",
    "firmware-rf build",
]
for c in BLOCK:
    check("blocks: " + c.replace("\n", "\\n")[:60], run_hook("block_rm_rf.py", c) == 2)
for c in PASS:
    check("allows: " + c.replace("\n", "\\n")[:60], run_hook("block_rm_rf.py", c) == 0)
check("rm hook off with KICKOFF_DISABLED_HOOKS=rmrf", run_hook("block_rm_rf.py", "rm -rf build", {"KICKOFF_DISABLED_HOOKS": "rmrf"}) == 0)
check("rm hook ignores bad input", subprocess.run([sys.executable, str(HOOKS / "block_rm_rf.py")], input="not json",
                                                    capture_output=True, text=True).returncode == 0)

COAUTHOR_BAD = [
    'git commit -m "x" -m "Co-Authored-By: Claude <noreply@anthropic.com>"',
    "git commit -m @'\nFix\n\nCo-Authored-By: Claude Sonnet <noreply@anthropic.com>\n'@",
    'gh pr create --title t --body "Generated with [Claude Code](https://claude.com/claude-code)"',
]
COAUTHOR_OK = [
    'git commit -m "Fix the parser"',
    "git commit -m @'\nFix the parser\n'@",
    "echo Co-Authored-By: Claude",
    'git commit -m "Co-Authored-By: Jane <jane@example.com>"',
]
for c in COAUTHOR_BAD:
    check("coauthor blocks: " + c.replace("\n", "\\n")[:50], run_hook("block_claude_coauthor.py", c) == 2)
for c in COAUTHOR_OK:
    check("coauthor allows: " + c.replace("\n", "\\n")[:50], run_hook("block_claude_coauthor.py", c) == 0)

cfg = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
for matcher in ("Bash", "PowerShell"):
    cmds = " ".join(h["command"] for e in cfg if e["matcher"] == matcher for h in e["hooks"])
    check(f"hooks.json {matcher}: coauthor registered", "block_claude_coauthor.py" in cmds)
    check(f"hooks.json {matcher}: rm hook registered", "block_rm_rf.py" in cmds)

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    fm = "---\ntitle: T\nsummary: Test.\nkeywords: [t]\nstatus: draft\nupdated: 2026-11-02\n---\n"
    (root / "PROJECT_STATUS.md").write_text(fm + "# s\n", encoding="utf-8")
    (root / "sub" / "deeper").mkdir(parents=True)
    r = subprocess.run([sys.executable, str(HOOKS / "reindex_if_project.py")], cwd=root / "sub" / "deeper", capture_output=True, text=True)
    check("reindex hook finds the root from a subfolder", r.returncode == 0 and (root / "INDEX.md").exists())
    other = root / "plain"
    (other / ".git").mkdir(parents=True)
    r = subprocess.run([sys.executable, str(HOOKS / "reindex_if_project.py")], cwd=other, capture_output=True, text=True)
    check("reindex hook stops at a repository top without a status file", r.returncode == 0 and not (other / "INDEX.md").exists())

# Claude contribution line option: .kickoff/attribution.json (tools/attribution.py) lets the trailer through
sys.path.insert(0, str(HOOKS.parent / "kit" / "tools"))
import attribution  # noqa: E402

TRAILER = 'git commit -m "x" -m "Co-Authored-By: ' + 'Claude <noreply@anthropic.com>"'
with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    (root / "CLAUDE.md").write_text("# C\n" + attribution.NO + "\n- Other rule.\n", encoding="utf-8")
    (root / "sub").mkdir()
    check("attribution default: not allowed", not attribution.allowed(root))
    check("attribution default: hook blocks", run_hook("block_claude_coauthor.py", TRAILER, cwd=root / "sub") == 2)
    attribution.apply(root, True)
    cm = (root / "CLAUDE.md").read_text(encoding="utf-8")
    check("attribution yes: allowed", attribution.allowed(root))
    check("attribution yes: CLAUDE.md Git rule rewritten, other rules kept", "end commit messages with" in cm and "- Other rule." in cm)
    check("attribution yes: hook lets it through (also from a subfolder)", run_hook("block_claude_coauthor.py", TRAILER, cwd=root / "sub") == 0)
    attribution.apply(root, False)
    check("attribution no again: hook blocks", run_hook("block_claude_coauthor.py", TRAILER, cwd=root / "sub") == 2)
    check("attribution no again: original rule restored", attribution.NO in (root / "CLAUDE.md").read_text(encoding="utf-8"))
    (root / ".kickoff" / "attribution.json").write_text("{bad", encoding="utf-8")
    check("attribution unreadable file: stays blocked", run_hook("block_claude_coauthor.py", TRAILER, cwd=root) == 2)

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)

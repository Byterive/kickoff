#!/usr/bin/env python3
"""Tests for kickoff 1.4.2 (stdlib only): hub path stays out of guide.json (R42), audit uses relative paths (R43),
toggles go to settings.local.json (R44), doctor flags local paths and plugin names in tracked files (R45).
Usage: python test_privacy.py   (exit 1 on any failure)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

T = Path(__file__).resolve().parent
KIT = T.parent
PLUGIN = KIT.parent
fails = []
FM = "---\ntitle: T\nsummary: Test file.\nkeywords: [t]\nstatus: draft\nupdated: 2026-11-04\n---\n"
BS = chr(92)


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {str(detail)[:300]}"))
    if not ok:
        fails.append(name)


def run(args, cwd, home):
    env = dict(os.environ, USERPROFILE=str(home), HOME=str(home))
    env.pop("KICKOFF_DISABLED_HOOKS", None)
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True, env=env)


def git(repo, *a):
    e = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@example.com")
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, env=e).stdout.strip()


def project(d):
    r = Path(d)
    (r / "tools").mkdir()
    for f in ("build_index.py", "check_budgets.py", "budgets.json", "doctor.py", "proj_toggle.py", "profile_lib.py"):
        (r / "tools" / f).write_bytes((T / f).read_bytes())
    for n, c in (("PROJECT_STATUS.md", FM + "# s\n"), ("NEXT.md", FM + "# n\n"), ("CLAUDE.md", "# rules\n")):
        (r / n).write_text(c, encoding="utf-8")
    return r


with tempfile.TemporaryDirectory() as h:
    home = Path(h)
    (home / ".claude" / "kickoff").mkdir(parents=True)
    (home / ".claude" / "kickoff" / "config.json").write_text(json.dumps({"hub": "F:" + BS + "Secret_hub"}), encoding="utf-8")

    # ---- R42: hub path stays out of the project ----
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        res = run([T / "upgrade.py", r, "--guide", "local", "--apply"], r, home)
        gj = r / ".kickoff" / "guide.json"
        check("R42 guide.json is created", gj.exists(), res.stdout + res.stderr)
        txt = gj.read_text(encoding="utf-8") if gj.exists() else ""
        check("R42 guide.json has an empty hub", json.loads(txt or "{}").get("hub") == "", txt)
        check("R42 the user's hub path is not written into the project", "Secret_hub" not in txt)
        check("R42 template and bootstrap skill carry no hub path", '"hub": ""' in (KIT / "templates" / "guide.json.template").read_text(encoding="utf-8")
              and "hub from `~/.claude/kickoff/config.json`" not in (PLUGIN / "skills" / "project-bootstrap" / "SKILL.md").read_text(encoding="utf-8"))

    # ---- R43: audit rule ----
    a = (PLUGIN / "skills" / "project-audit" / "SKILL.md").read_text(encoding="utf-8")
    check("R43 audit skill requires relative paths", "relative to the project root" in a and "never absolute" in a)

    # ---- R44: toggles go to settings.local.json ----
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        (r / ".claude").mkdir()
        shared = r / ".claude" / "settings.json"
        shared.write_text(json.dumps({"enabledPlugins": {"some-plugin@byterive-kit": False},
                                      "permissions": {"deny": ["Read(./.env)", "Skill(oldskill)"]}}), encoding="utf-8")
        before = shared.read_text(encoding="utf-8")
        res = run([r / "tools" / "proj_toggle.py", "off", "zzskill"], r, home)
        loc = r / ".claude" / "settings.local.json"
        check("R44 toggle writes settings.local.json", loc.exists() and "Skill(zzskill)" in loc.read_text(encoding="utf-8"), res.stdout + res.stderr)
        check("R44 shared settings.json is not touched by a toggle", shared.read_text(encoding="utf-8") == before)
        res = run([r / "tools" / "proj_toggle.py", "list"], r, home)
        check("R44 list shows the shared toggle and skill rule", "some-plugin@byterive-kit" in res.stdout and "oldskill" in res.stdout, res.stdout)
        res = run([r / "tools" / "proj_toggle.py", "localize", "--dry-run"], r, home)
        check("R44 localize dry run changes nothing", shared.read_text(encoding="utf-8") == before and "dry run" in res.stdout, res.stdout + res.stderr)
        res = run([r / "tools" / "proj_toggle.py", "localize"], r, home)
        sh, lc = json.loads(shared.read_text(encoding="utf-8")), json.loads(loc.read_text(encoding="utf-8"))
        check("R44 localize moves plugin toggles and skill rules", "enabledPlugins" not in sh and lc["enabledPlugins"].get("some-plugin@byterive-kit") is False
              and "Skill(oldskill)" in lc["permissions"]["deny"] and "Skill(oldskill)" not in sh["permissions"]["deny"], (sh, lc))
        check("R44 localize keeps the shared secret-file deny rule", "Read(./.env)" in sh["permissions"]["deny"])
        res = run([r / "tools" / "proj_toggle.py", "localize"], r, home)
        check("R44 localize twice is harmless", "Nothing to move" in res.stdout, res.stdout)
        check("R44 gitignore template ignores settings.local.json", ".claude/settings.local.json" in (KIT / "gitignore" / "common.gitignore").read_text(encoding="utf-8"))

    # ---- R45: doctor flags local paths and plugin names in tracked files ----
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        git(r, "init", "-q")
        (r / "docs").mkdir()
        (r / "docs" / "notes.md").write_text(FM + "# n\nSee C:" + BS + "Users" + BS + "bob" + BS + ".claude and F:" + BS + "Claude_Apps" + BS + "proj.\n", encoding="utf-8")
        (r / "docs" / "ok.md").write_text(FM + "# n\nConfig in C:" + BS + "Users" + BS + "<you>" + BS + ".tool and ~/.tool.\n", encoding="utf-8")
        (r / "_audit").mkdir()
        (r / "_audit" / "INDEX.md").write_text(FM + "# a\nRoot F:" + BS + "Claude_Apps" + BS + "proj\n", encoding="utf-8")
        (r / ".guidebook").mkdir()
        (r / ".guidebook" / "facts.json").write_text(json.dumps({"p": "F:" + BS + "x"}), encoding="utf-8")
        (r / ".claude").mkdir()
        (r / ".claude" / "settings.json").write_text(json.dumps({"enabledPlugins": {"some-plugin@byterive-kit": False}}), encoding="utf-8")
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "init")
        out = run([r / "tools" / "doctor.py", r], r, home).stdout
        check("R45 doctor warns about tracked files with absolute paths", "tracked file(s) contain absolute local paths" in out, out)
        check("R45 doctor names the file and line", "docs/notes.md: line 9" in out, out)
        check("R45 doctor says a user account name is included", "include a user account name" in out, out)
        check("R45 placeholder paths like C:" + BS + "Users" + BS + "<you> are not flagged", "ok.md" not in out, out)
        check("R45 .guidebook is not scanned", ".guidebook/facts.json" not in out)
        check("R45 doctor flags absolute paths in _audit", "_audit/ has files with absolute paths" in out, out)
        check("R45 doctor flags plugin names in tracked settings.json", ".claude/settings.json is tracked and names 1 plugin" in out and "localize" in out, out)
        run([r / "tools" / "proj_toggle.py", "localize"], r, home)
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "localize")
        out = run([r / "tools" / "doctor.py", r], r, home).stdout
        check("R45 after localize the plugin-name warning is gone", "settings.json is tracked and names" not in out, out)
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        git(r, "init", "-q")
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "init")
        out = run([r / "tools" / "doctor.py", r], r, home).stdout
        check("R45 clean project: OK line", "no absolute local paths in tracked files" in out, out)

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)

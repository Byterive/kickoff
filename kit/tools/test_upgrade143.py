#!/usr/bin/env python3
"""Tests for kickoff 1.4.3 (stdlib only): profile reference stays inside the project (R48), co-author hint and plugin list (R49),
opt-in refresh of tool copies (R51). Usage: python test_upgrade143.py   (exit 1 on any failure)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

T = Path(__file__).resolve().parent
KIT = T.parent
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


def project(d, profile_ref):
    r = Path(d)
    (r / "tools").mkdir()
    for f in ("build_index.py", "check_budgets.py", "budgets.json", "doctor.py", "proj_toggle.py", "profile_lib.py"):
        (r / "tools" / f).write_bytes((T / f).read_bytes())
    (r / "PROJECT_STATUS.md").write_text(FM + "# s\n", encoding="utf-8")
    (r / "NEXT.md").write_text(FM + "# n\n", encoding="utf-8")
    (r / "DECISIONS.md").write_text(FM + "# Decisions\nNewest first.\n", encoding="utf-8")
    (r / "CLAUDE.md").write_text("# rules\nRules (full text: X:" + BS + "project" + BS + "plugins" + BS + "kickoff" + BS + "kit" + BS + "CLAUDE_INSTRUCTIONS.md, profile: "
                                 + profile_ref + "):\n", encoding="utf-8")
    return r


def old_profile_ref(name):
    return "X:" + BS + "project" + BS + "plugins" + BS + "kickoff" + BS + "kit" + BS + "profiles" + BS + name + ".md"


with tempfile.TemporaryDirectory() as h:
    home = Path(h)
    (home / ".claude").mkdir()

    # ---- R48: custom profile points at the project's own profile.md ----
    with tempfile.TemporaryDirectory() as d:
        r = project(d, old_profile_ref("custom"))
        (r / ".kickoff").mkdir()
        (r / ".kickoff" / "profile.md").write_text(FM + "# Custom profile\n", encoding="utf-8")
        before = run([r / "tools" / "doctor.py", r], r, home).stdout
        check("R48 doctor first warns about the outside profile path", "CLAUDE.md points outside the project" in before, before)
        res = run([T / "upgrade.py", r], r, home)
        check("R48 dry run lists the CLAUDE.md change and writes nothing", ".kickoff/profile.md" in res.stdout and "profiles" + BS + "custom.md" in (r / "CLAUDE.md").read_text(encoding="utf-8"), res.stdout + res.stderr)
        run([T / "upgrade.py", r, "--apply"], r, home)
        ct = (r / "CLAUDE.md").read_text(encoding="utf-8")
        check("R48 custom profile reference becomes .kickoff/profile.md", "profile: .kickoff/profile.md" in ct, ct)
        check("R48 no copy of the kit custom.md is made", not (r / ".kickoff" / "kit" / "profiles" / "custom.md").exists())
        check("R48 the kit instructions reference is inside the project too", "full text: .kickoff/kit/CLAUDE_INSTRUCTIONS.md" in ct, ct)
        check("R48 DECISIONS.md notes it", "kit references now point to .kickoff/kit/" in (r / "DECISIONS.md").read_text(encoding="utf-8"))
        again = run([T / "upgrade.py", r, "--apply"], r, home)
        check("R48 second run changes nothing in CLAUDE.md", (r / "CLAUDE.md").read_text(encoding="utf-8") == ct and "kit reference" not in again.stdout, again.stdout)
        after = run([r / "tools" / "doctor.py", r], r, home).stdout
        check("R48 doctor no longer warns about outside paths", "CLAUDE.md has no paths outside the project" in after, after)

    # ---- R48: built-in profile is copied into .kickoff/kit/profiles ----
    with tempfile.TemporaryDirectory() as d:
        r = project(d, old_profile_ref("unity"))
        run([T / "upgrade.py", r, "--apply"], r, home)
        ct = (r / "CLAUDE.md").read_text(encoding="utf-8")
        cp = r / ".kickoff" / "kit" / "profiles" / "unity.md"
        check("R48 built-in profile is copied to .kickoff/kit/profiles/unity.md", cp.exists() and cp.read_text(encoding="utf-8") == (KIT / "profiles" / "unity.md").read_text(encoding="utf-8"))
        check("R48 reference points at the copy", "profile: .kickoff/kit/profiles/unity.md" in ct, ct)
        st = json.loads((r / ".kickoff" / "kit" / ".sources.json").read_text(encoding="utf-8"))
        check("R48 the copy is hash-tracked like the other kit copies", "profiles/unity.md" in st.get("files", {}), st)

    # ---- R49: co-author hint and plugin list ----
    with tempfile.TemporaryDirectory() as d:
        r = project(d, old_profile_ref("custom"))
        out = run([r / "tools" / "doctor.py", r], r, home).stdout
        check("R49 not installed: doctor gives the install command", "kickoff is not installed (run: claude plugin install kickoff@byterive-kit)" in out, out)
        (home / ".claude" / "plugins").mkdir()
        (home / ".claude" / "plugins" / "installed_plugins.json").write_text(json.dumps({"plugins": {"kickoff@byterive-kit": [{"scope": "user", "installPath": str(r)}]}}), encoding="utf-8")
        out = run([r / "tools" / "doctor.py", r], r, home).stdout
        check("R49 installed but off here: doctor says how to switch it on", "kickoff is installed but switched off for this project (run: python tools/proj_toggle.py on kickoff)" in out, out)
        lst = run([r / "tools" / "proj_toggle.py", "list"], r, home).stdout
        check("R49 proj_toggle list shows kickoff once it is installed", "kickoff@byterive-kit" in lst, lst)
        (home / ".claude" / "settings.json").write_text(json.dumps({"enabledPlugins": {"kickoff@byterive-kit": True}}), encoding="utf-8")
        out = run([r / "tools" / "doctor.py", r], r, home).stdout
        check("R49 enabled: the co-author block is active", "co-author block active" in out, out)
        (home / ".claude" / "settings.json").unlink()
        (home / ".claude" / "plugins" / "installed_plugins.json").unlink()

    # ---- R51: refresh tool copies, opt-in ----
    with tempfile.TemporaryDirectory() as d:
        r = project(d, old_profile_ref("custom"))
        doctor = r / "tools" / "doctor.py"
        old = b"# old doctor copy\n" + doctor.read_bytes()
        doctor.write_bytes(old)
        budgets = (r / "tools" / "budgets.json")
        budgets.write_text('{"max_md_lines": 123}', encoding="utf-8")
        res = run([T / "upgrade.py", r, "--apply"], r, home)
        check("R51 without the flag nothing is refreshed, but the user is told", doctor.read_bytes() == old and "tool copy(ies) in tools/ differ" in res.stdout and "doctor.py" in res.stdout, res.stdout)
        res = run([T / "upgrade.py", r, "--refresh-tools"], r, home)
        check("R51 dry run lists the refresh and changes nothing", "refresh tools/doctor.py" in res.stdout and doctor.read_bytes() == old, res.stdout)
        run([T / "upgrade.py", r, "--refresh-tools", "--apply"], r, home)
        check("R51 apply replaces the copy with the kit version", doctor.read_bytes().replace(b"\r\n", b"\n") == (T / "doctor.py").read_bytes().replace(b"\r\n", b"\n"))
        bak = list((r / ".kickoff" / "backup").glob("*/doctor.py"))
        check("R51 the old copy is saved under .kickoff/backup/<date>/", len(bak) == 1 and bak[0].read_bytes() == old)
        check("R51 budgets.json is never touched", budgets.read_text(encoding="utf-8") == '{"max_md_lines": 123}')
        again = run([T / "upgrade.py", r, "--refresh-tools"], r, home)
        check("R51 second run has nothing to refresh", "refresh tools/" not in again.stdout and "tool copy(ies)" not in again.stdout, again.stdout)

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)

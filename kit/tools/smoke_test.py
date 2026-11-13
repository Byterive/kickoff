#!/usr/bin/env python3
"""Smoke test for the kit tools: scaffolds a throwaway project and runs index, budgets, doctor, presets.

Usage: python smoke_test.py   (exit 1 on any failure; touches only a temp folder and a temp HOME)
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

T = Path(__file__).resolve().parent
KIT = T.parent
fails = []


def run(args, cwd, env=None):
    e = dict(os.environ, **(env or {}))
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True, env=e)


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail[:200]}"))
    if not ok:
        fails.append(name)


with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as h:
    p = Path(d)
    (p / "tools").mkdir()
    for f in ("build_index.py", "check_budgets.py", "budgets.json", "doctor.py", "proj_toggle.py", "profile_lib.py"):
        (p / "tools" / f).write_bytes((T / f).read_bytes())
    fm = "---\ntitle: T\nsummary: Test file.\nkeywords: [t]\nstatus: draft\nupdated: 2026-10-22\n---\n"
    (p / "PROJECT_STATUS.md").write_text(fm + "# s\n", encoding="utf-8")
    (p / "NEXT.md").write_text(fm + "# n\n", encoding="utf-8")
    (p / "CLAUDE.md").write_text("# rules\n", encoding="utf-8")
    env = {"USERPROFILE": h, "HOME": h}
    r = run(["tools/doctor.py"], p, env)
    check("doctor runs", r.returncode == 0, r.stdout + r.stderr)
    r = run([str(T / "proj_toggle.py"), "preset", "unity", "--tier", "minimal", "--dry-run"], p, env)
    check("preset dry-run writes nothing", r.returncode == 0 and not (p / ".claude" / "settings.json").exists(), r.stderr)
    r = run([str(T / "proj_toggle.py"), "off", "zzskill"], p, env)
    check("skill off writes deny rule to settings.local.json", '"Skill(zzskill)"' in (p / ".claude" / "settings.local.json").read_text(), r.stderr)
    r = run([str(T / "proj_toggle.py"), "on", "zzskill"], p, env)
    check("skill on removes rule", "Skill(zzskill)" not in (p / ".claude" / "settings.local.json").read_text(), r.stderr)
    r = run([str(T / "proj_toggle.py"), "undo"], p, env)
    check("undo restores backup", r.returncode == 0, r.stderr + r.stdout)
    r = run([str(T / "upgrade.py"), str(p), "--guide", "local"], p, env)
    check("upgrade dry-run writes nothing", r.returncode == 0 and not (p / "DECISIONS.md").exists(), r.stderr + r.stdout)
    r = run([str(T / "upgrade.py"), str(p), "--guide", "local", "--apply"], p, env)
    check("upgrade --apply adds files", (p / "DECISIONS.md").exists() and (p / ".kickoff" / "guide.json").exists(), r.stderr + r.stdout)
    r = run([str(T / "upgrade.py"), str(p), "--guide", "local"], p, env)
    check("upgrade is idempotent", "Up to date" in r.stdout, r.stdout)
    r = run(["tools/doctor.py"], p, env)
    check("doctor sees the guide config", "guide" in r.stdout.lower(), r.stdout)
    r = run([str(T / "upgrade.py"), str(p)], p, env)
    check("fields not chosen is only an INFO", "fields not chosen" in r.stdout and not (p / ".kickoff" / "fields.json").exists(), r.stdout)
    r = run([str(T / "upgrade.py"), str(p), "--fields", "fields"], p, env)
    check("fields dry-run writes nothing", "deadline:" not in (p / "PROJECT_STATUS.md").read_text(encoding="utf-8")
          and not (p / ".kickoff" / "fields.json").exists(), r.stdout + r.stderr)
    r = run([str(T / "upgrade.py"), str(p), "--fields", "fields", "--apply"], p, env)
    st = (p / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    check("fields tier adds keys, no project.json", "project_status:" in st and "blocked_by:" in st and st.startswith("---")
          and "next:" in (p / "NEXT.md").read_text(encoding="utf-8") and not (p / ".kickoff" / "project.json").exists(), r.stdout + r.stderr)
    r = run([str(T / "upgrade.py"), str(p)], p, env)
    check("stored fields choice is not re-asked and is idempotent", "fields not chosen" not in r.stdout and "Up to date" in r.stdout, r.stdout)
    r = run(["tools/doctor.py"], p, env)
    check("doctor checks fields", "status fields present" in r.stdout, r.stdout)
    (p / ".kickoff" / "fields.json").write_text('{"contract": 1, "tier": "oldname"}\n', encoding="utf-8")
    r = run(["tools/doctor.py"], p, env)
    check("doctor reads an unknown stored tier as fields", "status fields present" in r.stdout, r.stdout)
    (p / "PROJECT_STATUS.md").write_text(st.replace("deadline:", "deadline: 2020-01-01", 1), encoding="utf-8")
    r = run(["tools/doctor.py"], p, env)
    check("doctor flags a passed deadline", "deadline 2020-01-01 has passed" in r.stdout, r.stdout)
    r = subprocess.run([sys.executable, str(T / "check_profiles.py")], capture_output=True, text=True)
    check("check_profiles.py passes (presets, gitignore, sections, extends, VS Code ids)", r.returncode == 0, r.stdout[-400:])

# ---- 1.3: project copy of proj_toggle, upgrade copies, plan tier, doctor plan checks, docs vs profiles ----
def sha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


with tempfile.TemporaryDirectory() as d2, tempfile.TemporaryDirectory() as h2:
    q, env2 = Path(d2), {"USERPROFILE": h2, "HOME": h2}
    (Path(h2) / ".claude" / "kickoff").mkdir(parents=True)
    (Path(h2) / ".claude" / "kickoff" / "always.json").write_text('{"keep": ["extra-plugin"]}', encoding="utf-8")
    (Path(h2) / ".claude" / "settings.json").write_text(json.dumps({"enabledPlugins": {
        "extra-plugin@byterive-kit": True, "kickoff@byterive-kit": True, "other-plugin@x": True}}), encoding="utf-8")
    (q / "tools").mkdir()
    for f in ("build_index.py", "check_budgets.py", "budgets.json", "doctor.py", "proj_toggle.py", "profile_lib.py"):
        (q / "tools" / f).write_bytes((T / f).read_bytes())
    fm2 = "---\ntitle: T\nsummary: Test file.\nkeywords: [t]\nstatus: draft\nupdated: 2026-11-02\n---\n"
    (q / "PROJECT_STATUS.md").write_text(fm2 + "# s\n", encoding="utf-8")
    (q / "NEXT.md").write_text(fm2 + "# n\n", encoding="utf-8")
    (q / "CLAUDE.md").write_text("# rules\nSee .kickoff/kit/WRAPUP_PROMPT.md\n", encoding="utf-8")

    r = run(["tools/proj_toggle.py", "preset", "unity", "--tier", "minimal", "--dry-run"], q, env2)
    check("proj_toggle copy with no kit stops with a clear message (no silent default)",
          r.returncode != 0 and "Cannot find the kickoff kit presets" in r.stdout + r.stderr, r.stdout + r.stderr)
    r = run(["tools/proj_toggle.py", "preset", "unity", "--dry-run"], q, {**env2, "CLAUDE_PLUGIN_ROOT": str(KIT.parent)})
    check("proj_toggle copy via CLAUDE_PLUGIN_ROOT keeps extra-plugin and applies the preset",
          "keep extra-plugin@byterive-kit" in r.stdout and "off  other-plugin@x" in r.stdout, r.stdout + r.stderr)

    r = run([str(T / "upgrade.py"), str(q), "--profile", "unity", "--fields", "plan"], q, env2)
    check("upgrade --fields plan dry run writes nothing", r.returncode == 0 and not (q / ".kickoff").exists() and "create .kickoff/plan.json" in r.stdout, r.stdout + r.stderr)
    r = run([str(T / "upgrade.py"), str(q), "--profile", "unity", "--fields", "plan", "--apply"], q, env2)
    need = [".kickoff/plan.json", ".kickoff/fields.json", "tools/plan.py", "tools/plan_lib.py", ".kickoff/kit/WRAPUP_PROMPT.md",
            ".kickoff/kit/CLAUDE_INSTRUCTIONS.md", ".kickoff/kit/.sources.json", ".kickoff/presets/_always.json", ".kickoff/presets/unity.json", ".kickoff/profiles/unity.md"]
    check("upgrade --fields plan --apply creates plan file, tools, kit copies and presets",
          all((q / n).exists() for n in need) and json.loads((q / ".kickoff" / "fields.json").read_text(encoding="utf-8"))["tier"] == "plan",
          [n for n in need if not (q / n).exists()] or r.stderr)
    r = run([str(T / "upgrade.py"), str(q), "--profile", "unity", "--fields", "plan"], q, env2)
    check("upgrade is idempotent with the plan tier", "Up to date" in r.stdout, r.stdout)
    r = run(["tools/proj_toggle.py", "preset", "unity", "--dry-run"], q, env2)
    check("proj_toggle copy uses .kickoff/presets with no plugin folder",
          "keep extra-plugin@byterive-kit" in r.stdout and "off  other-plugin@x" in r.stdout, r.stdout + r.stderr)

    wp = q / ".kickoff" / "kit" / "WRAPUP_PROMPT.md"
    wp.write_text("my own edit\n", encoding="utf-8")
    r = run([str(T / "upgrade.py"), str(q), "--apply"], q, env2)
    check("an edited kit copy is reported, not overwritten", wp.read_text(encoding="utf-8") == "my own edit\n" and "edited here" in r.stdout, r.stdout)
    wp.write_text("old kit text\n", encoding="utf-8")
    state_file = q / ".kickoff" / "kit" / ".sources.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    state["files"]["WRAPUP_PROMPT.md"] = sha(wp)
    state_file.write_text(json.dumps(state), encoding="utf-8")
    r = run([str(T / "upgrade.py"), str(q), "--apply"], q, env2)
    check("an unchanged old kit copy is refreshed", sha(wp) == sha(KIT / "WRAPUP_PROMPT.md") and "refresh .kickoff/kit/WRAPUP_PROMPT.md" in r.stdout, r.stdout)

    r = run(["tools/plan.py", "init", "--profile", "unity", "--priority", "20"], q, env2)
    check("plan.py init fills the empty template", r.returncode == 0 and len(json.loads((q / ".kickoff" / "plan.json").read_text(encoding="utf-8"))["phases"]) == 5, r.stdout + r.stderr)
    r = run(["tools/plan.py", "set-status", "p1", "IN_PROGRESS"], q, env2)
    r2 = run(["tools/plan.py", "set-status", "p1", "DONE", "--evidence", "smoke"], q, env2)
    r3 = run(["tools/plan.py", "render-status", "--write", "PROJECT_STATUS.md"], q, env2)
    check("set-status and render-status work in the project copy", r.returncode == 0 and r2.returncode == 0 and r3.returncode == 0
          and "Where we are" in (q / "PROJECT_STATUS.md").read_text(encoding="utf-8"), r.stderr + r2.stderr + r3.stderr)
    r = run(["tools/doctor.py"], q, env2)
    check("doctor validates the plan", "plan.json valid" in r.stdout and "no step is IN_PROGRESS past its end" in r.stdout, r.stdout)

    pf = q / ".kickoff" / "plan.json"
    data = json.loads(pf.read_text(encoding="utf-8"))
    data["phases"][1].update({"status": "IN_PROGRESS", "end": "2020-01-01", "start": "2019-12-01"})
    data["phases"][2].update({"steps": [{"id": "p3-s1", "name": "x", "status": "DONE"}], "status": "PLANNED"})
    pf.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    data["phases"][1]["steps"] = [{"id": "p2-s1", "name": "late one", "status": "IN_PROGRESS", "end": "2020-01-01"}]
    pf.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    r = run(["tools/doctor.py"], q, env2)
    check("doctor warns about a late step and a finished phase not marked DONE",
          "p2-s1 'late one' is IN_PROGRESS past its planned end" in r.stdout and "all steps are DONE or CUT but the phase is PLANNED" in r.stdout, r.stdout)
    pf.write_text('{"schema": 1, "phases": "no"}\n', encoding="utf-8")
    r = run(["tools/doctor.py"], q, env2)
    check("doctor fails on an invalid plan", r.returncode == 1 and "plan.json invalid" in r.stdout, r.stdout)
    pf.unlink()
    r = run(["tools/doctor.py"], q, env2)
    check("doctor warns about a missing plan file", ".kickoff/plan.json missing" in r.stdout, r.stdout)

# ---- 1.4: clarity rule, requirements ledger, status sections; D4 and D5 regression tests ----
import re as _re

drive = _re.compile(r"\b[A-Za-z]:[\\/]")
for rel in ("kit/CLAUDE.template.md", "kit/MASTER_SETUP_PROMPT.md", "kit/AUDIT_PROMPT.md", "kit/WRAPUP_PROMPT.md", "GUIDE.md", "README.md",
            "kit/templates/clarity-rule.md", "kit/templates/REQUIREMENTS.template.md", "kit/templates/status-sections.template.md"):
    body = (KIT.parent / rel).read_text(encoding="utf-8")
    check(f"D4: no drive path in {rel}", not drive.search(body), drive.search(body) and body[drive.search(body).start():][:60])
skill = (KIT.parent / "skills" / "wrap-up-thread" / "SKILL.md").read_text(encoding="utf-8")
check("D5: wrap-up skill points to WRAPUP_PROMPT.md and restates no steps",
      "WRAPUP_PROMPT.md" in skill and not _re.search(r"(?m)^\d+\.\s", skill), skill[:200])
wnums = [int(n) for n in _re.findall(r"(?m)^(\d+)\.\s", (KIT / "WRAPUP_PROMPT.md").read_text(encoding="utf-8"))]
check("wrap-up steps are numbered 1..N without gaps", wnums == list(range(1, len(wnums) + 1)) and len(wnums) >= 15, wnums)

with tempfile.TemporaryDirectory() as d3, tempfile.TemporaryDirectory() as h3:
    r3, env3 = Path(d3), {"USERPROFILE": h3, "HOME": h3}
    fm3 = "---\ntitle: T\nsummary: Test file.\nkeywords: [t]\nstatus: draft\nupdated: 2026-11-04\n---\n"
    (r3 / "PROJECT_STATUS.md").write_text(fm3 + "# Status\n\n## Setup\nMy own setup text.\n", encoding="utf-8")
    (r3 / "NEXT.md").write_text(fm3 + "# n\n", encoding="utf-8")
    (r3 / "CLAUDE.md").write_text("# rules\n- Test: pytest -q\n- Build: UNKNOWN\n", encoding="utf-8")
    (r3 / "README.md").write_text("# Demo\n\n## Usage\n```\npython main.py --fast\n```\n\n## Install\npip install -r requirements.txt\n", encoding="utf-8")
    (r3 / "data").mkdir()
    (r3 / "scripts").mkdir()
    (r3 / "scripts" / "download_prices.py").write_text("print('x')\n", encoding="utf-8")
    r = run([str(T / "upgrade.py"), str(r3), "--sections", "yes"], r3, env3)
    check("1.4 dry run writes nothing", "sections" in r.stdout and not (r3 / "REQUIREMENTS.md").exists()
          and "My own setup text." in (r3 / "PROJECT_STATUS.md").read_text(encoding="utf-8")
          and "How to run" not in (r3 / "PROJECT_STATUS.md").read_text(encoding="utf-8"), r.stdout + r.stderr)
    r = run([str(T / "upgrade.py"), str(r3), "--sections", "yes", "--apply"], r3, env3)
    st3 = (r3 / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    cl3 = (r3 / "CLAUDE.md").read_text(encoding="utf-8")
    check("clarity block appended once, rest of CLAUDE.md untouched",
          cl3.count("<!-- kickoff:clarity-rule -->") == 1 and cl3.startswith("# rules\n- Test: pytest -q\n- Build: UNKNOWN\n"), cl3[:200])
    check("REQUIREMENTS.md created", (r3 / "REQUIREMENTS.md").exists() and "Requirements ledger" in (r3 / "REQUIREMENTS.md").read_text(encoding="utf-8"))
    check("existing Setup section is left alone and not duplicated", st3.count("## Setup") == 1 and "My own setup text." in st3, st3)
    check("How to run pre-filled as GUESSED from CLAUDE.md and README",
          "## How to run\nGUESSED" in st3 and "Test: pytest -q" in st3 and "python main.py --fast" in st3, st3)
    check("Data pre-filled with the downloader candidate, Troubleshooting stays UNKNOWN",
          "scripts/download_prices.py" in st3 and "data/" in st3 and "## Troubleshooting\nUNKNOWN" in st3, st3)
    check("choices stored", json.loads((r3 / ".kickoff" / "options.json").read_text(encoding="utf-8")).get("sections") is True)
    r = run([str(T / "upgrade.py"), str(r3), "--sections", "yes"], r3, env3)
    check("1.4 upgrade is idempotent", "Up to date" in r.stdout, r.stdout)
    shutil.copytree(T, r3 / "tools", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "smoke_test.py", "test_*.py"))
    r = run(["tools/doctor.py"], r3, env3)
    check("doctor: clarity rule, ledger and sections lines",
          "clarity rule is in CLAUDE.md" in r.stdout and "REQUIREMENTS.md: nothing open" in r.stdout
          and "status sections: 1 of 4 confirmed, 2 GUESSED" in r.stdout and "1 UNKNOWN" in r.stdout, r.stdout)
    rq = r3 / "REQUIREMENTS.md"
    rq.write_text(rq.read_text(encoding="utf-8").replace("| R01 | | | |", "| R01 | Do the thing | OPEN | |").replace(
        "| Q1 | | |", "| Q1 | Which option? Recommendation: A | |"), encoding="utf-8")
    r = run(["tools/doctor.py"], r3, env3)
    check("doctor counts open requirements and unanswered questions", "1 requirement(s) OPEN, 1 question(s) unanswered" in r.stdout, r.stdout)

with tempfile.TemporaryDirectory() as d4, tempfile.TemporaryDirectory() as h4:
    r4, env4 = Path(d4), {"USERPROFILE": h4, "HOME": h4}
    (r4 / "PROJECT_STATUS.md").write_text(fm3 + "# s\n", encoding="utf-8")
    (r4 / "CLAUDE.md").write_text("# rules\n", encoding="utf-8")
    r = run([str(T / "upgrade.py"), str(r4), "--clarity", "no", "--sections", "no", "--apply"], r4, env4)
    check("opt-out is stored and nothing is added",
          "clarity-rule" not in (r4 / "CLAUDE.md").read_text(encoding="utf-8") and not (r4 / "REQUIREMENTS.md").exists()
          and "How to run" not in (r4 / "PROJECT_STATUS.md").read_text(encoding="utf-8")
          and json.loads((r4 / ".kickoff" / "options.json").read_text(encoding="utf-8")) == {"contract": 1, "clarity": False, "sections": False}, r.stdout + r.stderr)
    r = run([str(T / "upgrade.py"), str(r4)], r4, env4)
    check("opt-out is not re-asked", "Up to date" in r.stdout, r.stdout)

readme, guide = (KIT.parent / "README.md").read_text(encoding="utf-8"), (KIT.parent / "GUIDE.md").read_text(encoding="utf-8")
for prof in sorted(f.stem for f in (KIT / "profiles").glob("*.md") if f.stem != "INDEX"):
    check(f"README lists profile {prof}", prof in readme)
    check(f"GUIDE lists profile {prof}", prof in guide)
for script in ("test_hooks.py", "test_plan.py", "test_safety.py", "test_privacy.py", "test_upgrade143.py", "test_families.py"):
    r = subprocess.run([sys.executable, str(T / script)], capture_output=True, text=True)
    fail_lines = "\n".join(l for l in r.stdout.splitlines() if l.startswith("FAIL"))  # the tail alone only shows "N failure(s)"
    check(f"{script} passes", r.returncode == 0, fail_lines[-300:] + r.stderr[-300:] if fail_lines or r.stderr else r.stdout[-300:])

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)

#!/usr/bin/env python3
"""Tests for kickoff 1.4.1 (stdlib only): index safety (R34), guide detection (R35), CLAUDE.md paths (R36), hash fixing (R37),
line endings (R38), stale handover (R39), co-author check (R40). Usage: python test_safety.py   (exit 1 on any failure)
"""
import hashlib
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


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {str(detail)[:300]}"))
    if not ok:
        fails.append(name)


def run(args, cwd, home, extra=None):
    env = dict(os.environ, USERPROFILE=str(home), HOME=str(home), **(extra or {}))
    env.pop("KICKOFF_DISABLED_HOOKS", None) if not extra or "KICKOFF_DISABLED_HOOKS" not in extra else None
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True, env=env)


def git(repo, *args, env=None):
    e = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="old@example.com", GIT_COMMITTER_NAME="T",
             GIT_COMMITTER_EMAIL="old@example.com", FILTER_BRANCH_SQUELCH_WARNING="1", **(env or {}))
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=e).stdout.strip()


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts}


def project(d, eol="\n"):
    r = Path(d)
    (r / "tools").mkdir()
    for f in ("build_index.py", "check_budgets.py", "budgets.json", "doctor.py", "proj_toggle.py", "profile_lib.py"):
        (r / "tools" / f).write_bytes((T / f).read_bytes())
    (r / "PROJECT_STATUS.md").write_bytes((FM + "# s\n").replace("\n", eol).encode())
    (r / "NEXT.md").write_bytes((FM + "# n\n").replace("\n", eol).encode())
    (r / "CLAUDE.md").write_bytes(("# rules\n").replace("\n", eol).encode())
    return r


with tempfile.TemporaryDirectory() as h:
    home = Path(h)
    (home / ".claude").mkdir()

    # ---- R34: index safety ------------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        (r / "tools" / "budgets.json").write_text(json.dumps({"skip_dirs": ["skipme", "tests/fixtures", "locked"], "max_md_lines": 300,
                                                             "max_md_per_folder": 15, "max_code_lines": 400, "max_claude_md_lines": 200,
                                                             "code_extensions": [".py"], "required_frontmatter": ["title", "summary"],
                                                             "exempt_files": ["CLAUDE.md", "README.md", "INDEX.md"]}), encoding="utf-8")
        for sub in ("skipme", "tests/fixtures", "locked", "ok"):
            (r / sub).mkdir(parents=True)
            (r / sub / "page.md").write_text(FM + "# p\n", encoding="utf-8")
        (r / "ok" / "index.md").write_bytes(b"Hand-written home page\n")
        (r / "locked" / "index.md").write_bytes(b"Read-only sample page\n")
        before = snapshot(r)
        res = run([r / "tools" / "doctor.py", r], r, home)
        after = snapshot(r)
        new_files = sorted(set(after) - set(before))
        modified = sorted(k for k in before if k in after and before[k] != after[k])
        check("R34 doctor writes no INDEX.md under skip_dirs", not any(f.startswith(("skipme", "tests", "locked")) for f in new_files), new_files)
        check("R34 doctor modifies no existing file except generated indexes", all(m.endswith("INDEX.md") for m in modified), modified)
        check("R34 existing index.md files are untouched", (r / "ok" / "index.md").read_bytes() == b"Hand-written home page\n"
              and (r / "locked" / "index.md").read_bytes() == b"Read-only sample page\n")
        check("R34 doctor says which build_index ran and lists what it created",
              "index: ran the project's own tools/build_index.py" in res.stdout and "skip list: " in res.stdout and "created" in res.stdout, res.stdout)
        check("R34 doctor reports the file it left alone", "left alone" in res.stdout and "ok/index.md" in res.stdout, res.stdout)
        k = run([T / "build_index.py", r], Path(tempfile.gettempdir()), home)
        check("R34 the kit copy run from another folder uses the project's skip list",
              k.returncode == 0 and not (r / "skipme" / "INDEX.md").exists() and not (r / "tests" / "fixtures" / "INDEX.md").exists(), k.stdout + k.stderr)
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "a").mkdir()
        (Path(d) / "a" / "x.md").write_text(FM, encoding="utf-8")
        k = run([T / "build_index.py", d], Path(d), home)
        check("R34 the kit copy refuses a folder that is not a kickoff project", k.returncode == 2 and not (Path(d) / "a" / "INDEX.md").exists(), k.stdout + k.stderr)
        k = run([T / "build_index.py", d, "--force"], Path(d), home)
        check("R34 --force overrides the refusal", k.returncode == 0 and (Path(d) / "a" / "INDEX.md").exists(), k.stdout + k.stderr)

    # ---- R35: guide already present --------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        (r / ".guidebook").mkdir()
        up = run([T / "upgrade.py", r, "--guide", "local"], r, home)
        check("R35 upgrade does not ask about a guide when guidebook built one",
              "guide already present, built by guidebook" in up.stdout and "no guide set up" not in up.stdout
              and "create .kickoff/guide.json" not in up.stdout, up.stdout)
        run([T / "upgrade.py", r, "--guide", "local", "--apply"], r, home)
        check("R35 --guide local creates no guide.json then", not (r / ".kickoff" / "guide.json").exists())
        dr = run([r / "tools" / "doctor.py", r], r, home)
        check("R35 doctor says the guide is present", "guide already present, built by guidebook" in dr.stdout, dr.stdout)
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        up = run([T / "upgrade.py", r], r, home)
        check("R35 a project without any guide is still offered one", "no guide set up" in up.stdout, up.stdout)

    # ---- R36: CLAUDE.md references --------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        (r / "DECISIONS.md").write_text(FM + "# D\n\nNewest first. Format: date | decision.\n\n- 2026-01-01 | old | why | -\n", encoding="utf-8")
        orig = ("# rules\nProfile: unity\nRules (full text: X:\\project\\plugins\\kickoff\\kit\\CLAUDE_INSTRUCTIONS.md, "
                "profile: X:\\project\\plugins\\kickoff\\kit\\profiles\\unity.md):\n- Closing a thread: follow "
                "X:\\project\\plugins\\kickoff\\kit\\WRAPUP_PROMPT.md.\n- Other notes: F:\\Other\\notes.md\n- Keep this line.\n")
        (r / "CLAUDE.md").write_bytes(orig.encode())
        dry = run([T / "upgrade.py", r, "--clarity", "no"], r, home)
        check("R36 dry run shows the rewrite and changes nothing",
              "point 3 kit reference(s) inside the project, at .kickoff/kit/" in dry.stdout and (r / "CLAUDE.md").read_bytes() == orig.encode(), dry.stdout)
        run([T / "upgrade.py", r, "--clarity", "no", "--apply"], r, home)
        new = (r / "CLAUDE.md").read_text(encoding="utf-8")
        check("R36/R48 exactly the three kit references are rewritten (1.4.3: profile too), the rest is untouched",
              "full text: .kickoff/kit/CLAUDE_INSTRUCTIONS.md," in new and "follow .kickoff/kit/WRAPUP_PROMPT.md." in new
              and "profile: .kickoff/kit/profiles/unity.md" in new and "F:\\Other\\notes.md" in new and "- Keep this line." in new
              and new.count("<!-- kickoff:kit-references -->") == 1, new)
        check("R36 the change is noted in DECISIONS.md", "CLAUDE.md kit references now point to .kickoff/kit/" in (r / "DECISIONS.md").read_text(encoding="utf-8")
              and "- 2026-01-01 | old | why | -" in (r / "DECISIONS.md").read_text(encoding="utf-8"))
        again = run([T / "upgrade.py", r, "--clarity", "no"], r, home)
        check("R36 second run is idempotent", "Up to date" in again.stdout, again.stdout)
        dr = run([r / "tools" / "doctor.py", r], r, home)
        check("R36 doctor warns about the remaining path outside the project",
              "CLAUDE.md points outside the project: F:\\Other" in dr.stdout, dr.stdout)
        st = json.loads((r / ".kickoff" / "kit" / ".sources.json").read_text(encoding="utf-8"))
        st["kit_version"] = "1.0.0"
        (r / ".kickoff" / "kit" / ".sources.json").write_text(json.dumps(st), encoding="utf-8")
        dr = run([T / "doctor.py", r], r, home)
        check("R36 doctor warns when the kit copies are older than this kickoff", ".kickoff/kit/ copies are from kickoff 1.0.0" in dr.stdout, dr.stdout)

    # ---- R37: stale hashes after a history rewrite ------------------------------------------------------------
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        git(r, "init", "-q", "-b", "main")
        olds = []
        for i in range(3):
            (r / f"f{i}.txt").write_text(str(i), encoding="utf-8")
            git(r, "add", "-A")
            git(r, "commit", "-q", "-m", f"commit {i}")
            olds.append(git(r, "rev-parse", "HEAD"))
        git(r, "filter-branch", "-f", "--env-filter", 'export GIT_AUTHOR_EMAIL="new@example.com"; export GIT_COMMITTER_EMAIL="new@example.com"', "--", "--all")
        news = git(r, "log", "--reverse", "--format=%H").split("\n")
        (r / "NEXT.md").write_text(FM + f"# n\nStopped at {olds[2][:7]}; started from {olds[0]}.\n", encoding="utf-8")
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "docs")
        dr = run([r / "tools" / "doctor.py", r], r, home)
        check("R37 doctor warns about commit hashes git cannot find", "NEXT.md: commit hash(es) git cannot find" in dr.stdout and olds[2][:7] in dr.stdout, dr.stdout)
        mp = r / "map.txt"
        mk = run([T / "fix_hashes.py", "--make-map", r, "--old-ref", "refs/original/refs/heads/main", "--new-ref", "main~1", "--out", mp], r, home)
        pairs = dict(l.split() for l in mp.read_text(encoding="utf-8").splitlines()) if mp.exists() else {}
        check("R37 the old-to-new map pairs every commit", mk.returncode == 0 and pairs == dict(zip(olds, news[:3])), mk.stdout + mk.stderr)
        dry = run([T / "fix_hashes.py", r, "--map", mp], r, home)
        check("R37 dry run reports and writes nothing", "would change" in dry.stdout and olds[2][:7] in (r / "NEXT.md").read_text(encoding="utf-8"), dry.stdout)
        run([T / "fix_hashes.py", r, "--map", mp, "--apply"], r, home)
        nxt = (r / "NEXT.md").read_text(encoding="utf-8")
        check("R37 short and full hashes are replaced by the same-length new hash",
              f"Stopped at {news[2][:7]};" in nxt and f"started from {news[0]}." in nxt, nxt)
        dr = run([r / "tools" / "doctor.py", r], r, home)
        check("R37 doctor is quiet after the fix", "no unresolvable commit hashes" in dr.stdout, dr.stdout)
        amb = r / "amb.txt"
        amb.write_text("aaaaaaa1111 " + "b" * 40 + "\n", encoding="utf-8")
        (r / "NEXT.md").write_text("see abcdef1\n", encoding="utf-8")
        amb.write_text("abcdef1000000000000000000000000000000001 1111111111111111111111111111111111111111\n"
                       "abcdef1000000000000000000000000000000002 2222222222222222222222222222222222222222\n", encoding="utf-8")
        am = run([T / "fix_hashes.py", r, "--map", amb, "--apply"], r, home)
        check("R37 a short hash that matches two old commits is left alone", "matches more than one old commit" in am.stdout
              and (r / "NEXT.md").read_text(encoding="utf-8") == "see abcdef1\n", am.stdout)

    # ---- R38: line endings ---------------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as d:
        r = project(d, eol="\r\n")
        (r / "README.md").write_bytes(b"# Demo\r\n\r\n## Usage\r\npython main.py\r\n")
        run([T / "upgrade.py", r, "--profile", "unity", "--sections", "yes", "--fields", "fields", "--apply"], r, home)
        names = ["REQUIREMENTS.md", "DECISIONS.md", "CLAUDE.md", "PROJECT_STATUS.md", "NEXT.md", ".kickoff/presets/_always.json",
                 ".kickoff/kit/WRAPUP_PROMPT.md", ".kickoff/fields.json", ".kickoff/options.json"]
        bare = [n for n in names if (r / n).exists() and b"\n" in (r / n).read_bytes().replace(b"\r\n", b"")]
        check("R38 a CRLF project gets CRLF in every file the upgrade writes", not bare and all((r / n).exists() for n in names), bare)
        again = run([T / "upgrade.py", r, "--profile", "unity", "--sections", "yes", "--fields", "fields"], r, home)
        check("R38 the CRLF project is idempotent", "Up to date" in again.stdout, again.stdout)
        ga = (r / ".gitattributes").read_text(encoding="utf-8")
        check("R38 .gitattributes recommends eol rules for markdown and json", "*.md text eol=lf" in ga and "*.json text eol=lf" in ga, ga)
    with tempfile.TemporaryDirectory() as d:
        r = project(d, eol="\n")
        run([T / "upgrade.py", r, "--profile", "unity", "--sections", "yes", "--apply"], r, home)
        check("R38 an LF project stays LF", all(b"\r" not in p.read_bytes() for p in r.rglob("*") if p.is_file() and p.suffix in (".md", ".json")
                                                and ".git" not in p.parts and p.parent.name != "tools"), [str(p) for p in r.rglob("*.md") if b"\r" in p.read_bytes()])
    with tempfile.TemporaryDirectory() as d:
        r = project(d, eol="\n")
        (r / "CLAUDE.md").unlink()
        (r / ".gitattributes").write_text("* text=auto eol=crlf\n", encoding="utf-8")
        run([T / "upgrade.py", r, "--apply"], r, home)
        check("R38 with no CLAUDE.md, .gitattributes eol=crlf decides", (r / "NEXT.md").exists() and b"\r\n" in (r / "DECISIONS.md").read_bytes())

    # ---- R39: stale handover ----------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        git(r, "init", "-q", "-b", "main")
        (r / "NEXT.md").write_text(FM.replace("2026-11-04", "2020-01-01") + "# n\n**Half-done / uncommitted:** nothing committed yet.\n", encoding="utf-8")
        (r / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")  # tools import profile_lib; a real project ignores the cache
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "work")
        dr = run([r / "tools" / "doctor.py", r], r, home)
        check("R39 doctor flags NEXT.md older than HEAD", "NEXT.md was updated 2020-01-01 but HEAD is from" in dr.stdout, dr.stdout)
        check("R39 doctor flags 'uncommitted' text when git is clean", "NEXT.md talks about uncommitted work but git status is clean" in dr.stdout, dr.stdout)
    wp = (KIT / "WRAPUP_PROMPT.md").read_text(encoding="utf-8")
    check("R39 wrap-up recomputes uncommitted work from git status", "git status --short" in wp and "Recompute" in wp)
    check("R34 wrap-up uses the project's own index tool", "never the kit copy" in wp)

    # ---- R40: co-author block ---------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as d:
        r = project(d)
        (home / ".claude" / "settings.json").write_text(json.dumps({"enabledPlugins": {"kickoff@byterive-kit": True}}), encoding="utf-8")
        dr = run([r / "tools" / "doctor.py", r], r, home)
        check("R40 doctor reports the co-author block active", "co-author block active" in dr.stdout, dr.stdout)
        dr = run([r / "tools" / "doctor.py", r], r, home, {"KICKOFF_DISABLED_HOOKS": "coauthor"})
        check("R40 doctor reports it inactive when the hook is switched off", "co-author block inactive: KICKOFF_DISABLED_HOOKS" in dr.stdout, dr.stdout)
        (r / ".claude").mkdir()
        (r / ".claude" / "settings.json").write_text(json.dumps({"enabledPlugins": {"kickoff@byterive-kit": False}}), encoding="utf-8")
        dr = run([r / "tools" / "doctor.py", r], r, home)
        check("R40 doctor reports it inactive when the project turns kickoff off", "co-author block inactive: kickoff is" in dr.stdout, dr.stdout)
    hk = subprocess.run([sys.executable, str(T.parent.parent / "hooks" / "block_claude_coauthor.py")],
                        input=json.dumps({"tool_input": {"command": 'git commit -m "x" -m "Co-Authored-By: Claude <noreply@example.com>"'}}), capture_output=True, text=True)
    check("R40 the co-author hook blocks the trailer", hk.returncode == 2)

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)

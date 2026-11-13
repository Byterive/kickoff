#!/usr/bin/env python3
"""Tests for profile families (stdlib only): extends resolution, the go-backend alias, section merge, preset fallback,
default phases from the main profile, upgrade copying the whole family, and the .vscode/extensions.json writer.
Usage: python test_families.py   (exit 1 on any failure)"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

T = Path(__file__).resolve().parent
KIT = T.parent
sys.path.insert(0, str(T))
import profile_lib as P  # noqa: E402

fails = []


def check(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else "  " + str(detail)[-300:]))
    if not ok:
        fails.append(label)


def run(args, cwd):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=cwd)


with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    names = lambda n: [x for x, _ in P.lineage(n, root, [KIT])]  # noqa: E731
    check("backend-go extends backend", names("backend-go") == ["backend", "backend-go"], names("backend-go"))
    check("alias go-backend resolves to backend-go", names("go-backend") == ["backend", "backend-go"], names("go-backend"))
    check("a main profile has a one-step lineage", names("backend") == ["backend"])
    for sec, key in (("backend-rust", "rust_version"), ("backend-node", "node_version")):
        check(f"{sec} extends backend and replaces Extra frontmatter", names(sec) == ["backend", sec] and key in P.section([p for _, p in P.lineage(sec, root, [KIT])], "Extra frontmatter"), names(sec))
    paths = [p for _, p in P.lineage("backend-go", root, [KIT])]
    never = P.section(paths, "Never do")
    check("Never do is merged (main first, then go)", "Commit secrets" in never and "go vet" in never and never.index("Commit") < never.index("go vet"), never)
    fm = P.section(paths, "Extra frontmatter")
    check("Extra frontmatter is replaced by the secondary", "go_version" in fm and "runtime_version" not in fm, fm)
    check("a section the secondary lacks comes from the main", "Design" in P.section(paths, "Default phases"))
    check("VS Code sections are merged", "editorconfig" in P.section(paths, "VS Code") and "golang.go" in P.section(paths, "VS Code"))

    check("frontend-react extends frontend", names("frontend-react") == ["frontend", "frontend-react"], names("frontend-react"))
    check("trading-research extends data-research and keeps its own phases", names("trading-research") == ["data-research", "trading-research"]
          and "Backtest" in P.section([p for _, p in P.lineage("trading-research", root, [KIT])], "Default phases"))
    check("personal-utilities extends utility", names("personal-utilities") == ["utility", "personal-utilities"])
    tr = P.section([p for _, p in P.lineage("trading-research", root, [KIT])], "Never do")
    check("trading-research Never do merges main and own rules", "Commit raw data" in tr and "Live trading" in tr, tr)
    r = run([T / "proj_toggle.py", "preset", "frontend-vue", "--tier", "recommended", "--dry-run"], root)
    check("frontend-vue uses the frontend preset", "No preset" not in r.stdout + r.stderr and r.returncode == 0, r.stdout + r.stderr)

    # a project-level profile file wins; a missing parent is skipped, not a crash
    proj = root / "p"
    (proj / ".kickoff" / "profiles").mkdir(parents=True)
    (proj / ".kickoff" / "profiles" / "lonely.md").write_text("---\ntitle: t\nextends: nothere\n---\n## Default phases\n- One\n", encoding="utf-8")
    check("missing parent is skipped", [n for n, _ in P.lineage("lonely", proj, [KIT])] == ["lonely"])
    (proj / ".kickoff" / "profiles" / "a.md").write_text("---\ntitle: a\nextends: b\n---\n", encoding="utf-8")
    (proj / ".kickoff" / "profiles" / "b.md").write_text("---\ntitle: b\nextends: a\n---\n", encoding="utf-8")
    check("an extends cycle ends", len(P.lineage("a", proj, [KIT])) <= 2)

    # tools
    r = run([T / "plan.py", "--root", d, "--file", root / "plan.json", "init", "--profile", "backend-python"], root)
    plan = json.loads((root / "plan.json").read_text(encoding="utf-8")) if (root / "plan.json").exists() else {}
    check("plan.py init takes the main profile's phases for a secondary", r.returncode == 0 and len(plan.get("phases", [])) == 4, r.stdout + r.stderr)
    r = run([T / "proj_toggle.py", "preset", "go-backend", "--tier", "recommended", "--dry-run"], root)
    check("preset falls back to the main profile (alias too)", "No preset" not in r.stdout + r.stderr and r.returncode == 0, r.stdout + r.stderr)
    r = run([T / "check_budgets.py", d, "--profile", "backend-go"], root)
    check("check_budgets accepts a secondary profile", "Traceback" not in r.stderr, r.stderr)

    # upgrade copies the whole family
    q = root / "q"
    q.mkdir()
    (q / "PROJECT_STATUS.md").write_text("# s\n", encoding="utf-8")
    r = run([T / "upgrade.py", q, "--profile", "go-backend", "--apply"], q)
    check("upgrade copies main and secondary profile files", (q / ".kickoff" / "profiles" / "backend.md").exists() and (q / ".kickoff" / "profiles" / "backend-go.md").exists(), r.stdout + r.stderr)
    check("upgrade copies the main preset", (q / ".kickoff" / "presets" / "backend.json").exists(), r.stdout)
    gi = (q / ".gitignore").read_text(encoding="utf-8") if (q / ".gitignore").exists() else ""
    check("gitignore has main and secondary lines", "coverage.*" in gi and "/vendor/" in gi, gi)
    check("gitignore keeps extensions.json shareable", "!.vscode/extensions.json" in gi, gi)
    check("upgrade copies profile_lib.py beside the tools", True if (q / "tools" / "profile_lib.py").exists() else "tools" and False)

    r = run([T / "companions.py", q, "--profile", "unity", "--json"], q)
    try:
        rows = json.loads(r.stdout)
    except ValueError:
        rows = []
    check("companions lists unity-game-kit for the unity profile", any(x["name"] == "unity-game-kit" for x in rows), r.stdout + r.stderr)
    check("companions never installs (read-only, state is reported)", all(x["state"] in ("missing", "installed", "installed, off here") for x in rows))
    r = run([T / "companions.py", q, "--profile", "claude-plugin"], q)
    check("a profile without companions says so", "no companion plugins" in r.stdout, r.stdout)

    # extensions.json writer
    e = root / "e"
    (e / ".vscode").mkdir(parents=True)
    (e / ".vscode" / "extensions.json").write_text(json.dumps({"recommendations": ["my.own"], "unwantedRecommendations": ["x.y"]}), encoding="utf-8")
    r = run([T / "vscode_ext.py", e, "--profile", "backend-go"], e)
    check("dry run writes nothing", json.loads((e / ".vscode" / "extensions.json").read_text(encoding="utf-8"))["recommendations"] == ["my.own"], r.stdout)
    run([T / "vscode_ext.py", e, "--profile", "backend-go", "--apply"], e)
    data = json.loads((e / ".vscode" / "extensions.json").read_text(encoding="utf-8"))
    check("merge keeps existing entries and adds the family's", data["recommendations"][0] == "my.own" and "golang.go" in data["recommendations"] and "editorconfig.editorconfig" in data["recommendations"], data)
    check("merge keeps other keys", data.get("unwantedRecommendations") == ["x.y"], data)
    run([T / "vscode_ext.py", e, "--profile", "backend-go", "--apply"], e)
    check("second run adds nothing", json.loads((e / ".vscode" / "extensions.json").read_text(encoding="utf-8")) == data)
    u = root / "u"
    run([T / "vscode_ext.py", u, "--profile", "unity", "--apply"], root)
    check("unverified ids are skipped by default", not (u / ".vscode" / "extensions.json").exists() or "csdevkit" not in (u / ".vscode" / "extensions.json").read_text(encoding="utf-8"))
    bad = root / "bad"
    (bad / ".vscode").mkdir(parents=True)
    (bad / ".vscode" / "extensions.json").write_text("{ // comment\n}", encoding="utf-8")
    r = run([T / "vscode_ext.py", bad, "--profile", "backend-go", "--apply"], bad)
    check("invalid JSON is refused and left alone", r.returncode != 0 and (bad / ".vscode" / "extensions.json").read_text(encoding="utf-8").startswith("{ //"), r.stdout + r.stderr)

    # list_profiles, new_profile, undo
    r = run([T / "list_profiles.py"], root)
    check("list_profiles shows families and the alias", "backend-go (extends backend)" in r.stdout and "alias: go-backend -> backend-go" in r.stdout, r.stdout)
    r = run([T / "new_profile.py", q, "--name", "demo", "--extends", "backend"], q)
    check("new_profile prints a draft with extends and UNKNOWN markers", "extends: backend" in r.stdout and "UNKNOWN" in r.stdout and r.returncode == 0, r.stdout + r.stderr)
    r = run([T / "new_profile.py", q, "--name", "Bad Name"], q)
    check("new_profile refuses a bad name", r.returncode != 0)
    z = root / "z"
    z.mkdir()
    (z / "keep.txt").write_text("a", encoding="utf-8")
    run([T / "undo.py", z, "--snapshot"], z)
    (z / "docs").mkdir()
    (z / "docs" / "a.md").write_text("x", encoding="utf-8")
    (z / "NEXT.md").write_text("n", encoding="utf-8")
    (z / "keep.txt").write_text("changed", encoding="utf-8")
    run([T / "undo.py", z, "--record"], z)
    (z / "NEXT.md").write_text("edited by the user", encoding="utf-8")
    r = run([T / "undo.py", z], z)
    check("undo dry run changes nothing", (z / "docs" / "a.md").exists() and "would remove docs/a.md" in r.stdout, r.stdout)
    run([T / "undo.py", z, "--apply"], z)
    check("undo removes unchanged created files and empty folders", not (z / "docs").exists())
    check("undo keeps an edited file and pre-existing files", (z / "NEXT.md").read_text(encoding="utf-8") == "edited by the user" and (z / "keep.txt").read_text(encoding="utf-8") == "changed")
    r = run([T / "undo.py", root / "nothing"], root)
    check("undo with no record says so", r.returncode != 0)

    # profile stamp and doctor checks
    stamp = json.loads((q / ".kickoff" / "profile.stamp.json").read_text(encoding="utf-8")) if (q / ".kickoff" / "profile.stamp.json").exists() else {}
    check("upgrade records the profile stamp (alias resolved)", stamp.get("profile") == "backend-go" and stamp.get("fingerprint"), stamp)
    r = run([q / "tools" / "doctor.py", q], q)
    check("doctor: profile unchanged since setup", "profile 'backend-go' unchanged since setup" in r.stdout, r.stdout[-400:])
    cp = q / ".kickoff" / "profiles" / "backend-go.md"
    cp.write_text(cp.read_text(encoding="utf-8") + "\nextra line\n", encoding="utf-8")
    r = run([q / "tools" / "doctor.py", q], q)
    check("doctor: profile changed since setup is flagged", "profile 'backend-go' changed in the kit since this project was set up" in r.stdout, r.stdout[-400:])
    (q / "tools" / "profile_lib.py").unlink()
    r = run([q / "tools" / "doctor.py", q], q)
    check("doctor: missing profile_lib.py is flagged", "no profile_lib.py" in r.stdout or "doctor_extra.py not in tools" in r.stdout, r.stdout[-400:])

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)

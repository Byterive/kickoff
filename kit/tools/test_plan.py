#!/usr/bin/env python3
"""Conformance and behaviour tests for plan.py / plan_lib.py (stdlib only). Usage: python test_plan.py

Reads kit/tests/plan/expected.json (valid and invalid plan files with the exit codes and messages plan.py must give;
other readers and writers can be tested against the same files). Exit 1 on any failure.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

T = Path(__file__).resolve().parent
KIT = T.parent
FIX = KIT / "tests" / "plan"
sys.path.insert(0, str(T))
import plan_lib  # noqa: E402

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {str(detail)[:300]}"))
    if not ok:
        fails.append(name)


def plan(*args, cwd=None):
    r = subprocess.run([sys.executable, str(T / "plan.py"), *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout, r.stderr


expected = json.loads((FIX / "expected.json").read_text(encoding="utf-8"))
for rel, exp in expected["validate"].items():
    code, out, err = plan("--file", str(FIX / rel), "validate")
    ok = code == exp["exit"] and all(s in out for s in exp.get("stdout_contains", [])) and all(s in err for s in exp.get("stderr_contains", []))
    check(f"validate {rel} -> {exp['exit']}", ok, (code, out, err))
for i, exp in enumerate(expected["commands"], 1):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "plan.json"
        shutil.copy2(FIX / exp["file"], f)
        args = exp["args"]
        code, out, err = plan("--file", str(f), *args)
        ok = code == exp["exit"] and all(s in out for s in exp.get("stdout_contains", [])) and all(s in err for s in exp.get("stderr_contains", []))
        check(f"command {i}: {' '.join(args)} on {exp['file']}", ok, (code, out, err))


def tree(data):
    return {n["id"]: n for n, _ in plan_lib.nodes(data)}


with tempfile.TemporaryDirectory() as d:
    f = Path(d) / "plan.json"
    shutil.copy2(FIX / "valid" / "full.json", f)
    before = json.loads(f.read_text(encoding="utf-8"))
    code, out, err = plan("--file", str(f), "--today", "2026-12-02", "set-status", "p2-s1", "PASSED", "--evidence", "engine tests pass")
    after = json.loads(f.read_text(encoding="utf-8"))
    check("set-status accepts the alias PASSED and exits 0", code == 0, (out, err))
    n = tree(after)["p2-s1"]
    check("status DONE and actual_end filled", n["status"] == "DONE" and n["actual_end"] == "2026-12-02" and n["evidence"] == "engine tests pass", n)
    same = all(tree(before)[k].get(x) == tree(after)[k].get(x) for k in tree(before) for x in ("start", "end", "name", "id"))
    check("planned dates, names and ids unchanged", same)
    check("priority unchanged", before["priority"] == after["priority"] == 20)
    check("meta stamp written", after.get("meta", {}).get("updated_by") == "kickoff plan.py")
    text = f.read_text(encoding="utf-8")
    check("2-space indent, trailing newline, LF", text.endswith("}\n") and "\n  \"schema\"" in text and "\r" not in text)
    code, out, err = plan("--file", str(f), "set-status", "p2-s1", "IN_PROGRESS")
    check("reopening clears actual_end", tree(json.loads(f.read_text(encoding="utf-8")))["p2-s1"]["actual_end"] == "", out)

with tempfile.TemporaryDirectory() as d:
    f = Path(d) / "plan.json"
    shutil.copy2(FIX / "valid" / "unknown_keys.json", f)
    plan("--file", str(f), "set-status", "p1-s1", "DONE", "--actual-end", "2026-11-03")
    data = json.loads(f.read_text(encoding="utf-8"))
    n = tree(data)["p1-s1"]
    check("unknown keys are preserved", data.get("owner") == "someone" and tree(data)["p1"].get("colour") == "teal" and n.get("notes") == "keep me", data)
    check("explicit --actual-end used", n["actual_end"] == "2026-11-03")

with tempfile.TemporaryDirectory() as d:
    f = Path(d) / "plan.json"
    shutil.copy2(FIX / "valid" / "full.json", f)
    calls = []

    def mutate(data):
        calls.append(1)
        if len(calls) == 1:  # another writer (another tool) saves a new priority between our read and write
            other = json.loads(f.read_text(encoding="utf-8"))
            other["priority"] = 30
            f.write_text(json.dumps(other, indent=2) + "\n", encoding="utf-8")
        plan_lib.find(data, "p2-s2")[0]["status"] = "IN_PROGRESS"

    plan_lib.update(f, mutate)
    data = json.loads(f.read_text(encoding="utf-8"))
    check("concurrent edit is merged, not lost", len(calls) == 2 and data["priority"] == 30 and tree(data)["p2-s2"]["status"] == "IN_PROGRESS", (calls, data["priority"]))

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    code, out, err = plan("--root", str(root), "init", "--phase", "Research", "--phase", "Build", "--priority", "40")
    check("init from --phase creates a valid file", code == 0 and plan("--root", str(root), "validate")[0] == 0, err)
    check("init never overwrites", plan("--root", str(root), "init", "--phase", "X")[0] == 1)
    with tempfile.TemporaryDirectory() as empty:
        code, out, err = plan("--root", empty, "init", "--profile", "nonexistent-profile")
    check("init without phases explains itself", code == 1 and "no phases" in err, err)
    status = root / "PROJECT_STATUS.md"
    status.write_text("---\ntitle: S\n---\n# Status\nKeep this line.\n", encoding="utf-8")
    plan("--root", str(root), "render-status", "--write", "PROJECT_STATUS.md")
    first = status.read_text(encoding="utf-8")
    code, out, err = plan("--root", str(root), "render-status", "--write", "PROJECT_STATUS.md")
    check("render-status --write is idempotent and keeps other text", status.read_text(encoding="utf-8") == first and "Keep this line." in first and "already current" in out, out)
    plan("--root", str(root), "set-status", "p1", "DONE")
    plan("--root", str(root), "render-status", "--write", "PROJECT_STATUS.md")
    again = status.read_text(encoding="utf-8")
    check("render-status --write replaces the block", again != first and again.count("<!-- kickoff:where-we-are -->") == 1 and "Keep this line." in again, again)

for p in KIT.glob("profiles/*.md"):
    if p.stem != "custom":
        with tempfile.TemporaryDirectory() as d:
            code, out, err = plan("--root", d, "init", "--profile", p.stem)
            check(f"profile {p.stem} has default phases", code == 0 and plan("--root", d, "validate")[0] == 0, err)

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)

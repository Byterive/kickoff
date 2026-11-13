#!/usr/bin/env python3
"""Read and update a project's shared plan file, .kickoff/plan.json (stdlib only). Schema: kit/PLAN_SCHEMA.md.

  plan.py validate                         check the file (exit 0 ok, 2 invalid, 1 missing/error)
  plan.py show [--json]                    current phase and step, progress, late or slipped items
  plan.py next [--count 3] [--json]        next steps not yet DONE or CUT, in plan order
  plan.py set-status <id> <STATUS> [--actual-start DATE] [--actual-end DATE] [--evidence TEXT]
                                           change status, actual dates and evidence of one phase or step (nothing else)
  plan.py render-status [--write FILE]     the "Where we are" block (replaces the block in FILE if given)
  plan.py init [--profile NAME] [--phase NAME ...] [--priority N]
                                           create the file from a profile's "Default phases"; never overwrites

Global options: --root DIR (project folder, default current), --file PATH (default <root>/.kickoff/plan.json),
--today YYYY-MM-DD (for tests). Exit codes: 0 ok, 1 error or refused, 2 invalid plan file.

plan.py never changes start, end, priority, ids, names or unknown keys. Writes are atomic (temp file, then replace),
keep key order, use 2-space indent and a trailing newline. If the file changes between reading and writing (for
example another tool saved a new date), plan.py re-reads and applies only its own change again, so both edits survive.
"""
import argparse
import datetime
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import profile_lib  # noqa: E402
from plan_lib import (BLOCK_END, BLOCK_START, Failure, current, find, load, load_valid, next_items, nodes,  # noqa: E402
                      normalize_status, order_keys, parse_date, render_block, save_atomic, span, status_of, timing_notes,
                      update, validate)


def today_of(args):
    if args.today:
        d = parse_date(args.today)
        if not d:
            raise Failure("--today must be YYYY-MM-DD", 1)
        return d
    return datetime.date.today()


# ---- commands -------------------------------------------------------------------------------------------------

def cmd_validate(args, path):
    data = load(path)
    errs = validate(data)
    if errs:
        print("INVALID " + str(path))
        for e in errs:
            print("  " + e)
        return 2
    n_steps = sum(1 for _, p in nodes(data) if p is not None)
    print(f"OK: {len(data['phases'])} phase(s), {n_steps} step(s)")
    return 0


def cmd_show(args, path):
    data = load_valid(path)
    today = today_of(args)
    ph, st = current(data)
    steps = [n for n, p in nodes(data) if p is not None]
    done = sum(1 for s in steps if status_of(s) == "DONE")
    if args.json:
        print(json.dumps({"priority": data.get("priority"), "current_phase": ph and ph["id"], "current_step": st and st["id"],
                          "steps_done": done, "steps_total": len(steps)}))
        return 0
    print(f"Priority: {data.get('priority') if data.get('priority') is not None else 'not set'}")
    print(f"Current phase: {ph['name'] + ' (' + ph['id'] + ', ' + status_of(ph) + ')' if ph else 'none (all DONE or CUT)'}")
    print(f"Current step:  {st['name'] + ' (' + st['id'] + ', ' + status_of(st) + ')' if st else 'none'}")
    print(f"Progress: {done} of {len(steps)} step(s) DONE")
    for p in data["phases"]:
        sub = [s for s in p.get("steps", [])]
        note = timing_notes(p, today)
        print(f"- {p['id']} {p['name']} [{status_of(p)}] {span(p)}; {sum(1 for s in sub if status_of(s) == 'DONE')}/{len(sub)} steps" +
              (f"; {note}" if note else ""))
        for s in sub:
            n = timing_notes(s, today)
            print(f"    {s['id']} {s['name']} [{status_of(s)}] {span(s)}" + (f"; {n}" if n else ""))
    return 0


def cmd_next(args, path):
    data = load_valid(path)
    items = next_items(data, args.count)
    if args.json:
        print(json.dumps([{"id": n["id"], "name": n["name"], "phase": p["name"], "status": status_of(n),
                           "start": n.get("start", ""), "end": n.get("end", "")} for n, p in items]))
        return 0
    if not items:
        print("Nothing left: every phase and step is DONE or CUT.")
    for n, p in items:
        print(f"{n['id']} | {n['name']} | phase: {p['name']} | {span(n)} | {status_of(n)}")
    return 0


def cmd_set_status(args, path):
    status = normalize_status(args.status)
    today = today_of(args).isoformat()
    for label in ("actual_start", "actual_end"):
        v = getattr(args, label)
        if v is not None and parse_date(v) is False:
            raise Failure(f"--{label.replace('_', '-')} must be YYYY-MM-DD", 1)
    notes = []

    def mutate(data):
        node, _ = find(data, args.id)
        prev = status_of(node)
        node["status"] = status
        if args.actual_start is not None:
            node["actual_start"] = args.actual_start
        elif status == "IN_PROGRESS" and not node.get("actual_start"):
            node["actual_start"] = today
            notes.append(f"actual_start set to {today}")
        if args.evidence:
            node["evidence"] = args.evidence
        if args.actual_end is not None:
            node["actual_end"] = args.actual_end
        elif status == "DONE" and not node.get("actual_end"):
            node["actual_end"] = today
            notes.append(f"actual_end set to {today}")
        elif prev == "DONE" and status in ("PLANNED", "IN_PROGRESS") and node.get("actual_end"):
            node["actual_end"] = ""
            notes.append("actual_end cleared (reopened)")
        order_keys(node)

    update(path, mutate)
    print(f"{args.id}: {status}" + (" (" + "; ".join(notes) + ")" if notes else ""))
    return 0


def cmd_render_status(args, path):
    block = render_block(load_valid(path), today_of(args))
    if not args.write:
        sys.stdout.write(block)
        return 0
    target = Path(args.write)
    if not target.is_absolute():
        target = Path(args.root or ".").resolve() / target
    text = target.read_text(encoding="utf-8") if target.exists() else ""
    if BLOCK_START in text and BLOCK_END in text:
        a, b = text.index(BLOCK_START), text.index(BLOCK_END) + len(BLOCK_END)
        new = text[:a] + block.rstrip("\n") + text[b:]
    else:
        new = text.rstrip("\n") + ("\n\n" if text.strip() else "") + block
    if new != text:
        fd, tmp = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=str(target.parent))
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(new)
        os.replace(tmp, target)
    print(f"Where-we-are block {'updated in' if new != text else 'already current in'} {target}")
    return 0


def kit_dirs(root):
    cands = []
    if os.environ.get("CLAUDE_PLUGIN_ROOT"):
        cands.append(Path(os.environ["CLAUDE_PLUGIN_ROOT"]) / "kit")
    cands.append(Path(__file__).resolve().parent.parent)
    try:
        cands.append(Path((root / ".kickoff" / "kit_path").read_text(encoding="utf-8").strip()))
    except OSError:
        pass
    return [d for c in cands for d in (c, c / "kit") if (d / "profiles").is_dir()]


def default_phases(profile, root):
    paths = [p for _, p in profile_lib.lineage(profile, root, kit_dirs(root))]
    text = profile_lib.section(paths, "Default phases") if paths else ""
    out = []
    for line in profile_lib.bullets(text):
        name, _, steps = line.partition(":")
        out.append((name.strip(), [s.strip() for s in steps.split(";") if s.strip()]))
    return out


def cmd_init(args, path):
    existing = None
    if path.exists():
        existing = load(path)
        if not (isinstance(existing, dict) and existing.get("phases") == []):
            raise Failure(f"{path} already has a plan; plan.py init never overwrites", 1)
    root = Path(args.root or ".").resolve()
    phases = [(p, []) for p in (args.phase or [])] or (default_phases(args.profile, root) if args.profile else [])
    if not phases:
        raise Failure("no phases: give --profile NAME (its 'Default phases' section) or one or more --phase NAME", 1)
    if args.priority is not None and not (1 <= args.priority <= 999):
        raise Failure("--priority must be 1..999", 1)
    data = {"schema": 1, "priority": args.priority if args.priority is not None else (existing or {}).get("priority"), "phases": []}
    for i, (name, steps) in enumerate(phases, 1):
        ph = {"id": f"p{i}", "name": name, "start": "", "end": "", "status": "PLANNED", "actual_start": "", "actual_end": "",
              "steps": [{"id": f"p{i}-s{j}", "name": s, "start": "", "end": "", "status": "PLANNED", "actual_start": "",
                         "actual_end": ""} for j, s in enumerate(steps, 1)]}
        data["phases"].append(ph)
    errs = validate(data)
    if errs:
        raise Failure("generated plan is invalid:\n  " + "\n  ".join(errs), 2)
    path.parent.mkdir(parents=True, exist_ok=True)
    save_atomic(path, data)
    print(f"Created {path} with {len(phases)} phase(s). Set planned dates and priority by hand.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="plan.py", description=__doc__.split("\n")[0])
    ap.add_argument("--root")
    ap.add_argument("--file")
    ap.add_argument("--today")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    p = sub.add_parser("show")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("next")
    p.add_argument("--count", type=int, default=3)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("set-status")
    p.add_argument("id")
    p.add_argument("status")
    p.add_argument("--actual-start", dest="actual_start")
    p.add_argument("--actual-end", dest="actual_end")
    p.add_argument("--evidence")
    p = sub.add_parser("render-status")
    p.add_argument("--write")
    p = sub.add_parser("init")
    p.add_argument("--profile")
    p.add_argument("--phase", action="append")
    p.add_argument("--priority", type=int)
    args = ap.parse_args(argv)
    root = Path(args.root or ".").resolve()
    path = Path(args.file) if args.file else root / ".kickoff" / "plan.json"
    handlers = {"validate": cmd_validate, "show": cmd_show, "next": cmd_next, "set-status": cmd_set_status,
                "render-status": cmd_render_status, "init": cmd_init}
    try:
        return handlers[args.cmd](args, path)
    except Failure as e:
        print(f"plan.py: {e}", file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.exit(main())

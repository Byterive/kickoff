"""Plan file helpers shared by plan.py: schema validation, safe reading and writing, derived values (stdlib only).
Schema: kit/PLAN_SCHEMA.md."""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

STATUSES = ("PLANNED", "IN_PROGRESS", "DONE", "BLOCKED", "CUT")
ALIASES = {
    "PASSED": "DONE", "COMPLETE": "DONE", "COMPLETED": "DONE", "FINISHED": "DONE",
    "WIP": "IN_PROGRESS", "ACTIVE": "IN_PROGRESS", "STARTED": "IN_PROGRESS", "INPROGRESS": "IN_PROGRESS",
    "TODO": "PLANNED", "PENDING": "PLANNED", "UNTESTED": "PLANNED",
    "HOLD": "BLOCKED", "ON_HOLD": "BLOCKED", "STUCK": "BLOCKED",
    "DROPPED": "CUT", "CANCELLED": "CUT", "CANCELED": "CUT", "WONTFIX": "CUT",
}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KEY_ORDER = ["id", "name", "start", "end", "status", "actual_start", "actual_end", "evidence", "steps"]
BLOCK_START, BLOCK_END = "<!-- kickoff:where-we-are -->", "<!-- /kickoff:where-we-are -->"
OWN_FIELDS = ("status", "actual_start", "actual_end", "evidence")


class Failure(Exception):
    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


def parse_date(value):
    if value in (None, ""):
        return None
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return False


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def validate(data):
    """List of problems (empty = valid)."""
    errs = []
    if not isinstance(data, dict):
        return ["top level must be an object"]
    if not is_int(data.get("schema")):
        errs.append("schema must be an integer")
    elif data["schema"] != 1:
        errs.append(f"unsupported schema {data['schema']} (this tool reads schema 1)")
    pr = data.get("priority")
    if pr is not None and not (is_int(pr) and 1 <= pr <= 999):
        errs.append("priority must be an integer 1..999 or empty")
    phases = data.get("phases")
    if not isinstance(phases, list):
        errs.append("phases must be a list")
        return errs
    seen = set()

    def check_node(node, where, parent=None):
        if not isinstance(node, dict):
            errs.append(f"{where}: must be an object")
            return
        nid = node.get("id")
        if not isinstance(nid, str) or not ID_RE.match(nid):
            errs.append(f"{where}: id must be letters, digits, . _ - (got {nid!r})")
        elif nid in seen:
            errs.append(f"{where}: duplicate id {nid}")
        else:
            seen.add(nid)
        label = nid if isinstance(nid, str) else where
        if not isinstance(node.get("name"), str) or not node["name"].strip():
            errs.append(f"{label}: name must be a non-empty string")
        if "evidence" in node and not isinstance(node["evidence"], str):
            errs.append(f"{label}: evidence must be a string")
        st = node.get("status")
        if st is not None and st not in STATUSES:
            errs.append(f"{label}: status {st!r} is not one of {', '.join(STATUSES)}")
        dates = {}
        for key in ("start", "end", "actual_start", "actual_end"):
            d = parse_date(node.get(key))
            if d is False:
                errs.append(f"{label}: {key} must be YYYY-MM-DD or empty (got {node.get(key)!r})")
            dates[key] = d or None
        if dates["start"] and dates["end"] and dates["end"] < dates["start"]:
            errs.append(f"{label}: end is before start")
        if dates["actual_start"] and dates["actual_end"] and dates["actual_end"] < dates["actual_start"]:
            errs.append(f"{label}: actual_end is before actual_start")
        if parent is not None:
            pd = {k: parse_date(parent.get(k)) or None for k in ("start", "end")}
            if dates["start"] and pd["start"] and dates["start"] < pd["start"]:
                errs.append(f"{label}: starts before its phase")
            if dates["end"] and pd["end"] and dates["end"] > pd["end"]:
                errs.append(f"{label}: ends after its phase")
        return dates

    for i, ph in enumerate(phases):
        check_node(ph, f"phases[{i}]")
        steps = ph.get("steps", []) if isinstance(ph, dict) else []
        if not isinstance(steps, list):
            errs.append(f"phases[{i}]: steps must be a list")
            continue
        for j, st in enumerate(steps):
            check_node(st, f"phases[{i}].steps[{j}]", ph)
    return errs


def file_hash(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def load(path):
    if not path.exists():
        raise Failure(f"{path} not found", 1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        raise Failure(f"{path} is not valid JSON: {e}", 2)
    return data


def load_valid(path):
    data = load(path)
    errs = validate(data)
    if errs:
        raise Failure("invalid plan file:\n  " + "\n  ".join(errs), 2)
    return data


def save_atomic(path, data):
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError as e:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise Failure(f"could not write {path}: {e}", 1)


def update(path, mutate):
    """Read, apply mutate(data), write only if the file did not change meanwhile; otherwise re-read and re-apply."""
    for _ in range(5):
        before = file_hash(path)
        data = load_valid(path)
        message = mutate(data)
        meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        meta.update({"updated_by": "kickoff plan.py", "updated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
        data["meta"] = meta
        errs = validate(data)
        if errs:
            raise Failure("change would make the plan invalid:\n  " + "\n  ".join(errs), 2)
        if file_hash(path) != before:
            continue
        save_atomic(path, data)
        return message
    raise Failure("the plan file keeps changing; try again in a moment", 1)


def nodes(data):
    for ph in data.get("phases", []):
        yield ph, None
        for st in ph.get("steps", []):
            yield st, ph


def find(data, nid):
    for node, parent in nodes(data):
        if node.get("id") == nid:
            return node, parent
    raise Failure(f"no phase or step with id {nid}", 1)


def status_of(node):
    return node.get("status") or "PLANNED"


def current(data):
    for ph in data.get("phases", []):
        if status_of(ph) not in ("DONE", "CUT"):
            step = next((s for s in ph.get("steps", []) if status_of(s) not in ("DONE", "CUT")), None)
            return ph, step
    return None, None


def next_items(data, count):
    out = []
    for ph in data.get("phases", []):
        if status_of(ph) in ("DONE", "CUT"):
            continue
        steps = [s for s in ph.get("steps", []) if status_of(s) not in ("DONE", "CUT")]
        for s in (steps or ([] if ph.get("steps") else [ph])):
            out.append((s, ph))
    # steps already IN_PROGRESS first, then plan order
    out.sort(key=lambda x: 0 if status_of(x[0]) == "IN_PROGRESS" else 1)
    return out[:count]


def order_keys(node):
    known = [k for k in KEY_ORDER if k in node]
    rest = [k for k in node if k not in KEY_ORDER]
    items = {k: node[k] for k in known + rest}
    node.clear()
    node.update(items)


def normalize_status(word):
    w = re.sub(r"[\s-]+", "_", word.strip().upper())
    w = ALIASES.get(w, w)
    if w not in STATUSES:
        raise Failure(f"unknown status {word!r}; use {', '.join(STATUSES)} (aliases: PASSED=DONE, WIP=IN_PROGRESS, ...)", 1)
    return w


def timing_notes(node, today):
    """Late or slipped, from planned and actual dates; never changes anything."""
    end, aend = parse_date(node.get("end")) or None, parse_date(node.get("actual_end")) or None
    st = status_of(node)
    if st == "DONE" and end and aend and aend > end:
        return f"slipped {(aend - end).days} day(s)"
    if st in ("PLANNED", "IN_PROGRESS", "BLOCKED") and end and today > end:
        return f"late {(today - end).days} day(s)"
    return ""


def span(node):
    s, e = node.get("start") or "", node.get("end") or ""
    return f"{s or '?'} to {e or '?'}" if (s or e) else "no dates"


def render_block(data, today):
    ph, st = current(data)
    steps = [n for n, p in nodes(data) if p is not None]
    done = sum(1 for s in steps if status_of(s) == "DONE")
    lines = [BLOCK_START, "## Where we are"]
    lines.append(f"- Phase: {ph['name']} ({status_of(ph)}), planned {span(ph)}" if ph else "- Phase: none open (all DONE or CUT)")
    lines.append(f"- Step: {st['name']} ({st['id']}, {status_of(st)})" if st else "- Step: none")
    lines.append(f"- Progress: {done} of {len(steps)} step(s) DONE")
    items = next_items(data, 3)
    if items:
        lines.append("- Next:")
        lines += [f"  {i}. {n['name']} ({n['id']}, {span(n)})" for i, (n, _) in enumerate(items, 1)]
    slips = [f"{n['name']} ({n['id']}): {note}" for n, _ in nodes(data) for note in [timing_notes(n, today)] if note]
    if slips:
        lines.append("- Timing:")
        lines += [f"  - {s}" for s in slips]
    if data.get("priority") is not None:
        lines.append(f"- Priority: {data['priority']}")
    lines.append(BLOCK_END)
    return "\n".join(lines) + "\n"



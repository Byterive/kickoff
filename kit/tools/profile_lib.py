"""Profile families for kickoff (stdlib only): a secondary profile says `extends: <main>` in its frontmatter.

Lookup per name (first hit wins): <root>/.kickoff/profile.md (top level only), <root>/.kickoff/profiles/<name>.md,
~/.claude/kickoff/profiles/<name>/profile.md, then <kit>/profiles/<name>.md for each kit folder given.
Old names stay valid through ALIASES. Sections: a secondary's section replaces the main's, except MERGED
sections, which are joined main first. Used by plan.py, proj_toggle.py, check_budgets.py, upgrade.py, vscode_ext.py.
"""
import hashlib
import re
from pathlib import Path

ALIASES = {"go-backend": "backend-go"}
MERGED = ("never do", "known pitfalls", "vs code", "companion plugins")
MAX_DEPTH = 3
CRLF, LF, SEP = bytes([13, 10]), bytes([10]), bytes([0])
EXTENDS = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---", re.S)


def canonical(name):
    return ALIASES.get(name, name)


def find(name, root, kits, top=True):
    """Path of the profile file for one name, or None."""
    name = canonical(name)
    root = Path(root)
    cands = [root / ".kickoff" / "profile.md"] if top else []
    cands += [root / ".kickoff" / "profiles" / f"{name}.md",
              Path.home() / ".claude" / "kickoff" / "profiles" / name / "profile.md"]
    cands += [Path(k) / "profiles" / f"{name}.md" for k in kits]
    for c in cands:
        if c.exists():
            return c
    return None


def parent_of(path):
    m = EXTENDS.match(Path(path).read_text(encoding="utf-8"))
    if m:
        e = re.search(r"^extends[ \t]*:[ \t]*(\S+)", m.group(1), re.M)
        if e:
            return canonical(e.group(1).strip("\"'"))
    return None


def lineage(name, root, kits):
    """[(name, path)] from the main profile down to the named one. A missing parent is skipped."""
    out, seen, cur, top = [], set(), canonical(name), True
    while cur and cur not in seen and len(out) < MAX_DEPTH:
        seen.add(cur)
        p = find(cur, root, kits, top)
        if not p:
            break
        out.insert(0, (cur, p))
        cur, top = parent_of(p), False
    return out


def section(paths, heading):
    """Text of '## heading' for a lineage's paths (main first): merged for MERGED headings, else the most specific one."""
    pat = re.compile(rf"^##[ \t]+{re.escape(heading)}\b[^\n]*\n(.*?)(?=^##[ \t]|\Z)", re.S | re.M | re.I)
    found = [m.group(1).strip("\n") for p in paths
             for m in [pat.search(Path(p).read_text(encoding="utf-8"))] if m and m.group(1).strip()]
    if not found:
        return ""
    return "\n".join(found) if heading.lower() in MERGED else found[-1]


def bullets(text):
    return [l.strip()[2:].strip() for l in text.splitlines() if l.strip().startswith(("- ", "* "))]


def subsection(text, name):
    """Bodies of every '### name' block in text (a merged section repeats its blocks), joined."""
    pat = re.compile(rf"^###[ \t]+{re.escape(name)}\b[^\n]*\n(.*?)(?=^###[ \t]|\Z)", re.S | re.M | re.I)
    return "\n".join(m.group(1) for m in pat.finditer(text))


def fingerprint(name, root, kits):
    """Hash of the profile files of a lineage (line endings ignored); empty when the profile is not found."""
    parts = [Path(p).read_bytes().replace(CRLF, LF) for _, p in lineage(name, root, kits)]
    return hashlib.sha256(SEP.join(parts)).hexdigest() if parts else ""

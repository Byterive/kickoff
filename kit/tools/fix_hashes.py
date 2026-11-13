#!/usr/bin/env python3
"""Fix commit-hash references after a git history rewrite (stdlib only). Dry run unless --apply.

  fix_hashes.py [project_root] --map FILE [--apply]
      Replace old commit hashes with new ones in NEXT.md, PROJECT_STATUS.md, DECISIONS.md, REQUIREMENTS.md and
      .guidebook/state.json. A short hash (7 to 40 characters) is replaced by the same-length prefix of the new hash.
      A short hash that matches more than one old commit is left alone and reported.
  fix_hashes.py --make-map REPO --old-ref REF --new-ref REF [--out FILE]
      Build the old-to-new map for a rewrite that only changed commit metadata (same commits, same order, same trees):
      git filter-branch keeps the old branch under refs/original/refs/heads/<branch>. Counts, trees and subjects must match.

Map file: one "OLD NEW" pair (40-character hashes) per line, or a JSON object {old: new}.
This tool never rewrites history; it only edits the text files above.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

FILES = ("NEXT.md", "PROJECT_STATUS.md", "DECISIONS.md", "REQUIREMENTS.md", ".guidebook/state.json")
TOKEN = re.compile(r"\b[0-9a-f]{7,40}\b")


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def read_map(path):
    text = Path(path).read_text(encoding="utf-8")
    if text.lstrip().startswith("{"):
        pairs = json.loads(text)
    else:
        pairs = dict(line.split()[:2] for line in text.splitlines() if line.strip() and not line.startswith("#"))
    return {o.lower(): n.lower() for o, n in pairs.items()}


def make_map(repo, old_ref, new_ref, out):
    old = git(repo, "log", "--reverse", "--format=%H|%T|%s", old_ref).splitlines()
    new = git(repo, "log", "--reverse", "--format=%H|%T|%s", new_ref).splitlines()
    if len(old) != len(new):
        sys.exit(f"cannot pair commits: {len(old)} on {old_ref} but {len(new)} on {new_ref}")
    lines = []
    for a, b in zip(old, new):
        ha, ta, sa = a.split("|", 2)
        hb, tb, sb = b.split("|", 2)
        if ta != tb or sa != sb:
            sys.exit(f"cannot pair {ha[:7]} with {hb[:7]}: tree or subject differs (not a metadata-only rewrite)")
        lines.append(f"{ha} {hb}")
    text = "\n".join(lines) + "\n"
    if out:
        Path(out).write_text(text, encoding="utf-8", newline="\n")
        print(f"{len(lines)} pair(s) written to {out}")
    else:
        sys.stdout.write(text)


def fix(root, mapping, apply):
    changed = 0
    for rel in FILES:
        fp = root / rel
        if not fp.exists():
            continue
        raw = fp.read_bytes().decode("utf-8")
        edits, skipped = [], []

        def repl(m):
            tok = m.group(0)
            if not re.search(r"\d", tok) or not re.search(r"[a-f]", tok):
                return tok
            hits = [o for o in mapping if o.startswith(tok)]
            if len(hits) == 1:
                new = mapping[hits[0]][:len(tok)]
                edits.append((tok, new))
                return new
            if len(hits) > 1:
                skipped.append(tok)
            return tok

        out = TOKEN.sub(repl, raw)
        for tok in sorted(set(skipped)):
            print(f"{rel}: {tok} matches more than one old commit; left alone")
        if edits:
            changed += len(edits)
            print(f"{rel}: " + ", ".join(f"{a} -> {b}" for a, b in sorted(set(edits))) + f" ({len(edits)} reference(s))")
            if apply:
                fp.write_bytes(out.encode("utf-8"))
    print(("Applied: " if apply else "Dry run: ") + f"{changed} reference(s) " + ("fixed." if apply else "would change. Re-run with --apply."))


def main():
    a = sys.argv[1:]

    def opt(name):
        return a[a.index(name) + 1] if name in a else None

    if "--make-map" in a:
        if not (opt("--old-ref") and opt("--new-ref")):
            sys.exit("--make-map needs --old-ref and --new-ref")
        return make_map(opt("--make-map"), opt("--old-ref"), opt("--new-ref"), opt("--out"))
    if not opt("--map"):
        sys.exit(__doc__)
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] != "--map")]
    fix(Path(pos[0]).resolve() if pos else Path.cwd(), read_map(opt("--map")), "--apply" in a)


main()

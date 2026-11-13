"""Helpers for upgrade.py: guess the status sections (How to run, Setup, Data, Troubleshooting) from the repo, and
edit the frontmatter of status files (stdlib only)."""
import re
from pathlib import Path

FM = re.compile(r"\A(---[ \t]*\r?\n)(.*?)(\r?\n---[ \t]*(?:\r?\n|\Z))", re.S)


def missing_keys(path, keys):
    """Keys absent from the file's frontmatter; None when there is no file or no frontmatter."""
    if not path.exists():
        return None
    m = FM.match(path.read_text(encoding="utf-8"))
    if not m:
        return None
    return [k for k in keys if not re.search(rf"^{k}[ \t]*:", m.group(2), re.M)]


def frontmatter_with_keys(path, keys):
    """The file text with the given empty keys appended to its frontmatter."""
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    nl = "\r\n" if "\r\n" in m.group(1) else "\n"
    block = m.group(2) + nl + nl.join(f"{k}:" for k in keys)
    return m.group(1) + block + text[m.end(2):]


def readme_section(root, names, max_lines=6):
    for fname in ("README.md", "readme.md"):
        rp = root / fname
        if not rp.exists():
            continue
        lines = rp.read_text(encoding="utf-8", errors="ignore").splitlines()
        for i, line in enumerate(lines):
            m = re.match(r"^#{1,4}\s*(.+?)\s*$", line)
            if m and any(re.search(n, m.group(1), re.I) for n in names):
                body = []
                for l2 in lines[i + 1:]:
                    if re.match(r"^#{1,4}\s", l2):
                        break
                    if l2.strip() and not l2.strip().startswith("```"):
                        body.append(l2.rstrip())
                    if len(body) >= max_lines:
                        break
                if body:
                    return fname, m.group(1), body
    return None


def quote(source, heading, body):
    return f'GUESSED (from {source}, "{heading}"; confirm at the next wrap-up):\n' + "\n".join("> " + b for b in body)


def guess_sections(root):
    out = {}
    verify = []
    cm = root / "CLAUDE.md"
    if cm.exists():
        for line in cm.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.match(r"^-\s*(Build|Test|Lint/format|Run)\s*:\s*(.+)$", line)
            if m and not m.group(2).strip().upper().startswith("UNKNOWN"):
                verify.append(f"> {m.group(1)}: {m.group(2).strip()}")
    rs = readme_section(root, ["usage", "run", "quick ?start", "getting started"])
    if verify or rs:
        parts = []
        if verify:
            parts.append('GUESSED (from CLAUDE.md "How to verify"; confirm at the next wrap-up):\n' + "\n".join(verify))
        if rs:
            parts.append(quote(*rs))
        out["How to run"] = "\n\n".join(parts)
    rs = readme_section(root, ["install", "setup", "set up", "requirements", "prerequisites"])
    if rs:
        out["Setup"] = quote(*rs)
    data_dirs = [d for d in ("data", "Data", "datasets") if (root / d).is_dir()]
    loaders = sorted({str(q.relative_to(root)).replace("\\", "/") for pat in ("*download*", "*fetch*")
                      for base in (root, root / "scripts", root / "tools") if base.is_dir() for q in base.glob(pat)
                      if q.is_file() and q.suffix in (".py", ".sh", ".ps1", ".js", ".ts")})[:5]
    if data_dirs or loaders:
        lines = []
        if data_dirs:
            lines.append("> folder present: " + ", ".join(d + "/" for d in data_dirs))
        if loaders:
            lines.append("> possible downloader (check its --help for parameters): " + ", ".join(loaders))
        out["Data"] = "GUESSED (from the folder layout; confirm sources, paths and how to obtain them at the next wrap-up):\n" + "\n".join(lines)
    rs = readme_section(root, ["troubleshoot", "faq", "common problems", "known issues"], 8)
    if rs:
        out["Troubleshooting"] = quote(*rs)
    return out

#!/usr/bin/env python3
"""PreToolUse hook (Bash and PowerShell): block recursive forced deletes.

Reads the hook JSON on stdin. Exit 2 (message on stderr) blocks the call so Claude must ask the user
first. Otherwise exit 0.

Only a deleter in command position counts (rm, Remove-Item, ri, del, rmdir, rd, erase at the start of a
command, or after ; && || | ( or a newline), with both a recursive and a force flag. Text inside quotes,
heredoc bodies, PowerShell here-strings and commit messages is never treated as a command, so echo, grep and
git commit messages that merely mention a delete pass. These still count: sh -c / bash -c / powershell -Command
strings, eval, $( ) and backtick substitutions, and rm after xargs or find -exec. If the command cannot be parsed
(for example unbalanced quotes) the old behaviour applies: any rm -rf style text blocks.
"""
# This hook only READS the command text and blocks it; it never runs, evals or deletes anything.
# "rm -rf" below appears in comments and the block message only.
import os as _os
import sys as _sys
if "rmrf" in _os.environ.get("KICKOFF_DISABLED_HOOKS", "").split(","):
    _sys.exit(0)
import json
import re
import sys

DELETERS = {"rm", "remove-item", "ri", "del", "rmdir", "rd", "erase"}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "fish", "powershell", "pwsh", "cmd"}
WRAPPERS = {"sudo", "doas", "command", "builtin", "exec", "nohup", "time", "env", "nice", "then", "do", "else",
            "elif", "if", "while", "until", "!", "{"}
SEPARATORS = ";|&\n()"
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def strip_blocks(text):
    """Remove heredoc bodies and PowerShell here-strings (their text is data, not commands)."""
    text = re.sub(r"@'[ \t]*\r?\n.*?\r?\n'@", "''", text, flags=re.S)
    text = re.sub(r'@"[ \t]*\r?\n.*?\r?\n"@', '""', text, flags=re.S)
    out, pos = [], 0
    pattern = re.compile(r"<<-?[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
    while True:
        m = pattern.search(text, pos)
        if not m:
            out.append(text[pos:])
            break
        eol = text.find("\n", m.end())
        if eol == -1:
            out.append(text[pos:])
            break
        out.append(text[pos:eol + 1])
        tag, i = m.group(2), eol + 1
        end = None
        while i <= len(text):
            nl = text.find("\n", i)
            line = text[i:nl if nl != -1 else len(text)]
            if line.strip() == tag:
                end = i
                break
            if nl == -1:
                break
            i = nl + 1
        pos = end if end is not None else len(text)
    return "".join(out)


def tokenize(text):
    """Split into commands (lists of tokens). Quoted text joins into its token. Also returns substitutions found
    inside double quotes ($( ) and backticks) so they can be inspected as commands."""
    commands, tokens, cur = [], [], None
    subs = []
    i, n = 0, len(text)

    def flush_token():
        nonlocal cur
        if cur is not None:
            tokens.append(cur)
            cur = None

    def flush_command():
        nonlocal tokens
        flush_token()
        if tokens:
            commands.append(tokens)
        tokens = []

    while i < n:
        c = text[i]
        if c == "'":
            j = text.find("'", i + 1)
            if j == -1:
                raise ValueError("unbalanced quote")
            cur = (cur or "") + text[i + 1:j]
            i = j + 1
        elif c == '"':
            j, buf = i + 1, []
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j + 1])
                    j += 2
                    continue
                buf.append(text[j])
                j += 1
            if j >= n:
                raise ValueError("unbalanced quote")
            body = "".join(buf)
            for m in re.finditer(r"\$\(([^()]*)\)|`([^`]*)`", body):
                subs.append(m.group(1) or m.group(2) or "")
            cur = (cur or "") + body
            i = j + 1
        elif c == "\\" and i + 1 < n:
            cur = (cur or "") + text[i + 1]
            i += 2
        elif c in SEPARATORS:
            flush_command()
            i += 1
        elif c in " \t\r":
            flush_token()
            i += 1
        else:
            cur = (cur or "") + c
            i += 1
    flush_command()
    return commands, subs


def classify(tokens):
    """Return (recursive, force) from option tokens of a deleter."""
    rec = force = False
    for t in tokens:
        low = t.lower()
        if low.startswith("--"):
            rec = rec or low.startswith("--recursive")
            force = force or low.startswith("--force")
        elif low.startswith("-") and len(low) > 1:
            name = low[1:].split(":")[0]
            if name.startswith("rec"):
                rec = True
            elif name.startswith("fo") and not set(name) <= set("rfivdx"):
                force = True
            elif set(name) <= set("rfivdix") and name:
                rec = rec or "r" in name
                force = force or "f" in name
    return rec, force


def base(word):
    w = word.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return w[:-4] if w.endswith(".exe") else w


def dangerous(text, depth=0):
    if depth > 4:
        return False
    commands, subs = tokenize(strip_blocks(text))
    for s in subs:
        if dangerous(s, depth + 1):
            return True
    for tokens in commands:
        i, wrapped = 0, False
        while i < len(tokens) and (ASSIGN.match(tokens[i]) or base(tokens[i]) in WRAPPERS):
            wrapped = wrapped or base(tokens[i]) in ("sudo", "doas", "env", "nice", "nohup", "time")
            i += 1
            while i < len(tokens) and tokens[i].startswith("-") and base(tokens[i - 1]) in WRAPPERS:
                i += 1
        if i >= len(tokens):
            continue
        word, rest = base(tokens[i]), tokens[i + 1:]
        if wrapped and word not in DELETERS and word not in SHELLS:
            # options of the wrapper may hide the real command (sudo -u root rm -rf x): look for a deleter
            for k, t in enumerate(tokens[i:], i):
                if base(t) in DELETERS and all(classify(tokens[k + 1:])):
                    return True
        if word in DELETERS:
            rec, force = classify(rest)
            if rec and force:
                return True
        elif word in SHELLS:
            for k, t in enumerate(rest):
                if t.lower() in ("-c", "-lc", "-ic", "-command", "-c:", "/c", "-encodedcommand") and k + 1 < len(rest):
                    if dangerous(" ".join(rest[k + 1:]), depth + 1):
                        return True
        elif word == "eval":
            if dangerous(" ".join(rest), depth + 1):
                return True
        elif word in ("xargs", "find"):
            for k, t in enumerate(rest):
                if base(t) in DELETERS:
                    rec, force = classify(rest[k + 1:])
                    if rec and force:
                        return True
    return False


def old_match(cmd):
    rm = re.compile(
        r"\brm\s+(?:-[a-zA-Z]*\s+)*(?:-[a-zA-Z]*[rR][a-zA-Z]*[fF]|-[a-zA-Z]*[fF][a-zA-Z]*[rR]"
        r"|--recursive\b.*--force\b|--force\b.*--recursive\b|-[rR]\b.*\s-f\b|-f\b.*\s-[rR]\b)")
    ps = re.compile(r"\b(?:Remove-Item|ri|rm|del|rmdir)\b[^|;&]*-Recurse\b[^|;&]*-Force\b"
                    r"|\b(?:Remove-Item|ri|rm|del|rmdir)\b[^|;&]*-Force\b[^|;&]*-Recurse\b", re.I)
    return bool(rm.search(cmd) or ps.search(cmd))


def main():
    try:
        cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except Exception:
        return 0
    try:
        blocked = dangerous(cmd)
    except Exception:
        blocked = old_match(cmd)
    if blocked:
        sys.stderr.write("Blocked: recursive forced delete (rm -rf / Remove-Item -Recurse -Force). "
                         "Show the user exactly what would be deleted and get an explicit yes first.\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

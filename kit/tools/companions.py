#!/usr/bin/env python3
"""List a profile's companion plugins and whether each is installed and on here (read-only, stdlib only).

Usage: python companions.py [project_root] --profile NAME [--json]
Reads '## Companion plugins' of the profile (and of the main profile it extends). Each bullet is
`name: role | when: ... | command: ...`. Prints the install command for a missing plugin when its marketplace is known
(from ~/.claude/kickoff/config.json {"marketplaces": {"plugin": "marketplace"}}, else from any installed copy);
otherwise it says UNKNOWN. It never installs anything: the install runs only after the user agrees.
Marketplace names stay on this machine; profiles hold plugin names only."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import profile_lib  # noqa: E402

home = Path.home() / ".claude"


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def companions(profile, root, kits):
    paths = [p for _, p in profile_lib.lineage(profile, root, kits)]
    out = []
    for line in profile_lib.bullets(profile_lib.section(paths, "Companion plugins")):
        head, *rest = [x.strip() for x in line.split(" | ")]
        name, _, role = head.partition(":")
        info = {"name": name.strip(), "role": role.strip()}
        for r in rest:
            k, _, v = r.partition(":")
            info[k.strip()] = v.strip()
        out.append(info)
    return out


def status(profile, root, kits):
    """[{name, role, when, command, state, install}] for the profile's companion plugins; state is missing, installed or installed, off here."""
    items = companions(profile, root, kits)
    installed = list(load(home / "plugins" / "installed_plugins.json").get("plugins", {}))
    cfg = load(home / "kickoff" / "config.json").get("marketplaces", {})
    enabled = {}
    for f in (home / "settings.json", root / ".claude" / "settings.json", root / ".claude" / "settings.local.json"):
        enabled.update(load(f).get("enabledPlugins", {}))
    rows = []
    for it in items:
        full = next((i for i in installed if i.split("@")[0] == it["name"]), None)
        market = cfg.get(it["name"]) or (full.split("@")[1] if full and "@" in full else None)
        off = full is not None and enabled.get(full) is False
        state = "missing" if not full else ("installed, off here" if off else "installed")
        cmd = None
        if state == "missing":
            cmd = f"claude plugin install {it['name']}@{market}" if market else "marketplace UNKNOWN: add it to ~/.claude/kickoff/config.json"
        rows.append({**it, "state": state, "install": cmd})
    return rows


def main():
    a = sys.argv[1:]
    profile = a[a.index("--profile") + 1] if "--profile" in a else None
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] != "--profile")]
    root = Path(pos[0]).resolve() if pos else Path.cwd()
    if not profile:
        sys.exit("give --profile NAME")
    rows = status(profile, root, [HERE.parent])
    if "--json" in a:
        print(json.dumps(rows, indent=2))
        return
    if not rows:
        print(f"profile {profile}: no companion plugins listed")
    for r in rows:
        print(f"{r['name']}: {r['state']} ({r['role']})" + (f"\n  install after approval: {r['install']}" if r["install"] else ""))
        if r["state"] != "installed" and r.get("when"):
            print(f"  when: {r['when']}")


if __name__ == "__main__":
    main()

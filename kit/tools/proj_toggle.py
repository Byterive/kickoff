#!/usr/bin/env python3
"""Turn plugins and skills on or off for the current project (.claude/settings.local.json, which git ignores, so your plugin choices
and private marketplace names stay out of the repo; the shared .claude/settings.json is only read).

  proj_toggle.py list
  proj_toggle.py off|on <plugin|skill> [...]
  proj_toggle.py pick                       interactive checklist (terminal)
  proj_toggle.py preset <profile> [--tier minimal|recommended|full]
  proj_toggle.py find <term>                search plugins and skills by name/description
  proj_toggle.py localize                   move toggles from the shared settings.json into settings.local.json
  proj_toggle.py undo                       restore settings.local.json.bak
  add --dry-run to off/on/preset/pick to preview without writing

Plugins match installed plugins (name or name@marketplace; account-synced ones are name@synced)
and go to enabledPlugins. Any other name is a skill: written as a Skill(<name>) deny rule
(use 'plugin:*' for a whole plugin). A denied skill stays listed but cannot run.
Presets: <project>/.kickoff/presets/<p>.json, ~/.claude/kickoff/profiles/<p>/preset.json,
then the kit's presets/<p>.json (kit found via CLAUDE_PLUGIN_ROOT, this script, or .kickoff/kit_path). Format: {"keep": ["plugin-name", ...]}.
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

home = Path.home() / ".claude"
shared = Path.cwd() / ".claude" / "settings.json"
proj = Path.cwd() / ".claude" / "settings.local.json"


def find_kit():
    """The kickoff kit folder (has presets/): CLAUDE_PLUGIN_ROOT, then this script's own kit/, then
    <project>/.kickoff/kit_path (a path to the kit or plugin folder). None when none of them has presets/."""
    cands = []
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if root:
        cands.append(Path(root) / "kit")
    cands.append(Path(__file__).resolve().parent.parent)
    try:
        cands.append(Path((Path.cwd() / ".kickoff" / "kit_path").read_text(encoding="utf-8").strip()))
    except OSError:
        pass
    for c in cands:
        for d in (c, c / "kit"):
            if (d / "presets").is_dir():
                return d
    return None


kit = find_kit()
sys.path.insert(0, str(Path(__file__).resolve().parent))
import profile_lib  # noqa: E402


def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def installed():
    return list(load(home / "plugins" / "installed_plugins.json").get("plugins", {}))


def synced():
    """Account-synced plugins (claude.ai) load as <name>@synced, outside settings.json."""
    out = set()
    for f in (home / "plugins" / "synced").glob("*/*/.claude-plugin/plugin.json"):
        n = load(f).get("name")
        if n:
            out.add(f"{n}@synced")
    return out


def inherited():
    """enabledPlugins from the user settings, then the project's shared settings.json (read only)."""
    return {**load(home / "settings.json").get("enabledPlugins", {}), **load(shared).get("enabledPlugins", {})}


def all_plugins(s):
    return sorted(synced() | set(installed()) | set(inherited()) | set(s.get("enabledPlugins", {})))


def resolve_plugin(name, s):
    return next((k for k in all_plugins(s) if k == name or k.split("@")[0] == name), None)


def write(s, dry):
    perms = s.get("permissions", {})
    if not perms.get("deny"):
        perms.pop("deny", None)
    if not perms:
        s.pop("permissions", None)
    if not s.get("enabledPlugins"):
        s.pop("enabledPlugins", None)
    if dry:
        print("(dry run: nothing written)")
        return
    proj.parent.mkdir(exist_ok=True)
    if proj.exists():
        shutil.copy2(proj, proj.with_name("settings.local.json.bak"))
    proj.write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")
    print("Saved (backup: settings.local.json.bak, restore with 'undo'). Start a new session; "
          "in a terminal /reload-plugins also works.")


def cmd_list(s):
    user = load(home / "settings.json").get("enabledPlugins", {})
    sh = load(shared).get("enabledPlugins", {})
    plugins = s.get("enabledPlugins", {})
    for k in all_plugins(s):
        st = plugins.get(k, sh.get(k, user.get(k)))
        src = "project" if k in plugins or k in sh else "user" if k in user else "default"
        print(f"{'?  ' if st is None else 'ON ' if st else 'OFF'} {k}  ({src})")
    for r in load(shared).get("permissions", {}).get("deny", []) + s.get("permissions", {}).get("deny", []):
        if r.startswith("Skill("):
            print(f"OFF skill {r[6:-1]}  (project)")


def cmd_toggle(s, on, names):
    plugins = s.setdefault("enabledPlugins", {})
    deny = s.setdefault("permissions", {}).setdefault("deny", [])
    for n in names:
        key = resolve_plugin(n, s)
        if key:
            plugins[key] = on
            print(f"plugin {key}: {'enabled' if on else 'disabled'}")
            continue
        rule = f"Skill({n})"
        if on and rule in deny:
            deny.remove(rule)
        elif not on and rule not in deny:
            deny.append(rule)
        print(f"skill {n}: {'enabled' if on else 'disabled (blocked from running)'}")


def cmd_pick(s):
    user = inherited()
    plugins = s.setdefault("enabledPlugins", {})
    keys = all_plugins(s)
    state = {k: plugins.get(k, user.get(k, True)) for k in keys}
    while True:
        for i, k in enumerate(keys, 1):
            print(f"{i:>3}. [{'x' if state[k] else ' '}] {k}")
        a = input("Numbers to flip (e.g. 1 4 7), 'off' = all off, Enter = save, q = quit: ").strip()
        if a == "q":
            return False
        if a == "":
            break
        if a == "off":
            state = dict.fromkeys(keys, False)
        for x in a.split():
            if x.isdigit() and 0 < int(x) <= len(keys):
                state[keys[int(x) - 1]] ^= True
    for k in keys:
        if state[k] != plugins.get(k, user.get(k, True)):
            plugins[k] = state[k]
    return True


def preset_file(profile):
    """Preset of the profile, else of the main profile it extends (profile_lib), else None."""
    kits = [kit] if kit else []
    names = [n for n, _ in reversed(profile_lib.lineage(profile, Path.cwd(), kits))] or [profile_lib.canonical(profile)]
    for name in names:
        for p in (Path.cwd() / ".kickoff" / "presets" / f"{name}.json",
                  home / "kickoff" / "profiles" / name / "preset.json",
                  (kit / "presets" / f"{name}.json") if kit else Path("/nonexistent")):
            if p.exists():
                return p
    return None


def always_keep():
    """Plugins every project keeps: the project's .kickoff/presets/_always.json, else the kit's. No silent default."""
    for p in (Path.cwd() / ".kickoff" / "presets" / "_always.json",
              (kit / "presets" / "_always.json") if kit else Path("/nonexistent")):
        if p.exists():
            extra = load(home / "kickoff" / "always.json").get("keep", []) if (home / "kickoff" / "always.json").exists() else []
            return list(dict.fromkeys(load(p).get("keep", []) + extra))  # ~/.claude/kickoff/always.json adds your own, per machine
    sys.exit("Cannot find the kickoff kit presets (_always.json). Set CLAUDE_PLUGIN_ROOT to the plugin folder, "
             "put the kit path in .kickoff/kit_path, or run /kickoff:upgrade to copy the presets into .kickoff/presets/.")


def cmd_preset(s, profile, tier):
    always = always_keep() if tier != "full" else []
    f = preset_file(profile)
    if tier == "recommended" and not f:
        sys.exit(f"No preset for profile '{profile}'. Create one via /kickoff:kickoff (custom profile) "
                 f"or use --tier minimal|full.")
    keep = set(always) | (set(load(f).get("keep", [])) if tier == "recommended" else set())
    plugins = s.setdefault("enabledPlugins", {})
    for k in all_plugins(s):
        if tier == "full":
            if plugins.get(k) is False:
                plugins[k] = True
                print(f"on   {k}")
        elif k.split("@")[0] in keep:
            print(f"keep {k}")
        else:
            plugins[k] = False
            print(f"off  {k}")


def skills_index():
    roots = [home / "plugins" / "cache", home / "plugins" / "synced", home / "skills",
             Path.cwd() / ".claude" / "skills"]
    seen = {}
    for r in roots:
        for f in (r.glob("**/SKILL.md") if r.exists() else []):
            plugin = "(standalone)"
            for up in f.parents:
                pj = up / ".claude-plugin" / "plugin.json"
                if pj.exists():
                    plugin = load(pj).get("name", plugin)
                    break
            head = f.read_text(encoding="utf-8", errors="ignore")[:1500]
            n = re.search(r"^name:\s*(.+)$", head, re.M)
            d = re.search(r"^description:\s*(.+)$", head, re.M)
            name = (n.group(1) if n else f.parent.name).strip()
            seen[(plugin, name)] = d.group(1).strip() if d else ""
    return seen


def cmd_find(term):
    t = term.lower()
    hits = [(p, n, d) for (p, n), d in sorted(skills_index().items())
            if t in p.lower() or t in n.lower() or t in d.lower()]
    for p, n, d in hits[:30]:
        print(f"{p}:{n} - {d[:90]}")
    print(f"{len(hits)} match(es)" + (" (first 30 shown)" if len(hits) > 30 else ""))


def cmd_localize(s, dry):
    """Move enabledPlugins and Skill() deny rules from the shared settings.json into settings.local.json."""
    sh = load(shared)
    plugins = sh.get("enabledPlugins", {})
    deny = sh.get("permissions", {}).get("deny", [])
    skills = [r for r in deny if r.startswith("Skill(")]
    if not plugins and not skills:
        return print("Nothing to move: settings.json has no plugin toggles.")
    s.setdefault("enabledPlugins", {})
    for k, v in plugins.items():
        s["enabledPlugins"].setdefault(k, v)
    if skills:
        d = s.setdefault("permissions", {}).setdefault("deny", [])
        d.extend(r for r in skills if r not in d)
    print(f"Moving {len(plugins)} plugin toggle(s) and {len(skills)} skill rule(s) to settings.local.json:")
    for k in plugins:
        print(f"  {k}")
    if dry:
        return print("(dry run: nothing written)")
    sh.pop("enabledPlugins", None)
    if skills:
        sh["permissions"]["deny"] = [r for r in deny if r not in skills]
    shutil.copy2(shared, shared.with_name("settings.json.bak"))
    write(s, False)
    shared.write_text(json.dumps(sh, indent=2) + chr(10), encoding="utf-8")
    print("The shared settings.json no longer lists them. Commit that change to stop tracking the plugin names.")


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    tier = "recommended"
    if "--tier" in args:
        i = args.index("--tier")
        tier = args[i + 1]
        del args[i:i + 2]
    args = [a for a in args if a != "--dry-run"]
    cmd, names = (args[0] if args else "list"), args[1:]
    s = load(proj)
    if cmd == "list":
        return cmd_list(s)
    if cmd == "find" and names:
        return cmd_find(" ".join(names))
    if cmd == "undo":
        bak = proj.with_name("settings.local.json.bak")
        if not bak.exists():
            sys.exit("No backup to restore.")
        shutil.copy2(bak, proj)
        return print("Restored settings.local.json from settings.local.json.bak.")
    if cmd == "localize":
        return cmd_localize(s, dry)
    if cmd == "pick":
        if not cmd_pick(s):
            return
    elif cmd == "preset" and names:
        cmd_preset(s, names[0], tier)
    elif cmd in ("on", "off") and names:
        cmd_toggle(s, cmd == "on", names)
    else:
        sys.exit(__doc__)
    write(s, dry)


main()

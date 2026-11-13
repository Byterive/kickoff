"""Extra doctor checks (stdlib only): profile changed since setup, companion plugins, missing profile_lib.py.
checks(root, kit) returns [(level, message)] with level OK, WARN or INFO."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import companions  # noqa: E402
import profile_lib  # noqa: E402


def checks(root, kit):
    root, out = Path(root), []
    tools = root / "tools"
    if any((tools / t).exists() for t in ("proj_toggle.py", "plan.py", "check_budgets.py")) and not (tools / "profile_lib.py").exists():
        out.append(("WARN", "tools/ has kit tools but no profile_lib.py: run /kickoff:upgrade --refresh-tools (profile families need it)"))
    try:
        stamp = json.loads((root / ".kickoff" / "profile.stamp.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return out + [("INFO", "no profile stamp (.kickoff/profile.stamp.json): /kickoff:upgrade --profile NAME --apply records which profile version this project uses")]
    name = stamp.get("profile", "")
    now = profile_lib.fingerprint(name, root, [kit])
    if not now:
        out.append(("WARN", f"profile '{name}' recorded at setup was not found in the kit"))
    elif now != stamp.get("fingerprint"):
        out.append(("WARN", f"profile '{name}' changed in the kit since this project was set up (kit {stamp.get('kit_version', 'UNKNOWN')} then): review it, then /kickoff:upgrade --profile {name} --apply to record the new version"))
    else:
        out.append(("OK", f"profile '{name}' unchanged since setup"))
    for r in companions.status(name, root, [kit]):
        if r["state"] != "installed":
            out.append(("WARN", f"companion plugin {r['name']} is {r['state']} ({r['role']}); {r['install'] or 'turn it on with /kickoff:plugins'}"))
    return out

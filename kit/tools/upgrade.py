#!/usr/bin/env python3
"""Bring an existing kickoff project up to the current kit (lists first, writes only with --apply).

Usage: python upgrade.py [project_root] [--apply] [--profile NAME] [--guide none|local] [--refresh-tools]
                         [--fields none|fields|plan] [--sections yes|no] [--clarity yes|no]
Adds what is missing and never overwrites: DECISIONS.md, NEXT.md, tools/doctor.py, tools/proj_toggle.py,
.kickoff/presets/ and .kickoff/profiles/ (the always-keep list, the profile's preset and profile file, so the tools work without the plugin folder),
.kickoff/kit/ (copies of CLAUDE_INSTRUCTIONS.md and WRAPUP_PROMPT.md that CLAUDE.md points to; a copy is refreshed
only while it is unchanged since the kit wrote it, otherwise it is reported),
.gitignore / .gitattributes (appends missing lines only), .kickoff/guide.json (only with --guide local),
optional tracking fields (only with --fields; see kit/FIELDS_CONTRACT.md; the choice is stored in
.kickoff/fields.json so later runs do not ask again). Tier plan adds .kickoff/plan.json (from templates/plan.template.json)
and tools/plan.py.
Status sections (--sections yes): adds the headings How to run, Setup, Data and Troubleshooting to PROJECT_STATUS.md where
missing, pre-filled from the README, CLAUDE.md and the repo and marked GUESSED (nothing existing is changed).
Clarity rule (on by default, --clarity no to opt out): appends a marked block to CLAUDE.md and creates REQUIREMENTS.md
(templates/clarity-rule.md, templates/REQUIREMENTS.template.md). Both choices are stored in .kickoff/options.json.
Plugin sets and settings.json are not touched (use /plugins).
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import profile_lib
from upgrade_lib import frontmatter_with_keys, guess_sections, missing_keys

KIT = Path(__file__).resolve().parent.parent
a = sys.argv[1:]
apply = "--apply" in a


def opt(name, default=None):
    return a[a.index(name) + 1] if name in a else default


args = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--profile", "--guide", "--fields", "--sections", "--clarity"))]
root = Path(args[0]).resolve() if args else Path.cwd()
profile, guide = opt("--profile"), opt("--guide", "none")
family = profile_lib.lineage(profile, root, [KIT]) if profile else []  # [(name, path)] main first; old names resolve through ALIASES
fields_req = opt("--fields")
TIERS = ("none", "fields", "plan")
if fields_req not in (None, *TIERS):
    sys.exit("--fields must be none, fields or plan")
todo = []


def detect_eol():
    """Line ending of the project: CLAUDE.md first, then .gitattributes (eol=crlf / eol=lf), else LF."""
    cm = root / "CLAUDE.md"
    if cm.exists():
        return "\r\n" if b"\r\n" in cm.read_bytes() else "\n"
    ga = root / ".gitattributes"
    if ga.exists():
        txt = ga.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"eol=crlf", txt):
            return "\r\n"
    return "\n"


EOL = detect_eol()


def put(path, text):
    """Write text with the file's own line ending if it exists, else the project's."""
    eol = EOL
    if path.exists():
        eol = "\r\n" if b"\r\n" in path.read_bytes() else "\n"
    path.write_bytes(text.replace("\r\n", "\n").replace("\n", eol).encode("utf-8"))


def copy_text(src, dst):
    put(dst, Path(src).read_text(encoding="utf-8"))


def plan(msg, fn):
    todo.append(msg)
    print(("DO   " if apply else "TODO ") + msg)
    if apply:
        fn()


def copy_template(src, dst):
    text = (KIT / "templates" / src).read_text(encoding="utf-8").replace("YYYY-MM-DD", date.today().isoformat())
    put(dst, text)


def append_missing(dst, lines):
    have = set(dst.read_text(encoding="utf-8").splitlines()) if dst.exists() else set()
    new = [l for l in lines if l and l not in have]
    if new:
        base = dst.read_text(encoding="utf-8") if dst.exists() else ""
        put(dst, base + ("\n" if base and not base.endswith("\n") else "") + "\n".join(new) + "\n")


if not (root / "PROJECT_STATUS.md").exists():
    sys.exit("Not a kickoff project (no PROJECT_STATUS.md). Run /kickoff instead.")

for name, tpl in (("DECISIONS.md", "DECISIONS.template.md"), ("NEXT.md", "NEXT.template.md")):
    if not (root / name).exists():
        plan(f"create {name}", lambda n=name, t=tpl: copy_template(t, root / n))
for tool in ("doctor.py", "proj_toggle.py", "profile_lib.py", "doctor_extra.py", "companions.py"):
    if not (root / "tools" / tool).exists():
        plan(f"copy tools/{tool}", lambda t=tool: (root / "tools").mkdir(exist_ok=True) or shutil.copy2(KIT / "tools" / t, root / "tools" / t))


def sha(path):
    """Hash of the text with line endings normalized, so a CRLF copy compares equal to the LF kit file."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def kit_version():
    try:
        return json.loads((KIT.parent / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("version", "")
    except Exception:
        return ""


# presets the tools need when the plugin folder is not reachable
wanted_presets = ["_always.json"] + [f"{n}.json" for n, _ in family if (KIT / "presets" / f"{n}.json").exists()]
for name in wanted_presets:
    dst = root / ".kickoff" / "presets" / name
    if not dst.exists():
        plan(f"copy .kickoff/presets/{name}",
             lambda n=name, d=dst: (d.parent.mkdir(parents=True, exist_ok=True), copy_text(KIT / "presets" / n, d)))

# the profile files, main first (plan.py init reads "Default phases" from here when the plugin folder is out of reach)
for pname, ppath in family:
    dst = root / ".kickoff" / "profiles" / f"{pname}.md"
    if ppath.parent == KIT / "profiles" and not dst.exists():
        plan(f"copy .kickoff/profiles/{pname}.md",
             lambda s=ppath, d=dst: (d.parent.mkdir(parents=True, exist_ok=True), copy_text(s, d)))

# kit copies: refreshed only while unchanged since the kit wrote them
KIT_COPIES = ("CLAUDE_INSTRUCTIONS.md", "WRAPUP_PROMPT.md")
PROFILE_REF = re.compile(r"[A-Za-z]:[\\/][^\s`'\")\]]*?profiles[\\/]([A-Za-z0-9_-]+)\.md")
_ct = (root / "CLAUDE.md").read_text(encoding="utf-8") if (root / "CLAUDE.md").exists() else ""
for _m in PROFILE_REF.finditer(_ct):
    _own = (root / ".kickoff" / "profile.md").exists() and _m.group(1) == "custom"
    if not _own and (KIT / "profiles" / f"{_m.group(1)}.md").exists() and f"profiles/{_m.group(1)}.md" not in KIT_COPIES:
        KIT_COPIES += (f"profiles/{_m.group(1)}.md",)
state_path = root / ".kickoff" / "kit" / ".sources.json"
try:
    state = json.loads(state_path.read_text(encoding="utf-8"))
except Exception:
    state = {"kit_version": "", "files": {}}
state_dirty = False


def put_copy(name):
    dst = root / ".kickoff" / "kit" / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    copy_text(KIT / name, dst)
    state["files"][name] = sha(dst)
    state["kit_version"] = kit_version()
    put(state_path, json.dumps(state, indent=2) + "\n")


def record_copy(name):
    state["files"][name] = sha(root / ".kickoff" / "kit" / name)
    state["kit_version"] = kit_version()
    put(state_path, json.dumps(state, indent=2) + "\n")


for name in KIT_COPIES:
    dst = root / ".kickoff" / "kit" / name
    if not (KIT / name).exists():
        continue
    if not dst.exists():
        plan(f"copy .kickoff/kit/{name}", lambda n=name: put_copy(n))
    elif name not in state["files"]:
        if sha(dst) == sha(KIT / name):
            plan(f".kickoff/kit/{name}: record its hash", lambda n=name: record_copy(n))
        else:
            print(f"INFO .kickoff/kit/{name} differs from the kit and has no recorded hash; not refreshed")
    elif sha(dst) != state["files"][name]:
        print(f"INFO .kickoff/kit/{name} was edited here since the kit copied it; not refreshed (kit has a newer copy: "
              f"{'yes' if sha(KIT / name) != state['files'][name] else 'no'})")
    elif sha(KIT / name) != state["files"][name]:
        plan(f"refresh .kickoff/kit/{name} (unchanged here, kit {kit_version()})", lambda n=name: put_copy(n))

KIT_REF = re.compile(r"[A-Za-z]:[\\/][^\s`'\")\]]*?(CLAUDE_INSTRUCTIONS\.md|WRAPUP_PROMPT\.md|profiles[\\/][A-Za-z0-9_-]+\.md)")


def copy_ready(name):
    return (root / ".kickoff" / "kit" / name).exists() or any(f".kickoff/kit/{name}" in x for x in todo)


def ref_target(g):
    """Where a kit reference should point inside the project, or None when there is no copy to point at."""
    g = g.replace("\\", "/")
    if g == "profiles/custom.md" and (root / ".kickoff" / "profile.md").exists():
        return ".kickoff/profile.md"
    return ".kickoff/kit/" + g if copy_ready(g) else None


claude_file = root / "CLAUDE.md"
if claude_file.exists():
    ctext = claude_file.read_text(encoding="utf-8")
    refs = [m for m in KIT_REF.finditer(ctext) if ref_target(m.group(1))]
    if refs:
        def rewrite_refs():
            cur = claude_file.read_text(encoding="utf-8")
            cur = KIT_REF.sub(lambda m: ref_target(m.group(1)) or m.group(0), cur)
            if "kickoff:kit-references" not in cur:
                cur = cur.rstrip("\n") + "\n<!-- kickoff:kit-references -->\n"
            put(claude_file, cur)
            dec = root / "DECISIONS.md"
            if dec.exists():
                line = (f"- {date.today().isoformat()} | CLAUDE.md kit references now point to .kickoff/kit/ (or .kickoff/profile.md for a custom profile; were absolute paths outside the project) | "
                        "one copy per project, refreshed by /kickoff:upgrade while unedited | keep the absolute paths")
                dtxt = dec.read_text(encoding="utf-8")
                m = re.search(r"(?m)^Newest first\..*$", dtxt)
                put(dec, dtxt[:m.end()] + "\n\n" + line + dtxt[m.end():] if m else dtxt.rstrip("\n") + "\n" + line + "\n")
        plan(f"CLAUDE.md: point {len(refs)} kit reference(s) inside the project, at .kickoff/kit/ or .kickoff/profile.md (was: {refs[0].group(0)}); marked with a comment, noted in DECISIONS.md",
             rewrite_refs)

# tool copies inside the project (opt-in: --refresh-tools). Old copy saved under .kickoff/backup/<date>/; budgets.json is never touched.
TOOL_NAMES = ("build_index.py", "check_budgets.py", "doctor.py", "proj_toggle.py", "plan.py", "plan_lib.py", "profile_lib.py", "doctor_extra.py", "companions.py", "fix_hashes.py")
stale_tools = [n for n in TOOL_NAMES if (root / "tools" / n).exists() and (KIT / "tools" / n).exists() and sha(root / "tools" / n) != sha(KIT / "tools" / n)]


def refresh_tool(n):
    bak = root / ".kickoff" / "backup" / date.today().isoformat() / n
    bak.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "tools" / n, bak)
    copy_text(KIT / "tools" / n, root / "tools" / n)


if "--refresh-tools" in a:
    for n in stale_tools:
        plan(f"refresh tools/{n} to kit {kit_version()} (old copy saved to .kickoff/backup/{date.today().isoformat()}/{n})", lambda n=n: refresh_tool(n))
elif stale_tools:
    print(f"INFO {len(stale_tools)} tool copy(ies) in tools/ differ from kit {kit_version()}: {', '.join(stale_tools)} (refresh with: upgrade.py --refresh-tools --apply)")

want = (KIT / "gitignore" / "common.gitignore").read_text(encoding="utf-8").splitlines()
for _n, _p in family:
    if (KIT / "gitignore" / f"{_n}.gitignore").exists():
        want += (KIT / "gitignore" / f"{_n}.gitignore").read_text(encoding="utf-8").splitlines()
gi = root / ".gitignore"
have = set(gi.read_text(encoding="utf-8").splitlines()) if gi.exists() else set()
if [l for l in want if l and l not in have]:
    plan(".gitignore: add missing lines" if gi.exists() else "create .gitignore", lambda: append_missing(gi, want))
ga = root / ".gitattributes"
wa = (KIT / "templates" / "gitattributes").read_text(encoding="utf-8").splitlines()
if [l for l in wa if l and l not in (set(ga.read_text(encoding="utf-8").splitlines()) if ga.exists() else set())]:
    plan(".gitattributes: add missing lines" if ga.exists() else "create .gitattributes", lambda: append_missing(ga, wa))

gj = root / ".kickoff" / "guide.json"
guide_present = ((root / ".guidebook").is_dir() or (root / "docs" / "guide-src").is_dir()
                 or (root / "docs" / "guide" / "guide.manifest.json").exists())
if guide_present and not gj.exists():
    print("INFO guide already present, built by guidebook (no question needed" + ("; --guide local ignored" if guide == "local" else "") + ")")
elif guide == "local" and not gj.exists():
    def write_guide():
        cfg = json.loads((KIT / "templates" / "guide.json.template").read_text(encoding="utf-8"))
        cfg["brand"] = root.name
        cfg["hub"] = ""  # the hub path stays in ~/.claude/kickoff/config.json; never copied into the project
        gj.parent.mkdir(exist_ok=True)
        put(gj, json.dumps(cfg, indent=2) + "\n")
    plan("create .kickoff/guide.json (guide: local)", write_guide)
elif not gj.exists():
    print("INFO no guide set up (add with: upgrade.py --guide local)")

STATUS_KEYS = ("project_status", "target_date", "deadline", "blocked_by")
NEXT_KEYS = ("next",)


def add_keys(path, keys):
    put(path, frontmatter_with_keys(path, keys))


def write_json(path, data):
    path.parent.mkdir(exist_ok=True)
    put(path, json.dumps(data, indent=2) + "\n")


fj = root / ".kickoff" / "fields.json"
stored = None
if fj.exists():
    try:
        stored = json.loads(fj.read_text(encoding="utf-8")).get("tier")
    except Exception:
        stored = None
stored_plan = False
if fj.exists():
    try:
        stored_plan = json.loads(fj.read_text(encoding="utf-8")).get("plan") is True
    except Exception:
        stored_plan = False
if stored not in (None, *TIERS):  # a tier name from an older kit: keep the keys, and the plan file only if it was on
    stored = "plan" if stored_plan else "fields"
tier = fields_req or stored
use_plan = tier == "plan"
if tier is None:
    print("INFO fields not chosen (optional; ask: none / fields / plan, then --fields NAME)")
else:
    new_cfg = {"contract": 1, "tier": tier}
    if fields_req and fields_req != stored:
        plan(f"write .kickoff/fields.json (tier: {tier})",
             lambda: write_json(fj, new_cfg))
    if tier in ("fields", "plan"):
        for fname, keys in (("PROJECT_STATUS.md", STATUS_KEYS), ("NEXT.md", NEXT_KEYS)):
            path = root / fname
            miss = missing_keys(path, keys)
            if miss:
                plan(f"{fname}: add frontmatter keys {', '.join(miss)}", lambda p=path, k=miss: add_keys(p, k))
            elif miss is None and path.exists():
                print(f"INFO {fname} has no frontmatter; fields skipped for it")
        if not apply and any(x == "create NEXT.md" for x in todo):
            print("INFO NEXT.md will be created; its fields are added in the same --apply run")
    if use_plan:
        for pf in ("plan.py", "plan_lib.py", "profile_lib.py"):
            if not (root / "tools" / pf).exists():
                plan(f"copy tools/{pf}", lambda f=pf: (root / "tools").mkdir(exist_ok=True) or shutil.copy2(KIT / "tools" / f, root / "tools" / f))
        if not (root / ".kickoff" / "plan.json").exists():
            plan("create .kickoff/plan.json from templates/plan.template.json (empty; fill it with plan.py init or by hand)",
                 lambda: (root / ".kickoff").mkdir(exist_ok=True) or copy_text(KIT / "templates" / "plan.template.json", root / ".kickoff" / "plan.json"))

# ---- 1.4: clarity rule, requirements ledger, status sections (choices stored in .kickoff/options.json) ----
options_path = root / ".kickoff" / "options.json"
try:
    stored_opts = json.loads(options_path.read_text(encoding="utf-8"))
except Exception:
    stored_opts = {}
req_sections, req_clarity = opt("--sections"), opt("--clarity")
for flag, val in (("--sections", req_sections), ("--clarity", req_clarity)):
    if val not in (None, "yes", "no"):
        sys.exit(f"{flag} must be yes or no")
new_opts = dict(stored_opts, contract=1)
if req_sections:
    new_opts["sections"] = req_sections == "yes"
if req_clarity:
    new_opts["clarity"] = req_clarity == "yes"
if new_opts != stored_opts:
    plan("write .kickoff/options.json (" + ", ".join(f"{k}: {v}" for k, v in new_opts.items() if k != "contract") + ")",
         lambda: write_json(options_path, new_opts))
sections_on = new_opts.get("sections")
clarity_on = new_opts.get("clarity", True)

CLARITY_OPEN = "<!-- kickoff:clarity-rule -->"
if clarity_on:
    claude_md = root / "CLAUDE.md"
    if not claude_md.exists():
        print("INFO CLAUDE.md missing; the clarity rule is added when it exists (run /kickoff:kickoff)")
    elif CLARITY_OPEN not in claude_md.read_text(encoding="utf-8"):
        def add_rule():
            text = claude_md.read_text(encoding="utf-8")
            rule = (KIT / "templates" / "clarity-rule.md").read_text(encoding="utf-8")
            put(claude_md, text.rstrip("\n") + "\n\n" + rule)
        plan("CLAUDE.md: append the clarity rule block (marked, one block; the rest of the file is untouched)", add_rule)
    if not (root / "REQUIREMENTS.md").exists():
        plan("create REQUIREMENTS.md", lambda: copy_template("REQUIREMENTS.template.md", root / "REQUIREMENTS.md"))
else:
    print("INFO clarity rule is turned off for this project (--clarity yes turns it on)")


TITLES = ("How to run", "Setup", "Data", "Troubleshooting")
status_md = root / "PROJECT_STATUS.md"
if sections_on and status_md.exists():
    stext = status_md.read_text(encoding="utf-8")
    missing_sections = [h for h in TITLES if not re.search(rf"^##\s+{re.escape(h)}\b", stext, re.M | re.I)]
    if missing_sections:
        def add_sections():
            template = (KIT / "templates" / "status-sections.template.md").read_text(encoding="utf-8")
            chunks = {m.group(1): m.group(0).strip("\n") for m in re.finditer(r"^## (.+?)\n.*?(?=^## |\Z)", template, re.S | re.M)}
            guesses = guess_sections(root)
            add = []
            for h in missing_sections:
                if h in guesses:
                    add.append(f"## {h}\n{guesses[h]}\n")
                else:
                    add.append(chunks[h] + "\n")
            cur = status_md.read_text(encoding="utf-8")
            put(status_md, cur.rstrip("\n") + "\n\n" + "\n".join(add))
        plan("PROJECT_STATUS.md: add sections " + ", ".join(missing_sections) +
             " (pre-filled from the repo and marked GUESSED where found, else UNKNOWN with the question)", add_sections)
elif sections_on is None and status_md.exists():
    print("INFO status sections not chosen (How to run / Setup / Data / Troubleshooting; add with --sections yes, skip with --sections no)")


if profile and family:  # which profile version this project uses; doctor compares it with the kit (profile_lib.fingerprint)
    _stamp = {"contract": 1, "profile": profile_lib.canonical(profile), "kit_version": kit_version(), "fingerprint": profile_lib.fingerprint(profile, root, [KIT])}
    _sp = root / ".kickoff" / "profile.stamp.json"
    if not _sp.exists() or json.loads(_sp.read_text(encoding="utf-8")).get("fingerprint") != _stamp["fingerprint"]:
        plan("write .kickoff/profile.stamp.json (profile version for the doctor)", lambda: write_json(_sp, _stamp))

if not todo:
    print("Up to date. Nothing to add.")
elif not apply:
    print(f"\n{len(todo)} item(s). Re-run with --apply to do them (nothing is overwritten).")
else:
    print(f"\nDone: {len(todo)} item(s). Run /doctor next.")

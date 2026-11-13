#!/usr/bin/env python3
"""Project health check (read-only unless --repair).

Usage: python tools/doctor.py [project_root] [--repair] [--dry-run]
Checks: status file freshness, CLAUDE.md size, always-loaded weight, budgets/INDEX, plugin set,
stale plugin installs, risky permission rules, NEXT.md, optional tracking fields. --repair prunes stale plugin install
records from ~/.claude/plugins/installed_plugins.json (backup first; --dry-run only lists).
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
repair, dry = "--repair" in sys.argv, "--dry-run" in sys.argv
root = Path(args[0]).resolve() if args else Path.cwd()
home = Path.home() / ".claude"
HERE = Path(__file__).resolve().parent
res = []


def rep(level, msg):
    res.append(level)
    print(f"{level:<4} {msg}")


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return {}


# 1. status + next
ps = root / "PROJECT_STATUS.md"
if not ps.exists():
    rep("WARN", "PROJECT_STATUS.md missing (run /kickoff)")
else:
    m = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", ps.read_text(encoding="utf-8", errors="ignore"), re.M)
    if m:
        age = (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days
        rep("OK" if age <= 30 else "WARN", f"PROJECT_STATUS.md updated {age} days ago")
    else:
        rep("WARN", "PROJECT_STATUS.md has no 'updated' date")
rep("OK" if (root / "NEXT.md").exists() else "WARN", "NEXT.md " + ("present" if (root / "NEXT.md").exists()
                                                                  else "missing (written by /wrapup)"))

# 2. CLAUDE.md and always-loaded weight
cm = root / "CLAUDE.md"
if cm.exists():
    text = cm.read_text(encoding="utf-8", errors="ignore")
    lines, toks = text.count("\n") + 1, len(text) // 4
    rep("OK" if lines <= 200 else "FAIL", f"CLAUDE.md {lines} lines (max 200), ~{toks} tokens")
    rep("OK" if toks <= 3000 else "WARN", f"always-loaded context ~{toks} tokens (warn above 3000)")
else:
    rep("WARN", "CLAUDE.md missing")

# 3. budgets + indexes
cb = root / "tools" / "check_budgets.py"
bi = root / "tools" / "build_index.py"
if cb.exists() and bi.exists():
    out = subprocess.run([sys.executable, str(bi), str(root), "--verbose"], capture_output=True, text=True)
    r = subprocess.run([sys.executable, str(cb), str(root)], capture_output=True, text=True)
    rep("OK" if r.returncode == 0 else "FAIL", "budgets " + ("pass" if r.returncode == 0 else "violations: run /reindex"))
    if out.returncode != 0:
        rep("FAIL", "index: " + (out.stderr.strip() or out.stdout.strip())[:200])
    else:
        lines = [l.rstrip() for l in out.stdout.splitlines()]
        touched = [l.strip() for l in lines if l.startswith("  created") or l.startswith("  changed")]
        refused = [l.strip() for l in lines if l.startswith("  SKIPPED")]
        src = next((l.split("from ", 1)[1] for l in lines if "skip list from" in l), "defaults")
        rep("OK", f"index: ran the project's own tools/build_index.py (skip list: {src}); {len(touched)} file(s) created or changed")
        for l in touched[:20]:
            print(f"       {l}")
        if len(touched) > 20:
            print(f"       ... and {len(touched) - 20} more")
        for l in refused:
            rep("WARN", "index: " + l.replace("SKIPPED", "left alone:", 1))
else:
    rep("WARN", "tools/ missing (run /kickoff)")

# 4. plugin set and stale installs
s = load(root / ".claude" / "settings.json")
s_local = load(root / ".claude" / "settings.local.json")
off = [k for k, v in {**s.get("enabledPlugins", {}), **s_local.get("enabledPlugins", {})}.items() if v is False]
rep("OK", f"{len(off)} plugin(s) turned off for this project" if off else "no per-project plugin choices (run /plugins)")
ip = home / "plugins" / "installed_plugins.json"
data = load(ip)
stale = [(k, e) for k, v in data.get("plugins", {}).items() for e in v
         if e.get("installPath") and not Path(e["installPath"]).exists()]
if stale:
    rep("WARN", f"{len(stale)} stale plugin install record(s) (cache folder missing)")
    for k, e in stale:
        print(f"       {k} @ {e.get('projectPath', 'user')}")
    if repair and not dry:
        shutil.copy2(ip, ip.with_name("installed_plugins.json.bak"))
        for k, e in stale:
            data["plugins"][k].remove(e)
        data["plugins"] = {k: v for k, v in data["plugins"].items() if v}
        ip.write_text(json.dumps(data, indent=2), encoding="utf-8")
        rep("OK", "pruned stale records (backup: installed_plugins.json.bak)")
    elif repair:
        rep("OK", "dry run: nothing removed")
    else:
        print("       run with --repair to prune them")
else:
    rep("OK", "no stale plugin installs")

# 5. permissions
perm = s.get("permissions", {})
risky = [r for r in perm.get("allow", []) if r in ("Bash", "Bash(*)", "Write", "Edit") or ".env" in r]
rep("WARN" if risky else "OK", f"broad allow rules: {', '.join(risky)}" if risky else "no broad allow rules")
deny = " ".join(perm.get("deny", []))
rep("OK" if ".env" in deny else "WARN", ".env read is denied" if ".env" in deny else
    "no deny rule for .env (merge kit/templates/settings.starter.json)")

# 6. guide
gj = root / ".kickoff" / "guide.json"
if not gj.exists():
    if (root / ".guidebook").is_dir() or (root / "docs" / "guide-src").is_dir() or (root / "docs" / "guide" / "guide.manifest.json").exists():
        print("INFO guide already present, built by guidebook")
    else:
        print("INFO no guide set up (optional: /kickoff:upgrade, guide: local)")
else:
    g = load(gj)
    if not g.get("enabled", True):
        print("INFO guide is disabled in .kickoff/guide.json")
    else:
        out = root / g.get("output", "docs/guide")
        rep("OK" if (out / "guide.manifest.json").exists() else "WARN",
            "guide manifest present" if (out / "guide.manifest.json").exists() else
            f"guide not built yet ({out.name}/guide.manifest.json missing): run guidebook update")
        gb = shutil.which("guidebook")
        if gb:
            st = subprocess.run([gb, "status"], cwd=root, capture_output=True, text=True)
            rep("OK" if st.returncode == 0 else "WARN", "guide is fresh" if st.returncode == 0 else
                "guide has stale pages: run guidebook update")
        else:
            rep("WARN", "guidebook command not installed (guide config is ready)")
        if g.get("hub") and not Path(g["hub"]).exists():
            rep("WARN", f"hub folder not found: {g['hub']}")

# 7. tracking fields (optional; only when .kickoff/fields.json says fields or plan)
fcfg = load(root / ".kickoff" / "fields.json")
tier = fcfg.get("tier", "none")
if tier not in ("none", "fields", "plan"):  # a tier name from an older kit
    tier = "plan" if fcfg.get("plan") is True else "fields"
plan_on = tier == "plan"
if tier not in ("fields", "plan"):
    print("INFO tracking fields not enabled (optional: /kickoff:upgrade, see kit/FIELDS_CONTRACT.md)")
else:
    def fm(path):
        m = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---", path.read_text(encoding="utf-8", errors="ignore"), re.S) \
            if path.exists() else None
        return {k.strip(): v.strip().strip("\"'") for k, v in (l.split(":", 1) for l in m.group(1).splitlines()
                                                              if ":" in l)} if m else None

    def iso(v):
        try:
            return datetime.date.fromisoformat(v)
        except ValueError:
            return None

    sm, nm = fm(root / "PROJECT_STATUS.md"), fm(root / "NEXT.md")
    if sm is None:
        rep("WARN", "tracking fields on, but PROJECT_STATUS.md has no frontmatter")
    else:
        absent = [k for k in ("project_status", "target_date", "deadline", "blocked_by") if k not in sm]
        rep("WARN" if absent else "OK", f"status fields missing: {', '.join(absent)} (run /kickoff:upgrade)" if absent
            else "status fields present")
        for k in ("target_date", "deadline", "updated"):
            if sm.get(k) and not iso(sm[k]):
                rep("WARN", f"{k} '{sm[k]}' is not YYYY-MM-DD")
        dl = iso(sm.get("deadline", ""))
        if dl and dl < datetime.date.today() and sm.get("project_status", "").upper() not in (
                "DONE", "COMPLETE", "COMPLETED", "PASSED", "ARCHIVED"):
            rep("WARN", f"deadline {dl} has passed and project_status is '{sm.get('project_status') or 'blank'}'")
    if nm is None:
        rep("WARN", "tracking fields on, but NEXT.md is missing or has no frontmatter")
    else:
        rep("WARN" if "next" not in nm else "OK", "NEXT.md has no 'next' key (run /kickoff:upgrade)" if "next" not in nm
            else "NEXT.md 'next' key present")
        nu = iso(nm.get("updated", ""))
        if nu and (datetime.date.today() - nu).days > 14:
            rep("WARN", f"NEXT.md updated {(datetime.date.today() - nu).days} days ago (over 14)")

# 7b. plan file (only with the plan tier)
if plan_on:
    sys.path.insert(0, str(HERE))
    pf = root / ".kickoff" / "plan.json"
    try:
        import plan_lib
    except ImportError:
        plan_lib = None
        rep("WARN", "plan_lib.py missing next to doctor.py (copy tools/plan.py and tools/plan_lib.py: /kickoff:upgrade)")
    if plan_lib and not pf.exists():
        rep("WARN", ".kickoff/plan.json missing (run /kickoff:upgrade --fields plan, then plan.py init)")
    elif plan_lib:
        try:
            pdata = json.loads(pf.read_text(encoding="utf-8"))
            perrs = plan_lib.validate(pdata)
        except ValueError as e:
            pdata, perrs = None, [f"not valid JSON: {e}"]
        if perrs:
            rep("FAIL", f"plan.json invalid: {perrs[0]}" + (f" (+{len(perrs) - 1} more; run plan.py validate)" if len(perrs) > 1 else ""))
        else:
            rep("OK", "plan.json valid")
            today = datetime.date.today()
            late = [n for n, _ in plan_lib.nodes(pdata) if plan_lib.status_of(n) == "IN_PROGRESS"
                    and (plan_lib.parse_date(n.get("end")) or today) < today]
            for n in late:
                rep("WARN", f"{n['id']} '{n['name']}' is IN_PROGRESS past its planned end {n['end']}")
            for ph in pdata["phases"]:
                steps = ph.get("steps", [])
                if steps and all(plan_lib.status_of(s) in ("DONE", "CUT") for s in steps) and plan_lib.status_of(ph) not in ("DONE", "CUT"):
                    rep("WARN", f"phase {ph['id']} '{ph['name']}': all steps are DONE or CUT but the phase is {plan_lib.status_of(ph)}")
            if not late:
                rep("OK", "no step is IN_PROGRESS past its end")

# 7c. kit copies the project's CLAUDE.md points to
kc = root / ".kickoff" / "kit"
if (root / "CLAUDE.md").exists() and ".kickoff/kit/" in (root / "CLAUDE.md").read_text(encoding="utf-8", errors="ignore"):
    miss = [n for n in ("CLAUDE_INSTRUCTIONS.md", "WRAPUP_PROMPT.md") if not (kc / n).exists()]
    rep("WARN" if miss else "OK", f"CLAUDE.md points to .kickoff/kit/ but {', '.join(miss)} missing (run /kickoff:upgrade)" if miss
        else ".kickoff/kit/ copies present")

# 7d. clarity rule, requirements ledger, status sections (kickoff 1.4; choices in .kickoff/options.json)
opts = load(root / ".kickoff" / "options.json")
if opts.get("clarity", True):
    cmd_text = cm.read_text(encoding="utf-8", errors="ignore") if cm.exists() else ""
    if cm.exists():
        rep("OK" if "<!-- kickoff:clarity-rule -->" in cmd_text else "WARN",
            "clarity rule is in CLAUDE.md" if "<!-- kickoff:clarity-rule -->" in cmd_text
            else "clarity rule block missing from CLAUDE.md (run /kickoff:upgrade)")
    rq = root / "REQUIREMENTS.md"
    if not rq.exists():
        rep("WARN", "REQUIREMENTS.md missing (run /kickoff:upgrade)")
    else:
        rtext = rq.read_text(encoding="utf-8", errors="ignore")
        open_reqs = len(re.findall(r"^\|\s*R\d+\s*\|.*\|\s*OPEN\b", rtext, re.M))
        unanswered = len([m for m in re.finditer(r"^\|\s*Q\d+\s*\|([^|]*)\|([^|]*)\|\s*$", rtext, re.M)
                          if m.group(1).strip() and not m.group(2).strip()])
        rep("WARN" if open_reqs or unanswered else "OK",
            f"REQUIREMENTS.md: {open_reqs} requirement(s) OPEN, {unanswered} question(s) unanswered" if open_reqs or unanswered
            else "REQUIREMENTS.md: nothing open")
else:
    print("INFO clarity rule is turned off for this project (.kickoff/options.json)")
if opts.get("sections"):
    ptext = ps.read_text(encoding="utf-8", errors="ignore") if ps.exists() else ""
    filled = guessed = unknown = missing = 0
    for h in ("How to run", "Setup", "Data", "Troubleshooting"):
        m = re.search(rf"^##\s+{re.escape(h)}\b[^\n]*\n(.*?)(?=^##\s|\Z)", ptext, re.M | re.S | re.I)
        if not m:
            missing += 1
        else:
            body = m.group(1).strip()
            if not body or body.upper().startswith("UNKNOWN"):
                unknown += 1
            elif body.upper().startswith("GUESSED"):
                guessed += 1
            else:
                filled += 1
    done = filled
    rep("OK" if done == 4 else "WARN",
        f"status sections: {done} of 4 confirmed" + (f", {guessed} GUESSED (confirm at wrap-up)" if guessed else "") +
        (f", {unknown} UNKNOWN" if unknown else "") + (f", {missing} missing (run /kickoff:upgrade --sections yes)" if missing else ""))
elif opts.get("sections") is None:
    print("INFO status sections not chosen (How to run / Setup / Data / Troubleshooting; /kickoff:upgrade --sections yes)")

# 7e. kickoff 1.4.1 checks: paths, kit copies, stale hashes, line endings, handover, co-author block
def this_kit_version():
    for base in (os.environ.get("CLAUDE_PLUGIN_ROOT"), str(HERE.parent.parent)):
        if base and (Path(base) / ".claude-plugin" / "plugin.json").exists():
            return load(Path(base) / ".claude-plugin" / "plugin.json").get("version", "")
    return ""


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "0")[:3])


if cm.exists():
    ctext7 = cm.read_text(encoding="utf-8", errors="ignore")
    outside = [m.group(0) for m in re.finditer(r"[A-Za-z]:[\\/][^\s`'\")\]]+", ctext7)
               if not os.path.normcase(os.path.normpath(m.group(0))).startswith(os.path.normcase(str(root)))]
    if outside:
        rep("WARN", f"CLAUDE.md points outside the project: {outside[0]}" + (f" (+{len(outside) - 1} more)" if len(outside) > 1 else "") +
            " (/kickoff:upgrade fixes the CLAUDE_INSTRUCTIONS.md and WRAPUP_PROMPT.md references; edit others by hand)")
    else:
        rep("OK", "CLAUDE.md has no paths outside the project")
srcs = load(root / ".kickoff" / "kit" / ".sources.json")
kv = this_kit_version()
if srcs.get("kit_version") and kv:
    old_copy = vtuple(srcs["kit_version"]) < vtuple(kv)
    rep("WARN" if old_copy else "OK", f".kickoff/kit/ copies are from kickoff {srcs['kit_version']}, this kickoff is {kv} (run /kickoff:upgrade)"
        if old_copy else f".kickoff/kit/ copies are current (kickoff {kv})")

git_dir = root / ".git"
def git(*a):
    r = subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip()

if git_dir.exists():
    stale = {}
    for fname in ("NEXT.md", "PROJECT_STATUS.md", "DECISIONS.md", "REQUIREMENTS.md", ".guidebook/state.json"):
        fp = root / fname
        if not fp.exists():
            continue
        for tok in set(re.findall(r"\b[0-9a-f]{7,40}\b", fp.read_text(encoding="utf-8", errors="ignore"))):
            if not re.search(r"\d", tok) or not re.search(r"[a-f]", tok):
                continue
            if git("cat-file", "-e", tok + "^{commit}")[0] != 0 or not git("for-each-ref", "--contains", tok, "refs/heads", "refs/tags")[1]:
                stale.setdefault(fname, []).append(tok)
    if stale:
        for fname, toks in stale.items():
            rep("WARN", f"{fname}: commit hash(es) git cannot find or that no branch contains: {', '.join(sorted(toks)[:6])} (after a history rewrite use tools/fix_hashes.py)")
    else:
        rep("OK", "no unresolvable commit hashes in NEXT.md, PROJECT_STATUS.md, DECISIONS.md, REQUIREMENTS.md")
    nx = root / "NEXT.md"
    if nx.exists():
        ntext = nx.read_text(encoding="utf-8", errors="ignore")
        mu = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", ntext, re.M)
        code, head_date = git("log", "-1", "--format=%cs")
        if mu and code == 0 and head_date and mu.group(1) < head_date:
            rep("WARN", f"NEXT.md was updated {mu.group(1)} but HEAD is from {head_date}: 'Stopped at' and the uncommitted list may be stale (/kickoff:wrapup)")
        code, porcelain = git("status", "--short")
        porcelain = chr(10).join(l for l in porcelain.splitlines() if not l.endswith("INDEX.md"))
        if code == 0 and not porcelain and re.search(r"nothing (is )?committed|not (yet )?committed|uncommitted", ntext, re.I):
            rep("WARN", "NEXT.md talks about uncommitted work but git status is clean (/kickoff:wrapup recomputes it)")

ga7 = root / ".gitattributes"
ga_text = ga7.read_text(encoding="utf-8", errors="ignore") if ga7.exists() else ""
if not (re.search(r"\*\.md[^\n]*eol=", ga_text) and re.search(r"\*\.json[^\n]*eol=", ga_text)):
    print("INFO recommended .gitattributes lines: '*.md text eol=lf' and '*.json text eol=lf' (/kickoff:upgrade appends them)")

flags = {}
for sp in (home / "settings.json", root / ".claude" / "settings.json", root / ".claude" / "settings.local.json"):
    flags.update({k: v for k, v in load(sp).get("enabledPlugins", {}).items() if k.split("@")[0] == "kickoff"})
dis7 = os.environ.get("KICKOFF_DISABLED_HOOKS", "").split(",")
if not any(flags.values()):
    inst = any(k.split("@")[0] == "kickoff" for k in load(home / "plugins" / "installed_plugins.json").get("plugins", {}))
    rep("WARN", "co-author block inactive: kickoff is " + ("installed but switched off for this project (run: python tools/proj_toggle.py on kickoff)"
        if inst else "not installed (run: claude plugin install kickoff@byterive-kit)") + "; its hook is what blocks Co-Authored-By: Claude")
elif "coauthor" in dis7:
    rep("WARN", "co-author block inactive: KICKOFF_DISABLED_HOOKS contains 'coauthor'")
else:
    cmh, af = root / ".git" / "hooks" / "commit-msg", root / ".kickoff" / "attribution.json"
    rep("OK", ("Claude contribution line allowed for this project (.kickoff/attribution.json); hook lets it through" if af.exists() and '"claude_contribution": true' in af.read_text(encoding="utf-8", errors="ignore") else "co-author block active (kickoff plugin enabled; hook blocks Co-Authored-By: Claude)") +
        ("; git commit-msg hook installed" if cmh.exists() else "; no git commit-msg hook (optional, kit/tools/commit-msg.sample)"))

# 7f. kickoff 1.4.2: local paths and private plugin names in files git tracks
TEXT_EXT = {".md", ".json", ".txt", ".toml", ".yaml", ".yml", ".py", ".cs", ".js", ".ts", ".go", ".ps1", ".sh", ".cfg", ".ini"}
WIN_PATH = re.compile(r"[A-Za-z]:\\{1,2}(?![^\s`'\")\]]*<)(?:[^\s`'\")\]<>|*?]+)")
OWN_TOOLS = {"tools/" + n for n in ("doctor.py", "proj_toggle.py", "upgrade.py", "fix_hashes.py", "build_index.py", "check_budgets.py", "plan.py", "plan_lib.py")}
UNIX_HOME = re.compile(r"(?:/Users|/home)/(?!<|\$|\{|you\b|user\b|name\b)[A-Za-z0-9._-]+/")
ACCOUNT = re.compile(r"(?i)[A-Za-z]:\\{1,2}Users\\{1,2}(?!<)|(?:/Users|/home)/(?!<|\$|\{|you\b|user\b|name\b)")
if (root / ".git").exists():
    ls = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines()
    hits, acct = {}, set()
    for rel in ls:
        fp = root / rel
        if fp.suffix.lower() not in TEXT_EXT or rel.startswith((".guidebook/", ".kickoff/kit/")) or rel in OWN_TOOLS or not fp.is_file() or fp.stat().st_size > 400_000:
            continue
        for n, line in enumerate(fp.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if WIN_PATH.search(line) or UNIX_HOME.search(line):
                hits.setdefault(rel, []).append(n)
                if ACCOUNT.search(line):
                    acct.add(rel)
    if hits:
        rep("WARN", f"{len(hits)} tracked file(s) contain absolute local paths" + (f"; {len(acct)} include a user account name" if acct else "") + " (matters if the repo goes public)")
        for rel, ns in sorted(hits.items())[:15]:
            print(f"       {rel}: line {', '.join(map(str, ns[:5]))}" + (" ..." if len(ns) > 5 else ""))
    else:
        rep("OK", "no absolute local paths in tracked files")
    named = sorted(k for k in s.get("enabledPlugins", {}) if "@" in k) if ".claude/settings.json" in ls else []
    if named:
        rep("WARN", f".claude/settings.json is tracked and names {len(named)} plugin(s) (e.g. {named[0]}); run 'python tools/proj_toggle.py localize' to move them to the git-ignored settings.local.json")
    if any(r.startswith("_audit/") for r in hits):
        rep("WARN", "_audit/ has files with absolute paths (an audit should use relative paths)")

# 7b. profile version, companion plugins, profile_lib in tools/ (doctor_extra.py; skipped when the copy is missing)
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from doctor_extra import checks as extra_checks
    for _lvl, _msg in extra_checks(root, Path(__file__).resolve().parent.parent):
        rep(_lvl, _msg)
except ImportError:
    print("INFO doctor_extra.py not in tools/ (profile and companion checks skipped; /kickoff:upgrade --refresh-tools)")
# 8. hook switches
dis = os.environ.get("KICKOFF_DISABLED_HOOKS", "")
rep("OK", f"hooks disabled via KICKOFF_DISABLED_HOOKS: {dis}" if dis else
    "all kickoff hooks active (KICKOFF_DISABLED_HOOKS=reindex,coauthor,rmrf turns some off)")

fails, warns = res.count("FAIL"), res.count("WARN")
print(f"\n{fails} fail, {warns} warn")
sys.exit(1 if fails else 0)

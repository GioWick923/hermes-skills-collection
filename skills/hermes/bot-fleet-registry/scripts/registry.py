import json, os, re, subprocess, time

JOB_START = re.compile(r"^\s{2}[0-9a-f]{12}\s*\[")

def main():
    local = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    skills_dir = os.path.join(local, "hermes", "skills")
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, "..", "registry.json")
    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "skills": [], "cronjobs": []}

    for root, dirs, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            p = os.path.join(root, "SKILL.md")
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            m = re.search(r"^name:\s*(.+)$", txt, re.M)
            d = re.search(r"^description:\s*(.+)$", txt, re.M)
            c = re.search(r"^category:\s*(.+)$", txt, re.M)
            out["skills"].append({
                "name": m.group(1).strip() if m else os.path.basename(os.path.dirname(p)),
                "description": d.group(1).strip()[:120] if d else "",
                "category": c.group(1).strip() if c else "",
                "path": os.path.relpath(p, skills_dir).replace("\\", "/"),
            })
    out["skills"].sort(key=lambda s: (s["category"], s["name"]))

    try:
        r = subprocess.run(["hermes", "cron", "list"], capture_output=True, text=True, timeout=60)
        out["cron_raw_exit"] = r.returncode
        cur = {}
        for ln in r.stdout.splitlines():
            s = ln.strip()
            if JOB_START.match(ln):
                if cur:
                    out["cronjobs"].append(cur)
                cur = {}
            elif s.startswith("Name:"):
                cur = {"name": s.split("Name:", 1)[1].strip()}
            elif s.startswith("Schedule:") and cur:
                cur["schedule"] = s.split("Schedule:", 1)[1].strip()
            elif s.startswith("Next run:") and cur:
                cur["next"] = s.split("Next run:", 1)[1].strip()
            elif s.startswith("Deliver:") and cur:
                cur["deliver"] = s.split("Deliver:", 1)[1].strip()
            elif s.startswith("Last run:") and cur:
                cur["last"] = s.split("Last run:", 1)[1].strip()
                low = cur["last"].lower()
                cur["status"] = "error" if ("error" in low or "failed" in low) else ("ok" if "ok" in low else "unknown")
            elif s.startswith("Execution:") and cur:
                cur["execution"] = s.split("Execution:", 1)[1].strip()
                out["cronjobs"].append(cur)
                cur = {}
        if cur:
            out["cronjobs"].append(cur)
    except Exception as e:
        out["cron_error"] = str(e)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(out['skills'])} skills, {len(out['cronjobs'])} cronjobs -> registry.json")

if __name__ == "__main__":
    main()

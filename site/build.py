#!/usr/bin/env python3
"""Build the single-file site: site/index.template.html -> site/index.html

- Embeds all 10 character SVGs as data URIs (so there are no id clashes between them).
- Swaps in the working name. Change NAME / change it on the command line to rename the whole site:
      python3 site/build.py "SI Agents"
- Connect the Coin Sniffer to a hosted coin-check agent (see agent/README.md):
      python3 site/build.py --agent-url=https://your-agent.example.com
"""
import base64, json, os, subprocess, sys
from pathlib import Path

here = Path(__file__).parent
root = here.parent
args = [a for a in sys.argv[1:] if not a.startswith("--artifact") and not a.startswith("--agent-url")]
AGENT_URL = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--agent-url=")), os.environ.get("AGENT_URL", ""))
ART = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--artifact=")), None)
NAME = args[0] if args else "SI Agents"

FILES = {
    "judge": root / "character" / "judge-si.svg",
    "sniffles": root / "character" / "cast" / "detective-sniffles.svg",
    "chef": root / "character" / "cast" / "chef-si.svg",
    "coach": root / "character" / "cast" / "coach-si.svg",
    "doctor": root / "character" / "cast" / "dr-heartbreak.svg",
    "anchor": root / "character" / "cast" / "anchor-si.svg",
    "professor": root / "character" / "cast" / "professor-si.svg",
    "dj": root / "character" / "cast" / "dj-si.svg",
    "banker": root / "character" / "cast" / "banker-si.svg",
    "astronaut": root / "character" / "cast" / "astronaut-si.svg",
}
# Realistic (AI-generated) art: drop full-size files into character/realistic/<stem>.png|jpg|webp
# (stems below). Any character without a file keeps its vector art. Override the folder with REAL_DIR=...
REAL_DIR = Path(os.environ.get("REAL_DIR", root / "character" / "realistic"))
STEMS = {
    "judge": "judge-si", "sniffles": "detective-sniffles", "chef": "chef-si", "coach": "coach-si",
    "doctor": "dr-heartbreak", "anchor": "anchor-si", "professor": "professor-si", "dj": "dj-si",
    "banker": "banker-si", "astronaut": "astronaut-si",
}

def realistic(key):
    for ext in ("png", "jpg", "jpeg", "webp"):
        f = REAL_DIR / f"{STEMS[key]}.{ext}"
        if f.exists():
            out = subprocess.run(
                ["convert", str(f), "-resize", "640x640>", "-strip", "-quality", "80", "jpeg:-"],
                capture_output=True, check=True,
            ).stdout
            return "data:image/jpeg;base64," + base64.b64encode(out).decode()
    return None

imgs, real = {}, {}
for k, p in FILES.items():
    r = realistic(k)
    real[k] = bool(r)
    imgs[k] = r or "data:image/svg+xml;base64," + base64.b64encode(p.read_bytes()).decode()

page = (here / "index.template.html").read_text()
page = page.replace("/*IMG_JSON*/{}", json.dumps(imgs)).replace("/*REAL_JSON*/{}", json.dumps(real))
page = page.replace("/*AGENT_URL*/''", json.dumps(AGENT_URL.strip()))
page = page.replace("{{NAME_UP}}", NAME.upper()).replace("{{NAME}}", NAME)
(here / "index.html").write_text(page)

if ART:
    # Fragment for the claude.ai page host: no html/head/body wrappers, no downloads, no outside fetches.
    import re
    a = page.replace("/*CAN_DL*/true", "false").replace("/*CAN_LIVE*/true", "false")  # the preview host blocks outside calls, so no agent there either
    a = re.sub(r"<title>.*?</title>", f"<title>{NAME}</title>", a, count=1, flags=re.S)
    for pat in (r"<!doctype html>\s*", r"<html[^>]*>\s*", r"<head>\s*", r"</head>\s*", r"<body>\s*", r"</body>\s*", r"</html>\s*",
                r"<meta charset[^>]*>\s*", r'<meta name="viewport"[^>]*>\s*', r'<meta name="color-scheme"[^>]*>\s*',
                r'<meta name="theme-color"[^>]*>\s*', r'<meta name="description"[^>]*>\s*'):
        a = re.sub(pat, "", a, flags=re.I)
    Path(ART).write_text(a)
    print(f"wrote page fragment {ART} ({len(a):,} bytes)")
print(f"wrote {here / 'index.html'} ({len(page):,} bytes) as '{NAME}'; realistic art for: {[k for k,v in real.items() if v] or 'none (vector art)'}")

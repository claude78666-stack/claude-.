#!/usr/bin/env python3
"""Build the single-file site: site/index.template.html -> site/index.html

- Embeds all 10 character SVGs as data URIs (so there are no id clashes between them).
- Swaps in the working name. Change NAME / change it on the command line to rename the whole site:
      python3 site/build.py "Tin Gods"
"""
import base64, json, sys
from pathlib import Path

here = Path(__file__).parent
root = here.parent
NAME = sys.argv[1] if len(sys.argv) > 1 else "Tin Gods"

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
imgs = {
    k: "data:image/svg+xml;base64," + base64.b64encode(p.read_bytes()).decode()
    for k, p in FILES.items()
}

page = (here / "index.template.html").read_text()
page = page.replace("/*IMG_JSON*/{}", json.dumps(imgs))
page = page.replace("{{NAME_UP}}", NAME.upper()).replace("{{NAME}}", NAME)
(here / "index.html").write_text(page)
print(f"wrote {here / 'index.html'} ({len(page):,} bytes) as '{NAME}'")

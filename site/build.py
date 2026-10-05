#!/usr/bin/env python3
"""Inline the Judge SI artwork into the page template -> site/index.html (single self-contained file)."""
from pathlib import Path

here = Path(__file__).parent
svg = (here.parent / "character" / "judge-si.svg").read_text()
svg = svg.replace(
    "<svg ",
    '<svg id="judgeSvg" role="img" aria-label="Judge SI, a chrome robot judge in a powdered wig holding a gavel" ',
    1,
)
page = (here / "index.template.html").read_text().replace("<!--JUDGE_SVG-->", svg)
(here / "index.html").write_text(page)
print("wrote", here / "index.html", len(page), "bytes")

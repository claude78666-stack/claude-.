"""YouTube channel banner (2560x1440) in the Toon Noon logo style.

YouTube shows the full image only on TVs. Desktop shows the middle 2560x423 strip
and phones the middle 1546x423 "safe area", so the logo and tagline sit inside
the safe area and the decoration lives outside it.
"""
import base64, os
from gen import word, heart, svg, W, GAP, INK, CREAM, CORAL, SUN, TEAL, GRAPE, D

BW, BH = 2560, 1440
SAFE_W, SAFE_H = 1546, 423
FONT = base64.b64encode(open(os.path.join(D, "fonts", "fredoka-600.woff2"), "rb").read()).decode()


def heart_disc(cx, cy):
    # Matches the profile picture: the last O is a solid sun with a heart cut out.
    return f'<circle cx="{cx}" cy="{cy}" r="74" fill="{SUN}"/>' + heart(cx, cy + 4, 3.6, CREAM)


def ring(cx, cy, r, w, color):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{w}"/>'


def dot(cx, cy, r, color):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'


# Wordmark: one line, scaled to fit the phone safe area with room to spare.
toon_w = sum(W[c] for c in "TOON") + 3 * GAP
noon_w = sum(W[c] for c in "NOON") + 3 * GAP
space = 90
mark_w = toon_w + space + noon_w
k = 0.8
mark = word("TOON", 0, 0, [CORAL, SUN], INK) + \
       word("NOON", toon_w + space, 0, [TEAL, SUN], INK, heart_disc)
tag_size, tag_gap = 58, 40
block_h = 200 * k + tag_gap + tag_size
top = (BH - block_h) / 2
mx = (BW - mark_w * k) / 2

parts = [
    f'<defs><style>@font-face{{font-family:"Fredoka";font-weight:600;'
    f'src:url(data:font/woff2;base64,{FONT}) format("woff2");}}</style></defs>',
    f'<rect width="{BW}" height="{BH}" fill="{CREAM}"/>',
    # TV-only corners: big soft shapes bleeding off the edges.
    ring(150, 150, 300, 90, CORAL), dot(2420, 170, 230, SUN),
    ring(2440, 1330, 280, 90, TEAL), dot(170, 1310, 210, GRAPE),
    # Desktop strip, either side of the safe area: small hearts and dots.
    heart(300, 640, 5.5, CORAL), dot(170, 790, 26, TEAL), dot(430, 820, 16, SUN),
    dot(120, 590, 14, GRAPE),
    heart(2270, 800, 5.5, TEAL), dot(2400, 630, 26, CORAL), dot(2140, 610, 16, GRAPE),
    dot(2460, 840, 14, SUN),
    f'<g transform="translate({mx},{top}) scale({k})">{mark}</g>',
    f'<text x="{BW/2}" y="{top + 200*k + tag_gap + tag_size*0.8}" text-anchor="middle" '
    f'font-family="Fredoka" font-weight="600" font-size="{tag_size}" fill="{INK}" '
    f'letter-spacing="1">Little stories, big hearts</text>',
]
open(os.path.join(D, "youtube-banner.svg"), "w").write(svg(BW, BH, "".join(parts[1:]), parts[0]))

# Guide overlay (not for upload): shows the phone safe area and desktop strip.
sx, sy = (BW - SAFE_W) / 2, (BH - SAFE_H) / 2
guide = "".join(parts[1:]) + \
    f'<rect x="0" y="{sy}" width="{BW}" height="{SAFE_H}" fill="none" stroke="#999" stroke-width="4" stroke-dasharray="20 14"/>' + \
    f'<rect x="{sx}" y="{sy}" width="{SAFE_W}" height="{SAFE_H}" fill="none" stroke="#e00" stroke-width="6" stroke-dasharray="24 14"/>'
open(os.path.join(D, "banner-guide.svg.txt"), "w").write(svg(BW, BH, guide, parts[0]))
print("wrote youtube-banner.svg")

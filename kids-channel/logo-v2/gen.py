"""Draws the Toon Noon logos as SVG. Letters are custom geometry, not a font."""
import os

D = os.path.dirname(os.path.abspath(__file__))
INK, CREAM = "#1F2A44", "#FFF8EC"
CORAL, SUN, TEAL, GRAPE = "#FF6B5B", "#FFC23C", "#1FB5A8", "#7B5CE0"
S, GAP = 52, 26          # stroke width, letter gap (letter height is 200)
W = {"T": 150, "N": 160, "O": 200}


def letter(ch, x, y, color, extra=""):
    st = f'stroke="{color}" stroke-width="{S}" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    if ch == "T":
        return f'<path d="M{x+26},{y+26} H{x+124} M{x+75},{y+26} V{y+174}" {st}/>'
    if ch == "N":
        return f'<path d="M{x+26},{y+174} V{y+26} L{x+134},{y+174} V{y+26}" {st}/>'
    return f'<circle cx="{x+100}" cy="{y+100}" r="74" {st}/>' + extra


def clock(cx, cy, color):
    # Both hands pointing straight up = 12 o'clock = noon.
    return (f'<path d="M{cx},{cy} V{cy-30}" stroke="{color}" stroke-width="18" stroke-linecap="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="11" fill="{color}"/>')


def heart(cx, cy, s, color):
    return (f'<path transform="translate({cx},{cy}) scale({s})" fill="{color}" '
            'd="M0,9 C-4,6 -11,1 -11,-4 C-11,-8 -8,-10.5 -5.5,-10.5 C-3,-10.5 -1,-9 0,-7 C1,-9 3,-10.5 5.5,-10.5 C8,-10.5 11,-8 11,-4 C11,1 4,6 0,9 Z"/>')


def word(text, x, y, colors, ink, special=None):
    out, oi = [], 0
    for ch in text:
        if ch == "O":
            c = colors[oi]
            extra = special(x + 100, y + 100) if special and oi == len(colors) - 1 else ""
            out.append(letter("O", x, y, c, extra))
            oi += 1
        else:
            out.append(letter(ch, x, y, ink))
        x += W[ch] + GAP
    return "".join(out)


def svg(w, h, body, bg):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{bg}{body}</svg>')


# 1. Wide wordmark: banner, watermark, end screens.
toon_w = sum(W[c] for c in "TOON") + 3 * GAP
noon_w = sum(W[c] for c in "NOON") + 3 * GAP
w1, h1 = 2000, 640
x = (w1 - (toon_w + 90 + noon_w)) / 2
body = word("TOON", x, 220, [CORAL, SUN], INK) + \
       word("NOON", x + toon_w + 90, 220, [TEAL, GRAPE], INK, lambda cx, cy: clock(cx, cy, INK))
logos = {"toon-noon-wordmark.svg": svg(w1, h1, body, f'<rect width="{w1}" height="{h1}" fill="{CREAM}"/>')}

# 2 and 3. Stacked square: the four O's line up into a 2x2 grid of colour.
def stacked(bg_color, ink, last_o):
    size = 1200
    x_noon = (size - noon_w) / 2
    x_toon = x_noon + (W["N"] - W["T"])          # align the O columns
    top = (size - (200 * 2 + 70)) / 2
    b = word("TOON", x_toon, top, [CORAL, SUN], ink) + \
        word("NOON", x_noon, top + 270, [TEAL, last_o[0]], ink, last_o[1])
    bg = f'<rect width="{size}" height="{size}" rx="0" fill="{bg_color}"/>'
    return svg(size, size, b, bg)

logos["toon-noon-stacked.svg"] = stacked(CREAM, INK, (GRAPE, lambda cx, cy: clock(cx, cy, INK)))
# Dark version: the last O becomes a solid sun with a heart in it (noon sun + kindness).
logos["toon-noon-stacked-dark.svg"] = stacked(
    INK, CREAM,
    (SUN, lambda cx, cy: f'<circle cx="{cx}" cy="{cy}" r="74" fill="{SUN}"/>' + heart(cx, cy + 4, 3.6, INK)))

for name, s in logos.items():
    open(os.path.join(D, name), "w").write(s)
print("wrote", ", ".join(logos))

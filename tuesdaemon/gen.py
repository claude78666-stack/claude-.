# Tuesdaemon: a small demon who only shows up on Tuesdays. 4 poses -> SVG -> PNG (Chromium) -> sheet.
import subprocess, pathlib
OUT = pathlib.Path(__file__).parent
BODY, DARK, LIGHT, HORN, INK = '#8b5cf6', '#5b34c4', '#c9b3ff', '#ffd166', '#150c33'

def eyes(k):
    if k in ('neutral', 'happy'):
        sq = 0 if k == 'neutral' else 14
        return f'''<g stroke="{INK}" stroke-width="7"><ellipse cx="215" cy="245" rx="38" ry="{44-sq}" fill="#fff6b0"/><ellipse cx="325" cy="245" rx="38" ry="{44-sq}" fill="#fff6b0"/></g>
<g fill="{INK}"><ellipse cx="217" cy="248" rx="9" ry="{28-sq}"/><ellipse cx="327" cy="248" rx="9" ry="{28-sq}"/></g>
<g fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"><path d="M172 {196+(0 if k=='happy' else 6)} L250 {212+(0 if k=='happy' else 6)}"/><path d="M368 {196+(0 if k=='happy' else 6)} L290 {212+(0 if k=='happy' else 6)}"/></g>'''
    if k == 'sleepy':
        return f'''<g fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"><path d="M178 250 Q215 275 252 250"/><path d="M288 250 Q325 275 362 250"/></g>
<g font-family="Arial Black, Arial" font-weight="900" fill="#fff" stroke="{INK}" stroke-width="2"><text x="395" y="150" font-size="44">Z</text><text x="430" y="110" font-size="34">z</text><text x="458" y="76" font-size="26">z</text></g>'''
    if k == 'shock':
        return f'''<g stroke="{INK}" stroke-width="7"><circle cx="212" cy="243" r="50" fill="#fff6b0"/><circle cx="328" cy="243" r="50" fill="#fff6b0"/></g>
<g fill="{INK}"><ellipse cx="212" cy="243" rx="5" ry="30"/><ellipse cx="328" cy="243" rx="5" ry="30"/></g>'''

def mouth(k):
    if k == 'neutral': return f'<path d="M242 320 Q270 336 298 320" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>'
    if k == 'happy': return f'<path d="M222 305 Q270 380 318 305Z" fill="{INK}"/><path d="M240 335 Q270 358 300 335 Q270 346 240 335Z" fill="#ff7a8a"/><path d="M236 306 l10 16 l10 -16Z M284 306 l10 16 l10 -16Z" fill="#fff"/>'
    if k == 'sleepy': return f'<ellipse cx="270" cy="332" rx="14" ry="10" fill="{INK}"/>'
    if k == 'shock': return f'<ellipse cx="270" cy="345" rx="30" ry="38" fill="{INK}"/><path d="M252 316 l8 14 l8 -14Z" fill="#fff"/>'

def card(k, label):
    return f'''<g transform="rotate({-6 if k!='sleepy' else 4} 270 470)"><rect x="195" y="425" width="150" height="100" rx="14" fill="#fff" stroke="{INK}" stroke-width="7"/>
<rect x="195" y="425" width="150" height="34" rx="14" fill="#ff5468" stroke="{INK}" stroke-width="7"/><rect x="198" y="445" width="144" height="14" fill="#ff5468"/>
<text x="270" y="503" text-anchor="middle" font-family="Arial Black, Arial" font-weight="900" font-size="40" fill="{INK}">{label}</text></g>'''

def svg(k, cap, label):
    wing = f'<path d="M150 260 Q60 190 70 120 Q110 150 140 140 Q120 175 160 200Z" fill="{DARK}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/><path d="M390 260 Q480 190 470 120 Q430 150 400 140 Q420 175 380 200Z" fill="{DARK}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 600" width="1080" height="1200">
<defs><radialGradient id="g" cx="38%" cy="28%" r="85%"><stop offset="0" stop-color="{LIGHT}"/><stop offset=".45" stop-color="{BODY}"/><stop offset="1" stop-color="{DARK}"/></radialGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a0f4d"/><stop offset="1" stop-color="#0a0620"/></linearGradient></defs>
<rect width="540" height="600" fill="url(#bg)"/>
<ellipse cx="270" cy="545" rx="150" ry="16" fill="#000" opacity=".4"/>
{wing}
<path d="M360 470 Q470 470 465 400 Q460 360 500 350" fill="none" stroke="{INK}" stroke-width="22" stroke-linecap="round"/><path d="M360 470 Q470 470 465 400 Q460 360 500 350" fill="none" stroke="{BODY}" stroke-width="10" stroke-linecap="round"/>
<path d="M500 322 L528 352 L498 372 L482 346Z" fill="#ff5468" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>
<ellipse cx="270" cy="450" rx="92" ry="85" fill="url(#g)" stroke="{INK}" stroke-width="9"/>
<ellipse cx="225" cy="535" rx="38" ry="18" fill="{DARK}" stroke="{INK}" stroke-width="8"/><ellipse cx="315" cy="535" rx="38" ry="18" fill="{DARK}" stroke="{INK}" stroke-width="8"/>
<path d="M160 190 Q135 110 190 70 Q195 130 225 160Z" fill="{HORN}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/><path d="M380 190 Q405 110 350 70 Q345 130 315 160Z" fill="{HORN}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>
<path d="M138 262 L95 232 L142 215Z M402 262 L445 232 L398 215Z" fill="{BODY}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>
<ellipse cx="270" cy="265" rx="140" ry="122" fill="url(#g)" stroke="{INK}" stroke-width="9"/>
<ellipse cx="190" cy="190" rx="40" ry="18" fill="#fff" opacity=".35" transform="rotate(-28 190 190)"/>
{eyes(k)}{mouth(k)}
<g fill="#ff7aa0" opacity=".5"><ellipse cx="160" cy="315" rx="24" ry="14"/><ellipse cx="380" cy="315" rx="24" ry="14"/></g>
{card(k, label)}
<ellipse cx="190" cy="470" rx="22" ry="20" fill="{BODY}" stroke="{INK}" stroke-width="8"/><ellipse cx="350" cy="470" rx="22" ry="20" fill="{BODY}" stroke="{INK}" stroke-width="8"/>
<text x="270" y="585" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="40" fill="#fff" stroke="{INK}" stroke-width="2">{cap}</text>
</svg>'''

POSES = [('neutral', "It's Tuesday.", 'TUE'), ('happy', 'TUESDAY!!', 'TUE'), ('sleepy', 'not Tuesday...', 'MON'), ('shock', 'IS IT WEDNESDAY?!', 'WED')]
for k, cap, label in POSES:
    (OUT / f'tuesdaemon-{k}.svg').write_text(svg(k, cap, label))
subprocess.run(['node', str(OUT / 'png.cjs')], check=True)
subprocess.run(['montage'] + [str(OUT / f'tuesdaemon-{k}.png') for k, _, _ in POSES] + ['-tile', '4x1', '-geometry', '540x600+6+6', '-background', '#0a0620', str(OUT / 'tuesdaemon-sheet.png')], check=True)

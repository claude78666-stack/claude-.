# Blorp: a round blob with a tiny mouth. Generates 4 poses as SVG, then PNG via ImageMagick.
import subprocess, pathlib
OUT = pathlib.Path(__file__).parent
BODY, DARK, LIGHT, INK = '#7dff6b', '#34c04a', '#c9ffb8', '#10240f'

def eyes(kind):
    if kind == 'neutral':
        return f'''<g fill="#fff" stroke="{INK}" stroke-width="7"><ellipse cx="205" cy="270" rx="44" ry="52"/><ellipse cx="335" cy="270" rx="44" ry="52"/></g>
<g fill="{INK}"><circle cx="212" cy="278" r="19"/><circle cx="328" cy="278" r="19"/></g><g fill="#fff"><circle cx="219" cy="269" r="7"/><circle cx="335" cy="269" r="7"/></g>'''
    if kind == 'happy':
        return f'''<g fill="none" stroke="{INK}" stroke-width="14" stroke-linecap="round"><path d="M165 285 Q205 225 245 285"/><path d="M295 285 Q335 225 375 285"/></g>'''
    if kind == 'sad':
        return f'''<g fill="#fff" stroke="{INK}" stroke-width="7"><ellipse cx="205" cy="275" rx="42" ry="48"/><ellipse cx="335" cy="275" rx="42" ry="48"/></g>
<g fill="{INK}"><circle cx="205" cy="292" r="19"/><circle cx="335" cy="292" r="19"/></g><g fill="#fff"><circle cx="212" cy="284" r="7"/><circle cx="342" cy="284" r="7"/></g>
<g fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"><path d="M160 240 L240 216"/><path d="M380 240 L300 216"/></g>
<path d="M165 335 Q150 380 165 395 Q185 380 165 335Z" fill="#7fd6ff"/>'''
    if kind == 'shock':
        return f'''<g fill="#fff" stroke="{INK}" stroke-width="7"><circle cx="200" cy="262" r="58"/><circle cx="340" cy="262" r="58"/></g>
<g fill="{INK}"><circle cx="200" cy="262" r="9"/><circle cx="340" cy="262" r="9"/></g>'''

def mouth(kind):
    if kind == 'neutral': return f'<ellipse cx="270" cy="372" rx="13" ry="10" fill="{INK}"/>'
    if kind == 'happy': return f'<path d="M225 350 Q270 410 315 350Z" fill="{INK}"/><path d="M243 372 Q270 392 297 372 Q270 382 243 372Z" fill="#ff7a8a"/>'
    if kind == 'sad': return f'<path d="M238 392 Q270 360 302 392" fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
    if kind == 'shock': return f'<ellipse cx="270" cy="385" rx="26" ry="34" fill="{INK}"/>'

def svg(pose, caption):
    tilt = {'neutral': 0, 'happy': -4, 'sad': 3, 'shock': 0}[pose]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 600" width="1080" height="1200">
<defs><radialGradient id="g" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="{LIGHT}"/><stop offset=".45" stop-color="{BODY}"/><stop offset="1" stop-color="{DARK}"/></radialGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1a1240"/><stop offset="1" stop-color="#0a0620"/></linearGradient></defs>
<rect width="540" height="600" fill="url(#bg)"/>
<ellipse cx="270" cy="505" rx="150" ry="22" fill="#000" opacity=".35"/>
<g transform="rotate({tilt} 270 330)">
<path d="M270 105 C400 105 465 200 470 320 C474 430 410 505 270 505 C130 505 66 430 70 320 C75 200 140 105 270 105Z" fill="url(#g)" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>
<ellipse cx="170" cy="170" rx="42" ry="22" fill="#fff" opacity=".45" transform="rotate(-30 170 170)"/>
<path d="M250 108 Q262 70 285 62" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round"/><circle cx="288" cy="60" r="15" fill="{BODY}" stroke="{INK}" stroke-width="8"/>
{eyes(pose)}{mouth(pose)}
<g fill="#ff9aa8" opacity=".55"><ellipse cx="150" cy="345" rx="26" ry="15"/><ellipse cx="390" cy="345" rx="26" ry="15"/></g>
</g>
<text x="270" y="568" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="46" fill="#fff" stroke="{INK}" stroke-width="2">{caption}</text>
</svg>'''

for pose, cap in [('neutral', 'Blorp.'), ('happy', 'BLORP!'), ('sad', 'blorp...'), ('shock', 'BLORP?!')]:
    p = OUT / f'blorp-{pose}.svg'
    p.write_text(svg(pose, cap))
subprocess.run(['node', str(OUT / 'png.cjs')], check=True)
subprocess.run(['montage'] + [str(OUT / f'blorp-{x}.png') for x in ['neutral', 'happy', 'sad', 'shock']] + ['-tile', '4x1', '-geometry', '540x600+6+6', '-background', '#0a0620', str(OUT / 'blorp-sheet.png')], check=True)

# Bearcat Bob: bear + cat + crab claws. "Hugs hard. Pinches harder." 4 poses -> SVG -> PNG -> sheet.
import subprocess, pathlib
OUT = pathlib.Path(__file__).parent
FUR, DARK, LIGHT, CREAM, CLAW, CLAWD, INK = '#c98a52', '#8f5a30', '#f0c08a', '#fff0d6', '#ff5a3c', '#c8321c', '#25140a'

def claw(cx, cy, s, op):
    """Crab pincer facing outward. s=-1 left, 1 right. op = how wide it is open."""
    x = lambda dx: cx + s * dx
    up = f'M{x(0)} {cy-24} C{x(40)} {cy-34-op} {x(78)} {cy-26-op} {x(90)} {cy-10-op*.6} C{x(62)} {cy-14-op*.3} {x(36)} {cy-8} {x(0)} {cy+2}Z'
    lo = f'M{x(0)} {cy+24} C{x(40)} {cy+34+op} {x(78)} {cy+26+op} {x(90)} {cy+10+op*.6} C{x(62)} {cy+14+op*.3} {x(36)} {cy+8} {x(0)} {cy-2}Z'
    return f'''<path d="{up}" fill="{CLAW}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/><path d="{lo}" fill="{CLAW}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>
<circle cx="{cx}" cy="{cy}" r="34" fill="{CLAW}" stroke="{INK}" stroke-width="8"/><path d="M{x(-18)} {cy-14} Q{x(-4)} {cy-24} {x(12)} {cy-16}" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".6"/>'''

def eyes(k):
    if k == 'neutral':
        return f'<g stroke="{INK}" stroke-width="7"><circle cx="212" cy="215" r="32" fill="#fff"/><circle cx="328" cy="215" r="32" fill="#fff"/></g><g fill="{INK}"><circle cx="216" cy="220" r="17"/><circle cx="332" cy="220" r="17"/></g><g fill="#fff"><circle cx="222" cy="213" r="6"/><circle cx="338" cy="213" r="6"/></g>'
    if k == 'happy':
        return f'<g fill="none" stroke="{INK}" stroke-width="12" stroke-linecap="round"><path d="M178 228 Q212 182 246 228"/><path d="M294 228 Q328 182 362 228"/></g>'
    if k == 'pinch':
        return f'<g stroke="{INK}" stroke-width="7"><circle cx="212" cy="222" r="30" fill="#fff"/><circle cx="328" cy="222" r="30" fill="#fff"/></g><g fill="{INK}"><circle cx="218" cy="228" r="16"/><circle cx="322" cy="228" r="16"/></g><g fill="#fff"><circle cx="224" cy="222" r="5"/><circle cx="328" cy="222" r="5"/></g><g fill="none" stroke="{INK}" stroke-width="12" stroke-linecap="round"><path d="M168 168 L246 196"/><path d="M372 168 L294 196"/></g>'
    if k == 'shock':
        return f'<g stroke="{INK}" stroke-width="7"><circle cx="208" cy="212" r="42" fill="#fff"/><circle cx="332" cy="212" r="42" fill="#fff"/></g><g fill="{INK}"><circle cx="208" cy="212" r="8"/><circle cx="332" cy="212" r="8"/></g>'

def mouth(k):
    nose = f'<path d="M252 262 L288 262 L270 282Z" fill="#ff8aa0" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
    base = f'<path d="M270 282 L270 296"  stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
    if k == 'neutral': return nose + base + f'<path d="M236 296 Q253 312 270 296 Q287 312 304 296" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
    if k == 'happy': return nose + base + f'<path d="M232 296 Q270 350 308 296Z" fill="{INK}"/><path d="M250 326 Q270 340 290 326 Q270 332 250 326Z" fill="#ff7a8a"/>'
    if k == 'pinch': return nose + base + f'<path d="M240 312 Q270 292 300 312" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/><path d="M252 306 l8 12 l8 -12Z M272 306 l8 12 l8 -12Z" fill="#fff" stroke="{INK}" stroke-width="3"/>'
    if k == 'shock': return nose + base + f'<ellipse cx="270" cy="324" rx="22" ry="26" fill="{INK}"/>'

def whiskers():
    return f'<g stroke="{INK}" stroke-width="4" stroke-linecap="round" fill="none" opacity=".8"><path d="M205 280 L135 268"/><path d="M205 292 L132 296"/><path d="M207 304 L142 322"/><path d="M335 280 L405 268"/><path d="M335 292 L408 296"/><path d="M333 304 L398 322"/></g>'

def svg(k, cap):
    op = {'neutral': 4, 'happy': 22, 'pinch': 34, 'shock': 14}[k]
    ly = {'neutral': 440, 'happy': 400, 'pinch': 430, 'shock': 380}[k]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 600" width="1080" height="1200">
<defs><radialGradient id="g" cx="38%" cy="28%" r="85%"><stop offset="0" stop-color="{LIGHT}"/><stop offset=".5" stop-color="{FUR}"/><stop offset="1" stop-color="{DARK}"/></radialGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0c3a4a"/><stop offset="1" stop-color="#06141c"/></linearGradient></defs>
<rect width="540" height="600" fill="url(#bg)"/>
<ellipse cx="270" cy="548" rx="160" ry="16" fill="#000" opacity=".4"/>
<path d="M345 505 Q410 578 478 540 Q514 516 496 486" fill="none" stroke="{INK}" stroke-width="34" stroke-linecap="round"/><path d="M345 505 Q410 578 478 540 Q514 516 496 486" fill="none" stroke="{FUR}" stroke-width="20" stroke-linecap="round"/>
<path d="M410 560 l-4 -18 M450 556 l2 -18" stroke="{DARK}" stroke-width="8" stroke-linecap="round"/>
<ellipse cx="270" cy="445" rx="108" ry="100" fill="url(#g)" stroke="{INK}" stroke-width="9"/>
<ellipse cx="270" cy="465" rx="62" ry="62" fill="{CREAM}" opacity=".9"/>
<ellipse cx="205" cy="540" rx="42" ry="20" fill="{DARK}" stroke="{INK}" stroke-width="8"/><ellipse cx="335" cy="540" rx="42" ry="20" fill="{DARK}" stroke="{INK}" stroke-width="8"/>
<path d="M178 410 L{128 if k!='happy' else 135} {ly+6}" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><path d="M178 410 L{128 if k!='happy' else 135} {ly+6}" stroke="{FUR}" stroke-width="26" stroke-linecap="round"/>
<path d="M362 410 L{412 if k!='happy' else 405} {ly+6}" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><path d="M362 410 L{412 if k!='happy' else 405} {ly+6}" stroke="{FUR}" stroke-width="26" stroke-linecap="round"/>
{claw(112 if k!='happy' else 122, ly, -1, op)}{claw(428 if k!='happy' else 418, ly, 1, op)}
<circle cx="150" cy="128" r="52" fill="url(#g)" stroke="{INK}" stroke-width="9"/><circle cx="390" cy="128" r="52" fill="url(#g)" stroke="{INK}" stroke-width="9"/>
<circle cx="152" cy="132" r="26" fill="#e8a7a0" opacity=".85"/><circle cx="388" cy="132" r="26" fill="#e8a7a0" opacity=".85"/>
<ellipse cx="270" cy="225" rx="146" ry="126" fill="url(#g)" stroke="{INK}" stroke-width="9"/>
<ellipse cx="190" cy="150" rx="40" ry="16" fill="#fff" opacity=".35" transform="rotate(-25 190 150)"/>
<ellipse cx="270" cy="296" rx="82" ry="58" fill="{CREAM}" stroke="{INK}" stroke-width="6"/>
{eyes(k)}{mouth(k)}{whiskers()}
<g fill="#ff8aa0" opacity=".4"><ellipse cx="160" cy="288" rx="22" ry="13"/><ellipse cx="380" cy="288" rx="22" ry="13"/></g>
<text x="270" y="590" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="40" fill="#fff" stroke="{INK}" stroke-width="2">{cap}</text>
</svg>'''

POSES = [('neutral', 'Bob.'), ('happy', 'Hugs hard.'), ('pinch', 'Pinches harder.'), ('shock', 'BOB?!')]
for k, cap in POSES:
    (OUT / f'bearcat-{k}.svg').write_text(svg(k, cap))
subprocess.run(['node', str(OUT / 'png.cjs')], check=True)
subprocess.run(['montage'] + [str(OUT / f'bearcat-{k}.png') for k, _ in POSES] + ['-tile', '4x1', '-geometry', '540x600+6+6', '-background', '#06141c', str(OUT / 'bearcat-sheet.png')], check=True)

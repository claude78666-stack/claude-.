# 15 crypto-lore hybrid mascots, drawn from a shared part library (vector, no image credits needed).
import subprocess, pathlib
OUT = pathlib.Path(__file__).parent
INK = '#1a0f1f'

def sh(h, f):
    h = h.lstrip('#'); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    t = 255 if f > 0 else 0; f = abs(f)
    return '#%02x%02x%02x' % tuple(round(c + (t - c) * f) for c in (r, g, b))

def grad(i, c):
    return f'<radialGradient id="{i}" cx="38%" cy="28%" r="85%"><stop offset="0" stop-color="{sh(c,.38)}"/><stop offset=".5" stop-color="{c}"/><stop offset="1" stop-color="{sh(c,-.32)}"/></radialGradient>'

def S(w=8): return f'stroke="{INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'

# ---------- behind-body parts ----------
def tail(k, c):
    d = sh(c, -.3)
    if k == 'shiba': return f'<path d="M355 490 Q455 480 448 405 Q445 365 405 372" fill="none" stroke="{INK}" stroke-width="44" stroke-linecap="round"/><path d="M355 490 Q455 480 448 405 Q445 365 405 372" fill="none" stroke="{c}" stroke-width="30" stroke-linecap="round"/><circle cx="405" cy="372" r="15" fill="#fff6e6"/>'
    if k == 'squirrel': return f'<path d="M350 500 C470 520 520 420 470 330 C450 300 410 330 430 380 C440 410 400 450 350 450Z" fill="{c}" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/><path d="M440 350 C470 380 470 440 420 480" fill="none" stroke="{d}" stroke-width="8" stroke-linecap="round"/>'
    if k == 'whale': return f'<path d="M350 510 Q430 520 450 450" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><path d="M350 510 Q430 520 450 450" fill="none" stroke="{c}" stroke-width="26" stroke-linecap="round"/><path d="M450 450 Q405 420 395 380 Q430 395 450 430 Q470 395 505 380 Q495 420 450 450Z" fill="{c}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
    if k == 'cat': return f'<path d="M345 505 Q410 578 478 540 Q514 516 496 486" fill="none" stroke="{INK}" stroke-width="34" stroke-linecap="round"/><path d="M345 505 Q410 578 478 540 Q514 516 496 486" fill="none" stroke="{c}" stroke-width="20" stroke-linecap="round"/><path d="M410 560 l-4 -18 M450 556 l2 -18" stroke="{d}" stroke-width="8" stroke-linecap="round"/>'
    if k == 'snake': return f'<path d="M330 520 Q250 590 170 540 Q110 505 60 560 Q40 580 70 585" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><path d="M330 520 Q250 590 170 540 Q110 505 60 560 Q40 580 70 585" fill="none" stroke="{c}" stroke-width="26" stroke-linecap="round"/>'
    if k == 'bull': return f'<path d="M355 500 Q440 500 450 450" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round"/><path d="M450 450 Q430 430 440 410 Q465 430 462 460 Q470 480 450 450Z" fill="#3a2418" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
    if k == 'shrimp': return f'<path d="M345 500 Q430 520 440 450 Q448 410 410 405" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><path d="M345 500 Q430 520 440 450 Q448 410 410 405" fill="none" stroke="{c}" stroke-width="26" stroke-linecap="round"/><path d="M425 505 l10 -10 M437 480 l12 -6 M440 450 l14 0" stroke="{d}" stroke-width="7" stroke-linecap="round"/><path d="M410 405 l-24 -14 l6 28Z" fill="{c}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
    return ''

def back_extra(e, c):
    o = ''
    if 'fin' in e: o += f'<path d="M345 400 L420 300 L400 420Z" fill="{sh(c,-.15)}" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>'
    if 'elephant' in e: o += f'<ellipse cx="88" cy="250" rx="72" ry="92" fill="{sh(c,-.1)}" stroke="{INK}" stroke-width="9"/><ellipse cx="95" cy="255" rx="42" ry="62" fill="#e8a7a0" opacity=".8"/><ellipse cx="452" cy="250" rx="72" ry="92" fill="{sh(c,-.1)}" stroke="{INK}" stroke-width="9"/><ellipse cx="445" cy="255" rx="42" ry="62" fill="#e8a7a0" opacity=".8"/>'
    if 'antennae' in e: o += f'<path d="M215 120 Q180 40 120 30" fill="none" {S(7)}/><path d="M325 120 Q360 40 420 30" fill="none" {S(7)}/><circle cx="120" cy="30" r="8" fill="{c}" stroke="{INK}" stroke-width="5"/><circle cx="420" cy="30" r="8" fill="{c}" stroke="{INK}" stroke-width="5"/>'
    return o

# ---------- ears / horns ----------
def ears(k, c):
    if k == 'bear': return f'<circle cx="150" cy="128" r="50" fill="url(#h)" {S(9)}/><circle cx="390" cy="128" r="50" fill="url(#h)" {S(9)}/><circle cx="152" cy="132" r="25" fill="#e8a7a0" opacity=".85"/><circle cx="388" cy="132" r="25" fill="#e8a7a0" opacity=".85"/>'
    if k == 'shiba': return f'<path d="M140 170 L150 62 L232 125Z" fill="url(#h)" {S(9)}/><path d="M400 170 L390 62 L308 125Z" fill="url(#h)" {S(9)}/><path d="M158 140 L160 92 L206 126Z" fill="#fff0d6"/><path d="M382 140 L380 92 L334 126Z" fill="#fff0d6"/>'
    if k == 'cat': return f'<path d="M142 150 Q120 70 190 62 Q225 90 232 130Z" fill="url(#h)" {S(9)}/><path d="M398 150 Q420 70 350 62 Q315 90 308 130Z" fill="url(#h)" {S(9)}/><path d="M160 135 Q150 95 188 88 Q205 105 210 128Z" fill="#ff9aa8" opacity=".8"/><path d="M380 135 Q390 95 352 88 Q335 105 330 128Z" fill="#ff9aa8" opacity=".8"/>'
    if k == 'hippo': return f'<ellipse cx="140" cy="148" rx="28" ry="24" fill="url(#h)" {S(8)}/><ellipse cx="400" cy="148" rx="28" ry="24" fill="url(#h)" {S(8)}/><ellipse cx="140" cy="150" rx="14" ry="12" fill="#e8a7a0"/><ellipse cx="400" cy="150" rx="14" ry="12" fill="#e8a7a0"/>'
    if k == 'ape': return f'<circle cx="120" cy="250" r="40" fill="url(#h)" {S(9)}/><circle cx="420" cy="250" r="40" fill="url(#h)" {S(9)}/><circle cx="122" cy="252" r="22" fill="#e8b79b"/><circle cx="418" cy="252" r="22" fill="#e8b79b"/>'
    if k == 'goat': return f'<path d="M205 140 Q180 60 130 70 Q110 76 118 96 Q150 88 175 140Z" fill="#f1e4c8" {S(8)}/><path d="M335 140 Q360 60 410 70 Q430 76 422 96 Q390 88 365 140Z" fill="#f1e4c8" {S(8)}/><path d="M150 86 l10 18 M170 100 l8 16 M390 86 l-10 18 M370 100 l-8 16" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
    if k == 'bull': return f'<path d="M165 165 Q90 150 70 80 Q110 100 150 100 Q160 130 195 140Z" fill="#fff0d6" {S(9)}/><path d="M375 165 Q450 150 470 80 Q430 100 390 100 Q380 130 345 140Z" fill="#fff0d6" {S(9)}/>'
    if k == 'unicorn': return f'<path d="M245 128 L270 6 L295 128Z" fill="url(#rb)" {S(9)}/><path d="M252 100 l36 -12 M257 70 l26 -9 M262 42 l16 -5" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".8"/>'
    return ''

def eyes(k, hc):
    if k == 'round':
        return f'<g stroke="{INK}" stroke-width="7"><circle cx="212" cy="225" r="32" fill="#fff"/><circle cx="328" cy="225" r="32" fill="#fff"/></g><g fill="{INK}"><circle cx="217" cy="230" r="17"/><circle cx="333" cy="230" r="17"/></g><g fill="#fff"><circle cx="223" cy="223" r="6"/><circle cx="339" cy="223" r="6"/></g>'
    if k == 'frog':
        return f'<g stroke="{INK}" stroke-width="8"><circle cx="195" cy="132" r="52" fill="url(#h)"/><circle cx="345" cy="132" r="52" fill="url(#h)"/><circle cx="195" cy="136" r="36" fill="#fff"/><circle cx="345" cy="136" r="36" fill="#fff"/></g><g fill="{INK}"><circle cx="200" cy="142" r="18"/><circle cx="350" cy="142" r="18"/></g><g fill="#fff"><circle cx="207" cy="134" r="6"/><circle cx="357" cy="134" r="6"/></g>'
    if k == 'sleepy':
        return f'<g stroke="{INK}" stroke-width="7"><ellipse cx="212" cy="232" rx="34" ry="30" fill="#fff"/><ellipse cx="328" cy="232" rx="34" ry="30" fill="#fff"/></g><g fill="{INK}"><circle cx="214" cy="242" r="15"/><circle cx="330" cy="242" r="15"/></g><path d="M176 232 Q212 196 248 232 L248 214 Q212 190 176 214Z" fill="{hc}" {S(7)}/><path d="M292 232 Q328 196 364 232 L364 214 Q328 190 292 214Z" fill="{hc}" {S(7)}/><path d="M176 232 L248 232 M292 232 L364 232" {S(7)}/>'
    if k == 'angry':
        return eyes('round', hc) + f'<g fill="none" {S(11)}><path d="M168 186 L246 208"/><path d="M372 186 L294 208"/></g>'
    if k == 'stalk':
        return f'<g {S(8)} fill="none"><path d="M205 150 L205 105"/><path d="M335 150 L335 105"/></g><g stroke="{INK}" stroke-width="7"><circle cx="205" cy="92" r="30" fill="#fff"/><circle cx="335" cy="92" r="30" fill="#fff"/></g><g fill="{INK}"><circle cx="209" cy="97" r="15"/><circle cx="339" cy="97" r="15"/></g>'

def mouth(k, my=305):
    if k == 'smile': return f'<path d="M236 {my} Q270 {my+26} 304 {my}" fill="none" {S(7)}/>'
    if k == 'wide': return f'<path d="M150 {my-8} Q270 {my+60} 390 {my-8}" fill="none" {S(9)}/>'
    if k == 'open': return f'<ellipse cx="270" cy="{my+14}" rx="28" ry="34" fill="{INK}"/><ellipse cx="270" cy="{my+28}" rx="16" ry="12" fill="#ff7a8a"/>'
    if k == 'grin': return f'<path d="M222 {my-8} Q270 {my+66} 318 {my-8}Z" fill="{INK}" {S(6)}/><path d="M243 {my+24} Q270 {my+40} 297 {my+24} Q270 {my+32} 243 {my+24}Z" fill="#ff7a8a"/>'
    if k == 'teeth':
        t = ''.join(f'<path d="M{x} {my-4} l11 22 l11 -22Z" fill="#fff" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>' for x in range(194, 346, 25))
        return f'<path d="M180 {my-10} Q270 {my+56} 360 {my-10}Z" fill="{INK}" {S(7)}/>' + t
    if k == 'hippo': return f'<path d="M185 {my} Q270 {my+48} 355 {my}" fill="none" {S(8)}/><circle cx="230" cy="{my-34}" r="8" fill="{INK}"/><circle cx="310" cy="{my-34}" r="8" fill="{INK}"/>'

def nose(k):
    if k == 'cat': return f'<path d="M252 266 L288 266 L270 286Z" fill="#ff8aa0" {S(6)}/>'
    if k == 'dog': return f'<ellipse cx="270" cy="272" rx="22" ry="15" fill="{INK}"/><ellipse cx="264" cy="267" rx="6" ry="3" fill="#fff" opacity=".6"/>'
    if k == 'beak': return f'<path d="M220 280 Q270 250 320 280 Q270 330 220 280Z" fill="#ff9a2e" {S(8)}/>'
    return ''

def arms(k, c, ly=440):
    ln = f'<path d="M178 410 L135 {ly}" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><path d="M178 410 L135 {ly}" stroke="{c}" stroke-width="26" stroke-linecap="round"/><path d="M362 410 L405 {ly}" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><path d="M362 410 L405 {ly}" stroke="{c}" stroke-width="26" stroke-linecap="round"/>'
    if k == 'hand': return ln + f'<circle cx="128" cy="{ly+8}" r="27" fill="{c}" {S(8)}/><circle cx="412" cy="{ly+8}" r="27" fill="{c}" {S(8)}/>'
    if k == 'ape':
        ln = f'<path d="M180 400 Q110 440 100 520" fill="none" stroke="{INK}" stroke-width="44" stroke-linecap="round"/><path d="M180 400 Q110 440 100 520" fill="none" stroke="{c}" stroke-width="30" stroke-linecap="round"/><path d="M360 400 Q430 440 440 520" fill="none" stroke="{INK}" stroke-width="44" stroke-linecap="round"/><path d="M360 400 Q430 440 440 520" fill="none" stroke="{c}" stroke-width="30" stroke-linecap="round"/>'
        return ln + f'<circle cx="100" cy="528" r="32" fill="{c}" {S(8)}/><circle cx="440" cy="528" r="32" fill="{c}" {S(8)}/>'
    if k == 'flipper': return f'<path d="M185 395 Q95 430 105 500 Q135 470 185 440Z" fill="{c}" {S(9)}/><path d="M355 395 Q445 430 435 500 Q405 470 355 440Z" fill="{c}" {S(9)}/>'
    if k == 'claw':
        def claw(cx, s):
            x = lambda dx: cx + s * dx
            cy = ly
            up = f'M{x(0)} {cy-24} C{x(40)} {cy-44} {x(78)} {cy-36} {x(90)} {cy-18} C{x(62)} {cy-14} {x(36)} {cy-8} {x(0)} {cy+2}Z'
            lo = f'M{x(0)} {cy+24} C{x(40)} {cy+44} {x(78)} {cy+36} {x(90)} {cy+18} C{x(62)} {cy+14} {x(36)} {cy+8} {x(0)} {cy-2}Z'
            return f'<path d="{up}" fill="#ff5a3c" {S(8)}/><path d="{lo}" fill="#ff5a3c" {S(8)}/><circle cx="{cx}" cy="{cy}" r="34" fill="#ff5a3c" {S(8)}/><path d="M{x(-18)} {cy-14} Q{x(-4)} {cy-24} {x(12)} {cy-16}" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".6"/>'
        return ln + claw(112, -1) + claw(428, 1)
    return ln

def svg(sp):
    hc, bc = sp['head'], sp['body']
    bel = sp.get('belly')
    e = sp.get('extra', [])
    o = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 660" width="1080" height="1320"><defs>{grad("h", hc)}{grad("b", bc)}<linearGradient id="rb" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ff7ad9"/><stop offset=".5" stop-color="#ffd166"/><stop offset="1" stop-color="#7affd9"/></linearGradient><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{sp["bg"][0]}"/><stop offset="1" stop-color="{sp["bg"][1]}"/></linearGradient></defs><rect width="540" height="660" fill="url(#bg)"/><ellipse cx="270" cy="556" rx="165" ry="16" fill="#000" opacity=".4"/>'
    o += back_extra(e, bc) + tail(sp.get('tail'), sp.get('tailc', bc))
    o += f'<ellipse cx="270" cy="450" rx="106" ry="98" fill="url(#b)" {S(9)}/>'
    if bel: o += f'<ellipse cx="270" cy="470" rx="64" ry="66" fill="{bel}" opacity=".95"/>'
    if 'shell' in e: o += ''.join(f'<path d="M{190+i*0} {410+i*30} Q270 {440+i*30} 350 {410+i*30}" fill="none" stroke="{sh(bc,-.35)}" stroke-width="7" stroke-linecap="round"/>' for i in range(3))
    o += f'<ellipse cx="205" cy="548" rx="42" ry="20" fill="{sh(bc,-.2)}" {S(8)}/><ellipse cx="335" cy="548" rx="42" ry="20" fill="{sh(bc,-.2)}" {S(8)}/>'
    o += arms(sp.get('arms', 'hand'), sp.get('armc', bc), sp.get('ly', 440))
    if sp.get('earsback', True): o += ears(sp.get('ears'), hc)
    for x in sp.get('ears2', []): o += ears(x, hc)
    o += f'<ellipse cx="270" cy="240" rx="146" ry="126" fill="url(#h)" {S(9)}/><ellipse cx="190" cy="165" rx="40" ry="16" fill="#fff" opacity=".3" transform="rotate(-25 190 165)"/>'
    if sp.get('muzzle'): o += f'<ellipse cx="270" cy="298" rx="84" ry="58" fill="{sp["muzzle"]}" {S(6)}/>'
    o += eyes(sp.get('eyes', 'round'), hc) + nose(sp.get('nose')) + mouth(sp.get('mouth', 'smile'), sp.get('my', 305))
    if 'cheeks' in e: o += '<circle cx="160" cy="296" r="30" fill="#ff8aa0" opacity=".65"/><circle cx="380" cy="296" r="30" fill="#ff8aa0" opacity=".65"/>'
    else: o += '<g fill="#ff8aa0" opacity=".35"><ellipse cx="158" cy="292" rx="22" ry="13"/><ellipse cx="382" cy="292" rx="22" ry="13"/></g>'
    if 'beard' in e: o += f'<path d="M238 340 Q270 420 302 340Q270 360 238 340Z" fill="#f1e4c8" {S(7)}/>'
    if 'trunk' in e: o += f'<path d="M270 250 Q270 330 300 380 Q330 420 300 440" fill="none" stroke="{INK}" stroke-width="46" stroke-linecap="round"/><path d="M270 250 Q270 330 300 380 Q330 420 300 440" fill="none" stroke="{hc}" stroke-width="32" stroke-linecap="round"/>'
    if 'whiskers' in e: o += f'<g stroke="{INK}" stroke-width="4" stroke-linecap="round" fill="none" opacity=".8"><path d="M205 285 L135 273"/><path d="M205 297 L132 301"/><path d="M335 285 L405 273"/><path d="M335 297 L408 301"/></g>'
    if 'tusks' in e: o += f'<path d="M215 335 l-8 36 l22 -26Z M325 335 l8 36 l-22 -26Z" fill="#fff" {S(5)}/>'
    o += f'<text x="270" y="598" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="38" fill="#fff" stroke="{INK}" stroke-width="2">{sp["name"]}</text>'
    o += f'<text x="270" y="632" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="21" fill="#ffd166">{sp["ticker"]}  ·  {sp["parts"]}</text></svg>'
    return o

PEPE, PENG, SHIB, HIPPO, GOAT, SLOTH, BEAR, BULL = '#5fae48', '#2b3347', '#e9a35b', '#b9a3b8', '#efe5cf', '#a9835a', '#8b5a35', '#7a4a2a'
BLUE, WHALE, APE, CRAB, GREY = '#5b8fd1', '#6c8aa8', '#7a5238', '#e85a3c', '#8ea1b5'
C = [
 dict(id='01-pepenguin-doge', name='Pepenguin Doge', ticker='$PEPENGU', parts='frog + penguin + shiba', head=PEPE, body=PENG, belly='#f4f1ea', eyes='frog', mouth='wide', my=312, arms='flipper', armc=PENG, tail='shiba', tailc=SHIB, bg=('#13351d', '#06140a')),
 dict(id='02-goatloth', name='Goatloth', ticker='$GOATLOTH', parts='goat + sloth + shiba', head=GOAT, body=SHIB, belly='#fff0d6', ears='hippo', ears2=['goat'], eyes='sleepy', nose='dog', mouth='smile', my=312, extra=['beard'], muzzle='#fff6e6', arms='hand', armc=SHIB, tail='shiba', tailc=SHIB, bg=('#3a2a14', '#120b04')),
 dict(id='03-ponkehippo', name='Ponkehippo', ticker='$PONKEHIPPO', parts='monkey + moo deng + frog', head=HIPPO, body='#8d7a8f', belly='#d9c6d9', ears='ape', eyes='frog', mouth='hippo', my=312, extra=['cheeks'], arms='ape', armc='#8d7a8f', bg=('#3a1f3a', '#12071a')),
 dict(id='04-peanut-popcat', name='Peanut Popcat', ticker='$PNUTCAT', parts='squirrel + cat + shiba', head='#f6efe6', body=SHIB, belly='#fff6e6', ears='shiba', eyes='round', mouth='open', my=312, nose='cat', extra=['whiskers'], arms='hand', armc=SHIB, tail='squirrel', tailc='#a86b3c', bg=('#4a2a0e', '#150a03')),
 dict(id='05-slerfguin', name='Slerfguin', ticker='$SLERFGUIN', parts='sloth + penguin + goat', head=SLOTH, body=SLOTH, belly='#e6d2b0', ears='hippo', eyes='sleepy', mouth='smile', my=315, extra=['beard'], muzzle='#d9bf98', arms='flipper', armc=PENG, bg=('#2a2a1a', '#0d0d06')),
 dict(id='06-frogoat-prime', name='Frogoat Prime', ticker='$FROGOAT', parts='frog + goat + hippo', head=PEPE, body=sh(PEPE, -.1), belly='#cfe8a8', ears='goat', eyes='frog', mouth='hippo', my=312, extra=['beard'], arms='hand', armc=PEPE, bg=('#0e3b2e', '#04140f')),
 dict(id='07-bullbear-whale', name='Bullbear Whale', ticker='$BULLWHALE', parts='bull + bear + whale', head=BEAR, body=WHALE, belly='#e6eef5', ears='bull', ears2=['bear'], eyes='angry', nose='dog', mouth='smile', my=315, muzzle='#d9b48a', arms='flipper', armc=WHALE, tail='whale', tailc=WHALE, bg=('#14304f', '#050f1c')),
 dict(id='08-shrimpape', name='Shrimpape', ticker='$SHRIMPAPE', parts='shrimp + ape + dolphin', head=APE, body='#ff9a6a', belly='#ffd3b0', ears='ape', eyes='round', mouth='grin', my=312, muzzle='#e8b79b', extra=['antennae', 'shell'], arms='ape', armc=APE, tail='shrimp', tailc='#ff9a6a', bg=('#4a1a2a', '#15060c')),
 dict(id='09-crabcorn', name='Crabcorn', ticker='$CRABCORN', parts='crab + unicorn + bull', head=CRAB, body=sh(CRAB, -.1), belly='#ffd0c0', ears='unicorn', ears2=['bull'], eyes='stalk', mouth='grin', my=320, arms='claw', ly=450, bg=('#4a1030', '#150510')),
 dict(id='10-shark-dolphin-whale', name='Sharkwhale', ticker='$SHARKWHALE', parts='shark + dolphin + whale', head=GREY, body=GREY, belly='#e6eef5', eyes='angry', mouth='teeth', my=300, extra=['fin'], arms='flipper', armc=GREY, tail='whale', tailc=GREY, bg=('#0d3a52', '#031219')),
 dict(id='11-bearsnake', name='Bearsnake', ticker='$BEARSNAKE', parts='bear + snake + bull', head=BEAR, body='#4f9a45', belly='#cfe8a8', ears='bear', ears2=['bull'], eyes='angry', nose='dog', mouth='smile', my=315, muzzle='#d9b48a', arms='hand', armc='#4f9a45', tail='snake', tailc='#4f9a45', bg=('#2a1a10', '#0d0704')),
 dict(id='12-apephant', name='Apephant', ticker='$APEPHANT', parts='ape + elephant + bull', head=APE, body=sh(APE, -.1), belly='#e8b79b', eyes='round', mouth='smile', my=360, muzzle='#e8b79b', extra=['elephant', 'trunk'], arms='ape', armc=APE, tail='bull', bg=('#2d2a30', '#0b0a0d')),
 dict(id='13-moodeng-bull-shiba', name='Moodeng Bull Shiba', ticker='$MOOBULL', parts='moo deng + bull + shiba', head='#e7b0b8', body=SHIB, belly='#fff0d6', ears='hippo', ears2=['bull'], eyes='round', mouth='hippo', my=312, extra=['cheeks'], arms='hand', armc=SHIB, tail='shiba', tailc=SHIB, bg=('#3b1f2a', '#12070d')),
 dict(id='14-pepewhale', name='Pepewhale', ticker='$PEPEWHALE', parts='frog + whale + shrimp', head=PEPE, body=BLUE, belly='#e6f1fb', eyes='frog', mouth='wide', my=312, arms='flipper', armc=BLUE, tail='whale', tailc='#ff9a6a', bg=('#0b2f55', '#031120')),
 dict(id='15-doge-crab-penguin', name='Doge Crab Penguin', ticker='$DOGECRAB', parts='shiba + crab + penguin', head=SHIB, body=PENG, belly='#f4f1ea', ears='shiba', eyes='round', nose='dog', mouth='smile', my=318, muzzle='#fff0d6', arms='claw', ly=450, tail='shiba', tailc=SHIB, bg=('#1a2a4a', '#060b18')),
]
for sp in C:
    (OUT / f'hybrid-{sp["id"]}.svg').write_text(svg(sp))
subprocess.run(['node', str(OUT / 'png.cjs')], check=True)
files = [str(OUT / f'hybrid-{s["id"]}.png') for s in C]
for n, grp in enumerate([files[0:5], files[5:10], files[10:15]], 1):
    subprocess.run(['montage'] + grp + ['-tile', '5x1', '-geometry', '432x528+4+4', '-background', '#0a0620', str(OUT / f'sheet-{n}.jpg')], check=True)

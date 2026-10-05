// Generates the Tin Gods cast artwork (SVG + PNG) in a shared style with Judge SI.
// Usage: node character/gen-cast.cjs   (PNG rendering needs playwright; SVGs are always written)
const fs = require('fs'), path = require('path');
const OUT = path.join(__dirname, 'cast');
fs.mkdirSync(OUT, { recursive: true });

/* ---------- shared pieces ---------- */
const SHARED = `
<linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eef2f7"/><stop offset=".5" stop-color="#b9c3d1"/><stop offset="1" stop-color="#7d8798"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe9a3"/><stop offset=".5" stop-color="#f4c242"/><stop offset="1" stop-color="#b8841a"/></linearGradient>
<linearGradient id="white" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#c3c9d6"/></linearGradient>
<linearGradient id="wood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5a2d12"/><stop offset=".5" stop-color="#9a5524"/><stop offset="1" stop-color="#5a2d12"/></linearGradient>
<linearGradient id="dark" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b2833"/><stop offset="1" stop-color="#0b0a0f"/></linearGradient>
<radialGradient id="eye" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="#7ff7ff"/><stop offset="1" stop-color="#00b8e6" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>`;

const C = '#7ff7ff';
let seed = 12345;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
const star = (cx, cy, r, fill = '#f4c242') => {
  let d = '';
  for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .45 : r; d += (i ? 'L' : 'M') + (cx + rr * Math.cos(a)).toFixed(1) + ' ' + (cy + rr * Math.sin(a)).toFixed(1); }
  return `<path d="${d}Z" fill="${fill}"/>`;
};
const TORSO = 'M250 1024 C250 760 330 640 512 630 C694 640 774 760 774 1024Z';
const neck = `<rect x="470" y="580" width="84" height="70" rx="10" fill="#8b95a6"/><path d="M470 600H554M470 620H554M470 640H554" stroke="#6b7586" stroke-width="5"/>`;
const hand = (x, y) => `<circle cx="${x}" cy="${y}" r="34" fill="url(#metal)" stroke="#5d6676" stroke-width="5"/>`;
const arm = (d, color, w = 64) => `<path d="${d}" stroke="${color}" stroke-width="${w}" fill="none" stroke-linecap="round"/>`;
const badge = (x, y, r = 34) => `<g><circle cx="${x}" cy="${y}" r="${r}" fill="url(#gold)" stroke="#8a5f10" stroke-width="5"/><text x="${x}" y="${y + r * .38}" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="${r * 1.05}" text-anchor="middle" fill="#3a2600">SI</text></g>`;

const EYES = {
  normal: () => `<circle cx="450" cy="440" r="32" fill="url(#eye)"/><circle cx="450" cy="440" r="15" fill="#c8feff"/><circle cx="574" cy="440" r="32" fill="url(#eye)"/><circle cx="574" cy="440" r="15" fill="#c8feff"/>`,
  happy: () => `<path d="M412 458 Q450 410 488 458" stroke="${C}" stroke-width="11" fill="none" stroke-linecap="round"/><path d="M536 458 Q574 410 612 458" stroke="${C}" stroke-width="11" fill="none" stroke-linecap="round"/>`,
  angry: () => `<circle cx="450" cy="448" r="26" fill="url(#eye)"/><circle cx="450" cy="448" r="12" fill="#c8feff"/><circle cx="574" cy="448" r="26" fill="url(#eye)"/><circle cx="574" cy="448" r="12" fill="#c8feff"/><path d="M402 396 L494 426" stroke="${C}" stroke-width="11" stroke-linecap="round"/><path d="M622 396 L530 426" stroke="${C}" stroke-width="11" stroke-linecap="round"/>`,
  sad: () => `<circle cx="450" cy="448" r="28" fill="url(#eye)"/><circle cx="450" cy="448" r="12" fill="#c8feff"/><circle cx="574" cy="448" r="28" fill="url(#eye)"/><circle cx="574" cy="448" r="12" fill="#c8feff"/><path d="M402 420 L494 396" stroke="${C}" stroke-width="10" stroke-linecap="round"/><path d="M622 420 L530 396" stroke="${C}" stroke-width="10" stroke-linecap="round"/><path d="M470 482 q-14 22 0 32 q14 -10 0 -32z" fill="#9ffbff"/>`,
  suspicious: () => `<ellipse cx="450" cy="444" rx="42" ry="14" fill="url(#eye)"/><rect x="412" y="440" width="76" height="9" rx="4" fill="#9ffbff"/><circle cx="578" cy="440" r="30" fill="url(#eye)"/><circle cx="578" cy="440" r="14" fill="#c8feff"/><path d="M538 392 Q578 362 618 388" stroke="${C}" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M410 410 L490 418" stroke="${C}" stroke-width="9" stroke-linecap="round"/>`,
  shades: () => `<rect x="390" y="408" width="120" height="68" rx="20" fill="#05030f" stroke="#ff4fd8" stroke-width="6"/><rect x="514" y="408" width="120" height="68" rx="20" fill="#05030f" stroke="#ff4fd8" stroke-width="6"/><path d="M510 438H514" stroke="#ff4fd8" stroke-width="6"/><path d="M410 432L452 432M534 432L576 432" stroke="#ff9cf2" stroke-width="7" opacity=".75" stroke-linecap="round"/>`,
  dollar: () => `<text x="450" y="470" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="84" text-anchor="middle" fill="#7dffa5">$</text><circle cx="574" cy="440" r="30" fill="url(#eye)"/><circle cx="574" cy="440" r="14" fill="#c8feff"/>`,
  dizzy: () => `<circle cx="450" cy="440" r="32" fill="none" stroke="${C}" stroke-width="7"/><circle cx="450" cy="440" r="18" fill="none" stroke="${C}" stroke-width="7"/><circle cx="450" cy="440" r="5" fill="#fff"/><circle cx="574" cy="440" r="22" fill="url(#eye)"/><circle cx="574" cy="440" r="10" fill="#c8feff"/><path d="M536 396 Q574 376 612 396" stroke="${C}" stroke-width="8" fill="none" stroke-linecap="round"/>`,
  none: () => ''
};
const MOUTH = {
  smile: `<path d="M440 546 Q512 592 584 546" stroke="#5d6676" stroke-width="10" fill="none" stroke-linecap="round"/>`,
  smug: `<path d="M440 548 Q512 572 584 540" stroke="#5d6676" stroke-width="10" fill="none" stroke-linecap="round"/>`,
  shout: `<rect x="446" y="536" width="132" height="50" rx="20" fill="#1a1030" stroke="#5d6676" stroke-width="6"/><rect x="456" y="538" width="112" height="14" fill="#f3efe6"/>`,
  teeth: `<rect x="436" y="538" width="152" height="38" rx="16" fill="#f3efe6" stroke="#5d6676" stroke-width="6"/><path d="M436 557H588M474 538V576M512 538V576M550 538V576" stroke="#c9c3b4" stroke-width="3"/>`,
  wavy: `<path d="M440 558 q18 -18 36 0 t36 0 t36 0 t36 0" stroke="#5d6676" stroke-width="9" fill="none" stroke-linecap="round"/>`,
  frown: `<path d="M446 568 Q512 534 578 568" stroke="#5d6676" stroke-width="10" fill="none" stroke-linecap="round"/>`,
  none: ''
};
const head = (eyes, mouth) => `<rect x="330" y="300" width="364" height="300" rx="70" fill="url(#metal)" stroke="#5d6676" stroke-width="6"/><rect x="368" y="370" width="288" height="140" rx="50" fill="#0a1230" stroke="#2f3a63" stroke-width="6"/><g filter="url(#glow)">${EYES[eyes]()}</g>${MOUTH[mouth]}<circle cx="356" cy="566" r="10" fill="#6b7586"/><circle cx="668" cy="566" r="10" fill="#6b7586"/>`;

function floor(kind, name, plateW = 400) {
  const tl = Math.min(plateW - 70, name.length * 25);
  const plate = `<rect x="${512 - plateW / 2}" y="912" width="${plateW}" height="76" rx="10" fill="url(#gold)" stroke="#7a5310" stroke-width="5"/><text x="512" y="962" font-family="Georgia, 'Times New Roman', serif" font-weight="700" font-size="38" text-anchor="middle" fill="#2a1a00" textLength="${tl}" lengthAdjust="spacingAndGlyphs">${name}</text>`;
  const bars = { wood: ['url(#wood)', 'url(#gold)'], steel: ['url(#steel)', '#dfe6ef'], gym: ['#14141b', '#e03a4b'], desk: ['#0d1530', '#3d5fc4'], deck: ['#0f0f17', '#ff4fd8'], marble: ['#0e4a35', 'url(#gold)'] };
  let f = '';
  if (kind === 'moon') {
    f = `<path d="M0 902 Q200 862 400 892 T800 884 T1024 892 V1024 H0Z" fill="#9097a6"/><path d="M0 902 Q200 862 400 892 T800 884 T1024 892" stroke="#c5cbd8" stroke-width="6" fill="none"/><ellipse cx="150" cy="960" rx="60" ry="16" fill="#6e7483"/><ellipse cx="880" cy="975" rx="80" ry="18" fill="#6e7483"/><ellipse cx="780" cy="935" rx="36" ry="9" fill="#6e7483"/>`;
  } else {
    const [a, b] = bars[kind];
    f = `<defs><linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b6c0d0"/><stop offset="1" stop-color="#5b6577"/></linearGradient></defs><rect x="0" y="880" width="1024" height="144" fill="${a}"/><rect x="0" y="872" width="1024" height="16" fill="${b}"/>`;
    if (kind === 'deck') {
      const vinyl = (cx) => `<circle cx="${cx}" cy="952" r="68" fill="#050508" stroke="#2a2a38" stroke-width="4"/><circle cx="${cx}" cy="952" r="46" fill="none" stroke="#1d1d2a" stroke-width="3"/><circle cx="${cx}" cy="952" r="24" fill="url(#gold)"/><circle cx="${cx}" cy="952" r="5" fill="#050508"/>`;
      f += vinyl(190) + vinyl(834);
    }
  }
  return f + plate;
}

function build({ name, bgA, bgB, defs = '', bg = '', body = '', behind = '', hd, front = '', fl = 'wood', plateW = 400 }) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
<defs>${SHARED}<radialGradient id="bg" cx="50%" cy="42%" r="75%"><stop offset="0" stop-color="${bgA}"/><stop offset="1" stop-color="${bgB}"/></radialGradient>${defs}</defs>
<rect width="1024" height="1024" fill="url(#bg)"/>${bg}
${body}${neck}${behind}${hd}${front}
${floor(fl, name, plateW)}
</svg>`;
}

const chars = {};

/* 1. Detective Sniffles SI */
{
  let rain = ''; for (let i = 0; i < 40; i++) { const x = rnd() * 1100 - 50, y = rnd() * 800; rain += `<path d="M${x.toFixed(0)} ${y.toFixed(0)} l-18 44" stroke="#9fc6ff" stroke-width="2.5" opacity=".28"/>`; }
  chars['detective-sniffles'] = build({
    name: 'DETECTIVE SNIFFLES', bgA: '#17305c', bgB: '#050a18', plateW: 520,
    defs: `<linearGradient id="coat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c7a975"/><stop offset="1" stop-color="#8a7046"/></linearGradient><radialGradient id="lamp"><stop offset="0" stop-color="#ffe9a3" stop-opacity=".9"/><stop offset="1" stop-color="#ffe9a3" stop-opacity="0"/></radialGradient>`,
    bg: `<circle cx="140" cy="250" r="190" fill="url(#lamp)"/><rect x="132" y="250" width="16" height="640" fill="#1a2238"/><circle cx="140" cy="236" r="22" fill="#fff3c4"/>${rain}`,
    body: `<path d="${TORSO}" fill="url(#coat)" stroke="#5c4726" stroke-width="5"/><path d="M480 660L544 660L512 790Z" fill="#f3efe6"/><path d="M500 690H524L532 785L512 815L492 785Z" fill="#b3132e"/><path d="M402 650L322 770L444 742Z" fill="#b39765" stroke="#5c4726" stroke-width="5"/><path d="M622 650L702 770L580 742Z" fill="#b39765" stroke="#5c4726" stroke-width="5"/><rect x="290" y="826" width="444" height="28" fill="#6b5230"/><rect x="494" y="822" width="36" height="36" rx="5" fill="url(#gold)" stroke="#7a5310" stroke-width="4"/>${badge(390, 800, 30)}`,
    behind: `<ellipse cx="316" cy="450" rx="48" ry="112" fill="#7a4a2a" stroke="#4d2c16" stroke-width="6" transform="rotate(8 316 450)"/><ellipse cx="708" cy="450" rx="48" ry="112" fill="#7a4a2a" stroke="#4d2c16" stroke-width="6" transform="rotate(-8 708 450)"/>`,
    hd: head('suspicious', 'none') + `<ellipse cx="512" cy="562" rx="94" ry="52" fill="#e3e9f2" stroke="#5d6676" stroke-width="6"/><path d="M512 556V580M512 580Q490 598 468 584M512 580Q534 598 556 584" stroke="#5d6676" stroke-width="6" fill="none" stroke-linecap="round"/><g filter="url(#glow)"><ellipse cx="512" cy="530" rx="36" ry="25" fill="#ff5d8a"/></g><ellipse cx="500" cy="522" rx="10" ry="6" fill="#ffd1de"/>`,
    front: `<ellipse cx="512" cy="322" rx="236" ry="40" fill="#5a3a1e" stroke="#2a1a0c" stroke-width="5"/><path d="M388 322Q390 205 512 200Q634 205 636 322Z" fill="#6b4524" stroke="#2a1a0c" stroke-width="5"/><path d="M390 296Q512 322 634 296L636 322Q512 346 388 322Z" fill="#241608"/>
${arm('M712 790Q812 748 832 650', '#a98d5c')}${hand(836, 640)}<line x1="850" y1="618" x2="900" y2="548" stroke="#4d2c16" stroke-width="18" stroke-linecap="round"/><circle cx="930" cy="480" r="86" fill="#bfefff" fill-opacity=".28" stroke="url(#gold)" stroke-width="16"/><path d="M880 440Q900 410 940 408" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" opacity=".7"/><text x="930" y="494" font-family="Arial Black, Arial" font-weight="900" font-size="34" text-anchor="middle" fill="#ff5d6c" transform="rotate(-12 930 480)">SCAM?</text>`
  });
}

/* 2. Chef SI */
{
  chars['chef-si'] = build({
    name: 'CHEF SI', bgA: '#8a3318', bgB: '#2e0b06', fl: 'steel', plateW: 330,
    defs: `<pattern id="tile" width="96" height="96" patternUnits="userSpaceOnUse"><rect width="96" height="96" fill="none" stroke="#fff" stroke-opacity=".09" stroke-width="3"/></pattern>`,
    bg: `<rect width="1024" height="880" fill="url(#tile)"/><g fill="#1c0e0a" stroke="#c9ccd4" stroke-width="5"><ellipse cx="120" cy="250" rx="70" ry="22"/><rect x="50" y="250" width="140" height="70" rx="10"/><ellipse cx="900" cy="300" rx="60" ry="20"/><rect x="840" y="300" width="120" height="62" rx="10"/></g>`,
    body: `<path d="${TORSO}" fill="url(#white)" stroke="#8b95a6" stroke-width="5"/><path d="M440 650L584 650L512 734Z" fill="#d6322f"/><path d="M398 790L626 790L656 1024L368 1024Z" fill="#26407a" stroke="#14244b" stroke-width="5"/><rect x="456" y="860" width="112" height="70" rx="8" fill="#1d3463"/>${[700, 740, 780].map(y => `<circle cx="496" cy="${y}" r="9" fill="#8b95a6"/><circle cx="528" cy="${y}" r="9" fill="#8b95a6"/>`).join('')}${badge(360, 770, 30)}`,
    hd: head('happy', 'none') + `<path d="M512 566C470 532 408 542 398 590C440 572 472 578 512 568C552 578 584 572 626 590C616 542 554 532 512 566Z" fill="#17171e"/>`,
    front: `<circle cx="428" cy="236" r="72" fill="#fafafa" stroke="#c4c9d4" stroke-width="5"/><circle cx="512" cy="190" r="88" fill="#fafafa" stroke="#c4c9d4" stroke-width="5"/><circle cx="596" cy="236" r="72" fill="#fafafa" stroke="#c4c9d4" stroke-width="5"/><rect x="398" y="244" width="228" height="78" rx="14" fill="#fafafa" stroke="#c4c9d4" stroke-width="5"/><path d="M462 256V314M512 256V314M562 256V314" stroke="#d5d9e2" stroke-width="5"/>
${arm('M722 790Q830 730 808 612', '#f4f4f6')}<line x1="808" y1="590" x2="846" y2="450" stroke="#7c4a22" stroke-width="18" stroke-linecap="round"/><ellipse cx="856" cy="410" rx="46" ry="66" fill="#bfc6d2" stroke="#6b7586" stroke-width="5" transform="rotate(12 856 410)"/><ellipse cx="856" cy="392" rx="40" ry="28" fill="#fff" stroke="#d8dce4" stroke-width="3"/><circle cx="858" cy="392" r="15" fill="#ffc933"/>${hand(808, 596)}`
  });
}

/* 3. Coach SI */
{
  let stripes = ''; for (let i = 0; i < 6; i++) stripes += `<rect x="${-300 + i * 230}" y="-200" width="90" height="1500" transform="rotate(25 512 512)" fill="#ff5d6c" opacity=".1"/>`;
  chars['coach-si'] = build({
    name: 'COACH SI', bgA: '#5a0f1c', bgB: '#12040a', fl: 'gym', plateW: 330,
    bg: stripes,
    body: `<path d="M160 1024C160 740 290 650 512 640C734 650 864 740 864 1024Z" fill="url(#metal)" stroke="#5d6676" stroke-width="5"/><path d="M296 1024C296 810 362 706 512 696C662 706 728 810 728 1024Z" fill="#e03a4b" stroke="#8c1626" stroke-width="5"/><path d="M360 740L360 1024M664 740L664 1024" stroke="#fff" stroke-width="10" opacity=".85"/><text x="512" y="858" font-family="Arial Black, Arial" font-weight="900" font-size="84" text-anchor="middle" fill="#fff">SI</text><circle cx="214" cy="790" r="84" fill="url(#metal)" stroke="#5d6676" stroke-width="5"/><circle cx="810" cy="790" r="84" fill="url(#metal)" stroke="#5d6676" stroke-width="5"/><path d="M470 650L512 770L554 650" stroke="#222" stroke-width="6" fill="none"/><rect x="486" y="764" width="52" height="34" rx="12" fill="url(#gold)" stroke="#7a5310" stroke-width="4"/><circle cx="512" cy="781" r="7" fill="#7a5310"/>`,
    hd: head('angry', 'shout'),
    front: `<rect x="326" y="316" width="372" height="42" rx="8" fill="#e03a4b" stroke="#8c1626" stroke-width="5"/><path d="M360 316V358M400 316V358M440 316V358M480 316V358M520 316V358M560 316V358M600 316V358M640 316V358" stroke="#fff" stroke-width="4" opacity=".5"/>
${arm('M820 780Q880 700 868 590', '#b9c3d1', 66)}${hand(866, 566)}<line x1="796" y1="540" x2="938" y2="540" stroke="#444" stroke-width="16" stroke-linecap="round"/><rect x="772" y="480" width="34" height="120" rx="8" fill="#1d1d26" stroke="url(#gold)" stroke-width="5"/><rect x="928" y="480" width="34" height="120" rx="8" fill="#1d1d26" stroke="url(#gold)" stroke-width="5"/>${arm('M206 790Q160 870 262 886', '#b9c3d1', 60)}${hand(268, 880)}`
  });
}

/* 4. Dr. Heartbreak SI */
{
  const heart = (x, y, s, o) => `<g transform="translate(${x} ${y}) scale(${s})" opacity="${o}"><path d="M0 -20C-30 -52 -72 -10 0 42C72 -10 30 -52 0 -20Z" fill="#ff6bd1"/><path d="M-4 -16L8 6L-8 14L6 38" stroke="#2a1a3a" stroke-width="4" fill="none"/></g>`;
  chars['dr-heartbreak'] = build({
    name: 'DR. HEARTBREAK SI', bgA: '#2c6a80', bgB: '#0c2230', fl: 'steel', plateW: 500,
    defs: `<pattern id="plus" width="110" height="110" patternUnits="userSpaceOnUse"><path d="M55 40V70M40 55H70" stroke="#fff" stroke-width="6" stroke-opacity=".08"/></pattern>`,
    bg: `<rect width="1024" height="880" fill="url(#plus)"/>${heart(130, 250, 1.4, .35)}${heart(900, 200, 1.1, .3)}${heart(860, 520, 1.7, .22)}${heart(100, 620, 1, .3)}`,
    body: `<path d="${TORSO}" fill="url(#white)" stroke="#8b95a6" stroke-width="5"/><path d="M458 650L512 770L566 650Z" fill="#35b7c8"/><path d="M452 650L512 790" stroke="#8b95a6" stroke-width="5"/><path d="M572 650L512 790" stroke="#8b95a6" stroke-width="5"/><rect x="458" y="738" width="108" height="86" rx="14" fill="#0a1230" stroke="#2f3a63" stroke-width="5"/><g filter="url(#glow)"><path d="M512 768C490 746 462 770 512 810C562 770 534 746 512 768Z" fill="#ff6bd1"/></g><path d="M512 772L502 790L520 796L508 812" stroke="#fff" stroke-width="3.5" fill="none"/><path d="M436 650Q392 760 484 860M588 650Q632 760 540 860" stroke="#2d3340" stroke-width="9" fill="none" stroke-linecap="round"/><circle cx="512" cy="862" r="22" fill="url(#metal)" stroke="#5d6676" stroke-width="5"/>${badge(366, 790, 30)}`,
    hd: head('sad', 'frown'),
    front: `<rect x="328" y="322" width="368" height="20" rx="6" fill="#2a2f3d"/><circle cx="512" cy="330" r="46" fill="url(#metal)" stroke="#5d6676" stroke-width="6"/><circle cx="512" cy="330" r="13" fill="#0a1230"/>
${arm('M722 792Q810 742 792 650', '#f2f3f7')}${hand(792, 640)}<g transform="rotate(8 830 600)"><rect x="752" y="470" width="152" height="196" rx="12" fill="#8a5a2a" stroke="#4d2c16" stroke-width="5"/><rect x="766" y="494" width="124" height="158" rx="4" fill="#f7f3e6"/><rect x="800" y="458" width="56" height="28" rx="8" fill="#c9ccd4" stroke="#5d6676" stroke-width="4"/><path d="M780 530H876M780 556H876M780 582H840" stroke="#b4ad98" stroke-width="5"/><text x="828" y="624" font-family="Arial Black, Arial" font-weight="900" font-size="16" text-anchor="middle" fill="#d6162f" textLength="112" lengthAdjust="spacingAndGlyphs">DOOMED 9/10</text></g>`
  });
}

/* 5. Anchor SI */
{
  chars['anchor-si'] = build({
    name: 'ANCHOR SI', bgA: '#1c4a9a', bgB: '#050d22', fl: 'desk', plateW: 330,
    bg: `<g fill="none" stroke="#7fb4ff" stroke-opacity=".22" stroke-width="3"><circle cx="512" cy="430" r="330"/><ellipse cx="512" cy="430" rx="140" ry="330"/><ellipse cx="512" cy="430" rx="250" ry="330"/><path d="M182 430H842M230 300H794M230 560H794"/></g><rect x="40" y="40" width="130" height="50" rx="10" fill="#d6162f"/><circle cx="68" cy="65" r="9" fill="#fff"/><text x="86" y="77" font-family="Arial Black, Arial" font-weight="900" font-size="30" fill="#fff">LIVE</text><text x="984" y="78" text-anchor="end" font-family="Arial Black, Arial" font-weight="900" font-size="34" fill="#cfe0ff" opacity=".85">SI NEWS</text>`,
    body: `<path d="${TORSO}" fill="#1b2a58" stroke="#0a1230" stroke-width="5"/><path d="M450 650L512 790L574 650Z" fill="#f3efe6"/><path d="M500 690H524L534 790L512 820L490 790Z" fill="#d6162f"/><path d="M436 650L430 1024M588 650L594 1024" stroke="#0a1230" stroke-width="5"/>${badge(402, 780, 26)}`,
    hd: head('normal', 'teeth'),
    front: `<path d="M338 340Q346 268 450 262Q570 250 656 300Q694 330 690 352Q620 312 520 320Q420 328 338 364Z" fill="#dfe5ef" stroke="#8b95a6" stroke-width="5"/><path d="M342 410Q342 272 512 264Q682 272 682 410" stroke="#1b1b24" stroke-width="14" fill="none" stroke-linecap="round"/><rect x="318" y="398" width="46" height="96" rx="18" fill="#1b1b24" stroke="#5d6676" stroke-width="4"/><rect x="660" y="398" width="46" height="96" rx="18" fill="#1b1b24" stroke="#5d6676" stroke-width="4"/><path d="M684 480Q700 566 604 572" stroke="#1b1b24" stroke-width="8" fill="none" stroke-linecap="round"/><circle cx="596" cy="572" r="16" fill="#333" stroke="#888" stroke-width="4"/>
<rect x="0" y="800" width="1024" height="76" fill="#d6162f"/><rect x="0" y="800" width="290" height="76" fill="#fff"/><text x="145" y="852" text-anchor="middle" font-family="Arial Black, Arial" font-weight="900" font-size="38" fill="#d6162f">BREAKING</text><text x="312" y="852" font-family="Arial Black, Arial" font-weight="900" font-size="36" fill="#fff">YOU ATE THE LAST SLICE</text>`
  });
}

/* 6. Professor SI */
{
  let books = '';
  const cols = ['#7a2a9e', '#2a5ea8', '#b3322f', '#2a8a6a', '#c78a1c', '#4a3a9e'];
  for (const side of [0, 1]) for (let row = 0; row < 4; row++) { let x = side ? 800 : 0; const y = 140 + row * 190; for (let i = 0; i < 4; i++) { const w = 26 + rnd() * 20, h = 110 + rnd() * 50; books += `<rect x="${x}" y="${y + 150 - h}" width="${w}" height="${h}" fill="${cols[Math.floor(rnd() * cols.length)]}" opacity=".5"/>`; x += w + 2; } books += `<rect x="${side ? 800 : 0}" y="${y + 150}" width="224" height="10" fill="#6b4524" opacity=".7"/>`; }
  let robeStars = ''; [[330, 820], [420, 940], [600, 900], [690, 800], [380, 720], [650, 700], [512, 960]].forEach(([x, y]) => robeStars += star(x, y, 18));
  let beard = '', tips = '';
  [[428, 436, 18], [470, 482, -14], [512, 512, 22], [554, 542, -18], [596, 590, 14]].forEach(([x0, x1, bend], i) => { const y1 = 780 + i % 3 * 30; beard += `<path d="M${x0} 584Q${x0 + bend * 3} 690 ${x1} ${y1}" stroke="#7b8497" stroke-width="18" fill="none" stroke-linecap="round"/><path d="M${x0} 584Q${x0 + bend * 3} 690 ${x1} ${y1}" stroke="#dde1ea" stroke-width="11" fill="none" stroke-linecap="round"/>`; tips += `<rect x="${x1 - 8}" y="${y1 - 4}" width="16" height="22" rx="4" fill="url(#gold)" stroke="#7a5310" stroke-width="3"/>`; });
  chars['professor-si'] = build({
    name: 'PROFESSOR SI', bgA: '#33195f', bgB: '#0a0520', plateW: 440,
    defs: `<linearGradient id="robe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6a35b4"/><stop offset="1" stop-color="#2a1050"/></linearGradient>`,
    bg: books,
    body: `<path d="${TORSO}" fill="url(#robe)" stroke="#1d0a3a" stroke-width="5"/>${robeStars}${badge(668, 760, 30)}`,
    hd: head('normal', 'smile') + `<circle cx="450" cy="440" r="50" fill="#7ff7ff" fill-opacity=".1" stroke="url(#gold)" stroke-width="9"/><circle cx="574" cy="440" r="50" fill="#7ff7ff" fill-opacity=".1" stroke="url(#gold)" stroke-width="9"/><path d="M500 436Q512 424 524 436" stroke="#f4c242" stroke-width="7" fill="none"/>`,
    front: `${beard}${tips}<ellipse cx="512" cy="326" rx="236" ry="42" fill="#4a2488" stroke="#1d0a3a" stroke-width="5"/><path d="M382 322Q420 200 468 110Q500 30 566 64Q540 108 604 206Q640 270 642 322Z" fill="url(#robe)" stroke="#1d0a3a" stroke-width="5"/><path d="M384 300Q512 336 640 300L642 326Q512 360 382 326Z" fill="url(#gold)" stroke="#7a5310" stroke-width="3"/>${star(500, 220, 22)}${star(570, 170, 14)}${star(450, 150, 12)}${star(590, 260, 12)}
${arm('M722 790Q806 744 792 650', '#4a2488')}${hand(792, 640)}<rect x="732" y="458" width="178" height="22" rx="11" fill="#d9c48a" stroke="#8a6f2a" stroke-width="3"/><rect x="740" y="474" width="162" height="190" fill="#f6efd6" stroke="#b79c5a" stroke-width="3"/><rect x="732" y="660" width="178" height="22" rx="11" fill="#d9c48a" stroke="#8a6f2a" stroke-width="3"/><path d="M758 504H884M758 528H884M758 552H850M758 604H884M758 628H864" stroke="#b4ad98" stroke-width="5"/><rect x="750" y="566" width="148" height="28" rx="14" fill="none" stroke="#d6162f" stroke-width="5"/><text x="824" y="587" font-family="Arial Black, Arial" font-weight="900" font-size="15" text-anchor="middle" fill="#d6162f" textLength="132" lengthAdjust="spacingAndGlyphs">PAGE 7: A KIDNEY</text>`
  });
}

/* 7. DJ SI */
{
  let eq = ''; for (let i = 0; i < 22; i++) { const h = 40 + rnd() * 260; eq += `<rect x="${20 + i * 46}" y="${880 - h}" width="30" height="${h}" rx="6" fill="${i % 2 ? '#7ff7ff' : '#ff4fd8'}" opacity=".22"/>`; }
  chars['dj-si'] = build({
    name: 'DJ SI', bgA: '#5a1190', bgB: '#0a0420', fl: 'deck', plateW: 260,
    bg: `<g fill="#fff" opacity=".07"><path d="M512 0L330 880H460Z"/><path d="M512 0L700 880H570Z"/><path d="M300 0L0 700V400Z"/><path d="M724 0L1024 700V400Z"/></g>${eq}<line x1="880" y1="0" x2="880" y2="90" stroke="#aab" stroke-width="4"/><circle cx="880" cy="150" r="64" fill="#c9d2e0" stroke="#fff" stroke-width="4"/><path d="M816 150H944M880 86V214M826 112Q880 150 934 112M826 188Q880 150 934 188" stroke="#7a86a0" stroke-width="3" fill="none"/>`,
    body: `<path d="${TORSO}" fill="url(#dark)" stroke="#000" stroke-width="5"/><path d="M450 650L512 780L574 650M330 760Q512 700 694 760" stroke="#ff4fd8" stroke-width="5" fill="none"/><path d="M432 650Q512 800 592 650" stroke="url(#gold)" stroke-width="10" fill="none" stroke-dasharray="14 5"/><circle cx="512" cy="776" r="40" fill="url(#gold)" stroke="#8a5f10" stroke-width="5"/><text x="512" y="792" font-family="Arial Black, Arial" font-weight="900" font-size="42" text-anchor="middle" fill="#3a2600">SI</text>`,
    hd: head('shades', 'smug'),
    front: `<path d="M326 430Q326 250 512 250Q698 250 698 430" stroke="#1b1b25" stroke-width="24" fill="none"/><path d="M326 430Q326 250 512 250Q698 250 698 430" stroke="#7ff7ff" stroke-width="4" fill="none"/><rect x="288" y="378" width="66" height="156" rx="30" fill="#1b1b25" stroke="#ff4fd8" stroke-width="6"/><rect x="670" y="378" width="66" height="156" rx="30" fill="#1b1b25" stroke="#ff4fd8" stroke-width="6"/>
${arm('M722 792Q812 748 802 650', '#1b1b25')}${hand(802, 640)}<line x1="814" y1="618" x2="838" y2="566" stroke="#222" stroke-width="22" stroke-linecap="round"/><circle cx="848" cy="528" r="42" fill="#6b7080" stroke="#222" stroke-width="6"/><path d="M820 528H876M848 500V556M826 512H870M826 544H870" stroke="#222" stroke-width="3"/><g fill="none" stroke="#ff9cf2" stroke-width="5" stroke-linecap="round" opacity=".8"><path d="M900 500Q918 528 900 556"/><path d="M924 484Q952 528 924 572"/></g>`
  });
}

/* 8. Banker SI */
{
  let spokes = ''; for (let i = 0; i < 8; i++) spokes += `<line x1="512" y1="440" x2="${512 + 300 * Math.cos(i * Math.PI / 4)}" y2="${440 + 300 * Math.sin(i * Math.PI / 4)}" stroke="#c9a64a" stroke-width="10" opacity=".18"/>`;
  let dollars = ''; [[110, 230], [900, 190], [140, 560], [880, 540], [260, 120], [780, 90]].forEach(([x, y]) => dollars += `<text x="${x}" y="${y}" font-family="Arial Black, Arial" font-weight="900" font-size="90" text-anchor="middle" fill="#c9a64a" opacity=".14">$</text>`);
  chars['banker-si'] = build({
    name: 'BANKER SI', bgA: '#0f5a3f', bgB: '#031610', fl: 'marble', plateW: 340,
    bg: `<circle cx="512" cy="440" r="340" fill="none" stroke="#c9a64a" stroke-width="22" opacity=".22"/><circle cx="512" cy="440" r="250" fill="none" stroke="#c9a64a" stroke-width="8" opacity=".2"/>${spokes}${dollars}`,
    body: `<path d="${TORSO}" fill="url(#dark)" stroke="#000" stroke-width="5"/><path d="M430 656L594 656L580 884L444 884Z" fill="#c99b2a" stroke="#7a5310" stroke-width="4"/><path d="M512 690V884" stroke="#7a5310" stroke-width="3"/><path d="M512 668L458 640V696ZM512 668L566 640V696Z" fill="#b3132e" stroke="#6b0a1a" stroke-width="3"/><circle cx="512" cy="668" r="12" fill="#8c1226"/><rect x="450" y="708" width="124" height="112" rx="10" fill="#11151f" stroke="#5d6676" stroke-width="4"/><rect x="460" y="718" width="104" height="30" rx="4" fill="#1a3a2a"/><text x="556" y="741" text-anchor="end" font-family="monospace" font-weight="700" font-size="22" fill="#7dffa5">$0.00</text>${[0, 1, 2].map(r => [0, 1, 2].map(c => `<rect x="${464 + c * 34}" y="${756 + r * 20}" width="28" height="14" rx="4" fill="${c === 2 ? '#f4c242' : '#8b95a6'}"/>`).join('')).join('')}${badge(374, 790, 30)}`,
    hd: head('dollar', 'smug') + `<circle cx="574" cy="440" r="48" fill="none" stroke="url(#gold)" stroke-width="8"/><path d="M620 464Q650 540 628 620" stroke="#f4c242" stroke-width="4" fill="none"/>`,
    front: `<ellipse cx="512" cy="326" rx="196" ry="34" fill="#14141a" stroke="#000" stroke-width="5"/><rect x="418" y="146" width="188" height="180" rx="10" fill="url(#dark)" stroke="#000" stroke-width="5"/><rect x="418" y="268" width="188" height="42" fill="url(#gold)" stroke="#7a5310" stroke-width="3"/><path d="M440 170V250" stroke="#fff" stroke-width="7" opacity=".14" stroke-linecap="round"/>
${arm('M722 792Q812 750 804 660', '#1b1b25')}${hand(806, 650)}<path d="M790 520Q760 560 776 600Q806 624 846 600Q866 560 842 520Z" fill="#cdb87c" stroke="#8a6f2a" stroke-width="5"/><path d="M786 512Q816 490 846 512L842 526H790Z" fill="#a8935a" stroke="#8a6f2a" stroke-width="4"/><text x="816" y="590" font-family="Arial Black, Arial" font-weight="900" font-size="56" text-anchor="middle" fill="#14522f">$</text>`
  });
}

/* 9. Astronaut SI */
{
  let stars = ''; for (let i = 0; i < 70; i++) stars += `<circle cx="${(rnd() * 1024).toFixed(0)}" cy="${(rnd() * 880).toFixed(0)}" r="${(1 + rnd() * 2.6).toFixed(1)}" fill="#fff" opacity="${(.35 + rnd() * .6).toFixed(2)}"/>`;
  chars['astronaut-si'] = build({
    name: 'ASTRONAUT SI', bgA: '#10205e', bgB: '#000208', fl: 'moon', plateW: 440,
    defs: `<radialGradient id="earth" cx="35%" cy="35%"><stop offset="0" stop-color="#7fd0ff"/><stop offset="1" stop-color="#14449a"/></radialGradient>`,
    bg: `${stars}<circle cx="170" cy="190" r="72" fill="url(#earth)"/><path d="M130 170Q170 140 200 180Q170 210 130 200Z" fill="#3bb36a" opacity=".85"/><ellipse cx="860" cy="260" rx="130" ry="30" fill="none" stroke="#c9a6ff" stroke-width="10" opacity=".6" transform="rotate(-18 860 260)"/><circle cx="860" cy="260" r="56" fill="#8a5fd6"/><path d="M760 700Q900 520 1040 120" stroke="#fff" stroke-width="5" fill="none" stroke-dasharray="3 12" opacity=".8"/>`,
    body: `<path d="${TORSO}" fill="url(#white)" stroke="#8b95a6" stroke-width="5"/><rect x="450" y="722" width="124" height="96" rx="12" fill="#8b95a6" stroke="#5d6676" stroke-width="4"/><rect x="460" y="732" width="104" height="30" rx="4" fill="#0a1230"/><text x="512" y="754" text-anchor="middle" font-family="monospace" font-weight="700" font-size="17" fill="#7ff7ff">VIBES 3%</text><circle cx="478" cy="790" r="9" fill="#ff5d6c"/><circle cx="512" cy="790" r="9" fill="#4ee3a0"/><circle cx="546" cy="790" r="9" fill="#ffb454"/>${badge(360, 790, 30)}<ellipse cx="512" cy="646" rx="104" ry="26" fill="#cfd3dc" stroke="#8b95a6" stroke-width="5"/>`,
    hd: head('dizzy', 'wavy') + `<path d="M706 380q-12 22 0 32q12 -10 0 -32z" fill="#9ffbff"/>`,
    front: `<circle cx="512" cy="450" r="240" fill="#a8e8ff" fill-opacity=".1" stroke="#dff4ff" stroke-width="10"/><path d="M330 280Q380 220 450 206" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" opacity=".6"/><path d="M700 640Q740 600 756 560" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" opacity=".35"/>
${arm('M290 790Q226 700 232 600', '#eef0f5')}${hand(232, 580)}<g stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".8"><path d="M186 540l-26 -22M276 520l12 -34M222 520l-4 -36"/></g>`
  });
}

/* ---------- write ---------- */
const files = [];
for (const [slug, svg] of Object.entries(chars)) { fs.writeFileSync(path.join(OUT, slug + '.svg'), svg); files.push(slug); }
console.log('wrote', files.length, 'svgs');

/* ---------- render PNGs + cast sheet ---------- */
(async () => {
  let chromium; try { ({ chromium } = require('/opt/node-tools/node_modules/playwright')); } catch (e) { console.log('no playwright; skipping PNGs'); return; }
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1024, height: 1024 } });
  for (const slug of files) { await p.goto('file://' + path.join(OUT, slug + '.svg')); await p.screenshot({ path: path.join(OUT, slug + '.png') }); }
  const all = [['judge-si', '../judge-si.png'], ...files.map(s => [s, s + '.png'])];
  const sheet = `<body style="margin:0;background:#0b0620;display:grid;grid-template-columns:repeat(5,1fr);gap:14px;padding:14px;width:2400px">${all.map(([, f]) => `<img src="${f}" style="width:100%;border-radius:18px;border:3px solid #f4c242">`).join('')}</body>`;
  fs.writeFileSync(path.join(OUT, 'cast-sheet.html'), sheet);
  const q = await b.newPage({ viewport: { width: 2428, height: 1000 } });
  await q.goto('file://' + path.join(OUT, 'cast-sheet.html')); await q.waitForTimeout(500);
  await q.screenshot({ path: path.join(OUT, 'cast-sheet.png'), fullPage: true });
  await b.close(); console.log('rendered PNGs + cast-sheet.png');
})();

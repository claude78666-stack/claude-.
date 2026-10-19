#!/usr/bin/env python3
"""Turns Microsoft's official Gears of War: E-Day press images into moving backdrops -> gameplay/<id>.mp4

Run: python3 make_game_visuals.py
Downloads the screenshots and key art Xbox published on Xbox Wire (news.xbox.com) into official/ (not
committed), then for each section in script.json makes a slow Ken Burns slideshow of its images with
crossfades and an "Images: Xbox / The Coalition" credit, as long as that section's narration.
render_longform.py uses gameplay/<id>.mp4 as the section background when it exists; swap any of them for
your own recorded gameplay of the same name.
"""
import json
import subprocess
import urllib.request
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC, OUT = HERE / "official", HERE / "gameplay"
SRC.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)
W, H, FPS, XF = 1920, 1080, 24, 0.8
LEAD, TAIL, TEMPO = 1.3, 0.9, 0.94  # keep in step with render_longform.py
BASE = "https://xboxwire.thesourcemediaassets.com/sites/2/"
IMAGES = {
    "squad": "2026/10/02_GoW_EDAY_BravoSquad_Final-53f5381012ec445dcc22.jpg",
    "keyart": "2026/06/Gears-f783604b4900f089e04e.jpg",
    "logo": "2024/06/Gears-of-War-E-Day_KeyArt_1920x1080-13a83d877fdad66ada88.jpg",
    "emergence": "2026/10/GoW_EDAY_Adagio_4K_Final_09-0f31e58cf65dec22523a.jpg",
    "coop": "2026/10/GoW_EDAY_CoOp_Multiplayer_Final-6a6a958a8226f-2048x1152-1-26dc3ad403d0a951b058.jpg",
    "dom_marcus": "2026/08/GoW_EDAY_Dom_Marcus_Final-0c3e4d4c1ea8faee1366.jpg",
    "horde": "2026/10/GoW_EDAY_HordeSiege_Final-comp-6a6934fdd4953-dde655650345c91133a6.jpg",
    "marcus_bar": "2026/09/GoW_EDAY_MarcusCheers_Final-4053b1f9855d2efd4a42.jpg",
    "marcus": "2026/08/GoW_EDAY_Marcus_Final-b5aeeed1970d8c7f93a1.jpg",
    "lancer": "2026/08/GoW_EDAY_Marcus_Lancer_Final-b9e279b2d7bd791f1ec8.jpg",
    "gore": "2026/07/GoW_EDAY_Versus_Breechshot_Final_Logo-183ca26533a83dbebb7b.jpg",
    "versus": "2026/10/GoW_EDAY_Versus_Final-6a67ac11d1548-2048x1152-1-07715ca79bd19008bbfb.jpg",
    "locust": "2026/08/GoW_EDAY_Vraahk_Final-17f77a8d25382807c03e.jpg",
}
PLAN = {
    "01_what": ["keyart", "logo", "squad"],
    "02_when": ["emergence", "locust"],
    "02b_lore": ["marcus_bar", "dom_marcus"],
    "03_squad": ["squad", "dom_marcus", "marcus"],
    "04_campaign": ["marcus_bar", "emergence", "lancer"],
    "05_movement": ["coop", "versus"],
    "06_combat": ["lancer", "gore", "versus"],
    "07_enemies": ["locust", "horde", "emergence"],
    "08_coop": ["coop", "squad"],
    "09_multiplayer": ["versus", "gore"],
    "10_horde": ["horde", "locust"],
    "11_tech": ["emergence", "keyart", "lancer"],
    "12_reception": ["keyart", "dom_marcus"],
    "12b_tips": ["coop", "lancer"],
    "13_verdict": ["squad", "keyart", "logo"],
}


def fetch():
    for name, path in IMAGES.items():
        dst = SRC / f"{name}.jpg"
        if not dst.exists():
            req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0"})  # the CDN 403s urllib's default
            with urllib.request.urlopen(req, timeout=120) as r:
                dst.write_bytes(r.read())
        # normalise to 16:9 at 2x so the slow zoom stays sharp
        big = SRC / f"{name}_4k.png"
        if not big.exists():
            im = Image.open(dst).convert("RGB")
            scale = max(W * 2 / im.width, H * 2 / im.height)
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
            l, t = (im.width - W * 2) // 2, (im.height - H * 2) // 2
            im.crop((l, t, l + W * 2, t + H * 2)).save(big)


def seconds(sid):
    with wave.open(str(HERE / "voice" / f"{sid}.wav")) as w:
        return LEAD + w.getnframes() / w.getframerate() / TEMPO + TAIL


def credit():
    """Credit line, plus a dark fade on the left so Sifa's headings and cards stay readable."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in range(0, 1300, 4):
        d.rectangle([x, 0, x + 3, H], fill=(4, 3, 12, int(200 * (1 - x / 1300) ** 1.4)))
    d.text((W - 70, H - 36), "Images: Xbox / The Coalition", anchor="rm",
           font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 20),
           fill=(255, 255, 255, 150))
    img.save(SRC / "credit.png")


def slideshow(sid, names, total):
    n = len(names)
    each = (total + XF * (n - 1)) / n
    inputs, chain = [], []
    for i, name in enumerate(names):
        frames = int(each * FPS) + 1
        zin = i % 2 == 0  # alternate push-in and pull-out, drifting a different way each time
        z = f"min(1+0.10*on/{frames},1.10)" if zin else f"max(1.10-0.10*on/{frames},1.0)"
        x = "iw/2-(iw/zoom/2)" + ("+on*0.25" if i % 3 == 1 else "-on*0.20" if i % 3 == 2 else "")
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{each:.3f}", "-i", str(SRC / f"{name}_4k.png")]
        chain.append(f"[{i}:v]zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
                     f"trim=duration={each:.3f},setpts=PTS-STARTPTS,format=yuv420p[p{i}]")
    last, offset = "[p0]", each - XF
    for i in range(1, n):
        chain.append(f"{last}[p{i}]xfade=transition=fade:duration={XF}:offset={offset:.3f}[x{i}]")
        last, offset = f"[x{i}]", offset + each - XF
    inputs += ["-loop", "1", "-i", str(SRC / "credit.png")]
    chain.append(f"{last}[{n}:v]overlay=0:0:shortest=1,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", "[v]",
                    "-t", f"{total:.3f}", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                    str(OUT / f"{sid}.mp4")], check=True)
    print(sid, f"{total:.1f}s", "+".join(names), flush=True)


fetch()
credit()
for s in json.load(open(HERE / "script.json"))["sections"]:
    slideshow(s["id"], PLAN[s["id"]], seconds(s["id"]))

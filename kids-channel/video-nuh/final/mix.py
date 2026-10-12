"""Adds narration, captions, title and lesson cards, ambience and the logo to
video_silent.mp4, producing nuh_and_the_ark.mp4."""
import json, os, re, subprocess

D = os.path.dirname(os.path.abspath(__file__))
PV = os.path.join(D, "..", "previz")
FPS_PV, LEAD = 8, 1.0
shots = {k: ((a - 1) / FPS_PV, b / FPS_PV) for k, (a, b) in json.load(open(os.path.join(PV, "shots.json"))).items()}
durs = dict(json.load(open(os.path.join(PV, "durations.json"))))
text = dict(json.load(open(os.path.join(PV, "narration.json"))))
flashes = json.load(open(os.path.join(D, "flashes.json"))) if os.path.exists(os.path.join(D, "flashes.json")) else []
LOGO = os.path.join(D, "..", "..", "logo-gemini", "toon-noon-gemini-stacked.png")
TOTAL = shots["s11"][1]


def t(sec):
    h, r = divmod(max(sec, 0), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
       "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Sub,Fredoka Light SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H00301E14,&H96000000,0,0,0,0,100,100,0,0,1,3.5,1.5,2,160,160,60,1",
       "Style: Title,Fredoka Light SemiBold,92,&H00FFFFFF,&H00FFFFFF,&H00301E14,&H96000000,0,0,0,0,100,100,1,0,1,5,3,5,100,100,0,1",
       "Style: Card,Fredoka Light SemiBold,64,&H0050C8FF,&H00FFFFFF,&H00301E14,&H96000000,0,0,0,0,100,100,0,0,1,4.5,2,8,120,120,120,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
delays = []
for sid, (s0, s1) in shots.items():
    start = s0 + LEAD
    delays.append((sid, start))
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text[sid]) if p.strip()]
    tot = sum(len(p) for p in parts)
    cur = start
    for p in parts:
        d = durs[sid] * len(p) / tot
        ass.append(f"Dialogue: 0,{t(cur)},{t(cur + d)},Sub,,0,0,0,,{p}")
        cur += d

fade = r"{\fad(600,600)}"
ass.append(f"Dialogue: 1,{t(12.6)},{t(18.3)},Title,,0,0,0,,{fade}Prophet Nuh\\Nand the Great Ark")
# Lesson cards, timed to where each lesson is spoken in scene 10.
s10 = shots["s10"][0] + LEAD
d10 = durs["s10"]
body = text["s10"]
for word, card in (("One:", "1. Never give up doing good"), ("Two:", "2. Be kind to everyone"),
                   ("Three:", "3. Trust Allah"), ("Rabbighfir", "Rabbighfir li wa li walidayya")):
    st = s10 + d10 * body.index(word) / len(body)
    ass.append(f"Dialogue: 1,{t(st)},{t(min(st + 6.5, shots['s10'][1]))},Card,,0,0,0,,{fade}{card}")
s11 = shots["s11"][0] + LEAD
ass.append(f"Dialogue: 1,{t(s11)},{t(s11 + 5.5)},Card,,0,0,0,,{fade}Kindness Challenge:\\Nbe patient with someone!")
open(os.path.join(D, "final.ass"), "w").write("\n".join(ass) + "\n")


def sec(sid, frac):
    a, b = shots[sid]
    return a + (b - a) * frac


ins, mix = [], []
for k, (sid, st) in enumerate(delays):
    ins += ["-i", os.path.join(PV, "audio", f"{sid}.mp3")]
    ms = round(st * 1000)
    mix.append(f"[{k + 1}:a]adelay={ms}|{ms}[n{k}]")
sea = (f"anoisesrc=c=brown:a=0.06:d={TOTAL}:r=44100,lowpass=f=420,"
       f"volume='if(lt(t,{sec('s01', 1)}),1,0)+if(between(t,{sec('s09', 0.3)},{sec('s09', 1)}),0.7,0)':eval=frame[sea]")
rain = (f"anoisesrc=c=pink:a=0.06:d={TOTAL}:r=44100,highpass=f=700,lowpass=f=7000,"
        f"volume='if(between(t,{sec('s07', 0.45)},{sec('s08', 1)}),1,0)':eval=frame[rain]")
thunder_on = "+".join(f"between(t,{f + 0.25},{f + 2.2})*exp(-(t-{f + 0.25})*1.6)" for f in flashes[::3]) or "0"
thunder = (f"anoisesrc=c=brown:a=0.5:d={TOTAL}:r=44100,lowpass=f=140,"
           f"volume='{thunder_on}':eval=frame[thun]")
wind = (f"anoisesrc=c=pink:a=0.025:d={TOTAL}:r=44100,bandpass=f=500:width_type=o:w=1.5,"
        f"volume='if(between(t,{sec('s02', 0)},{sec('s06', 1)}),1,0)':eval=frame[wind]")
labels = "".join(f"[n{k}]" for k in range(len(delays)))
fc = ";".join(mix + [sea, rain, thunder, wind,
                     f"{labels}[sea][rain][thun][wind]amix=inputs={len(delays) + 4}:normalize=0,alimiter=limit=0.95[aout]"])
logo_on = sec("s11", 0.55)
vf = (f"[0:v]subtitles={os.path.join(D, 'final.ass')}:fontsdir={os.path.join(PV, 'fonts')}[v0];"
      f"[{len(delays) + 1}:v]scale=520:520,format=rgba,fade=in:st={logo_on}:d=1:alpha=1[lg];"
      f"[v0][lg]overlay=(W-w)/2:(H-h)/2:enable='gte(t,{logo_on})'[vout]")
cmd = (["ffmpeg", "-y", "-i", os.path.join(D, "video_silent.mp4")] + ins +
       ["-loop", "1", "-framerate", "24", "-t", str(TOTAL), "-i", LOGO,
        "-filter_complex", fc + ";" + vf, "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-t", str(TOTAL), os.path.join(D, "nuh_and_the_ark.mp4")])
subprocess.run(cmd, check=True)
print("wrote nuh_and_the_ark.mp4", TOTAL)

"""Turns the rendered previz frames into nuh_previz.mp4 with narration, subtitles,
scene labels, simple rain/sea ambience and the Toon Noon logo at the end."""
import json, os, re, subprocess

D = os.path.dirname(os.path.abspath(__file__))
FPS, LEAD = 8, 1.0
shots = json.load(open(os.path.join(D, "shots.json")))
durs = dict(json.load(open(os.path.join(D, "durations.json"))))
text = dict(json.load(open(os.path.join(D, "narration.json"))))
TITLES = {
    "s01": "Hook", "s02": "The people forget Allah", "s03": "Nuh's message",
    "s04": "They would not listen", "s05": "Kindness to everyone", "s06": "Building the ark",
    "s07": "All aboard", "s08": "The great flood", "s09": "Peace returns",
    "s10": "The lessons", "s11": "Outro",
}
LOGO = os.path.join(D, "..", "..", "logo-gemini", "toon-noon-gemini-stacked.png")


def t(sec):
    h, r = divmod(max(sec, 0), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1280", "PlayResY: 720", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
       "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Sub,Fredoka Light SemiBold,34,&H00FFFFFF,&H00FFFFFF,&H00442A1F,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,80,80,36,1",
       "Style: Label,Fredoka Light SemiBold,22,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,3,6,0,7,24,24,20,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
delays = []
for i, (sid, (f0, f1)) in enumerate(shots.items()):
    s0, s1 = (f0 - 1) / FPS, f1 / FPS
    ass.append(f"Dialogue: 1,{t(s0)},{t(s1)},Label,,0,0,0,,PREVIZ  ·  Scene {i + 1}: {TITLES[sid]}")
    start = s0 + LEAD
    delays.append((sid, start))
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text[sid]) if p.strip()]
    total = sum(len(p) for p in parts)
    cur = start
    for p in parts:
        dur = durs[sid] * len(p) / total
        ass.append(f"Dialogue: 0,{t(cur)},{t(cur + dur)},Sub,,0,0,0,,{p}")
        cur += dur
open(os.path.join(D, "subs.ass"), "w").write("\n".join(ass) + "\n")

total = shots["s11"][1] / FPS
ins, mix = [], []
for k, (sid, st) in enumerate(delays):
    ins += ["-i", os.path.join(D, "audio", f"{sid}.mp3")]
    ms = round(st * 1000)
    mix.append(f"[{k + 1}:a]adelay={ms}|{ms},volume=1.0[n{k}]")
# Ambience: soft sea in shot 1, rain from mid shot 7 to the end of shot 8.
def sec(sid, frac):
    a, b = shots[sid]
    return (a - 1 + (b - a) * frac) / FPS
sea = f"anoisesrc=c=brown:a=0.05:d={total}:r=24000,lowpass=f=500,volume='if(lt(t,{sec('s01', 1)}),1,0)':eval=frame[sea]"
rain = (f"anoisesrc=c=pink:a=0.05:d={total}:r=24000,highpass=f=800,lowpass=f=6000,"
        f"volume='if(between(t,{sec('s07', 0.4)},{sec('s08', 1)}),1,0)':eval=frame[rain]")
labels = "".join(f"[n{k}]" for k in range(len(delays)))
fc = ";".join(mix + [sea, rain, f"{labels}[sea][rain]amix=inputs={len(delays) + 2}:normalize=0,alimiter=limit=0.95[aout]"])

logo_on = sec("s11", 0.35)
vf = (f"[0:v]scale=1280:720:flags=lanczos,subtitles={os.path.join(D, 'subs.ass')}:fontsdir={os.path.join(D, 'fonts')}[v0];"
      f"[{len(delays) + 1}:v]scale=420:420,format=rgba,fade=in:st={logo_on}:d=1:alpha=1[lg];"
      f"[v0][lg]overlay=(W-w)/2:(H-h)/2-20:enable='gte(t,{logo_on})'[vout]")
cmd = (["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(D, "frames", "f_%05d.png")] + ins +
       ["-loop", "1", "-framerate", str(FPS), "-t", str(total), "-i", LOGO,
        "-filter_complex", fc + ";" + vf, "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-r", "24", "-c:a", "aac", "-b:a", "160k",
        "-t", str(total), os.path.join(D, "nuh_previz.mp4")])
subprocess.run(cmd, check=True)
print("wrote nuh_previz.mp4", round(total, 1), "s")

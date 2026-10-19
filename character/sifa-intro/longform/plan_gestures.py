#!/usr/bin/env python3
"""Where Sifa gestures -> gestures.json (per section: [[seconds_into_section, gesture, trigger_word], ...])

How real hosts move (gameranx / streamer facecams, and the reference Short): hands rest most of the time;
a gesture starts just before the stressed word it belongs to and is over in 1-2 s; the "yes" gesture
(right hand up to chest height, fingers loosely curled, bobbing like a nod) only lands on a strong
positive line. Here: one gesture every 15-30 s, picked by the words she says (aligned word times),
yes only on the key lines, nothing during the chapter wipe.
"""
import json
import re

import render_longform as v1
import render_v2 as r

RULES = [   # first match wins
    ("yes",   r"^(absolutely|best|love|agent|worth|yes|easily|finally)$"),
    ("count", r"^(one|two|three|four|five)[:,.]?$"),
    ("point", r"^(look|see|watch|here|this|these|that's)$"),
    ("both",  r"^(huge|massive|biggest|everything|whole|all|every|entire)$"),
    ("palm",  r"^(so|what|how|why|and|but|now|if|because)$"),
]
GAP_MIN, GAP_MAX, START = 15.0, 30.0, 2.0
LEAD_IN = 0.4   # the hand starts moving a little before the word


def plan(section):
    voice = v1.BUILD / f"vo_{section['id']}.wav"
    words = r.word_times(section["text"], voice, v1.LEAD)
    picks, last = [], -GAP_MIN
    for w, t0, _ in words:
        if t0 < START or t0 - last < GAP_MIN:
            continue
        key = r._norm(w)
        kind = next((k for k, pat in RULES if re.match(pat, key)), None)
        # a strong word always counts; a soft one only once we're due (~22 s without a gesture)
        if kind in ("yes", "count", "point", "both") or (kind == "palm" and t0 - last > 22) or t0 - last > GAP_MAX:
            picks.append([round(t0 - LEAD_IN, 2), kind or "palm", w])
            last = t0
    return picks


if __name__ == "__main__":
    out = {s["id"]: plan(s) for s in v1.SECTIONS}
    json.dump(out, open(v1.HERE / "gestures.json", "w"), indent=1)
    for sid, g in out.items():
        print(sid, g)

"""Generate one Veo 3.1 image-to-video shot for the Sifa intro via the Gemini API.

Run: python3 gen_veo.py <first_frame.png> <prompt.txt> <out.mp4>
Auth is injected by the session proxy; set GEMINI_API_KEY to run elsewhere.
"""
import base64
import json
import os
import sys
import time
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "veo-3.1-generate-preview"

frame, prompt_file, out = sys.argv[1:4]
key = os.environ.get("GEMINI_API_KEY")
headers = {"Content-Type": "application/json", **({"x-goog-api-key": key} if key else {})}


def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


body = {
    "instances": [{
        "prompt": open(prompt_file).read().strip(),
        "image": {"bytesBase64Encoded": base64.b64encode(open(frame, "rb").read()).decode(),
                  "mimeType": "image/png"},
    }],
    "parameters": {"aspectRatio": "16:9", "resolution": "1080p", "durationSeconds": 8,
                   "personGeneration": "allow_adult"},
}
op = call(f"{API}/models/{MODEL}:predictLongRunning", body)
print("operation", op["name"], flush=True)
while not op.get("done"):
    time.sleep(10)
    op = call(f"{API}/{op['name']}")
if "error" in op:
    sys.exit(f"Veo error: {op['error']}")
resp = op["response"]["generateVideoResponse"]
samples = resp.get("generatedSamples")
if not samples:
    sys.exit(f"No video returned: {json.dumps(resp)[:500]}")
req = urllib.request.Request(samples[0]["video"]["uri"], headers=headers)
with urllib.request.urlopen(req, timeout=300) as r, open(out, "wb") as f:
    f.write(r.read())
print("saved", out)

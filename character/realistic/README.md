# Realistic character art (AI-generated)

Photorealistic 3D-render versions of the Tin Gods cast. The flat vector art in `../` and `../cast/` is still what the website uses.

`previews/` holds 200px thumbnails only (from Canva). Full-size originals live at the links below.
**Figma links expire 7 days after 2026-10-05. Download them before then.**

All 10 full-size (1024px) images are in this folder and are what the website uses (2026-10-05). Source of each:

| Character | File | Made with |
|---|---|---|
| Judge SI | judge-si.png | Figma |
| Detective Sniffles SI | detective-sniffles.png | Figma |
| Chef SI | chef-si.png | Figma |
| Coach SI | coach-si.png | Figma |
| Dr. Heartbreak SI | dr-heartbreak.png | Figma |
| Anchor SI | anchor-si.png | Figma |
| Professor SI | professor-si.png | Figma |
| DJ SI | dj-si.png | Figma, cropped to remove a real brand name that appeared on the turntables |
| Banker SI | banker-si.png | Figma |
| Astronaut SI | astronaut-si.png | Figma |

`previews/` keeps the earlier 200px Canva versions of Judge SI, Sniffles, Chef, Coach and Dr. Heartbreak (not used by the site).

Prompts used a shared style: "Photorealistic 3D render, portrait from the chest up, brushed chrome robot, dark glass visor with glowing cyan eyes, small round gold SI badge, cinematic rim lighting, octane render, 8k, no text".

## How the website uses these
`python3 site/build.py "Tin Gods"` looks for `character/realistic/<stem>.png|jpg|webp` and swaps that character's art to the realistic image (resized to 640px and embedded). Characters without a file keep their vector art.

Stems: `judge-si`, `detective-sniffles`, `chef-si`, `coach-si`, `dr-heartbreak`, `anchor-si`, `professor-si`, `dj-si`, `banker-si`, `astronaut-si`.

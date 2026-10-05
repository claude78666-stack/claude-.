# Realistic character art (AI-generated)

Photorealistic 3D-render versions of the Tin Gods cast. The flat vector art in `../` and `../cast/` is still what the website uses.

`previews/` holds 200px thumbnails only (from Canva). Full-size originals live at the links below.
**Figma links expire 7 days after 2026-10-05. Download them before then.**

| Character | Source | Full-size link |
|---|---|---|
| Judge SI | Canva | https://www.canva.com/M/MAHXJZqZbiA |
| Judge SI (alt) | Figma | https://www.figma.com/api/mcp/asset/95890460-81f7-4b6d-8135-4bcf6db4c716.png |
| Detective Sniffles SI | Canva | https://www.canva.com/M/MAHXJaWW1KU |
| Chef SI | Canva | https://www.canva.com/M/MAHXJVDKX-c |
| Coach SI | Canva | https://www.canva.com/M/MAHXJT8oxds |
| Dr. Heartbreak SI | Canva | https://www.canva.com/M/MAHXJSrE69U |
| Anchor SI | Figma | https://www.figma.com/api/mcp/asset/0133f968-de20-4ef8-9629-b7fb9879030d.png |
| Professor SI | Figma | https://www.figma.com/api/mcp/asset/e4d1faac-cd69-429b-b18d-eba2f59b0ef9.png |
| DJ SI | Figma | https://www.figma.com/api/mcp/asset/4f0d9fc5-a9b9-41f1-90fe-42c124fc5464.png |
| Banker SI | Figma | https://www.figma.com/api/mcp/asset/bc4eaf23-7350-4162-aa8f-146710e8477b.png |
| Astronaut SI | Figma | https://www.figma.com/api/mcp/asset/2f643923-fb93-44cd-927b-fd40ab39dd8d.png |

Prompts used a shared style: "Photorealistic 3D render, portrait from the chest up, brushed chrome robot, dark glass visor with glowing cyan eyes, small round gold SI badge, cinematic rim lighting, octane render, 8k, no text".

## How the website uses these
`python3 site/build.py "Tin Gods"` looks for `character/realistic/<stem>.png|jpg|webp` and swaps that character's art to the realistic image (resized to 640px and embedded). Characters without a file keep their vector art.

Stems: `judge-si`, `detective-sniffles`, `chef-si`, `coach-si`, `dr-heartbreak`, `anchor-si`, `professor-si`, `dj-si`, `banker-si`, `astronaut-si`.

**Current state (2026-10-05):** the website uses the cartoon art for all 10 characters, by the owner's choice. The realistic images are parked: only 200px previews (in `previews/`) and the links above exist. To use realistic art again, put full-size files here named with the stems above and re-run the build.

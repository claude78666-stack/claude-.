// Uses FFmpeg to make square (1:1) and landscape (16:9) versions of a vertical render.
// Run: npm run resize            (defaults to out/showcase.mp4)
//      node scripts/resize.mjs path/to/video.mp4
// Needs `ffmpeg` on your PATH (https://ffmpeg.org/download.html).
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const input = process.argv[2] ?? 'out/showcase.mp4';
const { dir, name } = path.parse(input);

const targets = {
  square: 'scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2:color=0x0b1014',
  landscape: 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x0b1014',
};

for (const [label, vf] of Object.entries(targets)) {
  const out = path.join(dir, `${name}-${label}.mp4`);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', input, '-vf', vf, '-c:a', 'copy', out], {
    stdio: 'inherit',
  });
  console.log(`Wrote ${out}`);
}

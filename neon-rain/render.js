// usage: node render.js out.mp4 [testTimes comma list -> writes PNGs instead]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const dir = __dirname;
(async () => {
  const out = process.argv[2];
  const tests = process.argv[3];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('pageerror', e => console.error('PAGE ERROR', e));
  await p.goto('file://' + path.join(dir, 'scene.html'));
  await p.waitForFunction('window.ready===true');
  if (tests) {
    for (const t of tests.split(',').map(Number)) {
      const d = await p.evaluate(t => { draw(t); return document.getElementById('c').toDataURL('image/png'); }, t);
      fs.writeFileSync(path.join(dir, `test_${t}.png`), Buffer.from(d.split(',')[1], 'base64'));
    }
    await b.close(); return;
  }
  const FPS = 30, N = 300;
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) {
    const d = await p.evaluate(t => { draw(t); return document.getElementById('c').toDataURL('image/jpeg', 0.94); }, i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) console.log('frame', i);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
})();

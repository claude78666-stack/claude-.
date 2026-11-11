// node render.js out.mp4 [t1,t2,...]  (serve this folder on :8765 first)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const [out, tests] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('pageerror', e => console.error('PAGE ERROR', e.message));
  p.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await p.goto('http://127.0.0.1:8765/index.html');
  await p.waitForFunction('window.ready===true', null, { timeout: 120000 });
  const grab = t => p.evaluate(t => { renderAt(t); return document.querySelector('canvas').toDataURL('image/jpeg', 0.94); }, t);
  if (tests) {
    for (const t of tests.split(',').map(Number)) {
      const s = Date.now(); const d = await grab(t);
      fs.writeFileSync(path.join(__dirname, `test_${t}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
      console.log('t', t, (Date.now() - s) + 'ms');
    }
    return b.close();
  }
  const FPS = 30, N = 300;
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '' + FPS, '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) {
    const d = await grab(i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 30 === 0) console.log('frame', i);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();

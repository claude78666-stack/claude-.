// Renders the logo SVGs to PNG with headless Chromium at 2x.
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch();
  for (const f of fs.readdirSync(__dirname).filter((x) => x.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(__dirname, f), 'utf8');
    const [, w, h] = svg.match(/width="(\d+)" height="(\d+)"/);
    const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 2 });
    await p.setContent(`<body style="margin:0">${svg}</body>`);
    await p.screenshot({ path: path.join(__dirname, f.replace('.svg', '.png')) });
    await p.close();
  }
  await b.close();
})();

// Renders blorp-*.svg to PNG with headless Chromium (no rsvg needed).
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1200 } });
  for (const f of fs.readdirSync(__dirname).filter((x) => /^blorp-.*\.svg$/.test(x))) {
    await p.setContent(`<body style="margin:0">${fs.readFileSync(path.join(__dirname, f), 'utf8')}</body>`);
    await p.screenshot({ path: path.join(__dirname, f.replace('.svg', '.png')) });
  }
  await b.close();
})();

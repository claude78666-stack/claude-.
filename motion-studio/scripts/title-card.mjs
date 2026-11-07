// Generates public/title.svg with Satori (JSX-style markup -> SVG).
// Run: npm run title-card
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import satori from 'satori';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const font = await fs.readFile(path.join(root, 'public', 'Inter-Black.otf'));

const h = (type, style, children) => ({ type, props: { style, children } });

const card = h(
  'div',
  {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#f3ead6',
    borderRadius: 48,
    border: '10px solid #d9a521',
  },
  [
    h('div', { fontSize: 44, color: '#2f8f83', letterSpacing: 10 }, 'CLAUDE CODE'),
    h('div', { fontSize: 120, color: '#0b1014', lineHeight: 1.05, marginTop: 20 }, 'Motion'),
    h('div', { fontSize: 120, color: '#e2603f', lineHeight: 1.05 }, 'Studio'),
    h('div', { fontSize: 36, color: '#0b1014', marginTop: 30, opacity: 0.7 }, 'describe it. render it.'),
  ],
);

const svg = await satori(card, {
  width: 900,
  height: 700,
  fonts: [{ name: 'Inter', data: font, weight: 900, style: 'normal' }],
});

await fs.writeFile(path.join(root, 'public', 'title.svg'), svg);
console.log('Wrote public/title.svg');

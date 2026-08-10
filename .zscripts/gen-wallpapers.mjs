import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';
import path from 'path';

const OUT_DIR = '/home/z/my-project/public/uploads/wallpapers';
fs.mkdirSync(OUT_DIR, { recursive: true });

const wallpapers = [
  ['wp_1.png', 'Abstract dark financial dashboard background, subtle glowing data graphs and candlestick charts, deep navy and emerald green accents, minimalist, professional, no text, high quality, 4k wallpaper'],
  ['wp_2.png', 'Majestic mountain summit at golden dawn, sea of clouds below, soft warm light, cinematic, serene, professional desktop wallpaper, no text'],
  ['wp_3.png', 'Abstract geometric network of golden nodes connected by thin lines on deep charcoal background, venture capital growth concept, elegant, minimal, no text, high quality wallpaper'],
  ['wp_4.png', 'Aerial view of financial district skyline at blue hour, glass skyscrapers glowing, subtle bokeh, cinematic, professional desktop wallpaper, no text'],
  ['wp_5.png', 'Abstract flowing data streams, dark background with cyan and amber light trails, digital finance concept, elegant, minimal, no text, 4k wallpaper'],
  ['wp_6.png', 'Minimalist gradient mesh background, deep slate blue to warm gold, soft smooth waves, modern professional, no text, desktop wallpaper'],
];

const zai = await ZAI.create();
let ok = 0;
for (const [file, prompt] of wallpapers) {
  const out = path.join(OUT_DIR, file);
  try {
    process.stdout.write(`generating ${file}... `);
    const resp = await zai.images.generations.create({ prompt, size: '1344x768' });
    const b64 = resp.data[0].base64;
    fs.writeFileSync(out, Buffer.from(b64, 'base64'));
    const sz = fs.statSync(out).size;
    console.log(`OK (${sz} bytes)`);
    ok++;
  } catch (e) {
    console.log(`FAIL: ${e.message}`);
  }
}
console.log(`DONE: ${ok}/${wallpapers.length} wallpapers generated`);

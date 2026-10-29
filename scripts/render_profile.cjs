/* Render self-contained SVG artwork without depending on installed system fonts. */
const fs = require('node:fs/promises');
const path = require('node:path');
const sharp = require('sharp');

const root = path.resolve(__dirname, '..');

async function render(source, target) {
  await sharp(source).png().toFile(target);
}

async function main() {
  for (const name of ['header', 'header-light', 'avatar', 'avatar-light']) {
    await render(path.join(root, 'assets/profile', name + '.svg'), path.join(root, 'assets/profile', name + '.png'));
  }
  const frames = process.argv[2];
  if (frames) {
    for (const name of ['header', 'header-light', 'avatar', 'avatar-light']) {
      const dir = path.join(frames, name);
      const files = (await fs.readdir(dir)).filter(file => file.endsWith('.svg')).sort();
      for (let i = 0; i < files.length; i += 3) {
        await Promise.all(files.slice(i, i + 3).map(file => render(path.join(dir, file), path.join(dir, file.replace('.svg', '.png')))));
      }
      process.stdout.write(`Rendered ${files.length} ${name} frames.\n`);
    }
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });

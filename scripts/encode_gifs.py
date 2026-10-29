"""Encode smooth, bounded-size GIFs using a shared palette per animation."""
import argparse
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('frames_dir', type=Path)
    args = parser.parse_args()
    for name in ('header', 'header-light', 'avatar', 'avatar-light'):
        files = sorted((args.frames_dir / name).glob('*.png'))
        images = [Image.open(file).convert('RGB') for file in files]
        # Include both a lit and quiet frame so the fixed palette retains skin
        # detail, the type, and all the moving accent colors without flickering.
        sample = Image.new('RGB', (images[0].width, images[0].height * 3))
        for index, frame in enumerate((images[0], images[len(images)//3], images[len(images)*2//3])):
            sample.paste(frame, (0, index * frame.height))
        palette = sample.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in images]
        target = ROOT / 'assets/profile' / (name + '.gif')
        indexed[0].save(target, save_all=True, append_images=indexed[1:], duration=100,
                        loop=0, disposal=1, optimize=True)
        print(f'{name}.gif: {len(indexed)} frames, {target.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()

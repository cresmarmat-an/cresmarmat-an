"""Generate portfolio-matched hero artwork and deterministic animation frames."""
import argparse
import base64
import math
from pathlib import Path

from design_utils import ROOT, embed_mark, grid, palette, svg_document, text_path

PORTRAIT = base64.b64encode((ROOT / 'assets/profile/portrait.png').read_bytes()).decode()


def portrait(x, y, size, p, phase):
    turn = math.sin(phase * math.tau) * 14
    r = size * .46
    center = size / 2
    return f'''<g transform="translate({x} {y})">
      <defs>
        <radialGradient id="portrait-coral"><stop stop-color="{p['accent']}" stop-opacity=".17"/><stop offset="1" stop-color="{p['accent']}" stop-opacity="0"/></radialGradient>
        <radialGradient id="portrait-violet"><stop stop-color="{p['secondary']}" stop-opacity=".2"/><stop offset="1" stop-color="{p['secondary']}" stop-opacity="0"/></radialGradient>
        <linearGradient id="u-upper" x2="0" y2="1"><stop stop-color="white"/><stop offset=".53" stop-color="white"/><stop offset=".77" stop-color="white" stop-opacity="0"/></linearGradient>
        <radialGradient id="u-lower" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix({size*.7} 0 0 {size*.72} {center} {size*.4})"><stop stop-color="white"/><stop offset=".4" stop-color="white"/><stop offset=".6" stop-color="white" stop-opacity=".95"/><stop offset=".76" stop-color="white" stop-opacity="0"/></radialGradient>
        <mask id="u-portrait" maskUnits="userSpaceOnUse" x="0" y="0" width="{size}" height="{size}"><rect width="{size}" height="{size}" fill="url(#u-upper)"/><rect width="{size}" height="{size}" fill="url(#u-lower)"/></mask>
      </defs>
      <ellipse cx="{size*.4}" cy="{size*.63}" rx="{size*.52}" ry="{size*.5}" fill="url(#portrait-coral)"/>
      <ellipse cx="{size*.67}" cy="{size*.35}" rx="{size*.49}" ry="{size*.5}" fill="url(#portrait-violet)"/>
      <circle cx="{center}" cy="{center}" r="{r}" fill="none" stroke="{p['accent']}" stroke-opacity=".25" stroke-width=".8"/>
      <circle cx="{center}" cy="{center}" r="{r*.89}" fill="none" stroke="{p['secondary']}" stroke-opacity=".3" stroke-dasharray="2 6" stroke-width=".7"/>
      <g transform="rotate({turn} {center} {center})"><circle cx="{center}" cy="{center-r}" r="2.5" fill="{p['accent']}"/></g>
      <g transform="rotate({-turn+135} {center} {center})"><circle cx="{center}" cy="{center-r*.89}" r="2" fill="{p['secondary']}"/></g>
      <image x="{size*.05}" y="{size*.05}" width="{size*.9}" height="{size*.9}" href="data:image/png;base64,{PORTRAIT}" mask="url(#u-portrait)"/>
    </g>'''


def hero(theme, mobile=False, phase=0):
    p = palette(theme)
    width, height = (480, 600) if mobile else (960, 400)
    field = grid(width, height, theme)
    # One cell of travel closes the loop without a grid jump.
    field = field.replace('patternUnits="userSpaceOnUse"', f'patternUnits="userSpaceOnUse" patternTransform="translate(0 {-phase*64:.3f})"')
    body = [field,
            f'<defs><radialGradient id="hero-ambient"><stop stop-color="{p["accent"]}" stop-opacity=".065"/><stop offset="1" stop-color="{p["accent"]}" stop-opacity="0"/></radialGradient></defs>',
            f'<ellipse cx="{width*.36}" cy="{height*.55}" rx="{width*.52}" ry="{height*.95}" fill="url(#hero-ambient)"/>']
    if mobile:
        body += [text_path("Hi, I'm", 32, 55, 20, p['text']),
                 text_path('Cresmar', 30, 128, 65, p['text']),
                 text_path('Mat-an', 30, 201, 65, p['text'])]
        positions = [(6, 1), (6, 3), (0, 7), (6, 8)]
        photo = (75, 260, 350)
    else:
        body += [text_path("Hi, I'm", 40, 100, 25, p['text']),
                 text_path('Cresmar', 35, 185, 80, p['text']),
                 text_path('Mat-an', 35, 274, 80, p['text'])]
        positions = [(7, 1), (8, 2), (14, 2), (6, 5), (0, 5)]
        photo = (570, 12, 376)
    names = ['luau', 'javascript', 'visualstudio', 'rust', 'vscode']
    colors = [p['accent'], p['secondary'], p['tertiary']]
    for index, (col, row) in enumerate(positions):
        x, y = col * 64, row * 64 - phase * 64
        loop_fade = math.sin(phase * math.pi) ** 2
        opacity = loop_fade * (.3 + .55 * (math.cos((phase + index * .19) * math.tau) * .5 + .5))
        body += [f'<g opacity="{opacity:.4f}"><rect x="{x+.5}" y="{y+.5:.3f}" width="63" height="63" rx="3" fill="{colors[index%3]}" fill-opacity=".075" stroke="{colors[index%3]}" stroke-opacity=".25" stroke-width=".7"/>',
                 embed_mark(names[index], x+17, y+17, 30, theme), '</g>']
    body.append(portrait(*photo, p, phase))
    # Thin routed signals move along the coordinate field; text and portrait stay still.
    signal_x = (phase * (width + 160) - 80)
    body.append(f'<path d="M{signal_x:.3f} {height-32}h38" stroke="{p["secondary"]}" stroke-opacity=".4" stroke-width="1"/>')
    body.append(f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="6" fill="none" stroke="{p["line"]}" stroke-width="1"/>')
    return svg_document(''.join(body), width, height, 'Cresmar Mat-an',
                        "A colorful coordinate field, Poppins lettering, and a portrait with a head-safe lower U fade.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frames-dir', type=Path)
    parser.add_argument('--frames', type=int, default=48)
    args = parser.parse_args()
    for theme in ('dark', 'light'):
        for mobile in (False, True):
            name = ('avatar' if mobile else 'header') + ('-light' if theme == 'light' else '')
            (ROOT / 'assets/profile' / (name + '.svg')).write_text(hero(theme, mobile, .25), encoding='utf-8', newline='\n')
            if args.frames_dir:
                target = args.frames_dir / name
                target.mkdir(parents=True, exist_ok=True)
                for frame in range(args.frames):
                    (target / f'{frame:03}.svg').write_text(hero(theme, mobile, frame / args.frames), encoding='utf-8', newline='\n')
    print('Generated responsive dark/light hero sources.')


if __name__ == '__main__':
    main()

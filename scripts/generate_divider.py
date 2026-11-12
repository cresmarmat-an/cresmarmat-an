"""Generate the thin gradient rule that separates the profile's intro from its links.

Run from any directory with: python scripts/generate_divider.py
It borrows the portfolio navigation's coral, violet and green line, fading out at
both ends, in a stronger variant for each GitHub color theme. The artwork is a
flat gradient, so it stretches to the README column without distortion.
"""

from pathlib import Path

from design_utils import palette


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "profile"
WIDTH, HEIGHT = 960, 2


def divider(theme):
    colors = palette(theme)
    opacity = .9 if theme == "light" else .85
    stops = (
        (0, colors["accent"], 0),
        (.25, colors["accent"], opacity),
        (.5, colors["secondary"], opacity),
        (.75, colors["tertiary"], opacity),
        (1, colors["tertiary"], 0),
    )
    gradient = "".join(
        f'<stop offset="{offset:g}" stop-color="{color}" stop-opacity="{alpha:g}"/>'
        for offset, color, alpha in stops
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="none">'
        f'<defs><linearGradient id="line">{gradient}</linearGradient></defs>'
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#line)"/></svg>\n'
    )


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for theme, name in (("dark", "divider.svg"), ("light", "divider-light.svg")):
        destination = OUTPUT / name
        destination.write_text(divider(theme), encoding="utf-8", newline='\n')
        print(destination.relative_to(ROOT))


if __name__ == "__main__":
    main()

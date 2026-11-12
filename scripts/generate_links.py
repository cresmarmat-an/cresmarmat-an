"""Generate self-contained Poppins link buttons for both GitHub color themes.

Run from any directory with: python scripts/generate_links.py
Typography is converted to paths by design_utils so GitHub's image renderer does
not depend on a locally installed font or an external stylesheet.

Each button hugs its label. The pills are compact enough that all five fit one
row in the narrowest desktop README column, and the first three fit one row on
a 360px phone, so the buttons wrap as 3 + 2 instead of leaving a lone orphan.
Every canvas keeps a small transparent margin, which gives neighbouring buttons
an even gap without any spacing markup in the README.
"""

from math import ceil
from pathlib import Path
from xml.etree import ElementTree as ET

from design_utils import palette, text_path, text_width


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "links"

HEIGHT = 42         # canvas height; the pill is the canvas minus the margin
MARGIN = 2          # transparent margin on every side
PAD = 14            # space between the pill edge and its content
ICON = 18           # icon box, drawn from a 24 unit artboard
GAP = 8             # space between icon and label
FONT = 13           # label size in px, Poppins Medium
RADIUS = 4          # matches the portfolio's controls

# Icon shapes retain the geometry used by the existing profile link assets.
# Each is drawn on a 24 unit artboard; the optional transform fits a glyph
# into that artboard.
STROKE = 'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
LINKS = (
    (
        "portfolio", "Portfolio", "accent", "",
        f'<g {STROKE}>'
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M3 12h18M12 3a17 17 0 0 1 0 18 17 17 0 0 1 0-18Z"/></g>',
    ),
    (
        "email", "Email", "accent", "",
        f'<g {STROKE}>'
        '<rect x="2.5" y="4.5" width="19" height="15" rx="3"/>'
        '<path d="m3 6 9 7 9-7"/></g>',
    ),
    (
        "x", "X", "secondary", "",
        f'<g {STROKE}>'
        '<path d="M4 3h4l12 18h-4L4 3Zm16 0L4 21"/></g>',
    ),
    (
        "facebook", "Facebook", "secondary", "",
        '<g fill="{color}" stroke="none">'
        '<path d="M14 22v-9h3l.5-4H14V7c0-1.1.4-2 2-2h2V1.5a21 21 0 0 0-3-.2c-3 0-5 1.8-5 5.2V9H7v4h3v9"/></g>',
    ),
    (
        "roblox", "Roblox", "tertiary", ' transform="translate(2 2) scale(.8333)"',
        '<g fill="{color}" stroke="none">'
        '<path d="M18.926 23.998 0 18.892 5.075.002 24 5.108ZM15.348 10.09l-5.282-1.453-1.414 5.273 5.282 1.453z"/></g>',
    ),
)


def metrics(label):
    """Pill width (even, so edges stay on whole pixels), canvas width, content width."""
    content = ICON + GAP + text_width(label, FONT, weight="Medium")
    pill = ceil((2 * PAD + content) / 2) * 2
    return pill, pill + 2 * MARGIN, content


def button(theme, slug, label, accent_key, fit, icon):
    colors = palette(theme)
    primary = slug == "portfolio"
    surface = colors["accent"] if primary else colors["card"]
    ink = colors["on_accent"] if primary else colors["text"]
    border = colors["accent"] if primary else colors["line"]
    icon_color = ink if primary else colors[accent_key]
    pill, width, content = metrics(label)
    left = MARGIN + (pill - content) / 2
    scale = ICON / 24
    centre = HEIGHT / 2
    baseline = centre + FONT * 0.35
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" '
        f'viewBox="0 0 {width} {HEIGHT}" role="img" aria-labelledby="title">'
        f'<title id="title">{label}</title>'
        f'<rect x="{MARGIN + .5}" y="{MARGIN + .5}" width="{pill - 1}" height="{HEIGHT - 2 * MARGIN - 1}" '
        f'rx="{RADIUS}" fill="{surface}" stroke="{border}" stroke-width="1"/>'
        f'<g transform="translate({left:.3f} {centre - ICON / 2:.3f}) scale({scale})">'
        f'<g{fit}>' + icon.format(color=icon_color) + '</g></g>'
        + text_path(label, left + ICON + GAP, baseline, FONT, ink, weight="Medium")
        + '</svg>\n'
    )


def validate(source, label):
    svg = ET.fromstring(source)
    ns = "{http://www.w3.org/2000/svg}"
    pill, width, _ = metrics(label)
    assert svg.get("width") == str(width) and svg.get("height") == str(HEIGHT)
    assert svg.get("viewBox") == f"0 0 {width} {HEIGHT}"
    assert svg.find(f"{ns}title").text == label
    rect = svg.find(f"{ns}rect")
    assert rect.get("rx") == str(RADIUS) and rect.get("stroke-width") == "1"
    assert rect.get("x") == str(MARGIN + .5) and rect.get("y") == str(MARGIN + .5)
    assert rect.get("width") == str(pill - 1) and rect.get("height") == str(HEIGHT - 2 * MARGIN - 1)
    assert all(node.tag not in {f"{ns}script", f"{ns}foreignObject", f"{ns}text", f"{ns}image"} for node in svg.iter())
    assert "href=" not in source and "url(" not in source


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "light"):
        suffix = "" if theme == "dark" else "-light"
        for slug, label, accent_key, fit, icon in LINKS:
            source = button(theme, slug, label, accent_key, fit, icon)
            validate(source, label)
            destination = OUTPUT / f"{slug}{suffix}.svg"
            destination.write_text(source, encoding="utf-8", newline='\n')
            print(destination.relative_to(ROOT), f"{metrics(label)[1]}x{HEIGHT}")


if __name__ == "__main__":
    main()

"""Generate self-contained Poppins link buttons for both GitHub color themes.

Run from any directory with: python scripts/generate_links.py
Typography is converted to paths by design_utils so GitHub's image renderer does
not depend on a locally installed font or an external stylesheet.
"""

from pathlib import Path
from xml.etree import ElementTree as ET

from design_utils import palette, text_path, text_width


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "links"

# Icon shapes retain the geometry used by the existing profile link assets.
LINKS = (
    (
        "portfolio", "Portfolio", "accent",
        '<g transform="translate(16 14)" fill="none" stroke="{color}" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M3 12h18M12 3a17 17 0 0 1 0 18 17 17 0 0 1 0-18Z"/></g>',
    ),
    (
        "email", "Email", "accent",
        '<g transform="translate(16 14)" fill="none" stroke="{color}" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2.5" y="4.5" width="19" height="15" rx="3"/>'
        '<path d="m3 6 9 7 9-7"/></g>',
    ),
    (
        "x", "X", "secondary",
        '<g transform="translate(16 14)" fill="none" stroke="{color}" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M4 3h4l12 18h-4L4 3Zm16 0L4 21"/></g>',
    ),
    (
        "facebook", "Facebook", "secondary",
        '<g transform="translate(16 14)" fill="{color}" stroke="none">'
        '<path d="M14 22v-9h3l.5-4H14V7c0-1.1.4-2 2-2h2V1.5a21 21 0 0 0-3-.2c-3 0-5 1.8-5 5.2V9H7v4h3v9"/></g>',
    ),
    (
        "roblox", "Roblox", "tertiary",
        '<g transform="translate(18 16) scale(.8333)" fill="{color}" stroke="none">'
        '<path d="M18.926 23.998 0 18.892 5.075.002 24 5.108ZM15.348 10.09l-5.282-1.453-1.414 5.273 5.282 1.453z"/></g>',
    ),
)


def button(theme, slug, label, accent_key, icon):
    colors = palette(theme)
    primary = slug == "portfolio"
    surface = colors["accent"] if primary else colors["card"]
    ink = colors["on_accent"] if primary else colors["text"]
    border = colors["accent"] if primary else colors["line"]
    icon_color = ink if primary else colors[accent_key]
    content_width = 24 + 12 + text_width(label, 15, weight="Medium")
    content_shift = (164 - content_width) / 2 - 16
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="164" height="52" '
        'viewBox="0 0 164 52" role="img" aria-labelledby="title">'
        f'<title id="title">{label}</title>'
        f'<rect x=".5" y="3.5" width="163" height="45" rx="4" '
        f'fill="{surface}" stroke="{border}" stroke-width="1"/>'
        f'<g transform="translate({content_shift:.3f} 0)">'
        + icon.format(color=icon_color)
        + text_path(label, 52, 31, 15, ink, weight="Medium")
        + '</g></svg>\n'
    )


def validate(source, label):
    svg = ET.fromstring(source)
    ns = "{http://www.w3.org/2000/svg}"
    assert svg.get("width") == "164" and svg.get("height") == "52"
    assert svg.get("viewBox") == "0 0 164 52"
    assert svg.find(f"{ns}title").text == label
    assert svg.find(f"{ns}rect").get("rx") == "4"
    assert svg.find(f"{ns}rect").get("stroke-width") == "1"
    assert svg.find(f"{ns}rect").get("y") == "3.5"
    assert svg.find(f"{ns}rect").get("height") == "45"
    assert all(node.tag not in {f"{ns}script", f"{ns}foreignObject", f"{ns}text", f"{ns}image"} for node in svg.iter())
    assert "href=" not in source and "url(" not in source
    assert "M146 23v6" not in source
    content_width = 24 + 12 + text_width(label, 15, weight="Medium")
    assert svg.find(f"{ns}g").get("transform") == f"translate({(164 - content_width) / 2 - 16:.3f} 0)"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "light"):
        suffix = "" if theme == "dark" else "-light"
        for slug, label, accent_key, icon in LINKS:
            source = button(theme, slug, label, accent_key, icon)
            validate(source, label)
            destination = OUTPUT / f"{slug}{suffix}.svg"
            destination.write_text(source, encoding="utf-8", newline='\n')
            print(destination.relative_to(ROOT))


if __name__ == "__main__":
    main()

"""Generate compact, self-contained technology sections in both color schemes.

Run with the same Python/fontTools environment as scripts/design_utils.py.
All text is outlined Poppins and all marks are embedded local SVG geometry.
"""
from html import escape
from pathlib import Path

from design_utils import embed_mark, grid, palette, svg_document, text_path, text_width


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "sections"
SECTIONS = (
    (
        "roblox", "Roblox development", "Luau, Lua, Roblox Studio, Rojo",
        (("luau", "Luau"), ("lua", "Lua"), ("roblox-studio", "Roblox Studio"), ("rojo", "Rojo")),
    ),
    (
        "web", "Web development", "Interfaces, styling, and interactive graphics",
        (("javascript", "JavaScript"), ("typescript", "TypeScript"), ("nextjs", "Next.js"),
         ("nodejs", "Node.js"), ("html", "HTML"), ("css", "CSS"),
         ("tailwindcss", "Tailwind CSS"), ("threejs", "Three.js")),
    ),
    (
        "systems", "Languages and tooling", "Python, C, C#, C++, Rust, Git, VS Code, Visual Studio",
        (("python", "Python"), ("c", "C"), ("csharp", "C#"), ("cpp", "C++"),
         ("rust", "Rust"), ("git", "Git"), ("vscode", "VS Code"), ("visualstudio", "Visual Studio")),
    ),
)


def technology_cell(name, label, center_x, top, theme, mobile, accent):
    """A single 64px coordinate cell with a readable label beneath it."""
    p = palette(theme)
    left = center_x - 32
    label_size = 15.5 if mobile else 14
    # Cap the longest label to its slot without changing its words.
    label_size = min(label_size, label_size * 106 / max(106, text_width(label, label_size)))
    pieces = [
        f'<g role="listitem" aria-label="{escape(label, quote=True)}">',
        f'<title>{escape(label)}</title>',
        f'<rect x="{left}" y="{top}" width="64" height="64" rx="4" fill="{p["card"]}" stroke="{p["line"]}"/>',
        f'<path d="M{left + 9} {top + .5}H{left + .5}V{top + 9}M{left + 55} {top + 63.5}H{left + 63.5}V{top + 55}" fill="none" stroke="{accent}" stroke-opacity=".75" stroke-width="1"/>',
        embed_mark(name, left + 12, top + 12, 40, theme),
        text_path(label, center_x, top + 91, label_size, p["text"], anchor="middle"),
        '</g>',
    ]
    return ''.join(pieces)


def section_svg(slug, title, subtitle, items, theme, mobile):
    width = 480 if mobile else 960
    height = (226 if len(items) == 4 else 330) if mobile else (220 if len(items) == 4 else 236)
    p = palette(theme)
    margin = 24 if mobile else 32
    title_size = 23 if mobile else 25
    subtitle_size = 12 if mobile else 13
    body = [
        f'<defs><clipPath id="panel-clip"><rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="6"/></clipPath></defs>',
        '<g clip-path="url(#panel-clip)">', grid(width, height, theme),
        # A quiet title strip keeps the coordinate field behind the tools.
        f'<rect x="1" y="1" width="{width - 2}" height="80" fill="{p["bg"]}" fill-opacity=".93"/>',
        text_path(title, margin, 42, title_size, p["text"], weight="Regular"),
        text_path(subtitle, margin, 66, subtitle_size, p["muted"]),
    ]
    # Three small registration points echo the portfolio's colored circuit nodes.
    if not mobile:
        for index, color in enumerate((p["accent"], p["secondary"], p["tertiary"])):
            body.append(f'<circle cx="{width - 64 + index * 13}" cy="38" r="2" fill="{color}" opacity=".85"/>')
    body.append('<g role="list" aria-label="Technologies">')
    columns = 4 if mobile else len(items)
    slot_width = 112
    start_x = (width - (columns - 1) * slot_width) / 2
    top = 104 if mobile else (100 if len(items) == 4 else 110)
    accents = (p["accent"], p["secondary"], p["tertiary"])
    for index, (name, label) in enumerate(items):
        row, column = divmod(index, columns)
        center_x = start_x + column * slot_width
        body.append(technology_cell(name, label, center_x, top + row * 112, theme, mobile, accents[index % 3]))
    body.extend([
        '</g></g>',
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="6" fill="none" stroke="{p["line"]}"/>',
    ])
    description = title + ': ' + ', '.join(label for _, label in items) + '. ' + subtitle
    return svg_document(''.join(body), width, height, title, description)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for slug, title, subtitle, items in SECTIONS:
        for theme in ("dark", "light"):
            for mobile in (False, True):
                suffix = ('-mobile' if mobile else '') + ('-light' if theme == 'light' else '')
                target = OUTPUT / (slug + suffix + '.svg')
                target.write_text(section_svg(slug, title, subtitle, items, theme, mobile), encoding='utf-8', newline='\n')
                print(target.relative_to(ROOT))


if __name__ == '__main__':
    main()

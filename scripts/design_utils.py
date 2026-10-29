"""Shared, self-contained SVG primitives for the portfolio-matched profile."""
from functools import lru_cache
from pathlib import Path
from html import escape
import copy
import re
import xml.etree.ElementTree as ET

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent.parent
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

def palette(theme):
    if isinstance(theme, dict):
        return theme
    if theme == 'light':
        return dict(bg='#faf8f5', card='#fffdfa', text='#25211f', muted='#736a64',
                    accent='#bd4129', secondary='#9763bf', tertiary='#708b3e',
                    line='#dfd6ce', on_accent='#fffdfa')
    return dict(bg='#111010', card='#1b1818', text='#f6f1eb', muted='#a2978f',
                accent='#fa8066', secondary='#be8ee4', tertiary='#a0c25f',
                line='#3a3330', on_accent='#21120e')

@lru_cache(maxsize=4)
def font_data(weight='Regular'):
    font = TTFont(ROOT / 'assets' / 'fonts' / ('Poppins-' + weight + '.ttf'))
    return font, font.getGlyphSet(), font.getBestCmap(), font['head'].unitsPerEm

def text_width(text, size, weight='Regular'):
    font, glyphs, cmap, units = font_data(weight)
    return sum(font['hmtx'].metrics[cmap.get(ord(char), '.notdef')][0] for char in text) * size / units

def text_path(text, x, y, size, color, weight='Regular', anchor='start'):
    font, glyphs, cmap, units = font_data(weight)
    width = text_width(text, size, weight)
    if anchor in ('middle', 'center'):
        x -= width / 2
    elif anchor in ('end', 'right'):
        x -= width
    pen = SVGPathPen(glyphs)
    advance = 0
    for char in text:
        name = cmap.get(ord(char), '.notdef')
        glyphs[name].draw(TransformPen(pen, (1, 0, 0, 1, advance, 0)))
        advance += font['hmtx'].metrics[name][0]
    scale = size / units
    return (f'<g aria-label="{escape(text, quote=True)}" fill="{color}" '
            f'transform="translate({x:.3f} {y:.3f}) scale({scale:.7f} {-scale:.7f})">'
            f'<path d="{pen.getCommands()}"/></g>')

def grid(width, height, theme, cell=64):
    p = palette(theme)
    return (f'<defs><pattern id="coordinate-grid" width="{cell}" height="{cell}" patternUnits="userSpaceOnUse">'
            f'<path d="M{cell} 0H0V{cell}" fill="none" stroke="{p["line"]}" stroke-width=".7"/>'
            '</pattern></defs>'
            f'<rect width="{width}" height="{height}" fill="{p["bg"]}"/>'
            f'<rect width="{width}" height="{height}" fill="url(#coordinate-grid)" opacity=".48"/>')

_mark_serial = 0

def embed_mark(name, x, y, size, theme):
    global _mark_serial
    _mark_serial += 1
    p = palette(theme)
    root = ET.parse(ROOT / 'assets' / 'marks' / (name + '.svg')).getroot()
    root = copy.deepcopy(root)
    for key in ('x', 'y', 'width', 'height', 'role', 'aria-labelledby'):
        root.attrib.pop(key, None)
    root.set('x', str(x)); root.set('y', str(y))
    root.set('width', str(size)); root.set('height', str(size))
    root.set('preserveAspectRatio', 'xMidYMid meet')
    if name in ('rust', 'threejs'):
        root.set('fill', p['text'])
    raw = ET.tostring(root, encoding='unicode')
    ids = re.findall(r'\bid="([^"]+)"', raw)
    for old in sorted(ids, key=len, reverse=True):
        new = f'mark-{_mark_serial}-{old}'
        raw = raw.replace(f'id="{old}"', f'id="{new}"')
        raw = raw.replace(f'url(#{old})', f'url(#{new})')
        raw = raw.replace(f'href="#{old}"', f'href="#{new}"')
    if name in ('rust', 'threejs', 'rojo'):
        raw = re.sub(r'(?i)(?<=fill=")(?:#fff(?:fff)?|white|#000(?:000)?|black)(?=")', p['text'], raw)
        raw = re.sub(r'(?i)fill:(?:white|black|#fff(?:fff)?|#000(?:000)?)(?=;|"|$)', 'fill:' + p['text'], raw)
    return raw

def svg_document(body, width, height, title, description=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
            f'<title>{escape(title)}</title><desc>{escape(description)}</desc>{body}</svg>\n')

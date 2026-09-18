"""Convert text to SVG path data using real font outlines (fontTools)."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = '/tmp/claude-0/fonts/'
_cache = {}


def font(name):
    if name not in _cache:
        _cache[name] = TTFont(FONTS + name)
    return _cache[name]


def text_path(txt, fontfile, size, x=0, y=0, tracking=0.0, anchor='middle'):
    """Return (d, width). y is the baseline. tracking in em units."""
    f = font(fontfile)
    upm = f['head'].unitsPerEm
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f['hmtx']
    s = size / upm
    advs = []
    names = []
    for ch in txt:
        g = cmap.get(ord(ch))
        names.append(g)
        adv = hmtx[g][0] if g else upm * 0.3
        advs.append(adv * s + tracking * size)
    total = sum(advs) - tracking * size
    if anchor == 'middle':
        cx = x - total / 2
    elif anchor == 'end':
        cx = x - total
    else:
        cx = x
    parts = []
    for g, adv in zip(names, advs):
        if g:
            pen = SVGPathPen(gs)
            tp = TransformPen(pen, (s, 0, 0, -s, cx, y))
            gs[g].draw(tp)
            parts.append(pen.getCommands())
        cx += adv
    return ' '.join(parts), total

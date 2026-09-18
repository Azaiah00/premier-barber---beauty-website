"""Vector remaster of the Premier Barber & Beauty badge.
Outputs SVG variants + high-res transparent PNG/WebP exports."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from textpath import text_path
import cairosvg

OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT, exist_ok=True)

BLUE = '#1f3fe0'
BLUE_D = '#0a1a86'
BLUE_L = '#4d6bff'
INK = '#0a0a0c'
WHITE = '#ffffff'
ALFA = 'fontsource-alfa-slab-one-5.3.0/files/alfa-slab-one-latin-400-normal.woff'
ZILLA = 'fontsource-zilla-slab-5.3.0/files/zilla-slab-latin-700-normal.woff'

C = (600, 632)


def rot(x, y, a, cx=0, cy=0):
    r = math.radians(a)
    return (cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r))


def razor(mirror=False):
    """Open straight razor. Pivot at origin. Blade rotated separately from handle."""
    blade = ('M-468,-46 L-150,-36 C-114,-35 -86,-30 -64,-22 L-16,-11 L-12,11 '
             'C-44,16 -78,20 -118,25 C-160,30 -190,33 -230,36 L-450,50 C-464,51 -472,44 -472,36 Z')
    bevel = 'M-452,14 L-200,9 C-150,7 -110,4 -80,-1'
    edge = 'M-450,50 L-230,36 C-190,33 -160,30 -118,25'
    tang = 'M-20,-14 C-8,-22 10,-20 18,-10 L18,10 C8,18 -8,18 -14,12 Z'
    handle = ('M20,-24 C170,-33 360,-38 528,-36 C562,-35 580,-18 580,0 C580,18 562,35 528,36 '
              'C360,38 170,33 20,24 C10,16 10,-16 20,-24 Z')
    handle_hi = 'M56,-15 C210,-23 380,-27 512,-25'
    ba, ha = 25, 16
    g = f'''
      <g transform="rotate({ha})">
        <path d="{handle}" fill="{INK}" stroke="{WHITE}" stroke-width="5"/>
        <path d="{handle_hi}" fill="none" stroke="#3a3d48" stroke-width="5" stroke-linecap="round"/>
        <circle cx="544" cy="0" r="10" fill="{WHITE}"/><circle cx="544" cy="0" r="3.5" fill="{INK}"/>
      </g>
      <g transform="rotate({ba})">
        <path d="{blade}" fill="{WHITE}" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>
        <path d="{bevel}" fill="none" stroke="#c3c9d8" stroke-width="4" stroke-linecap="round"/>
        <path d="{edge}" fill="none" stroke="#8a93a8" stroke-width="2"/>
        <path d="{tang}" fill="{WHITE}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>
      </g>
      <circle cx="0" cy="0" r="8" fill="{INK}"/>
    '''
    P = (598, 574)
    if mirror:
        return f'<g transform="translate(1200,0) scale(-1,1)"><g transform="translate({P[0]},{P[1]})">{g}</g></g>'
    return f'<g transform="translate({P[0]},{P[1]})">{g}</g>'


def globe():
    cx, cy, r = C[0], C[1], 326
    lines = []
    for lat in range(-60, 90, 20):
        y = cy + r * math.sin(math.radians(lat)) * 0.98
        rx = r * math.cos(math.radians(lat))
        lines.append(f'<ellipse cx="{cx}" cy="{y:.1f}" rx="{rx:.1f}" ry="{rx*0.16:.1f}"/>')
    for lon in range(-75, 90, 25):
        rx = abs(r * math.sin(math.radians(lon)))
        lines.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{max(rx,0.5):.1f}" ry="{r}"/>')
    return ''.join(lines)


def wheat(side):
    """Wheat sprig: curved stem with paired slim grains."""
    parts = [f'<path d="M0,64 C-4,34 -2,4 10,-44" fill="none" stroke="{WHITE}" stroke-width="4.5" stroke-linecap="round"/>']
    for i in range(5):
        t = i / 4
        y = 44 - t * 78
        x = -2 + t * 8
        for sgn in (-1, 1):
            gx = x + sgn * 11
            parts.append(f'<path d="M{x:.1f},{y+6:.1f} C{gx - sgn*2:.1f},{y:.1f} {gx + sgn*6:.1f},{y-14:.1f} {gx + sgn*2:.1f},{y-26:.1f} '
                         f'C{gx - sgn*8:.1f},{y-16:.1f} {x:.1f},{y-6:.1f} {x:.1f},{y+6:.1f} Z" fill="{WHITE}" stroke="{BLUE_D}" stroke-width="1.6"/>')
    parts.append(f'<path d="M10,-40 C18,-54 16,-66 10,-76 C4,-66 2,-54 10,-40 Z" fill="{WHITE}" stroke="{BLUE_D}" stroke-width="1.6"/>')
    inner = ''.join(parts)
    tx = 600 + side * 142
    rotang = -48 * side
    sc = f'scale({-1 if side < 0 else 1},1)'
    return f'<g transform="translate({tx},416) rotate({rotang}) {sc}">{inner}</g>'


def comb(angle):
    teeth = ''.join(f'<rect x="{-15 + i*6}" y="-6" width="3" height="26" fill="{WHITE}"/>' for i in range(6))
    body = f'<rect x="-13" y="-72" width="26" height="144" rx="4" fill="{WHITE}" stroke="{BLUE_D}" stroke-width="3"/>'
    tooth_lines = ''.join(
        f'<line x1="-13" y1="{-64 + i*7}" x2="1" y2="{-64 + i*7}" stroke="{BLUE_D}" stroke-width="2"/>' for i in range(19))
    return f'<g transform="translate(600,388) rotate({angle})">{body}{tooth_lines}</g>'


def mini_razor(angle):
    blade = 'M-92,-7 L-12,-6 L0,0 L-12,6 L-90,8 Z'
    handle = 'M4,-5 L92,-5 C98,-5 100,-2 100,0 C100,2 98,5 92,5 L4,5 Z'
    return (f'<g transform="translate(600,436) rotate({angle})">'
            f'<path d="{handle}" fill="{WHITE}" stroke="{BLUE_D}" stroke-width="3"/>'
            f'<path d="{blade}" fill="{WHITE}" stroke="{BLUE_D}" stroke-width="3"/></g>')


def pole():
    x, top, bot, w = 600, 348, 458, 30
    stripes = ''.join(
        f'<path d="M{x-40},{top + i*22} l80,-40 l0,11 l-80,40 Z" fill="{BLUE}"/>' for i in range(-1, 9))
    return f'''
    <defs><clipPath id="poleclip"><rect x="{x-w/2}" y="{top}" width="{w}" height="{bot-top}" rx="4"/></clipPath></defs>
    <rect x="{x-w/2-8}" y="{top-14}" width="{w+16}" height="16" rx="5" fill="{WHITE}" stroke="{BLUE_D}" stroke-width="3"/>
    <circle cx="{x}" cy="{top-30}" r="18" fill="{WHITE}" stroke="{BLUE_D}" stroke-width="3"/>
    <path d="M{x-7},{top-38} a9,9 0 0 1 13,-2" fill="none" stroke="{BLUE_D}" stroke-width="3" stroke-linecap="round"/>
    <rect x="{x-w/2}" y="{top}" width="{w}" height="{bot-top}" rx="4" fill="{WHITE}"/>
    <g clip-path="url(#poleclip)">{stripes}</g>
    <rect x="{x-w/2}" y="{top}" width="{w}" height="{bot-top}" rx="4" fill="none" stroke="{BLUE_D}" stroke-width="3"/>
    <rect x="{x-w/2-8}" y="{bot-2}" width="{w+16}" height="16" rx="5" fill="{WHITE}" stroke="{BLUE_D}" stroke-width="3"/>
    '''


def crest():
    return (comb(-28) + comb(28) + mini_razor(-18) + mini_razor(198) + pole()
            + wheat(-1) + wheat(1))


def wordmarks():
    premier, pw = text_path('PREMIER', ALFA, 132, 600, 592, tracking=0.02)
    bb, bw = text_path('BARBER & BEAUTY', ALFA, 60, 600, 648, tracking=0.035)
    salon, sw = text_path('BARBER AND BEAUTY SALON', ZILLA, 30, 600, 684, tracking=0.42)
    bar_w = max(pw, bw) + 120
    x0 = 600 - bar_w / 2
    return f'''
    <!-- PREMIER banner -->
    <rect x="{x0}" y="478" width="{bar_w}" height="134" rx="8" fill="{WHITE}" stroke="{INK}" stroke-width="10"/>
    <path d="{premier}" transform="translate(8,8)" fill="{INK}" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>
    <path d="{premier}" fill="{INK}" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>
    <path d="{premier}" fill="{WHITE}"/>
    <!-- BARBER & BEAUTY -->
    <path d="{bb}" transform="translate(4,4)" fill="{INK}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>
    <path d="{bb}" fill="{INK}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>
    <path d="{bb}" fill="{BLUE}"/>
    <!-- salon band -->
    <rect x="{x0}" y="656" width="{bar_w}" height="40" fill="{INK}"/>
    <path d="{salon}" fill="{WHITE}"/>
    '''


def badge_svg(transparent=True, ondark=False):
    defs = f'''
    <defs>
      <radialGradient id="disc" cx="50%" cy="38%" r="70%">
        <stop offset="0" stop-color="{BLUE_L}"/>
        <stop offset="0.55" stop-color="{BLUE}"/>
        <stop offset="1" stop-color="{BLUE_D}"/>
      </radialGradient>
      <clipPath id="discclip"><circle cx="{C[0]}" cy="{C[1]}" r="326"/></clipPath>
      <linearGradient id="globefade" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0.45" stop-color="#fff" stop-opacity="0"/>
        <stop offset="0.75" stop-color="#fff" stop-opacity="1"/>
      </linearGradient>
      <mask id="globemask"><rect x="0" y="0" width="1200" height="1200" fill="url(#globefade)"/></mask>
    </defs>'''
    circle = f'''
    <circle cx="{C[0]}" cy="{C[1]}" r="362" fill="{INK}"/>
    <circle cx="{C[0]}" cy="{C[1]}" r="340" fill="{WHITE}"/>
    <circle cx="{C[0]}" cy="{C[1]}" r="326" fill="url(#disc)"/>
    <g clip-path="url(#discclip)" mask="url(#globemask)" fill="none" stroke="#9db1ff" stroke-width="2" opacity="0.38">{globe()}</g>
    '''
    key = f'<circle cx="{C[0]}" cy="{C[1]}" r="368" fill="{WHITE}"/>' if ondark else ''
    body = defs + key + circle + razor(False) + razor(True) + crest() + wordmarks()
    bg = '' if transparent else '<rect x="0" y="0" width="1200" height="1200" fill="#ffffff"/>'
    # crop to content: x 40..1160, y 262..1000
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="36 250 1128 752" width="1128" height="752" '
            f'role="img" aria-label="Premier Barber &amp; Beauty Salon logo">{bg}{body}</svg>')


if __name__ == '__main__':
    for name, kw in [('premier-badge', {}), ('premier-badge-ondark', {'ondark': True})]:
        svg = badge_svg(**kw)
        open(f'{OUT}/{name}.svg', 'w').write(svg)
        for w in (2400, 1200, 600, 320):
            cairosvg.svg2png(bytestring=svg.encode(), write_to=f'{OUT}/{name}-{w}.png', output_width=w)
    cairosvg.svg2png(bytestring=badge_svg(False).encode(), write_to=f'{OUT}/preview-white.png', output_width=1200)
    print('ok')

"""Wordmark, monogram, favicon set and OG image for Premier Barber & Beauty."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from textpath import text_path
from build_logo import ALFA, ZILLA, BLUE, BLUE_D, BLUE_L, INK, WHITE, OUT
import cairosvg
from PIL import Image


def monogram_svg(size=512, ring=True):
    p, pw = text_path('P', ALFA, 300, 256, 362)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="{size}" height="{size}">
  <defs><radialGradient id="g" cx="50%" cy="35%" r="70%"><stop offset="0" stop-color="{BLUE_L}"/>
  <stop offset=".6" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE_D}"/></radialGradient></defs>
  <circle cx="256" cy="256" r="252" fill="{INK}"/>
  <circle cx="256" cy="256" r="226" fill="{WHITE}"/>
  <circle cx="256" cy="256" r="210" fill="url(#g)"/>
  <path d="{p}" transform="translate(9,9)" fill="{INK}" stroke="{INK}" stroke-width="16" stroke-linejoin="round"/>
  <path d="{p}" fill="{INK}" stroke="{INK}" stroke-width="16" stroke-linejoin="round"/>
  <path d="{p}" fill="{WHITE}"/>
</svg>'''


def wordmark_svg(color=WHITE, accent=BLUE_L):
    """Horizontal lockup: PREMIER / BARBER & BEAUTY — for nav + footer."""
    prem, pw = text_path('PREMIER', ALFA, 100, 0, 92, tracking=0.03, anchor='start')
    sub, sw = text_path('BARBER & BEAUTY SALON', ZILLA, 25.5, 3, 132, tracking=0.34, anchor='start')
    w = max(pw, sw) + 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} 142" role="img" aria-label="Premier Barber &amp; Beauty Salon">
  <path d="{prem}" fill="{color}"/>
  <path d="{sub}" fill="{accent}"/>
</svg>'''


if __name__ == '__main__':
    open(f'{OUT}/premier-monogram.svg', 'w').write(monogram_svg())
    for s in (16, 32, 48, 180, 192, 512):
        cairosvg.svg2png(bytestring=monogram_svg().encode(), write_to=f'{OUT}/icon-{s}.png', output_width=s, output_height=s)
    Image.open(f'{OUT}/icon-48.png').save(f'{OUT}/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    open(f'{OUT}/premier-wordmark-white.svg', 'w').write(wordmark_svg())
    open(f'{OUT}/premier-wordmark-black.svg', 'w').write(wordmark_svg(INK, BLUE))
    for n in ('white', 'black'):
        cairosvg.svg2png(url=f'{OUT}/premier-wordmark-{n}.svg', write_to=f'{OUT}/premier-wordmark-{n}-1600.png', output_width=1600)
    print('ok')

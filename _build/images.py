"""Image manifest + optimizer. Crops use fractional boxes (l, t, r, b) of the source."""
import os, json
from PIL import Image, ImageOps

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')  # put original downloads here (pbb-<pro>-NN.jpg)

# id: (source, crop_box_fraction or None, alt, max_width)
KEY = {
    'hero':            ('maal-38', (0.0, 0.08, 1.0, 0.72), 'Master Barber Maal giving a client a razor line-up inside the blue-walled Premier Barber & Beauty Salon', 2200),
    'hero-portrait':   ('maal-38', (0.18, 0.0, 0.95, 1.0), 'Master Barber Maal at work inside Premier Barber & Beauty Salon', 1400),
    'space-chair':     ('maal-36', (0.0, 0.1, 1.0, 0.95), 'A black-and-chrome barber chair under ring lights against Premier’s royal-blue wall', 1400),
    'space-wide':      ('ig-23', None, 'Wide view of Premier Barber & Beauty Salon with hexagon LED ceiling lights, stations and a waiting lounge', 900),
    'space-room':      ('ig-06', None, 'A client relaxing in a barber chair between ring lights at Premier', 720),
    'space-sign':      ('samaya-22', (0.0, 0.0, 1.0, 0.5), 'The Premier Barber & Beauty sign on the white brick wall of the salon', 1400),
    # portraits (square)
    'maal-portrait':   ('maal-38', (0.36, 0.02, 0.86, 0.52), 'Portrait of Master Barber Maal', 900),
    'darnell-portrait':('darnell-01', None, 'Darnell Da Barber logo illustration', 400),
    'ryan-portrait':   ('ryan-39', (0.18, 0.0, 1.0, 0.82), 'Textured crop by Ryan In The Cut', 900),
    'samaya-portrait': ('samaya-04', (0.0, 0.08, 1.0, 0.83), 'Red wig install by Hair by Samaya', 900),
    'adonis-portrait': ('ig-16', (0.0, 0.0, 1.0, 0.56), 'Adonis, the Jack of All Fadez, in the Premier shop', 640),
    'saint-portrait':  ('saint-01', (0.02, 0.1, 0.98, 0.9), 'Blessed By Saint chrome logo', 900),
    'samaya-logo':     ('samaya-01', None, 'Hair by Samaya logo', 292),
    'saint-logo':      ('saint-01', (0.02, 0.18, 0.98, 0.82), 'Blessed By Saint chrome logo', 900),
    'adonis-avatar':   ('adonis-01', (0.28, 0.0, 0.72, 0.44), 'Illustrated portrait of Adonis, The Jack of All Fadez', 700),
    # cards (4:5-ish)
    'maal-card':       ('maal-16', None, 'Curly top with a clean skin fade by Master Barber Maal', 1100),
    'darnell-card':    ('igpost-5', (0.0, 0.05, 1.0, 0.62), 'Fresh fade by OG Barber Darnell inside Premier', 1100),
    'ryan-card':       ('ryan-22', None, 'Textured modern cut with a taper by Ryan In The Cut', 1100),
    'samaya-card':     ('samaya-22', (0.0, 0.08, 1.0, 1.0), 'Long red stitch braids by Hair by Samaya under the Premier sign', 1100),
    'adonis-card':     ('adonis-42', None, 'Twists with a sharp taper and line-up by Adonis Tha Barber', 1100),
    'saint-card':      ('saint-04', (0.0, 0.06, 1.0, 0.78), 'Top-knot with a skin fade under blue light by Blessed By Saint', 1100),
}

# gallery: (source, pro_slug, category, alt)
G = []
def g(src, pro, cat, alt):
    G.append((src, pro, cat, alt))

for n, alt in [('02', 'Low taper with textured top'), ('05', 'Copper textured crop with a burst fade'), ('06', 'Textured fringe with a low taper'),
               ('07', 'Teen taper with a sharp line-up'), ('10', 'Curly high top with a mid fade'), ('11', 'Clean waves with a crisp line-up'),
               ('12', 'Kids fade with a textured top'), ('15', 'Curly top with a taper'), ('17', 'Sharp line-up and beard'),
               ('18', 'Kids scissor cut'), ('19', 'Curly top with a skin fade'), ('22', 'Short natural cut with a taper'),
               ('24', 'Skin fade with a textured top and full beard'), ('25', 'Modern mullet with a skin fade'), ('30', 'Textured scissor cut'),
               ('33', 'Scissor-cut fringe'), ('34', 'Textured scissor cut with a taper')]:
    g(f'maal-{n}', 'maal', 'kids' if n in ('07', '12', '18') else 'barber', f'{alt} by Master Barber Maal')
for n, alt in [('01', 'Curly textured crop with a taper'), ('03', 'Curly fringe with a low taper'), ('04', 'Waves with a line-up and beard'),
               ('05', 'Curly crop with a burst fade'), ('08', 'Curly fringe with a mid taper'), ('10', 'Curly top with a low fade'),
               ('12', 'Textured crop'), ('16', 'Curly high top with a fade and beard'), ('17', 'Curly crop with a taper'),
               ('20', 'Curly top with a fade and beard'), ('23', 'Textured modern cut with a taper'), ('32', 'Curly modern mullet'),
               ('39', 'Wavy fringe with a taper')]:
    g(f'ryan-{n}', 'ryan', 'barber', f'{alt} by Ryan In The Cut')
for n, alt, cat in [('02', 'Fresh taper with a silver beard', 'barber'), ('03', 'Afro with a sharp beard line-up', 'barber'),
                    ('05', 'Curly top with a fade', 'barber'), ('07', 'Textured fringe', 'barber'), ('09', 'Low fade with a full beard', 'barber'),
                    ('10', 'Waves with a sharp beard line-up', 'barber'), ('15', 'Top knot with a skin fade', 'barber'),
                    ('17', 'Locs with a clean taper', 'barber'), ('18', 'Twists with a taper', 'barber'), ('21', 'Kids cut with a part design', 'kids'),
                    ('32', 'Kids fade', 'kids'), ('34', 'Platinum women’s cut with designs', 'barber'), ('42', 'Twists with a taper', 'barber'),
                    ('46', 'Kids top knot with a design', 'kids'), ('47', 'Kids top knot with a fade', 'kids'), ('48', 'Curly top with a taper', 'barber'),
                    ('53', 'Kids fringe with a skin fade', 'kids'), ('56', 'Curly afro with a taper', 'barber'), ('58', 'Afro with a beard fade', 'barber')]:
    g(f'adonis-{n}', 'adonis', cat, f'{alt} by Adonis Tha Barber')
for n, alt in [('03', 'Sleek wig install'), ('04', 'Red straight wig install'), ('05', 'Stitch braids with a heart design'),
               ('06', 'Feed-in braids'), ('07', 'Stitch braids'), ('08', 'Body-wave wig install'), ('11', 'Long straight wig install'),
               ('12', 'Deep-wave wig install'), ('13', 'Men’s stitch braids'), ('14', 'Boho knotless braids'), ('15', 'Fulani braids'),
               ('17', 'Men’s braids with a design'), ('18', 'Sleek ginger ponytail'), ('19', 'Honey-blonde wig install'),
               ('21', 'Side-part wig install'), ('22', 'Long red stitch braids')]:
    g(f'samaya-{n}', 'samaya', 'beauty', f'{alt} by Hair by Samaya')
for src, alt in [('ig-04', 'Pink body-wave wig install'), ('ig-09', 'Orange wig with a braided halo'), ('ig-28', 'Red wig install'),
                 ('ig-35', 'Sleek pigtails with bows'), ('ig-37', 'Deep-wave wig with a side part'), ('ig-39', 'Long knotless braids'),
                 ('ig-40', 'Boho Fulani braids'), ('ig-44', 'Boho knotless braids'), ('ig-20', 'Crimped wig install'), ('ig-24', 'Honey-blonde wig install')]:
    g(src, 'samaya', 'beauty', f'{alt} at Premier Barber & Beauty')
for n, alt in [('03', 'Curly top with a bald fade'), ('04', 'Top knot with a skin fade')]:
    g(f'saint-{n}', 'saint', 'barber', f'{alt} by Blessed By Saint')
for n, alt in [('05', 'Beard line-up and fade'), ('07', 'High-top fade with a razor part'), ('12', 'Fade with beard'),
               ('17', 'Braids with a sharp line-up'), ('20', 'Waves with a part design'), ('23', 'Kids cut with a freehand design')]:
    g(f'darnell-{n}', 'darnell', 'kids' if n == '23' else 'barber', f'{alt} by OG Barber Darnell')

# de-dup
seen = set(); GALLERY = []
for x in G:
    if x[0] in seen: continue
    seen.add(x[0]); GALLERY.append(x)


def load(src):
    im = Image.open(f'{RAW}/pbb-{src}.jpg')
    im = ImageOps.exif_transpose(im).convert('RGB')
    return im


def process(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    manifest = {}

    def save(key, im, maxw, alt, widths=(480, 960, 1600, 2200)):
        W, H = im.size
        ws = sorted(set([w for w in widths if w < min(W, maxw)] + [min(W, maxw)]))
        files = []
        for w in ws:
            h = round(H * w / W)
            fn = f'{key}-{w}.webp'
            im.resize((w, h), Image.LANCZOS).save(f'{out_dir}/{fn}', 'WEBP', quality=80, method=6)
            files.append((fn, w))
        manifest[key] = {'files': files, 'w': ws[-1], 'h': round(H * ws[-1] / W), 'alt': alt}

    for key, (src, crop, alt, maxw) in KEY.items():
        im = load(src)
        if crop:
            W, H = im.size
            im = im.crop((int(crop[0] * W), int(crop[1] * H), int(crop[2] * W), int(crop[3] * H)))
        save(key, im, maxw, alt)
    for i, (src, pro, cat, alt) in enumerate(GALLERY):
        im = load(src)
        save(f'g-{src}', im, 1200, alt, widths=(400, 800, 1200))
        manifest[f'g-{src}'].update({'pro': pro, 'cat': cat})
    json.dump(manifest, open(f'{out_dir}/../manifest.json', 'w'), indent=0)
    return manifest


if __name__ == '__main__':
    import sys
    m = process(sys.argv[1])
    print(len(m), 'images')

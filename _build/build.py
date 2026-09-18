"""Static site generator for Premier Barber & Beauty.
python3 build.py  -> renders every page into ../dist (images must already be processed via images.py)."""
import json, os, re, sys, datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
from images import GALLERY as GALLERY_SRC

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.abspath(os.path.join(HERE, '..'))  # repo root is the publish dir
M = json.load(open(os.path.join(DIST, 'assets', 'manifest.json')))
V = datetime.datetime.now().strftime('%Y%m%d%H%M')
UPDATED = 'September 2026'
S = data.SITE
DOMAIN = S['domain'].rstrip('/')
# Link previews (iMessage, SMS, social) must load og:image from a live host. Netlify sets URL
# on deploy; until premierbarberbeauty.com is live, fall back to the Netlify site URL.
SHARE_BASE = (
    os.environ.get('URL', '').rstrip('/')
    or os.environ.get('DEPLOY_PRIME_URL', '').rstrip('/')
    or 'https://premier-barber-beauty-website.netlify.app'
)

env = Environment(loader=FileSystemLoader(os.path.join(HERE, 'templates')), autoescape=select_autoescape(['html']), trim_blocks=True, lstrip_blocks=True)


def fmt(t):
    h, m = map(int, t.split(':'))
    ap = 'PM' if h >= 12 else 'AM'
    h = h % 12 or 12
    return f'{h}:{m:02d} {ap}' if m else f'{h} {ap}'


def money(n):
    return f'${n:.2f}' if n % 1 else f'${int(n)}'


# ------------------------------------------------------------------ enrich team
AVATAR = {'maal': 'maal-portrait', 'darnell': 'darnell-portrait', 'ryan': 'ryan-portrait',
          'samaya': 'samaya-logo', 'adonis': 'adonis-portrait', 'saint': 'saint-logo'}
PRO_HOURS = {  # only pros whose platform publishes a full week
    'darnell': [('Sunday', '10:00', '16:00'), ('Monday', None, None), ('Tuesday', None, None), ('Wednesday', '14:00', '18:00'),
                ('Thursday', '09:00', '18:00'), ('Friday', '09:00', '18:00'), ('Saturday', '10:00', '17:00')],
}
TEAM = []
for p in data.TEAM:
    p = dict(p)
    p['avatar_key'] = AVATAR[p['slug']]
    menu2 = []
    for title, items in p['menu']:
        its = []
        for name, price, dur, desc in items:
            plus = 'starts here' in desc
            d = desc.replace(' Price starts here.', '').replace('Price starts here.', '').strip()
            its.append({'name': name, 'price': price, 'dur': dur, 'desc': d, 'plus': plus})
        menu2.append({'title': title, 'items': its})
    p['menu2'] = menu2
    allitems = [i for g in menu2 for i in g['items']]
    adult = [i['price'] for g in menu2 for i in g['items']
             if not re.search(r'kid|teen|pre-teen|senior|line|beard|brow|shampoo|towel|enhancement|mobile|after|shave', i['name'] + ' ' + g['title'], re.I)]
    p['from_price'] = money(min(adult)) if p['kind'] == 'barber' and adult else '—'
    p['kids'] = any(re.search(r'kid|pre-teen|teen', g['title'] + ' ' + i['name'], re.I) for g in menu2 for i in g['items'])
    TEAM.append(p)
PRO = {p['slug']: p for p in TEAM}
TOTAL_REVIEWS = data.TOTAL_REVIEWS
AVG = data.AVG_RATING
AVG_RATING_1 = int(AVG * 10) / 10  # floor to one decimal so we never overstate (4.97 -> 4.9)

# ------------------------------------------------------------------ derived price facts (computed, not typed)
def price_of(slug, name):
    for g in PRO[slug]['menu2']:
        for i in g['items']:
            if i['name'] == name:
                return i['price']
    raise KeyError((slug, name))

adult_cut_prices = [price_of(*x) for x in [('darnell', 'All Even Cut & Baldhead'), ('darnell', 'Fade, Taper & Afro'), ('ryan', 'Full Cut'),
                                          ('maal', 'All Even Haircut'), ('maal', 'Fade / Taper Haircut'), ('maal', 'Skin Fade Haircut'),
                                          ('adonis', 'Haircut & Beard'), ('saint', 'Haircut (16+)'), ('adonis', 'Women’s Haircut')]]
ADULT_RANGE = f'{money(min(adult_cut_prices))}–{money(max(adult_cut_prices))}'
KIDS_FROM = money(min(i['price'] for p in TEAM for g in p['menu2'] for i in g['items']
                     if re.search(r'kid', g['title'] + ' ' + i['name'], re.I) and not re.search(r'line', i['name'], re.I)))
assert KIDS_FROM == '$20', KIDS_FROM
braid_prices = [i['price'] for g in PRO['samaya']['menu2'] if g['title'] in ('Knotless Braids', 'Fulani / Tribal', 'Stitch Braids') for i in g['items']]
BRAIDS_FROM = money(min(braid_prices))
assert ADULT_RANGE == '$30–$52.50', ADULT_RANGE

TEASER = [
    {'kicker': 'Barbershop', 'title': 'Barber', 'anchor': 'haircuts', 'img': 'g-adonis-10', 'items': [
        ('Fade / taper haircut', f"{money(price_of('darnell','Fade, Taper & Afro'))}–{money(price_of('maal','Fade / Taper Haircut'))}", 'Darnell · Maal'),
        ('Skin fade', money(price_of('maal', 'Skin Fade Haircut')), 'Maal · razor finish & style'),
        ('Full cut + beard', f"{money(price_of('ryan','Full Cut + Beard'))}–{money(price_of('adonis','Haircut & Beard'))}", 'Ryan · Adonis · Darnell'),
        ('Haircut, beard included', money(price_of('saint', 'Haircut (16+)')), 'Saint · tailored to you'),
        ('Hot towel face shave', money(price_of('maal', 'Hot Towel Face Shave')), 'Maal · lather, razor, massage'),
        ('Kids cuts', f"from {KIDS_FROM}", 'All five barbers · ages 2 and up'),
    ]},
    {'kicker': 'Beauty bar', 'title': 'Beauty', 'anchor': 'braids', 'img': 'g-samaya-22', 'items': [
        ('Knotless braids', f"from {money(price_of('samaya','Jumbo Knotless'))}", 'Samaya · jumbo to smedium'),
        ('Fulani / tribal braids', f"from {money(price_of('samaya','Large Fulani / Tribal Braids'))}", 'Samaya'),
        ('Stitch braids', f"from {money(price_of('samaya','Large Straight-Back Stitch Braids'))}", 'Samaya · freestyle or straight-back'),
        ('Wig install & customization', f"from {money(price_of('samaya','Wig Install / Styling'))}", 'Samaya · knots, plucking, color'),
        ('Silk press', money(price_of('samaya', 'Silk Press')), 'Samaya · wash, blowout & silk'),
        ('Loc retwist', f"from {money(price_of('samaya','Loc Retwist'))}", 'Samaya · starter locs available'),
    ]},
]
# sanity: the "full cut + beard" range must include Darnell's facial-hair price
assert price_of('ryan', 'Full Cut + Beard') <= price_of('darnell', 'Fades, Tapers & Afros with Facial Hair') <= price_of('adonis', 'Haircut & Beard')

# ------------------------------------------------------------------ services categories
CATMAP = {
    ('maal', 'Adult Haircuts'): 'haircuts', ('maal', 'Teens (11–17)'): 'kids', ('maal', 'Kids (10 & under)'): 'kids',
    ('maal', 'Shaves & Beard'): 'beard', ('maal', 'Extras'): 'extras',
    ('darnell', 'Adults (13+)'): 'haircuts', ('darnell', 'Pre-Teens (6–12)'): 'kids', ('darnell', 'Kids (2–5)'): 'kids',
    ('ryan', 'Cuts'): 'haircuts', ('ryan', 'Line-Ups & Beard'): 'beard',
    ('samaya', 'Knotless Braids'): 'braids', ('samaya', 'Fulani / Tribal'): 'braids', ('samaya', 'Stitch Braids'): 'braids',
    ('samaya', 'Wigs & Weaves'): 'wigs', ('samaya', 'Styling & Locs'): 'styling',
    ('adonis', 'Cuts'): 'haircuts', ('adonis', 'Kids'): 'kids', ('adonis', 'Line-Ups & Add-Ons'): 'beard',
    ('saint', 'Cuts'): 'haircuts',
}
CATS = [
    {'id': 'haircuts', 'title': 'Haircuts', 'kicker': 'Barbershop', 'blurb': 'Fades, tapers, scissor cuts, afros, textured crops and women’s cuts from five barbers.'},
    {'id': 'kids', 'title': 'Kids & teens', 'kicker': 'Barbershop', 'blurb': 'Patient hands for first haircuts through high school, priced by age.'},
    {'id': 'beard', 'title': 'Line-ups, beard & shaves', 'kicker': 'Barbershop', 'blurb': 'Razor line-ups, beard sculpting, hot-towel shaves and hairline enhancements.'},
    {'id': 'braids', 'title': 'Braids', 'kicker': 'Beauty', 'blurb': 'Knotless, Fulani and stitch braids in every size. Bring your own braiding hair.'},
    {'id': 'wigs', 'title': 'Wigs & weaves', 'kicker': 'Beauty', 'blurb': 'Custom wig installs, touch-ups, quick weaves, frontal ponytails and crochet.'},
    {'id': 'styling', 'title': 'Silk press, styling & locs', 'kicker': 'Beauty', 'blurb': 'Silk presses, sleek styles, loc retwists, starter locs and shape-ups.'},
    {'id': 'extras', 'title': 'Extras & after-hours', 'kicker': 'Specialty', 'blurb': 'Straight-razor brows, shampoo, and mobile or after-hours cuts by appointment.'},
]
for c in CATS:
    c['blocks'] = []
for p in TEAM:
    for g in p['menu2']:
        cid = CATMAP[(p['slug'], g['title'])]
        cat = next(c for c in CATS if c['id'] == cid)
        blk = next((b for b in cat['blocks'] if b['pro']['slug'] == p['slug']), None)
        if not blk:
            blk = {'pro': p, 'items': []}; cat['blocks'].append(blk)
        for it in g['items']:
            it2 = dict(it)
            if cid == 'kids' and not re.search(r'kid|teen', it['name'], re.I):
                it2['name'] = f"{it['name']} · {g['title']}"
            blk['items'].append(it2)
assert all(c['blocks'] for c in CATS)
assert sum(len(b['items']) for c in CATS for b in c['blocks']) == sum(len(g['items']) for p in TEAM for g in p['menu2'])

# ------------------------------------------------------------------ gallery + strips + quotes
GALLERY = [f'g-{src}' for src, *_ in GALLERY_SRC]
# interleave pros so no one pro dominates a row
by_pro = {}
for k in GALLERY:
    by_pro.setdefault(M[k]['pro'], []).append(k)
order = []
while any(by_pro.values()):
    for slug in ['maal', 'samaya', 'adonis', 'ryan', 'darnell', 'saint']:
        if by_pro.get(slug):
            order.append(by_pro[slug].pop(0))
GALLERY = order
hi = [k for k in GALLERY if M[k]['w'] >= 700]
STRIPS = [hi[0:12], hi[12:24]]

QUOTES = []
for slug, idx in [('maal', 0), ('samaya', 0), ('darnell', 0), ('adonis', 0), ('saint', 0), ('samaya', 1), ('darnell', 1), ('maal', 1), ('ryan', 0)]:
    who, text = PRO[slug]['quotes'][idx]
    QUOTES.append({'who': who, 'text': text, 'slug': slug, 'first': PRO[slug]['first']})

# ------------------------------------------------------------------ JSON-LD
hours_spec = [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': d, 'opens': o, 'closes': c} for d, o, c in S['hours'] if o]
BUSINESS = {
    '@context': 'https://schema.org', '@type': ['BarberShop', 'HairSalon'], '@id': DOMAIN + '/#business',
    'name': S['name'], 'alternateName': 'Premier Barber & Beauty', 'url': DOMAIN + '/',
    'telephone': '+1-804-332-7091', 'priceRange': '$$',
    'image': [DOMAIN + '/assets/brand/og-image.jpg'], 'logo': DOMAIN + '/assets/brand/premier-badge-1200.png',
    'description': 'Barbershop and beauty salon in Midlothian, VA with six independent pros: fades, tapers, hot-towel shaves, kids cuts, knotless and stitch braids, wig installs and silk presses.',
    'address': {'@type': 'PostalAddress', 'streetAddress': S['street'], 'addressLocality': S['city'], 'addressRegion': S['region'], 'postalCode': S['zip'], 'addressCountry': 'US'},
    'geo': {'@type': 'GeoCoordinates', 'latitude': S['geo'][0], 'longitude': S['geo'][1]},
    'areaServed': ['Midlothian, VA', 'Chesterfield, VA', 'Richmond, VA'],
    'openingHoursSpecification': hours_spec,
    'sameAs': [S['instagram'], S['facebook']],
    'paymentAccepted': 'Credit card',
    'amenityFeature': [{'@type': 'LocationFeatureSpecification', 'name': n, 'value': True} for n in ['Parking', 'Wi-Fi', 'Wheelchair accessible', 'Child friendly']],
    'employee': [{'@type': 'Person', 'name': p['name'], 'jobTitle': p['role'].split(' · ')[0], 'url': f"{DOMAIN}/team/{p['slug']}"} for p in TEAM],
}
FAQ_LD = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in data.FAQ]}


def crumbs(*items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': DOMAIN + u} for i, (n, u) in enumerate(items)]}


def ld(o):
    return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')


NAV = [('team.html', 'Team', 'team'), ('services.html', 'Services', 'services'), ('gallery.html', 'Gallery', 'gallery'),
       ('about.html', 'About', 'about'), ('contact.html', 'Contact', 'contact')]

BOOKING = {
    'sms': S['sms_href'],
    'shopHours': S['hours'],
    'team': [{'slug': p['slug'], 'name': p['name'], 'first': p['first'], 'role': p['role'], 'platform': p['platform'], 'book_url': p['book_url'],
              'rating': p['rating'], 'reviews': p['reviews'],
              'img': 'assets/img/' + next(f for f, w in M[p['card']]['files'] if w >= 480),
              'hours': PRO_HOURS.get(p['slug']),
              'menu': [{'title': g['title'], 'items': [{'name': i['name'], 'price': i['price'], 'dur': i['dur'], 'plus': i['plus']} for i in g['items']]} for g in p['menu2']]}
             for p in TEAM],
}

COMMON = dict(S=S, TEAM=TEAM, PRO=PRO, M=M, V=V, NAV=NAV, fmt=fmt, money=money, TOTAL_REVIEWS=TOTAL_REVIEWS, AVG_RATING_1=AVG_RATING_1,
              FAQ=data.FAQ, hours_json=json.dumps(S['hours']), UPDATED=UPDATED,
              share_base=SHARE_BASE, og_default=f'{SHARE_BASE}/assets/brand/og-image.jpg')

PAGES = []


def render(tpl, out, **ctx):
    depth = out.count('/')
    R = '../' * depth
    # og:url should match the host people share (Netlify now, custom domain later).
    if 'canonical' in ctx and 'share_page' not in ctx:
        ctx['share_page'] = ctx['canonical'].replace(DOMAIN, SHARE_BASE, 1)
    html = env.get_template(tpl).render(R=R, **COMMON, **ctx)
    html = re.sub(r'\n\s*\n+', '\n', html)
    path = os.path.join(DIST, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(html)
    PAGES.append((out, ctx.get('priority', 0.7)))


def canon(path):
    return DOMAIN + path


hero_pre = next(f for f, w in M['hero']['files'] if w >= 1600)
render('index.html', 'index.html', page='home', priority=1.0,
       title='Premier Barber & Beauty | Barbershop & Salon in Midlothian, VA',
       og_title='Premier Barber & Beauty Salon: Sharp lines. Soft glam.',
       description=f'Midlothian barbershop & beauty salon on Hull St Rd: fades, tapers, shaves, kids cuts, braids & wig installs. {AVG_RATING_1}★ from {TOTAL_REVIEWS} reviews. Book online.',
       canonical=canon('/'),
       # Hero photo for share cards (JPEG og-image.jpg on inner pages; home uses hero).
       og_image=f'{SHARE_BASE}/assets/img/{hero_pre}',
       og_image_type='image/webp', og_image_width='1600', og_image_height='900',
       # Uncomment next 3 lines and remove og_image* above to use the logo card (1200×630 JPG) instead:
       # og_image=f'{SHARE_BASE}/assets/brand/og-image.jpg',
       # og_image_type=None, og_image_width='1200', og_image_height='630',
       preload_img=hero_pre, jsonld=[ld(BUSINESS), ld(FAQ_LD)],
       TEASER=TEASER, STRIPS=STRIPS, QUOTES=QUOTES)
render('team.html', 'team.html', page='team', priority=0.9,
       title='Meet the Barbers & Stylists | Premier Barber & Beauty',
       description='Meet the six pros at Premier Barber & Beauty in Midlothian, VA: barbers Maal, Darnell, Ryan, Adonis and Saint, plus braid & wig specialist Samaya.',
       canonical=canon('/team'), jsonld=[ld(crumbs(('Home', '/'), ('Team', '/team')))])
for p in TEAM:
    work = [k for k in GALLERY if M[k]['pro'] == p['slug']]
    person = {'@context': 'https://schema.org', '@type': 'Person', 'name': p['name'], 'jobTitle': p['role'].split(' · ')[0],
              'worksFor': {'@id': DOMAIN + '/#business'}, 'url': f"{DOMAIN}/team/{p['slug']}", 'sameAs': [p['instagram'], p['profile_url']],
              'image': f"{DOMAIN}/assets/img/{M[p['card']]['files'][-1][0]}",
              'makesOffer': [{'@type': 'Offer', 'name': i['name'], 'price': i['price'], 'priceCurrency': 'USD'} for g in p['menu2'] for i in g['items']]}
    render('pro.html', f"team/{p['slug']}.html", page='team', p=p, work=work, priority=0.8,
           title=f"{p['name']} | {'Braids & Wigs' if p['kind']=='beauty' else 'Barber'} in Midlothian, VA | Premier",
           description=f"{p['name']} at Premier Barber & Beauty in Midlothian, VA. {p['rating']:.1f}★ from {p['reviews']} {p['platform']} reviews. See the full menu, prices and photos, then book online.",
           canonical=canon(f"/team/{p['slug']}"), preload_img=None,
           jsonld=[ld(person), ld(crumbs(('Home', '/'), ('Team', '/team'), (p['name'], f"/team/{p['slug']}")))])
render('services.html', 'services.html', page='services', priority=0.9, CATS=CATS, ADULT_RANGE=ADULT_RANGE, KIDS_FROM=KIDS_FROM, BRAIDS_FROM=BRAIDS_FROM,
       title='Services & Prices: Haircuts, Braids & Wigs | Premier',
       description=f'Full price list for Premier Barber & Beauty in Midlothian, VA. Adult cuts {ADULT_RANGE}, kids from {KIDS_FROM}, braids from {BRAIDS_FROM}, wig installs, silk press and more.',
       canonical=canon('/services'), jsonld=[ld(crumbs(('Home', '/'), ('Services', '/services')))])
render('gallery.html', 'gallery.html', page='gallery', priority=0.7, GALLERY=GALLERY,
       title='Gallery | Fades, Braids & Wig Installs | Premier Barber & Beauty',
       description=f'{len(GALLERY)} real fades, tapers, designs, braids and wig installs from the pros at Premier Barber & Beauty in Midlothian, VA. Tap a look and book that pro.',
       canonical=canon('/gallery'), jsonld=[ld(crumbs(('Home', '/'), ('Gallery', '/gallery')))])
render('book.html', 'book.html', page='book', priority=0.9, booking_json=json.dumps(BOOKING, ensure_ascii=False).replace('</', '<\\/'),
       title='Book an Appointment | Premier Barber & Beauty, Midlothian VA',
       description='Book your barber or stylist at Premier Barber & Beauty in Midlothian, VA. Pick your pro, service and time, then confirm on Booksy, StyleSeat or theCut.',
       canonical=canon('/book'), jsonld=[ld(crumbs(('Home', '/'), ('Book', '/book')))])
render('about.html', 'about.html', page='about', priority=0.6,
       title='About Premier Barber & Beauty Salon | Midlothian, VA',
       description='Premier Barber & Beauty Salon brings master barbers and beauty pros together on Hull Street Road in Midlothian, VA. Learn about the shop and join the team.',
       canonical=canon('/about'), jsonld=[ld(crumbs(('Home', '/'), ('About', '/about')))])
render('contact.html', 'contact.html', page='contact', priority=0.8,
       title='Contact & Directions | Premier Barber & Beauty, 11800 Hull St Rd',
       description='Visit Premier Barber & Beauty at 11800-G Hull Street Road, Midlothian VA 23112. Call or text (804) 332-7091. Hours, map and contact form.',
       canonical=canon('/contact'), jsonld=[ld(BUSINESS), ld(crumbs(('Home', '/'), ('Contact', '/contact')))])
render('simple.html', 'thanks.html', page='thanks', priority=0,
       title='Message sent | Premier Barber & Beauty', description='Thanks for reaching out to Premier Barber & Beauty.',
       canonical=canon('/thanks'), jsonld=[], big='Message <span class="em">sent.</span>',
       copy='Thanks for reaching out. The shop will get back to you soon. Need a chair sooner? Book online in about a minute.')
render('simple.html', '404.html', page='404', priority=0,
       title='Page not found | Premier Barber & Beauty', description='That page moved or never existed.',
       canonical=canon('/404'), jsonld=[], big='Missed <span class="em">the</span> line.',
       copy='That page moved or never existed. Let’s get you back in the chair.')

# ------------------------------------------------------------------ sitemap / robots / manifest
today = datetime.date.today().isoformat()
urls = []
for out, pr in PAGES:
    if pr == 0:
        continue
    path = '/' if out == 'index.html' else '/' + out[:-5]
    urls.append(f'  <url><loc>{DOMAIN}{path}</loc><lastmod>{today}</lastmod><priority>{pr:.1f}</priority></url>')
open(os.path.join(DIST, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
open(os.path.join(DIST, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /thanks\n\nSitemap: {DOMAIN}/sitemap.xml\n')
json.dump({'name': S['name'], 'short_name': 'Premier', 'start_url': '/', 'display': 'standalone', 'background_color': '#05060b', 'theme_color': '#05060b',
           'icons': [{'src': '/assets/brand/icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': '/assets/brand/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]},
          open(os.path.join(DIST, 'site.webmanifest'), 'w'), indent=2)
print('built', len(PAGES), 'pages ·', 'reviews', TOTAL_REVIEWS, 'avg', AVG, '->', AVG_RATING_1, '· adult', ADULT_RANGE, 'kids', KIDS_FROM, 'braids', BRAIDS_FROM)

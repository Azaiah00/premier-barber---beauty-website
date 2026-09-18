# Premier Barber & Beauty Salon: website

The website for **Premier Barber & Beauty Salon**, 11800-G Hull Street Road, Midlothian, VA 23112 · (804) 332-7091.
Built by Real Estate Advancement / Couture House Co.

It's a static site: plain HTML, CSS and JS with no framework and no build step on deploy.

## Deploy (Netlify)
1. Push this folder to GitHub (repo root = this folder).
2. In Netlify, choose **Add new site → Import from Git** and pick the repo.
3. Leave the **Build command empty** and set the **Publish directory** to `.`.
4. Deploy. `netlify.toml` already handles caching, security headers, old Squarespace redirects, and blocking `/_build`.
5. Point **premierbarberbeauty.com** at Netlify (Domain settings → add custom domain) and turn on HTTPS.
6. The contact form on `/contact` uses **Netlify Forms** automatically. Submissions show up under Site → Forms, and you can add email notifications there.

## Pages
| Page | File |
|---|---|
| Home | `index.html` |
| Team + comparison table | `team.html` |
| Pro pages (6) | `team/maal.html`, `darnell`, `ryan`, `samaya`, `adonis`, `saint` |
| Services & prices (every item, by category) | `services.html` |
| Gallery (filters + lightbox) | `gallery.html` |
| Booking concierge (pro → service → time → hand-off) | `book.html` |
| About / join the team | `about.html` |
| Contact (Netlify form, map, hours) | `contact.html` |
| Form thank-you / 404 | `thanks.html`, `404.html` |

## Booking
Every "Book" button deep-links to that pro's **real** calendar:

| Pro | Platform | Link |
|---|---|---|
| Master Barber Maal | Booksy | https://link.booksy.com/MaalTheBarber |
| OG Barber Darnell | StyleSeat | https://www.styleseat.com/m/v/DarnellDaBarber |
| Ryan In The Cut | theCut | https://book.thecut.co/ryan_inthecut |
| Hair by Samaya | Booksy | https://hairbysamaya.booksy.com/a/ |
| Adonis Tha Barber | theCut | https://book.thecut.co/loso |
| Blessed By Saint | Booksy | https://blessedbysaint.booksy.com |

`book.html` is a guided concierge. The visitor picks a pro, service and preferred time, and then gets handed to the pro's live calendar with their details ready to copy or text. It never claims a slot is reserved.
Deep link to a specific pro: `book.html?pro=maal`

## Editing content
All content (prices, bios, reviews, hours, FAQ) lives in **`_build/data.py`**. To change it:
```bash
pip install jinja2
python3 _build/build.py      # re-renders every .html page in the repo root
```
Templates are in `_build/templates/`. Styles are in `assets/css/site.css`, and behavior is in `assets/js/site.js` and `assets/js/book.js`.

To add new photos, put originals named `pbb-<pro>-NN.jpg` in `_build/raw/`, add them to `_build/images.py`, then run `python3 _build/images.py assets/img`. This generates responsive WebP files at 400–2200 px.

## Brand assets (`assets/brand/`)
- `premier-badge.svg` / `premier-badge-ondark.svg`: vector remaster of the shop badge (transparent background, sharp at any size)
- `premier-badge-2400.png`, `-1200.png`: transparent PNG exports for print and social
- `premier-badge-original-cleaned.png`: the original logo with its background removed
- `premier-wordmark-white.svg` / `-black.svg`: horizontal wordmark
- `premier-monogram.svg`, `icon-*.png`, `/favicon.ico`, `/apple-touch-icon.png`: app and browser icons
- `og-image.jpg`: 1200×630 social share image

The logo source files are in `_build/logo/` (`build_logo.py`, `build_marks.py`).

## Tech notes
- Fonts are self-hosted: Anton, Inter, Playfair Display Italic, Alfa Slab One (all OFL).
- Motion uses GSAP 3 + ScrollTrigger (free Standard License) and Lenis smooth scroll, all self-hosted in `assets/vendor/`. `prefers-reduced-motion` is fully respected.
- SEO: unique titles and descriptions, canonical URLs, Open Graph, `BarberShop`/`HairSalon` LocalBusiness + FAQPage + Person + Breadcrumb JSON-LD, `sitemap.xml`, `robots.txt`.
- Images: responsive WebP `srcset`, lazy-loaded below the fold, and the hero image is preloaded.

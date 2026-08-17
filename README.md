# Carpenter Engineering, Inc. — portfolio site

A single-page portfolio of civil engineering work by Bob Carpenter, PE, founder
of Carpenter Engineering, Inc. (Vancouver, WA). Published with GitHub Pages at
<https://troycarp.github.io/>.

This is a GitHub Pages *user site*, which means the repo name must stay exactly
`troycarp.github.io` — matching the account name. If the account is ever renamed
again, rename this repo to match, or Pages silently demotes it to a project site
served from a `/repo-name/` subpath instead of the root domain. The absolute URLs
in the `<head>` of `index.html` (canonical, `og:url`, `og:image`, JSON-LD `url`)
would need updating too; every other path in the site is relative and is
subpath-safe either way.

Static HTML, CSS, and vanilla JavaScript — no build step to deploy, no
framework, no dependencies. Push to `master` and Pages serves it.

## Layout

```
index.html              the whole page
assets/css/site.css     all styling
assets/js/projects.js   project copy + gallery image lists (edit this to change text)
assets/js/site.js       header, mobile nav, filters, lightbox
assets/img/             web-sized WebP, generated from originals/
assets/brand/           transparent logos and favicons, generated from originals/
originals/              camera files and vendor logo art — source only, never referenced
tools/                  regeneration scripts
```

## Adding or changing a project

1. Put the photos in `originals/`.
2. Add a slug and its source files to `GALLERIES` in `tools/build_images.py`.
3. Run `python3 tools/build_images.py` from the repo root.
4. Add a card to the `work-grid` in `index.html` (copy an existing `<article
   class="project">` and change `data-project`, `data-cats`, the image, and the
   text).
5. Add the matching detail entry to `assets/js/projects.js`.

`data-cats` drives the filter buttons; the counts on those buttons are computed
at runtime, so they update themselves. Valid values: `land`, `public`,
`industrial`, `utility`, `water`.

## Regenerating assets

Needs `cwebp` (`brew install webp`), macOS `sips`, and Pillow
(`pip install Pillow`).

```sh
python3 tools/build_images.py   # project photos, hero, portrait, plan sheet
python3 tools/build_logos.py    # transparent PNG logos from the brand TIFs
python3 tools/build_meta.py     # favicons and the social share card
```

Run `build_logos.py` before `build_meta.py` — the share card and favicons are
composited from the logos it produces.

## Local preview

```sh
python3 -m http.server 8000
```

then open <http://localhost:8000>. Opening `index.html` as a `file://` URL works
too, but the fonts load over the network either way.

## Notes

- The plan sheet shown in the "Deliverables" section is cropped to the drawing
  area on purpose — the full sheet's title block carries the office address and
  email address, which are deliberately not published on this site.
- Contact is phone only, by choice. Add an email in the contact section of
  `index.html` and in the `ProfessionalService` JSON-LD block if that changes.
- The site commits to a single light theme; there is no dark mode.

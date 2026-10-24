# Die Line Maker

A free, browser-based die cut line tool for CorelDraw users. Upload a sticker or label image and download a print-ready PDF with the artwork and a **CutContour** spot colour cut line on separate layers, plus SVG, EPS, DXF and PNG. Everything runs in the visitor's browser: images are never uploaded.

The site also has 14 tutorials and guides for CorelDraw and Photoshop.

## Folders

| Folder | What's in it |
|---|---|
| `site/` | The website. This is the folder you deploy. See [site/README.md](site/README.md). |
| `content/blog/` | Article sources. Edit these, then run the builder. |
| `tools/` | `build_blog.py` builds the blog, legal pages, sitemap and SEO tags. `serve.py` is a local preview server. |
| `tests/` | Die detection test suite (18 cases) and the share image generator. |
| `site.config.json` | Domain, contact email, WhatsApp number and analytics token. |

## Deploy

The site is static, so there is no build step on the host. Connect this repository to **Cloudflare Pages** or **Netlify** and set:

- Build command: *(leave empty)*
- Output / publish directory: `site`

## Work on it locally

```bash
python3 tools/build_blog.py
```

```bash
python3 tools/serve.py 8090 site
```

Then open http://127.0.0.1:8090. To run the tests, serve the project folder (`python3 tools/serve.py 8091 .`) and open http://127.0.0.1:8091/tests/.

## Licence notes

General Sans by Indian Type Foundry is loaded from Fontshare under the ITF Free Font License. Its licence forbids redistributing the font files, so they are not in this repository. CorelDraw, Photoshop, Roland and VersaWorks are trademarks of their owners; this project isn't affiliated with them.

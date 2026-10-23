# Die Line Maker: website

A static website with no server code, database or build step needed to host it. All image tracing and file generation happen in the visitor's browser.

```
site/
  index.html            landing page (how it works, CorelDraw guide, FAQ)
  editor.html           the tool: a full-screen editor (open with ?sample to start on the sample sticker)
  privacy.html          privacy policy (generated)
  terms.html            terms of use (generated)
  404.html, robots.txt  generated
  assets/site.css       shared styles (design tokens, header, footer, articles)
  assets/fonts/         Uncut Sans (SIL Open Font License, see OFL-LICENSE.txt)
  assets/site.js        shared behaviour (mobile menu, theme toggle, guides search and filters,
                        copy buttons, back to top, reading progress)
  blog/index.html       guides & blog listing
  blog/*.html           articles
```

## Put it on your own domain

Upload the whole `site` folder. Pick one:

- **Netlify (easiest, free):** go to https://app.netlify.com/drop and drag this `site` folder onto the page. You get a live link straight away. You can add your own domain under *Domain settings*.
- **Cloudflare Pages (free):** go to the Cloudflare dashboard, then *Workers & Pages → Create → Pages → Upload assets*, and upload this folder.
- **GitHub Pages (free):** push this folder to a repository, then turn on *Settings → Pages*.
- **Existing hosting (cPanel, Hostinger, etc.):** upload the folder's contents to `public_html/` (or a subfolder such as `public_html/die-line-maker/`).
- **Shopify store:** Shopify pages can't run this script directly. Host the folder using one of the options above, then link to it or embed it with:
  ```html
  <iframe src="https://YOUR-HOSTED-URL/" style="width:100%;height:1400px;border:0" title="Die Line Maker"></iframe>
  ```

## Writing or editing articles

Articles are written in `../content/blog/*.html`, outside this folder so the sources aren't uploaded. Each file starts with a `<!--meta {...} -->` block (title, description, summary, related posts, sources).

After adding or editing an article, rebuild the blog pages:

```bash
python3 tools/build_blog.py
```

Run it from the project folder (the one that contains `site/`, `content/` and `tools/`). New articles also need their slug added to `ORDER` in `tools/build_blog.py` so they appear on the blog index.

## Going live checklist

1. Fill in `site.config.json` (project folder):
   - `site_url`: your live address, for example `"https://dielinemaker.com"`.
   - `contact_email`: shown on the privacy and terms pages (they show a placeholder until you set it). Setting it also adds a floating **Contact** button.
   - `whatsapp` (optional): digits with country code, for example `"919812345678"`. The contact button then opens WhatsApp instead of email.
   - `cf_analytics_token` (optional): your Cloudflare Web Analytics token. It's cookie-free, so no cookie banner is needed, and the privacy policy updates itself to mention it. If you ever switch to Google Analytics, you'll need a cookie consent banner and a privacy policy update.
2. Rebuild:
   ```bash
   python3 tools/build_blog.py
   ```
   This adds canonical links, absolute share-image links, breadcrumbs in structured data, `sitemap.xml`, and the sitemap line in `robots.txt`.
3. Upload the `site` folder (see above). `404.html` is picked up automatically by Netlify and Cloudflare Pages.
4. In Google Search Console, add the site and submit `https://YOUR-DOMAIN/sitemap.xml`.
5. Have the privacy policy and terms read by someone who knows Indian law before you rely on them. They describe how the site really works, but they are a template, not legal advice.
6. Share any page link. The preview uses `assets/og.png`; regenerate it with `tests/make-images.html` if the design changes, then shrink it to a 128-colour PNG (the current one is 32 KB).

## Testing die detection

`tests/index.html` runs 18 cases (transparent PNGs, coloured, dark and white backgrounds, thin lines, 40 small pieces, drop shadows, edge cases, photos, tiny and huge images, and two sticker sheets) against the live editor (`site/editor.html`). See `tests/REPORT.md` for the latest results and how to run it.

## Previewing locally

```bash
python3 tools/serve.py 8090 site
```

Then open http://127.0.0.1:8090. This server tells the browser not to cache, so edits show on every reload. The shared CSS and JS links carry a `?v=` version that the builder updates whenever those files change, so visitors also get fresh copies after an update.

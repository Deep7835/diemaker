#!/usr/bin/env python3
"""Build the Die Line Maker blog.

Reads article fragments from content/blog/*.html and writes finished pages to
site/blog/<slug>.html plus site/blog/index.html.

Each fragment starts with a <!--meta {json} --> block, then the intro, a
<!--toc--> marker (table of contents goes there), the <div class="prose"> body,
a <!--cta--> marker (call to action goes there) and an optional FAQ section.

Run from anywhere:  python3 tools/build_blog.py
"""
import hashlib, html, json, math, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8")) if (ROOT / "site.config.json").exists() else {}
SITE_URL = (CONFIG.get("site_url") or "").rstrip("/")      # empty until the site has a domain
SITE_NAME = CONFIG.get("site_name") or "Die Line Maker"
LOCALE = CONFIG.get("locale") or "en_IN"
CF_TOKEN = (CONFIG.get("cf_analytics_token") or "").strip()      # Cloudflare Web Analytics (cookie-free); empty = off
CONTACT_EMAIL = (CONFIG.get("contact_email") or "").strip()
WHATSAPP = re.sub(r"\D", "", CONFIG.get("whatsapp") or "")           # digits with country code, e.g. 919812345678
# cache-busting version for the shared CSS and JS: changes whenever either file changes
ASSET_V = hashlib.sha1(b"".join((ROOT / "site" / "assets" / f).read_bytes() for f in ("site.css", "site.js"))).hexdigest()[:8]
LEGAL_DATE = date(2026, 10, 24)                                      # "Effective" date on the privacy and terms pages
def absu(path):
    """Absolute URL for a site path like 'blog/x.html', or None while no domain is set."""
    return f"{SITE_URL}/{path}" if SITE_URL else None
SRC, OUT = ROOT / "content" / "blog", ROOT / "site" / "blog"
UPDATED = date(2026, 10, 20)          # shown as "Updated" on every article
# reading order on the blog index
ORDER = ["die-cut-lines-in-coreldraw", "powertrace-sticker-coreldraw", "contour-tool-cut-line-coreldraw",
         "print-and-cut-versaworks-coreldraw", "step-and-repeat-sticker-sheet-coreldraw", "coreldraw-die-line-mistakes",
         "photoshop-cut-line-stickers", "photoshop-white-border-sticker", "photoshop-export-stickers-for-print",
         "photoshop-sticker-design-tips", "cutcontour-spot-color", "sticker-bleed-and-safe-zone",
         "white-ink-clear-stickers", "kiss-cut-vs-die-cut-stickers"]
CATS = ["Tutorial", "Guide", "Tips", "Blog"]               # filter order on the guides page
APPS = ["CorelDraw", "Photoshop", "General"]

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' "
        "fill='%230f172a'/%3E%3Ccircle cx='16' cy='16' r='8' fill='none' stroke='%234d8dff' stroke-width='2.4' "
        "stroke-dasharray='3.4 2.6'/%3E%3C/svg%3E")
LOGO = ('<span class="mark"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="6" r="3"/>'
        '<path d="M8.12 8.12 12 12M20 4 8.12 15.88"/><circle cx="6" cy="18" r="3"/><path d="M14.8 14.8 20 20"/></svg></span>')
THEME_HEAD = ("<script>try{var t=localStorage.getItem('dlm-theme');if(t==='dark'||t==='light')"
              "document.documentElement.dataset.theme=t}catch(e){}</script>\n")
THEME_BTN = ('<button class="themebtn" type="button" aria-label="Switch colour theme">'
             '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">'
             '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
             '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M20.5 14.2A8.5 8.5 0 1 1 9.8 3.5a7 7 0 0 0 10.7 10.7Z"/></svg></button>')
SEARCH = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">'
          '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>')


def analytics():
    """Cookie-free Cloudflare Web Analytics beacon, only when a token is set in site.config.json."""
    if not CF_TOKEN:
        return ""
    return (f"<script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
            f"data-cf-beacon='{json.dumps({'token': CF_TOKEN})}'></script>\n")


def contact_fab():
    """Floating contact button, only when an email or WhatsApp number is set."""
    if WHATSAPP:
        return ('<a class="contactfab" href="https://wa.me/' + WHATSAPP + '" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">'
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                '<path d="M3.5 20.5 5 16.3A8.5 8.5 0 1 1 8 19.2Z"/><path d="M9 9.5c.3 2.3 2.2 4.4 4.6 5 .6.1 1.4-.7 1.4-1.4l-1.6-.8-.8.8c-1-.4-1.9-1.3-2.3-2.3l.8-.8L10.4 8c-.7 0-1.5.8-1.4 1.5Z"/></svg>'
                '<span>WhatsApp</span></a>\n')
    if CONTACT_EMAIL:
        return ('<a class="contactfab" href="mailto:' + html.escape(CONTACT_EMAIL) + '" aria-label="Email us">'
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-10 6L2 7"/></svg><span>Contact</span></a>\n')
    return ""


MENU = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">'
        '<path d="M4 7h16M4 12h16M4 17h16"/></svg>')


def load():
    arts = {}
    for f in SRC.glob("*.html"):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->\s*(.*)", raw, re.S)
        if not m:
            raise SystemExit(f"{f.name}: missing <!--meta {{...}} --> block")
        meta, body = json.loads(m.group(1)), m.group(2)
        words = len(re.sub(r"<[^>]+>", " ", body).split())
        meta["mins"] = max(1, math.ceil(words / 200))
        meta["body"] = body
        arts[meta["slug"]] = meta
    return arts


def social(title, desc, path, kind="website"):
    """Canonical, Open Graph and Twitter tags. URLs are absolute only once SITE_URL is set."""
    e = html.escape
    out = [f'<meta property="og:site_name" content="{e(SITE_NAME)}">', f'<meta property="og:type" content="{kind}">',
           f'<meta property="og:locale" content="{LOCALE}">', f'<meta property="og:title" content="{e(title)}">',
           f'<meta property="og:description" content="{e(desc)}">', '<meta name="twitter:card" content="summary_large_image">',
           f'<meta name="twitter:title" content="{e(title)}">', f'<meta name="twitter:description" content="{e(desc)}">']
    if SITE_URL:
        out = [f'<link rel="canonical" href="{absu(path)}">', f'<meta property="og:url" content="{absu(path)}">'] + out + [
               f'<meta property="og:image" content="{absu("assets/og.png")}">', '<meta property="og:image:width" content="1200">',
               '<meta property="og:image:height" content="630">', f'<meta name="twitter:image" content="{absu("assets/og.png")}">']
    return "\n".join(out) + "\n"


def head(title, desc, canonical_note, extra="", path="", kind="website", P="../"):
    e = html.escape
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{canonical_note}<title>{e(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{e(desc)}">
{social(title, desc, path, kind)}<meta name="theme-color" content="#f4f5f8">
<link rel="apple-touch-icon" href="{P}assets/apple-touch-icon.png">
<link rel="icon" href="{ICON}">
<link rel="preconnect" href="https://api.fontshare.com">
<link rel="preconnect" href="https://cdn.fontshare.com" crossorigin>
<link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=general-sans@1&amp;display=swap">
<link rel="stylesheet" href="{P}assets/site.css?v={ASSET_V}">
{THEME_HEAD}{extra}{analytics()}</head>"""


def header(P="../", B="", current="guides"):
    links = [(f"{P}editor.html", "Editor", False), (f"{P}index.html#how", "How it works", False),
             (f"{P}index.html#coreldraw", "CorelDraw guide", False), (f"{B}index.html", "Guides &amp; blog", current == "guides"),
             (f"{P}index.html#faq", "FAQ", False)]
    nav = "\n      ".join(f'<a href="{h}"{" aria-current=\"page\"" if cur else ""}>{t}</a>' for h, t, cur in links)
    mob = "\n    ".join(f'<a href="{h}">{t}</a>' for h, t, _ in links)
    return f"""<header class="nav">
  <div class="in wrapw gut">
    <a class="logo" href="{P}index.html" aria-label="Die Line Maker home">{LOGO}<span>Die Line Maker<b>.</b></span></a>
    <nav aria-label="Main">
      {nav}
    </nav>
    <a class="btn primary" href="{P}editor.html">Make a die line</a>
    {THEME_BTN}
    <button class="menubtn" type="button" aria-expanded="false" aria-controls="mobileMenu" aria-label="Menu">{MENU}</button>
  </div>
  <div class="mobilemenu" id="mobileMenu" hidden>
    {mob}
    <a class="btn primary" href="{P}editor.html">Make a die line</a>
  </div>
</header>"""


def foot_learn(prefix):
    """Footer 'Learn' column; prefix is '' on blog pages and 'blog/' on the homepage."""
    items = [("index.html", "All tutorials &amp; guides"), ("index.html#coreldraw", "CorelDraw tutorials"),
             ("index.html#photoshop", "Photoshop tutorials"), ("index.html#tips", "Tips"),
             ("die-cut-lines-in-coreldraw.html", "Die cut lines in CorelDraw")]
    lis = "".join(f'\n      <li><a href="{prefix}{h}">{t}</a></li>' for h, t in items)
    return f'<div><h3>Learn</h3><ul>{lis}\n    </ul></div>'


def foot_legal(P):
    return (f'<div><h3>About</h3><ul>\n      <li><a href="{P}privacy.html">Privacy policy</a></li>\n'
            f'      <li><a href="{P}terms.html">Terms of use</a></li>\n    </ul></div>')


def footer(arts, P="../", B=""):
    return f"""<footer>
  <div class="in wrapw gut">
    <div><p><b style="color:var(--ink)">Die Line Maker</b>, a free die cut line tool for printers, sign shops and sticker makers. Everything runs in your browser, so your artwork is never uploaded.</p></div>
    <div><h3>Tool</h3><ul>
      <li><a href="{P}editor.html">Make a die line</a></li>
      <li><a href="{P}index.html#coreldraw">CorelDraw guide</a></li>
      <li><a href="{P}index.html#faq">FAQ</a></li>
      <li><a href="{B}index.html">All guides</a></li>
    </ul></div>
    {foot_learn(B)}
    {foot_legal(P)}
    <p class="fine">CorelDraw is a trademark of its owner. Roland, VersaWorks and other names belong to their owners. This site isn't affiliated with any of them.</p>
  </div>
</footer>
{contact_fab()}<script src="{P}assets/site.js?v={ASSET_V}" defer></script>
</body>
</html>
"""


CTA = """<div class="cta">
  <div><b>Make your die line in a minute</b><p>Upload a sticker image and download a CorelDraw-ready PDF with a CutContour cut line, bleed and safe zone. Free, and your image never leaves your computer.</p></div>
  <a class="btn primary" href="../editor.html">Open Die Line Maker</a>
</div>"""


def article_page(a, arts):
    e = html.escape
    body = a["body"]
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body.split("<!--cta-->")[0])
    toc = '<nav class="toc" aria-label="On this page"><h2>On this page</h2><ol>' + "".join(
        f'<li><a href="#{i}">{t}</a></li>' for i, t in heads) + "</ol></nav>"
    body = body.replace("<!--toc-->", toc).replace("<!--cta-->", CTA)
    faqs = re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", body, re.S)
    strip = lambda s: re.sub(r"<[^>]+>", "", s)
    path = f'blog/{a["slug"]}.html'
    art = {"@context": "https://schema.org", "@type": "Article", "headline": a["h1"], "description": a["metaDesc"],
           "datePublished": a.get("published", UPDATED.isoformat()), "dateModified": UPDATED.isoformat(),
           "inLanguage": "en", "articleSection": a.get("cat", "Guide"), "about": a.get("app", "General"),
           "author": {"@type": "Organization", "name": SITE_NAME}, "publisher": {"@type": "Organization", "name": SITE_NAME}}
    if SITE_URL:
        art["mainEntityOfPage"] = absu(path); art["url"] = absu(path); art["image"] = absu("assets/og.png")
    ld = [art]
    if faqs:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(ans)}} for q, ans in faqs]})
    if SITE_URL:   # breadcrumb items must be absolute URLs, so only once the domain is known
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": absu("")},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": absu("blog/")},
            {"@type": "ListItem", "position": 3, "name": a["crumb"], "item": absu(path)}]})
    extra = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    note = f"<!-- Detected Article Type: {a['type']} | Sentiment Target Range: {a['range']} | Sentiment Tone: {a['tone']} -->\n"
    related = "".join(f'<li><a href="{s}.html">{e(arts[s]["h1"])}</a></li>' for s in a.get("related", []) if s in arts)
    sources = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{e(t)}</a></li>' for t, u in a.get("sources", []))
    return f"""{head(a["metaTitle"], a["metaDesc"], note, extra, path, "article")}
<body class="skin lightfirst">
<a class="skip" href="#article">Skip to the article</a>
{header()}
<main id="article" class="gut">
<article class="article">
<ol class="crumbs"><li><a href="../index.html">Home</a></li><li><a href="index.html">Guides</a></li><li aria-current="page">{e(a["crumb"])}</li></ol>
<h1>{e(a["h1"])}</h1>
<p class="meta"><span>{e(a.get("cat", a["tagline"]))}</span><span>{e(a.get("app", "General"))}</span><span>{a["mins"]} min read</span><span>Updated {UPDATED.day} {UPDATED.strftime("%B %Y")}</span></p>
{body}
<section class="related keep"><h2>Keep reading</h2><ul>{related}</ul></section>
<section class="related"><h2>Sources</h2><ul>{sources}</ul></section>
</article>
</main>
{footer(arts)}"""


def index_page(arts):
    e = html.escape
    missing = [s for s in arts if s not in ORDER]
    if missing: raise SystemExit(f"Add these slugs to ORDER in tools/build_blog.py: {missing}")
    cards = "".join(f"""
  <li data-cat="{e(arts[s].get('cat', 'Blog'))}" data-app="{e(arts[s].get('app', 'General'))}"><a class="pcard" href="{s}.html">
    <span class="chips"><span class="tagline">{e(arts[s].get('cat', arts[s]['tagline']))}</span><span class="appchip">{e(arts[s].get('app', 'General'))}</span></span>
    <h2>{e(arts[s]["h1"])}</h2>
    <p>{e(arts[s]["summary"])}</p>
    <span class="meta">{arts[s]["mins"]} min read</span>
  </a></li>""" for s in ORDER if s in arts)
    count = lambda k, v: sum(1 for a in arts.values() if a.get(k) == v)
    plural = {"Tutorial": "Tutorials", "Guide": "Guides", "Tips": "Tips", "Blog": "Blog"}
    cat_btns = f'<button type="button" data-f="cat" data-v="" aria-pressed="true">All <span>{len(arts)}</span></button>' + "".join(
        f'<button type="button" data-f="cat" data-v="{c}" aria-pressed="false">{plural[c]} <span>{count("cat", c)}</span></button>' for c in CATS if count("cat", c))
    app_btns = '<button type="button" data-f="app" data-v="" aria-pressed="true">All apps</button>' + "".join(
        f'<button type="button" data-f="app" data-v="{a}" aria-pressed="false">{a}</button>' for a in APPS if count("app", a))
    title = "Die Cut Tutorials and Guides for CorelDraw and Photoshop"
    desc = ("Free die cut tutorials, guides and tips for CorelDraw and Photoshop: cut lines, PowerTRACE, Contour, "
            "CutContour, print and cut with VersaWorks, sticker sheets, white borders, bleed and white ink.")
    return f"""{head(title, desc, "", "", "blog/")}
<body class="skin lightfirst">
<a class="skip" href="#guides">Skip to the guides</a>
{header()}
<main id="guides">
<section class="bloghead wrapw gut">
  <ol class="crumbs"><li><a href="../index.html">Home</a></li><li aria-current="page">Guides</li></ol>
  <div class="eyebrow">Guides &amp; blog</div>
  <h1 style="margin-top:12px">Tutorials, guides and tips for die cut stickers</h1>
  <p class="lede">Plain-English help for printers, sign shops and sticker makers, in CorelDraw and Photoshop. New here? Start with <a href="die-cut-lines-in-coreldraw.html">die cut lines in CorelDraw</a>.</p>
  <div class="search" role="search">{SEARCH}<label class="sr-only" for="postSearch">Search the guides</label><input id="postSearch" type="search" placeholder="Search guides, e.g. PowerTRACE, white ink, VersaWorks" autocomplete="off" enterkeyhint="search"></div>
  <div class="filters" role="group" aria-label="Filter by type">{cat_btns}</div>
  <div class="filters filters-app" role="group" aria-label="Filter by app">{app_btns}</div>
</section>
<div class="wrapw gut">
<ul class="cards" id="postList">{cards}
</ul>
<p class="lede" id="noPosts" hidden>No guides match that search or filter. Try fewer words, or pick <b>All</b>.</p>
{CTA.replace('class="cta"', 'class="cta" style="margin-top:0;margin-bottom:56px"')}
</div>
</main>
{footer(arts)}"""


def home_sections(arts):
    """Homepage 'Learn' section: the latest CorelDraw and Photoshop posts."""
    e = html.escape
    pick = [s for s in ORDER if arts.get(s, {}).get("app") == "CorelDraw"][:3] + [s for s in ORDER if arts.get(s, {}).get("app") == "Photoshop"][:3]
    cards = "".join(f"""
      <li data-app="{e(arts[s]['app'])}"><a class="pcard" href="blog/{s}.html">
        <span class="chips"><span class="tagline">{e(arts[s].get('cat', 'Guide'))}</span><span class="appchip">{e(arts[s]['app'])}</span></span>
        <h3 style="font-size:18px;line-height:1.25">{e(arts[s]['h1'])}</h3>
        <p>{e(arts[s]['summary'])}</p>
        <span class="meta">{arts[s]['mins']} min read</span>
      </a></li>""" for s in pick)
    return f"""<!--learn:start-->
<section class="sec" id="learn">
  <div class="wrapw gut">
    <div class="sech"><div class="eyebrow">Learn</div><h2>Tutorials for CorelDraw and Photoshop</h2>
      <p class="lede">Step-by-step help for every part of the job, from tracing a sticker to sending a print and cut file. {len(arts)} free guides and counting.</p></div>
    <ul class="cards" style="margin-bottom:24px">{cards}
    </ul>
    <a class="btn ink pill" href="blog/index.html">See all tutorials &amp; guides</a>
  </div>
</section>
<!--learn:end-->"""


HOME_TITLE = "Die Cut Line Maker for CorelDraw: Free CutContour PDF"
HOME_DESC = ("Upload a sticker image and get a CorelDraw-ready die cut line with a CutContour spot colour, "
             "bleed and sheet layout. Free, and your images never leave your device.")


def home_seo(s):
    """Title, description, social tags and structured data for the homepage (FAQ read from the page itself)."""
    e = html.escape
    strip = lambda t: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).strip()
    faq_html = s[s.find('id="faq"'):]
    faqs = re.findall(r"<details(?: id=\"[^\"]*\")?><summary>(.*?)</summary><p>(.*?)</p></details>", faq_html, re.S)
    app = {"@context": "https://schema.org", "@type": "WebApplication", "name": SITE_NAME, "applicationCategory": "DesignApplication",
           "operatingSystem": "Any (runs in the browser)", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
           "description": HOME_DESC, "featureList": ["CutContour spot colour PDF for CorelDraw", "Automatic contour tracing",
           "Bleed, safe zone and white border", "Sticker sheet detection", "SVG, EPS, DXF and PNG export", "Vector artwork option"]}
    if SITE_URL: app["url"] = absu("")
    ld = [app]
    if faqs:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(ans)}} for q, ans in faqs]})
    scripts = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    return (f"<!--seo:start--><title>{e(HOME_TITLE)}</title>\n<meta name=\"description\" content=\"{e(HOME_DESC)}\">\n"
            + social(HOME_TITLE, HOME_DESC, "") + '<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">\n' + scripts + "<!--seo:end-->")


def contact_line():
    if CONTACT_EMAIL:
        return f'email <a href="mailto:{html.escape(CONTACT_EMAIL)}">{html.escape(CONTACT_EMAIL)}</a>'
    return 'email <b>[add your email to site.config.json]</b>'


def legal_page(slug, title, desc, h1, body, arts):
    d = f"{LEGAL_DATE.day} {LEGAL_DATE.strftime('%B %Y')}"
    return f"""{head(title, desc, "", "", f"{slug}.html", "website", "")}
<body class="skin lightfirst">
<a class="skip" href="#legal">Skip to content</a>
{header("", "blog/", "")}
<main id="legal" class="gut">
<article class="article">
<ol class="crumbs"><li><a href="index.html">Home</a></li><li aria-current="page">{html.escape(h1)}</li></ol>
<h1>{html.escape(h1)}</h1>
<p class="meta"><span>Effective {d}</span><span>Last updated {d}</span></p>
<div class="prose">
{body}
</div>
</article>
</main>
{footer(arts, "", "blog/")}"""


def privacy_body():
    if CF_TOKEN:
        stats = ("<p>To count visits we use <a href=\"https://www.cloudflare.com/web-analytics/\" target=\"_blank\" rel=\"noopener\">Cloudflare Web Analytics</a>. "
                 "It doesn't use cookies or local storage and doesn't build a profile of you. It records page views, the page you came from, "
                 "your browser type and a rough country, and shows them to us only as totals.</p>")
    else:
        stats = "<p>The site doesn't use analytics, advertising or tracking scripts.</p>"
    return f"""<p>{SITE_NAME} is a free tool that makes die cut lines from sticker and label images. This policy explains what happens to your information when you use the website. In short: <b>your images never leave your device, and we don't collect personal data.</b></p>

<h2 id="images">Your images and designs</h2>
<p>When you upload an image, it is opened and processed by your own web browser, on your own computer or phone. The image, the cut line and the files you download (PDF, SVG, EPS, DXF, PNG, ZIP) are created on your device. They are not sent to us or to anyone else, and we can't see them.</p>
<p>When you close or reload the page, the image is gone. We don't keep a copy, because we never had one.</p>

<h2 id="collect">What we collect</h2>
<p>There are no accounts, sign-ups, forms or payments on this site, so we don't ask for your name, email address, phone number or any other personal details.</p>
{stats}

<h2 id="cookies">Cookies and local storage</h2>
<p>The site doesn't set cookies. If you use the light or dark mode switch, your choice is saved in your browser's local storage under the name <b>dlm-theme</b>, so the site looks the same next time. It stays on your device and is never sent to us. You can clear it at any time by clearing your browser's site data.</p>
<p>Because we don't use tracking or advertising cookies, the site doesn't show a cookie banner.</p>

<h2 id="hosting">Hosting</h2>
<p>Like every website, our hosting provider receives basic technical information when your browser asks for a page: your IP address, browser type, the page requested and the time. The host uses this to deliver the site and protect it from abuse, and keeps it only for a short time under its own privacy policy. We don't use it to identify you.</p>
<p>Styles and scripts are served from our own website. The General Sans font comes from <a href="https://www.fontshare.com/" target="_blank" rel="noopener">Fontshare</a>, run by Indian Type Foundry, so your browser downloads it from their servers. Like any web server, they receive your IP address and browser type when it does. We don't send them anything else.</p>

<h2 id="links">Links to other websites</h2>
<p>Our guides link to other websites, such as software makers' manuals. Those sites have their own privacy policies, which apply once you leave {SITE_NAME}.</p>

<h2 id="rights">Your rights</h2>
<p>We follow India's Digital Personal Data Protection Act, 2023. Since we don't collect personal data, there is usually nothing for us to show, correct or delete. If you think we hold information about you, or you have a question or complaint about privacy, {contact_line()} and we'll reply within 30 days.</p>

<h2 id="children">Children</h2>
<p>The site isn't aimed at children, and we don't knowingly collect any information from anyone, including children.</p>

<h2 id="changes">Changes to this policy</h2>
<p>If we change how the site works, for example by adding a feature that needs personal data, we'll update this page and the date at the top before the change takes effect.</p>

<h2 id="contact">Contact</h2>
<p>For anything about this policy, {contact_line()}.</p>"""


def terms_body():
    return f"""<p>These terms apply when you use the {SITE_NAME} website, its die line editor and its guides. By using the site you agree to them. If you don't agree, please don't use the site.</p>

<h2 id="service">The service</h2>
<p>{SITE_NAME} is free. It traces images you choose and creates cut line files for printing and cutting. It runs in your browser, and we may change, improve or stop any part of it at any time.</p>

<h2 id="artwork">Your artwork</h2>
<p>You keep all rights to the images you upload and the files you make. We don't receive your images and claim no rights to them.</p>
<p>Only use images you own or have permission to use. You are responsible for making sure your stickers, labels and designs don't break copyright, trademark or any other law.</p>

<h2 id="check">Check every file before cutting</h2>
<p>Automatic tracing is a starting point, not a guarantee. Every printer, cutter and material is different. Before a production run, <b>open the file in your design software, check the cut line, bleed and spot colour name, and do a test cut</b> on scrap material.</p>
<p>We aren't responsible for wasted material, damaged blades or machines, missed deadlines or lost business caused by a file made with the site, or by acting on our guides.</p>

<h2 id="warranty">No warranty</h2>
<p>The site, the tool and the guides are provided "as is" and "as available", without any warranty that they are accurate, complete, error-free or suitable for a particular job. Our guides are general information, written in good faith. Software and printers change, so always check your own software's documentation.</p>

<h2 id="liability">Limit of liability</h2>
<p>As far as the law allows, {SITE_NAME} and the people who run it are not liable for any indirect, incidental or consequential loss, or for any loss of profit, data or materials, arising from using or not being able to use the site. Since the service is free, our total liability for any claim is limited to ₹1,000.</p>

<h2 id="use">Fair use</h2>
<p>Please don't try to break, overload or misuse the site, copy it to pass off as your own service, or use it for anything unlawful.</p>

<h2 id="trademarks">Trademarks</h2>
<p>CorelDraw, Photoshop, Roland, VersaWorks and other product names are trademarks of their owners. {SITE_NAME} isn't affiliated with or endorsed by any of them. The names are used only to describe compatibility.</p>

<h2 id="law">Governing law</h2>
<p>These terms are governed by the laws of India. Any dispute will be handled by the courts of India.</p>

<h2 id="changes">Changes to these terms</h2>
<p>We may update these terms. The date at the top shows the latest version. Continuing to use the site after a change means you accept the updated terms.</p>

<h2 id="contact">Contact</h2>
<p>Questions about these terms? {contact_line()}.</p>"""


def write_legal(arts):
    site = ROOT / "site"
    (site / "privacy.html").write_text(legal_page(
        "privacy", f"Privacy Policy · {SITE_NAME}",
        f"How {SITE_NAME} handles your information: images are processed in your browser and never uploaded, no accounts, no tracking cookies.",
        "Privacy policy", privacy_body(), arts), encoding="utf-8")
    (site / "terms.html").write_text(legal_page(
        "terms", f"Terms of Use · {SITE_NAME}",
        f"The terms for using the free {SITE_NAME} die line tool and guides: your artwork stays yours, check files before cutting, no warranty.",
        "Terms of use", terms_body(), arts), encoding="utf-8")


def write_site_files(arts):
    site = ROOT / "site"
    robots = "User-agent: *\nAllow: /\n" + (f"\nSitemap: {absu('sitemap.xml')}\n" if SITE_URL else "")
    (site / "robots.txt").write_text(robots, encoding="utf-8")
    if SITE_URL:
        pages = [("", "1.0"), ("editor.html", "0.9"), ("blog/", "0.8"), ("privacy.html", "0.3"), ("terms.html", "0.3")] + [(f"blog/{s}.html", "0.7") for s in ORDER if s in arts]
        urls = "".join(f"  <url><loc>{absu(u)}</loc><lastmod>{UPDATED.isoformat()}</lastmod><priority>{pr}</priority></url>\n" for u, pr in pages)
        (site / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                          + urls + "</urlset>\n", encoding="utf-8")
    elif (site / "sitemap.xml").exists():
        (site / "sitemap.xml").unlink()
    # 404 page: root-relative links so it works at any missing address
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Page not found · {html.escape(SITE_NAME)}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="{ICON}">
<link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=general-sans@1&amp;display=swap">
<link rel="stylesheet" href="/assets/site.css?v={ASSET_V}">
{THEME_HEAD}</head>
<body class="skin lightfirst">
<main class="gut" style="min-height:100vh;display:grid;place-items:center;text-align:center">
  <div style="display:grid;gap:14px;justify-items:center;max-width:460px">
    <a class="logo" href="/">{LOGO}<span>{html.escape(SITE_NAME)}<b>.</b></span></a>
    <h1 style="font-size:44px">Page not found</h1>
    <p class="lede" style="margin:0">That address doesn't exist. Make a die line, or browse the tutorials and guides.</p>
    <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center"><a class="btn primary" href="/editor.html">Make a die line</a><a class="btn" href="/blog/">Tutorials &amp; guides</a></div>
  </div>
</main>
</body>
</html>
"""
    (site / "404.html").write_text(page, encoding="utf-8")


def update_home(arts):
    home = ROOT / "site" / "index.html"
    s = home.read_text(encoding="utf-8")
    s = re.sub(r"<!--seo:start-->.*?<!--seo:end-->", lambda m: home_seo(s), s, flags=re.S)
    s = re.sub(r"<!--learn:start-->.*?<!--learn:end-->", lambda m: home_sections(arts), s, flags=re.S)
    s = re.sub(r"<!--footguides:start-->.*?<!--footguides:end-->",
               lambda m: "<!--footguides:start-->" + foot_learn("blog/") + "<!--footguides:end-->", s, flags=re.S)
    s = managed(s, fab=True)
    home.write_text(s, encoding="utf-8")


def managed(s, fab):
    """Theme script + analytics before </head>, and the contact button before </body>, kept between markers."""
    s = re.sub(r'assets/site\.(css|js)(\?v=\w+)?"', lambda m: f'assets/site.{m.group(1)}?v={ASSET_V}"', s)
    block = "<!--head:start-->\n" + THEME_HEAD + analytics() + "<!--head:end-->\n"
    if "<!--head:start-->" in s:
        s = re.sub(r"<!--head:start-->.*?<!--head:end-->\n", lambda m: block, s, flags=re.S)
    else:
        s = s.replace("</head>", block + "</head>", 1)
    if fab:
        fb = "<!--fab:start-->\n" + contact_fab() + "<!--fab:end-->\n"
        if "<!--fab:start-->" in s:
            s = re.sub(r"<!--fab:start-->.*?<!--fab:end-->\n", lambda m: fb, s, flags=re.S)
        else:
            i = s.rindex('<script src="assets/site.js'); s = s[:i] + fb + s[i:]
    return s


EDITOR_TITLE = "Die Line Editor: Make a CutContour Cut Line Online · Die Line Maker"
EDITOR_DESC = ("Upload a sticker or label image and get a CorelDraw-ready CutContour cut line, bleed, white border and sheet layout. "
               "Free and private: it runs in your browser.")


def update_editor():
    """Title, description and social tags for the full-screen editor page."""
    page = ROOT / "site" / "editor.html"
    if not page.exists():
        return
    e = html.escape
    seo = (f'<!--seo:start--><title>{e(EDITOR_TITLE)}</title>\n<meta name="description" content="{e(EDITOR_DESC)}">\n'
           + social(EDITOR_TITLE, EDITOR_DESC, "editor.html") + "<!--seo:end-->")
    s = page.read_text(encoding="utf-8")
    s = re.sub(r"<!--seo:start-->.*?<!--seo:end-->", lambda m: seo, s, flags=re.S)
    page.write_text(managed(s, fab=False), encoding="utf-8")


def main():
    arts = load()
    OUT.mkdir(parents=True, exist_ok=True)
    for a in arts.values():
        (OUT / f'{a["slug"]}.html').write_text(article_page(a, arts), encoding="utf-8")
    (OUT / "index.html").write_text(index_page(arts), encoding="utf-8")
    update_home(arts)
    update_editor()
    write_legal(arts)
    write_site_files(arts)
    if not SITE_URL:
        print("Note: site_url is empty in site.config.json, so canonical links, sitemap.xml and absolute share images are skipped.")
    if not CONTACT_EMAIL:
        print("Note: contact_email is empty in site.config.json, so the privacy and terms pages show a placeholder instead of an email address.")
    print(f"Built {len(arts)} articles + index into {OUT}")


if __name__ == "__main__":
    main()

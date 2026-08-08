#!/usr/bin/env python3
# Adds a shared sticky navbar to every tool and generates the root index page.
import re, os, io

ROOT = "/home/claude/work/tools"

# slug, nav label, page title, one-line description, mark html
TOOLS = [
    ("csv-json", "CSV \u2194 JSON", "CSV \u2194 JSON",
     "Convert in either direction. Quoted fields, embedded newlines and unusual delimiters are handled properly.",
     '<span class="tmark tmark-glyph">\u21c4</span>'),
    ("jwt-decoder", "JWT decoder", "JWT decoder",
     "Read a token\u2019s header, payload and claims, and check its signature against a secret.",
     '<span class="tmark tmark-glyph">{}</span>'),
    ("password-generator", "Passwords", "Password generator",
     "Random passwords or passphrases from your browser\u2019s cryptographic randomness, with entropy and crack-time estimates.",
     '<span class="tmark tmark-glyph">\u2022\u2022</span>'),
    ("pdf-merge", "PDF merge", "PDF merge",
     "Drop PDFs, drag to reorder, pick page ranges, download one file.",
     '<span class="tmark tmark-pdf"></span>'),
    ("qr-generator", "QR code", "QR generator",
     "Type anything and get a QR code. Choose the error-correction level, download PNG or SVG.",
     '<span class="tmark tmark-qr"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>'),
]

MARKER = "<!-- site-nav -->"

NAV_CSS = """
<style>/* ── shared site nav ─────────────────────────────────────────── */
.sitenav{position:sticky;top:0;z-index:60;margin:-32px -20px 26px;padding:0 20px;
  background:var(--bg);border-bottom:1px solid var(--border)}
@supports (backdrop-filter:blur(2px)){
  .sitenav{background:color-mix(in srgb,var(--bg) 80%,transparent);
    -webkit-backdrop-filter:saturate(180%) blur(14px);backdrop-filter:saturate(180%) blur(14px)}
}
.sitenav-in{max-width:840px;margin:0 auto;height:46px;display:flex;align-items:center;gap:14px}
.nv-home{display:inline-flex;align-items:center;gap:8px;flex:none;text-decoration:none;
  color:var(--text);font-size:13.5px;font-weight:600;letter-spacing:-.01em}
.nv-logo{width:20px;height:20px;display:block;flex:none}
.nv-logo .bg{fill:var(--solid)}
.nv-logo .fg{fill:var(--solid-text)}
.nv-links{display:flex;align-items:center;gap:2px;margin-left:auto;
  overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none}
.nv-links::-webkit-scrollbar{display:none}
.nv-links a{flex:none;white-space:nowrap;text-decoration:none;color:var(--muted);
  font-size:13px;padding:5px 9px;border-radius:var(--radius-sm);
  transition:color .12s ease,background-color .12s ease}
.nv-links a:hover{color:var(--text);background:var(--subtle)}
.nv-links a[aria-current="page"]{color:var(--text);font-weight:600;background:var(--subtle)}
.sitenav a:focus-visible{outline:2px solid var(--text);outline-offset:2px}
@media (max-width:620px){
  .sitenav-in{gap:8px}
  .nv-word{display:none}
  .nv-links{-webkit-mask-image:linear-gradient(90deg,#000 0,#000 90%,transparent 100%);
    mask-image:linear-gradient(90deg,#000 0,#000 90%,transparent 100%);padding-right:10px}
}
@media (prefers-reduced-motion:reduce){.nv-links a{transition:none}}
</style>"""

LOGO = ('<svg class="nv-logo" viewBox="0 0 20 20" aria-hidden="true">'
        '<rect class="bg" width="20" height="20" rx="5"/>'
        '<g class="fg">'
        '<rect x="5" y="5" width="4" height="4" rx="1"/>'
        '<rect x="11" y="5" width="4" height="4" rx="1"/>'
        '<rect x="5" y="11" width="4" height="4" rx="1"/>'
        '<rect x="11" y="11" width="4" height="4" rx="1" opacity=".4"/>'
        '</g></svg>')


def nav_html(base, current):
    """base: '' from root, '../' from a tool dir. current: slug or 'home'."""
    home_cur = ' aria-current="page"' if current == "home" else ""
    links = []
    for slug, label, _t, _d, _m in TOOLS:
        cur = ' aria-current="page"' if slug == current else ""
        links.append('        <a href="%s%s/"%s>%s</a>' % (base, slug, cur, label))
    return (
        MARKER + '\n<nav class="sitenav" aria-label="Tools">\n'
        '  <div class="sitenav-in">\n'
        '    <a class="nv-home" href="%s"%s>%s<span class="nv-word">tools</span></a>\n'
        '    <div class="nv-links">\n%s\n    </div>\n'
        '  </div>\n</nav>\n' % (base or "./", home_cur, LOGO, "\n".join(links))
    )


def inject(slug):
    path = os.path.join(ROOT, slug, "index.html")
    with io.open(path, encoding="utf-8") as f:
        html = f.read()
    if MARKER in html:
        print("  skip (already has nav):", slug)
        return
    # 1. stylesheet just before </head>
    assert "</head>" in html, slug
    html = html.replace("</head>", NAV_CSS + "\n</head>", 1)
    # 2. nav markup immediately after <body ...>
    m = re.search(r"<body[^>]*>", html)
    assert m, slug
    html = html[: m.end()] + "\n" + nav_html("../", slug) + html[m.end():]
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("  navbar added:", slug)


if __name__ == "__main__":
    print("Injecting navbar:")
    for slug, *_ in TOOLS:
        inject(slug)

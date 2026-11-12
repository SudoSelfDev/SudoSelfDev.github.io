#!/usr/bin/env python3
"""Build sudoself.dev.

Reads site.toml and content/logs/*.md, then writes the HTML pages, the logs
feed, sitemap.xml and robots.txt into this folder. Run it after every change:

    pip install -r requirements.txt
    python3 build.py

See README.md for how to write a log.
"""
import hashlib
import html
import json
import math
import re
import tomllib
from pathlib import Path

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parent
CFG = tomllib.loads((ROOT / 'site.toml').read_text(encoding='utf-8'))
SITE = CFG['site']
URL = SITE['url'].rstrip('/')
E = html.escape

# Inline SVG icons
GH = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>'
XI = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
SUN = '<svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
MOON = '<svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/></svg>'
BURGER = '<svg class="i-burger" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
CLOSE = '<svg class="i-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>'

# ------------------------------------------------------------------ helpers

def asset_version():
    h = hashlib.sha1()
    for name in ('style.css', 'script.js'):
        h.update((ROOT / name).read_bytes())
    return h.hexdigest()[:8]


VER = asset_version()


def write(path, text):
    full = ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text, encoding='utf-8')
    print('  wrote', path)


def jsonld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'


def theme_boot(preload_portrait):
    extra = ''
    if preload_portrait:
        extra = ("var l=document.createElement('link');l.rel='preload';l.as='image';"
                 "l.href=t==='light'?'/assets/portrait.webp':'/assets/portrait-dark.webp';document.head.appendChild(l);")
    return ("<script>(function(){var t;try{t=localStorage.getItem('theme')}catch(e){}"
            "if(t!=='light'&&t!=='dark'){t=window.matchMedia&&matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'}"
            "var d=document.documentElement;d.setAttribute('data-theme',t);d.classList.add('js');" + extra + "})();</script>")


def head(title, desc, path, og_type='website', extra='', preload_portrait=False):
    url = URL + path
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="alternate" type="application/atom+xml" title="{E(SITE['name'])} logs" href="/blogs/feed.xml">
<meta property="og:site_name" content="{E(SITE['name'])}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{URL}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{URL}/assets/og.png">
{theme_boot(preload_portrait)}
<link rel="preload" href="/assets/fonts/jost.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/crimson-pro.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css?v={VER}">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''


def nav_items():
    items = [('/#about', 'About', 'about'), ('/#learning', 'Learning', 'learning')]
    if CFG.get('projects'):
        items.append(('/#projects', 'Projects', 'projects'))
    items += [('/blogs/', 'Logs', 'logs'), ('/#contact', 'Contact', 'contact')]
    return items


def header(current=''):
    links = '\n      '.join(
        f'<li><a href="{href}" data-section="{key}"{" aria-current=\"page\"" if key == current else ""}>{text}</a></li>'
        for href, text, key in nav_items())
    return f'''<header class="site-header">
  <a class="brand" href="/">[{E(SITE['name'])}]</a>
  <div class="header-tools">
    <button id="theme-toggle" class="theme-toggle" type="button" aria-label="Toggle light and dark theme">{SUN}{MOON}</button>
    <button id="menu-toggle" class="menu-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav">{BURGER}{CLOSE}</button>
  </div>
  <nav id="site-nav" aria-label="Main">
    <ul>
      {links}
    </ul>
  </nav>
</header>
'''


def footer():
    pages = ''.join(f'<li><a href="{href}">{text}</a></li>' for href, text, _ in nav_items())
    elsewhere = [
        f'<li><a href="https://github.com/{E(SITE["github"])}" target="_blank" rel="noopener">{GH}{E(SITE["github"])}</a></li>',
        f'<li><a href="https://x.com/{E(SITE["x"])}" target="_blank" rel="noopener">{XI}@{E(SITE["x"])}</a></li>',
    ]
    if SITE.get('linkedin'):
        elsewhere.append(f'<li><a href="{E(SITE["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a></li>')
    elsewhere.append('<li><a href="https://learntocloud.guide/" target="_blank" rel="noopener">Learn to Cloud</a></li>')
    elsewhere.append('<li><a href="/blogs/feed.xml">RSS feed</a></li>')
    return f'''<footer class="site-footer">
  <div><h4>Pages</h4><ul>{pages}</ul></div>
  <div><h4>Elsewhere</h4><ul>
    {chr(10).join("    " + e for e in elsewhere).strip()}
  </ul></div>
  <div><h4>Say hi</h4><ul><li><a href="mailto:{E(SITE['email'])}">{E(SITE['email'])}</a></li></ul></div>
</footer>
<p class="copy">&copy; {SITE['year']} {E(SITE['name'])}</p>
<script src="/script.js?v={VER}"></script>
</body>
</html>
'''

# ------------------------------------------------------------------ logs

FENCE = re.compile(r'^```([\w+-]+)?(?:[ \t]+title="([^"]*)")?[ \t]*\n(.*?)\n```[ \t]*$', re.M | re.S)


def render_code(lang, title, code):
    try:
        lexer = get_lexer_by_name(lang) if lang else TextLexer()
    except ClassNotFound:
        lexer = TextLexer()
    body = highlight(code, lexer, HtmlFormatter(nowrap=True)).rstrip('\n')
    label = title or lang or 'Code'
    return (f'<div class="code-block"><div class="code-block-header">{E(label)}</div>'
            f'<pre class="hl"><code>{body}</code></pre></div>')


def render_markdown(text):
    """Markdown to HTML. Returns (html, toc) where toc is a list of (id, label)."""
    blocks = []

    def stash(m):
        blocks.append(render_code(m.group(1), m.group(2), m.group(3)))
        return f'\n\n@@CODE{len(blocks) - 1}@@\n\n'

    text = FENCE.sub(stash, text)
    md = markdown.Markdown(
        extensions=['attr_list', 'toc', 'tables', 'sane_lists'],
        extension_configs={'toc': {'permalink': '#', 'permalink_class': 'anchor',
                                   'permalink_title': 'Link to this section', 'toc_depth': '2-3'}})
    out = md.convert(text)
    for i, block in enumerate(blocks):
        out = out.replace(f'<p>@@CODE{i}@@</p>', block)
    # "(1) Do this" at the start of a paragraph becomes a numbered step
    out = re.sub(r'<p>\((\d+)\) ', r'<p><span class="step-number">\1</span> ', out)
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', out)
    toc = [(t['id'], re.sub(r'^//\s*\d+\.\s*', '', html.unescape(t['name']))) for t in md.toc_tokens if t['level'] == 2]
    return out, toc


def load_logs():
    logs = []
    for path in sorted((ROOT / 'content' / 'logs').glob('*.md')):
        raw = path.read_text(encoding='utf-8')
        m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
        if not m:
            raise SystemExit(f'{path.name}: missing the --- front matter block at the top')
        meta = {}
        for line in m.group(1).splitlines():
            if line.strip():
                key, _, value = line.partition(':')
                meta[key.strip()] = value.strip()
        for key in ('title', 'date', 'summary'):
            if not meta.get(key):
                raise SystemExit(f'{path.name}: front matter needs "{key}"')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', meta['date']):
            raise SystemExit(f'{path.name}: date must look like 2026-03-27')
        body = m.group(2)
        words = len(re.findall(r'\w+', FENCE.sub(' ', body))) + len(re.findall(r'\w+', ' '.join(c[2] for c in FENCE.findall(body)))) // 2
        meta.update(slug=path.stem, body=body, minutes=max(1, math.ceil(words / 200)))
        meta['label'] = f"{meta['date']} // LOG_{meta['log']}" if meta.get('log') else meta['date']
        logs.append(meta)
    return sorted(logs, key=lambda l: (l['date'], l.get('log', '')), reverse=True)


def entry_card(log, reveal=False):
    return f'''<a class="entry{" reveal" if reveal else ""}" href="/blogs/{log['slug']}/">
        <p class="meta">{E(log['label'])}</p>
        <h3>{E(log['title'])}</h3>
        <p>{E(log['summary'])}</p>
        <span class="more">Read the log</span>
      </a>'''


def build_log(log):
    body, toc = render_markdown(log['body'])
    path = f"/blogs/{log['slug']}/"
    desc = log.get('description') or log['summary']
    page_title = f"{SITE['name']} | {log.get('page_title') or log['title']}"
    meta_bits = [log['label']]
    if log.get('kind'):
        meta_bits.append(log['kind'])
    meta_bits.append(f"{log['minutes']} min read")
    toc_html = ''
    if len(toc) > 1:
        rows = '\n'.join(f'      <li><a href="#{i}"><span class="toc-num">{n:02d}</span> {E(label)}</a></li>'
                         for n, (i, label) in enumerate(toc, 1))
        toc_html = f'''<nav class="toc" aria-label="Table of contents">
    <div class="toc-header">// Table of Contents</div>
    <ol class="toc-list">
{rows}
    </ol>
  </nav>
  '''
    subtitle = f'<p class="post-subtitle">{E(log["subtitle"])}</p>' if log.get('subtitle') else ''
    ld = jsonld({
        '@context': 'https://schema.org', '@type': 'BlogPosting',
        'headline': log['title'], 'description': desc, 'datePublished': log['date'],
        'url': URL + path, 'image': URL + '/assets/og.png',
        'author': {'@type': 'Person', 'name': SITE['author'], 'url': URL + '/'},
    })
    extra = f'<meta property="article:published_time" content="{log["date"]}">\n' + ld
    page = head(page_title, desc, path, og_type='article', extra=extra) + header('logs') + f'''
<main class="page" id="main">
  <a href="/blogs/" class="back-link">&lt;- /back_to_archive</a>
  <article>
  <p class="post-meta">{E(' // '.join(meta_bits))}</p>
  <h1 class="post-title">{E(log['title'])}</h1>
  {subtitle}
  {toc_html}<div class="prose">
  {body}
  </div>
  </article>
</main>

''' + footer()
    write(f"blogs/{log['slug']}/index.html", page)

# ------------------------------------------------------------------ home sections

def roadmap_html():
    phases = CFG.get('roadmap') or []
    if not phases:
        return ''
    label = {'done': 'Done', 'current': 'In progress', 'todo': 'Up next'}
    rows = []
    for p in phases:
        status = p.get('status', 'todo')
        if status not in label:
            raise SystemExit(f'site.toml: roadmap status must be done, current or todo (got "{status}")')
        detail = f'<small>{E(p["detail"])}</small>' if p.get('detail') else ''
        rows.append(f'<li class="{status}"><span class="dot"></span><span class="name">{E(p["name"])}{detail}</span>'
                    f'<span class="state">{label[status]}</span></li>')
    return '<ol class="roadmap-track reveal">\n        ' + '\n        '.join(rows) + '\n      </ol>'


def projects_html():
    projects = CFG.get('projects') or []
    if not projects:
        return ''
    cards = []
    for p in projects:
        tags = ''.join(f'<span>{E(t)}</span>' for t in p.get('tags', []))
        tags = f'<div class="tags">{tags}</div>' if tags else ''
        inner = f'<h3>{E(p["name"])}</h3><p>{E(p["description"])}</p>{tags}'
        if p.get('url'):
            cards.append(f'<a class="project reveal" href="{E(p["url"])}" target="_blank" rel="noopener">{inner}</a>')
        else:
            cards.append(f'<div class="project reveal">{inner}</div>')
    return f'''
  <section id="projects">
    <div class="wrap">
      <h2 class="section-title reveal">Projects</h2>
      <div class="projects">
        {chr(10).join("        " + c for c in cards).strip()}
      </div>
    </div>
  </section>
'''


def build_home(logs):
    latest = '\n      '.join(entry_card(l, reveal=True) for l in logs[:3])
    buttons = [f'<a class="btn fill" href="mailto:{E(SITE["email"])}">Email me</a>']
    if SITE.get('resume'):
        buttons.append(f'<a class="btn" href="{E(SITE["resume"])}" target="_blank" rel="noopener">R&eacute;sum&eacute;</a>')
    if SITE.get('linkedin'):
        buttons.append(f'<a class="btn" href="{E(SITE["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>')
    buttons.append(f'<a class="btn" href="https://x.com/{E(SITE["x"])}" target="_blank" rel="noopener">@{E(SITE["x"])} on X</a>')
    buttons.append(f'<a class="btn" href="https://github.com/{E(SITE["github"])}" target="_blank" rel="noopener">GitHub</a>')
    same_as = [f'https://github.com/{SITE["github"]}', f'https://x.com/{SITE["x"]}']
    if SITE.get('linkedin'):
        same_as.append(SITE['linkedin'])
    ld = jsonld({'@context': 'https://schema.org', '@type': 'Person', 'name': SITE['author'], 'url': URL + '/',
                 'image': URL + '/assets/og.png', 'description': SITE['description'], 'sameAs': same_as})
    page = head(f"{SITE['name']} | Cloud Engineer Portfolio", SITE['description'], '/', extra=ld, preload_portrait=True) + header() + f'''
<header class="hero" id="top">
  <div class="portrait" role="img" aria-label="Portrait of El Mehdi smiling, wearing round glasses and an olive hoodie"></div>
  <div class="title">
    <span class="iam">I AM</span>
    <h1>El Mehdi</h1>
  </div>
</header>

<main id="main">
  <div class="wrap intro" id="about">
    <p class="status"><i></i>Status: System Online // Region: Global</p>
    <p class="kicker">Cloud Engineer, in the making</p>
    <p class="lead">I'm El Mehdi, a problem-solver by trade and a cloud engineer at heart.</p>
    <div class="cols">
      <p>Drawing heavily from my background in customer service, I've mastered the art of staying composed during high-pressure situations, asking the right analytical questions, and delivering reliable, user-centric solutions.</p>
      <p>That same mindset is now what drives my transition into tech. Good engineering, I believe, starts with understanding people, and that's something I've been doing for years.</p>
    </div>
    <a class="btn" href="#contact">Get in touch</a>
  </div>

  <section id="learning">
    <div class="wrap">
      <h2 class="section-title reveal">What I'm learning</h2>
      <div class="learn">
        <div class="reveal" style="--d:0ms"><h3>Linux</h3><p>Getting comfortable on the command line and learning how the operating system underneath everything works.</p></div>
        <div class="reveal" style="--d:110ms"><h3>Bash</h3><p>Scripting and automating the daily workflow, from small helpers to setup scripts.</p></div>
        <div class="reveal" style="--d:220ms"><h3>Networking</h3><p>Understanding how systems talk to each other, and the infrastructure that follows from it.</p></div>
      </div>
      <p class="roadmap reveal">I'm building this foundation through the <a href="https://learntocloud.guide/" target="_blank" rel="noopener">Learn to Cloud</a> roadmap by <a href="https://x.com/madebygps" target="_blank" rel="noopener">@madebygps</a>. Rather than just skimming the surface, I'm mastering the fundamentals from the ground up. The destination is clear: a career as a Cloud Engineer.</p>
      {roadmap_html()}
    </div>
  </section>
{projects_html()}
  <section class="band" id="logs">
    <div class="wrap">
      <h2 class="section-title reveal">System logs</h2>
      {latest}
      <p class="all-logs reveal"><a href="/blogs/">/all_logs</a></p>
    </div>
  </section>

  <section class="hello" id="contact">
    <div class="wrap">
      <h2 class="section-title reveal">Say hello</h2>
      <p class="reveal">I'm learning in public and always happy to talk about cloud, Linux or the road into tech.</p>
      <div class="cta reveal" style="--d:120ms">
        {chr(10).join("        " + b for b in buttons).strip()}
      </div>
    </div>
  </section>
</main>

''' + footer()
    write('index.html', page)


def build_logs_index(logs):
    cards = '\n  '.join(entry_card(l) for l in logs)
    page = head(f"{SITE['name']} | Logs", f"Technical logs and notes by {SITE['author']}.", '/blogs/') + header('logs') + f'''
<main class="page" id="main">
  <div class="page-head">
    <p class="kicker">System log // Entries</p>
    <h1>Technical archive</h1>
  </div>
  {cards}
  <p class="feed-link"><a href="/blogs/feed.xml">/rss_feed</a></p>
</main>

''' + footer()
    write('blogs/index.html', page)


def build_404():
    page = head(f"{SITE['name']} | Page not found", 'This page does not exist.', '/404.html') + header() + '''
<main class="wrap not-found" id="main">
  <p class="code">404</p>
  <p>That page isn't here. It may have moved, or the link may have a typo.</p>
  <a class="btn fill" href="/">Back to home</a>
</main>

''' + footer()
    write('404.html', page)


def build_feed(logs):
    updated = (logs[0]['date'] if logs else f"{SITE['year']}-01-01") + 'T00:00:00Z'
    entries = ''.join(f'''  <entry>
    <title>{E(l['title'])}</title>
    <link href="{URL}/blogs/{l['slug']}/"/>
    <id>{URL}/blogs/{l['slug']}/</id>
    <published>{l['date']}T00:00:00Z</published>
    <updated>{l['date']}T00:00:00Z</updated>
    <summary>{E(l['summary'])}</summary>
  </entry>
''' for l in logs)
    write('blogs/feed.xml', f'''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{E(SITE['name'])} logs</title>
  <subtitle>Technical logs and notes by {E(SITE['author'])}.</subtitle>
  <link href="{URL}/blogs/feed.xml" rel="self"/>
  <link href="{URL}/blogs/"/>
  <id>{URL}/blogs/</id>
  <updated>{updated}</updated>
  <author><name>{E(SITE['author'])}</name></author>
{entries}</feed>
''')


def build_sitemap(logs):
    urls = [(URL + '/', logs[0]['date'] if logs else None), (URL + '/blogs/', logs[0]['date'] if logs else None)]
    urls += [(f"{URL}/blogs/{l['slug']}/", l['date']) for l in logs]
    rows = ''.join(f'  <url><loc>{u}</loc>' + (f'<lastmod>{d}</lastmod>' if d else '') + '</url>\n' for u, d in urls)
    write('sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n')


def main():
    logs = load_logs()
    print(f'Building {SITE["name"]} with {len(logs)} log(s)')
    build_home(logs)
    build_logs_index(logs)
    for log in logs:
        build_log(log)
    build_404()
    build_feed(logs)
    build_sitemap(logs)
    print('Done.')


if __name__ == '__main__':
    main()

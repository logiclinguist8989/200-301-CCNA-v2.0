#!/usr/bin/env python3
"""Build the CCNA 200-301 v2.0 study website (GitHub Pages) from the Markdown guides on main.

Usage:
    python3 build_site.py <repo-checkout-of-main> <output-dir>

Needs:  pip install markdown
Output: a static site (index, intro, one page per chapter, search index, assets) that GitHub Pages
        serves from the gh-pages branch as-is. Nothing here changes the guides on main.
"""

import html
import json
import re
import shutil
import sys
from pathlib import Path

import markdown

from extras import add_memory_tricks, callouts, extract_quiz, lab_it, quiz_html, terminals

GUIDE1 = "CCNA 200-301 v2.0 Study Guide.md"
GUIDE2 = "Part 2 — Chapters 24–28.md"
REPO_URL = "https://github.com/logiclinguist8989/200-301-CCNA-v2.0"

DOMAINS = [
    ("1", "Network Infrastructure & Connectivity", "25 %", [1, 2, 3, 4, 14, 16, 17], "blue"),
    ("2", "Switching & Network Access", "25 %", [5, 6, 7, 8, 9, 15], "green"),
    ("3", "IP Routing", "20 %", [10, 11, 12, 13], "amber"),
    ("4", "Network Services & Security", "20 %", [18, 19, 20, 21, 22, 23, 24], "purple"),
    ("5", "AI, Operations & Management", "10 %", [25, 26, 27], "red"),
    ("R", "Final Review", "all", [28], "teal"),
]
DOMAIN_OF = {ch: d for d in DOMAINS for ch in d[3]}


# --------------------------------------------------------------------------- splitting

def split_guides(repo: Path):
    """Return intro markdown and {chapter: (title, markdown)}."""
    t1 = (repo / GUIDE1).read_text(encoding="utf-8")
    t2 = (repo / GUIDE2).read_text(encoding="utf-8")
    first = re.search(r"^## Chapter 1 —", t1, re.M).start()
    intro = t1[:first]
    intro = re.sub(r"^# .*\n", "", intro, count=1)            # page has its own H1
    body = t1[first:] + "\n" + re.sub(r"^# .*\n(?:\n?This file continues.*\n)?", "", t2, count=1)
    chapters = {}
    marks = [(m.start(), int(m.group(1)), m.group(0)) for m in re.finditer(r"^## Chapter (\d+) — .*$", body, re.M)]
    for i, (pos, n, head) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        title = head.split("—", 1)[1].strip()
        md = body[pos:end]
        md = md.split("\n", 1)[1]                              # drop the H2; the page shows its own title
        chapters[n] = (title, md)
    return intro, chapters


# --------------------------------------------------------------------------- markdown -> html

def slugify(value, sep="-"):
    value = value.strip().lower()
    value = re.sub(r"<[^>]+>", "", value)
    value = "".join(c for c in value if c.isalnum() or c in " -_")
    return value.replace(" ", sep)


MD = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                       extension_configs={"toc": {"slugify": slugify, "toc_depth": "3-4"}})


def render(md_text):
    MD.reset()
    out = MD.convert(md_text)
    return out, MD.toc_tokens


def page_of_figure(num):
    ch = int(num.split(".")[0])
    return f"chapter-{ch:02d}.html#fig-{num.replace('.', '-')}"


def postprocess(h, this_page):
    # Figures: give each an id and a zoomable class; captions become <figcaption>-style
    def fig(m):
        src, alt, num, cap = m.group(1), m.group(2), m.group(3), m.group(4)
        fid = "fig-" + num.replace(".", "-")
        return (f'<figure class="fig" id="{fid}"><button class="zoom" aria-label="Enlarge figure {num}">'
                f'<img src="{src}" alt="{alt}" loading="lazy"></button>'
                f'<figcaption><a class="fignum" href="#{fid}">Figure {num}</a> {cap}</figcaption></figure>')
    h = re.sub(r'<p align="center">\s*<img src="([^"]+)" alt="([^"]*)" width="100%">\s*</p>\s*'
               r'<p align="center"><sub><b>Figure (\d+\.\d+)</b> — (.+?)</sub></p>', fig, h, flags=re.S)
    # Cross-links between the two Markdown files -> site pages
    h = h.replace('href="Part%202%20%E2%80%94%20Chapters%2024%E2%80%9328.md"', 'href="chapter-24.html"')
    h = re.sub(r'href="CCNA%20200-301%20v2.0%20Study%20Guide.md(#[^"]*)?"',
               lambda m: 'href="intro.html' + (m.group(1) or "") + '"', h)
    # "Figure 9.5" mentions in prose -> links (outside code, links and headings)
    parts = re.split(r"(<pre.*?</pre>|<code.*?</code>|<a .*?</a>|<h[1-6].*?</h[1-6]>|<figure.*?</figure>)", h, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"\bFigures? (\d{1,2}\.\d{1,2})\b",
                          lambda m: f'<a class="figref" href="{local(page_of_figure(m.group(1)), this_page)}">{m.group(0)}</a>',
                          parts[i])
    h = "".join(parts)
    # Callouts for the guide's recurring labels, and terminal-style CLI blocks
    h = callouts(h)
    h = terminals(h)
    # Wide tables scroll on small screens
    h = h.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return h


def local(target, this_page):
    page, _, frag = target.partition("#")
    return f"#{frag}" if page == this_page else target


# --------------------------------------------------------------------------- search index

def text_sections(h, page, title):
    """Split rendered HTML at h3 headings into searchable sections."""
    out = []
    chunks = re.split(r'(<h3 id="[^"]+">.*?</h3>)', h, flags=re.S)
    current = ("", title)
    buf = chunks[0]
    def flush(anchor, head, buf):
        txt = html.unescape(re.sub(r"<[^>]+>", " ", buf))
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            out.append({"p": page + (f"#{anchor}" if anchor else ""), "t": head, "c": title, "x": txt[:4000]})
    for i in range(1, len(chunks), 2):
        flush(*current, buf)
        m = re.match(r'<h3 id="([^"]+)">(.*?)</h3>', chunks[i], re.S)
        current = (m.group(1), html.unescape(re.sub(r"<[^>]+>", "", m.group(2))))
        buf = chunks[i + 1]
    flush(*current, buf)
    return out


# --------------------------------------------------------------------------- templates

def sidebar(chapters, active):
    rows = [f'<a class="nav-home{" active" if active == "index.html" else ""}" href="index.html">🏠 Home</a>',
            f'<a class="{"active" if active == "intro.html" else ""}" href="intro.html">📘 Start here · Part 0</a>',
            f'<a class="{"active" if active == "practice.html" else ""}" href="practice.html">🎯 Subnetting practice</a>']
    for num, name, weight, chs, col in DOMAINS:
        label = f"Domain {num} · {name}" if num != "R" else name
        rows.append(f'<div class="nav-group {col}"><span>{html.escape(label)}</span>')
        for ch in chs:
            page = f"chapter-{ch:02d}.html"
            t = html.escape(chapters[ch][0])
            rows.append(f'<a class="ch{" active" if active == page else ""}" href="{page}" data-ch="{ch}">'
                        f'<span class="chn">{ch}</span><span class="cht">{t}</span><span class="done" aria-hidden="true">✓</span></a>')
        rows.append("</div>")
    return "\n".join(rows)


def page_toc(tokens):
    items = []
    def walk(ts):
        for t in ts:
            if t["level"] == 3:
                items.append(f'<a href="#{t["id"]}">{html.escape(html.unescape(t["name"]))}</a>')
            walk(t.get("children", []))
    walk(tokens)
    return "\n".join(items)


def shell(title, body, chapters, active, toc="", desc="CCNA 200-301 v2.0 study guide and lab manual"):
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · CCNA 200-301 v2.0 Study Guide</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="icon" href="assets/site/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site/style.css">
<script>try{{const t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head><body>
<header class="topbar">
  <button class="menu" aria-label="Open chapter menu">☰</button>
  <a class="brand" href="index.html"><span class="logo">CCNA</span><span>200-301 v2.0 Study Guide</span></a>
  <div class="search"><input id="q" type="search" placeholder="Search the guide…  ( / )" autocomplete="off" aria-label="Search the guide"><div id="results" role="listbox"></div></div>
  <button class="theme" aria-label="Toggle dark mode">◐</button>
  <a class="gh" href="{REPO_URL}" aria-label="Source on GitHub">GitHub</a>
</header>
<aside class="sidebar"><div class="progress"><div class="bar"><i></i></div><span></span></div><nav>{sidebar(chapters, active)}</nav></aside>
<main class="content">{body}</main>
{f'<aside class="toc"><div class="toc-title">On this page</div>{toc}</aside>' if toc else ''}
<div class="lightbox" hidden><img alt=""><button aria-label="Close">✕</button></div>
<script src="assets/site/app.js"></script>
</body></html>
"""


def chapter_page(n, title, h, chapters, nq=0):
    num, dname, weight, chs, col = DOMAIN_OF[n]
    prev_l = f'<a class="pn prev" href="chapter-{n - 1:02d}.html"><small>← Chapter {n - 1}</small>{html.escape(chapters[n - 1][0])}</a>' if n > 1 else '<a class="pn prev" href="intro.html"><small>← Start here</small>Part 0</a>'
    next_l = f'<a class="pn next" href="chapter-{n + 1:02d}.html"><small>Chapter {n + 1} →</small>{html.escape(chapters[n + 1][0])}</a>' if n < 28 else '<a class="pn next" href="index.html"><small>Finished →</small>Back to home</a>'
    figs = len(re.findall(r'<figure class="fig"', h))
    label = f"Domain {num} · {dname}" if num != "R" else dname
    head = f"""<div class="chapter-head {col}">
  <div class="eyebrow">{html.escape(label)}</div>
  <h1><span class="num">Chapter {n}</span>{html.escape(title)}</h1>
  <div class="meta"><span>🖼️ {figs} figure{'s' if figs != 1 else ''}</span><span>⏱️ ~{max(5, round(len(re.sub('<[^>]+>', '', h).split()) / 220))} min read</span>{f'<a class="qmeta" href="#quiz" data-ch="{n}" data-total="{nq}">📝 Self-check: {nq} questions</a>' if nq else ''}
  <label class="mark"><input type="checkbox" data-ch="{n}"> Mark chapter as done</label></div>
</div>"""
    return head + f'<article class="prose">{h}</article><nav class="prevnext">{prev_l}{next_l}</nav>'


def home_page(chapters, figcount, quizcount):
    cards = []
    for num, name, weight, chs, col in DOMAINS:
        label = f"Domain {num}" if num != "R" else "Review"
        items = []
        for ch in chs:
            t, _ = chapters[ch]
            items.append(f'<a class="card" href="chapter-{ch:02d}.html" data-ch="{ch}"><span class="cn">{ch}</span>'
                         f'<span class="ct">{html.escape(t)}</span><span class="done" aria-hidden="true">✓</span></a>')
        cards.append(f'<section class="domain {col}"><header><span class="dl">{label}</span><h3>{html.escape(name)}</h3>'
                     f'<span class="w">{weight if num != "R" else ""}</span></header><div class="cards">{"".join(items)}</div></section>')
    return f"""
<section class="hero">
  <div class="hero-text">
    <div class="eyebrow">Free · open · hands-on</div>
    <h1>Pass the <span class="hl">CCNA 200-301 v2.0</span> by building one network, chapter by chapter.</h1>
    <p>28 chapters mapped to every v2.0 exam objective, Packet Tracer labs on a single growing campus, practice questions with full answers — and {figcount} hand-built diagrams that show how it really works.</p>
    <div class="cta"><a class="btn primary" href="intro.html">Start studying →</a><a class="btn" href="chapter-01.html">Jump to Chapter 1</a></div>
    <div class="stats"><div><b>28</b><span>chapters</span></div><div><b>{figcount}</b><span>figures</span></div><div><b>{quizcount}</b><span>quiz questions</span></div><div><b>5</b><span>exam domains</span></div></div>
  </div>
  <figure class="hero-fig"><button class="zoom" aria-label="Enlarge the campus diagram"><img src="assets/figures/ch28/fig-28-01-final-campus-lab.svg" alt="The finished campus lab"></button><figcaption>The campus you will have built by Chapter 28</figcaption></figure>
</section>
<section class="progress-card"><div><b>Your progress</b><span class="ptext"></span></div><div class="bar"><i></i></div><p>Tick “Mark chapter as done” at the top of each chapter. Progress is saved in this browser only.</p></section>
<section class="tools">
  <a class="tool" href="chapter-01.html#quiz"><span class="ti">📝</span><b>Self-check quizzes</b><span>{quizcount} questions at the end of every chapter. Click an answer, see why, keep your score.</span></a>
  <a class="tool" href="practice.html"><span class="ti">🎯</span><b>Subnetting practice</b><span>Endless random addresses. Find the network, broadcast and host range — and build a streak.</span></a>
  <a class="tool" href="chapter-01.html#1a3-the-osi-and-tcpip-models"><span class="ti">🧠</span><b>Exam tips &amp; memory tricks</b><span>Colour-coded boxes for exam tips, common traps, memory tricks and “Lab it” pointers.</span></a>
  <a class="tool" href="chapter-12.html"><span class="ti">⌨️</span><b>Real CLI feel</b><span>IOS commands shown in a router console, with one-click “Copy commands”.</span></a>
</section>
<section class="domains-art"><img src="assets/readme/ccna-domains.svg" alt="The five exam domains and the chapters that cover them"></section>
{''.join(cards)}
<section class="about">
  <div><h3>🤖 How this guide was made</h3><p>All content, labs and figures were generated by Claude (Anthropic) from the official Cisco CCNA 200-301 v2.0 exam topics, directed and reviewed by Ayush Hamal. Verify commands against Cisco documentation and run every lab yourself.</p></div>
  <div><h3>📄 License</h3><p>Guide and figures: <a href="{REPO_URL}/blob/main/LICENSE-CONTENT">CC BY-NC-SA 4.0</a> · tools: <a href="{REPO_URL}/blob/main/LICENSE-CODE">MIT</a>. Cisco, CCNA and Packet Tracer are trademarks of Cisco Systems, Inc.; this is an independent resource.</p></div>
  <div><h3>🛠️ Found a mistake?</h3><p>Open an <a href="{REPO_URL}/issues">issue</a> or a pull request on <a href="{REPO_URL}">GitHub</a>.</p></div>
</section>
"""


def practice_page():
    return """<div class="chapter-head blue"><div class="eyebrow">Practice tool · Chapter 2 skill</div>
<h1><span class="num">Practice</span>Subnetting practice</h1>
<div class="meta"><span>🎯 Unlimited random questions</span><span>⌨️ Press Enter to check, Enter again for the next one</span>
<a class="qmeta" href="chapter-02.html#26-calculating-network-broadcast-and-host-range">📘 Review the method in 2.6</a></div></div>
<section class="sn" id="sn">
  <div class="sn-top">
    <div class="sn-levels" role="radiogroup" aria-label="Difficulty">
      <button type="button" data-level="easy" class="on">Easy <small>/24 – /30</small></button>
      <button type="button" data-level="medium">Medium <small>/16 – /30</small></button>
      <button type="button" data-level="hard">Hard <small>/8 – /30</small></button>
    </div>
    <div class="sn-stats"><div><b class="st-streak">0</b><span>streak 🔥</span></div><div><b class="st-best">0</b><span>best streak</span></div><div><b class="st-total">0</b><span>solved</span></div></div>
  </div>
  <div class="sn-q"><small>Find the subnet for this host</small><div class="sn-addr"></div><div class="sn-mask"></div></div>
  <form class="sn-form" autocomplete="off">
    <label>Network address<input name="net" inputmode="decimal" placeholder="e.g. 192.168.1.0"></label>
    <label>Broadcast address<input name="bc" inputmode="decimal" placeholder="e.g. 192.168.1.63"></label>
    <label>First usable host<input name="first" inputmode="decimal"></label>
    <label>Last usable host<input name="last" inputmode="decimal"></label>
    <label>Usable hosts<input name="hosts" inputmode="numeric"></label>
    <div class="sn-buttons"><button class="btn primary" type="submit">Check</button><button class="btn sn-show" type="button">Show solution</button><button class="btn sn-next" type="button">Next address →</button></div>
  </form>
  <div class="sn-result" hidden></div>
  <p class="callout memory-trick"><strong>Memory trick</strong><b>Magic number = 256 − the interesting octet of the mask.</b> Find the octet where the mask is not 255 or 0, list the multiples of the magic number in that octet, and the host's subnet starts at the multiple just below it. The broadcast is the next subnet minus one.</p>
</section>
"""


# --------------------------------------------------------------------------- main

def main(repo, out):
    repo, out = Path(repo), Path(out)
    if out.exists():
        for p in out.iterdir():
            if p.name in (".git", "_generator"):
                continue
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    out.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    intro_md, chapters = split_guides(repo)
    assert sorted(chapters) == list(range(1, 29)), sorted(chapters)

    search = []
    # intro
    h, toks = render(intro_md)
    h = postprocess(h, "intro.html")
    body = ('<div class="chapter-head teal"><div class="eyebrow">Start here</div><h1><span class="num">Part 0</span>'
            'How to use this guide</h1></div>' + f'<article class="prose">{h}</article>'
            '<nav class="prevnext"><a class="pn prev" href="index.html"><small>← Home</small>Overview</a>'
            f'<a class="pn next" href="chapter-01.html"><small>Chapter 1 →</small>{html.escape(chapters[1][0])}</a></nav>')
    (out / "intro.html").write_text(shell("Start here", body, chapters, "intro.html", page_toc(toks)), encoding="utf-8")
    search += text_sections(h, "intro.html", "Part 0 · Start here")
    # chapters
    figcount = quizcount = 0
    for n in range(1, 29):
        title, md = chapters[n]
        md, quiz = extract_quiz(add_memory_tricks(md, n))
        h, toks = render(md)
        page = f"chapter-{n:02d}.html"
        if quiz:
            h = h.replace("<div>QUIZ-PLACEHOLDER</div>", '<div id="quiz"></div>' + quiz_html(n, quiz))
            quizcount += len(quiz["qs"])
        h = lab_it(postprocess(h, page), n)
        figcount += len(re.findall(r'<figure class="fig"', h))
        (out / page).write_text(shell(f"Chapter {n} — {title}", chapter_page(n, title, h, chapters, len(quiz["qs"]) if quiz else 0), chapters, page,
                                      page_toc(toks), desc=f"CCNA 200-301 v2.0 — Chapter {n}: {title}"), encoding="utf-8")
        search += text_sections(h, page, f"Chapter {n} · {title}")
    # home, practice + 404
    (out / "index.html").write_text(shell("Home", home_page(chapters, figcount, quizcount), chapters, "index.html"), encoding="utf-8")
    (out / "practice.html").write_text(shell("Subnetting practice", practice_page(), chapters, "practice.html",
                                             desc="Unlimited IPv4 subnetting practice for the CCNA 200-301 v2.0"), encoding="utf-8")
    (out / "404.html").write_text(shell("Not found", '<div class="chapter-head teal"><h1><span class="num">404</span>Page not found</h1></div>'
                                       '<p class="prose">That page does not exist. <a href="index.html">Go to the home page</a>.</p>', chapters, ""), encoding="utf-8")
    # assets
    shutil.copytree(repo / "assets" / "figures", out / "assets" / "figures")
    shutil.copytree(repo / "assets" / "readme", out / "assets" / "readme")
    shutil.copytree(here / "static", out / "assets" / "site")
    (out / "assets" / "site" / "search.json").write_text(json.dumps(search, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (out / ".nojekyll").write_text("")
    print(f"Built {len(chapters) + 4} pages, {figcount} figures, {quizcount} quiz questions, {len(search)} search sections -> {out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

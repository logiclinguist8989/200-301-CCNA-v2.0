# Study website generator

This branch (`gh-pages`) is the published website for the
[CCNA 200-301 v2.0 Study Guide](https://github.com/logiclinguist8989/200-301-CCNA-v2.0).
Everything outside this folder is generated — do not edit it by hand.

The site is built from the Markdown guides on `main`: a landing page, a "Start here" page, one page per
chapter, a chapter sidebar grouped by exam domain, full-text search, dark/light mode, per-chapter
progress tracking (saved in the reader's browser), and click-to-zoom figures.

## Rebuild after changing `main`

```bash
pip install markdown
git clone https://github.com/logiclinguist8989/200-301-CCNA-v2.0.git ccna
cd ccna && git worktree add ../site gh-pages
python3 ../site/_generator/build_site.py . ../site
cd ../site && git add -A && git commit -m "site: rebuild from main" && git push
```

`build_site.py` keeps `_generator/` and `.git` and replaces everything else.

| File | Purpose |
| --- | --- |
| `build_site.py` | Splits the guides into pages and renders them (Python + `markdown`) |
| `static/style.css` | Layout, colours, dark mode, callouts, responsive design |
| `static/app.js` | Search, theme toggle, progress tracking, figure zoom, "on this page" highlighting |
| `static/favicon.svg` | Site icon |

Licensed like the rest of the repository: generated pages and figures under CC BY-NC-SA 4.0, the
generator code under MIT (see `LICENSE`, `LICENSE-CONTENT` and `LICENSE-CODE` on `main`).

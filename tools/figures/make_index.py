#!/usr/bin/env python3
"""Write docs/FIGURES.md: a browsable index of every figure, grouped by chapter,
with its caption and a link to the section of the guide that uses it."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GUIDES = ["CCNA 200-301 v2.0 Study Guide.md", "Part 2 — Chapters 24–28.md"]
CAPTION = re.compile(r'<img src="(assets/figures/[^"]+)" alt="[^"]*" width="100%">\n</p>\n'
                     r'<p align="center"><sub><b>Figure (\d+\.\d+)</b> — (.+?)</sub></p>')
CHAPTER = re.compile(r"^## (Chapter (\d+)[^\n]*)$", re.M)


def slug(heading: str) -> str:
    """GitHub-style heading anchor."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def url_path(name: str) -> str:
    return name.replace(" ", "%20").replace("—", "%E2%80%94").replace("–", "%E2%80%93")


def main():
    chapters = {}
    for guide in GUIDES:
        text = (ROOT / guide).read_text(encoding="utf-8")
        heads = [(m.start(), m.group(1), int(m.group(2))) for m in CHAPTER.finditer(text)]
        for m in CAPTION.finditer(text):
            src, num, cap = m.group(1), m.group(2), m.group(3)
            head = [h for h in heads if h[0] < m.start()][-1]
            ch = chapters.setdefault(head[2], {"title": head[1], "guide": guide, "figs": []})
            ch["figs"].append((num, cap, src))
    total = sum(len(c["figs"]) for c in chapters.values())
    out = ["# Figure index", "",
           f"All **{total} figures** in the study guide, grouped by chapter. Every figure is a scalable SVG generated",
           "from code in [`tools/figures`](../tools/figures) — see the [README](../README.md#%EF%B8%8F-figures) for how to rebuild them.", ""]
    out.append("| Chapter | Figures |")
    out.append("| --- | --- |")
    for n in sorted(chapters):
        c = chapters[n]
        out.append(f"| [{c['title']}](#{slug(c['title'])}) | {len(c['figs'])} |")
    out.append("")
    for n in sorted(chapters):
        c = chapters[n]
        out += [f"## {c['title']}", "",
                f"Source: [`{c['guide']}`](../{url_path(c['guide'])}#{slug(c['title'])})", "",
                "| Figure | Caption | Preview |", "| --- | --- | --- |"]
        for num, cap, src in c["figs"]:
            out.append(f"| **{num}** | {cap} | <a href=\"../{src}\"><img src=\"../{src}\" width=\"260\" alt=\"Figure {num}\"></a> |")
        out.append("")
    dest = ROOT / "docs" / "FIGURES.md"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {dest.relative_to(ROOT)} ({total} figures, {len(chapters)} chapters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

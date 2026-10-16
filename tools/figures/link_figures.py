#!/usr/bin/env python3
"""Replace '[embedded content: Figure X.Y — caption]' placeholders in the guides
with the generated SVG figure and its caption. Safe to re-run: placeholders whose
figure has not been built yet are left untouched."""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build import load_chapters  # noqa: E402
from registry import FIGURES, filename  # noqa: E402

ROOT = HERE.parent.parent
GUIDES = ["CCNA 200-301 v2.0 Study Guide.md", "Part 2 — Chapters 24–28.md"]
PLACEHOLDER = re.compile(r"&#91;embedded content: Figure (\d+\.\d+) — (.+?)\\\]")


def block(number, caption):
    slug, _ = FIGURES[number]
    src = f"assets/figures/{filename(number, slug)}"
    alt = f"Figure {number} — {caption}".replace('"', "&quot;")
    return (f'<p align="center">\n  <img src="{src}" alt="{alt}" width="100%">\n</p>\n'
            f'<p align="center"><sub><b>Figure {number}</b> — {caption}</sub></p>')


def main():
    load_chapters()
    total = 0
    for name in GUIDES:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        count = 0

        def sub(m):
            nonlocal count
            number, caption = m.group(1), m.group(2)
            if number not in FIGURES or not (ROOT / "assets/figures" / filename(number, FIGURES[number][0])).exists():
                return m.group(0)
            count += 1
            return block(number, caption)

        text = PLACEHOLDER.sub(sub, text)
        path.write_text(text, encoding="utf-8")
        left = len(PLACEHOLDER.findall(text))
        print(f"{name}: linked {count} figure(s), {left} placeholder(s) remaining")
        total += count
    print(f"{total} figure(s) linked.")


if __name__ == "__main__":
    main()

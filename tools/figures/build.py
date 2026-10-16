#!/usr/bin/env python3
"""Generate every study-guide figure as SVG into assets/figures/.

Usage:
    python3 tools/figures/build.py              # build all figures
    python3 tools/figures/build.py 5.3 9.5      # build selected figures
    python3 tools/figures/build.py --png DIR    # also write PNG previews (needs cairosvg)
"""

import importlib
import pkgutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from registry import FIGURES, filename, sort_key  # noqa: E402

ROOT = HERE.parent.parent
OUT = ROOT / "assets" / "figures"


def load_chapters():
    import chapters
    for mod in pkgutil.iter_modules(chapters.__path__):
        importlib.import_module(f"chapters.{mod.name}")


def main(argv):
    png_dir = None
    if "--png" in argv:
        i = argv.index("--png")
        png_dir = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    load_chapters()
    wanted = argv or sorted(FIGURES, key=sort_key)
    for number in wanted:
        slug, fn = FIGURES[number]
        canvas = fn()
        path = OUT / filename(number, slug)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(canvas.svg(), encoding="utf-8")
        if png_dir:
            import cairosvg
            png_dir.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(url=str(path), write_to=str(png_dir / (path.stem + ".png")), scale=1.0)
        print(f"Figure {number:>5}  ->  {path.relative_to(ROOT)}")
    print(f"{len(wanted)} figure(s) built.")
    if not argv:
        import readme_art
        readme_art.main()


if __name__ == "__main__":
    main(sys.argv[1:])

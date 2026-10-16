#!/usr/bin/env python3
"""Fail if any Markdown file references a local image or file that does not exist,
or if a figure placeholder is left unconverted."""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r'(?:src="|\]\()([^"\)\s#]+)')


def main():
    errors = 0
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        if "&#91;embedded content:" in text:
            print(f"{md.relative_to(ROOT)}: unconverted figure placeholder")
            errors += 1
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path = (md.parent / unquote(target)).resolve()
            if not path.exists():
                print(f"{md.relative_to(ROOT)}: missing {target}")
                errors += 1
    print("link check:", "OK" if not errors else f"{errors} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

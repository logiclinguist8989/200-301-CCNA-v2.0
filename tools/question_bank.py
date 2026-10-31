#!/usr/bin/env python3
"""Parse and validate the CCNA-style question bank in question-bank/chNN.md.

Usage:
    python3 tools/question_bank.py            # validate every chapter file and print a summary
    python3 tools/question_bank.py --json     # print the parsed bank as JSON
    python3 tools/question_bank.py question-bank/ch05.md   # validate one file

The file format is described in question-bank/README.md. The study website imports parse_bank()
from this module, so the Markdown files are the single source of truth.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "question-bank"
TYPES = {"multiple choice": "mc", "drag and drop — order": "order", "drag and drop — match": "match", "cli": "cli"}


class BankError(Exception):
    pass


def _blockquote(lines):
    return "\n".join(re.sub(r"^>\s?", "", l) for l in lines)


def _parse_question(ch, head, body, testlet, path):
    m = re.match(r"### Q(\d+) · (.+?)\s*$", head)
    if not m:
        raise BankError(f"{path.name}: bad question heading: {head!r}")
    n, kind_text = int(m.group(1)), m.group(2).strip()
    base = re.sub(r"\s*—\s*choose \w+$", "", kind_text.lower())
    if base not in TYPES:
        raise BankError(f"{path.name} Q{n}: unknown question type {kind_text!r}")
    q = {"id": f"c{ch}-{n}", "ch": ch, "n": n, "type": TYPES[base], "kind": kind_text, "testlet": testlet}

    lines = body.strip("\n").split("\n")
    src = next((l for l in lines if l.startswith("<sub>Source:")), None)
    if not src:
        raise BankError(f"{path.name} Q{n}: missing '<sub>Source: …</sub>' line")
    q["source"] = re.sub(r"</?sub>|Source:\s*", "", src).strip()
    lines.remove(src)

    exp_start = next((i for i, l in enumerate(lines) if l.startswith("> **Explanation:**")), None)
    if exp_start is None:
        raise BankError(f"{path.name} Q{n}: missing '> **Explanation:**' block")
    q["explanation"] = _blockquote(lines[exp_start:]).replace("**Explanation:**", "", 1).strip()
    lines = lines[:exp_start]
    text = "\n".join(lines).strip()

    if q["type"] == "mc":
        opts = [(l[6:].strip(), l[3] == "x") for l in lines if re.match(r"- \[[ x]\] ", l)]
        if len(opts) < 3:
            raise BankError(f"{path.name} Q{n}: a multiple-choice question needs at least 3 options")
        k = sum(c for _, c in opts)
        want = {"choose two": 2, "choose three": 3}.get(kind_text.lower().split("— ")[-1], 1)
        if k != want:
            raise BankError(f"{path.name} Q{n}: {k} correct options marked, heading expects {want}")
        q["options"] = opts
        q["stem"] = re.sub(r"(?m)^- \[[ x]\] .*\n?", "", text).strip()
    elif q["type"] == "order":
        items = [re.sub(r"^\d+\.\s+", "", l).strip() for l in lines if re.match(r"\d+\.\s+", l)]
        if len(items) < 3:
            raise BankError(f"{path.name} Q{n}: an order question needs at least 3 numbered items")
        q["order"] = items
        q["stem"] = re.sub(r"(?m)^\d+\.\s+.*\n?", "", text).strip()
    elif q["type"] == "match":
        rows = [l for l in lines if l.startswith("|")]
        if len(rows) < 4:
            raise BankError(f"{path.name} Q{n}: a match question needs a table with at least 2 rows")
        pairs = [tuple(c.strip() for c in r.strip("|").split("|")) for r in rows[2:]]
        extra = next((l for l in lines if l.startswith("**Extra targets:**")), "")
        extras = [e.strip(" `") for e in extra.replace("**Extra targets:**", "").split("·") if e.strip()]
        targets = list(dict.fromkeys([t for _, t in pairs] + extras))
        q["pairs"], q["targets"] = pairs, targets
        q["stem"] = "\n".join(l for l in lines if not l.startswith("|") and l != extra).strip()
    else:  # cli
        prompt = next((l for l in lines if l.startswith("**Prompt:**")), None)
        acc = next((l for l in lines if l.startswith("**Accepted:**")), None)
        if not prompt or not acc:
            raise BankError(f"{path.name} Q{n}: a CLI question needs '**Prompt:**' and '**Accepted:**' lines")
        q["prompt"] = prompt.replace("**Prompt:**", "").strip().strip("`")
        q["accepted"] = re.findall(r"`([^`]+)`", acc)
        if not q["accepted"]:
            raise BankError(f"{path.name} Q{n}: no accepted command in backticks")
        q["stem"] = "\n".join(l for l in lines if l not in (prompt, acc)).strip()
    if not q["stem"]:
        raise BankError(f"{path.name} Q{n}: empty question text")
    return q


def parse_file(path):
    ch = int(re.search(r"ch(\d+)\.md$", path.name).group(1))
    text = path.read_text(encoding="utf-8")
    questions, testlets, seen = [], {}, set()
    sections = re.split(r"(?m)^(## .*)$", text)
    for i in range(1, len(sections), 2):
        head, body = sections[i].strip(), sections[i + 1]
        testlet = None
        tm = re.match(r"## Testlet (\w+) · (.+)$", head)
        parts = re.split(r"(?m)^(### Q\d+ · .*)$", body)
        if tm:
            testlet = f"c{ch}-T{tm.group(1)}"
            testlets[testlet] = {"title": tm.group(2).strip(), "scenario": parts[0].strip()}
        for j in range(1, len(parts), 2):
            q = _parse_question(ch, parts[j], re.split(r"(?m)^---\s*$", parts[j + 1])[0], testlet, path)
            if q["n"] in seen:
                raise BankError(f"{path.name}: duplicate question number Q{q['n']}")
            seen.add(q["n"])
            questions.append(q)
    return questions, testlets


def parse_bank(bank_dir=BANK):
    questions, testlets = [], {}
    for path in sorted(Path(bank_dir).glob("ch[0-9][0-9].md")):
        q, t = parse_file(path)
        questions += q
        testlets.update(t)
    return questions, testlets


def main():
    files = [a for a in sys.argv[1:] if a.endswith(".md")]
    if files:
        for f in files:
            try:
                q, t = parse_file(Path(f))
            except BankError as e:
                sys.exit(f"question bank: {e}")
            kinds = {}
            for x in q:
                kinds[x["type"]] = kinds.get(x["type"], 0) + 1
            print(f"{Path(f).name}: OK — {len(q)} questions, {len(t)} testlet(s); " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())))
        return
    try:
        questions, testlets = parse_bank()
    except BankError as e:
        sys.exit(f"question bank: {e}")
    if "--json" in sys.argv:
        print(json.dumps({"questions": questions, "testlets": testlets}, ensure_ascii=False, indent=1))
        return
    by_type, by_ch = {}, {}
    for q in questions:
        by_type[q["type"]] = by_type.get(q["type"], 0) + 1
        by_ch[q["ch"]] = by_ch.get(q["ch"], 0) + 1
    print(f"question bank: OK — {len(questions)} questions, {len(testlets)} testlets, {len(by_ch)} chapters")
    print("  by type:    " + ", ".join(f"{k} {v}" for k, v in sorted(by_type.items())))
    print("  by chapter: " + ", ".join(f"{k}:{v}" for k, v in sorted(by_ch.items())))


if __name__ == "__main__":
    main()

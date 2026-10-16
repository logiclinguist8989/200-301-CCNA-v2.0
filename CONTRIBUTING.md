# Contributing

Thank you for helping improve the CCNA 200-301 v2.0 Study Guide. Corrections, clearer explanations and better figures are all welcome.

## Reporting a problem

Open an issue with:

- the chapter and section number (for example **5.5**) or the figure number (for example **Figure 9.5**);
- what is wrong and, if you can, a source (Cisco documentation, an RFC, or device output);
- for lab problems, the Packet Tracer version you used.

## Making a change

1. Fork the repository and create a branch: `git checkout -b fix/ch12-dr-election`.
2. Make your edit in the guide (`CCNA 200-301 v2.0 Study Guide.md` or `Part 2 — Chapters 24–28.md`).
3. If you change a figure, edit its function in `tools/figures/chapters/` and rebuild (see below).
4. Run the checks, commit with a clear message, and open a pull request.

### Commit messages

Use a short type prefix and an imperative summary, for example:

```
docs(ch12): correct DR election tie-break order
fix(figures): move label off the trunk line in Figure 6.4
build(figures): add a firewall icon to svgkit
```

## Working with figures

Figures are generated SVG files — never edit the files in `assets/figures/` by hand.

```bash
python3 tools/figures/build.py 6.4          # rebuild one figure
python3 tools/figures/build.py              # rebuild all
python3 tools/figures/link_figures.py       # embed new figures in the guides
python3 tools/figures/make_index.py         # refresh docs/FIGURES.md
python3 tools/check_links.py                # verify links and images
```

Optional PNG previews for reviewing layout: `pip install cairosvg`, then `python3 tools/figures/build.py --png /tmp/previews`.

Style rules for new figures:

- Use the shared palette, device icons and helpers in `tools/figures/svgkit.py`; keep one figure card style.
- Number figures by chapter (`Figure 12.3`) and register them with `@figure("12.3", "short-slug")`.
- Use the guide's unified addressing plan (VLANs 10/30/40/99, `10.10.VLAN.0/24`, RFC 5737 / 3849 documentation ranges).
- Check that labels never cross lines or other labels, and that the figure matches the text and tables beside it.
- Never include real passwords, keys or production addresses.

## Content conventions

- Cisco IOS commands in code blocks, with the prompt (`R1(config-if)#`) when the mode matters.
- Keep spelling consistent within a chapter (the guide mixes British and American spelling, e.g. "organisation" and "neighbor"); keep protocol and command terms exactly as Cisco writes them.
- Each chapter keeps its structure: objectives, explanation, configuration, verification, troubleshooting, lab, questions, answers, figure checklist, progress record.

## License of contributions

By contributing, you agree that your changes to the guides, docs and figures are licensed under
[CC BY-NC-SA 4.0](LICENSE-CONTENT), and your changes to code in `tools/` and `.github/` under the
[MIT License](LICENSE-CODE), as described in [LICENSE](LICENSE).

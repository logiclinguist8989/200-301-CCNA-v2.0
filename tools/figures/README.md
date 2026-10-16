# Figure generator

Every figure in the guide is produced by this small, dependency-free Python package, so the artwork stays
consistent (one palette, one icon set, one typography scale) and any figure can be fixed in one place.

| File | Purpose |
| --- | --- |
| `svgkit.py` | Canvas (figure card with badge, title, subtitle, footer), shapes, packet/frame strips, flowchart and sequence-diagram helpers, and vector device icons in the style of the Cisco topology icon set: router, switch, multilayer switch, PC, laptop, server, firewall, access point, WLC, IP phone, printer, camera, cloud, hypervisor host, controller, database, AI agent |
| `registry.py` | `@figure("9.5", "slug")` decorator and output file naming |
| `chapters/*.py` | The figures themselves, one module per chapter group |
| `build.py` | Renders figures to `assets/figures/chNN/fig-NN-MM-slug.svg` (`--png DIR` adds PNG previews via cairosvg) |
| `link_figures.py` | Replaces figure placeholders in the guides with the image and caption |
| `make_index.py` | Writes `docs/FIGURES.md` |
| `readme_art.py` | Draws the README artwork in `assets/readme/` (run automatically by `build.py` when building everything) |

The canvas grows automatically to fit its content above the footer, and text that relies on column
alignment (show-command output) is written with `xml:space="preserve"` so browsers keep the spacing.

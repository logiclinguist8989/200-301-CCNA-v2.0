"""svgkit — a tiny, dependency-free SVG drawing kit for the CCNA study-guide figures.

Every figure in ``assets/figures`` is generated from code with this module so the
artwork stays consistent (one palette, one icon set, one typography scale) and
can be regenerated or corrected in one place.

Device icons follow the shapes of the standard Cisco network topology icon set
(router = cylinder with crossing arrows, switch = box with bidirectional arrows,
multilayer switch = cube with arrows on top, and so on), redrawn as clean vector
art so they stay sharp at any zoom level.
"""

from __future__ import annotations

import html
import math

# --------------------------------------------------------------------------- #
# Palette and typography
# --------------------------------------------------------------------------- #

FONT = "Inter, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', monospace"

INK = "#0f2540"        # primary text
MUTED = "#5b6b7f"      # secondary text
FAINT = "#94a3b8"      # tertiary / guides
LINE = "#cbd5e1"       # borders
PAPER = "#ffffff"
PANEL = "#f6f8fb"      # neutral panel

CISCO = "#049fd9"
NAVY = "#0b3b66"

# Semantic colour families: (stroke, fill, text-on-fill)
BLUE = ("#1d6fd1", "#e7f0fc", "#0f3f80")
GREEN = ("#1f9d63", "#e4f6ec", "#0f5a37")
RED = ("#d64040", "#fde8e8", "#8a1c1c")
AMBER = ("#d9861a", "#fdf1df", "#7a4708")
PURPLE = ("#7357d1", "#efeafd", "#3e2a85")
TEAL = ("#0f9aa8", "#e0f5f7", "#0b5b63")
GREY = ("#8796a8", "#f1f4f8", "#334155")
NAVYF = ("#0b3b66", "#0b3b66", "#ffffff")
CISCOF = ("#049fd9", "#049fd9", "#ffffff")

FAMILIES = {
    "blue": BLUE, "green": GREEN, "red": RED, "amber": AMBER, "purple": PURPLE,
    "teal": TEAL, "grey": GREY, "gray": GREY, "navy": NAVYF, "cisco": CISCOF,
}


def fam(c):
    if isinstance(c, tuple):
        return c
    return FAMILIES[c]


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def text_width(s: str, size: float, weight: int = 400, mono: bool = False) -> float:
    """Rough advance-width estimate (good enough for layout of short labels)."""
    if mono:
        return len(s) * size * 0.61
    w = 0.0
    for ch in s:
        if ch in "il.,:;|'!`":
            w += 0.28
        elif ch in "fjrt()[]{} -/":
            w += 0.36
        elif ch in "mwMW":
            w += 0.86
        elif ch.isupper() or ch in "0123456789":
            w += 0.64
        else:
            w += 0.54
    k = 1.06 if weight >= 600 else 1.0
    return w * size * k


# --------------------------------------------------------------------------- #
# Canvas
# --------------------------------------------------------------------------- #

class Canvas:
    """A figure card: white rounded panel, figure badge, title, subtitle, body."""

    def __init__(self, width, height, number, title, subtitle=None, footer=None, badge=None):
        self.badge_text = badge or f"FIG {number}"
        self.w = width
        self.h = height
        self.number = number
        self.title = title
        self.subtitle = subtitle
        self.footer = footer if isinstance(footer, (list, tuple)) else ([footer] if footer else [])
        self.parts: list[str] = []
        self.top = 96 if subtitle else 74   # y where body content can start
        self.maxy = 0                        # lowest content drawn so far (for auto-fit)

    # -- raw ------------------------------------------------------------- #
    def add(self, s: str):
        self.parts.append(s)
        return self

    # -- text ------------------------------------------------------------ #
    def text(self, x, y, s, size=14, color=INK, weight=400, anchor="start",
             mono=False, italic=False, opacity=None, rotate=None):
        fam_ = MONO if mono else FONT
        if rotate is None:
            self.maxy = max(self.maxy, y + size * 0.3)
        extra = ""
        if italic:
            extra += ' font-style="italic"'
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        if rotate is not None:
            extra += f' transform="rotate({rotate} {x} {y})"'
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam_}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{extra}' +
            (' xml:space="preserve">' if "  " in str(s) else ">") + f'{esc(s)}</text>'
        )

    def lines(self, x, y, items, size=13, color=INK, gap=None, anchor="start", mono=False, weight=400):
        gap = gap or size * 1.45
        for i, s in enumerate(items):
            if isinstance(s, tuple):  # (text, color, weight)
                t, c, wt = (list(s) + [None, None])[:3]
                self.text(x, y + i * gap, t, size, c or color, wt or weight, anchor, mono)
            else:
                self.text(x, y + i * gap, s, size, color, weight, anchor, mono)

    # -- shapes ---------------------------------------------------------- #
    def rect(self, x, y, w, h, fill=PAPER, stroke=LINE, sw=1.5, r=10, dash=None, opacity=None, shadow=False):
        self.maxy = max(self.maxy, y + h)
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        if shadow:
            extra += ' filter="url(#shadow)"'
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def circle(self, cx, cy, r, fill=PAPER, stroke=LINE, sw=1.5, dash=None):
        self.maxy = max(self.maxy, cy + r)
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def line(self, x1, y1, x2, y2, color=FAINT, sw=2, dash=None, arrow=None, opacity=None, cap="round"):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        if arrow in ("end", "both"):
            extra += f' marker-end="url(#{self._marker(color)})"'
        if arrow in ("start", "both"):
            extra += f' marker-start="url(#{self._marker(color, True)})"'
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                 f'stroke-width="{sw}" stroke-linecap="{cap}"{extra}/>')

    def path(self, d, color=FAINT, sw=2, fill="none", dash=None, arrow=None, opacity=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        if arrow in ("end", "both"):
            extra += f' marker-end="url(#{self._marker(color)})"'
        if arrow in ("start", "both"):
            extra += f' marker-start="url(#{self._marker(color, True)})"'
        self.add(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" '
                 f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')

    def poly(self, pts, color=FAINT, sw=2, arrow="end", dash=None, r=8):
        """Orthogonal polyline with rounded corners through points."""
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
            d1 = math.hypot(x1 - x0, y1 - y0)
            d2 = math.hypot(x2 - x1, y2 - y1)
            rr = min(r, d1 / 2, d2 / 2)
            ax = x1 - (x1 - x0) / d1 * rr if d1 else x1
            ay = y1 - (y1 - y0) / d1 * rr if d1 else y1
            bx = x1 + (x2 - x1) / d2 * rr if d2 else x1
            by = y1 + (y2 - y1) / d2 * rr if d2 else y1
            d += f" L{ax:.1f},{ay:.1f} Q{x1:.1f},{y1:.1f} {bx:.1f},{by:.1f}"
        d += f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"
        self.path(d, color, sw, arrow=arrow, dash=dash)

    _markers: dict

    def _marker(self, color, reverse=False):
        if not hasattr(self, "_mk"):
            self._mk = {}
        key = (color, reverse)
        if key not in self._mk:
            mid = f"m{len(self._mk)}"
            self._mk[key] = mid
        return self._mk[key]

    # -- composite blocks ------------------------------------------------ #
    def box(self, x, y, w, h, title=None, lines=(), color="grey", size=13, title_size=15,
            align="left", highlight=False, mono_lines=False, dash=None, r=10, pad=16, shadow=True,
            solid=False, valign="top"):
        st, fl, tx = fam(color)
        solid = solid or color in ("navy", "cisco")
        fill = st if solid else (fl if (highlight or color != "grey") else PAPER)
        if color == "grey" and not highlight:
            fill = PAPER
        stroke = st if (highlight or color != "grey") else LINE
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=2 if highlight else 1.5, r=r, dash=dash, shadow=shadow)
        tcol = "#ffffff" if solid else INK
        lcol = "#ffffff" if solid else MUTED
        n = (1 if title else 0) + len(lines)
        block_h = (title_size * 1.5 if title else 0) + len(lines) * size * 1.45
        if valign == "middle":
            cy = y + (h - block_h) / 2 + (title_size if title else size) * 0.95
        else:
            cy = y + pad + (title_size if title else size) * 0.8
        if align == "center":
            ax, anchor = x + w / 2, "middle"
        else:
            ax, anchor = x + pad, "start"
        if title:
            self.text(ax, cy, title, title_size, tcol, 650, anchor)
            cy += title_size * 1.5
        for ln in lines:
            if isinstance(ln, tuple):
                t, c = ln[0], ln[1]
                wt = ln[2] if len(ln) > 2 else 400
                self.text(ax, cy, t, size, c, wt, anchor, mono_lines)
            else:
                self.text(ax, cy, ln, size, lcol, 400, anchor, mono_lines)
            cy += size * 1.45
        return (x, y, w, h)

    def pill(self, x, y, s, color="blue", size=12, solid=False, anchor="middle", weight=600, mono=False):
        st, fl, tx = fam(color)
        w = text_width(s, size, weight, mono) + 18
        h = size + 10
        x0 = x - w / 2 if anchor == "middle" else (x if anchor == "start" else x - w)
        self.rect(x0, y - h / 2, w, h, fill=st if solid else fl, stroke=st, sw=1.2, r=h / 2)
        self.text(x0 + w / 2, y + size * 0.36, s, size, "#ffffff" if solid else tx, weight, "middle", mono)
        return w

    def badge(self, cx, cy, s, color="blue", r=12, size=12):
        st, fl, tx = fam(color)
        self.circle(cx, cy, r, fill=st, stroke=PAPER, sw=2)
        self.text(cx, cy + size * 0.36, s, size, "#ffffff", 700, "middle")

    def note(self, x, y, w, h, lines, color="grey", size=13, title=None):
        st, fl, tx = fam(color)
        self.rect(x, y, w, h, fill=fl if color != "grey" else PANEL, stroke=st if color != "grey" else LINE, sw=1.2, r=10)
        self.rect(x, y, 5, h, fill=st if color != "grey" else FAINT, stroke="none", sw=0, r=2)
        cy = y + 22
        if title:
            self.text(x + 18, cy, title, size + 1, tx if color != "grey" else INK, 650)
            cy += size * 1.6
        for ln in lines:
            if isinstance(ln, tuple):
                self.text(x + 18, cy, ln[0], size, ln[1], ln[2] if len(ln) > 2 else 400)
            else:
                self.text(x + 18, cy, ln, size, INK if color == "grey" else tx)
            cy += size * 1.5

    def cells(self, x, y, specs, h=46, size=13, gap=0, label_size=11):
        """Packet / frame strip. specs = [(label, width, color, sublabel)]"""
        cx = x
        out = []
        for spec in specs:
            label, w = spec[0], spec[1]
            color = spec[2] if len(spec) > 2 else "grey"
            sub = spec[3] if len(spec) > 3 else None
            st, fl, tx = fam(color)
            fill = PAPER if color == "grey" else fl
            stroke = LINE if color == "grey" else st
            if color in ("navy", "cisco"):
                fill = st
            self.rect(cx, y, w, h, fill=fill, stroke=stroke, sw=1.5, r=4)
            tc = "#ffffff" if color in ("navy", "cisco") else (INK if color == "grey" else tx)
            if sub:
                self.text(cx + w / 2, y + h / 2 - 2, label, size, tc, 600, "middle")
                self.text(cx + w / 2, y + h / 2 + size, sub, label_size, tc if color in ("navy", "cisco") else MUTED, 400, "middle")
            else:
                self.text(cx + w / 2, y + h / 2 + size * 0.36, label, size, tc, 600, "middle")
            out.append((cx, w))
            cx += w + gap
        return out

    def brace(self, x1, x2, y, label=None, color=BLUE[0], up=True, size=12):
        d = -8 if up else 8
        self.path(f"M{x1},{y - d} L{x1},{y} L{x2},{y} L{x2},{y - d}", color, 1.6)
        if label:
            ty = y - 8 if up else y + 18
            self.text((x1 + x2) / 2, ty, label, size, color, 600, "middle")

    def diamond(self, cx, cy, w, h, lines, color="amber", size=12):
        st, fl, tx = fam(color)
        self.add(f'<polygon points="{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}" '
                 f'fill="{fl}" stroke="{st}" stroke-width="1.8" filter="url(#shadow)"/>')
        n = len(lines)
        for i, s in enumerate(lines):
            self.text(cx, cy + (i - (n - 1) / 2) * size * 1.3 + size * 0.36, s, size, tx, 600, "middle")

    def link_label(self, x, y, s, size=11, color=MUTED, bg=PAPER, mono=False, weight=500):
        w = text_width(s, size, weight, mono) + 8
        self.rect(x - w / 2, y - size * 0.85, w, size * 1.4, fill=bg, stroke="none", sw=0, r=3)
        self.text(x, y + size * 0.3, s, size, color, weight, "middle", mono)

    def cable(self, x1, y1, x2, y2, kind="copper", label1=None, label2=None, mid=None, color=None, sw=3, dash=None):
        """A device-to-device link with optional interface labels near each end."""
        col = color or {"copper": "#64748b", "fiber": "#e08a1e", "serial": "#d64040",
                        "trunk": "#1d6fd1", "wan": "#7357d1", "wireless": "#0f9aa8",
                        "console": "#0f9aa8", "cross": "#d64040"}.get(kind, "#64748b")
        if kind == "wireless":
            dash = dash or "2 7"
        if kind == "console":
            dash = dash or "8 5"
        self.line(x1, y1, x2, y2, col, sw, dash=dash)
        L = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        off = min(46, L * 0.28)
        if label1:
            self.link_label(x1 + ux * off, y1 + uy * off, label1, mono=True, size=11)
        if label2:
            self.link_label(x2 - ux * off, y2 - uy * off, label2, mono=True, size=11)
        if mid:
            self.link_label((x1 + x2) / 2, (y1 + y2) / 2, mid, size=11, color=col, weight=600)

    # -- devices --------------------------------------------------------- #
    def device(self, kind, cx, cy, name=None, lines=(), s=1.0, label="below", name_size=14, line_size=12,
               highlight=None, line_colors=None):
        fn = ICONS[kind]
        if highlight:
            st, fl, _ = fam(highlight)
            self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{46 * s:.1f}" fill="{fl}" stroke="{st}" '
                     f'stroke-width="2" stroke-dasharray="5 4" opacity="0.95"/>')
        self.add(f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s})">{fn()}</g>')
        hh = ICON_H.get(kind, 30) * s
        if highlight:
            hh = max(hh, 46 * s - 6)
        if name is None:
            return
        if label == "below":
            y = cy + hh + name_size + 2
            self.text(cx, y, name, name_size, INK, 700, "middle")
            for i, ln in enumerate(lines):
                c = (line_colors[i] if line_colors else MUTED)
                self.text(cx, y + (i + 1) * line_size * 1.4, ln, line_size, c, 400, "middle", mono=False)
        elif label == "above":
            n = len(lines)
            top_h = max(ICON_H.get(kind, 30) * s, 46 * s if highlight else 0)
            y = cy - top_h - 8 - n * line_size * 1.4
            self.text(cx, y, name, name_size, INK, 700, "middle")
            for i, ln in enumerate(lines):
                self.text(cx, y + (i + 1) * line_size * 1.4, ln, line_size, MUTED, 400, "middle")
        elif label in ("right", "left"):
            wx = ICON_W.get(kind, 34) * s
            if highlight:
                wx = max(wx, 46 * s + 2)
            x = cx + wx + 10 if label == "right" else cx - wx - 10
            anchor = "start" if label == "right" else "end"
            n = len(lines)
            y = cy - (n * line_size * 1.4) / 2 + name_size * 0.35
            self.text(x, y, name, name_size, INK, 700, anchor)
            for i, ln in enumerate(lines):
                c = (line_colors[i] if line_colors else MUTED)
                self.text(x, y + (i + 1) * line_size * 1.4, ln, line_size, c, 400, anchor)

    def fit(self, content_bottom):
        """Grow the canvas so content ending at `content_bottom` clears the footer."""
        foot = 34 + 19 * len(self.footer) + (16 if self.footer else 0)
        self.h = max(self.h, int(content_bottom + foot + 12))

    # -- render ---------------------------------------------------------- #
    def svg(self) -> str:
        self.fit(self.maxy)
        W, H = self.w, self.h
        head = []
        head.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
                    f'role="img" aria-labelledby="t d" xml:space="preserve" style="white-space:pre">')
        head.append(f'<title id="t">{"Figure " + esc(self.number) + " — " if self.number else ""}{esc(self.title)}</title>')
        head.append(f'<desc id="d">{esc(self.subtitle or self.title)}</desc>')
        defs = [
            '<defs>',
            '<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">'
            '<feDropShadow dx="0" dy="1.5" stdDeviation="2" flood-color="#0f2540" flood-opacity="0.10"/></filter>',
            '<linearGradient id="gRouter" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#2a8fd8"/><stop offset="1" stop-color="#0b5a9c"/></linearGradient>',
            '<linearGradient id="gRouterTop" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#7cc4f2"/><stop offset="1" stop-color="#3a9be0"/></linearGradient>',
            '<linearGradient id="gFront" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#1f7fcc"/><stop offset="1" stop-color="#0b4f8a"/></linearGradient>',
            '<linearGradient id="gTop" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#8fd0f7"/><stop offset="1" stop-color="#46a6e6"/></linearGradient>',
            '<linearGradient id="gSide" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0" stop-color="#0b4f8a"/><stop offset="1" stop-color="#083a66"/></linearGradient>',
            '<linearGradient id="gScreen" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#3fb4ef"/><stop offset="1" stop-color="#0b6fb8"/></linearGradient>',
            '<linearGradient id="gMetal" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#eef2f7"/><stop offset="1" stop-color="#c9d3df"/></linearGradient>',
            '<linearGradient id="gDark" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#3b4a5e"/><stop offset="1" stop-color="#1e293b"/></linearGradient>',
            '<linearGradient id="gCloud" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#dbe7f5"/></linearGradient>',
            '<linearGradient id="gFire" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#e2574c"/><stop offset="1" stop-color="#a8261d"/></linearGradient>',
            '<linearGradient id="gHeader" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="{CISCO}"/></linearGradient>',
        ]
        for (color, rev), mid in getattr(self, "_mk", {}).items():
            if rev:
                defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="7" markerHeight="7" '
                            f'orient="auto-start-reverse"><path d="M10,1 L1,5 L10,9 z" fill="{color}"/></marker>')
            else:
                defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
                            f'orient="auto"><path d="M0,1 L9,5 L0,9 z" fill="{color}"/></marker>')
        defs.append('</defs>')
        frame = [
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{PAPER}" stroke="#dbe3ec"/>',
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="6" rx="3" fill="url(#gHeader)"/>',
        ]
        # Figure badge + title
        badge = self.badge_text
        bw = text_width(badge, 11, 700) + 18
        frame.append(f'<rect x="28" y="24" width="{bw:.1f}" height="22" rx="11" fill="{NAVY}"/>')
        frame.append(f'<text x="{28 + bw / 2:.1f}" y="39" font-family="{FONT}" font-size="11" font-weight="700" '
                     f'fill="#ffffff" text-anchor="middle" letter-spacing="0.6">{esc(badge)}</text>')
        frame.append(f'<text x="{28 + bw + 12:.1f}" y="41" font-family="{FONT}" font-size="19" font-weight="700" '
                     f'fill="{INK}">{esc(self.title)}</text>')
        if self.subtitle:
            frame.append(f'<text x="28" y="70" font-family="{FONT}" font-size="13.5" fill="{MUTED}">{esc(self.subtitle)}</text>')
        foot = []
        if self.footer:
            n = len(self.footer)
            y0 = H - 18 - (n - 1) * 19
            foot.append(f'<line x1="28" y1="{y0 - 22}" x2="{W - 28}" y2="{y0 - 22}" stroke="#e5eaf0" stroke-width="1"/>')
            for i, f in enumerate(self.footer):
                foot.append(f'<text x="28" y="{y0 + i * 19}" font-family="{FONT}" font-size="12.5" fill="{MUTED}">{esc(f)}</text>')
        foot.append(f'<text x="{W - 24}" y="{H - 10}" font-family="{FONT}" font-size="9.5" fill="#b6c2d0" '
                    f'text-anchor="end">CCNA 200-301 v2.0 Study Guide</text>')
        body = "\n".join(self.parts)
        return "\n".join(head + defs + frame + [body] + foot + ["</svg>"]) + "\n"


# --------------------------------------------------------------------------- #
# Device icons — each returns SVG drawn around (0,0)
# --------------------------------------------------------------------------- #

def _arrow_shape(x, y, ang, L=11, col="#ffffff", sw=2.2):
    """small arrow centred on x,y pointing at angle (deg)."""
    a = math.radians(ang)
    dx, dy = math.cos(a) * L / 2, math.sin(a) * L / 2
    x1, y1, x2, y2 = x - dx, y - dy, x + dx, y + dy
    hx = x2 - math.cos(a) * 4.2
    hy = y2 - math.sin(a) * 4.2
    px, py = -math.sin(a) * 3.4, math.cos(a) * 3.4
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {hx + px:.1f},{hy + py:.1f} {hx - px:.1f},{hy - py:.1f}" fill="{col}"/>')


def icon_router():
    rx, ry, h = 34, 12, 26
    s = []
    s.append(f'<ellipse cx="0" cy="{h / 2 + 2}" rx="{rx + 2}" ry="{ry}" fill="#0f2540" opacity="0.12"/>')
    s.append(f'<path d="M{-rx},{-h / 2} L{-rx},{h / 2} A{rx},{ry} 0 0 0 {rx},{h / 2} L{rx},{-h / 2} Z" fill="url(#gRouter)"/>')
    s.append(f'<ellipse cx="0" cy="{-h / 2}" rx="{rx}" ry="{ry}" fill="url(#gRouterTop)" stroke="#0b5a9c" stroke-width="1"/>')
    # four arrows on the top ellipse: two inward (left/right), two outward (front/back)
    t = -h / 2
    s.append(_arrow_shape(-18, t, 0, 12))
    s.append(_arrow_shape(18, t, 180, 12))
    s.append(_arrow_shape(0, t - 5.5, -90, 9))
    s.append(_arrow_shape(0, t + 5.5, 90, 9))
    s.append(f'<line x1="{-rx + 6}" y1="{h / 2 - 2}" x2="{rx - 6}" y2="{h / 2 - 2}" stroke="#7cc4f2" stroke-width="0.8" opacity="0.4"/>')
    return "".join(s)


def _box3d(w, h, d, front="url(#gFront)", top="url(#gTop)", side="url(#gSide)"):
    x0, y0 = -w / 2 - d / 4, -h / 2 + d / 4
    s = []
    s.append(f'<ellipse cx="2" cy="{h / 2 + d / 4 + 3}" rx="{w / 2 + 6}" ry="6" fill="#0f2540" opacity="0.12"/>')
    s.append(f'<polygon points="{x0},{y0} {x0 + d / 2},{y0 - d / 2} {x0 + w + d / 2},{y0 - d / 2} {x0 + w},{y0}" fill="{top}" stroke="#0b4f8a" stroke-width="0.8"/>')
    s.append(f'<polygon points="{x0 + w},{y0} {x0 + w + d / 2},{y0 - d / 2} {x0 + w + d / 2},{y0 + h - d / 2} {x0 + w},{y0 + h}" fill="{side}"/>')
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{front}"/>')
    return "".join(s), (x0, y0)


def icon_switch():
    w, h, d = 70, 22, 18
    body, (x0, y0) = _box3d(w, h, d)
    s = [body]
    # arrows on the top face: two pointing right, two pointing left (Cisco workgroup switch)
    ty = y0 - d / 4
    cx = x0 + w / 2 + d / 4
    s.append(_arrow_shape(cx - 12, ty - 3.5, 0, 16, sw=1.9))
    s.append(_arrow_shape(cx + 12, ty - 3.5, 0, 16, sw=1.9))
    s.append(_arrow_shape(cx - 12, ty + 3.5, 180, 16, sw=1.9))
    s.append(_arrow_shape(cx + 12, ty + 3.5, 180, 16, sw=1.9))
    # port LEDs on the front
    for i in range(8):
        s.append(f'<rect x="{x0 + 8 + i * 7}" y="{y0 + h - 8}" width="4.5" height="3.5" rx="0.8" fill="#9fe3b5" opacity="0.9"/>')
    return "".join(s)


def icon_l3switch():
    w, h, d = 50, 40, 22
    body, (x0, y0) = _box3d(w, h, d)
    s = [body]
    ty = y0 - d / 4
    cx = x0 + w / 2 + d / 4
    s.append(_arrow_shape(cx - 10, ty, 0, 12, sw=1.9))
    s.append(_arrow_shape(cx + 10, ty, 180, 12, sw=1.9))
    s.append(_arrow_shape(cx, ty - 4, -90, 8, sw=1.6))
    s.append(_arrow_shape(cx, ty + 4, 90, 8, sw=1.6))
    # front arrows (multilayer marking)
    fx, fy = x0 + w / 2, y0 + h / 2
    s.append(_arrow_shape(fx - 9, fy - 6, 0, 13, sw=1.8))
    s.append(_arrow_shape(fx + 9, fy - 6, 0, 13, sw=1.8))
    s.append(_arrow_shape(fx - 9, fy + 6, 180, 13, sw=1.8))
    s.append(_arrow_shape(fx + 9, fy + 6, 180, 13, sw=1.8))
    return "".join(s)


def icon_pc():
    s = []
    s.append('<ellipse cx="0" cy="33" rx="30" ry="4" fill="#0f2540" opacity="0.10"/>')
    s.append('<rect x="-30" y="-28" width="60" height="42" rx="4" fill="url(#gDark)"/>')
    s.append('<rect x="-26" y="-24" width="52" height="33" rx="2" fill="url(#gScreen)"/>')
    s.append('<path d="M-26,-24 L6,-24 L-26,4 Z" fill="#ffffff" opacity="0.12"/>')
    s.append('<rect x="-5" y="14" width="10" height="9" fill="#475569"/>')
    s.append('<rect x="-17" y="22" width="34" height="5" rx="2" fill="url(#gDark)"/>')
    s.append('<rect x="-26" y="28" width="52" height="5" rx="1.5" fill="url(#gMetal)" stroke="#94a3b8" stroke-width="0.6"/>')
    return "".join(s)


def icon_laptop():
    s = []
    s.append('<ellipse cx="0" cy="22" rx="36" ry="4" fill="#0f2540" opacity="0.10"/>')
    s.append('<rect x="-26" y="-24" width="52" height="36" rx="3" fill="url(#gDark)"/>')
    s.append('<rect x="-22" y="-20" width="44" height="28" rx="1.5" fill="url(#gScreen)"/>')
    s.append('<path d="M-32,13 L32,13 L36,20 L-36,20 Z" fill="url(#gMetal)" stroke="#94a3b8" stroke-width="0.8"/>')
    s.append('<rect x="-8" y="15" width="16" height="2.5" rx="1" fill="#94a3b8"/>')
    return "".join(s)


def icon_server():
    s = []
    s.append('<ellipse cx="0" cy="35" rx="26" ry="4" fill="#0f2540" opacity="0.12"/>')
    s.append('<polygon points="-20,-30 -10,-37 28,-37 18,-30" fill="#5d6f86"/>')
    s.append('<polygon points="18,-30 28,-37 28,27 18,34" fill="#1e293b"/>')
    s.append('<rect x="-20" y="-30" width="38" height="64" rx="2" fill="url(#gDark)"/>')
    for i in range(4):
        y = -24 + i * 11
        s.append(f'<rect x="-15" y="{y}" width="28" height="7" rx="1.5" fill="#475569"/>')
        s.append(f'<circle cx="8" cy="{y + 3.5}" r="1.6" fill="#4ade80"/>')
    s.append('<rect x="-15" y="22" width="28" height="6" rx="1" fill="#049fd9" opacity="0.85"/>')
    return "".join(s)


def icon_firewall():
    w, h, d = 56, 36, 18
    body, (x0, y0) = _box3d(w, h, d, front="url(#gFire)", top="#f08a80", side="#8f1f17")
    s = [body]
    # brick pattern
    for r in range(3):
        y = y0 + r * 12
        s.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}" stroke="#ffd9d4" stroke-width="1.2" opacity="0.8"/>')
        off = 0 if r % 2 == 0 else 9
        for k in range(4):
            x = x0 + off + k * 18
            if x0 < x < x0 + w:
                s.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + 12}" stroke="#ffd9d4" stroke-width="1.2" opacity="0.8"/>')
    return "".join(s)


def icon_ap():
    s = []
    s.append('<ellipse cx="0" cy="16" rx="30" ry="5" fill="#0f2540" opacity="0.10"/>')
    s.append('<ellipse cx="0" cy="8" rx="28" ry="9" fill="#0b5a9c"/>')
    s.append('<rect x="-28" y="2" width="56" height="6" fill="#0b5a9c"/>')
    s.append('<ellipse cx="0" cy="2" rx="28" ry="9" fill="url(#gTop)" stroke="#0b5a9c" stroke-width="1"/>')
    s.append('<circle cx="0" cy="2" r="2.5" fill="#4ade80"/>')
    for i, r in enumerate((10, 17, 24)):
        s.append(f'<path d="M{-r * 0.8:.1f},{-8 - r * 0.35:.1f} A{r},{r} 0 0 1 {r * 0.8:.1f},{-8 - r * 0.35:.1f}" '
                 f'fill="none" stroke="#049fd9" stroke-width="2.4" stroke-linecap="round" opacity="{1 - i * 0.22}"/>')
    return "".join(s)


def icon_wlc():
    w, h, d = 64, 22, 16
    body, (x0, y0) = _box3d(w, h, d)
    s = [body]
    cx, cy = x0 + w / 2, y0 + h / 2 + 2
    for i, r in enumerate((5, 10)):
        s.append(f'<path d="M{cx - r},{cy - r * 0.2} A{r},{r} 0 0 1 {cx + r},{cy - r * 0.2}" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/>')
    s.append(f'<circle cx="{cx}" cy="{cy + 1}" r="2" fill="#fff"/>')
    return "".join(s)


def icon_phone():
    s = []
    s.append('<ellipse cx="0" cy="22" rx="30" ry="4" fill="#0f2540" opacity="0.10"/>')
    s.append('<path d="M-28,18 L-22,-18 L24,-18 L30,18 Z" fill="url(#gDark)"/>')
    s.append('<rect x="-30" y="-24" width="13" height="40" rx="5" fill="#334155" stroke="#1e293b" stroke-width="1"/>')
    s.append('<rect x="-12" y="-13" width="24" height="12" rx="1.5" fill="url(#gScreen)"/>')
    for r in range(3):
        for c in range(3):
            s.append(f'<rect x="{-9 + c * 7}" y="{2 + r * 5}" width="5" height="3" rx="0.8" fill="#cbd5e1"/>')
    s.append('<rect x="16" y="-12" width="6" height="22" rx="1.5" fill="#475569"/>')
    return "".join(s)


def icon_cloud():
    d = ("M-44,14 C-60,14 -60,-8 -42,-8 C-44,-26 -18,-32 -8,-18 C-2,-34 26,-34 30,-14 "
         "C48,-18 56,4 42,14 Z")
    return (f'<path d="{d}" transform="translate(2,4)" fill="#0f2540" opacity="0.10"/>'
            f'<path d="{d}" fill="url(#gCloud)" stroke="#7aa7d6" stroke-width="2"/>')


def icon_printer():
    s = []
    s.append('<ellipse cx="0" cy="22" rx="30" ry="4" fill="#0f2540" opacity="0.10"/>')
    s.append('<rect x="-16" y="-24" width="32" height="14" fill="#ffffff" stroke="#94a3b8"/>')
    s.append('<rect x="-28" y="-12" width="56" height="28" rx="4" fill="url(#gDark)"/>')
    s.append('<rect x="-18" y="8" width="36" height="12" fill="#ffffff" stroke="#94a3b8"/>')
    s.append('<line x1="-12" y1="13" x2="12" y2="13" stroke="#94a3b8"/>')
    s.append('<circle cx="20" cy="-4" r="2" fill="#4ade80"/>')
    return "".join(s)


def icon_camera():
    s = []
    s.append('<ellipse cx="0" cy="22" rx="24" ry="4" fill="#0f2540" opacity="0.10"/>')
    s.append('<rect x="-4" y="-2" width="8" height="22" fill="#475569"/>')
    s.append('<rect x="-16" y="18" width="32" height="5" rx="2" fill="#334155"/>')
    s.append('<g transform="rotate(-12)"><rect x="-26" y="-20" width="44" height="20" rx="5" fill="url(#gMetal)" stroke="#94a3b8"/>'
             '<rect x="18" y="-17" width="8" height="14" rx="2" fill="#334155"/>'
             '<circle cx="22" cy="-10" r="4" fill="#049fd9"/></g>')
    return "".join(s)


def icon_hypervisor():
    """A rack server with stacked VM tiles."""
    s = []
    s.append('<ellipse cx="0" cy="30" rx="40" ry="5" fill="#0f2540" opacity="0.10"/>')
    s.append('<rect x="-38" y="-6" width="76" height="32" rx="3" fill="url(#gDark)"/>')
    for i in range(3):
        s.append(f'<rect x="-32" y="{0 + i * 8}" width="40" height="5" rx="1" fill="#475569"/>')
    s.append('<circle cx="24" cy="4" r="2" fill="#4ade80"/><circle cx="30" cy="4" r="2" fill="#4ade80"/>')
    for i, c in enumerate(("#1d6fd1", "#1f9d63", "#7357d1")):
        s.append(f'<rect x="{-32 + i * 23}" y="-30" width="19" height="20" rx="3" fill="{c}"/>')
        s.append(f'<text x="{-22.5 + i * 23}" y="-16" font-family="{FONT}" font-size="8" font-weight="700" fill="#fff" text-anchor="middle">VM</text>')
    return "".join(s)


def icon_controller():
    s = []
    s.append('<ellipse cx="0" cy="30" rx="34" ry="5" fill="#0f2540" opacity="0.10"/>')
    s.append('<rect x="-34" y="-28" width="68" height="54" rx="6" fill="url(#gDark)"/>')
    s.append('<rect x="-28" y="-22" width="56" height="30" rx="2" fill="url(#gScreen)"/>')
    # mini dashboard
    s.append('<polyline points="-24,2 -14,-6 -6,-2 4,-14 14,-8 24,-16" fill="none" stroke="#fff" stroke-width="2"/>')
    s.append('<rect x="-28" y="13" width="18" height="8" rx="1.5" fill="#049fd9"/>')
    s.append('<rect x="-6" y="13" width="18" height="8" rx="1.5" fill="#1f9d63"/>')
    s.append('<rect x="16" y="13" width="12" height="8" rx="1.5" fill="#d9861a"/>')
    return "".join(s)


def icon_user():
    return ('<circle cx="0" cy="-14" r="11" fill="#475569"/>'
            '<path d="M-20,22 C-20,2 20,2 20,22 Z" fill="#475569"/>')


def icon_robot():
    s = []
    s.append('<ellipse cx="0" cy="30" rx="28" ry="4" fill="#0f2540" opacity="0.10"/>')
    s.append('<line x1="0" y1="-30" x2="0" y2="-22" stroke="#7357d1" stroke-width="2.5"/><circle cx="0" cy="-32" r="3.5" fill="#7357d1"/>')
    s.append('<rect x="-26" y="-22" width="52" height="40" rx="10" fill="#7357d1"/>')
    s.append('<rect x="-19" y="-14" width="38" height="20" rx="6" fill="#efeafd"/>')
    s.append('<circle cx="-8" cy="-4" r="4" fill="#3e2a85"/><circle cx="8" cy="-4" r="4" fill="#3e2a85"/>')
    s.append('<rect x="-10" y="10" width="20" height="3" rx="1.5" fill="#efeafd"/>')
    s.append('<rect x="-32" y="-6" width="6" height="14" rx="2" fill="#5b45b0"/><rect x="26" y="-6" width="6" height="14" rx="2" fill="#5b45b0"/>')
    return "".join(s)


def icon_database():
    return ('<ellipse cx="0" cy="26" rx="26" ry="4" fill="#0f2540" opacity="0.10"/>'
            '<path d="M-22,-18 L-22,18 A22,7 0 0 0 22,18 L22,-18 Z" fill="url(#gDark)"/>'
            '<path d="M-22,-4 A22,7 0 0 0 22,-4 M-22,8 A22,7 0 0 0 22,8" fill="none" stroke="#64748b" stroke-width="1.5"/>'
            '<ellipse cx="0" cy="-18" rx="22" ry="7" fill="#64748b"/>')


def icon_file():
    return ('<path d="M-18,-26 L8,-26 L20,-14 L20,26 L-18,26 Z" fill="#ffffff" stroke="#64748b" stroke-width="2"/>'
            '<path d="M8,-26 L8,-14 L20,-14" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>'
            '<line x1="-10" y1="-4" x2="12" y2="-4" stroke="#94a3b8" stroke-width="2"/>'
            '<line x1="-10" y1="4" x2="12" y2="4" stroke="#94a3b8" stroke-width="2"/>'
            '<line x1="-10" y1="12" x2="6" y2="12" stroke="#94a3b8" stroke-width="2"/>')


def icon_tablet():
    return ('<rect x="-20" y="-28" width="40" height="56" rx="6" fill="url(#gDark)"/>'
            '<rect x="-16" y="-22" width="32" height="42" rx="2" fill="url(#gScreen)"/>'
            '<circle cx="0" cy="24" r="1.8" fill="#94a3b8"/>')


ICONS = {
    "router": icon_router, "switch": icon_switch, "l3switch": icon_l3switch, "pc": icon_pc,
    "laptop": icon_laptop, "server": icon_server, "firewall": icon_firewall, "ap": icon_ap,
    "wlc": icon_wlc, "phone": icon_phone, "cloud": icon_cloud, "printer": icon_printer,
    "camera": icon_camera, "hypervisor": icon_hypervisor, "controller": icon_controller,
    "user": icon_user, "robot": icon_robot, "database": icon_database, "file": icon_file,
    "tablet": icon_tablet,
}

# half-height below centre (for label placement) and half-width (for side labels)
ICON_H = {"router": 26, "switch": 22, "l3switch": 30, "pc": 34, "laptop": 22, "server": 36, "firewall": 30,
          "ap": 18, "wlc": 20, "phone": 22, "cloud": 22, "printer": 22, "camera": 24, "hypervisor": 30,
          "controller": 30, "user": 22, "robot": 30, "database": 26, "file": 26, "tablet": 28}
ICON_W = {"router": 36, "switch": 40, "l3switch": 34, "pc": 30, "laptop": 36, "server": 28, "firewall": 36,
          "ap": 30, "wlc": 38, "phone": 30, "cloud": 56, "printer": 30, "camera": 26, "hypervisor": 40,
          "controller": 34, "user": 20, "robot": 32, "database": 26, "file": 20, "tablet": 20}


# --------------------------------------------------------------------------- #
# Reusable figure patterns
# --------------------------------------------------------------------------- #

def wrap(s: str, max_chars: int):
    words, out, cur = s.split(" "), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        out.append(cur)
    return out


def check_flow(c: Canvas, start, checks, end=None, x=60, y=None, qw=330, fix_x=None, fix_w=None, step=124,
               start_lines=(), end_lines=(), yes="yes", no="no", qsize=13):
    """Vertical decision chain: start box → diamonds (yes → fix box on right) → end box."""
    y = y or c.top + 10
    cx = x + qw / 2 + 25
    fix_x = fix_x or x + qw + 140
    fix_w = fix_w or (c.w - fix_x - 40)
    c.box(x, y, qw + 50, 64, start, list(start_lines), "navy", solid=True, size=12, title_size=13.5)
    prev = y + 64
    yy = y + 64 + 30 + 46
    for q, fix, col in checks:
        c.line(cx, prev, cx, yy - 46, FAINT, 2, arrow="end")
        ql = q if isinstance(q, list) else wrap(q, 34)
        c.diamond(cx, yy, qw, 92, ql, "amber", qsize)
        c.line(cx + qw / 2, yy, fix_x - 6, yy, FAINT, 2, arrow="end")
        c.text((cx + qw / 2 + fix_x) / 2, yy - 10, yes, 13, AMBER[0], 700, "middle")
        fl = fix if isinstance(fix, list) else wrap(fix, int(fix_w / 7.4))
        bh = max(64, 26 + len(fl) * 19)
        c.box(fix_x, yy - bh / 2, fix_w, bh, None, [(ln, INK, 500) for ln in fl], col, size=13, valign="middle")
        c.text(cx + 12, yy + 64, no, 12, MUTED, 700)
        prev = yy + 46
        yy += step
    if end:
        c.line(cx, prev, cx, yy - 60, FAINT, 2, arrow="end")
        c.box(x, yy - 58, qw + 50, 64, end, list(end_lines), "green", highlight=True, size=12, title_size=13.5)
        last = yy + 6
    else:
        last = prev
    c.fit(last)
    return yy


def sequence(c: Canvas, actors, messages, top=None, bottom=None, gap=None, label_size=12.5):
    """Simple sequence diagram.

    actors: list of (key, x, icon_kind, name, sublines)
    messages: list of dicts: {"a": from_key, "b": to_key, "t": label, "s": sublabel, "c": colour, "self": bool,
                              "dash": bool, "note": str}
    """
    top = top or c.top + 20
    pos = {}
    for key, x, kind, name, sub in actors:
        pos[key] = x
        c.device(kind, x, top + 34, name, sub, s=0.85, name_size=13.5, line_size=11.5)
    y0 = top + 120 + 14 * max(len(a[4]) for a in actors)
    bottom = bottom or c.h - 70
    for key, x in pos.items():
        c.line(x, y0 - 10, x, bottom, "#cbd5e1", 2, dash="4 5")
    gap = gap or (bottom - y0 - 20) / max(1, len(messages))
    y = y0 + 16
    for m in messages:
        col = m.get("c", BLUE[0])
        a, b = pos[m["a"]], pos.get(m.get("b", m["a"]), pos[m["a"]])
        if m.get("self") or a == b:
            c.rect(a - 150, y - 16, 300, 30, fill=PANEL, stroke=LINE, r=8)
            c.text(a, y + 4, m["t"], label_size, INK, 600, "middle")
        else:
            c.line(a, y, b + (-8 if b > a else 8), y, col, 2.4, arrow="end", dash="7 5" if m.get("dash") else None)
            mx = (a + b) / 2
            c.text(mx, y - 8, m["t"], label_size, col, 700, "middle")
            if m.get("s"):
                c.text(mx, y + 17, m["s"], 11.5, MUTED, 400, "middle")
        if m.get("n"):
            c.badge(min(a, b) - 26 if not m.get("self") else a - 172, y, str(m["n"]), "navy", r=11, size=11)
        y += gap
    return y


def octet_bits(c: Canvas, x, y, bits, cell=34, h=38, colors=None, size=15, labels=None):
    """Row of bit cells. colors: list of family names per bit (or None for plain)."""
    for i, b in enumerate(bits):
        col = colors[i] if colors else None
        if col:
            st, fl, tx = fam(col)
            c.rect(x + i * cell, y, cell - 3, h, fill=fl, stroke=st, sw=1.4, r=4)
            c.text(x + i * cell + (cell - 3) / 2, y + h / 2 + size * 0.36, b, size, tx, 700, "middle", mono=True)
        else:
            c.rect(x + i * cell, y, cell - 3, h, fill=PAPER, stroke=LINE, sw=1.2, r=4)
            c.text(x + i * cell + (cell - 3) / 2, y + h / 2 + size * 0.36, b, size, INK, 500, "middle", mono=True)
        if labels:
            c.text(x + i * cell + (cell - 3) / 2, y - 8, labels[i], 11, MUTED, 600, "middle")

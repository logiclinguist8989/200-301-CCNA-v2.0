"""Chapter 10 — The routing table; Chapter 11 — Static routing."""

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL, MONO)


# ----------------------------------------------------------------------------- Chapter 10

@figure("10.1", "router-forwarding-process")
def f10_1():
    c = Canvas(1160, 560, "10.1", "The router's per-packet forwarding process",
               "The same seven steps for every packet — the only routing reasons to drop it are shown in red",
               ["The control plane builds the RIB; the forwarding plane (CEF) uses an optimized copy but follows the same table."])
    steps = [("1", "Receive", ["FCS OK?", "Dst MAC = mine?"]), ("2", "De-encap", ["strip frame,", "decrement TTL"]),
             ("3", "Look up", ["dst IP: longest", "prefix match"]), ("5", "Next hop", ["+ exit interface", "(recursive lookup)"]),
             ("6", "Resolve MAC", ["ARP (IPv4)", "ND (IPv6)"]), ("7", "Re-encap", ["new MACs + FCS,", "send"])]
    xs = [40, 225, 410, 595, 780, 965]
    for (n, t, d), x in zip(steps, xs):
        c.box(x, 140, 160, 92, None, [], "blue" if n in ("3", "5") else "grey")
        c.badge(x + 22, 164, n, "navy")
        c.text(x + 40, 169, t, 14, INK, 700)
        c.text(x + 14, 199, d[0], 12, MUTED, 500)
        c.text(x + 14, 217, d[1], 12, MUTED, 500)
    for x in xs[:-1]:
        c.line(x + 162, 186, x + 182, 186, FAINT, 2, arrow="end")
    # drops
    c.line(305, 232, 305, 330, RED[0], 2, arrow="end")
    c.text(315, 290, "TTL = 0", 12, RED[0], 700)
    c.box(200, 334, 210, 84, "Drop", ["ICMP Time Exceeded", "(how traceroute works)"], "red", size=12, title_size=14)
    c.line(490, 232, 490, 330, RED[0], 2, arrow="end")
    c.text(500, 290, "4  no match, no default", 12, RED[0], 700)
    c.box(430, 334, 220, 84, "Drop", ["ICMP Destination", "Unreachable"], "red", size=12, title_size=14)
    c.device("router", 900, 380, "R1", ["routing table (RIB) → CEF"], s=1.1)
    c.cells(40, 470, [("Eth hdr", 110, "purple"), ("IP · TTL 64 → 63", 200, "amber"), ("Data", 140, "blue"), ("FCS", 70, "purple")], h=40, size=12)
    c.text(600, 495, "IP header kept (TTL −1), Ethernet header + FCS rebuilt", 12.5, MUTED, 600)
    return c


@figure("10.2", "routing-entry-anatomy")
def f10_2():
    c = Canvas(1160, 420, "10.2", "Anatomy of one routing table entry from R1",
               "Read any route left to right: how learned, where to, how trusted, how costly, which neighbor and interface",
               ["Connected (C) and local (L) routes have no brackets and no next hop — the network is directly attached."])
    parts = [("O", "Source", "O = OSPF", "purple"), ("10.10.40.0/24", "Destination", "prefix / length", "blue"),
             ("[110/2]", "AD / metric", "trust 110 · cost 2", "amber"), ("via 10.0.0.2,", "Next hop", "neighbor's IP", "green"),
             ("00:14:02,", "Age", "time since learned", "grey"), ("GigabitEthernet0/0/0", "Exit interface", "send out here", "teal")]
    c.rect(40, 120, 1080, 66, fill="#0f172a", stroke="none", r=10)
    x = 120
    from svgkit import fam, text_width
    for tok, title, desc, col in parts:
        w = len(tok) * 13.4
        st = fam(col)[0] if col != "grey" else "#94a3b8"
        c.text(x, 162, tok, 22, "#e2e8f0", 600, mono=True)
        c.line(x, 174, x + w - 8, 174, st, 3)
        cx = x + w / 2 - 4
        k = parts.index((tok, title, desc, col))
        by = 240 if k % 2 == 0 else 320
        c.line(cx, 190, cx, by - 2, st, 1.6)
        c.box(cx - 72, by, 144, 66, title, [desc], col, align="center", size=12, title_size=13.5, shadow=False)
        x += w + 12
    return c


@figure("10.3", "route-selection")
def f10_3():
    c = Canvas(1160, 560, "10.3", "Route selection: two separate jobs",
               "AD and metric decide what is installed for each prefix; longest match decides which installed route a packet uses",
               ["AD and metric never compete across different prefixes: a static /16 (AD 1) does not beat an OSPF /24 (AD 110) for 10.10.40.25."])
    c.rect(40, 100, 520, 400, fill=PURPLE[1], stroke=PURPLE[0], r=14, sw=1.5)
    c.text(300, 130, "Building the table (control plane)", 15, PURPLE[2], 700, "middle")
    c.text(300, 150, "runs when routing information changes", 12, MUTED, 500, "middle")
    c.box(70, 170, 460, 70, None, [("Candidates for the SAME prefix 10.10.40.0/24", INK, 700), "static AD 1 · OSPF AD 110 · RIP AD 120"], "grey", size=12.5)
    c.line(300, 240, 300, 266, FAINT, 2, arrow="end")
    c.box(70, 270, 460, 70, "1  Lowest administrative distance", ["picks the source (most trusted)"], "amber", size=12.5)
    c.line(300, 340, 300, 366, FAINT, 2, arrow="end")
    c.box(70, 370, 460, 70, "2  Lowest metric", ["within that protocol; equal metrics → ECMP"], "amber", size=12.5)
    c.text(300, 474, "→ installed in the routing table", 13, PURPLE[2], 700, "middle")
    c.rect(600, 100, 520, 400, fill=BLUE[1], stroke=BLUE[0], r=14, sw=1.5)
    c.text(860, 130, "Forwarding a packet (data plane)", 15, BLUE[2], 700, "middle")
    c.text(860, 150, "runs for every packet", 12, MUTED, 500, "middle")
    c.box(630, 170, 460, 70, None, [("Packet to 10.10.40.25", INK, 700), "compare against installed routes only"], "grey", size=12.5)
    c.line(860, 240, 860, 266, FAINT, 2, arrow="end")
    c.box(630, 270, 460, 70, "3  Longest prefix match", ["the most specific route that contains the address"], "blue", size=12.5)
    c.line(860, 340, 860, 366, FAINT, 2, arrow="end")
    c.box(630, 370, 460, 70, None, [("10.10.40.0/24 wins over 10.10.0.0/16", BLUE[2], 700), "AD is not consulted here"], "green", size=12.5)
    c.line(562, 300, 598, 300, FAINT, 2, arrow="end", dash="5 4")
    return c


@figure("10.4", "longest-prefix-match")
def f10_4():
    c = Canvas(1160, 470, "10.4", "Longest prefix match for 10.10.40.25",
               "Bars show how many leading bits each route compares — filled bars contain the address; the longest filled bar wins",
               ["Length alone is never enough: the /30 is longest of all but does not contain 10.10.40.25."])
    rows = [("0.0.0.0/0", 0, True, "via 198.51.100.1 (default)"), ("10.10.0.0/16", 16, True, "via 10.0.0.2"),
            ("10.10.40.0/24", 24, True, "via 10.0.0.2, G0/0/0 ← WINNER"), ("10.10.30.0/24", 24, False, "3rd octet 30 ≠ 40"),
            ("10.0.0.4/30", 30, False, "covers only .4 – .7")]
    x0, w = 250, 600
    y = 120
    for i in range(0, 33, 8):
        c.text(x0 + w * i / 32, y - 6, str(i), 11, MUTED, 600, "middle")
    for name, n, hit, note in rows:
        y += 56
        win = name == "10.10.40.0/24"
        c.text(60, y + 24, name, 15, INK, 700, mono=True)
        c.rect(x0, y, w, 36, fill=PANEL, stroke=LINE, r=6)
        if n:
            col = GREEN if win else (BLUE if hit else RED)
            c.rect(x0, y, w * n / 32, 36, fill=col[0] if hit else col[1], stroke=col[0], r=6, sw=1.6 if hit else 1.4,
                   dash=None if hit else "5 4")
            c.text(x0 + 10, y + 23, f"/{n}", 12.5, "#ffffff" if hit else col[2], 700)
        else:
            c.text(x0 + 10, y + 23, "/0 matches everything", 12, BLUE[2], 600)
        c.text(x0 + w + 20, y + 23, note, 12.5, GREEN[2] if win else (MUTED if hit else RED[0]), 700 if win else 500)
    return c


# ----------------------------------------------------------------------------- Chapter 11

def lab11(c, y=230, full=False):
    r1, r2, isp = (560, y), (920, y), (200, y)
    c.cable(isp[0] + 38, isp[1], r1[0] - 38, r1[1], "copper", "G0/0/0" if full else None, "G0/0/0")
    c.path(f"M{r1[0] + 34},{r1[1] - 14} C{r1[0] + 120},{r1[1] - 80} {r2[0] - 120},{r2[1] - 80} {r2[0] - 34},{r2[1] - 14}", "#64748b", 3)
    c.path(f"M{r1[0] + 34},{r1[1] + 14} C{r1[0] + 120},{r1[1] + 80} {r2[0] - 120},{r2[1] + 80} {r2[0] - 34},{r2[1] + 14}", "#64748b", 3, dash="8 6")
    c.device("cloud", *isp, "ISP", ["Lo0 203.0.113.8 (Internet host)"])
    c.device("router", *r1, "R1 (HQ)", ["Lo10 10.10.10.0/24"])
    c.device("router", *r2, "R2 (Branch)", ["Lo20 10.20.20.0/24"])
    return r1, r2, isp


@figure("11.1", "static-route-types")
def f11_1():
    c = Canvas(1160, 600, "11.1", "Default, network, host and floating static routes on R1",
               "Each blue arrow is one of R1's static routes pointing toward its destination — the Lab 11.1 network",
               ["Every network route needs a matching route back on the far router — a one-way route is the most common static fault."])
    r1, r2, isp = lab11(c, 260)
    c.link_label(740, 186, "primary 10.0.12.0/30", color=MUTED)
    c.link_label(740, 334, "backup 10.0.21.0/30", color=MUTED)
    c.path("M520,210 C450,170 330,170 260,210", BLUE[0], 3, arrow="end")
    c.badge(390, 162, "a", "blue")
    c.path("M600,200 C680,130 820,130 890,195", BLUE[0], 3, arrow="end")
    c.badge(745, 122, "b", "blue")
    c.path("M600,320 C680,400 820,400 890,325", BLUE[0], 3, arrow="end", )
    c.badge(640, 380, "c", "blue")
    c.path("M590,340 C680,440 840,440 905,340", PURPLE[0], 2.4, arrow="end", dash="6 5")
    c.badge(860, 420, "d", "purple")
    leg = [("a", "Default", "ip route 0.0.0.0 0.0.0.0 198.51.100.1", "blue"),
           ("b", "Network", "ip route 10.20.20.0 255.255.255.0 10.0.12.2", "blue"),
           ("c", "Host", "ip route 10.20.20.10 255.255.255.255 10.0.21.2", "blue"),
           ("d", "Floating", "ip route 10.20.20.0 255.255.255.0 10.0.21.2 200", "purple")]
    for i, (k, t, cmd, col) in enumerate(leg):
        x = 40 + (i % 2) * 560
        y = 490 + (i // 2) * 34
        c.badge(x + 12, y, k, col)
        c.text(x + 32, y + 5, t, 13, INK, 700)
        c.text(x + 110, y + 5, cmd, 12.5, MUTED, 500, mono=True)
    return c


@figure("11.2", "next-hop-vs-exit-interface")
def f11_2():
    c = Canvas(1160, 520, "11.2", "Next-hop, exit-interface and fully specified static routes",
               "Command → routing-table line → what R1 must ARP for",
               ["IPv6 with a link-local next hop must be fully specified: ipv6 route 2001:db8:acad:20::/64 g0/0/1 fe80::2"])
    rows = [("1  Next hop only", "ip route 10.20.20.0 255.255.255.0 10.0.12.2", "S 10.20.20.0/24 [1/0] via 10.0.12.2",
             "recursive lookup → ARP for 10.0.12.2", "grey", False),
            ("2  Exit interface only", "ip route 10.20.20.0 255.255.255.0 g0/0/1", "S 10.20.20.0/24 is directly connected, G0/0/1",
             "ARP for EVERY destination — needs proxy ARP", "red", True),
            ("3  Fully specified", "ip route 10.20.20.0 255.255.255.0 g0/0/1 10.0.12.2", "S 10.20.20.0/24 [1/0] via 10.0.12.2, G0/0/1",
             "no recursion; ARP only for the next hop ✓", "green", False)]
    y = 110
    for t, cmd, rt, arp, col, bad in rows:
        c.box(40, y, 1080, 116, None, [], col, highlight=col == "green")
        c.text(60, y + 28, t, 15, INK, 700)
        c.text(60, y + 58, cmd, 13, INK, 600, mono=True)
        c.text(60, y + 86, rt, 12.5, MUTED, 500, mono=True)
        c.device("router", 800, y + 58, None, s=0.6)
        if bad:
            c.line(830, y + 58, 1000, y + 58, RED[0], 2.2, arrow="end", dash="6 4")
        else:
            c.line(830, y + 58, 1000, y + 58, GREEN[0] if col == "green" else BLUE[0], 2.2, arrow="end")
        c.text(915, y + 96, arp, 11.5, RED[0] if bad else MUTED, 600, "middle")
        y += 132
    return c


@figure("11.3", "floating-static-failover")
def f11_3():
    c = Canvas(1160, 520, "11.3", "Floating static failover on R1",
               "The backup route (AD 200) floats above the primary (AD 1) until the primary's interface goes down",
               ["Static routes only fail over when the LOCAL next hop or interface fails — a fault further away is not detected."])
    for x0, title, up in ((40, "Before: primary link up", True), (600, "After: G0/0/1 down", False)):
        c.rect(x0, 100, 520, 360, fill="#f8fafc", stroke=LINE, r=14)
        c.text(x0 + 260, 128, title, 15, INK, 700, "middle")
        r1, r2 = (x0 + 100, 250), (x0 + 420, 250)
        c.path(f"M{r1[0] + 34},{r1[1] - 14} C{r1[0] + 100},{r1[1] - 70} {r2[0] - 100},{r2[1] - 70} {r2[0] - 34},{r2[1] - 14}",
               BLUE[0] if up else RED[0], 4 if up else 2.5, dash=None if up else "6 5")
        c.path(f"M{r1[0] + 34},{r1[1] + 14} C{r1[0] + 100},{r1[1] + 70} {r2[0] - 100},{r2[1] + 70} {r2[0] - 34},{r2[1] + 14}",
               "#94a3b8" if up else BLUE[0], 2.5 if up else 4)
        if not up:
            c.text(x0 + 260, 205, "✗", 20, RED[0], 700, "middle")
        c.device("router", *r1, "R1", s=0.9)
        c.device("router", *r2, "R2", s=0.9)
        c.text(x0 + 260, 186 if up else 176, "G0/0/1 · AD 1", 12, BLUE[0] if up else RED[0], 700, "middle")
        c.text(x0 + 260, 316, "G0/0/2 · AD 200", 12, MUTED if up else BLUE[0], 700, "middle")
        c.rect(x0 + 20, 360, 480, 82, fill="#0f172a", stroke="none", r=8)
        c.text(x0 + 36, 384, "R1# show ip route static", 12, "#7dd3fc", 600, mono=True)
        if up:
            c.text(x0 + 36, 410, "S  10.20.20.0/24 [1/0] via 10.0.12.2", 12.5, "#e2e8f0", 500, mono=True)
            c.text(x0 + 36, 430, "(AD 200 route: only in running-config)", 11.5, "#94a3b8", 500, mono=True)
        else:
            c.text(x0 + 36, 410, "S  10.20.20.0/24 [200/0] via 10.0.21.2", 12.5, "#86efac", 600, mono=True)
            c.text(x0 + 36, 430, "(primary removed with its interface)", 11.5, "#94a3b8", 500, mono=True)
    return c


@figure("11.4", "lab-11-1-topology")
def f11_4():
    c = Canvas(1160, 560, "11.4", "Lab 11.1 topology with IPv4 and IPv6 addressing",
               "3 × ISR4331 joined with copper crossover; LANs simulated with loopbacks — dual stack",
               ["R1 and R2 use link-locals fe80::1 and fe80::2 on their point-to-point links. ipv6 unicast-routing on every router."])
    isp, r1, r2 = (170, 280), (560, 280), (960, 280)
    c.cable(isp[0] + 56, isp[1], r1[0] - 38, r1[1], "copper", ".1", ".2")
    c.link_label(365, 312, "198.51.100.0/30", mono=True)
    c.link_label(365, 332, "2001:db8:ffff::/64", mono=True)
    c.path(f"M{r1[0] + 34},{r1[1] - 14} C{r1[0] + 130},{r1[1] - 110} {r2[0] - 130},{r2[1] - 110} {r2[0] - 34},{r2[1] - 14}", "#64748b", 3)
    c.path(f"M{r1[0] + 38},{r1[1] + 4} C{r1[0] + 200},{r1[1] + 190} {r2[0] - 200},{r2[1] + 190} {r2[0] - 38},{r2[1] + 4}", "#64748b", 3, dash="8 6")
    c.link_label(760, 186, "G0/0/1 primary · 10.0.12.0/30 · 2001:db8:acad:f012::/64", mono=True)
    c.link_label(760, 440, "G0/0/2 backup · 10.0.21.0/30 · 2001:db8:acad:f021::/64", mono=True)
    for x, y, t in ((620, 236, ".1"), (900, 236, ".2"), (630, 300, ".1"), (890, 300, ".2")):
        c.text(x, y, t, 12, BLUE[0], 700, "middle")
    c.device("cloud", *isp, "ISP", ["G0/0/0 198.51.100.1", "Lo0 203.0.113.8/32", "2001:db8:9999::8/128"])
    c.device("router", *r1, "R1 (HQ)", ["G0/0/0 198.51.100.2", "Lo10 10.10.10.1/24", "2001:db8:acad:10::1/64"])
    c.device("router", *r2, "R2 (Branch)", ["Lo20 10.20.20.1/24", "2001:db8:acad:20::1/64", "(stands in for the branch server)"])
    return c

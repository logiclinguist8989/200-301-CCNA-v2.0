"""Chapter 8 — CDP and LLDP; Chapter 9 — Rapid PVST+."""

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL)
from chapters.ch06_07 import bundle


def role(c, x, y, text, kind):
    col = {"root": "green", "desg": "blue", "altn": "red", "edge": "teal"}[kind]
    c.pill(x, y, text, col, 10.5, solid=kind in ("root", "altn"))


# ----------------------------------------------------------------------------- Chapter 8

@figure("8.1", "discovery-scope")
def f8_1():
    c = Canvas(1160, 480, "8.1", "CDP and LLDP see only directly connected neighbors",
               "Advertisements are sent out each interface and never forwarded — build the full map hop by hop",
               ["PCs and printers usually run neither protocol: document them from the MAC address table, DHCP and ARP instead."])
    r1, d1, s1, pc = (160, 250), (480, 250), (800, 250), (1060, 250)
    c.cable(r1[0] + 38, r1[1], d1[0] - 38, d1[1], "copper", "G0/0/0", "Gi1/0/24")
    c.cable(d1[0] + 38, d1[1], s1[0] - 46, s1[1], "copper", "Gi1/0/1", "Gi0/1")
    c.cable(s1[0] + 46, s1[1], pc[0] - 34, pc[1], "copper", "Fa0/1")
    for a, b in ((r1, d1), (d1, s1)):
        mx = (a[0] + b[0]) / 2
        c.line(a[0] + 40, a[1] - 52, b[0] - 40, b[1] - 52, TEAL[0], 2.4, arrow="end")
        c.line(b[0] - 40, a[1] + 96, a[0] + 40, a[1] + 96, TEAL[0], 2.4, arrow="end")
        c.text(mx, a[1] - 62, "CDP / LLDP advertisement", 11.5, TEAL[0], 700, "middle")
    c.device("router", *r1, "R1", ["knows: DSW1"])
    c.device("l3switch", *d1, "DSW1", ["knows: R1, SW1"])
    c.device("switch", *s1, "SW1", ["knows: DSW1"])
    c.device("pc", *pc, "PC1", ["runs neither protocol"])
    c.line(1028, 218, 1092, 282, RED[0], 2.5)
    c.path(f"M{r1[0] + 30},380 C{r1[0] + 200},420 {s1[0] - 200},420 {s1[0] - 30},380", RED[0], 2, dash="6 5", arrow="end")
    c.text(480, 440, "✗ R1 never hears about SW1 — DSW1 does not relay advertisements", 12.5, RED[0], 700, "middle")
    return c


@figure("8.2", "documentation-validation-workflow")
def f8_2():
    c = Canvas(1160, 560, "8.2", "Documentation validation workflow — run once per link",
               "Matches go straight to the published record; mismatches are fixed in the docs or, via change control, in the network",
               ["Hosts that run neither protocol: verify with show mac address-table interface <port> and DHCP/ARP tables."])
    y = 120
    steps = [(40, "1  Collect docs", ["drawing, port table,", "IP plan, inventory"], "grey"),
             (250, "2  Gather evidence", ["show cdp/lldp neighbors", "detail · show int status"], "blue"),
             (460, "3  Compare per link", ["hostname, local + remote", "port, model, mgmt IP"], "blue")]
    for x, t, l, col in steps:
        c.box(x, y, 190, 100, t, l, col, size=12, title_size=14)
    c.line(230, y + 50, 248, y + 50, FAINT, 2, arrow="end")
    c.line(440, y + 50, 458, y + 50, FAINT, 2, arrow="end")
    c.diamond(800, y + 50, 220, 100, ["Matches?"], "amber", 14)
    c.line(650, y + 50, 688, y + 50, FAINT, 2, arrow="end")
    c.box(960, y, 170, 100, "6  Publish", ["date + who verified;", "update descriptions"], "green", size=12, title_size=14)
    c.line(910, y + 50, 958, y + 50, GREEN[0], 2, arrow="end")
    c.text(934, y + 40, "yes", 13, GREEN[0], 700, "middle")
    c.line(800, y + 100, 800, 290, FAINT, 2, arrow="end")
    c.text(812, 270, "no", 13, AMBER[0], 700)
    c.diamond(800, 340, 300, 100, ["4  Network follows the", "approved design?"], "amber", 13)
    c.line(950, 340, 976, 340, GREEN[0], 2, arrow="end")
    c.box(980, 300, 150, 80, "Docs wrong", ["update them"], "purple", size=12, title_size=14)
    c.line(1055, 300, 1055, y + 104, GREEN[0], 2, arrow="end")
    c.text(962, 330, "yes", 13, GREEN[0], 700, "middle")
    c.poly([(650, 340), (420, 340), (420, 380)], RED[0], 2)
    c.text(520, 330, "no", 13, RED[0], 700, "middle")
    c.box(290, 384, 260, 80, "Network is wrong", ["fix via change control,", "then re-check from step 2"], "red", size=12, title_size=14)
    c.poly([(290, 424), (250, 424), (250, y + 102), ], RED[0], 2, dash="6 5")
    c.box(40, 400, 190, 60, "5  Non-CDP hosts", ["MAC/ARP/DHCP tables"], "teal", size=12, title_size=13.5)
    return c


@figure("8.3", "dsw1-audit")
def f8_3():
    c = Canvas(1160, 560, "8.3", "Auditing DSW1: documented neighbors vs what CDP discovered",
               "Each box reads: neighbor / my port → its port / model or address — mismatches outlined in red",
               ["Read the Port ID column for the far end. CDP lists each EtherChannel member separately.",
                "A mismatch does not automatically mean the network is wrong — decide which side matches the approved design."])
    c.text(300, 112, "Documentation (months old)", 15, INK, 700, "middle")
    c.text(860, 112, "show cdp neighbors detail (today)", 15, INK, 700, "middle")
    rows = [
        ("Gi1/0/1", ("SW1", "Gi1/0/1 → Gi0/1", "mgmt 10.10.99.21"), ("SW1", "Gi1/0/1 → Gi0/1", "IP 10.10.99.11"), [2], "IP differs"),
        ("Gi1/0/2", ("SW2", "Gi1/0/2 → Gi0/2", "WS-C3650"), ("SW2", "Gi1/0/2 → Gi0/1", "WS-C2960"), [1, 2], "port + model"),
        ("Gi1/0/21", ("DSW2", "Gi1/0/21 → Gi1/0/21", "WS-C3650"), ("DSW2", "Gi1/0/21 → Gi1/0/21", "WS-C3650"), [], "match ✓"),
        ("Gi1/0/24", ("R2", "Gi1/0/24 → G0/0/0", "ISR4331"), ("R1", "Gi1/0/24 → G0/0/0", "ISR4331"), [0], "renamed"),
    ]
    y = 132
    for port, doc, cdp, bad, verdict in rows:
        for x, data, is_cdp in ((90, doc, False), (650, cdp, True)):
            ok = not bad
            c.rect(x, y, 420, 82, fill=GREEN[1] if ok else ("#ffffff"), stroke=GREEN[0] if ok else LINE, r=10, sw=1.5)
            for i, t in enumerate(data):
                hit = i in bad
                ty = y + 24 + i * 22
                if hit:
                    c.rect(x + 10, ty - 15, 400, 21, fill=RED[1] if is_cdp else "#fff7f7", stroke=RED[0], r=5, sw=1.6)
                c.text(x + 20, ty, t, 14 if i == 0 else 12.5, INK if i == 0 else (RED[2] if hit else MUTED), 700 if i == 0 else 500, mono=i == 1)
        c.line(512, y + 41, 646, y + 41, GREEN[0] if not bad else RED[0], 2, arrow="end", dash=None if not bad else "5 4")
        c.text(579, y + 34, verdict, 10.5, GREEN[0] if not bad else RED[0], 700, "middle")
        c.pill(52, y + 41, port, "navy", 10.5, solid=True, mono=True)
        y += 98
    return c


# ----------------------------------------------------------------------------- Chapter 9

@figure("9.1", "layer2-loop")
def f9_1():
    c = Canvas(1160, 520, "9.1", "A Layer 2 loop without STP: one broadcast becomes an endless storm",
               "Ethernet has no TTL, so each switch floods the broadcast out every other port — forever",
               ["Effects within seconds: ① broadcast storm  ② MAC table instability (%SW_MATM-4-MACFLAP_NOTIF)  ③ duplicate frames."])
    a, b, cc = (580, 160), (330, 380), (830, 380)
    for p, q in ((a, b), (a, cc), (b, cc)):
        c.line(p[0], p[1] + 20, q[0], q[1] - 10, "#64748b", 3.5)
    # loop arrows
    c.path("M520,200 L380,330", RED[0], 3, arrow="end")
    c.path("M390,392 L770,392", RED[0], 3, arrow="end")
    c.path("M780,330 L640,200", RED[0], 3, arrow="end")
    c.path("M640,170 L780,300", "#f87171", 3, arrow="end", dash="7 5")
    c.path("M770,365 L390,365", "#f87171", 3, arrow="end", dash="7 5")
    c.path("M380,300 L520,170", "#f87171", 3, arrow="end", dash="7 5")
    c.device("switch", *a, "SW-A", label="above")
    c.device("switch", *b, "SW-B", label="left")
    c.device("switch", *cc, "SW-C", label="right")
    c.cable(b[0] - 20, b[1] + 22, 200, 460, "copper")
    c.device("pc", 170, 470, None, s=0.7)
    c.text(170, 512, "PC1 sends one ARP broadcast", 12, INK, 700, "middle")
    c.box(910, 140, 220, 130, "Copies multiply", ["each lap adds more frames", "links + CPUs saturate", "network melts down"], "red", size=12)
    return c


@figure("9.2", "bridge-id")
def f9_2():
    c = Canvas(1160, 440, "9.2", "Bridge ID: 4-bit priority + 12-bit VLAN + 48-bit MAC",
               "Priorities move in steps of 4096 because the priority field sits above the 12-bit extended system ID",
               ["Lower BID wins. Priority is compared first; the MAC address breaks ties. Valid priorities: 0, 4096, 8192 … 61440."])
    pos = c.cells(60, 140, [("Priority", 180, "blue", "4 bits"), ("Extended system ID (VLAN)", 340, "amber", "12 bits"),
                            ("MAC address", 520, "purple", "48 bits")], h=64, size=15)
    c.brace(60, 580, 230, "Bridge priority shown by IOS (16 bits)", INK, up=False)
    c.text(60, 300, "VLAN 10 example", 15, INK, 700)
    c.cells(60, 316, [("1000", 180, "blue", "= 32768"), ("0000 0000 1010", 340, "amber", "= 10"), ("0011.1111.1111", 520, "purple", "switch MAC")], h=56, size=15)
    c.text(600, 300, "32768 + 10 = 32778", 18, BLUE[2], 800, "middle")
    return c


@figure("9.3", "stp-election")
def f9_3():
    c = Canvas(1160, 560, "9.3", "STP election result for VLAN 10",
               "All priorities 32778, all links 1 Gb/s (cost 4) — lowest MAC wins root; the leftover port discards",
               ["Every link has exactly one designated port; every non-root switch exactly one root port.",
                "SW-B Gi0/2 wins the B–C tie on lower sender BID, so SW-C Gi0/2 becomes the alternate (discarding) port."])
    a, b, cc = (580, 170), (300, 420), (860, 420)
    c.line(a[0] - 40, a[1] + 20, b[0] + 30, b[1] - 22, "#64748b", 3.5)
    c.line(a[0] + 40, a[1] + 20, cc[0] - 30, cc[1] - 22, "#64748b", 3.5)
    c.line(b[0] + 46, b[1], 640, cc[1], "#64748b", 3.5)
    c.line(640, cc[1], cc[0] - 46, cc[1], RED[0], 3.5, dash="7 5")
    c.device("switch", *a, "SW-A — ROOT", ["0011.1111.1111"], label="above", highlight="green")
    c.device("switch", *b, "SW-B", ["0022.2222.2222 · cost 4"], label="left")
    c.device("switch", *cc, "SW-C", ["0033.3333.3333 · cost 4"], label="right")
    role(c, 470, 220, "Gi0/1 Desg", "desg")
    role(c, 690, 220, "Gi0/2 Desg", "desg")
    role(c, 330, 350, "Gi0/1 Root", "root")
    role(c, 830, 350, "Gi0/1 Root", "root")
    role(c, 420, 450, "Gi0/2 Desg", "desg")
    role(c, 740, 450, "Gi0/2 Altn — discarding", "altn")
    c.text(580, 412, "tie at cost 4 → lower sender BID (SW-B) wins", 12, MUTED, 600, "middle")
    return c


@figure("9.4", "stp-protection-placement")
def f9_4():
    c = Canvas(1160, 600, "9.4", "Where each STP protection feature belongs",
               "Root guard: distribution downlinks · Loop guard: access uplinks · PortFast + BPDU guard: every host port",
               ["BPDU guard err-disables a host port that receives any BPDU. Root guard puts a port root-inconsistent on a superior BPDU.",
                "Loop guard puts a non-designated port loop-inconsistent when BPDUs stop arriving (e.g. a unidirectional fiber)."])
    d1, d2, s1, s2 = (420, 170), (740, 170), (300, 360), (860, 360)
    c.line(d1[0] + 40, d1[1], d2[0] - 40, d2[1], "#64748b", 3.5)
    for d, s in ((d1, s1), (d1, s2), (d2, s1), (d2, s2)):
        c.line(d[0], d[1] + 34, s[0], s[1] - 22, "#64748b", 3)
    c.device("l3switch", *d1, "DSW1", ["root primary (10, 30)"], label="left")
    c.device("l3switch", *d2, "DSW2", ["root primary (40, 99)"], label="right")
    c.device("switch", *s1, "SW1", label="left")
    c.device("switch", *s2, "SW2", label="right")
    import math
    for d, s in ((d1, s1), (d1, s2), (d2, s1), (d2, s2)):
        dx, dy = s[0] - d[0], s[1] - d[1]
        L = math.hypot(dx, dy)
        c.circle(d[0] + dx / L * 52, d[1] + 34 + dy / L * 18, 8, fill=AMBER[0], stroke="#ffffff", sw=2)
        c.circle(s[0] - dx / L * 40, s[1] - 22 - dy / L * 14, 8, fill=PURPLE[0], stroke="#ffffff", sw=2)
    for x, s in ((200, s1), (400, s1), (760, s2), (960, s2)):
        c.line(s[0] + (x - s[0]) * 0.3, s[1] + 22, x, 450, "#64748b", 2.5)
        c.circle(s[0] + (x - s[0]) * 0.45, s[1] + 22 + (450 - s[1] - 22) * 0.3, 8, fill=GREEN[0], stroke="#ffffff", sw=2)
        c.device("pc", x, 480, None, s=0.65)
    leg = [(AMBER[0], "Root guard", "on distribution downlinks — the root must stay up here"),
           (PURPLE[0], "Loop guard", "on access uplinks (non-designated ports)"),
           (GREEN[0], "PortFast + BPDU guard", "on every host-facing access port")]
    y = 540
    for i, (col, t, d) in enumerate(leg):
        x = 60 + i * 360
        c.circle(x, y - 4, 8, fill=col, stroke="#ffffff", sw=2)
        c.text(x + 16, y, t, 13, INK, 700)
        c.text(x + 16, y + 18, d, 11, MUTED, 500)
    return c


@figure("9.5", "lab-9-1-topology")
def f9_5():
    c = Canvas(1160, 700, "9.5", "Lab 9.1 topology with the expected Rapid PVST+ roles for VLAN 10",
               "Lab 6.1 plus three new links — DSW1 is root for VLANs 10/30, DSW2 for 40/99",
               ["Costs (short method): Po1/Po2 = 3 (2 × 1 Gb/s) · Gi1/0/23 = 4 (1 Gb/s) · Fa0/24 = 19 (100 Mb/s).",
                "Host ports Fa0/1–2: Desg FWD, P2p Edge (PortFast). Lab 10.1 reuses this topology."])
    d1, d2, s1, s2 = (330, 190), (830, 190), (330, 470), (830, 470)
    c.line(d1[0] + 44, d1[1], d2[0] - 44, d2[1], "#64748b", 4)
    bundle(c, (d1[0], d1[1] + 34), (s1[0], s1[1] - 22), gap=16, color=BLUE[0])
    bundle(c, (d1[0] + 30, d1[1] + 30), (s2[0] - 36, s2[1] - 20), gap=16, color=BLUE[0])
    c.line(d2[0] - 30, d2[1] + 30, s1[0] + 40, s1[1] - 18, "#94a3b8", 2.5, dash="8 6")
    c.line(d2[0], d2[1] + 34, s2[0], s2[1] - 22, "#94a3b8", 2.5, dash="8 6")
    c.device("l3switch", *d1, "DSW1 — root VLAN 10", ["priority 24586 (root primary)"], label="above", highlight="green")
    c.device("l3switch", *d2, "DSW2", ["root secondary for VLAN 10"], label="above")
    c.device("switch", *s1, "SW1", label="left")
    c.device("switch", *s2, "SW2", label="right")
    # role pills
    role(c, 480, 172, "Gi1/0/23 Desg", "desg")
    role(c, 690, 172, "Gi1/0/23 Root · 4", "root")
    role(c, 250, 260, "Po1 Desg", "desg")
    role(c, 470, 262, "Po2 Desg", "desg")
    role(c, 250, 400, "Po1 Root · 3", "root")
    role(c, 720, 408, "Po2 Root · 3", "root")
    role(c, 660, 258, "Gi1/0/5 Altn BLK", "altn")
    role(c, 900, 270, "Gi1/0/6 Altn BLK", "altn")
    role(c, 450, 420, "Fa0/24 Desg", "desg")
    role(c, 900, 400, "Fa0/24 Desg", "desg")
    for x, s, n in ((230, s1, "PC1"), (430, s1, "PC2"), (730, s2, "PC3"), (930, s2, "Printer1")):
        c.line(s[0] + (x - s[0]) * 0.3, s[1] + 22, x, 548, "#64748b", 2.5)
        c.device("printer" if n == "Printer1" else "pc", x, 578, n, [], s=0.7, name_size=12.5)
    # legend
    lx, ly = 970, 300
    c.rect(lx, ly, 160, 112, fill=PANEL, stroke=LINE, r=10)
    c.line(lx + 12, ly + 24, lx + 52, ly + 24, BLUE[0], 4)
    c.text(lx + 60, ly + 28, "Po · cost 3", 11.5, INK, 600)
    c.line(lx + 12, ly + 50, lx + 52, ly + 50, "#64748b", 4)
    c.text(lx + 60, ly + 54, "1 Gb/s · cost 4", 11.5, INK, 600)
    c.line(lx + 12, ly + 76, lx + 52, ly + 76, "#94a3b8", 2.5, dash="8 6")
    c.text(lx + 60, ly + 80, "100 Mb/s · 19", 11.5, INK, 600)
    c.text(lx + 12, ly + 102, "dashed = new in Lab 9.1", 9.5, MUTED, 500)
    return c

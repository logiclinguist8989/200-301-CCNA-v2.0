"""Chapter 12 — OSPF; Chapter 13 — FHRP; Chapter 14 — DHCP."""

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL,
                    check_flow, sequence)
from chapters.ch06_07 import bundle


# ----------------------------------------------------------------------------- Chapter 12

@figure("12.1", "ospf-neighbor-states")
def f12_1():
    c = Canvas(1160, 760, "12.1", "OSPF neighbor states from Down to Full",
               "Arrows are packets; the left column is the state they put R1 in — FULL only when both databases match",
               ["Stuck in INIT: one-way Hellos (ACL, mismatch) · stuck in 2-WAY on a LAN between DROthers: normal · ExStart/Exchange: MTU mismatch."])
    states = ["DOWN", "INIT", "2-WAY", "EXSTART", "EXCHANGE", "LOADING", "FULL"]
    msgs = [
        ("r1", "r2", "Hello (seen: none)", "to 224.0.0.5", BLUE[0]),
        ("r2", "r1", "Hello (seen: 1.1.1.1)", "R1 sees its own RID → 2-WAY", BLUE[0]),
        ("r1", "r2", "DBD (empty) — who is master?", "higher RID becomes master", PURPLE[0]),
        ("r2", "r1", "DBD — LSA headers summary", "", PURPLE[0]),
        ("r1", "r2", "LSR — send me what I lack", "", AMBER[0]),
        ("r2", "r1", "LSU — full LSAs", "then LSAck", GREEN[0]),
    ]
    sequence(c, [("r1", 420, "router", "R1", ["RID 1.1.1.1"]), ("r2", 900, "router", "R2", ["RID 2.2.2.2"])],
             [{"a": a, "b": b, "t": t, "s": s, "c": col} for a, b, t, s, col in msgs], bottom=690)
    y0 = c.top + 20 + 120 + 14
    gap = (690 - y0 - 20) / 6
    st_y = [y0 - 16] + [y0 + 16 + i * gap for i in range(6)]
    cols = ["grey", "amber", "blue", "purple", "purple", "amber", "green"]
    for s_, y, col in zip(states, st_y, cols):
        c.pill(140, y, s_, col, 12.5, solid=s_ == "FULL")
    c.line(140, st_y[0] + 14, 140, st_y[-1] - 14, FAINT, 2, dash="3 4")
    return c


@figure("12.2", "dr-bdr-election")
def f12_2():
    c = Canvas(1160, 560, "12.2", "DR/BDR election on a broadcast LAN",
               "Highest priority wins (then highest RID); everyone forms FULL with the DR and BDR only",
               ["DROthers stay 2-WAY with each other — correct and expected. Priority 0 = never DR. Elections are not preemptive.",
                "DROthers send updates to 224.0.0.6 (DR + BDR); the DR floods them back to 224.0.0.5 (all OSPF routers)."])
    sw = (580, 300)
    pos = {"dr": (580, 140, "R3 — DR", ["priority 100 · RID 3.3.3.3"]),
           "bdr": (240, 300, "R2 — BDR", ["priority 50 · RID 2.2.2.2"]),
           "o1": (360, 470, "R1 — DROther", ["priority 1 · RID 1.1.1.1"]),
           "o2": (800, 470, "R4 — DROther", ["priority 1 · RID 4.4.4.4"])}
    for k, (x, y, *_r) in pos.items():
        c.line(x, y, sw[0], sw[1], "#cbd5e1", 3)
    def adj(a, b, full=True):
        (x1, y1, *_), (x2, y2, *_) = pos[a], pos[b]
        c.line(x1, y1, x2, y2, BLUE[0] if full else "#94a3b8", 3 if full else 2.2, dash=None if full else "7 5", opacity=0.9)
    for a, b in (("dr", "bdr"), ("dr", "o1"), ("dr", "o2"), ("bdr", "o1"), ("bdr", "o2")):
        adj(a, b)
    adj("o1", "o2", False)
    c.device("switch", *sw, "SW-LAN", ["10.0.123.0/24"], label="right")
    for k, (x, y, n, l) in pos.items():
        c.device("router", x, y, n, l, highlight="green" if k == "dr" else ("blue" if k == "bdr" else None), s=0.95,
                 label={"dr": "right", "bdr": "left"}.get(k, "below"))
    c.link_label(580, 470, "2-WAY only (expected)", color=MUTED)
    lx, ly = 900, 120
    c.rect(lx, ly, 230, 90, fill=PANEL, stroke=LINE, r=10)
    c.line(lx + 16, ly + 30, lx + 60, ly + 30, BLUE[0], 3)
    c.text(lx + 70, ly + 34, "FULL adjacency", 12.5, INK, 600)
    c.line(lx + 16, ly + 62, lx + 60, ly + 62, "#94a3b8", 2.2, dash="7 5")
    c.text(lx + 70, ly + 66, "2-WAY neighbor", 12.5, INK, 600)
    return c


@figure("12.3", "lab-12-1-topology")
def f12_3():
    c = Canvas(1160, 600, "12.3", "Lab 12.1 topology: a broadcast LAN with DR/BDR and a point-to-point link",
               "3 × ISR4331 + 1 × 2960 — single-area OSPFv2 and OSPFv3, area 0",
               ["R1–R2 G0/0/1: ip ospf network point-to-point on both ends — no DR election, faster adjacency.",
                "Loopbacks stand in for each router's user LAN; set ip ospf network point-to-point on them to advertise the /24."])
    sw = (580, 200)
    r1, r2, r3 = (250, 400), (580, 420), (910, 400)
    c.rect(150, 110, 860, 60, fill=BLUE[1], stroke=BLUE[0], r=10, opacity=0.6)
    c.text(170, 146, "Broadcast LAN 10.0.123.0/24 · 2001:db8:acad:123::/64 — DR/BDR elected", 13, BLUE[2], 700)
    for r, ip in ((r1, ".1"), (r2, ".2"), (r3, ".3")):
        c.cable(sw[0] + (r[0] - sw[0]) * 0.12, sw[1] + 22, r[0], r[1] - 28, "copper", None, f"G0/0/0 {ip}")
    c.path(f"M{r1[0] + 30},{r1[1] + 22} C{r1[0] + 120},{r1[1] + 110} {r2[0] - 120},{r2[1] + 110} {r2[0] - 30},{r2[1] + 22}", PURPLE[0], 3.5)
    c.link_label(415, 505, "G0/0/1 p2p 10.0.12.0/30", color=PURPLE[0], weight=700)
    c.device("switch", *sw, "SW-LAN", ["2960"], label="right")
    c.device("router", *r1, "R1", ["RID 1.1.1.1 · pri 1 · DROther", "Lo10 10.10.10.1/24"], label="left")
    c.device("router", *r2, "R2 — BDR", ["RID 2.2.2.2 · pri 50", "Lo20 10.20.20.1/24"], label="right", highlight="blue")
    c.device("router", *r3, "R3 — DR", ["RID 3.3.3.3 · pri 100", "Lo30 10.30.30.1/24"], label="right", highlight="green")
    return c


# ----------------------------------------------------------------------------- Chapter 13

@figure("13.1", "fhrp-group")
def f13_1():
    c = Canvas(1160, 560, "13.1", "One virtual gateway shared by an active and a standby router",
               "Hosts use the virtual IP 10.10.10.1 — they never know which real switch is answering",
               ["The active router answers ARP for the virtual IP with the virtual MAC (HSRPv2 0000.0c9f.fXXX). On failure the standby takes over",
                "both addresses and sends a gratuitous ARP so switches relearn where the virtual MAC lives."])
    d1, d2 = (380, 220), (780, 220)
    c.rect(250, 130, 660, 170, fill="#ffffff", stroke=BLUE[0], r=16, dash="8 6", sw=2)
    c.pill(580, 128, "Virtual router · 10.10.10.1 · 0000.0c9f.f00a", "blue", 13, solid=True)
    c.device("l3switch", *d1, "DSW1 — Active", ["real 10.10.10.2 · priority 110"], highlight="green")
    c.device("l3switch", *d2, "DSW2 — Standby", ["real 10.10.10.3 · priority 100"])
    c.line(440, 200, 720, 200, TEAL[0], 2, arrow="both", dash="5 4")
    c.text(580, 190, "Hellos every 3 s", 12, TEAL[0], 700, "middle")
    sw = (580, 400)
    c.cable(d1[0] + 30, d1[1] + 84, sw[0] - 30, sw[1] - 22, "trunk")
    c.cable(d2[0] - 30, d2[1] + 84, sw[0] + 30, sw[1] - 22, "trunk")
    c.device("switch", *sw, "SW1", label="right")
    for x, n in ((380, "PC1"), (780, "PC2")):
        c.cable(sw[0] + (x - sw[0]) * 0.2, sw[1] + 22, x, 450, "copper")
        c.device("pc", x, 480, n, ["gateway 10.10.10.1"], s=0.75, label="right")
    return c


@figure("13.2", "hsrp-failover-timeline")
def f13_2():
    c = Canvas(1160, 440, "13.2", "HSRP failover timeline with default timers",
               "Hello 3 s, hold 10 s — hosts have no gateway from the failure until DSW2's hold timer expires",
               ["Faster timers (standby 10 timers 1 3) shrink the gap at the cost of more Hellos. VRRP defaults: advert 1 s, down ≈ 3 s."])
    x0, w = 120, 960
    def X(t):
        return x0 + w * t / 15
    c.text(40, 160, "DSW1", 14, INK, 700)
    c.text(40, 240, "DSW2", 14, INK, 700)
    c.rect(X(0), 140, X(3) - X(0), 32, fill=GREEN[0], stroke="none", r=4)
    c.text((X(0) + X(3)) / 2, 161, "Active", 12, "#ffffff", 700, "middle")
    c.rect(X(3), 140, X(15) - X(3), 32, fill=RED[1], stroke=RED[0], r=4, dash="5 4")
    c.text((X(3) + X(15)) / 2, 161, "failed — no Hellos", 12, RED[2], 700, "middle")
    c.rect(X(0), 220, X(13) - X(0), 32, fill=PANEL, stroke=LINE, r=4)
    c.text((X(0) + X(13)) / 2, 241, "Standby — counting the hold timer from the last Hello", 12, MUTED, 600, "middle")
    c.rect(X(13), 220, X(15) - X(13), 32, fill=GREEN[0], stroke="none", r=4)
    c.text((X(13) + X(15)) / 2, 241, "Active", 12, "#ffffff", 700, "middle")
    for t in (0, 3):
        c.line(X(t), 130, X(t), 260, TEAL[0], 1.5, dash="3 3")
        c.text(X(t), 124, "Hello", 11, TEAL[0], 700, "middle")
    c.rect(X(3), 290, X(13) - X(3), 34, fill=RED[0], stroke="none", r=6)
    c.text((X(3) + X(13)) / 2, 312, "hosts have no working gateway  ≈ 10 s (hold time)", 13, "#ffffff", 700, "middle")
    c.line(X(0), 350, X(15), 350, INK, 1.5, arrow="end")
    for t in range(0, 16):
        c.line(X(t), 346, X(t), 354, INK, 1)
        if t % 1 == 0:
            c.text(X(t), 372, f"{t}s", 11, MUTED, 500, "middle")
    c.pill(X(3), 104, "DSW1 fails (t = 3 s)", "red", 11.5)
    c.pill(X(13), 200, "hold expires → gratuitous ARP", "green", 11.5)
    return c


@figure("13.3", "lab-13-1-hsrp-plan")
def f13_3():
    c = Canvas(1160, 600, "13.3", "Lab 13.1 HSRP plan: one active gateway per VLAN pair",
               "Active gateway aligned with the STP root from Lab 9.1 — hosts keep the same .1 gateway as before",
               ["Real SVIs: DSW1 .2, DSW2 .3 in every VLAN · virtual IP .1 · preempt on both · priorities 110 (active) / 100 (standby)."])
    d1, d2, s1, s2 = (330, 240), (830, 240), (330, 470), (830, 470)
    c.line(d1[0] + 44, d1[1], d2[0] - 44, d2[1], "#64748b", 4)
    for d in (d1, d2):
        for s in (s1, s2):
            c.line(d[0], d[1] + 34, s[0], s[1] - 22, "#94a3b8", 3)
    c.rect(450, 290, 260, 140, fill="#ffffff", stroke=LINE, r=12)
    c.device("l3switch", *d1, "DSW1", label="left", highlight="blue")
    c.device("l3switch", *d2, "DSW2", label="right", highlight="green")
    c.device("switch", *s1, "SW1", ["PC1 VLAN 10 · PC2 VLAN 30"], label="left")
    c.device("switch", *s2, "SW2", ["PC3 VLAN 10 · Printer1 VLAN 40"], label="right")
    c.box(60, 100, 260, 64, "Active: VLAN 10, 30", ["priority 110 · Standby 40, 99"], "blue", size=12, title_size=14)
    c.box(840, 100, 290, 64, "Active: VLAN 40, 99", ["priority 110 · Standby 10, 30"], "green", size=12, title_size=14)
    rows = [("VLAN 10", "10.10.10.1", "blue"), ("VLAN 30", "10.10.30.1", "blue"), ("VLAN 40", "10.10.40.1", "green"), ("VLAN 99", "10.10.99.1", "green")]
    for i, (v, ip, col) in enumerate(rows):
        c.pill(580, 340 + i * 25, f"{v} → {ip}", col, 11.5)
    c.text(580, 314, "Virtual gateways (HSRP)", 13, INK, 700, "middle")
    return c


# ----------------------------------------------------------------------------- Chapter 14

@figure("14.1", "dhcp-dora")
def f14_1():
    c = Canvas(1160, 620, "14.1", "The DHCP DORA exchange",
               "Client UDP 68 ↔ server UDP 67 — the client's messages are broadcasts because it has no address yet",
               ["The lease starts at the ACK. At 50 % of the lease the client renews by unicast; at 87.5 % it rebinds by broadcast."])
    sequence(c, [("pc", 300, "pc", "Client", ["MAC 0050.7966.6801", "no address yet"]), ("srv", 860, "server", "DHCP server", ["10.10.10.5"])], [
        {"a": "pc", "b": "srv", "t": "D  Discover — “is there a DHCP server?”", "s": "0.0.0.0:68 → 255.255.255.255:67 (broadcast)", "c": AMBER[0], "n": 1},
        {"a": "srv", "b": "pc", "t": "O  Offer — 10.10.10.11/24, gw, DNS, lease", "s": "after a ping check for conflicts", "c": BLUE[0], "n": 2},
        {"a": "pc", "b": "srv", "t": "R  Request — “I take 10.10.10.11”", "s": "broadcast, so other servers withdraw their offers", "c": AMBER[0], "n": 3},
        {"a": "srv", "b": "pc", "t": "A  Acknowledgment — lease begins", "s": "client now uses 10.10.10.11", "c": GREEN[0], "n": 4},
    ], bottom=560)
    return c


@figure("14.2", "dhcp-relay-giaddr")
def f14_2():
    c = Canvas(1160, 600, "14.2", "DHCP relay: a broadcast becomes a unicast stamped with giaddr",
               "ip helper-address goes on the interface that RECEIVES the client's broadcast — the client VLAN's SVI",
               ["The server picks the pool whose network contains giaddr, and needs a route back to the giaddr subnet.",
                "Configure the helper on both HSRP switches: each relays, the server answers both, the client takes one Offer."])
    pc, d1, r1 = (130, 230), (560, 230), (980, 230)
    c.line(pc[0] + 36, pc[1], d1[0] - 40, d1[1], "#94a3b8", 4)
    c.line(d1[0] + 40, d1[1], r1[0] - 40, r1[1], BLUE[0], 6)
    c.device("pc", *pc, "PC1", ["VLAN 10 · DHCP client"])
    c.device("l3switch", *d1, "DSW1 — relay", ["interface vlan 10", "ip helper-address 10.0.0.1"])
    c.device("router", *r1, "R1 — DHCP server", ["10.0.0.1 · pool STAFF 10.10.10.0/24"])
    c.text(340, 200, "① broadcast", 12.5, MUTED, 700, "middle")
    c.text(770, 200, "② unicast + giaddr", 12.5, BLUE[0], 700, "middle")
    def card(x, title, rows, col):
        c.box(x, 380, 340, 150, title, rows, col, size=12.5, title_size=14, mono_lines=True)
    card(40, "① Client → relay (VLAN 10)", ["src 0.0.0.0:68", "dst 255.255.255.255:67", "giaddr 0.0.0.0", "chaddr 0050.7966.6801"], "grey")
    card(410, "② Relay → server (routed)", ["src 10.0.0.2", "dst 10.0.0.1:67 (unicast)", ("giaddr 10.10.10.2", BLUE[2], 700), "chaddr 0050.7966.6801"], "blue")
    card(780, "③ Server picks the pool", ["10.10.10.2 is in 10.10.10.0/24", "→ pool STAFF", "Offer unicast to giaddr", "relay forwards to client"], "green")
    return c


@figure("14.3", "dhcp-troubleshooting")
def f14_3():
    c = Canvas(1100, 760, "14.3", "DHCP troubleshooting: follow the Discover from client to server",
               "One question per hop; the first “yes” is the fault — fix it, then start again from the top",
               ["show ip dhcp server statistics: Discovers arriving but no Offers → pool problem; no Discovers → relay, routing or VLAN."])
    check_flow(c, "Client shows 169.254.x.x (no Offer received)", [
        ("Client port down, wrong VLAN or no PortFast?", "show interfaces status / switchport · spanning-tree portfast", "blue"),
        ("ip helper-address missing on the client VLAN's SVI?", "show ip interface vlan X → add ip helper-address <server>", "amber"),
        ("Server unreachable from the SVI address?", "ping <server> source vlan X → fix routing both ways", "purple"),
        ("No pool containing giaddr, pool exhausted, or service dhcp off?", "show ip dhcp pool · show ip dhcp conflict · service dhcp", "red"),
    ], end="Client gets an address", end_lines=["Verify gateway = HSRP virtual IP, DNS present"], start_lines=["Start at the client"], qsize=12.5)
    return c


@figure("14.4", "lab-14-1-topology")
def f14_4():
    c = Canvas(1160, 640, "14.4", "Lab 14.1 topology: three DHCP roles in one network",
               "R1 = server for the campus · DSW1 + DSW2 = relays · R1 G0/0/1 = DHCP client of the ISP",
               ["Pools STAFF 10.10.10.0/24 and WIRELESS 10.10.30.0/24 (gateway = HSRP .1, excluded .1–.10, DNS 10.10.99.53).",
                "Printers and switches keep static addresses. Lab 15.1 reuses this topology."])
    isp, r1, d1, d2, s1, s2 = (130, 180), (430, 180), (430, 340), (830, 340), (430, 500), (830, 500)
    c.cable(isp[0] + 56, isp[1], r1[0] - 38, r1[1], "copper", "G0/0/0", "G0/0/1", "DHCP client")
    c.cable(r1[0], r1[1] + 26, d1[0], d1[1] - 36, "copper", "G0/0/0", "Gi1/0/24", "10.0.0.0/30")
    c.line(d1[0] + 44, d1[1], d2[0] - 44, d2[1], "#64748b", 4)
    for d in (d1, d2):
        for s in (s1, s2):
            c.line(d[0] + (s[0] - d[0]) * 0.08, d[1] + 34, s[0] - (s[0] - d[0]) * 0.08, s[1] - 22, BLUE[0] if d[0] == s[0] else "#94a3b8", 3)
    c.device("cloud", *isp, "ISP", ["G0/0/0 198.51.100.1/29", "pool OUTSIDE · Lo0 192.0.2.8"])
    c.device("router", *r1, "R1 — DHCP server", ["10.0.0.1 · pools STAFF, WIRELESS", "G0/0/1 → 198.51.100.2/29 (DHCP)"], label="right")
    c.device("l3switch", *d1, "DSW1 — relay", ["vlan 10, 30: helper 10.0.0.1"], label="left")
    c.device("l3switch", *d2, "DSW2 — relay", ["vlan 10, 30: helper 10.0.0.1"], label="right")
    c.device("switch", *s1, "SW1", label="left")
    c.device("switch", *s2, "SW2", label="right")
    for x, s, k, n, l in ((330, s1, "pc", "PC1", "VLAN 10 · DHCP"), (530, s1, "pc", "PC2", "VLAN 30 · DHCP"),
                          (730, s2, "pc", "PC3", "VLAN 10 · DHCP"), (930, s2, "printer", "Printer1", "VLAN 40 · static")):
        c.line(s[0] + (x - s[0]) * 0.3, s[1] + 22, x, 556, "#64748b", 2.5)
        c.device(k, x, 586, n, [l], s=0.7, name_size=12.5, line_size=11)
    return c

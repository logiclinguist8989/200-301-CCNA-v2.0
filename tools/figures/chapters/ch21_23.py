"""Chapter 21 — NAT; Chapter 22 — DNS; Chapter 23 — Layer 2 security."""

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL,
                    check_flow, fam)


# ----------------------------------------------------------------------------- Chapter 21

@figure("21.1", "nat-address-terms")
def f21_1():
    c = Canvas(1160, 540, "21.1", "NAT address terms: inside/outside, local/global",
               "R1 rewrites only the SOURCE of the outgoing packet — the destination is unchanged",
               ["Local = as seen on the inside · Global = as seen on the outside. Outside local = outside global unless outside",
                "addresses are also translated (not configured at CCNA level). NAT hides addressing but is not a security feature."])
    c.rect(40, 100, 500, 210, fill=BLUE[1], stroke=BLUE[0], r=14, dash="7 5", opacity=0.7)
    c.text(60, 126, "INSIDE (private, RFC 1918)", 13, BLUE[2], 700)
    c.rect(620, 100, 500, 210, fill=AMBER[1], stroke=AMBER[0], r=14, dash="7 5", opacity=0.7)
    c.text(640, 126, "OUTSIDE (internet)", 13, AMBER[2], 700)
    pc, r1, isp, srv = (130, 210), (580, 210), (800, 210), (1040, 210)
    c.line(pc[0] + 34, 210, r1[0] - 38, 210, "#64748b", 3)
    c.line(r1[0] + 38, 210, isp[0] - 56, 210, "#64748b", 3)
    c.line(isp[0] + 56, 210, srv[0] - 30, 210, "#64748b", 3)
    c.device("pc", *pc, "PC1", ["10.10.10.11"])
    c.device("router", *r1, "R1", ["NAT"], highlight="purple")
    c.link_label(470, 250, "ip nat inside", color=BLUE[0], mono=True)
    c.link_label(690, 250, "ip nat outside", color=AMBER[0], mono=True)
    c.device("cloud", *isp, "ISP")
    c.device("server", *srv, "Web host", ["192.0.2.8"])
    def pkt(x, y, title, src, dst):
        c.text(x, y - 10, title, 13, INK, 700)
        c.cells(x, y, [(f"src {src[0]}", 250, src[1], src[2]), (f"dst {dst[0]}", 210, dst[1], dst[2])], h=54, size=13)
    pkt(60, 360, "Packet on the inside", ("10.10.10.11", "blue", "inside local"), ("192.0.2.8", "grey", "outside local"))
    pkt(640, 360, "Same packet on the outside", ("198.51.100.2", "amber", "inside global"), ("192.0.2.8", "grey", "outside global"))
    c.line(530, 387, 630, 387, PURPLE[0], 3, arrow="end")
    c.text(580, 377, "R1", 12, PURPLE[0], 800, "middle")
    return c


@figure("21.2", "pat-translation-table")
def f21_2():
    c = Canvas(1160, 520, "21.2", "PAT translation table: one public address, many ports",
               "ip nat inside source list NAT-INSIDE interface g0/0/1 overload — every host leaves as 198.51.100.2",
               ["R1 keeps the original source port when it is free and picks another when it is taken (Host B below).",
                "ICMP has no ports — the query identifier is used the same way. View the table with show ip nat translations."])
    hosts = [("Host A", "10.10.10.11"), ("Host B", "10.10.10.12"), ("Host C", "10.10.30.11")]
    for i, (n, ip) in enumerate(hosts):
        c.device("pc", 110, 140 + i * 90, n, [ip], s=0.6, label="right", name_size=12.5, line_size=11.5)
    c.device("router", 520, 230, "R1", ["PAT · overload"], s=1.1)
    c.device("cloud", 800, 230, "Internet", ["198.51.100.2 → 192.0.2.8"])
    for i in range(3):
        c.line(250, 140 + i * 90, 470, 230, "#94a3b8", 2)
    c.line(560, 230, 740, 230, AMBER[0], 4)
    hdr = ["Pro", "Inside global", "Inside local", "Outside global"]
    rows = [("tcp", "198.51.100.2:49200", "10.10.10.11:49200", "192.0.2.8:443", False),
            ("tcp", "198.51.100.2:49201", "10.10.10.12:49200", "192.0.2.8:443", True),
            ("tcp", "198.51.100.2:51010", "10.10.30.11:51010", "192.0.2.8:80", False)]
    x0, y0 = 40, 360
    widths = [80, 300, 300, 300]
    c.rect(x0, y0, sum(widths) + 40, 36, fill="#0f172a", stroke="none", r=6)
    x = x0 + 16
    for h, w in zip(hdr, widths):
        c.text(x, y0 + 23, h, 12.5, "#7dd3fc", 700, mono=True)
        x += w
    for i, row in enumerate(rows):
        y = y0 + 40 + i * 32
        if row[4]:
            c.rect(x0, y, sum(widths) + 40, 30, fill=AMBER[1], stroke=AMBER[0], r=4)
        x = x0 + 16
        for val, w in zip(row[:4], widths):
            c.text(x, y + 20, val, 12.5, AMBER[2] if row[4] and "49201" in val else INK, 700 if row[4] and "49201" in val else 500, mono=True)
            x += w
    c.text(x0 + sum(widths) + 30, y0 + 92, "← port changed", 12, AMBER[0], 700, "end")
    return c


@figure("21.3", "lab-21-1-topology")
def f21_3():
    c = Canvas(1160, 640, "21.3", "Lab 21.1 topology and NAT plan",
               "The ISP no longer routes 10.0.0.0/8 — only translated (public) addresses can cross",
               ["Pool and outside subnet: 198.51.100.0/29 (ISP .1, R1 G0/0/1 .2). ISP excludes .3–.6 from its DHCP pool for NAT use."])
    c.rect(40, 100, 640, 380, fill=BLUE[1], stroke=BLUE[0], r=16, dash="8 6", opacity=0.55)
    c.text(60, 126, "INSIDE · 10.10.0.0/16 (private)", 13, BLUE[2], 700)
    r1, isp, d1, s2 = (600, 220), (900, 220), (380, 220), (380, 380)
    c.cable(d1[0] + 40, d1[1], r1[0] - 38, r1[1], "copper", "Gi1/0/24", "G0/0/0 inside")
    c.cable(r1[0] + 38, r1[1], isp[0] - 56, isp[1], "copper", "G0/0/1 outside", ".1")
    c.line(d1[0], d1[1] + 34, s2[0], s2[1] - 22, BLUE[0], 4)
    c.device("router", *r1, "R1", ["198.51.100.2/29"], label="above")
    c.device("cloud", *isp, "ISP", ["no route to 10.0.0.0/8", "Lo0 192.0.2.8 (internet host)"])
    c.text(isp[0], isp[1] + 110, "✗ replies to 10.x addresses are dropped", 12, RED[0], 700, "middle")
    c.device("l3switch", *d1, "DSW1 / DSW2", label="left")
    c.device("switch", *s2, "SW1 / SW2", label="left")
    for x, n, l, k in ((150, "PC1", "10.10.10.11", "pc"), (300, "PC2", "10.10.30.x", "pc"), (460, "PC3", "10.10.10.x", "pc"), (610, "WEB1", "10.10.40.80", "server")):
        c.line(s2[0] + (x - s2[0]) * 0.2, s2[1] + 22, x, 410, "#64748b", 2)
        c.device(k, x, 438, None, s=0.55)
        c.text(x + 30 if k == "server" else x + 26, 432, n, 12, INK, 700)
        c.text(x + 30 if k == "server" else x + 26, 448, l, 11, MUTED, 500)
    parts = [("A", "Dynamic NAT", "pool ONE-ADDR 198.51.100.5", "VLAN 10 only — second host fails", "blue"),
             ("B", "PAT (overload)", "interface G0/0/1 overload", "all of 10.10.0.0/16 share .2", "green"),
             ("C", "Static NAT", "10.10.40.80 ↔ 198.51.100.3", "WEB1 reachable from outside", "purple")]
    for i, (k, t, cmd, note, col) in enumerate(parts):
        x = 40 + i * 365
        c.box(x, 500, 350, 92, None, [], col)
        c.badge(x + 22, 524, k, col)
        c.text(x + 42, 529, t, 14, INK, 700)
        c.text(x + 18, 556, cmd, 12, INK, 600, mono=True)
        c.text(x + 18, 578, note, 12, MUTED, 500)
    return c


# ----------------------------------------------------------------------------- Chapter 22

@figure("22.1", "recursive-dns-resolution")
def f22_1():
    c = Canvas(1160, 560, "22.1", "Recursive DNS resolution and caching",
               "PC1 sends one query; the recursive resolver walks root → TLD → authoritative, then caches the answer for its TTL",
               ["UDP 53 for normal queries, TCP 53 for large answers and zone transfers. A corrected record can take up to its TTL to “arrive”."])
    pc, rr = (110, 300), (430, 300)
    c.device("pc", *pc, "PC1", ["stub resolver"])
    c.device("server", *rr, "Recursive resolver", ["10.10.99.53 · cache"], highlight="blue")
    c.line(pc[0] + 36, 290, rr[0] - 50, 290, BLUE[0], 2.5, arrow="end")
    c.text(260, 280, "① www.campus.example A?", 12, BLUE[0], 700, "middle")
    c.line(rr[0] - 50, 314, pc[0] + 36, 314, GREEN[0], 2.5, arrow="end")
    c.text(260, 334, "⑧ 10.10.40.80 (TTL 3600)", 12, GREEN[0], 700, "middle")
    srvs = [(780, 140, "Root server  “.”", "② ask → ③ referral to .example TLD"),
            (780, 300, "TLD server  .example", "④ ask → ⑤ referral to ns1.campus.example"),
            (780, 460, "Authoritative  ns1.campus.example", "⑥ ask → ⑦ answer (aa flag)")]
    for x, y, n, t in srvs:
        c.device("database", x, y, None, s=0.9)
        c.text(x + 40, y - 6, n, 14, INK, 700)
        c.text(x + 40, y + 14, t, 12, MUTED, 500)
        c.line(rr[0] + 40, rr[1] - 10, x - 30, y - 6, PURPLE[0], 2, arrow="end")
        c.line(x - 30, y + 8, rr[0] + 40, rr[1] + 8, AMBER[0], 2, arrow="end", dash="6 4")
    return c


@figure("22.2", "campus-zone-records")
def f22_2():
    c = Canvas(1160, 600, "22.2", "The campus.example records and how they chain",
               "Ask for a name on the left; the arrow shows what the record returns",
               ["CNAME, MX and NS return NAMES, so the client must look those up again; only A, AAAA and PTR end the chain.",
                "MX must point to a host name with an A/AAAA record — never to an IP address or a CNAME."])
    rows = [("www.campus.example", "CNAME", "web1.campus.example", "web1"),
            ("web1.campus.example", "A", "10.10.40.80", None),
            ("campus.example", "MX 10", "mail.campus.example", "mail"),
            ("mail.campus.example", "A", "mail server IPv4", None),
            ("campus.example", "NS", "ns1.campus.example", "ns1"),
            ("ns1.campus.example", "A", "10.10.99.53", None),
            ("80.40.10.10.in-addr.arpa", "PTR", "web1.campus.example", None)]
    colors = {"CNAME": "purple", "A": "green", "MX 10": "amber", "NS": "teal", "PTR": "blue"}
    y = 110
    for name, t, data, chain in rows:
        col = colors[t]
        c.rect(40, y, 330, 52, fill="#ffffff", stroke=LINE, r=8)
        c.text(56, y + 32, name, 13, INK, 600, mono=True)
        c.pill(450, y + 26, t, col, 12.5, solid=True)
        c.line(372, y + 26, 418, y + 26, FAINT, 2)
        c.line(490, y + 26, 568, y + 26, fam(col)[0], 2.2, arrow="end")
        F = fam(col)
        c.rect(572, y, 330, 52, fill=F[1], stroke=F[0], r=8)
        c.text(588, y + 32, data, 13, F[2], 700, mono=True)
        if chain:
            c.path(f"M904,{y + 26} C960,{y + 26} 960,{y + 66 + 26} 380,{y + 66 + 8}", F[0], 1.8, arrow="end", dash="5 4")
            c.text(980, y + 56, "look up again", 11, F[0], 700)
        y += 66
    return c


@figure("22.3", "dns-diagnosis-flow")
def f22_3():
    c = Canvas(1100, 720, "22.3", "DNS diagnosis flow — separate DNS from reachability first",
               "Works by IP but not by name → a name problem; fails by IP too → DNS is not the cause",
               ["Tools: nslookup <name> [server] · dig <name> <type> [@server] · Resolve-DnsName · ipconfig /displaydns and /flushdns."])
    check_flow(c, "Service fails by name", [
        ("Does it fail by IP address too?", "Not DNS — troubleshoot reachability (Chapters 10–21)", "grey"),
        ("Client has no / wrong DNS server?", "ipconfig /all → fix the DHCP dns-server or static setting", "amber"),
        ("NXDOMAIN or empty answer?", "Missing record or wrong name/suffix — add or fix the A/AAAA/CNAME target", "red"),
        ("Answer returned but wrong data?", "Old address, wrong AAAA, MX → CNAME, stale cache (TTL) — fix and flush", "purple"),
    ], end="SERVFAIL or timeout?", end_lines=["Resolver can't reach / lame delegation (NS)"], start_lines=["user: “the website is down”"])
    return c


# ----------------------------------------------------------------------------- Chapter 23

@figure("23.1", "dhcp-snooping")
def f23_1():
    c = Canvas(1160, 600, "23.1", "DHCP snooping: trusted uplinks, untrusted access ports",
               "Server messages (OFFER, ACK) are dropped on untrusted ports — the rogue server is silenced",
               ["Enable globally AND per VLAN: ip dhcp snooping · ip dhcp snooping vlan 10,30 · trust on uplinks (or the port-channel).",
                "no ip dhcp snooping information option when the snooping switch is not the relay. Rate-limit untrusted ports against starvation."])
    d1, sw, pc, rog = (580, 150), (580, 320), (320, 450), (840, 450)
    c.line(d1[0], d1[1] + 34, sw[0], sw[1] - 22, GREEN[0], 5)
    c.link_label(580, 240, "Gi0/1–2 · TRUSTED", color=GREEN[0], weight=700)
    c.device("l3switch", *d1, "DSW1 (relay)", ["→ DHCP server R1 10.0.0.1"], label="right")
    c.device("switch", *sw, "SW1", ["ip dhcp snooping"], label="right")
    c.line(sw[0] - 30, sw[1] + 20, pc[0] + 30, pc[1] - 30, "#64748b", 2.5)
    c.line(sw[0] + 30, sw[1] + 20, rog[0] - 26, rog[1] - 34, "#64748b", 2.5)
    c.link_label(430, 400, "Fa0/1 untrusted", color=MUTED)
    c.link_label(730, 400, "Fa0/10 untrusted", color=MUTED)
    c.device("pc", *pc, "PC1", ["DISCOVER / REQUEST allowed"])
    c.device("server", *rog, "ROGUE", ["10.10.10.200 · DHCP on"], highlight="red")
    c.path(f"M{rog[0] - 40},{rog[1] - 10} C{rog[0] - 120},{rog[1] - 40} {sw[0] + 110},{sw[1] + 40} {sw[0] + 60},{sw[1] + 20}", RED[0], 2.5, arrow="end", dash="6 4")
    c.pill(860, 395, "OFFER dropped ✗", "red", 12, solid=True)
    c.path(f"M{d1[0] - 30},{d1[1] + 40} C{d1[0] - 120},{d1[1] + 140} {pc[0] + 60},{pc[1] - 160} {pc[0] + 10},{pc[1] - 44}", GREEN[0], 2.5, arrow="end")
    c.pill(360, 260, "OFFER / ACK from R1 ✓", "green", 12, solid=True)
    c.rect(40, 528, 1080, 40, fill="#0f172a", stroke="none", r=8)
    c.text(60, 553, "Binding table:  MAC 0060.2f11.0001 · IP 10.10.10.11 · lease 86400 · VLAN 10 · Fa0/1   → used by DAI", 12.5, "#e2e8f0", 600, mono=True)
    return c


@figure("23.2", "dai-decisions")
def f23_2():
    c = Canvas(1160, 480, "23.2", "Dynamic ARP inspection decisions on untrusted ports",
               "Sender IP + MAC must match a DHCP snooping binding for that port and VLAN — or an ARP ACL",
               ["Trust the uplinks (ip arp inspection trust) or the gateway's ARP replies are dropped and the whole VLAN loses its gateway.",
                "Log: %SW_DAI-4-DHCP_SNOOPING_DENY: 1 Invalid ARPs (Res) on Fa0/12, vlan 10."])
    hdr = ["ARP arrives on", "Sender IP / MAC", "Binding table says", "Decision"]
    xs = [40, 230, 560, 900]
    for x, h in zip(xs, hdr):
        c.text(x + 10, 120, h, 13, MUTED, 700)
    rows = [("Fa0/1 · PC1", "10.10.10.11 / 0060.2f11.0001", "10.10.10.11 / 0060.2f11.0001 on Fa0/1 ✓", "FORWARD", "green"),
            ("Fa0/12 · attacker", "10.10.10.1 / 0090.21aa.0012", "Fa0/12 has no binding for the gateway IP", "DROP + log", "red"),
            ("Fa0/2 · Printer1", "10.10.40.11 / printer MAC", "no binding (static address)", "ARP ACL permits", "amber")]
    y = 140
    for port, ipmac, bind, dec, col in rows:
        F = fam(col)
        c.rect(40, y, 1080, 74, fill=F[1], stroke=F[0], r=10, sw=1.6)
        c.text(50, y + 44, port, 13.5, INK, 700)
        c.text(240, y + 44, ipmac, 12.5, INK, 600, mono=True)
        c.text(570, y + 44, bind, 12.5, F[2], 600)
        c.pill(1010, y + 37, dec, col, 12.5, solid=True)
        y += 90
    return c


@figure("23.3", "lab-23-1-port-roles")
def f23_3():
    c = Canvas(1160, 620, "23.3", "Lab 23.1 port roles on SW1 and SW2",
               "Trusted uplinks (green) · every access port gets the same protections (grey band) · the rogue server is a test",
               ["DHCP snooping + DAI: VLANs 10, 30 (and 40, 99 where used). ARP ACL for static hosts: printer, servers. Recover err-disabled",
                "ports with shutdown / no shutdown after removing the cause."])
    d1, d2, s1, s2 = (380, 150), (780, 150), (380, 320), (780, 320)
    for d in (d1, d2):
        for s in (s1, s2):
            c.line(d[0], d[1] + 34, s[0], s[1] - 22, GREEN[0], 3.5)
    c.line(d1[0] + 44, d1[1], d2[0] - 44, d2[1], "#64748b", 4)
    c.device("l3switch", *d1, "DSW1", label="left")
    c.device("l3switch", *d2, "DSW2", label="right")
    c.device("switch", *s1, "SW1", label="left")
    c.device("switch", *s2, "SW2", label="right")
    c.pill(580, 240, "uplinks: ip dhcp snooping trust · ip arp inspection trust", "green", 12, solid=True)
    hosts1 = [(200, "pc", "PC1", "Fa0/1"), (300, "server", "AAA-1", "Fa0/5"), (400, "server", "DNS1", "Fa0/6"), (520, "server", "ROGUE", "Fa0/10")]
    hosts2 = [(680, "pc", "PC3", "Fa0/1"), (780, "printer", "Printer1", "Fa0/2"), (880, "server", "FILES", "Fa0/5"), (980, "server", "WEB1", "Fa0/6")]
    for hs, s in ((hosts1, s1), (hosts2, s2)):
        for x, k, n, p in hs:
            rog = n == "ROGUE"
            c.line(s[0] + (x - s[0]) * 0.2, s[1] + 22, x, 400, RED[0] if rog else "#64748b", 3 if rog else 2)
            c.device(k, x, 432, None, s=0.55)
            c.text(x, 476, n, 12, RED[0] if rog else INK, 700, "middle")
            c.text(x, 492, p, 11, MUTED, 600, "middle", mono=True)
    c.rect(40, 506, 1080, 46, fill=PANEL, stroke=LINE, r=10)
    c.text(60, 535, "Access ports: untrusted · ip dhcp snooping limit rate 15 · port-security · storm-control · ipv6 nd raguard · PortFast + BPDU guard", 12, INK, 600)
    return c

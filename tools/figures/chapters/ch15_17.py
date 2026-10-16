"""Chapter 15 — Troubleshooting tools; Chapter 16 — Wireless; Chapter 17 — Client connectivity."""

import math

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL,
                    sequence, fam)


# ----------------------------------------------------------------------------- Chapter 15

@figure("15.1", "divide-and-conquer")
def f15_1():
    c = Canvas(1160, 600, "15.1", "Divide and conquer: one question and its commands per layer",
               "Start at the Network layer with ping — success → look higher, failure → look lower",
               ["Always test both directions: ping … source <interface> proves the return route as well as the forward one."])
    bands = [("Application · L5–7", "Does the service answer?", "nslookup · curl / browser · telnet <ip> <port> · show logging", "grey"),
             ("Transport · L4", "Is the port open, or filtered?", "show access-lists · show ip nat translations · capture: SYN → RST?", "teal"),
             ("Network · L3", "Can I reach the IP, both ways?", "ping [source] · traceroute · show ip route · show ip int brief · show arp", "blue"),
             ("Data link · L2", "Right VLAN, trunk, MAC, STP state?", "show vlan brief · show interfaces trunk · show mac address-table · show spanning-tree · show cdp neighbors", "purple"),
             ("Physical · L1", "Is the link up and clean?", "show interfaces status · show interfaces (CRC, errors) · show inventory / transceiver", "amber")]
    y = 110
    for name, q, cmds, col in bands:
        hi = col == "blue"
        st, fl, tx = fam(col)
        c.rect(40, y, 1030, 82, fill=fl if col != "grey" else PANEL, stroke=st, sw=2.5 if hi else 1.2, r=10)
        c.text(60, y + 32, name, 15, tx if col != "grey" else INK, 700)
        c.text(60, y + 56, q, 13, INK, 500)
        c.text(380, y + 46, cmds, 12.5, INK, 500, mono=True)
        if hi:
            c.pill(1000, y + 16, "start here", "blue", 11, solid=True)
        y += 92
    c.path("M1078,330 C1130,280 1130,200 1078,160", GREEN[0], 2.5, arrow="end")
    c.text(1128, 245, "ping OK", 11.5, GREEN[0], 700, rotate=-90)
    c.path("M1078,370 C1130,430 1130,520 1078,560", RED[0], 2.5, arrow="end")
    c.text(1128, 470, "ping fails", 11.5, RED[0], 700, rotate=-90)
    return c


@figure("15.2", "traceroute-ttl")
def f15_2():
    c = Canvas(1160, 600, "15.2", "How traceroute discovers each hop with rising TTL",
               "Each probe dies one router further on; the router where it dies reveals itself with ICMP Time Exceeded",
               ["IOS and Linux/macOS send UDP probes (ports from 33434); Windows tracert sends ICMP Echo. Three probes per hop.",
                "* * * means no reply for that hop — often an ACL or a router that rate-limits ICMP, not necessarily a failure."])
    xs = [130, 400, 640, 880, 1060]
    names = [("pc", "PC1", "10.10.10.11"), ("l3switch", "DSW1", "hop 1 · 10.10.10.2"), ("router", "R1", "hop 2 · 10.0.0.1"),
             ("cloud", "ISP", "hop 3 · 198.51.100.1"), ("server", "Host", "192.0.2.8")]
    for i in range(4):
        c.line(xs[i] + 40, 170, xs[i + 1] - 40, 170, "#94a3b8", 3)
    for x, (k, n, ip) in zip(xs, names):
        c.device(k, x, 170, n, [ip], s=0.85, name_size=13.5, line_size=11.5)
    rows = [(1, 1, "Time Exceeded from 10.10.10.2", AMBER), (2, 2, "Time Exceeded from 10.0.0.1", AMBER),
            (3, 3, "Time Exceeded from 198.51.100.1", AMBER), (4, 4, "Port Unreachable / Echo Reply — done", GREEN)]
    y = 290
    for ttl, reach, reply, col in rows:
        c.pill(60, y, f"TTL {ttl}", "navy", 11.5, solid=True, anchor="start")
        c.line(xs[0] + 30, y, xs[reach] - 14, y, BLUE[0], 2.4, arrow="end")
        if reach < 4:
            c.text(xs[reach], y + 5, "✗", 16, RED[0], 700, "middle")
        c.line(xs[reach] - 14, y + 20, xs[0] + 30, y + 20, col[0], 2, arrow="end", dash="6 4")
        c.text((xs[0] + xs[reach]) / 2 + 20, y + 38, reply, 11.5, col[2], 700, "middle")
        y += 72
    return c


@figure("15.3", "reading-a-capture")
def f15_3():
    c = Canvas(1160, 540, "15.3", "Reading the capture: four conversations and what each proves",
               "Group frames by conversation, then ask what each one proves about the path",
               ["Verdict for the “cannot print” ticket: the network is fine — the printer's raw-print service (TCP 9100) is closed; IPP (631) works."])
    convs = [("Frames 1–2 · ARP", ["Who has 10.10.10.1?", "→ 0000.0c9f.f00a"], "Gateway resolves to the HSRP virtual MAC ✓", "green"),
             ("Frames 3–4 · ICMP", ["Echo request to 192.0.2.8", "reply ttl=253"], "Internet path and NAT work ✓", "green"),
             ("Frames 5–6 · TCP 9100", ["SYN →", "← RST, ACK"], "Host reachable, port 9100 CLOSED ✗", "amber"),
             ("Frames 7–9 · TCP 631", ["SYN → SYN-ACK → ACK", "three-way handshake"], "IPP printing service open ✓", "green")]
    for i, (t, l, verdict, col) in enumerate(convs):
        x = 40 + (i % 2) * 550
        y = 110 + (i // 2) * 190
        st, fl, tx = fam(col)
        c.rect(x, y, 530, 170, fill=fl, stroke=st, r=12, sw=2.5 if col == "amber" else 1.5)
        c.text(x + 20, y + 32, t, 15, INK, 700)
        c.rect(x + 20, y + 48, 490, 56, fill="#0f172a", stroke="none", r=6)
        c.text(x + 34, y + 70, l[0], 12.5, "#e2e8f0", 500, mono=True)
        c.text(x + 34, y + 92, l[1], 12.5, "#e2e8f0", 500, mono=True)
        c.text(x + 20, y + 140, verdict, 14, tx, 700)
    return c


# ----------------------------------------------------------------------------- Chapter 16

@figure("16.1", "24ghz-channel-overlap")
def f16_1():
    c = Canvas(1160, 470, "16.1", "2.4 GHz channels 1–13: only 1, 6 and 11 avoid overlap",
               "Channels are 5 MHz apart but each is about 22 MHz wide — drawn to scale",
               ["Adjacent-channel interference (e.g. APs on 1 and 3) corrupts frames; co-channel interference (both on 6) only makes APs take turns.",
                "Use 20 MHz channels in 2.4 GHz. 1–11 in the USA; 1–13 in most other countries."])
    f0, f1 = 2400, 2486
    x0, w = 60, 1040
    base = 360
    def X(f):
        return x0 + (f - f0) / (f1 - f0) * w
    for ch in range(1, 14):
        fc = 2412 + 5 * (ch - 1)
        hi = ch in (1, 6, 11)
        col = {1: BLUE, 6: GREEN, 11: PURPLE}.get(ch, GREY)
        h = 190 if hi else 150
        xa, xb = X(fc - 11), X(fc + 11)
        d = f"M{xa:.1f},{base} C{xa + (xb - xa) * 0.15:.1f},{base - h} {xb - (xb - xa) * 0.15:.1f},{base - h} {xb:.1f},{base}"
        c.path(d, col[0] if hi else "#b8c2cf", 3 if hi else 1.6, fill=col[1] if hi else "none", opacity=0.95 if hi else 0.9)
    for ch in range(1, 14):
        fc = 2412 + 5 * (ch - 1)
        hi = ch in (1, 6, 11)
        col = {1: BLUE, 6: GREEN, 11: PURPLE}.get(ch, GREY)
        c.text(X(fc), 130, str(ch), 15 if hi else 12, col[0] if hi else MUTED, 800 if hi else 600, "middle")
        c.line(X(fc), 138, X(fc), base - (190 if hi else 150) * 0.75 - 4, col[0] if hi else "#d5dbe3", 1, dash="2 3")
    c.line(x0, base, x0 + w, base, INK, 1.5)
    for f in range(2400, 2490, 10):
        c.line(X(f), base, X(f), base + 6, INK, 1)
        c.text(X(f), base + 22, str(f), 11, MUTED, 500, "middle")
    c.text(x0 + w, base + 40, "MHz", 11, MUTED, 600, "end")
    return c


@figure("16.2", "channel-reuse-plan")
def f16_2():
    c = Canvas(1160, 560, "16.2", "A 2.4 GHz channel reuse plan with channels 1, 6 and 11",
               "Wherever two cells overlap they carry different channels — neighbours never share a frequency",
               ["Overlap cells by roughly 15–20 % for roaming. In a controller-based WLAN, RRM picks channels and power automatically."])
    R = 70
    cols = {1: BLUE, 6: GREEN, 11: PURPLE}
    cx0, cy0 = 260, 170

    def chan(row, col):
        q, r = col, row - (col - (col & 1)) // 2
        return [1, 6, 11][(q + 2 * r) % 3]
    for row in range(4):
        for col in range(6):
            x = cx0 + col * R * 1.5 * 1.15
            y = cy0 + row * R * math.sqrt(3) * 1.0 + (col % 2) * R * math.sqrt(3) / 2
            ch = chan(row, col)
            F = cols[ch]
            c.circle(x, y, R * 0.98, fill=F[1], stroke=F[0], sw=1.6)
    for row in range(4):
        for col in range(6):
            x = cx0 + col * R * 1.5 * 1.15
            y = cy0 + row * R * math.sqrt(3) * 1.0 + (col % 2) * R * math.sqrt(3) / 2
            ch = chan(row, col)
            F = cols[ch]
            c.add(f'<g transform="translate({x:.1f},{y - 6:.1f}) scale(0.45)">' + __import__("svgkit").icon_ap() + '</g>')
            c.text(x, y + 22, f"ch {ch}", 13, F[2], 800, "middle")
    for i, ch in enumerate((1, 6, 11)):
        c.pill(60, 160 + i * 40, f"channel {ch}", ["blue", "green", "purple"][i], 12.5, solid=True, anchor="start")
    return c


@figure("16.3", "8021x-flow")
def f16_3():
    c = Canvas(1160, 760, "16.3", "WPA2/WPA3-Enterprise: 802.1X authentication",
               "Supplicant ↔ authenticator speak EAP over the air (EAPOL); authenticator ↔ server carry the same EAP inside RADIUS",
               ["Common EAP methods: EAP-TLS (certificates both sides — strongest), PEAP (server certificate + password in a TLS tunnel), EAP-FAST.",
                "RADIUS: UDP 1812 authentication, 1813 accounting. The same server can also authenticate wired 802.1X and admins (Chapter 18)."])
    sequence(c, [("sup", 200, "laptop", "Supplicant", ["client software"]), ("auth", 580, "ap", "Authenticator", ["AP or WLC"]),
                 ("srv", 960, "server", "Authentication server", ["RADIUS (e.g. Cisco ISE)"])], [
        {"a": "sup", "b": "auth", "t": "802.11 open auth + association", "c": GREY[0], "n": 1},
        {"a": "auth", "b": "sup", "t": "EAP-Request / Identity", "c": BLUE[0], "n": 2},
        {"a": "sup", "b": "auth", "t": "EAP-Response / Identity", "c": BLUE[0]},
        {"a": "auth", "b": "srv", "t": "RADIUS Access-Request (EAP)", "c": PURPLE[0], "n": 3},
        {"a": "srv", "b": "sup", "t": "EAP method exchange — TLS tunnel, credentials", "s": "relayed by the authenticator", "c": PURPLE[0], "dash": True, "n": 4},
        {"a": "srv", "b": "auth", "t": "RADIUS Access-Accept (+ key material)", "c": GREEN[0], "n": 5},
        {"a": "auth", "b": "sup", "t": "EAP-Success", "c": GREEN[0]},
        {"a": "auth", "b": "sup", "t": "4-way handshake → session keys", "c": AMBER[0], "n": 6},
    ], bottom=650)
    c.rect(200, 655, 380, 10, fill=BLUE[0], stroke="none", r=5)
    c.text(390, 690, "encrypted user traffic (AES-CCMP / GCMP)", 12.5, BLUE[0], 700, "middle")
    return c


@figure("16.4", "lab-16-1-topology")
def f16_4():
    c = Canvas(1160, 600, "16.4", "Lab 16.1 topology: an ESS of two APs on channels 1 and 6",
               "Same SSID on both APs — a laptop roams through the overlap without changing SSID or address",
               ["SSID Staff-WiFi · WPA2-Personal (PSK) with AES on both APs · R-W serves DHCP pool WLAN 192.168.30.0/24 (gateway .1)."])
    rw, sw = (580, 150), (580, 280)
    apa, apb = (390, 410), (770, 410)
    c.circle(apa[0], apa[1] + 20, 170, fill=BLUE[1], stroke=BLUE[0], sw=1.5, dash="6 5")
    c.circle(apb[0], apb[1] + 20, 170, fill=GREEN[1], stroke=GREEN[0], sw=1.5, dash="6 5")
    c.cable(rw[0], rw[1] + 26, sw[0], sw[1] - 22, "copper", "G0/0/0", "Fa0/24")
    c.cable(sw[0] - 30, sw[1] + 20, apa[0] + 10, apa[1] - 30, "copper", "Fa0/1", "Port 0")
    c.cable(sw[0] + 30, sw[1] + 20, apb[0] - 10, apb[1] - 30, "copper", "Fa0/2", "Port 0")
    c.device("router", *rw, "R-W", ["192.168.30.1/24 · DHCP"], label="right")
    c.device("switch", *sw, "SW-W", label="right")
    c.device("ap", *apa, "AP-A", ["channel 1"], s=1.1)
    c.device("ap", *apb, "AP-B", ["channel 6"], s=1.1)
    c.device("laptop", 260, 500, "L1", ["DHCP"], s=0.8, name_size=12.5)
    c.device("laptop", 580, 500, "L2", ["roaming"], s=0.8, name_size=12.5)
    c.cable(260, 470, apa[0] - 20, apa[1] + 30, "wireless", sw=2.5)
    c.cable(580, 470, apb[0] - 30, apb[1] + 30, "wireless", sw=2.5)
    c.text(580, 400, "overlap ≈ 15–20 %", 11.5, MUTED, 700, "middle")
    return c


# ----------------------------------------------------------------------------- Chapter 17

@figure("17.1", "client-check-ladder")
def f17_1():
    c = Canvas(1160, 420, "17.1", "Client connectivity checks in order — stop at the first “no”",
               "Users start complaining at the last step; you start at the first",
               ["Windows: ipconfig /all, ping, tracert, nslookup · macOS: ifconfig, netstat -rn · Linux: ip addr, ip route, resolvectl"])
    steps = [("1", "Link", "cable / right SSID?", "unplugged, wrong SSID, wrong Wi-Fi security"),
             ("2", "Address", "valid IP + mask?", "169.254.x.x → DHCP failed; wrong mask"),
             ("3", "Gateway", "set, same subnet, answers?", "missing or wrong gateway"),
             ("4", "Remote IP", "beyond the gateway?", "routing, ACL, NAT"),
             ("5", "Names", "DNS set and resolving?", "no DNS server, wrong server"),
             ("6", "Application", "service answers?", "port, proxy, host firewall")]
    w = 170
    for i, (n, t, q, cause) in enumerate(steps):
        x = 40 + i * (w + 14)
        hi = n == "6"
        c.box(x, 120, w, 120, None, [], "blue" if hi else "grey", highlight=hi)
        c.badge(x + 22, 144, n, "navy")
        c.text(x + 42, 149, t, 15, INK, 700)
        c.text(x + 14, 180, q.split(" ")[0] + " " + " ".join(q.split(" ")[1:3]), 12, MUTED, 500)
        c.text(x + 14, 198, " ".join(q.split(" ")[3:]), 12, MUTED, 500)
        if i < 5:
            c.line(x + w + 2, 180, x + w + 12, 180, FAINT, 2, arrow="end")
        c.line(x + w / 2, 242, x + w / 2, 272, RED[0], 1.6, arrow="end")
        from svgkit import wrap
        for j, ln in enumerate(wrap(cause, 22)):
            c.text(x + w / 2, 292 + j * 16, ln, 11.5, RED[0], 600, "middle")
    c.text(40, 262, "if “no”:", 11.5, RED[0], 700)
    return c


@figure("17.2", "mask-decides-delivery")
def f17_2():
    c = Canvas(1160, 560, "17.2", "The mask decides: send to the gateway, or deliver directly?",
               "Client 10.10.30.25 sends to the printer 10.10.40.11 — same packet, two different masks",
               ["With the wrong /16 it may still “work” if the router answers with proxy ARP — which hides the fault. Fix the mask."])
    for x0, title, mask, local in ((40, "Correct mask /24", "255.255.255.0", False), (600, "Wrong mask /16", "255.255.0.0", True)):
        F = RED if local else GREEN
        c.rect(x0, 100, 520, 400, fill="#f8fafc", stroke=LINE, r=14)
        c.text(x0 + 260, 128, title, 15, INK, 700, "middle")
        c.box(x0 + 20, 145, 480, 82, None, [("My network: 10.10.30.25 AND " + mask, INK, 600),
              f"= {'10.10.0.0' if local else '10.10.30.0'}   ·   10.10.40.11 → {'10.10.0.0  (same!)' if local else '10.10.40.0  (different)'}"],
              "grey", size=12.5, mono_lines=False)
        c.device("laptop", x0 + 90, 300, "Client", [f"10.10.30.25 /{16 if local else 24}"], s=0.8, name_size=12.5)
        c.device("l3switch", x0 + 260, 300, "Gateway", ["10.10.30.1"], s=0.8, name_size=12.5)
        c.device("printer", x0 + 430, 300, "Printer", ["10.10.40.11"], s=0.8, name_size=12.5)
        if local:
            c.path(f"M{x0 + 120},270 C{x0 + 200},210 {x0 + 330},210 {x0 + 405},270", RED[0], 2.5, arrow="end", dash="6 5")
            c.text(x0 + 260, 252, "ARP for 10.10.40.11 directly", 12, RED[0], 700, "middle")
        else:
            c.line(x0 + 125, 300, x0 + 225, 300, GREEN[0], 3, arrow="end")
            c.line(x0 + 300, 300, x0 + 400, 300, GREEN[0], 3, arrow="end")
            c.text(x0 + 175, 286, "via gw", 11.5, GREEN[0], 700, "middle")
        c.box(x0 + 20, 400, 480, 80, "No reply — printer is on another segment ✗" if local else "Routed to VLAN 40 — success ✓",
              ["(unless the router answers with proxy ARP)" if local else "ARP only for the gateway's MAC"], "red" if local else "green",
              size=12.5, title_size=14, highlight=True)
    return c

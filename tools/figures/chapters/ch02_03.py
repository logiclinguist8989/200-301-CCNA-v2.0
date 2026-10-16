"""Chapter 2 — IPv4 addressing and subnetting; Chapter 3 — IPv6 addressing."""

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL,
                    check_flow, sequence, octet_bits)


# ----------------------------------------------------------------------------- Chapter 2

@figure("2.1", "octet-place-values")
def f2_1():
    c = Canvas(1000, 440, "2.1", "Octet place values: 10101100 = 172",
               "Add the place value of every 1 bit; every 0 bit contributes nothing",
               ["The same eight place values (128 … 1) apply to every octet of every IPv4 address."])
    bits = "10101100"
    vals = [128, 64, 32, 16, 8, 4, 2, 1]
    x0, cell = 150, 86
    for i, (b, v) in enumerate(zip(bits, vals)):
        on = b == "1"
        x = x0 + i * cell
        c.text(x + cell / 2 - 4, 132, f"2^{7 - i}", 11.5, MUTED, 500, "middle")
        c.box(x, 142, cell - 8, 50, None, [], "grey", shadow=False)
        c.text(x + cell / 2 - 4, 174, str(v), 18, INK, 700, "middle")
        if on:
            c.rect(x, 202, cell - 8, 56, fill=BLUE[0], stroke=BLUE[0], r=8)
        else:
            c.rect(x, 202, cell - 8, 56, fill="#f8fafc", stroke=LINE, r=8)
        c.text(x + cell / 2 - 4, 240, b, 26, "#ffffff" if on else FAINT, 700, "middle", mono=True)
        if on:
            c.line(x + cell / 2 - 4, 262, x + cell / 2 - 4, 290, BLUE[0], 2, arrow="end")
            c.pill(x + cell / 2 - 4, 306, f"+{v}", "blue", 13)
    c.text(60, 174, "Place value", 13, MUTED, 700)
    c.text(60, 236, "Bit", 13, MUTED, 700)
    c.text(500, 358, "128 + 32 + 8 + 4 = 172", 22, INK, 800, "middle")
    return c


@figure("2.2", "address-in-binary")
def f2_2():
    c = Canvas(1240, 520, "2.2", "192.168.10.75/26 bit by bit",
               "26 network bits (shaded) are identical in all three rows; only the 6 host bits change",
               ["AND the address with the mask → network. Set all host bits to 1 → broadcast. Hosts = 2^6 − 2 = 62."])
    rows = [
        ("Address", "192.168.10.75", "11000000.10101000.00001010.01001011"),
        ("Mask /26", "255.255.255.192", "11111111.11111111.11111111.11000000"),
        ("Network", "192.168.10.64", "11000000.10101000.00001010.01000000"),
        ("Broadcast", "192.168.10.127", "11000000.10101000.00001010.01111111"),
    ]
    cell = 26
    x0 = 250
    y = 138
    for oi in range(4):
        c.text(x0 + oi * (8 * cell + 14) + 4 * cell, 124, f"octet {oi + 1}", 11.5, MUTED, 600, "middle")
    for label, dec, b in rows:
        c.text(40, y + 26, label, 14, INK, 700)
        c.text(40, y + 44, dec, 12.5, MUTED, 500, mono=True)
        k = 0
        for oi, octet in enumerate(b.split(".")):
            for bi, bit in enumerate(octet):
                net = k < 26
                x = x0 + oi * (8 * cell + 14) + bi * cell
                col = ("blue" if net else ("amber" if label != "Mask /26" else None))
                if label in ("Network", "Broadcast") and not net:
                    col = "green" if label == "Network" else "red"
                st, fl, tx = {"blue": BLUE, "amber": AMBER, "green": GREEN, "red": RED, None: GREY}[col]
                c.rect(x, y, cell - 3, 40, fill=fl, stroke=st, sw=1.1, r=3)
                c.text(x + (cell - 3) / 2, y + 26, bit, 14, tx, 700, "middle", mono=True)
                k += 1
        y += 70
    c.brace(x0, x0 + 3 * (8 * cell + 14) + 2 * cell - 3, 420, "26 network bits — shaded", BLUE[0], up=False)
    hx = x0 + 3 * (8 * cell + 14) + 2 * cell
    c.brace(hx, hx + 6 * cell - 3, 420, "6 host bits", AMBER[0], up=False)
    return c


@figure("2.3", "block-size-number-line")
def f2_3():
    c = Canvas(1100, 400, "2.3", "/26 cuts the fourth octet into four blocks of 64",
               "Block size = 256 − 192 = 64 → host .75 falls in the .64 block",
               ["Network = the block start (.64). Broadcast = next block start − 1 (.127). Usable hosts .65 – .126."])
    x0, w = 60, 980
    blocks = [(0, "192.168.10.0/26"), (64, "192.168.10.64/26"), (128, "192.168.10.128/26"), (192, "192.168.10.192/26")]
    for start, lab in blocks:
        x = x0 + start / 256 * w
        bw = 64 / 256 * w
        hit = start == 64
        c.rect(x + 2, 170, bw - 4, 80, fill=BLUE[1] if hit else PANEL, stroke=BLUE[0] if hit else LINE, sw=2.5 if hit else 1.5, r=8)
        c.text(x + bw / 2, 204, lab, 14, BLUE[2] if hit else INK, 700, "middle", mono=True)
        c.text(x + bw / 2, 228, f".{start} – .{start + 63}", 12.5, MUTED, 500, "middle")
        c.text(x + 2, 274, str(start), 13, INK, 700, "middle")
    c.text(x0 + w - 2, 274, "255", 13, INK, 700, "middle")
    xh = x0 + 75 / 256 * w
    c.line(xh, 130, xh, 166, RED[0], 2.5, arrow="end")
    c.pill(xh, 118, "host .75", "red", 13, solid=True)
    c.line(x0, 286, x0 + w, 286, FAINT, 1.5)
    nx = x0 + 64 / 256 * w
    bx = x0 + 127.5 / 256 * w
    c.pill(nx + 40, 316, "network .64", "green", 12)
    c.pill(bx - 50, 316, "broadcast .127", "red", 12)
    return c


@figure("2.4", "vlsm-plan")
def f2_4():
    c = Canvas(1160, 520, "2.4", "VLSM plan for 172.16.0.0/24, drawn to scale",
               "Largest first; each block starts on a multiple of its own size — the last /27 is enlarged below",
               ["Allocating smallest-first often breaks the alignment rule and wastes space. The dashed /29 is free for growth."])
    x0, w = 40, 1080
    segs = [(0, 128, "Staff VLAN 10", "172.16.0.0/25 · 126 hosts", "blue"),
            (128, 64, "Wireless VLAN 30", ".128/26 · 62 hosts", "green"),
            (192, 32, "Printers/IoT", "VLAN 40 · .192/27", "amber"),
            (224, 32, "", "", "grey")]
    for start, size, t, s, col in segs:
        x = x0 + start / 256 * w
        bw = size / 256 * w
        if col == "grey":
            c.rect(x + 1, 130, bw - 2, 80, fill=PURPLE[1], stroke=PURPLE[0], sw=1.5, r=6)
            c.text(x + bw / 2, 166, "last /27", 12, PURPLE[2], 700, "middle")
            c.text(x + bw / 2, 184, ".224 – .255", 11, MUTED, 500, "middle")
        else:
            c.box(x + 1, 130, bw - 2, 80, t, [s], col, size=12, title_size=13.5, shadow=False, r=6)
    for v in (0, 64, 128, 192, 224, 256):
        c.text(x0 + v / 256 * w, 228, f".{v}" if v < 256 else ".255", 11.5, MUTED, 600, "middle")
    # zoom lines
    zx0, zx1 = x0 + 224 / 256 * w, x0 + w
    c.path(f"M{zx0},238 L{x0},296", PURPLE[0], 1.5, dash="5 4")
    c.path(f"M{zx1},238 L{x0 + w},296", PURPLE[0], 1.5, dash="5 4")
    sub = [(224, 16, "Mgmt VLAN 99", ".224/28 · 14 hosts", "teal"),
           (240, 4, "R1–R2", ".240/30", "red"),
           (244, 4, "R1–R3", ".244/30", "red"),
           (248, 8, "Spare", ".248/29", "grey")]
    for start, size, t, s, col in sub:
        x = x0 + (start - 224) / 32 * w
        bw = size / 32 * w
        if col == "grey":
            c.rect(x + 2, 300, bw - 4, 90, fill="#ffffff", stroke=FAINT, sw=1.8, r=6, dash="6 5")
            c.text(x + bw / 2, 340, t, 14, MUTED, 700, "middle")
            c.text(x + bw / 2, 360, s + " · unallocated", 12, MUTED, 500, "middle")
        else:
            c.box(x + 2, 300, bw - 4, 90, t, [s], col, size=12, title_size=14, shadow=False, align="center")
    for v in (224, 240, 244, 248, 256):
        c.text(x0 + (v - 224) / 32 * w, 408, f".{v}" if v < 256 else ".255", 11.5, MUTED, 600, "middle")
    return c


@figure("2.5", "route-summarization")
def f2_5():
    c = Canvas(1100, 470, "2.5", "Four /24s summarize to one /22",
               "Compare the third-octet bits: the first 6 match in every network, only the last 2 change",
               ["16 matching bits (octets 1–2) + 6 matching bits (octet 3) = /22  →  10.10.8.0/22 (255.255.252.0) covers 10.10.8.0 – 10.10.11.255"])
    nets = [("10.10.8.0/24", "00001000"), ("10.10.9.0/24", "00001001"), ("10.10.10.0/24", "00001010"), ("10.10.11.0/24", "00001011")]
    y = 130
    for name, b in nets:
        c.text(60, y + 26, name, 15, INK, 700, mono=True)
        c.text(260, y + 26, "10.10.", 15, MUTED, 600, mono=True)
        octet_bits(c, 330, y, b, cell=50, h=40, colors=["blue"] * 6 + ["amber"] * 2, size=17)
        c.text(760, y + 26, ". 0", 15, MUTED, 600, mono=True)
        y += 56
    c.brace(330, 330 + 6 * 50 - 3, y + 6, "6 identical bits", BLUE[0], up=False)
    c.brace(330 + 6 * 50, 330 + 8 * 50 - 3, y + 6, "00 01 10 11", AMBER[0], up=False)
    c.box(830, 150, 230, 150, "Summary", [("10.10.8.0/22", BLUE[2], 700), "mask 255.255.252.0", "block of 4 in octet 3", "8 is a multiple of 4 ✓"], "blue", highlight=True)
    return c


@figure("2.6", "host-ipv4-troubleshooting")
def f2_6():
    c = Canvas(1100, 740, "2.6", "Host IPv4 troubleshooting: cheapest check first",
               "The first “yes” names the fault; when all four say “no”, addressing is not the problem",
               ["Windows: ipconfig /all · Linux: ip -4 addr, ip route · macOS: ifconfig en0, netstat -rn"])
    check_flow(c, "Read the host's address, mask and gateway", [
        ("Address is 169.254.x.x?", "DHCP failed — fix the link, VLAN, DHCP server or relay (Chapter 14)", "red"),
        ("Mask differs from the subnet plan?", "Wrong mask — the host misjudges what is local; correct it", "amber"),
        ("Gateway blank or outside the host's own subnet?", "Wrong gateway — set the router's address in this subnet", "purple"),
        ("Address conflict warning, %IP-4-DUPADDR, ARP flipping?", "Duplicate IP — find both MACs, re-address one", "blue"),
    ], end="Addressing is correct", end_lines=["Move on to VLANs, routing, DNS"], start_lines=["ipconfig /all · ip addr · ifconfig"])
    return c


@figure("2.7", "lab-2-1-topology")
def f2_7():
    c = Canvas(1160, 560, "2.7", "Lab 2.1 topology: three VLSM subnets on R1's three interfaces",
               "Each host's gateway is the R1 interface on its own switch — all links copper straight-through",
               ["Subnets from Figure 2.4: Staff 172.16.0.0/25 · Wireless 172.16.0.128/26 · Printers/IoT 172.16.0.192/27"])
    r1 = (580, 150)
    sws = [(220, 320, "SW1", "G0/0/0", "172.16.0.1/25", "blue"), (580, 320, "SW2", "G0/0/1", "172.16.0.129/26", "green"),
           (940, 320, "SW3", "G0/0/2", "172.16.0.193/27", "amber")]
    hosts = [("pc", "PC-Staff", "172.16.0.10/25", "gw 172.16.0.1"), ("pc", "PC-Wireless", "172.16.0.140/26", "gw 172.16.0.129"),
             ("printer", "Printer1", "172.16.0.200/27", "gw 172.16.0.193")]
    for (x, y, n, rif, ip, col), (k, hn, hip, gw) in zip(sws, hosts):
        c.rect(x - 160, 250, 320, 270, fill=[BLUE, GREEN, AMBER][["blue", "green", "amber"].index(col)][1], stroke="none", r=14, opacity=0.55)
        sx = r1[0] + (x - r1[0]) * 0.06
        c.poly([(sx, r1[1] + 24), (sx, 222), (x, 222), (x, y - 26)], "#64748b", 3, arrow=None)
        c.link_label(x, y - 50, f"{rif} → Gi0/1", mono=True)
        c.cable(x, y + 22, x, 430, "copper", "Fa0/1", "Fa0")
        c.device("switch", x, y, n, label="right")
        c.device(k, x, 462, hn, [hip, gw])
        c.text(x - 148, 272, ip.replace(".1/", ".0/").replace(".129/", ".128/").replace(".193/", ".192/"), 12.5, [BLUE, GREEN, AMBER][["blue", "green", "amber"].index(col)][2], 700)
    c.device("router", *r1, "R1", ["ISR4331", "G0/0/0 .1/25 · G0/0/1 .129/26 · G0/0/2 .193/27"], label="right")
    return c


# ----------------------------------------------------------------------------- Chapter 3

@figure("3.1", "ipv6-gua-structure")
def f3_1():
    c = Canvas(1160, 420, "3.1", "Structure of a global unicast address in a /64",
               "2001:db8:acad:10:250:79ff:fe66:6801/64 — eight hextets of 16 bits",
               ["The provider assigns the /48; you design the 16-bit subnet ID (here VLAN 10); the host forms the 64-bit interface ID (EUI-64 in Figure 3.2)."])
    hx = ["2001", "0db8", "acad", "0010", "0250", "79ff", "fe66", "6801"]
    cols = ["blue", "blue", "blue", "amber", "green", "green", "green", "green"]
    x0, cw = 50, 130
    for i, (h, col) in enumerate(zip(hx, cols)):
        c.cells(x0 + i * cw, 150, [(h, cw - 8, col)], h=60, size=20)
        if i < 7:
            c.text(x0 + i * cw + cw - 4, 186, ":", 22, MUTED, 700, "middle")
        c.text(x0 + i * cw + (cw - 8) / 2, 140, f"{i * 16}–{i * 16 + 15}", 10.5, FAINT, 500, "middle")
    c.brace(x0, x0 + 3 * cw - 8, 232, "Global routing prefix · 48 bits · from the ISP / registry", BLUE[0], up=False)
    c.brace(x0 + 3 * cw, x0 + 4 * cw - 8, 232, "Subnet ID · 16", AMBER[0], up=False)
    c.brace(x0 + 4 * cw, x0 + 8 * cw - 8, 232, "Interface ID · 64 bits · SLAAC / EUI-64 / random / static", GREEN[0], up=False)
    c.brace(x0, x0 + 4 * cw - 8, 300, "Prefix /64 — one per LAN or VLAN", INK, up=False)
    c.text(x0 + 4 * cw - 50, 120, "you design this", 12, AMBER[0], 700, "middle")
    return c


@figure("3.2", "modified-eui-64")
def f3_2():
    c = Canvas(1160, 520, "3.2", "Modified EUI-64 for MAC 0050.7966.6801",
               "Split the MAC, insert FF FE, flip the 7th (U/L) bit of the first byte",
               ["Result: global 2001:db8:acad:10:250:79ff:fe66:6801 · link-local fe80::250:79ff:fe66:6801",
                "Flip, don't set: if the U/L bit is already 1 it becomes 0 (02 → 00)."])
    def row(y, label, cells):
        c.text(40, y + 30, label, 14, INK, 700)
        x = 290
        for t, col in cells:
            c.cells(x, y, [(t, 70, col)], h=48, size=18)
            x += 78
    row(110, "MAC address", [(b, "purple") for b in ["00", "50", "79", "66", "68", "01"]])
    row(190, "1  Split in half", [("00", "purple"), ("50", "purple"), ("79", "purple"), ("", "grey"), ("", "grey"), ("66", "purple"), ("68", "purple"), ("01", "purple")])
    row(270, "2  Insert FF FE", [("00", "purple"), ("50", "purple"), ("79", "purple"), ("FF", "amber"), ("FE", "amber"), ("66", "purple"), ("68", "purple"), ("01", "purple")])
    row(350, "3  Flip U/L bit", [("02", "red"), ("50", "purple"), ("79", "purple"), ("FF", "amber"), ("FE", "amber"), ("66", "purple"), ("68", "purple"), ("01", "purple")])
    c.box(940, 150, 190, 230, "First byte", [("00 = 0000 0000", INK, 600), "", "bit 7 (value 2)", "is the U/L bit", "", ("02 = 0000 0010", RED[0], 700)], "red", mono_lines=False, size=13)
    c.text(290 + 4 * 78, 448, "Interface ID  0250:79ff:fe66:6801", 18, GREEN[2], 800, "middle", mono=True)
    return c


@figure("3.3", "slaac-sequence")
def f3_3():
    c = Canvas(1100, 700, "3.3", "SLAAC: PC1 builds its own address and gateway from R1's RA",
               "Time runs downward; arrows show who sends each NDP (ICMPv6) message",
               ["Steps 1 and 4 happen inside PC1. No DHCP server is involved. The gateway is R1's link-local address fe80::1."])
    sequence(c, [("pc", 300, "pc", "PC1", ["Staff VLAN 10"]), ("r1", 800, "router", "R1", ["G0/0/0 · fe80::1"])], [
        {"a": "pc", "self": True, "t": "Create link-local fe80::250:79ff:fe66:6801", "n": 1},
        {"a": "pc", "b": "r1", "t": "NS (DAD) for the link-local address", "s": "to solicited-node multicast — no reply = unique", "c": AMBER[0], "dash": True},
        {"a": "pc", "b": "r1", "t": "RS — Router Solicitation", "s": "to ff02::2 (all routers)", "c": BLUE[0], "n": 2},
        {"a": "r1", "b": "pc", "t": "RA — prefix 2001:db8:acad:10::/64, A=1 M=0 O=0", "s": "router lifetime > 0 → fe80::1 is the default gateway", "c": GREEN[0], "n": 3},
        {"a": "pc", "self": True, "t": "Build 2001:db8:acad:10:250:79ff:fe66:6801", "n": 4},
        {"a": "pc", "b": "r1", "t": "NS (DAD) for the global address", "s": "no NA comes back → address becomes valid", "c": AMBER[0], "dash": True, "n": 5},
        {"a": "pc", "self": True, "t": "Ready: link-local + global + gateway", "n": 6},
    ], bottom=620)
    return c


@figure("3.4", "lab-3-1-topology")
def f3_4():
    c = Canvas(1160, 600, "3.4", "Lab 3.1 dual-stack topology: IPv6 added to the Lab 2.1 network",
               "Each /64 matches its IPv4 subnet; every host's IPv6 gateway is R1's link-local fe80::1 (from RAs)",
               ["R1 needs ipv6 unicast-routing to send RAs. LAN prefixes must be /64 for SLAAC."])
    r1 = (580, 150)
    data = [(220, "SW1", "G0/0/0", "2001:db8:acad:10::1/64", "172.16.0.1/25", "pc", "PC-Staff", ["SLAAC", "2001:db8:acad:10:<IID>"], "blue"),
            (580, "SW2", "G0/0/1", "2001:db8:acad:30::1/64", "172.16.0.129/26", "pc", "PC-Wireless", ["SLAAC", "2001:db8:acad:30:<IID>"], "green"),
            (940, "SW3", "G0/0/2", "2001:db8:acad:40::1/64", "172.16.0.193/27", "printer", "Printer1", ["Static", "2001:db8:acad:40::200/64"], "amber")]
    for x, sw, rif, v6, v4, k, hn, hl, col in data:
        F = {"blue": BLUE, "green": GREEN, "amber": AMBER}[col]
        c.rect(x - 165, 250, 330, 300, fill=F[1], stroke="none", r=14, opacity=0.55)
        c.text(x - 150, 274, v6.replace("::1/64", "::/64"), 13, F[2], 700, mono=True)
        sx = r1[0] + (x - r1[0]) * 0.06
        c.poly([(sx, r1[1] + 24), (sx, 222), (x, 222), (x, 316)], "#64748b", 3, arrow=None)
        c.link_label(x, 305, rif, mono=True)
        c.cable(x, 362, x, 440, "copper")
        c.device("switch", x, 340, sw, label="right")
        c.device(k, x, 470, hn, hl + ["gw fe80::1"])
    c.device("router", *r1, "R1", ["link-local fe80::1 on every interface", "ipv6 unicast-routing"], label="right")
    return c

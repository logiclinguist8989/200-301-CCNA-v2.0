"""Chapter 6 — EtherChannel with LACP; Chapter 7 — Edge-host ports."""

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL)


def bundle(c, a, b, gap=10, color=BLUE[0], sw=4, ellipse=True, label=None, dashed_second=False, second_color=None):
    """Two parallel links between points a and b, with an optional bundle ellipse."""
    import math
    (x1, y1), (x2, y2) = a, b
    L = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / L * gap / 2, (x2 - x1) / L * gap / 2
    c.line(x1 + nx, y1 + ny, x2 + nx, y2 + ny, color, sw)
    c.line(x1 - nx, y1 - ny, x2 - nx, y2 - ny, second_color or color, sw, dash="7 5" if dashed_second else None)
    if ellipse:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        c.add(f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="16" ry="{gap + 10}" fill="none" stroke="{color}" '
              f'stroke-width="2" transform="rotate({ang:.1f} {mx:.1f} {my:.1f})"/>')
        if label:
            c.link_label(mx + 34, my, label, color=color, weight=700)


# ----------------------------------------------------------------------------- Chapter 6

@figure("6.1", "stp-vs-etherchannel")
def f6_1():
    c = Canvas(1160, 500, "6.1", "Same two cables — STP blocks one, EtherChannel uses both",
               "STP sees a loop between parallel links; a port-channel turns them into one logical link",
               ["Up to eight physical links per bundle. If a member fails, traffic moves to the survivors in under a second, with no STP recalculation."])
    for x0, title in ((40, "Without EtherChannel: STP blocks one link"), (600, "With EtherChannel: Po1 forwards on both")):
        c.rect(x0, 100, 520, 340, fill="#f8fafc", stroke=LINE, r=14)
        c.text(x0 + 260, 128, title, 15, INK, 700, "middle")
    # left
    d, s = (300, 200), (300, 360)
    c.line(d[0] - 14, d[1] + 32, s[0] - 14, s[1] - 22, GREEN[0], 4)
    c.line(d[0] + 14, d[1] + 32, s[0] + 14, s[1] - 22, RED[0], 4, dash="7 5")
    c.device("l3switch", *d, "DSW1", label="right")
    c.device("switch", *s, "SW1", label="right")
    c.pill(200, 285, "forwarding", "green", 11.5)
    c.pill(410, 285, "STP blocking ✗", "red", 11.5)
    c.text(300, 425, "Pay for 2 Gb/s, use 1 Gb/s", 13, RED[0], 700, "middle")
    # right
    d, s = (860, 200), (860, 360)
    bundle(c, (d[0], d[1] + 32), (s[0], s[1] - 22), gap=28, color=BLUE[0])
    c.device("l3switch", *d, "DSW1", label="right")
    c.device("switch", *s, "SW1", label="right")
    c.pill(760, 285, "Gi1/0/1 ✓", "blue", 11.5)
    c.pill(960, 285, "Gi1/0/3 ✓", "blue", 11.5)
    c.pill(860, 250, "Po1 — one STP port", "blue", 11.5, solid=True)
    c.text(860, 425, "2 × 1 Gb/s = 2 Gb/s aggregate, one logical link", 13, GREEN[0], 700, "middle")
    return c


@figure("6.2", "per-flow-load-balancing")
def f6_2():
    c = Canvas(1160, 470, "6.2", "EtherChannel load-balances per flow, not per packet",
               "A hash of addresses (src-dst-ip here) picks one member for each flow — so frames of a flow stay in order",
               ["One big transfer between two hosts is limited to one member's speed (1 Gb/s on a 2 × 1 Gb/s bundle).",
                "Change the method with port-channel load-balance src-dst-ip (global configuration)."])
    sw1, d1 = (160, 260), (1000, 260)
    c.device("switch", *sw1, "SW1", ["Po1"])
    c.device("l3switch", *d1, "DSW1", ["Po1"])
    c.rect(330, 190, 120, 140, fill=AMBER[1], stroke=AMBER[0], r=10)
    c.text(390, 248, "hash", 15, AMBER[2], 700, "middle")
    c.text(390, 268, "src-dst-ip", 11.5, AMBER[2], 600, "middle", mono=True)
    c.line(206, 260, 328, 260, FAINT, 3)
    c.line(450, 215, 958, 240, BLUE[0], 6)
    c.line(450, 305, 958, 280, "#94a3b8", 6)
    c.link_label(560, 222, "member Gi0/1", color=BLUE[0], weight=700, mono=True)
    c.link_label(560, 300, "member Gi0/2", color=MUTED, weight=700, mono=True)
    flows = [("10.10.10.11 → 10.10.30.11", BLUE[0], 160), ("10.10.10.12 → 10.0.0.1", BLUE[0], 186),
             ("10.10.30.11 → 10.10.40.11", "#94a3b8", 336), ("10.10.10.11 → 203.0.113.1", "#94a3b8", 362)]
    for t, col, y in flows:
        c.text(700, y, t, 12.5, col if col != "#94a3b8" else MUTED, 700, "middle", mono=True)
    for i, y in enumerate((228, 232, 236)):
        c.rect(600 + i * 70, y - 9 + i * 1.5, 30, 14, fill=BLUE[0], stroke="none", r=3)
    for i, y in enumerate((292, 288, 284)):
        c.rect(620 + i * 70, y - 4 - i * 1.5, 30, 14, fill="#94a3b8", stroke="none", r=3)
    return c


@figure("6.3", "l2-vs-l3-etherchannel")
def f6_3():
    c = Canvas(1160, 520, "6.3", "Layer 2 trunk EtherChannel (Po1) vs Layer 3 routed EtherChannel (Po3)",
               "Both bundle two members with LACP; the difference is what the port-channel interface is",
               ["Layer 3: configure no switchport on the members and the Po BEFORE channel-group, or the bundle comes up as Layer 2 (S)."])
    for x0, t in ((40, "Layer 2 — a trunk bundle"), (600, "Layer 3 — a routed bundle")):
        c.rect(x0, 100, 520, 360, fill="#f8fafc", stroke=LINE, r=14)
        c.text(x0 + 260, 128, t, 15, INK, 700, "middle")
    d, s = (300, 200), (300, 370)
    bundle(c, (d[0], d[1] + 32), (s[0], s[1] - 22), gap=26, color=BLUE[0])
    c.device("l3switch", *d, "DSW1", ["Gi1/0/1, Gi1/0/3 → Po1"], label="right", line_size=11.5)
    c.device("switch", *s, "SW1", ["Gi0/1, Gi0/2 → Po1"], label="right", line_size=11.5)
    c.box(60, 250, 200, 100, None, [("channel-group 1 mode active", INK, 600), "switchport mode trunk", "native 999", "allowed 10,30,40,99"], "blue", size=11.5, pad=10)
    d2, s2 = (860, 200), (860, 370)
    bundle(c, (d2[0], d2[1] + 32), (s2[0], s2[1] - 30), gap=26, color=PURPLE[0])
    c.device("l3switch", *d2, "DSW1", ["Po3 10.0.0.5/30"], label="right", line_size=11.5)
    c.device("l3switch", *s2, "DSW2", ["Po3 10.0.0.6/30"], label="right", line_size=11.5)
    c.box(620, 250, 200, 100, None, [("no switchport", INK, 600), "channel-group 3 mode active", "interface Po3", "ip address …/30"], "purple", size=11.5, pad=10)
    return c


@figure("6.4", "lab-6-1-topology")
def f6_4():
    c = Canvas(1160, 660, "6.4", "Lab 6.1 topology: two Layer 2 trunk bundles and a Layer 3 bundle",
               "Figure 5.6 with each access uplink doubled and a second distribution switch (DSW2)",
               ["Po1/Po2: Layer 2 trunks, LACP active, native 999, allowed 10,30,40,99 · Po3: Layer 3 routed, LACP active.",
                "port-channel load-balance src-dst-ip on DSW1. DSW2 Loopback0 10.255.0.2/32 is the test address."])
    r1, d1, d2, s1, s2 = (420, 150), (420, 300), (900, 300), (200, 470), (640, 470)
    c.cable(r1[0], r1[1] + 26, d1[0], d1[1] - 36, "copper", "G0/0/0", "Gi1/0/24", "10.0.0.0/30")
    bundle(c, (d1[0] - 34, d1[1] + 24), (s1[0] + 30, s1[1] - 20), gap=18, color=BLUE[0])
    bundle(c, (d1[0] + 34, d1[1] + 24), (s2[0] - 30, s2[1] - 20), gap=18, color=BLUE[0])
    bundle(c, (d1[0] + 40, d1[1]), (d2[0] - 40, d2[1]), gap=18, color=PURPLE[0])
    c.link_label(660, 270, "Po3 · Gi1/0/21–22 ↔ Gi1/0/21–22", color=PURPLE[0], weight=700)
    c.link_label(660, 330, "10.0.0.5/30  ↔  10.0.0.6/30", color=PURPLE[0], mono=True)
    c.link_label(160, 400, "Po1 · Gi1/0/1, 1/0/3 ↔ Gi0/1–2", color=BLUE[0], weight=700)
    c.link_label(710, 395, "Po2 · Gi1/0/2, 1/0/4 ↔ Gi0/1–2", color=BLUE[0], weight=700)
    c.device("router", *r1, "R1", ["G0/0/0 10.0.0.1/30"], label="right")
    c.device("l3switch", *d1, "DSW1", label="left")
    c.device("l3switch", *d2, "DSW2", ["Lo0 10.255.0.2/32"], label="right")
    c.device("switch", *s1, "SW1", label="left")
    c.device("switch", *s2, "SW2", label="right")
    for x, s, k, n, l in [(110, s1, "pc", "PC1", "VLAN 10"), (290, s1, "pc", "PC2", "VLAN 30"),
                          (560, s2, "pc", "PC3", "VLAN 10"), (740, s2, "printer", "Printer1", "VLAN 40")]:
        c.cable(s[0] + (x - s[0]) * 0.3, s[1] + 22, x, 548, "copper")
        c.device(k, x, 580, n, [l], s=0.8, name_size=13, line_size=11.5)
    return c


# ----------------------------------------------------------------------------- Chapter 7

@figure("7.1", "edge-port-profiles")
def f7_1():
    c = Canvas(1160, 640, "7.1", "Edge-device port profiles for objective 2.2.a–e",
               "Left: plain access ports · Right: trunks, LACP trunk bundles — and the controller-based AP exception",
               ["Baseline on every edge port: description · switchport mode access/trunk · PortFast · BPDU guard · unused ports shut down."])
    c.rect(40, 100, 520, 480, fill="#f8fafc", stroke=LINE, r=14)
    c.text(300, 128, "Access ports", 15, INK, 700, "middle")
    c.rect(600, 100, 520, 480, fill="#f8fafc", stroke=LINE, r=14)
    c.text(860, 128, "Trunk ports (and bundles)", 15, INK, 700, "middle")
    left = [("pc", "Desktop / laptop", "data VLAN 10", None), ("printer", "Printer", "VLAN 40 · PoE sometimes", None),
            ("camera", "IoT / camera", "isolated IoT VLAN · PoE", None), ("phone", "IP phone + PC", "data 10 + voice VLAN 20 · PoE", None)]
    for i, (k, n, l, _) in enumerate(left):
        y = 190 + i * 100
        c.device(k, 120, y, n, [l], s=0.75, label="right", name_size=13.5, line_size=12)
        c.line(470, y, 540, y, "#64748b", 3)
    right = [("ap", "AP — standalone", "trunk: native mgmt + 1 VLAN per SSID", "trunk"),
             ("hypervisor", "Virtualized host", "trunk of all VM VLANs, often LACP", "lacp"),
             ("firewall", "Network appliance", "trunk or access, often LACP", "lacp"),
             ("ap", "AP — controller-based", "access VLAN 99 only · CAPWAP to WLC", "access")]
    for i, (k, n, l, mode) in enumerate(right):
        y = 190 + i * 100
        c.device(k, 680, y, n, [l], s=0.7, label="right", name_size=13.5, line_size=12)
        if mode == "trunk":
            c.line(1040, y, 1100, y, BLUE[0], 5)
        elif mode == "lacp":
            c.line(1040, y - 5, 1100, y - 5, BLUE[0], 4)
            c.line(1040, y + 5, 1100, y + 5, BLUE[0], 4)
            c.add(f'<ellipse cx="1070" cy="{y}" rx="10" ry="14" fill="none" stroke="{BLUE[0]}" stroke-width="1.8"/>')
        else:
            c.line(1040, y, 1100, y, "#64748b", 3)
            c.pill(1000, y + 30, "exception", "amber", 11)
    ly = 560
    for x, lab, col, two in ((620, "access", "#64748b", False), (760, "trunk", BLUE[0], False), (900, "LACP trunk bundle", BLUE[0], True)):
        if two:
            c.line(x, ly - 4, x + 40, ly - 4, col, 3)
            c.line(x, ly + 4, x + 40, ly + 4, col, 3)
        else:
            c.line(x, ly, x + 40, ly, col, 4 if lab == "trunk" else 3)
        c.text(x + 48, ly + 4, lab, 12, MUTED, 600)
    return c


@figure("7.2", "voice-vlan")
def f7_2():
    c = Canvas(1160, 560, "7.2", "One switch port, two VLANs: the IP phone and the PC behind it",
               "Voice frames are tagged VLAN 20; data frames stay untagged in VLAN 10; the port is still an access port",
               ["switchport mode access · switchport access vlan 10 · switchport voice vlan 20 · power inline auto",
                "The port does not appear in show interfaces trunk, even though voice frames are tagged."])
    sw, ph, pc = (200, 220), (600, 220), (980, 220)
    c.line(sw[0] + 46, sw[1], ph[0] - 40, ph[1], BLUE[0], 6)
    c.link_label(400, 220, "Gi1/0/2 — tagged voice + untagged data + PoE", color=BLUE[0], weight=700)
    c.cable(ph[0] + 40, ph[1], pc[0] - 34, pc[1], "copper", "PC port", "NIC", "untagged data only")
    c.device("switch", *sw, "SW4", ["Catalyst 3650 PoE"], s=1.1)
    c.device("phone", *ph, "IP phone", ["voice VLAN 20 · 10.10.20.x"], s=1.1)
    c.device("pc", *pc, "PC-B", ["data VLAN 10 · 10.10.10.x"])
    c.path(f"M{sw[0] + 20},{sw[1] - 40} C{sw[0] + 120},{sw[1] - 120} {ph[0] - 120},{ph[1] - 120} {ph[0] - 20},{ph[1] - 40}", TEAL[0], 2.2, dash="6 5", arrow="end")
    c.pill(400, 118, "CDP / LLDP-MED: “your voice VLAN is 20”", "teal", 12)
    c.text(400, 316, "PoE powers the phone", 12.5, AMBER[0], 700, "middle")
    def card(x, title, tagged, col):
        F = col
        c.text(x, 372, title, 13.5, INK, 700)
        specs = [("DA", 50, "purple"), ("SA", 50, "purple")]
        if tagged:
            specs.append(("802.1Q VID 20 · PCP 5", 180, "teal"))
        specs += [("Type", 54, "amber"), ("Payload", 90, "blue"), ("FCS", 46, "red")]
        c.cells(x, 386, specs, h=40, size=12)
    card(60, "Voice frame (switch ↔ phone)", True, TEAL)
    card(620, "Data frame (switch ↔ phone ↔ PC)", False, BLUE)
    return c


@figure("7.3", "standalone-vs-lightweight-ap")
def f7_3():
    c = Canvas(1160, 600, "7.3", "Where SSIDs map to VLANs decides the AP's switch port",
               "Standalone AP: trunk to the AP · Controller-based AP: access port + CAPWAP tunnel to the WLC",
               ["CAPWAP: control UDP 5246 (DTLS-encrypted), data UDP 5247. The WLC maps each SSID to a VLAN on its own trunk."])
    c.rect(40, 100, 520, 440, fill="#f8fafc", stroke=LINE, r=14)
    c.text(300, 128, "Standalone (autonomous) AP", 15, INK, 700, "middle")
    c.rect(600, 100, 520, 440, fill="#f8fafc", stroke=LINE, r=14)
    c.text(860, 128, "Controller-based AP (local mode)", 15, INK, 700, "middle")
    # left
    sw, ap = (300, 210), (300, 400)
    c.line(sw[0], sw[1] + 24, ap[0], ap[1] - 30, BLUE[0], 6)
    c.link_label(300, 300, "Gi1/0/4 trunk", color=BLUE[0], weight=700)
    c.text(320, 330, "native 99 (AP mgmt) · allowed 30,35,99", 11.5, BLUE[2], 600)
    c.device("switch", *sw, "SW4", label="right")
    c.device("ap", *ap, "AP-Lobby", ["maps SSIDs to VLANs itself"], s=1.1)
    c.pill(160, 470, "Staff-WiFi → VLAN 30", "green", 11.5)
    c.pill(440, 470, "Guest → VLAN 35", "amber", 11.5)
    # right
    sw2, ap2, wlc = (760, 210), (760, 420), (1010, 230)
    c.cable(sw2[0], sw2[1] + 24, ap2[0], ap2[1] - 30, "copper", None, None, "access VLAN 99")
    c.line(sw2[0] + 46, sw2[1], wlc[0] - 40, wlc[1], BLUE[0], 6)
    c.link_label(890, 200, "trunk", color=BLUE[0], weight=700)
    c.device("switch", *sw2, "SW4", ["Gi1/0/5"], label="left")
    c.device("wlc", *wlc, "WLC", ["SSID → VLAN 30, 35"])
    c.device("ap", *ap2, "LAP-1", ["lightweight AP"], s=1.1)
    c.path(f"M{ap2[0] + 40},{ap2[1] - 10} C{ap2[0] + 220},{ap2[1] - 10} {wlc[0] + 20},{wlc[1] + 160} {wlc[0]},{wlc[1] + 60}", PURPLE[0], 3, dash="9 6", arrow="end")
    c.pill(980, 400, "CAPWAP tunnel", "purple", 12, solid=True)
    c.text(980, 424, "UDP 5246 / 5247", 11.5, PURPLE[2], 600, "middle")
    return c


@figure("7.4", "lab-7-1-topology")
def f7_4():
    c = Canvas(1160, 600, "7.4", "Lab 7.1 topology: one PoE switch, five edge-device profiles",
               "SW4 — Catalyst 3650-24PS with an AC power supply · a new file, independent of Lab 6.1",
               ["PT note: AccessPoint-PT bridges one SSID untagged, so Gi1/0/4 is an access port in VLAN 30 in the simulator.",
                "Gi1/0/11–12 (ESXi-01, Po11) are configuration practice only — no device is attached."])
    sw = (580, 160)
    c.device("switch", *sw, "SW4", ["Catalyst 3650-24PS · PoE"], s=1.3, label="left")
    cols = [(130, "Gi1/0/1", "access VLAN 10", "pc", "PC-A", ["DHCP · 10.10.10.x"]),
            (355, "Gi1/0/2", "VLAN 10 + voice 20 · PoE", "phone", "IP Phone 7960", ["DHCP · 10.10.20.x"]),
            (580, "Gi1/0/3", "access VLAN 40 · PoE off", "printer", "Printer1", ["10.10.40.21/24"]),
            (805, "Gi1/0/4", "access VLAN 30", "ap", "AccessPoint-PT", ["SSID Staff-WiFi"]),
            (1030, "Gi1/0/11–12", "trunk · LACP Po11", "hypervisor", "ESXi-01", ["config practice"])]
    for x, p, mode, k, n, l in cols:
        two = k == "hypervisor"
        if two:
            c.line(sw[0] + 50, sw[1] + 10, x - 4, 330, BLUE[0], 3.5, dash="7 5")
            c.line(sw[0] + 56, sw[1] + 2, x + 6, 326, BLUE[0], 3.5, dash="7 5")
        else:
            c.cable(sw[0] + (x - sw[0]) * 0.08, sw[1] + 30, x, 322, "copper")
        c.pill(x, 280, p, "navy", 11.5, solid=True, mono=True)
        c.device(k, x, 360, n, l + [mode], s=0.85, name_size=13, line_size=11.5)
    # PC-B behind phone and laptop behind AP
    c.cable(355, 460, 355, 492, "copper")
    c.device("pc", 355, 520, "PC-B", ["via the phone's PC port · VLAN 10"], s=0.7, name_size=12.5, line_size=11)
    c.cable(805, 456, 805, 492, "wireless", sw=2.5)
    c.device("laptop", 805, 520, "Laptop", ["wireless · VLAN 30"], s=0.8, name_size=12.5, line_size=11)
    return c

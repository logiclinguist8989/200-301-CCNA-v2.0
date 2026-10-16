"""Chapter 4 — Virtualization; Chapter 5 — VLANs, trunks and SVIs."""

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL,
                    check_flow)


def layer(c, x, y, w, h, text, color, sub=None, size=13):
    c.box(x, y, w, h, text, [sub] if sub else [], color, align="center", size=11.5, title_size=size,
          valign="middle", shadow=False, r=6, pad=8)


# ----------------------------------------------------------------------------- Chapter 4

@figure("4.1", "hypervisor-stacks")
def f4_1():
    c = Canvas(1160, 560, "4.1", "Three software stacks, read from the hardware upward",
               "Type 1 hypervisors sit on the hardware; Type 2 need a host OS; containers share one kernel",
               ["Containers drop the guest OS entirely — they start in seconds and use far less memory than VMs."])
    cols = [(40, "Type 1 — bare-metal", "ESXi · Hyper-V · KVM · Xen"),
            (420, "Type 2 — hosted", "VirtualBox · Workstation · Parallels"),
            (800, "Containers", "Docker · containerd · Podman")]
    W = 320
    for x, t, ex in cols:
        c.text(x + W / 2, 112, t, 16, INK, 700, "middle")
        c.text(x + W / 2, 132, ex, 12, MUTED, 500, "middle")
    base = 470
    # hardware row
    for x, *_ in cols:
        c.rect(x, base, W, 44, fill="url(#gDark)", stroke="none", r=6)
        c.text(x + W / 2, base + 27, "Physical hardware: CPU · RAM · disk · NIC", 12.5, "#ffffff", 600, "middle")
    def apps(x, y, n, guest=True, color="blue"):
        bw = (W - (n - 1) * 8) / n
        for i in range(n):
            ax = x + i * (bw + 8)
            fam_ = [BLUE, GREEN, PURPLE][i]
            if guest:
                c.rect(ax, y, bw, 150, fill=fam_[1], stroke=fam_[0], sw=1.5, r=8)
                c.text(ax + bw / 2, y + 18, f"VM {i + 1}", 11.5, fam_[2], 700, "middle")
                layer(c, ax + 6, y + 28, bw - 12, 36, "App", "grey", size=12)
                layer(c, ax + 6, y + 70, bw - 12, 30, "Bins/Libs", "grey", size=11)
                layer(c, ax + 6, y + 106, bw - 12, 36, "Guest OS", "amber", size=12)
            else:
                c.rect(ax, y + 40, bw, 110, fill=fam_[1], stroke=fam_[0], sw=1.5, r=8)
                c.text(ax + bw / 2, y + 58, f"Container {i + 1}", 11.5, fam_[2], 700, "middle")
                layer(c, ax + 6, y + 68, bw - 12, 36, "App", "grey", size=12)
                layer(c, ax + 6, y + 110, bw - 12, 32, "Bins/Libs", "grey", size=11)
    # Type 1
    x = cols[0][0]
    layer(c, x, base - 56, W, 48, "Type 1 hypervisor", "navy", None, 14)
    apps(x, base - 216, 3)
    # Type 2
    x = cols[1][0]
    layer(c, x, base - 50, W, 42, "Host OS (Windows / macOS / Linux)", "teal", None, 13)
    layer(c, x, base - 98, W, 42, "Type 2 hypervisor (an application)", "navy", None, 13)
    apps(x, base - 258, 3)
    # Containers
    x = cols[2][0]
    layer(c, x, base - 50, W, 42, "Host OS — one shared kernel", "teal", None, 13)
    layer(c, x, base - 98, W, 42, "Container engine", "purple", None, 13)
    apps(x, base - 258, 3, guest=False)
    return c


@figure("4.2", "virtual-switching")
def f4_2():
    c = Canvas(1160, 600, "4.2", "Virtual switching: VM traffic leaves the host as an 802.1Q trunk",
               "vNICs sit in port groups; the vSwitch tags frames with the port group's VLAN; two uplinks form one LACP bundle",
               ["SW1 must allow every port-group VLAN on the trunk, or VMs in a missing VLAN are cut off.",
                "SW1's MAC table learns VM-Web, VM-DB and VM-Mgmt (OUI 00:50:56 = VMware) all on Po1."])
    c.rect(40, 100, 760, 440, fill="#f8fafc", stroke=LINE, r=14, dash="6 5")
    c.text(60, 126, "ESXi-01 — Type 1 hypervisor host", 14, INK, 700)
    vms = [(150, "VM-Web", "Staff · VLAN 10", BLUE), (390, "VM-DB", "Staff · VLAN 10", BLUE), (630, "VM-Mgmt", "Mgmt · VLAN 99", AMBER)]
    for x, n, pg, F in vms:
        c.device("pc", x, 180, n, ["vNIC · own MAC"], s=0.8, name_size=13, line_size=11)
    # port groups
    c.rect(70, 268, 440, 52, fill=BLUE[1], stroke=BLUE[0], r=8)
    c.text(290, 299, "Port group “Staff” — VLAN 10", 13, BLUE[2], 700, "middle")
    c.rect(530, 268, 240, 52, fill=AMBER[1], stroke=AMBER[0], r=8)
    c.text(650, 299, "Port group “Mgmt” — VLAN 99", 13, AMBER[2], 700, "middle")
    for x, *_ in vms:
        c.line(x, 236, x, 266, FAINT, 2, arrow="end")
    c.rect(70, 340, 700, 70, fill="url(#gFront)", stroke="none", r=10)
    c.text(420, 372, "vSwitch (Layer 2 inside the hypervisor)", 15, "#ffffff", 700, "middle")
    c.text(420, 393, "adds 802.1Q tag 10 or 99 on the way out · switches VM-to-VM frames locally", 12, "#d6ebfb", 500, "middle")
    for x in (290, 650):
        c.line(x, 322, x, 338, FAINT, 2, arrow="end")
    # uplinks
    for i, x in enumerate((340, 500)):
        c.rect(x - 50, 440, 100, 40, fill="url(#gDark)", stroke="none", r=6)
        c.text(x, 465, f"vmnic{i}", 13, "#ffffff", 700, "middle", mono=True)
        c.line(x, 410, x, 438, FAINT, 2)
    # trunk to SW1
    sw = (1000, 500)
    c.poly([(340, 480), (340, 506), (952, 506)], BLUE[0], 4, arrow=None)
    c.poly([(500, 480), (500, 494), (952, 494)], BLUE[0], 4, arrow=None)
    c.add(f'<ellipse cx="880" cy="500" rx="12" ry="20" fill="none" stroke="{BLUE[0]}" stroke-width="2"/>')
    c.pill(990, 410, "LACP bundle Po1 · 802.1Q trunk", "blue", 12, solid=True)
    c.text(990, 434, "allowed VLANs 10, 99", 11.5, BLUE[2], 600, "middle")
    c.device("switch", *sw, "SW1", ["Gi1/0/1–2 → Po1"])
    return c


@figure("4.3", "docker-networking")
def f4_3():
    c = Canvas(1160, 560, "4.3", "Default Docker networking: a private bridge behind NAT",
               "Only the published port (-p 8080:80) is reachable from the LAN — 172.17.0.2 is invisible outside the host",
               ["Containers reach the outside world with the host's IP (masquerade NAT) — the same idea as router NAT in Chapter 21."])
    c.device("laptop", 110, 230, "Laptop", ["192.168.1.20", "http://192.168.1.50:8080"])
    c.device("router", 110, 430, "Home router", ["192.168.1.1"])
    c.cable(110, 402, 110, 318, "copper")
    c.rect(300, 110, 820, 400, fill="#f8fafc", stroke=LINE, r=14)
    c.text(320, 136, "Linux host — eth0 192.168.1.50", 14, INK, 700)
    c.rect(330, 160, 220, 120, fill=AMBER[1], stroke=AMBER[0], r=10)
    c.text(440, 190, "iptables NAT", 14, AMBER[2], 700, "middle")
    c.text(440, 212, "DNAT :8080 → 172.17.0.2:80", 12, AMBER[2], 600, "middle", mono=True)
    c.text(440, 232, "MASQUERADE outbound", 12, AMBER[2], 600, "middle", mono=True)
    c.text(440, 258, "(published port)", 11.5, MUTED, 500, "middle")
    c.rect(330, 330, 760, 60, fill="url(#gFront)", stroke="none", r=10)
    c.text(710, 366, "docker0 bridge · 172.17.0.1/16", 15, "#ffffff", 700, "middle", mono=True)
    ctrs = [(650, "web (nginx)", "172.17.0.2", "port 80", True), (880, "app", "172.17.0.3", "not published", False)]
    for x, n, ip, p, pub in ctrs:
        F = GREEN if pub else GREY
        c.rect(x - 95, 170, 190, 110, fill=F[1], stroke=F[0], r=10, sw=2 if pub else 1.5)
        c.text(x, 200, n, 14, INK, 700, "middle")
        c.text(x, 222, ip, 13, MUTED, 600, "middle", mono=True)
        c.text(x, 244, p, 12, F[2] if pub else MUTED, 600, "middle")
        c.line(x, 282, x, 328, FAINT, 2)
        c.text(x + 8, 310, "veth", 11, MUTED, 600)
    # request path
    c.path("M150,215 C230,180 260,190 326,205", GREEN[0], 3, arrow="end")
    c.text(240, 170, "① TCP :8080", 12, GREEN[0], 700, "middle")
    c.line(440, 282, 440, 326, GREEN[0], 3, arrow="end")
    c.text(452, 310, "② to 172.17.0.2:80", 12, GREEN[0], 700)
    c.line(650, 330, 650, 286, GREEN[0], 3, arrow="end")
    c.line(140, 120, 290, 120, RED[0], 2, dash="5 4")
    c.text(215, 110, "✗ 172.17.0.2 unreachable", 11.5, RED[0], 600, "middle")
    return c


@figure("4.4", "virtualbox-network-modes")
def f4_4():
    c = Canvas(1160, 560, "4.4", "VirtualBox NAT, Bridged and Host-only modes",
               "The highlighted line is the VM's path — VirtualBox defaults and a typical home network",
               ["NAT: VM can browse out but the LAN cannot reach it · Bridged: VM is a separate PC on the LAN · Host-only: VM ↔ host only."])
    panels = [(40, "NAT (default)", "VM 10.0.2.15 hides behind the laptop"),
              (420, "Bridged", "VM gets an address from the home router"),
              (800, "Host-only", "Private network between VM and laptop")]
    for x, t, s in panels:
        c.rect(x, 100, 320, 410, fill="#f8fafc", stroke=LINE, r=14)
        c.text(x + 160, 128, t, 16, INK, 700, "middle")
        c.text(x + 160, 148, s, 12, MUTED, 500, "middle")
    # NAT
    x = 40
    c.device("router", x + 160, 200, "Home router", ["192.168.1.1"], s=0.8, label="right", name_size=12.5, line_size=11)
    c.rect(x + 30, 270, 260, 220, fill="#ffffff", stroke=FAINT, r=10, dash="5 4")
    c.text(x + 44, 292, "Laptop", 12, INK, 700); c.text(x + 44, 306, "192.168.1.20", 11, MUTED, 500)
    c.rect(x + 70, 314, 180, 46, fill=AMBER[1], stroke=AMBER[0], r=8)
    c.text(x + 160, 342, "VirtualBox NAT 10.0.2.2", 12, AMBER[2], 700, "middle")
    c.device("pc", x + 160, 420, None, s=0.7)
    c.text(x + 160, 465, "VM 10.0.2.15", 12.5, INK, 700, "middle")
    c.line(x + 160, 392, x + 160, 362, GREEN[0], 3.5)
    c.line(x + 160, 312, x + 160, 230, GREEN[0], 3.5, arrow="end")
    # Bridged
    x = 420
    c.device("router", x + 160, 200, "Home router", ["192.168.1.1 · DHCP"], s=0.8, label="right", name_size=12.5, line_size=11)
    c.rect(x + 30, 270, 260, 220, fill="#ffffff", stroke=FAINT, r=10, dash="5 4")
    c.text(x + 44, 292, "Laptop", 12, INK, 700); c.text(x + 44, 306, "192.168.1.20", 11, MUTED, 500)
    c.rect(x + 70, 314, 180, 46, fill=PANEL, stroke=LINE, r=8)
    c.text(x + 160, 342, "physical NIC (shared)", 12, MUTED, 600, "middle")
    c.device("pc", x + 160, 420, None, s=0.7)
    c.text(x + 160, 465, "VM 192.168.1.60", 12.5, INK, 700, "middle")
    c.line(x + 160, 392, x + 160, 230, GREEN[0], 3.5, arrow="end")
    # Host-only
    x = 800
    c.device("router", x + 160, 200, "Home router", ["not reachable"], s=0.8, label="right", name_size=12.5, line_size=11)
    c.rect(x + 30, 270, 260, 220, fill="#ffffff", stroke=FAINT, r=10, dash="5 4")
    c.text(x + 44, 292, "Laptop", 12, INK, 700); c.text(x + 44, 306, "vboxnet0", 11, MUTED, 500); c.text(x + 196, 292, "192.168.56.1", 11, MUTED, 500)
    c.rect(x + 70, 314, 180, 46, fill=PURPLE[1], stroke=PURPLE[0], r=8)
    c.text(x + 160, 342, "host-only network", 12, PURPLE[2], 700, "middle")
    c.device("pc", x + 160, 420, None, s=0.7)
    c.text(x + 160, 465, "VM 192.168.56.101", 12.5, INK, 700, "middle")
    c.line(x + 160, 392, x + 160, 362, GREEN[0], 3.5, arrow="end")
    c.line(x + 160, 310, x + 160, 236, RED[0], 2, dash="5 4")
    c.text(x + 172, 262, "✗", 16, RED[0], 700)
    return c


# ----------------------------------------------------------------------------- Chapter 5

@figure("5.1", "vlans-broadcast-domains")
def f5_1():
    c = Canvas(1160, 560, "5.1", "A VLAN is a broadcast domain",
               "PC1's broadcast is flooded only to the other VLAN 10 port — PC3, PC4 and the printer never see it",
               ["Dashed boxes are VLAN memberships, not separate hardware. Traffic between VLANs needs a router or Layer 3 switch."])
    sw = (580, 190)
    c.device("switch", *sw, "SW1", ["one physical switch, three broadcast domains"], s=1.4, label="above")
    groups = [(60, 330, "VLAN 10 — Staff · 10.10.10.0/24", BLUE, [("pc", "PC1", "Fa0/1", True), ("pc", "PC2", "Fa0/2", False)]),
              (440, 330, "VLAN 30 — Wireless · 10.10.30.0/24", GREEN, [("pc", "PC3", "Fa0/3", False), ("laptop", "PC4", "Fa0/4", False)]),
              (820, 330, "VLAN 40 — Printers", AMBER, [("printer", "Printer1", "Fa0/5", False)])]
    for gx, gy, t, F, devs in groups:
        w = 280
        c.rect(gx, gy, w, 200, fill=F[1], stroke=F[0], r=14, dash="7 5", sw=2)
        c.text(gx + 14, gy + 186, t, 12.5, F[2], 700)
        n = len(devs)
        for i, (k, name, port, src) in enumerate(devs):
            dx = gx + w / (n + 1) * (i + 1)
            dy = gy + 72
            col = F[0] if F is BLUE else "#94a3b8"
            c.line(dx, dy - 36, sw[0] + (dx - sw[0]) * 0.12, sw[1] + 30, col, 2.5 if F is BLUE else 2)
            c.device(k, dx, dy, name, [port], s=0.8, name_size=13, line_size=11)
    # broadcast arrows
    p1 = 60 + 280 / 3
    p2 = 60 + 280 / 3 * 2
    c.path(f"M{p1 + 14},{362} C{p1 + 60},300 {sw[0] - 120},250 {sw[0] - 56},{sw[1] + 10}", RED[0], 3, arrow="end")
    c.path(f"M{sw[0] - 60},{sw[1] + 26} C{sw[0] - 160},290 {p2 + 40},300 {p2 + 6},{358}", RED[0], 3, arrow="end")
    c.pill(250, 250, "broadcast FFFF.FFFF.FFFF", "red", 12, solid=True)
    return c


@figure("5.2", "dot1q-tag")
def f5_2():
    c = Canvas(1160, 470, "5.2", "The 802.1Q tag: 4 bytes inserted between the source MAC and Type",
               "The sending switch adds the tag on a trunk, recalculates the FCS, and the frame grows to 1522 bytes",
               ["PCP (CoS) 5 is used for voice in Chapter 7. VID 0 and 4095 are reserved; 1–4094 are usable."])
    pos = c.cells(70, 130, [("Dest MAC", 150, "purple", "6"), ("Src MAC", 150, "purple", "6"), ("802.1Q tag", 160, "teal", "4 bytes"),
                            ("Type", 100, "amber", "2"), ("Payload", 260, "blue", "46–1500"), ("FCS", 90, "red", "4 · recalculated")], h=60)
    tx, tw = pos[2]
    zx, zw = 120, 920
    c.path(f"M{tx},192 L{zx},290", TEAL[0], 1.6, dash="5 4")
    c.path(f"M{tx + tw},192 L{zx + zw},290", TEAL[0], 1.6, dash="5 4")
    fields = [("TPID = 0x8100", 16, "teal", "16 bits · “this frame is tagged”"), ("PCP", 3, "amber", "3 bits · priority 0–7"),
              ("DEI", 1, "grey", "1"), ("VID", 12, "blue", "12 bits · VLAN ID 1–4094")]
    x = zx
    for t, bits, col, sub in fields:
        w = zw * bits / 32
        c.cells(x, 290, [(t, w - 2, col)], h=56, size=14)
        if bits > 1:
            c.text(x + w / 2, 368, sub, 12, MUTED, 600, "middle")
        x += w
    c.text(zx + zw * 20 / 32 + zw * 12 / 64, 394, "e.g. 0000 0000 1010 = VLAN 10", 12, BLUE[2], 700, "middle", mono=True)
    return c


@figure("5.3", "frame-across-trunk")
def f5_3():
    c = Canvas(1160, 460, "5.3", "A VLAN 10 frame crossing an 802.1Q trunk",
               "The tag exists only on the trunk — PC1 and PC3 never see it",
               ["Access ports send and receive untagged frames. Native-VLAN frames (999 in this guide) cross the trunk untagged."])
    pc1, sw1, sw2, pc3 = (100, 200), (400, 200), (760, 200), (1060, 200)
    c.cable(pc1[0] + 34, pc1[1], sw1[0] - 46, sw1[1], "copper", None, "Fa0/1")
    c.line(sw1[0] + 46, sw1[1], sw2[0] - 46, sw2[1], BLUE[0], 7)
    c.link_label(580, 200, "802.1Q trunk Gi0/1 ↔ Gi0/1", color=BLUE[0], weight=700)
    c.cable(sw2[0] + 46, sw2[1], pc3[0] - 34, pc3[1], "copper", "Fa0/1")
    c.device("pc", *pc1, "PC1", ["VLAN 10 access"])
    c.device("switch", *sw1, "SW1", ["inserts tag"])
    c.device("switch", *sw2, "SW2", ["reads VID, removes tag"])
    c.device("pc", *pc3, "PC3", ["VLAN 10 access"])
    def frame(x, y, tagged):
        specs = [("DA", 34, "purple"), ("SA", 34, "purple")]
        if tagged:
            specs.append(("VID 10", 58, "teal"))
        specs += [("Type", 42, "amber"), ("Data", 50, "blue"), ("FCS", 38, "red")]
        c.cells(x, y, specs, h=36, size=11)
    steps = [(40, "1  Untagged into the access port", False), (320, "2  SW1 adds VID 10 on the trunk", True),
             (600, "3  SW2 reads VID 10 → VLAN 10", True), (880, "4  Tag removed toward PC3", False)]
    for x, t, tag in steps:
        c.text(x, 330, t, 12.5, INK, 700)
        frame(x, 345, tag)
    for x in (230, 1000):
        pass
    c.line(150, 300, 1010, 300, FAINT, 2, arrow="end")
    return c


@figure("5.4", "inter-vlan-routing")
def f5_4():
    c = Canvas(1160, 600, "5.4", "Inter-VLAN routing: router-on-a-stick vs multilayer-switch SVIs",
               "The highlighted path carries a packet from a VLAN 10 host to a VLAN 30 host",
               ["Router-on-a-stick: one trunk, traffic goes up and back down (hairpin) · SVIs: routed inside DSW1 at hardware speed."])
    c.rect(40, 100, 520, 440, fill="#f8fafc", stroke=LINE, r=14)
    c.text(300, 128, "Router-on-a-stick", 16, INK, 700, "middle")
    c.rect(600, 100, 520, 440, fill="#f8fafc", stroke=LINE, r=14)
    c.text(860, 128, "Multilayer switch with SVIs", 16, INK, 700, "middle")
    # left
    r1, sw = (300, 210), (300, 360)
    c.line(r1[0], r1[1] + 26, sw[0], sw[1] - 24, BLUE[0], 6)
    c.link_label(300, 290, "trunk", color=BLUE[0], weight=700)
    c.device("router", *r1, "R1", ["G0/0/1.10 10.10.10.1 · dot1q 10", "G0/0/1.30 10.10.30.1 · dot1q 30"], label="right", line_size=11.5)
    c.device("switch", *sw, "SW1", label="right")
    for x, n, ip, F in ((160, "PC1", "VLAN 10", BLUE), (440, "PC2", "VLAN 30", GREEN)):
        c.cable(x, 440, sw[0] + (x - sw[0]) * 0.2, sw[1] + 22, "copper")
        c.device("pc", x, 470, n, [ip], s=0.8, name_size=13, line_size=11.5)
    c.path("M170,430 L270,380 L282,250", RED[0], 3, arrow="end")
    c.path("M318,250 L330,380 L430,430", RED[0], 3, arrow="end")
    c.text(240, 320, "up in 10", 11.5, RED[0], 700, "end")
    c.text(340, 320, "down in 30", 11.5, RED[0], 700, "start")
    # right
    d = (860, 260)
    c.device("l3switch", *d, "DSW1", ["ip routing"], label="right", s=1.2)
    c.rect(700, 170, 110, 34, fill=BLUE[1], stroke=BLUE[0], r=8)
    c.text(755, 192, "Vlan10 .10.1", 11.5, BLUE[2], 700, "middle")
    c.rect(910, 170, 110, 34, fill=GREEN[1], stroke=GREEN[0], r=8)
    c.text(965, 192, "Vlan30 .30.1", 11.5, GREEN[2], 700, "middle")
    c.path("M810,187 L908,187", RED[0], 3, arrow="end")
    c.text(860, 162, "routed internally", 11.5, RED[0], 700, "middle")
    for x, n, ip in ((720, "PC1", "VLAN 10"), (1000, "PC2", "VLAN 30")):
        c.cable(x, 440, d[0] + (x - d[0]) * 0.2, d[1] + 34, "copper")
        c.device("pc", x, 470, n, [ip], s=0.8, name_size=13, line_size=11.5)
    return c


@figure("5.5", "vlan-troubleshooting")
def f5_5():
    c = Canvas(1100, 700, "5.5", "VLAN, trunk and gateway troubleshooting — work outward from the host",
               "Assumes the host's IP settings are already correct (Figure 2.6)",
               ["Each check moves one hop further from the host: its port, the VLAN database, the trunks, then the gateway."])
    check_flow(c, "Host cannot reach its gateway or same-VLAN hosts", [
        ("Host port in the wrong VLAN?", "show interfaces <int> switchport → switchport access vlan <id>", "blue"),
        ("VLAN missing from the switch?", "show vlan brief → create the VLAN (vlan <id>) on every switch that needs it", "amber"),
        ("Trunk down, VLAN not allowed, or native mismatch?", "show interfaces trunk → fix mode, allowed list, native VLAN on both ends", "purple"),
        ("Gateway SVI down, missing or wrong IP?", "show ip interface brief → no shutdown, ip routing, correct address", "red"),
    ], end="Layer 2 path is healthy", end_lines=["Move on to routing (Chapter 10)"], start_lines=["Start at the host's own access port"])
    return c


@figure("5.6", "lab-5-1-topology")
def f5_6():
    c = Canvas(1160, 640, "5.6", "Lab 5.1 topology: VLANs, trunks, SVIs and the routed uplink",
               "1 × ISR4331 · 1 × Catalyst 3650-24PS · 2 × 2960-24TT · 3 × PC · 1 × printer — reused in Chapters 6–9",
               ["Trunks: native VLAN 999, allowed 10, 30, 40, 99. Switch-to-switch links use crossover in Packet Tracer.",
                "Management SVIs: SW1 10.10.99.11/24, SW2 10.10.99.12/24, gateway 10.10.99.1."])
    r1, d1, s1, s2 = (580, 150), (580, 300), (300, 430), (860, 430)
    c.cable(r1[0], r1[1] + 26, d1[0], d1[1] - 36, "copper", "G0/0/0", "Gi1/0/24", "routed /30")
    c.line(d1[0] - 36, d1[1] + 20, s1[0] + 40, s1[1] - 18, BLUE[0], 6)
    c.line(d1[0] + 36, d1[1] + 20, s2[0] - 40, s2[1] - 18, BLUE[0], 6)
    c.link_label(470, 362, "trunk Gi1/0/1 ↔ Gi0/1", color=BLUE[0], weight=700)
    c.link_label(690, 362, "trunk Gi1/0/2 ↔ Gi0/1", color=BLUE[0], weight=700)
    c.device("router", *r1, "R1", ["G0/0/0 10.0.0.1/30", "Lo0 203.0.113.1/32"], label="right")
    c.device("l3switch", *d1, "DSW1", ["Gi1/0/24 10.0.0.2/30", "SVIs Vlan10/30/40/99 = 10.10.x.1/24"], label="right")
    c.device("switch", *s1, "SW1", label="left")
    c.device("switch", *s2, "SW2", label="right")
    hosts = [(170, s1, "pc", "PC1", "VLAN 10 · 10.10.10.11", "Fa0/1"), (430, s1, "pc", "PC2", "VLAN 30 · 10.10.30.11", "Fa0/2"),
             (730, s2, "pc", "PC3", "VLAN 10 · 10.10.10.12", "Fa0/1"), (990, s2, "printer", "Printer1", "VLAN 40 · 10.10.40.11", "Fa0/2")]
    for x, s, k, n, l, p in hosts:
        c.cable(s[0] + (x - s[0]) * 0.25, s[1] + 22, x, 525, "copper", p)
        c.device(k, x, 555, n, [l], s=0.85, name_size=13, line_size=11.5)
    return c

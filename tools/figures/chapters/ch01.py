"""Chapter 1 — Networking foundations, cables and interfaces."""

from registry import figure
from svgkit import (Canvas, check_flow, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL,
                    CISCO, NAVY, MONO)


@figure("1.1", "encapsulation")
def f1_1():
    c = Canvas(1100, 600, "1.1", "Each layer wraps the data in its own header on the way down",
               "PC1 sending an HTTPS request to the web server at 203.0.113.80",
               ["TCP header: source port 50123 → destination port 443 (HTTPS)   ·   IP header: 10.10.10.11 → 203.0.113.80, unchanged end to end (without NAT)",
                "Ethernet header: PC1's MAC → R1's MAC (the default gateway), rebuilt at every router hop"])
    rows = [
        ("Application", "OSI layers 5–7", "Data", [("Data (HTTPS)", 200, "blue")], 610),
        ("Transport", "OSI layer 4", "Segment", [("TCP hdr", 120, "green"), ("Data", 200, "blue")], 490),
        ("Network / Internet", "OSI layer 3", "Packet", [("IP hdr", 120, "amber"), ("TCP hdr", 120, "green"), ("Data", 200, "blue")], 370),
        ("Data Link", "OSI layer 2", "Frame", [("Eth hdr", 120, "purple"), ("IP hdr", 120, "amber"), ("TCP hdr", 120, "green"), ("Data", 200, "blue"), ("FCS", 80, "purple")], 250),
    ]
    y = 118
    for name, osi, pdu, cells, x in rows:
        c.text(40, y + 20, name, 15, INK, 700)
        c.text(40, y + 40, osi, 12.5, MUTED)
        c.cells(x, y, cells, h=50)
        c.pill(960, y + 25, pdu, "navy", 13, solid=True)
        y += 74
    c.text(40, y + 20, "Physical", 15, INK, 700)
    c.text(40, y + 40, "OSI layer 1", 12.5, MUTED)
    c.rect(250, y, 640, 50, fill="#0f2540", stroke="#0f2540", r=4)
    bits = "0 1 1 0 1 0 0 1 1 0 1 0 0 0 1 0 1 1 0 1 0 1 1 0 0 1 0 1 1 1 0 0 1 0 1"
    c.text(570, y + 31, bits, 14, "#7dd3fc", 600, "middle", mono=True)
    c.pill(960, y + 25, "Bits", "navy", 13, solid=True)
    # send / receive arrows
    c.line(1040, 120, 1040, y + 50, BLUE[0], 2.5, arrow="end")
    c.text(1040, y + 72, "send", 12, BLUE[0], 600, "middle")
    c.line(1070, y + 50, 1070, 120, GREEN[0], 2.5, arrow="end")
    c.text(1070, 112, "receive", 12, GREEN[0], 600, "middle")
    return c


@figure("1.2", "hop-by-hop-forwarding")
def f1_2():
    c = Canvas(1160, 560, "1.2", "IP addresses stay the same end to end; MAC addresses change at each router",
               "PC1 opens https://203.0.113.80 — the frame is rebuilt when R1 forwards the packet",
               ["With NAT on R1 (Chapter 21), the source IP would also be translated at the Internet edge."])
    y = 190
    xs = {"pc": 110, "sw": 380, "r1": 650, "isp": 870, "srv": 1060}
    c.cable(xs["pc"] + 32, y, xs["sw"] - 42, y, label1="Fa0", label2="Fa0/1")
    c.cable(xs["sw"] + 44, y, xs["r1"] - 38, y, label1="Gi0/2", label2="G0/0/0")
    c.cable(xs["r1"] + 38, y, xs["isp"] - 56, y, label1="G0/0/1")
    c.cable(xs["isp"] + 56, y, xs["srv"] - 30, y)
    c.device("pc", xs["pc"], y, "PC1", ["10.10.10.11"])
    c.device("switch", xs["sw"], y, "SW1", ["Layer 2 switch"])
    c.device("router", xs["r1"], y, "R1", ["Default gateway"], highlight="blue")
    c.device("cloud", xs["isp"], y, "ISP", ["Internet"])
    c.device("server", xs["srv"], y, "Web server", ["203.0.113.80"])
    # travel arrows
    c.line(150, 128, 610, 128, BLUE[0], 2.5, arrow="end")
    c.text(380, 118, "Frame A — links 1 and 2 (SW1 does not change it)", 12.5, BLUE[0], 650, "middle")
    c.line(690, 128, 1020, 128, PURPLE[0], 2.5, arrow="end")
    c.text(855, 118, "Frame B — rebuilt by R1", 12.5, PURPLE[0], 650, "middle")
    # frames
    def frame(x, y, title, color, dst, src, ipsrc):
        c.text(x, y - 10, title, 13.5, INK, 700)
        c.cells(x, y, [(dst[0], 170, "purple", dst[1]), (src[0], 150, "purple", src[1]),
                       ("IP 10.10.10.11 → 203.0.113.80", 230, "amber", ipsrc), ("Data", 70, "blue"), ("FCS", 50, "purple")], h=54, size=12.5)
    frame(40, 330, "Frame A on PC1 → SW1 → R1", BLUE, ("Dst MAC", "R1 G0/0/0"), ("Src MAC", "PC1"), "unchanged")
    frame(40, 430, "Frame B after R1 (toward the ISP)", PURPLE, ("Dst MAC", "next-hop router"), ("Src MAC", "R1 G0/0/1"), "unchanged")
    c.note(760, 320, 360, 170, [
        "• SW1 reads only the destination MAC and",
        "  forwards the frame untouched.",
        "• R1 strips the old Ethernet header, routes",
        "  on the IP destination and writes a new one.",
        "• Source and destination IP never change.",
    ], "blue", 13, title="What changes, what stays")
    return c


@figure("1.3", "ethernet-frame")
def f1_3():
    c = Canvas(1160, 470, "1.3", "Ethernet II frame layout, in transmission order",
               "Field sizes in bytes (not drawn to scale) — the highlighted payload is the IP packet from Figure 1.1",
               ["Minimum frame 64 bytes, maximum 1518 bytes (1522 with an 802.1Q tag). Smaller frames are runts; larger are giants."])
    specs = [("Preamble + SFD", 150, "grey", "7 + 1"), ("Destination MAC", 170, "purple", "6"), ("Source MAC", 150, "purple", "6"),
             ("802.1Q tag", 110, "teal", "4 (trunks only)"), ("Type", 100, "amber", "2"), ("Payload (IP packet)", 280, "blue", "46 – 1500"),
             ("FCS", 90, "red", "4")]
    pos = c.cells(40, 160, specs, h=64, size=13.5)
    c.rect(pos[3][0], 160, pos[3][1], 64, fill="none", stroke=TEAL[0], sw=2, r=4, dash="6 4", shadow=False)
    purposes = ["Clock sync; not counted", "Where the frame goes on this link", "Who sent it on this link",
                "VLAN ID + priority (Ch. 5)", "0x0800 IPv4 · 0x86DD IPv6 · 0x0806 ARP", "MTU 1500 bytes", "CRC check — mismatch = dropped"]
    for (x, w), p in zip(pos, purposes):
        c.line(x + w / 2, 230, x + w / 2, 262, FAINT, 1.4)
        words = p.split(" · ") if "·" in p else [p]
        if len(p) > 22 and "·" not in p:
            mid = p.rfind(" ", 0, len(p) // 2 + 6)
            words = [p[:mid], p[mid + 1:]]
        for i, wd in enumerate(words):
            c.text(x + w / 2, 282 + i * 17, wd, 12, MUTED, 400, "middle")
    c.brace(pos[1][0], pos[-1][0] + pos[-1][1], 140, "Counted in frame size: 64 – 1518 bytes", BLUE[0], up=True)
    c.text(pos[0][0] + pos[0][1] / 2, 140, "Layer 1 only", 12, MUTED, 600, "middle")
    c.cells(40, 350, [("0050.7966.6801", 300, "purple", "MAC address = 48 bits, 12 hex digits")], h=50)
    c.cells(360, 350, [("OUI 0050.79", 180, "purple", "manufacturer (24 bits)"), ("66.6801", 160, "grey", "vendor-assigned (24 bits)")], h=50)
    c.cells(720, 350, [("FFFF.FFFF.FFFF", 170, "red", "broadcast"), ("0100.5Exx.xxxx", 200, "amber", "IPv4 multicast")], h=50)
    return c


@figure("1.4", "switch-forwarding-logic")
def f1_4():
    c = Canvas(1100, 690, "1.4", "A switch learns from the source MAC and forwards on the destination MAC",
               "This logic runs once for every frame that arrives on a port",
               ["Entries age out after 300 seconds by default. Unknown multicast is flooded like a broadcast by default."])
    c.device("switch", 120, 170, "SW1", ["frame arrives on Fa0/1"], s=1.1)
    c.box(260, 120, 330, 92, "1  Learn", ["Record SOURCE MAC → incoming port + VLAN", "in the MAC address table"], "green", highlight=True)
    c.line(185, 170, 255, 166, FAINT, 2, arrow="end")
    c.diamond(425, 300, 300, 104, ["Destination MAC", "broadcast, multicast or unknown?"], "amber")
    c.line(425, 212, 425, 246, FAINT, 2, arrow="end")
    c.box(40, 390, 300, 110, "Flood", ["Out every port in the same VLAN", "except the one it arrived on"], "purple", highlight=True)
    c.poly([(275, 300), (190, 300), (190, 385)], FAINT, 2)
    c.text(230, 290, "yes", 13, AMBER[0], 700, "middle")
    c.diamond(700, 440, 280, 100, ["Known MAC on the", "same incoming port?"], "amber")
    c.poly([(575, 300), (700, 300), (700, 386)], FAINT, 2)
    c.text(640, 290, "no — known unicast", 13, AMBER[0], 700, "middle")
    c.box(420, 540, 250, 64, "Filter", ["Drop the frame"], "red", highlight=True, title_size=14)
    c.poly([(560, 440), (545, 440), (545, 535)], FAINT, 2)
    c.text(525, 470, "yes", 13, AMBER[0], 700, "end")
    c.box(780, 540, 280, 64, "Forward", ["Out that one port only"], "blue", highlight=True, title_size=14)
    c.poly([(840, 440), (920, 440), (920, 535)], FAINT, 2)
    c.text(880, 430, "no", 13, AMBER[0], 700, "middle")
    # MAC table sample
    c.rect(680, 110, 380, 150, fill="#0f172a", stroke="#0f172a", r=10)
    c.text(700, 136, "SW1# show mac address-table dynamic", 12.5, "#7dd3fc", 600, mono=True)
    c.lines(700, 162, ["Vlan  Mac Address     Type     Ports",
                        "----  --------------  -------  -----",
                        "   1  0050.7966.6801  DYNAMIC  Fa0/1",
                        "   1  0050.7966.6802  DYNAMIC  Gi0/1"], 12.5, "#e2e8f0", mono=True, gap=20)
    return c


@figure("1.5", "ios-modes")
def f1_5():
    c = Canvas(1120, 520, "1.5", "Every configuration change starts from privileged EXEC (R1#)",
               "Each arrow is labelled with the command that moves you one level down",
               ["exit: one level up  ·  end or Ctrl+Z: straight back to R1#  ·  disable: R1# back to R1>",
                "conf t is short for configure terminal  ·  do show … runs a show command from any configuration mode"])
    top = 110
    c.box(40, top, 300, 100, "User EXEC", [("R1>", INK, 700), "limited show and ping"], "grey", mono_lines=False)
    c.box(410, top, 300, 100, "Privileged EXEC", [("R1#", BLUE[2], 700), "show, copy, reload, debug"], "blue", highlight=True)
    c.box(780, top, 300, 100, "Global configuration", [("R1(config)#", INK, 700), "hostname, enable secret"], "grey")
    c.line(340, top + 50, 405, top + 50, BLUE[0], 2.2, arrow="end")
    c.link_label(372, top + 36, "enable", mono=True, color=BLUE[0])
    c.line(710, top + 50, 775, top + 50, BLUE[0], 2.2, arrow="end")
    c.link_label(742, top + 36, "conf t", mono=True, color=BLUE[0])
    c.line(405, top + 78, 345, top + 78, FAINT, 1.6, arrow="end", dash="5 4")
    c.link_label(375, top + 92, "disable", mono=True, size=10)
    by = 320
    subs = [(40, "Interface configuration", "R1(config-if)#", "IP address, speed, duplex", "interface g0/0/0"),
            (410, "Line configuration", "R1(config-line)#", "console and VTY login rules", "line vty 0 4"),
            (780, "Router configuration", "R1(config-router)#", "routing protocol settings", "router ospf 1")]
    c.line(930, top + 100, 930, 260, BLUE[0], 2.2)
    c.line(190, 260, 930, 260, BLUE[0], 2.2)
    for x, t, p, d, cmd in subs:
        c.line(x + 150, 260, x + 150, by - 4, BLUE[0], 2.2, arrow="end")
        c.link_label(x + 150, 288, cmd, mono=True, color=BLUE[0])
        c.box(x, by, 300, 100, t, [(p, INK, 700), d], "grey")
    return c


@figure("1.6", "straight-vs-crossover")
def f1_6():
    c = Canvas(1160, 560, "1.6", "Transmit must always land on receive",
               "Straight-through vs crossover pin mapping for 10/100 Ethernet (MDI vs MDI-X)",
               ["Arrows run from transmit (Tx) to receive (Rx). 10/100 Mb/s Ethernet uses pins 1, 2, 3 and 6.",
                "1000BASE-T uses all four pairs in both directions; auto-MDIX lets a port swap its own pairs."])
    # RJ45 plug drawings
    def rj45(x, y, label):
        std_a = label == "T568A"
        c.rect(x, y, 120, 70, fill="url(#gMetal)", stroke="#94a3b8", r=6)
        c.rect(x + 30, y - 14, 60, 16, fill="#e2e8f0", stroke="#94a3b8", r=3)
        cols = ["#f8fafc", "#f97316", "#f8fafc", "#2563eb", "#f8fafc", "#16a34a", "#f8fafc", "#92400e"]
        stripes = ["#f97316", None, "#16a34a", None, "#2563eb", None, "#92400e", None]
        cols568b = ["#fff", "#f97316", "#fff", "#2563eb", "#fff", "#16a34a", "#fff", "#92400e"]
        for i in range(8):
            px = x + 12 + i * 12.5
            if std_a:
                cols568b = ["#fff", "#16a34a", "#fff", "#2563eb", "#fff", "#f97316", "#fff", "#92400e"]
            c.rect(px, y + 10, 8, 50, fill=cols568b[i], stroke="#94a3b8", sw=0.6, r=1)
            st = ["#16a34a" if std_a else "#f97316", None, "#f97316" if std_a else "#16a34a", None, "#2563eb", None, "#92400e", None][i]
            if st:
                c.rect(px + 2.5, y + 10, 3, 50, fill=st, stroke="none", sw=0, r=0)
            c.text(px + 4, y + 82, str(i + 1), 10, MUTED, 600, "middle")
        c.text(x + 60, y + 102, label, 11.5, MUTED, 600, "middle")

    def side(x0, title, left, right, cross):
        c.text(x0, 112, title[0], 16, INK, 700)
        c.text(x0, 132, title[1], 12.5, MUTED)
        c.box(x0, 150, 170, 220, left[0], [], "grey", align="center", title_size=14)
        c.box(x0 + 330, 150, 170, 220, right[0], [], "grey", align="center", title_size=14)
        pins = ["1", "2", "3", "6"]
        for i, p in enumerate(pins):
            y = 210 + i * 42
            c.text(x0 + 24, y + 5, f"{p}  {left[1][i]}", 14, INK, 600, mono=True)
            c.text(x0 + 354, y + 5, f"{p}  {right[1][i]}", 14, INK, 600, mono=True)
        if not cross:
            for i in range(4):
                y = 210 + i * 42
                if i < 2:
                    c.line(x0 + 172, y, x0 + 326, y, BLUE[0], 2.4, arrow="end")
                else:
                    c.line(x0 + 326, y, x0 + 172, y, GREEN[0], 2.4, arrow="end")
        else:
            ys = [210 + i * 42 for i in range(4)]
            c.line(x0 + 172, ys[2], x0 + 326, ys[0], BLUE[0], 2.4, arrow="end")
            c.line(x0 + 172, ys[3], x0 + 326, ys[1], BLUE[0], 2.4, arrow="end")
            c.line(x0 + 326, ys[2], x0 + 172, ys[0], GREEN[0], 2.4, arrow="end")
            c.line(x0 + 326, ys[3], x0 + 172, ys[1], GREEN[0], 2.4, arrow="end")
        rj45(x0 + 25, 400, "T568B")
        rj45(x0 + 355, 400, "T568A" if cross else "T568B")
        c.text(x0 + 250, 440, "B ↔ A" if cross else "B ↔ B", 15, RED[0] if cross else BLUE[0], 700, "middle")

    side(40, ("Straight-through: unlike devices", "PC ↔ switch, router ↔ switch, AP ↔ switch"),
         ("PC (MDI)", ["Tx+", "Tx−", "Rx+", "Rx−"]), ("Switch (MDI-X)", ["Rx+", "Rx−", "Tx+", "Tx−"]), False)
    side(620, ("Crossover: like devices", "switch ↔ switch, PC ↔ PC, router ↔ router"),
         ("Switch (MDI-X)", ["Rx+", "Rx−", "Tx+", "Tx−"]), ("Switch (MDI-X)", ["Rx+", "Rx−", "Tx+", "Tx−"]), True)
    return c


@figure("1.7", "multimode-vs-singlemode")
def f1_7():
    c = Canvas(1160, 610, "1.7", "Multimode bounces light along many paths; single-mode carries one",
               "Core size, light source and light paths (cross-sections and side views not to scale)",
               ["MMF: several paths of different lengths spread a pulse out (modal dispersion) → hundreds of metres.",
                "SMF: one path keeps the pulse sharp → kilometres. Each link uses two strands: Tx on one end to Rx on the other."])

    def fiber(y, title, sub, core_h, jacket, color, mm):
        c.text(40, y, title, 16, INK, 700)
        c.text(40, y + 20, sub, 12.5, MUTED)
        # cross-section
        cx, cy = 130, y + 110
        c.circle(cx, cy, 62, fill=jacket, stroke="#0f2540", sw=1)
        c.circle(cx, cy, 50, fill="#f1f5f9", stroke="#94a3b8", sw=1)
        c.circle(cx, cy, core_h / 2 + 2, fill="#fde68a" if not mm else "#bae6fd", stroke="#0f2540", sw=1)
        c.text(cx, cy + 78, "cladding 125 µm", 11.5, MUTED, 500, "middle")
        # side view
        x0, x1 = 260, 850
        c.rect(x0, cy - 50, x1 - x0, 100, fill="#f1f5f9", stroke="#94a3b8", r=10)
        c.rect(x0, cy - core_h / 2, x1 - x0, core_h, fill="#bae6fd" if mm else "#fde68a", stroke="#64748b", sw=1, r=2)
        # light source
        c.rect(x0 - 50, cy - 18, 44, 36, fill="url(#gDark)", stroke="none", r=5)
        c.text(x0 - 28, cy + 4, "LED" if mm else "LASER", 9.5 if not mm else 10, "#fde047", 700, "middle")
        if mm:
            colors = ["#2563eb", "#16a34a", "#d97706"]
            for k, (amp, per) in enumerate([(0, 0), (core_h / 2 - 4, 120), (core_h / 2 - 4, 70)]):
                if amp == 0:
                    c.line(x0, cy, x1, cy, colors[k], 2.4)
                    continue
                pts = []
                x = x0
                up = True
                while x < x1:
                    pts.append(f"{x:.0f},{cy + (-amp if up else amp):.0f}")
                    x += per / 2
                    up = not up
                pts[0] = f"{x0},{cy}"
                c.add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[k]}" stroke-width="2.2" stroke-linejoin="round" opacity="0.9"/>')
            # pulse spreading
            c.add(f'<path d="M{x1 + 30},{cy + 30} q 30,-90 60,0" fill="#bae6fd" stroke="#2563eb" stroke-width="2"/>')
            c.text(x1 + 60, cy + 52, "wide, smeared pulse", 11.5, MUTED, 600, "middle")
        else:
            c.line(x0, cy, x1, cy, "#dc2626", 3)
            c.add(f'<path d="M{x1 + 45},{cy + 30} q 15,-110 30,0" fill="#fde68a" stroke="#dc2626" stroke-width="2"/>')
            c.text(x1 + 60, cy + 52, "sharp pulse", 11.5, MUTED, 600, "middle")
        c.text(x1 - 10, cy - 58, "core " + ("50 / 62.5 µm" if mm else "≈ 9 µm"), 12, INK, 700, "end")

    fiber(108, "Multimode fiber (MMF)", "Orange (OM1/OM2) or aqua (OM3/OM4) jacket · LED / VCSEL · 1000BASE-SX, 10GBASE-SR",
          44, "#f59e0b", BLUE, True)
    fiber(330, "Single-mode fiber (SMF)", "Yellow jacket · laser · 1000BASE-LX/LH, 10GBASE-LR (10 km)", 10, "#facc15", RED, False)
    # LC connector inset
    c.rect(1010, 130, 120, 300, fill=PANEL, stroke=LINE, r=10)
    c.text(1070, 145, "LC duplex", 12.5, INK, 700, "middle")
    for i, col in enumerate(("#38bdf8", "#facc15")):
        x = 1040 + i * 40
        c.rect(x - 10, 165, 20, 70, fill="#e2e8f0", stroke="#64748b", r=3)
        c.rect(x - 4, 150, 8, 18, fill="#f8fafc", stroke="#64748b", r=2)
        c.rect(x - 6, 235, 12, 90, fill=col, stroke="#64748b", r=3)
    c.text(1050, 345, "Tx", 11, MUTED, 700, "middle")
    c.text(1090, 345, "Rx", 11, MUTED, 700, "middle")
    c.text(1070, 380, "SFP / SFP+ optic", 11, MUTED, 500, "middle")
    c.rect(1030, 390, 80, 18, fill="url(#gMetal)", stroke="#94a3b8", r=3)
    return c


@figure("1.8", "duplex-mismatch")
def f1_8():
    c = Canvas(1160, 540, "1.8", "A duplex mismatch: link up/up, but each side logs different errors",
               "SW1 is hard-coded to 100/full; SW2 is on auto, senses 100 Mb/s and falls back to half duplex",
               ["Always compare counters on BOTH ends. Fix: set both ends identically, or leave both on auto."])
    y = 200
    c.device("switch", 250, y, "SW1", ["Gi0/1 — speed 100, duplex full"], s=1.2)
    c.device("switch", 910, y, "SW2", ["Gi0/1 — auto → 100 / HALF"], s=1.2, highlight="red")
    c.cable(305, y, 855, y, "copper", "Gi0/1", "Gi0/1", "link up/up — pings may still succeed", color="#64748b")
    c.pill(580, 140, "Negotiation fails: SW2 cannot learn the duplex → default half (10/100 Mb/s)", "amber", 12.5)
    c.box(60, 300, 420, 150, "Full-duplex side (SW1)", [
        "Transmits whenever it likes, even while receiving",
        ("CRC errors, runts, input errors  ↑", RED[0], 700),
        "because SW2 aborts frames mid-transmission",
        "when it detects a 'collision'"], "blue")
    c.box(680, 300, 420, 150, "Half-duplex side (SW2)", [
        "Listens first (CSMA/CD) and backs off",
        ("Late collisions, collisions  ↑", RED[0], 700),
        "because SW1 talks over it after the first",
        "64 bytes — impossible on a healthy link"], "red", highlight=True)
    c.text(580, 380, "Users notice:", 13, INK, 700, "middle")
    c.text(580, 400, "slow, worse under load", 13, MUTED, 400, "middle")
    return c


@figure("1.9", "interface-troubleshooting")
def f1_9():
    c = Canvas(1100, 700, "1.9", "Interface troubleshooting: status first, then counters, on both ends",
               "Work down the left column; the first “yes” tells you what to fix",
               ["Only when every check says “no” do you move up to the Layer 2 and Layer 3 checks in later chapters.",
                "Then document the fix and add an interface description."])
    check_flow(c, "show ip interface brief / show interfaces status", [
        ("administratively down?", "no shutdown", "blue"),
        ("err-disabled?", "show logging → fix the cause → shutdown, then no shutdown", "red"),
        ("down/down or notconnect?", "Cable seated? Right type? Length? Far end on? Optics match? Fiber Tx/Rx swapped? Rx dBm too low?", "amber"),
        ("up/up but slow or dropping?", "Compare speed and duplex on both ends; clear counters; watch CRC, runts, late collisions", "purple"),
    ], end="Counters clean but still failing?", end_lines=["The fault is above Layer 1: VLAN, trunk, IP, gateway"],
        start_lines=["Check BOTH ends of the link"], step=116)
    return c


@figure("1.10", "lab-1-1-topology")
def f1_10():
    c = Canvas(1160, 640, "1.10", "Lab 1.1 topology: cables, interfaces and IPv4 addresses",
               "1 × ISR4331 (R1) · 2 × 2960-24TT (SW1, SW2) · 2 × PC · 1 × admin laptop — subnet 10.10.10.0/24",
               ["Straight-through between unlike devices (MDI ↔ MDI-X); crossover between like devices; rollover for the console."])
    r1 = (330, 150); sw1 = (330, 330); sw2 = (830, 330); pc1 = (110, 470); pc2 = (1050, 470); lap = (560, 500)
    c.cable(r1[0], r1[1] + 28, sw1[0], sw1[1] - 24, "copper", "G0/0/0", "Gi0/2", None)
    c.cable(sw1[0] + 46, sw1[1], sw2[0] - 46, sw2[1], "cross", "Gi0/1", "Gi0/1", "crossover", sw=3.5)
    c.cable(pc1[0] + 20, pc1[1] - 30, sw1[0] - 36, sw1[1] + 18, "copper", "Fa0", "Fa0/1")
    c.cable(pc2[0] - 20, pc2[1] - 30, sw2[0] + 36, sw2[1] + 18, "copper", "Fa0", "Fa0/1")
    c.cable(lap[0] - 30, lap[1] - 18, sw1[0] + 30, sw1[1] + 22, "console", "RS-232", "Console", "rollover")
    c.device("router", *r1, "R1", ["ISR4331", "G0/0/0 10.10.10.1/24"], label="right")
    c.device("switch", *sw1, "SW1", ["2960-24TT"], label="left")
    c.device("switch", *sw2, "SW2", ["2960-24TT"], label="right")
    c.device("pc", *pc1, "PC1", ["10.10.10.11/24", "gw 10.10.10.1"])
    c.device("pc", *pc2, "PC2", ["10.10.10.12/24", "gw 10.10.10.1"])
    c.device("laptop", *lap, "Admin", ["out-of-band console"])
    # legend
    lx, ly = 860, 120
    c.rect(lx, ly, 260, 130, fill=PANEL, stroke=LINE, r=10)
    c.text(lx + 16, ly + 24, "Cable legend", 13, INK, 700)
    for i, (lab, col, dash) in enumerate([("Copper straight-through", "#64748b", None), ("Copper crossover", "#d64040", None),
                                          ("Console (rollover)", "#0f9aa8", "8 5")]):
        yy = ly + 52 + i * 26
        c.line(lx + 16, yy, lx + 66, yy, col, 3, dash=dash)
        c.text(lx + 78, yy + 4, lab, 12.5, INK)
    return c

"""Chapter 18 — AAA; Chapter 19 — File transfer and images; Chapter 20 — ACLs."""

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL,
                    sequence, fam, octet_bits)


# ----------------------------------------------------------------------------- Chapter 18

@figure("18.1", "aaa-tacacs-login")
def f18_1():
    c = Canvas(1160, 720, "18.1", "An SSH login authenticated, authorized and accounted by TACACS+",
               "The switch is the AAA client (NAS); the server holds the accounts — TACACS+ uses TCP 49 and encrypts the whole body",
               ["RADIUS (UDP 1812/1813) combines authentication and authorization and encrypts only the password.",
                "TACACS+ separates the three A's, so per-command authorization is possible."])
    sequence(c, [("adm", 200, "laptop", "Administrator", ["ssh -l alice 10.10.99.2"]), ("nas", 580, "l3switch", "DSW1 (AAA client)", ["10.10.99.2"]),
                 ("srv", 960, "server", "AAA-1 (TACACS+)", ["10.10.99.20 · Cisco ISE"])], [
        {"a": "adm", "b": "nas", "t": "SSH session opens — username / password", "c": GREY[0], "n": 1},
        {"a": "nas", "b": "srv", "t": "Authentication START (alice, password)", "s": "TCP 49 · shared key", "c": BLUE[0], "n": 2},
        {"a": "srv", "b": "nas", "t": "Authentication PASS", "c": GREEN[0]},
        {"a": "nas", "b": "srv", "t": "Authorization REQUEST (exec shell)", "c": PURPLE[0], "n": 3},
        {"a": "srv", "b": "nas", "t": "Authorization PASS — priv-lvl 15", "c": GREEN[0]},
        {"a": "nas", "b": "adm", "t": "DSW1#  prompt", "c": GREY[0]},
        {"a": "nas", "b": "srv", "t": "Accounting START … commands … STOP", "s": "for the whole session", "c": BLUE[0], "dash": True, "n": 4},
    ], bottom=640)
    return c


@figure("18.2", "aaa-method-list")
def f18_2():
    c = Canvas(1160, 470, "18.2", "AAA method list: ERROR moves on, FAIL stops",
               "aaa authentication login default group ADMIN-TAC local — tried left to right",
               ["Only an unreachable/timed-out server (ERROR) falls back to local accounts. A reject (FAIL) ends the attempt —",
                "so someone removed from the AAA server cannot get in with an old local password."])
    c.box(40, 160, 180, 90, "Login", ["user + password"], "grey", size=12.5, title_size=15)
    c.line(222, 205, 290, 205, FAINT, 2, arrow="end")
    c.box(294, 150, 260, 110, "1  group ADMIN-TAC", ["ask the TACACS+ servers", "10.10.99.20 (TCP 49)"], "blue", size=12.5, title_size=14.5)
    c.line(556, 180, 760, 140, GREEN[0], 2.4, arrow="end")
    c.text(640, 140, "PASS", 13, GREEN[0], 800, "middle")
    c.box(764, 104, 340, 70, "Access granted", ["server said accept"], "green", size=12.5, title_size=14.5, highlight=True)
    c.line(556, 232, 760, 272, RED[0], 2.4, arrow="end")
    c.text(650, 278, "FAIL (reject)", 13, RED[0], 800, "middle")
    c.box(764, 238, 340, 70, "Access denied", ["local database is NOT tried"], "red", size=12.5, title_size=14.5, highlight=True)
    c.line(424, 262, 424, 330, AMBER[0], 2.4, arrow="end", dash="7 5")
    c.text(436, 302, "ERROR — no answer / all servers dead", 12.5, AMBER[0], 800)
    c.box(294, 334, 260, 70, "2  local", ["username netadmin secret …"], "amber", size=12.5, title_size=14.5)
    return c


@figure("18.3", "lab-18-1-topology")
def f18_3():
    c = Canvas(1160, 540, "18.3", "Lab 18.1: AAA-1 in VLAN 99 serving DSW1 (TACACS+) and SW1 (RADIUS)",
               "Only the devices this lab touches — the rest of the Figure 14.4 campus is unchanged",
               ["Server clients: DSW1 10.10.99.2 TACACS key T4cacs-Sh4red-Key · SW1 10.10.99.11 RADIUS key R4dius-Sh4red-Key.",
                "Server user alice / Al1ce-2026 · local fallback netadmin / N3t-Admin-2026 on both switches."])
    d1, s1, aaa, adm = (300, 190), (580, 360), (900, 360), (300, 420)
    c.cable(d1[0] + 30, d1[1] + 30, s1[0] - 40, s1[1] - 20, "trunk", None, None, "Po1 trunk")
    c.cable(s1[0] + 46, s1[1], aaa[0] - 30, aaa[1], "copper", "Fa0/5", None, "access VLAN 99")
    c.cable(adm[0] + 36, adm[1] - 10, s1[0] - 46, s1[1] + 10, "copper", None, "Fa0/1")
    c.device("l3switch", *d1, "DSW1", ["10.10.99.2 · TACACS+ client"], label="left")
    c.device("switch", *s1, "SW1", ["10.10.99.11 · RADIUS client"], label="below")
    c.device("server", *aaa, "AAA-1", ["10.10.99.20/24 · gw 10.10.99.1", "Services → AAA: On"])
    c.device("laptop", *adm, "PC1 (admin)", ["ssh -l alice …"], s=0.85)
    c.path(f"M{d1[0] + 40},{d1[1] - 10} C{600},{110} {800},{150} {aaa[0] - 6},{aaa[1] - 46}", PURPLE[0], 2.5, arrow="end", dash="8 6")
    c.pill(640, 128, "TACACS+ · TCP 49", "purple", 12, solid=True)
    c.path(f"M{s1[0] + 30},{s1[1] - 30} C{680},{270} {820},{270} {aaa[0] - 20},{aaa[1] - 44}", TEAL[0], 2.5, arrow="end", dash="8 6")
    c.pill(760, 250, "RADIUS · UDP 1812/1813", "teal", 12, solid=True)
    return c


# ----------------------------------------------------------------------------- Chapter 19

@figure("19.1", "scp-server-vs-client")
def f19_1():
    c = Canvas(1160, 520, "19.1", "Who opens the SSH connection decides the role",
               "Left: the switch is the SCP server · Right: the switch is an SCP/SFTP client of a file server",
               ["IOS XE: SCP server and client; SFTP client only. Both run inside SSH (TCP 22) and reuse Chapter 18 users and keys.",
                "SCP server needs: ip scp server enable · SSH · aaa authorization exec (privilege 15)."])
    for x0, t in ((40, "Switch as SCP server"), (600, "Switch as SCP / SFTP client")):
        c.rect(x0, 100, 520, 360, fill="#f8fafc", stroke=LINE, r=14)
        c.text(x0 + 260, 128, t, 15, INK, 700, "middle")
    c.device("laptop", 140, 230, "Admin PC", s=0.9)
    c.device("l3switch", 460, 230, "DSW1", ["ip scp server enable"], s=0.9)
    c.line(186, 230, 420, 230, BLUE[0], 3, arrow="end")
    c.text(303, 218, "opens SSH (TCP 22)", 12, BLUE[0], 700, "middle")
    c.rect(60, 330, 480, 100, fill=PANEL, stroke=LINE, r=8)
    c.text(76, 356, "On the PC:", 12, MUTED, 700)
    c.text(76, 382, "scp -O DSW1.cfg netadmin@10.10.99.2:flash:/", 12.5, INK, 600, mono=True)
    c.text(76, 406, "scp -O netadmin@10.10.99.2:flash:/x.bin .", 12.5, INK, 600, mono=True)
    c.device("l3switch", 700, 230, "DSW1", s=0.9)
    c.device("server", 1020, 230, "FILES", ["10.10.99.30"], s=0.9)
    c.line(744, 230, 990, 230, PURPLE[0], 3, arrow="end")
    c.text(865, 218, "opens SSH (TCP 22)", 12, PURPLE[0], 700, "middle")
    c.rect(620, 330, 480, 100, fill=PANEL, stroke=LINE, r=8)
    c.text(636, 356, "On the switch:", 12, MUTED, 700)
    c.text(636, 382, "copy running-config scp://netadmin@10.10.99.30/…", 12, INK, 600, mono=True)
    c.text(636, 406, "copy running-config sftp://netadmin@10.10.99.30//…", 12, INK, 600, mono=True)
    return c


@figure("19.2", "image-upgrade-workflow")
def f19_2():
    c = Canvas(1160, 520, "19.2", "Software image upgrade workflow with hash verification",
               "Left to right along the top, then back along the middle row — the hash check is the gate",
               ["No valid image at boot drops the device to ROMMON (rommon 1 >) — always check show boot before reloading.",
                "Install mode (Catalyst 9000): install add file flash:<image>.bin activate commit · Bundle mode: boot system flash:<image>.bin"])
    top = [("1", "Choose image", ["exact platform;", "record SHA-512"], "grey"), ("2", "Check space", ["dir flash:", "bytes free > size"], "grey"),
           ("3", "Copy securely", ["copy scp://… flash:"], "blue")]
    for i, (n, t, l, col) in enumerate(top):
        x = 40 + i * 280
        c.box(x, 110, 240, 96, None, [], col)
        c.badge(x + 22, 134, n, "navy")
        c.text(x + 42, 139, t, 14.5, INK, 700)
        for j, ln in enumerate(l):
            c.text(x + 18, 168 + j * 18, ln, 12, MUTED, 500, mono=ln.startswith(("dir", "copy")))
        if i < 2:
            c.line(x + 242, 158, x + 278, 158, FAINT, 2, arrow="end")
    c.diamond(980, 158, 250, 110, ["4  verify /sha512", "matches Cisco's hash?"], "amber", 12.5)
    c.line(842, 158, 852, 158, FAINT, 2, arrow="end")
    c.path("M920,190 C880,240 720,250 700,210", RED[0], 2.2, arrow="end", dash="6 5")
    c.text(780, 262, "mismatch → delete, copy again", 12, RED[0], 700, "middle")
    c.line(980, 213, 980, 288, GREEN[0], 2.2, arrow="end")
    c.text(992, 254, "match", 12, GREEN[0], 700)
    mid = [("5", "Point boot to it", ["boot system … or", "install add … activate"], "blue"), ("6", "Back up config", ["copy run scp://…", "maintenance window"], "grey"),
           ("7", "Reload + confirm", ["show version", "keep old image"], "green")]
    for i, (n, t, l, col) in enumerate(mid):
        x = 860 - i * 300
        c.box(x, 292, 260, 96, None, [], col)
        c.badge(x + 22, 316, n, "navy")
        c.text(x + 42, 321, t, 14.5, INK, 700)
        for j, ln in enumerate(l):
            c.text(x + 18, 350 + j * 18, ln, 12, MUTED, 500)
        if i < 2:
            c.line(x - 2, 340, x - 36, 340, FAINT, 2, arrow="end")
    return c


# ----------------------------------------------------------------------------- Chapter 20

@figure("20.1", "acl-processing")
def f20_1():
    c = Canvas(1160, 560, "20.1", "ACL processing: top-down, first match, implicit deny",
               "A packet walks down the list until one line matches, then leaves with that line's action — later lines are never read",
               ["Order matters: put specific lines before general ones. One ACL per interface, per direction, per protocol.",
                "An ACL with only deny lines blocks everything — it needs at least one permit."])
    aces = [("10", "deny   ip 10.10.30.0 0.0.0.255 10.10.99.0 0.0.0.255", "deny"),
            ("20", "permit tcp 10.10.30.0 0.0.0.255 host 10.10.40.11 eq 631", "permit"),
            ("30", "deny   ip 10.10.30.0 0.0.0.255 10.10.40.0 0.0.0.255", "deny"),
            ("40", "permit ip any any", "permit")]
    c.device("pc", 110, 170, "Packet", ["10.10.30.25 → 10.10.40.11", "TCP 631"], s=0.8, name_size=13, line_size=11.5)
    y = 120
    for seq, txt, act in aces:
        hit = seq == "20"
        c.rect(260, y, 620, 60, fill=GREEN[1] if hit else "#ffffff", stroke=GREEN[0] if hit else LINE, sw=2 if hit else 1.4, r=8)
        c.text(280, y + 36, seq, 13, MUTED, 700, mono=True)
        c.text(320, y + 36, txt, 12.5, INK, 600, mono=True)
        c.line(570, y + 62, 570, y + 80, FAINT, 2, arrow="end")
        c.text(582, y + 76, "no match", 10.5, MUTED, 600)
        col = GREEN if act == "permit" else RED
        c.line(882, y + 30, 960, y + 30, col[0], 2, arrow="end")
        c.pill(1040, y + 30, act.upper(), "green" if act == "permit" else "red", 12, solid=hit)
        y += 82
    c.rect(260, y, 620, 56, fill=RED[1], stroke=RED[0], sw=2, r=8, dash="7 5")
    c.text(280, y + 34, "(implicit)   deny ip any any — invisible, always last", 12.5, RED[2], 700, mono=True)
    c.line(882, y + 28, 960, y + 28, RED[0], 2, arrow="end")
    c.pill(1040, y + 28, "DENY", "red", 12)
    c.path("M150,190 C200,190 220,150 256,150", BLUE[0], 2.5, arrow="end")
    c.text(1040, 262, "first match → stop", 11, GREEN[2], 700, "middle")
    return c


@figure("20.2", "wildcard-matching")
def f20_2():
    c = Canvas(1160, 470, "20.2", "Wildcard mask matching: 10.10.30.0 0.0.0.255",
               "0 = this octet/bit must match · 1 = ignore — the first three octets must equal 10.10.30",
               ["Shortcuts: host 10.10.30.25 = 10.10.30.25 0.0.0.0 · any = 0.0.0.0 255.255.255.255 · wildcard = 255.255.255.255 − subnet mask."])
    cols = [("Wildcard", ["0", "0", "0", "255"], "x"), ("ACL address", ["10", "10", "30", "0"], "x"),
            ("10.10.30.25", ["10", "10", "30", "25"], "ok"), ("10.10.40.11", ["10", "10", "40", "11"], "bad")]
    x0 = 300
    for r, (label, octs, kind) in enumerate(cols):
        y = 120 + r * 72
        c.text(60, y + 32, label, 15, INK, 700, mono=label[0].isdigit())
        for i, o in enumerate(octs):
            x = x0 + i * 150
            must = i < 3
            if kind == "x":
                col = "blue" if (must and r == 0) else ("grey" if r == 0 else ("blue" if must else "grey"))
            elif kind == "ok":
                col = "green" if must else "grey"
            else:
                col = ("red" if i == 2 else "green") if must else "grey"
            c.cells(x, y, [(o, 130, col)], h=50, size=18)
        if kind == "ok":
            c.pill(1000, y + 25, "MATCH ✓", "green", 13, solid=True)
        elif kind == "bad":
            c.pill(1000, y + 25, "NO MATCH ✗", "red", 13, solid=True)
    c.text(x0 + 225, 106, "must match", 12, BLUE[0], 700, "middle")
    c.text(x0 + 515, 106, "ignored", 12, MUTED, 700, "middle")
    return c


@figure("20.3", "lab-20-1-policy")
def f20_3():
    c = Canvas(1160, 600, "20.3", "Lab 20.1 policy: WIRELESS-IN on VLAN 30 and MGMT-ONLY on the VTY lines",
               "Green = permitted · amber = limited to one service · red = denied",
               ["WIRELESS-IN is applied inbound on interface vlan 30 on BOTH DSW1 and DSW2, so the policy survives an HSRP failover.",
                "The extended ACL sits close to the source; DHCP (UDP 67) and ping stay permitted."])
    c.device("laptop", 140, 230, "VLAN 30 — Wireless", ["10.10.30.0/24 (PC2)"])
    c.device("l3switch", 420, 230, "DSW1 / DSW2", ["int vlan 30 · ip access-group", "WIRELESS-IN in"])
    c.line(186, 230, 380, 230, BLUE[0], 3, arrow="end")
    dests = [("VLAN 99 — Management", "10.10.99.0/24 · AAA-1, FILES, switch SVIs", "deny everything", "red"),
             ("Printer1 · VLAN 40", "10.10.40.11", "permit TCP 631 (IPP) only", "amber"),
             ("Rest of VLAN 40", "10.10.40.0/24", "deny", "red"),
             ("Everything else", "DHCP, ping, internet 192.0.2.8 …", "permit ip any any", "green")]
    for i, (t, sub, act, col) in enumerate(dests):
        y = 110 + i * 82
        st, fl, tx = fam(col)
        c.rect(640, y, 480, 70, fill=fl, stroke=st, sw=2.2, r=10)
        c.text(660, y + 28, t, 14, INK, 700)
        c.text(660, y + 50, sub, 12, MUTED, 500)
        c.text(1100, y + 28, act, 12, tx, 700, "end")
        c.path(f"M466,230 C560,230 560,{y + 35} 636,{y + 35}", st, 2, arrow="end")
    c.rect(40, 450, 1080, 70, fill=PURPLE[1], stroke=PURPLE[0], r=10)
    c.text(60, 478, "MGMT-ONLY (standard ACL) → line vty 0 15 · access-class MGMT-ONLY in", 14, PURPLE[2], 700)
    c.text(60, 502, "permit 10.10.99.0 0.0.0.255 · permit host 10.10.10.11 (PC1, admin) · implicit deny — guards SSH to the switches themselves", 12, INK, 500)
    return c

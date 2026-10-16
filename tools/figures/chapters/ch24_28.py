"""Part 2 — Chapters 24–28: VPN, syslog/SNMP, management and Ansible, AI in NetOps, final review."""

from registry import figure
from svgkit import (Canvas, BLUE, GREEN, RED, AMBER, PURPLE, TEAL, GREY, INK, MUTED, FAINT, LINE, PANEL,
                    sequence, fam, wrap)
from chapters.ch06_07 import bundle


# ----------------------------------------------------------------------------- Chapter 24

@figure("24.1", "site-to-site-vs-remote-access")
def f24_1():
    c = Canvas(1160, 600, "24.1", "Site-to-site and remote-access VPNs",
               "Site-to-site: gateway ↔ gateway, transparent to hosts · Remote access: client software ↔ headend",
               ["Both protect confidentiality (AES), integrity (SHA-2 / GCM), authentication (PSK, certificates, user + MFA) and anti-replay.",
                "Firewalls in the path must permit UDP 500, UDP 4500 (NAT-T) and ESP (IP 50) — plus TCP/UDP 443 for TLS remote access."])
    c.text(40, 118, "Site-to-site — permanent, IPsec (IKEv1/IKEv2 + ESP), tunnel mode", 14.5, INK, 700)
    hq, br, net = (230, 230), (930, 230), (580, 230)
    c.device("cloud", *net, "Internet", s=1.1)
    c.line(hq[0] + 38, 230, net[0] - 66, 230, "#94a3b8", 3)
    c.line(net[0] + 66, 230, br[0] - 38, 230, "#94a3b8", 3)
    c.path(f"M{hq[0] + 30},{hq[1] - 26} C{hq[0] + 200},{hq[1] - 110} {br[0] - 200},{br[1] - 110} {br[0] - 30},{br[1] - 26}", BLUE[0], 9, opacity=0.25)
    c.path(f"M{hq[0] + 30},{hq[1] - 26} C{hq[0] + 200},{hq[1] - 110} {br[0] - 200},{br[1] - 110} {br[0] - 30},{br[1] - 26}", BLUE[0], 2.5)
    c.pill(580, 158, "IPsec tunnel — encrypted", "blue", 12, solid=True)
    c.device("router", *hq, "HQ gateway", ["172.16.1.0/24 behind it"])
    c.device("router", *br, "Branch gateway", ["172.16.2.0/24 behind it"])
    for x in (90, 1070):
        c.device("pc", x, 230, None, s=0.65)
        c.line(x + (24 if x < 500 else -24), 230, (hq if x < 500 else br)[0] + (-38 if x < 500 else 38), 230, "#64748b", 2.5)
    c.line(40, 330, 1120, 330, "#e5eaf0", 1.5)
    c.text(40, 368, "Remote access — on demand, IPsec IKEv2 or TLS/DTLS (e.g. Cisco Secure Client), user authentication", 14.5, INK, 700)
    lap, net2, head, lan = (150, 460), (500, 460), (800, 460), (1030, 460)
    c.device("laptop", *lap, "Remote user", ["VPN client software"])
    c.device("cloud", *net2, "Internet / home Wi-Fi")
    c.device("firewall", *head, "VPN headend", ["firewall / router", "AAA + MFA"])
    c.device("server", *lan, "Corporate LAN")
    c.line(lap[0] + 40, 460, net2[0] - 56, 460, "#94a3b8", 3)
    c.line(net2[0] + 56, 460, head[0] - 40, 460, "#94a3b8", 3)
    c.line(head[0] + 40, 460, lan[0] - 30, 460, "#64748b", 3)
    c.path(f"M{lap[0] + 30},{lap[1] - 30} C{lap[0] + 200},{lap[1] - 100} {head[0] - 200},{head[1] - 100} {head[0] - 30},{head[1] - 36}", PURPLE[0], 9, opacity=0.25)
    c.path(f"M{lap[0] + 30},{lap[1] - 30} C{lap[0] + 200},{lap[1] - 100} {head[0] - 200},{head[1] - 100} {head[0] - 30},{head[1] - 36}", PURPLE[0], 2.5)
    c.pill(475, 396, "full tunnel or split tunnel", "purple", 12, solid=True)
    return c


@figure("24.2", "esp-transport-vs-tunnel")
def f24_2():
    c = Canvas(1160, 520, "24.2", "ESP transport mode vs tunnel mode",
               "Tunnel mode hides the original IP header behind a new one; transport mode keeps it",
               ["The new IP header carries the gateways' public addresses, so private addresses cross the internet unseen.",
                "ESP is IP protocol 50. AH (protocol 51) authenticates but never encrypts and does not survive NAT."])
    c.text(40, 118, "Original packet", 14, INK, 700)
    c.cells(40, 130, [("IP header", 180, "grey"), ("TCP", 120, "grey"), ("Data", 300, "grey")], h=46, size=13.5)
    c.text(40, 220, "ESP transport mode — host to host (or GRE over IPsec); original header kept", 14, INK, 700)
    p = c.cells(40, 252, [("IP header", 180, "grey"), ("ESP hdr", 120, "amber"), ("TCP", 120, "blue"), ("Data", 300, "blue"),
                          ("ESP trailer", 140, "blue"), ("ESP auth", 120, "amber")], h=46, size=13.5)
    c.brace(p[2][0], p[4][0] + p[4][1], 246, "encrypted", BLUE[0], up=True)
    c.brace(p[1][0], p[4][0] + p[4][1], 304, "authenticated (integrity check)", MUTED, up=False)
    c.text(40, 360, "ESP tunnel mode — gateway to gateway (site-to-site, remote access); the default on Cisco routers", 14, INK, 700)
    p = c.cells(40, 392, [("New IP hdr", 150, "red"), ("ESP hdr", 110, "amber"), ("Orig IP hdr", 150, "blue"), ("TCP", 100, "blue"),
                          ("Data", 230, "blue"), ("ESP trailer", 130, "blue"), ("ESP auth", 110, "amber")], h=46, size=13.5)
    c.brace(p[2][0], p[5][0] + p[5][1], 386, "encrypted", BLUE[0], up=True)
    c.brace(p[1][0], p[5][0] + p[5][1], 444, "authenticated", MUTED, up=False)
    c.text(p[0][0] + 75, 456, "public IPs", 11.5, RED[0], 700, "middle")
    return c


@figure("24.3", "lab-24-1-topology")
def f24_3():
    c = Canvas(1160, 520, "24.3", "Lab 24.1: the tunnel carries 172.16 traffic the ISP cannot route",
               "A separate Packet Tracer file — three 2911 routers and two PCs; it does not change the campus",
               ["HQ and BR: default route to the ISP; crypto ACL 110 matches 172.16.1.0/24 ↔ 172.16.2.0/24 (BR mirrors it).",
                "Without the tunnel the ISP drops 172.16.x packets; with it they travel inside ESP between 203.0.113.1 and .6."])
    pcs = (100, 300)
    hq, isp, br, pcb = (360, 300), (580, 300), (800, 300), (1060, 300)
    c.cable(pcs[0] + 34, 300, hq[0] - 38, 300, "copper")
    c.cable(hq[0] + 38, 300, isp[0] - 38, 300, "copper", "G0/1 .1/30", "G0/0 .2")
    c.cable(isp[0] + 38, 300, br[0] - 38, 300, "copper", "G0/1 .5", ".6/30 G0/1")
    c.cable(br[0] + 38, 300, pcb[0] - 34, 300, "copper")
    c.path(f"M{hq[0]},{hq[1] - 40} L{hq[0]},170 L{br[0]},170 L{br[0]},{br[1] - 40}", BLUE[0], 3)
    c.pill(580, 150, "IPsec tunnel · crypto map VPN-MAP · pre-shared key · AES-256 · SHA", "blue", 12.5, solid=True)
    c.device("pc", *pcs, "PC-HQ", ["172.16.1.10/24", "gw 172.16.1.1"])
    c.device("router", *hq, "HQ (2911)", ["G0/0 172.16.1.1", "G0/1 203.0.113.1/30"], highlight="blue")
    c.device("router", *isp, "ISP (2911)", ["G0/0 203.0.113.2", "G0/1 203.0.113.5"])
    c.device("router", *br, "BR (2911)", ["G0/1 203.0.113.6/30", "G0/0 172.16.2.1"], highlight="blue")
    c.device("pc", *pcb, "PC-BR", ["172.16.2.10/24", "gw 172.16.2.1"])
    c.text(580, 420, "knows only the two /30 links", 12.5, RED[0], 700, "middle")
    return c


# ----------------------------------------------------------------------------- Chapter 25

@figure("25.1", "syslog-anatomy")
def f25_1():
    c = Canvas(1160, 470, "25.1", "Anatomy of an IOS syslog message",
               "seq-no: timestamp: %FACILITY-SEVERITY-MNEMONIC: description",
               ["service sequence-numbers adds the seq-no · service timestamps log datetime msec localtime show-timezone sets the timestamp.",
                "SYS-5-CONFIG_I is what you search for in documentation and filters."])
    parts = [("000234:", "Sequence number", "service sequence-numbers", "grey"),
             ("Oct 15 2026 10:03:05.117 UTC:", "Timestamp", "service timestamps …", "teal"),
             ("%SYS", "Facility", "IOS component", "blue"),
             ("-5", "Severity", "0–7 (5 = notifications)", "amber"),
             ("-CONFIG_I:", "Mnemonic", "the event code", "purple"),
             ("Configured from console by netadmin on vty0 (10.10.99.21)", "Description", "who, how, from where", "green")]
    c.rect(40, 116, 1080, 84, fill="#0f172a", stroke="none", r=10)
    x = 60
    y = 150
    for i, (tok, t, d, col) in enumerate(parts):
        st = fam(col)[0] if col != "grey" else "#94a3b8"
        if i == 5:
            x, y = 60, 186
        w = len(tok) * 9.15
        c.text(x, y, tok, 15, "#e2e8f0", 600, mono=True)
        c.line(x, y + 6, x + w - 4, y + 6, st, 3)
        x += w + 10
    for i, (tok, t, d, col) in enumerate(parts):
        bx = 40 + (i % 3) * 365
        by = 236 + (i // 3) * 92
        c.box(bx, by, 350, 76, t, [d, (tok if len(tok) < 34 else tok[:31] + "…", fam(col)[2] if col != "grey" else INK, 600)], col, size=12, title_size=14)
    return c


@figure("25.2", "syslog-severity-threshold")
def f25_2():
    c = Canvas(1160, 560, "25.2", "Syslog severity levels and the logging threshold",
               "Lower number = more severe — a configured level sends that level AND every more severe one",
               ["Mnemonic for the order: “Every Awesome Cisco Engineer Will Need Ice cream Daily” (0 → 7).",
                "Defaults: console and monitor 7 (debugging); syslog server (logging trap) 6 (informational), UDP 514."])
    levels = [("0", "emergencies", "system unusable"), ("1", "alerts", "immediate action needed"), ("2", "critical", "PSECURE_VIOLATION, BLOCK_BPDUGUARD"),
              ("3", "errors", "LINK-3-UPDOWN"), ("4", "warnings", "LOGIN_FAILED, NATIVE_VLAN_MISMATCH"), ("5", "notifications", "LINEPROTO-5-UPDOWN, CONFIG_I, ADJCHG"),
              ("6", "informational", "IPACCESSLOGP, ADDRESS_ASSIGN"), ("7", "debugging", "debug output")]
    shades = ["#7f1d1d", "#991b1b", "#b91c1c", "#dc2626", "#ea580c", "#d97706", "#2563eb", "#64748b"]
    y = 110
    for (n, k, ex), col in zip(levels, shades):
        sent = int(n) <= 6
        c.rect(120, y, 620, 46, fill=col if sent else "#f1f5f9", stroke=col, r=8, sw=1.5)
        c.text(144, y + 30, n, 18, "#ffffff" if sent else col, 800, mono=True)
        c.text(184, y + 30, k, 15, "#ffffff" if sent else INK, 700)
        c.text(360, y + 30, ex, 12, "#ffffff" if sent else MUTED, 500, mono=True)
        y += 52
    c.path("M760,112 L780,112 L780,466 L760,466", BLUE[0], 2.5)
    c.text(800, 280, "logging trap informational", 14, BLUE[0], 800, mono=True)
    c.text(800, 304, "→ sends levels 0 – 6 to 10.10.99.40", 13, INK, 600)
    c.text(800, 506, "level 7 stays on the device", 12.5, MUTED, 600)
    c.line(60, 120, 60, 500, INK, 2, arrow="end")
    c.text(48, 300, "less severe", 12, MUTED, 700, "middle", rotate=-90)
    return c


@figure("25.3", "snmp-manager-agent")
def f25_3():
    c = Canvas(1160, 470, "25.3", "SNMP: manager, agent, operations and ports",
               "Polling: the manager asks on UDP 161 · Notifications: the agent tells the manager on UDP 162",
               ["Traps are unacknowledged; Informs (v2c/v3) are resent until confirmed. SNMPv3 authPriv adds authentication (SHA) and encryption (AES).",
                "OIDs address values in the MIB: 1.3.6.1.2.1.1.5.0 = sysName · 1.3.6.1.2.1.2.2.1.10 = ifInOctets."])
    nms, ag = (170, 220), (990, 220)
    c.device("controller", *nms, "SNMP manager (NMS1)", ["10.10.99.40 · graphs, alarms"], s=1.1)
    c.device("router", *ag, "R1 — SNMP agent", ["MIB: sysName, ifInOctets, CPU …"], s=1.2)
    c.line(270, 150, 890, 150, BLUE[0], 2.6, arrow="end")
    c.text(580, 138, "Get · GetNext · GetBulk · Set  →  UDP 161", 13, BLUE[0], 700, "middle")
    c.line(890, 210, 270, 210, GREEN[0], 2.6, arrow="end")
    c.text(580, 200, "Response (value of the OID)", 13, GREEN[0], 700, "middle")
    c.line(890, 270, 270, 270, AMBER[0], 3, arrow="end", dash="8 5")
    c.text(580, 260, "Trap / Inform  →  UDP 162 (agent starts it)", 13, AMBER[0], 700, "middle")
    c.box(40, 330, 1080, 62, None, [("v1 / v2c: community string in clear text (RO / RW)  ·  v3: users, groups, noAuthNoPriv / authNoPriv / authPriv", INK, 600)], "grey", size=13, valign="middle")
    return c


# ----------------------------------------------------------------------------- Chapter 26

@figure("26.1", "five-management-approaches")
def f26_1():
    c = Canvas(1160, 600, "26.1", "Five network management approaches",
               "Each step down moves the source of truth further from the individual device",
               ["The approaches combine: a controller for the campus, Ansible playbooks in Git for routers, the CLI for troubleshooting."])
    rows = [("Device-based", "CLI / GUI on each device", "each running-config", "cli", "grey"),
            ("Cloud-based", "vendor dashboard (e.g. Meraki); devices call home", "vendor cloud service", "cloud", "teal"),
            ("Controller-based", "on-prem controller (Catalyst Center, WLC, SD-WAN)", "the controller's database", "controller", "blue"),
            ("Automation-based", "scripts / Ansible push the same change everywhere", "scripts + variables", "robot", "purple"),
            ("Infrastructure as code", "files in Git → review → pipeline deploys", "the Git repository", "file", "green")]
    y = 108
    for i, (t, how, truth, icon, col) in enumerate(rows):
        F = fam(col)
        x = 40 + i * 40
        c.rect(x, y, 1080 - i * 40, 80, fill=F[1] if col != "grey" else PANEL, stroke=F[0], r=12, sw=1.6)
        if icon == "cli":
            c.rect(x + 22, y + 18, 56, 44, fill="#0f172a", stroke="none", r=6)
            c.text(x + 30, y + 46, ">_", 16, "#86efac", 700, mono=True)
        else:
            c.device(icon, x + 50, y + 40, None, s=0.55)
        c.text(x + 100, y + 32, t, 16, INK, 700)
        c.text(x + 100, y + 56, how, 12.5, MUTED, 500)
        c.text(1100, y + 32, "source of truth", 11, MUTED, 600, "end")
        c.text(1100, y + 56, truth, 13.5, F[2] if col != "grey" else INK, 700, "end")
        y += 92
    c.line(24, 120, 24, 560, BLUE[0], 2, arrow="end")
    return c


@figure("26.2", "controller-north-south")
def f26_2():
    c = Canvas(1160, 600, "26.2", "Controller-based management: northbound and southbound interfaces",
               "Operators and scripts talk only to the controller; the controller talks to the devices",
               ["Northbound: usually a REST API with JSON over HTTPS. Southbound: NETCONF (XML over SSH, port 830), RESTCONF (HTTPS),",
                "SSH CLI, SNMP — and CAPWAP for lightweight APs. The controller keeps the desired state and translates intent into configuration."])
    apps = [("user", "Operator / GUI"), ("file", "Scripts · Ansible"), ("controller", "Dashboards · ITSM")]
    for i, (k, n) in enumerate(apps):
        c.device(k, 300 + i * 280, 150, n, s=0.75, name_size=13)
    for i in range(3):
        c.line(300 + i * 280, 205, 300 + i * 280 + (580 - 300 - i * 280) * 0.5, 292, BLUE[0], 2.2, arrow="both")
    c.pill(580, 240, "NORTHBOUND · REST API · JSON over HTTPS", "blue", 12.5, solid=True)
    c.rect(240, 296, 680, 90, fill="url(#gFront)", stroke="none", r=14)
    c.text(580, 334, "Controller — Catalyst Center · WLC · SD-WAN Manager", 16, "#ffffff", 700, "middle")
    c.text(580, 358, "desired state · inventory · policy · images · assurance", 12.5, "#d6ebfb", 500, "middle")
    devs = [("router", "Routers"), ("l3switch", "Distribution"), ("switch", "Access"), ("ap", "Lightweight APs")]
    for i, (k, n) in enumerate(devs):
        x = 260 + i * 213
        c.line(580 + (x - 580) * 0.3, 388, x, 464, PURPLE[0], 2.2, arrow="both")
        c.device(k, x, 490, n, s=0.8, name_size=13)
    c.pill(580, 420, "SOUTHBOUND · NETCONF · RESTCONF · SSH · SNMP · CAPWAP", "purple", 12.5, solid=True)
    return c


@figure("26.3", "ansible-iac-workflow")
def f26_3():
    c = Canvas(1160, 640, "26.3", "Ansible architecture and an infrastructure-as-code workflow",
               "The control node reads inventory and playbooks from Git and opens SSH sessions — nothing is installed on the devices",
               ["Idempotent: running the playbook again changes nothing if the device already matches. Drift = a device differs from the repository.",
                "Rollback = revert the commit and let the pipeline deploy the previous state."])
    c.rect(40, 100, 1080, 270, fill="#f8fafc", stroke=LINE, r=14)
    c.text(60, 126, "Ansible architecture (agentless)", 14, INK, 700)
    c.rect(80, 150, 330, 190, fill=BLUE[1], stroke=BLUE[0], r=12, sw=2)
    c.text(100, 176, "Control node (Linux)", 14, BLUE[2], 700)
    for i, (t, d) in enumerate([("inventory.ini", "devices + groups"), ("show.yml", "playbook → plays → tasks"),
                                ("group_vars/ · vault", "variables, encrypted secrets"), ("cisco.ios collection", "ios_command, ios_config …")]):
        c.text(100, 206 + i * 34, t, 12.5, INK, 700, mono=True)
        c.text(100, 222 + i * 34, d, 11, MUTED, 500)
    devs = [("router", "R1", 175), ("l3switch", "DSW1 / DSW2", 255), ("switch", "SW1 / SW2", 330)]
    for k, n, y in devs:
        c.line(412, 245, 820, y - 6, TEAL[0], 2.2, arrow="end")
        c.device(k, 860, y - 6, n, s=0.6, label="right", name_size=13)
    c.pill(620, 160, "SSH (network_cli) · parallel", "teal", 12, solid=True)
    c.text(60, 410, "Infrastructure-as-code workflow", 14, INK, 700)
    steps = [("1", "Branch + edit", "add VLAN 50 in", "group_vars/switches.yml", "grey"),
             ("2", "Pull request", "colleague reviews", "the diff", "blue"),
             ("3", "Automated checks", "lint + dry run", "--check --diff", "amber"),
             ("4", "Merge → pipeline", "CI/CD runs the", "playbook, verifies", "green"),
             ("5", "Rollback", "revert the commit,", "redeploy", "red")]
    for i, (n, t, a, b, col) in enumerate(steps):
        x = 40 + i * 220
        c.box(x, 426, 200, 110, None, [], col)
        c.badge(x + 22, 450, n, "navy")
        c.text(x + 40, 455, t, 13.5, INK, 700)
        c.text(x + 16, 486, a, 12, MUTED, 500)
        c.text(x + 16, 506, b, 12, MUTED, 500, mono=b.startswith(("--", "group")))
        if i < 4:
            c.line(x + 202, 480, x + 218, 480, FAINT, 2, arrow="end")
    return c


# ----------------------------------------------------------------------------- Chapter 27

@figure("27.1", "agent-loop")
def f27_1():
    c = Canvas(1160, 640, "27.1", "The agent loop, its tools and guardrails",
               "An agent gets a goal, plans a step, acts through a tool, observes the result and evaluates — until done or it needs a person",
               ["Tools are the agent's only way to see or touch the network (often published through the Model Context Protocol, MCP).",
                "Generative AI answers once and a person acts; an agent acts itself — so the main risk is a wrong action at machine speed."])
    c.device("user", 110, 300, "Goal", ["from a person, alert or ticket"], s=1.0)
    c.line(150, 300, 250, 300, FAINT, 2, arrow="end")
    cx, cy, R = 470, 300, 140
    steps = [("Plan", "choose the next step", -90, "blue"), ("Act", "call a tool", 0, "purple"),
             ("Observe", "read the result", 90, "teal"), ("Evaluate", "goal met? need a human?", 180, "amber")]
    import math
    c.circle(cx, cy, R, fill="none", stroke="#cbd5e1", sw=3, dash="8 6")
    for t, d, ang, col in steps:
        a = math.radians(ang)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        c.box(x - 86, y - 34, 172, 68, t, [d], col, align="center", size=11.5, title_size=14.5)
    for ang in (-45, 45, 135, 225):
        a = math.radians(ang)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        da = math.radians(ang + 90)
        c.line(x - 8 * math.cos(da), y - 8 * math.sin(da), x + 8 * math.cos(da), y + 8 * math.sin(da), FAINT, 2.5, arrow="end")
    c.device("robot", cx, cy, None, s=1.0)
    c.text(cx, cy + 50, "LLM-based agent", 12, PURPLE[2], 700, "middle")
    tools = [("Read-only CLI / show", "teal"), ("Telemetry · SNMP · syslog", "teal"), ("Ticketing (ITSM)", "blue"),
             ("Source of truth · Git", "green"), ("Automation (Ansible) — gated", "amber")]
    c.text(840, 128, "Tools", 14, INK, 700)
    for i, (t, col) in enumerate(tools):
        y = 150 + i * 56
        F = fam(col)
        c.rect(840, y, 280, 44, fill=F[1], stroke=F[0], r=8)
        c.text(858, y + 28, t, 13, F[2], 700)
        c.line(700, cy, 836, y + 22, "#cbd5e1", 1.5)
    c.rect(40, 476, 1080, 58, fill=RED[1], stroke=RED[0], r=10)
    c.text(60, 501, "Guardrails", 13.5, RED[2], 800)
    c.text(60, 522, "least privilege (read-only by default) · approval gates · dry runs · audit log · step / rate limits · treat tool output as data, not instructions", 12, INK, 500)
    return c


@figure("27.2", "autonomy-levels")
def f27_2():
    c = Canvas(1160, 470, "27.2", "Levels of autonomy for AI agents in network operations",
               "Each step to the right lets the agent do more alone — and raises the impact of a mistake",
               ["Match the level to the task: alert triage can act read-only; configuration changes stay at “recommend” with a person approving."])
    levels = [("Assist", "summarise, explain, spot trends", "grey"), ("Recommend", "propose a fix; human approves", "blue"),
              ("Act within guardrails", "routine, reversible actions", "amber"), ("Closed loop", "detect → fix → verify alone", "red")]
    for i, (t, d, col) in enumerate(levels):
        x = 40 + i * 275
        c.box(x, 120, 255, 110, t, [d], col, size=12.5, title_size=16, highlight=col != "grey")
        if i < 3:
            c.line(x + 257, 175, x + 273, 175, FAINT, 2, arrow="end")
    c.line(60, 270, 1100, 270, AMBER[0], 6, arrow="end")
    c.text(580, 260, "more autonomy → bigger impact of a mistake → more guardrails needed", 13, AMBER[2], 700, "middle")
    c.line(60, 330, 1100, 330, INK, 1.5)
    c.pill(300, 330, "human IN the loop — approves each step", "green", 12.5, solid=True)
    c.pill(860, 330, "human ON the loop — supervises, can stop it", "purple", 12.5, solid=True)
    return c


@figure("27.3", "operations-prompt-components")
def f27_3():
    c = Canvas(1160, 640, "27.3", "The four components of an operations prompt",
               "Built top to bottom into one troubleshooting prompt — only the relevant evidence, no secrets",
               ["Selecting the best prompt: discard any that leaks restricted data → prefer a specific task with constraints → a fitting persona",
                "→ a checkable output format → real evidence instead of guesses."])
    comps = [("1  Persona", "You are a senior network engineer helping a junior NOC colleague.", "blue"),
             ("2  Instructions", "OSPF between R1 and R2 (IOS XE 17.x) is stuck in EXSTART. Using only the outputs below, find the most likely cause. Do not invent commands; say if you need more data.", "purple"),
             ("3  Data classification", "Pasted: show ip ospf neighbor + interface MTU lines (sanitised, internal). Removed: enable secret, TACACS+ key, SNMP community → <REDACTED>.", "amber"),
             ("4  Output format", "Answer as a table: Cause | Evidence line | Fix command | Risk — then a 3-step verification plan.", "green")]
    y = 108
    for t, body, col in comps:
        F = fam(col)
        lines = wrap(body, 112)
        h = 44 + len(lines) * 20
        c.rect(40, y, 1080, h, fill=F[1], stroke=F[0], r=10, sw=1.6)
        c.rect(40, y, 8, h, fill=F[0], stroke="none", r=3)
        c.text(64, y + 28, t, 14.5, F[2], 800)
        for i, ln in enumerate(lines):
            c.text(64, y + 52 + i * 20, ln, 13, INK, 500)
        y += h + 14
    c.box(40, y + 4, 1080, 60, None, [("Restricted data never goes in: passwords, enable secrets, pre-shared keys, SNMP communities, private keys, TACACS+/RADIUS keys.", RED[2], 600)],
          "red", size=13, valign="middle")
    return c


# ----------------------------------------------------------------------------- Chapter 28

@figure("28.1", "final-campus-lab")
def f28_1():
    c = Canvas(1160, 780, "28.1", "The finished campus lab — all features",
               "The map for every Chapter 28 scenario: routing, gateway, NAT and security at the core; hosts and Layer 2 protections at the edge",
               ["VLANs 10 Staff · 30 Wireless · 40 Printers/IoT · 99 Management (native 999 on trunks). STP roots: DSW1 10/30, DSW2 40/99.",
                "Management in VLAN 99: AAA-1 .20 · FILES .30 · NMS1 .40 · DNS1 .53. WEB1 10.10.40.80 is published as 198.51.100.3."])
    isp, r1, d1, d2, s1, s2 = (580, 140), (580, 280), (330, 420), (830, 420), (330, 580), (830, 580)
    c.cable(isp[0], isp[1] + 26, r1[0], r1[1] - 30, "copper", None, "G0/0/1", "198.51.100.0/29")
    c.cable(r1[0] - 34, r1[1] + 16, d1[0] + 40, d1[1] - 26, "copper", "G0/0/0", "Gi1/0/24", "10.0.0.0/30")
    bundle(c, (d1[0] + 44, d1[1] - 6), (d2[0] - 44, d2[1] - 6), gap=14, color=PURPLE[0])
    c.line(d1[0] + 44, d1[1] + 18, d2[0] - 44, d2[1] + 18, "#64748b", 3)
    c.link_label(580, 378, "Po3 L3 · 10.0.0.4/30", color=PURPLE[0], weight=700)
    c.link_label(580, 438, "Gi1/0/23 trunk", color=MUTED)
    bundle(c, (d1[0], d1[1] + 34), (s1[0], s1[1] - 22), gap=14, color=BLUE[0])
    bundle(c, (d2[0], d2[1] + 34), (s2[0], s2[1] - 22), gap=14, color=BLUE[0])
    c.line(d2[0] - 30, d2[1] + 30, s1[0] + 40, s1[1] - 18, "#94a3b8", 2, dash="8 6")
    c.line(d1[0] + 30, d1[1] + 30, s2[0] - 40, s2[1] - 18, "#94a3b8", 2, dash="8 6")
    c.device("cloud", *isp, "ISP", ["DHCP to R1 · Lo0 192.0.2.8"], label="right")
    c.device("router", *r1, "R1", ["DHCP server · PAT + static NAT", "SNMP agent · syslog → NMS1"], label="right")
    c.device("l3switch", *d1, "DSW1", ["HSRP active 10/30 · SVIs .2", "DHCP relay · WIRELESS-IN · AAA"], label="left")
    c.device("l3switch", *d2, "DSW2", ["HSRP active 40/99 · SVIs .3", "DHCP relay · WIRELESS-IN"], label="right")
    c.device("switch", *s1, "SW1", ["snooping · DAI · port-security"], label="left")
    c.device("switch", *s2, "SW2", ["snooping · DAI · port-security"], label="right")
    h1 = [(150, "pc", "PC1", "V10"), (230, "pc", "PC2", "V30"), (310, "server", "AAA-1", "V99"), (390, "server", "DNS1", "V99")]
    h2 = [(690, "pc", "PC3", "V10"), (770, "printer", "Printer1", "V40"), (850, "server", "FILES", "V99"), (930, "server", "WEB1", "V40"), (1010, "controller", "NMS1", "V99")]
    for hs, s in ((h1, s1), (h2, s2)):
        for x, k, n, v in hs:
            c.line(s[0] + (x - s[0]) * 0.15, s[1] + 22, x, 650, "#94a3b8", 1.8)
            c.device(k, x, 676, None, s=0.5)
            c.text(x, 712, n, 11.5, INK, 700, "middle")
            c.text(x, 727, v, 10.5, MUTED, 600, "middle")
    return c

"""Reading extras for the study site: callouts, memory tricks, terminal-style CLI blocks and chapter quizzes."""

import html
import re

import markdown

# --------------------------------------------------------------------------- memory tricks
# Keyed by the section number at the start of an H3; the trick is placed at the end of that section.
MEMORY = {
    "1A.3": "Now bottom-up, layers 1 → 7: <b>P</b>lease <b>D</b>o <b>N</b>ot <b>T</b>hrow <b>S</b>ausage <b>P</b>izza <b>A</b>way — "
            "Physical, Data link, Network, Transport, Session, Presentation, Application.",
    "1A.4": "PDU names from Layer 4 down: <b>S</b>ome <b>P</b>eople <b>F</b>ear <b>B</b>irthdays — Segment, Packet, Frame, Bits.",
    "1B.4": "Sort devices into two teams: <b>PCs and routers</b> (MDI) and <b>switches and hubs</b> (MDI-X). Same team → <b>crossover</b>; "
            "different teams → <b>straight-through</b>. The rollover cable is only for the console port.",
    "1B.7": "Read <code>status / protocol</code> as <b>Layer 1 / Layer 2</b>: up/up is healthy, down/down is physical, up/down is a "
            "Layer 2 mismatch, and <i>administratively down</i> means someone typed <code>shutdown</code>.",
    "2.6": "<b>Magic number = 256 − the interesting octet of the mask.</b> Subnets start at multiples of it; the broadcast is the next "
           "subnet minus one. Drill it until it is automatic in the <a href=\"practice.html\">subnetting practice game</a>.",
    "3.5": "Read the first hex digits: <b>2 or 3</b> → global unicast (2000::/3) · <b>FC / FD</b> → unique local · <b>FE80</b> → "
           "link-local · <b>FF</b> → multicast.",
    "3.6": "EUI-64 in three moves: <b>Split, Stuff, Flip</b> — split the MAC in half, stuff <code>FFFE</code> in the middle, flip the "
           "7th bit of the first byte.",
    "4.4": "Type <b>1</b> sits <b>1st</b> on the metal (bare-metal). Type <b>2</b> is the <b>2nd</b> layer up — it runs on top of a host OS.",
    "5.5": "<b>Native = naked.</b> Frames in the native VLAN cross an 802.1Q trunk untagged; every other VLAN wears a 4-byte tag.",
    "6.5": "LACP: <b>A</b>ctive <b>a</b>sks, <b>P</b>assive <b>p</b>auses. PAgP: <b>D</b>esirable asks, <b>A</b>uto waits. Two that only "
           "wait (passive + passive, auto + auto) never form a channel.",
    "7.4": "PoE standards go alphabetically up in power: <b>af</b> (PoE, 15.4 W) → <b>at</b> (PoE+, 30 W) → <b>bt</b> (PoE++, 60 W and up).",
    "8.4": "<b>C</b>DP is <b>C</b>isco's own; <b>LLDP</b> is the open IEEE 802.1AB version every vendor speaks. Default timers: CDP 60 s / "
           "180 s hold, LLDP 30 s / 120 s hold.",
    "9.6": "Every STP tie-break is <b>lowest wins</b>: bridge ID → root path cost → sender bridge ID → sender port ID. Elect the "
           "<b>root bridge</b>, then a <b>root port</b> per switch, then a <b>designated port</b> per link — everything left blocks.",
    "9.8": "RSTP has only three states — <b>D</b>iscarding, <b>L</b>earning, <b>F</b>orwarding. Discarding absorbs the old blocking, "
           "listening and disabled states.",
    "10.6": "Administrative distances to know cold: <b>connected 0 · static 1 · eBGP 20 · EIGRP 90 · OSPF 110 · RIP 120 · iBGP 200</b>. "
            "Lower is more trusted.",
    "11.7": "A floating static route <b>floats above</b> the primary because its AD is set higher (for example 130, above OSPF's 110). "
            "It <b>sinks into</b> the routing table only when the primary route disappears.",
    "12.4": "OSPF neighbor states in order: <b>D</b>id <b>I</b> <b>2</b> <b>E</b>ver <b>E</b>xpect <b>L</b>oving <b>F</b>riends? — "
            "Down, Init, 2-Way, ExStart, Exchange, Loading, Full.",
    "12.5": "Router ID order of preference: <b>M</b>anual <code>router-id</code> → highest <b>L</b>oopback IP → highest active "
            "<b>I</b>nterface IP. Think <b>M-L-I</b>.",
    "13.5": "<b>GLBP</b> is the only FHRP with <i>balancing</i> in its name — and the only one that load-balances across routers by "
            "default. HSRP and GLBP are Cisco; VRRP is the open standard.",
    "14.3": "<b>DORA</b>: Discover, Offer, Request, Acknowledge. Client on UDP 68, server on UDP 67.",
    "16.3": "The only non-overlapping 2.4 GHz channels: <b>1, 6 and 11</b>.",
    "18.5": "<b>TACACS+</b>: TCP 49, encrypts the whole body, keeps the three A's separate — ideal for device administration. "
            "<b>RADIUS</b>: UDP 1812/1813, encrypts only the password, combines authentication and authorization — ideal for network access.",
    "19.3": "<b>T</b>FTP is <b>T</b>rivial: no login, no encryption (UDP 69). For anything that matters, use SCP or SFTP over SSH (TCP 22).",
    "20.3": "<b>Wildcard = 255.255.255.255 − mask.</b> In a wildcard, <b>0 = must match</b> and <b>1 = don't care</b> — the opposite of a subnet mask.",
    "20.6": "<b>S</b>tandard ACLs go near the <b>D</b>estination; <b>E</b>xtended ACLs go near the <b>S</b>ource. "
            "Standard–Destination, Extended–Source.",
    "21.2": "<b>Inside / outside</b> tells you <i>where the host is</i>; <b>local / global</b> tells you <i>where the address is seen</i>. "
            "Inside local = your PC's private address; inside global = the public address the internet sees for it.",
    "22.3": "<b>AAAA</b> has four times the letters of <b>A</b> because IPv6 addresses have four times the bits (128 vs 32). "
            "CNAME = a nickname, MX = mail, PTR = points back from IP to name, NS = who answers for the zone.",
    "23.3": "<b>Trust the path to the real DHCP server</b> — uplinks toward it are trusted, every user port stays untrusted.",
    "23.7": "Port-security violation modes get stricter in alphabetical order: <b>P</b>rotect (drop silently) → <b>R</b>estrict "
            "(drop, log and count) → <b>S</b>hutdown (err-disable — the default).",
    "24.3": "<b>AH</b> only <b>A</b>uthenticates; <b>ESP</b> <b>E</b>ncrypts <i>and</i> authenticates. ESP is IP protocol 50, AH is 51.",
    "25.3": "Syslog severities 0 → 7: <b>E</b>very <b>A</b>wesome <b>C</b>isco <b>E</b>ngineer <b>W</b>ill <b>N</b>eed <b>I</b>ce-cream "
            "<b>D</b>aily — Emergency, Alert, Critical, Error, Warning, Notification, Informational, Debugging. Lower number = worse news.",
    "25.6": "SNMP: the manager <b>polls on UDP 161</b>; agents <b>send traps to UDP 162</b>. Only SNMPv3 adds authentication and encryption.",
    "26.5": "Ansible in three words: <b>agentless, push, YAML</b> — it connects over SSH, pushes the change, and the playbook is YAML.",
    "27.5": "Treat AI output like a config from a brand-new colleague: <b>check the evidence, check the scope, test in a lab</b> — then apply.",
}

CALLOUTS = {   # label in the guide -> (css class, shown label)
    "Exam tip": ("exam-tip", "Exam tip"), "Exam habit": ("exam-tip", "Exam habit"),
    "Common trap": ("trap", "Common trap"), "Common traps": ("trap", "Common traps"), "Trap": ("trap", "Trap"),
    "The trap": ("trap", "The trap"), "Common mistakes": ("trap", "Common mistakes"),
    "Security note": ("security-note", "Security note"), "Best practice": ("best-practice", "Best practice"),
    "PT note": ("lab-it", "PT note"), "PT notes": ("lab-it", "PT notes"),
    "Packet Tracer limitation": ("lab-it", "Packet Tracer limitation"),
}


def add_memory_tricks(md, n):
    for key, text in MEMORY.items():
        if int(re.match(r"\d+", key).group()) != n:
            continue
        m = re.search(rf"^### {re.escape(key)} .*$", md, re.M)
        if not m:
            raise SystemExit(f"memory trick anchor not found: {key}")
        nxt = re.search(r"^#{2,3} ", md[m.end():], re.M)
        at = m.end() + nxt.start() if nxt else len(md)
        block = f'\n<p class="callout memory-trick"><strong>Memory trick</strong>{text}</p>\n\n'
        md = md[:at].rstrip() + "\n\n" + block + md[at:]
    return md


def callouts(h):
    labels = "|".join(sorted(map(re.escape, CALLOUTS), key=len, reverse=True))
    def rep(m):
        cls, shown = CALLOUTS[m.group(1)]
        return f'<p class="callout {cls}"><strong>{shown}</strong>'
    h = re.sub(rf"<p><strong>({labels})[:.]?</strong>[:.]?\s*", rep, h)
    h = re.sub(r"<p><strong>(Memory aid[^<]*?):?</strong>:?\s*",
               lambda m: f'<p class="callout memory-trick"><strong>{m.group(1)}</strong>', h)
    # sentence case after the label ("when the exam…" -> "When the exam…")
    return re.sub(r'(<p class="callout [^"]+"><strong>[^<]*</strong>)([a-z])', lambda m: m.group(1) + m.group(2).upper(), h)


def lab_it(h, n):
    """Add a 'Lab it' callout after the learning objectives, pointing to the chapter's first lab."""
    m = re.search(r'<h([34]) id="([^"]+)">((?:(?!</h\1>).)*?\bLab (\d+\.\d+)(?:(?!</h\1>).)*)</h\1>', h, re.S)
    if not m:
        return h
    name = re.sub(r"<[^>]+>", "", m.group(3)).strip()
    name = re.sub(r"^[\dA-Z.]+\s+(?=Packet Tracer|Lab|Hands-on)", "", name)
    box = (f'<p class="callout lab-it"><strong>Lab it</strong>This chapter is hands-on. Once the theory clicks, jump to '
           f'<a href="#{m.group(2)}">{html.escape(html.unescape(name))}</a> and build it yourself — reading about a '
           f'network is good, breaking and fixing one is better.</p>')
    heads = [x.start() for x in re.finditer(r'<h3 id=', h)]
    at = heads[1] if len(heads) > 1 else 0
    return h[:at] + box + h[at:]


# --------------------------------------------------------------------------- terminal blocks
PROMPT = re.compile(r"^([A-Za-z][\w.-]{0,30}(?:\([\w-]+\))?[#>]|C:\\[^>]*>|\$)(\s?)(.*)$")


def _term_line(line):
    m = PROMPT.match(line)
    if m:
        cmd = m.group(3)
        c, _, cm = cmd.partition("  !") if "  !" in cmd else (cmd, "", "")
        out = f'<span class="tp">{html.escape(m.group(1))}</span>{m.group(2)}<span class="tc">{html.escape(c)}</span>'
        if cm or _:
            out += f'<span class="tm">  !{html.escape(cm)}</span>'
        return out, cmd.split("  !")[0].rstrip()
    if line.lstrip().startswith("!"):
        return f'<span class="tm">{html.escape(line)}</span>', None
    return html.escape(line), None


def terminals(h):
    def rep(m):
        cls, body = m.group(1) or "", html.unescape(m.group(2))
        lines = body.rstrip("\n").split("\n")
        prompts = [PROMPT.match(l) for l in lines]
        hosts = [p.group(1) for p in prompts if p and not p.group(1).startswith(("C:", "$"))]
        copy_btn = '<button class="copy" type="button" aria-label="Copy">Copy</button>'
        if not any(prompts):
            return f'<div class="codebox">{copy_btn}<pre><code{cls}>{m.group(2)}</code></pre></div>'
        rendered, cmds = [], []
        for l in lines:
            r, c = _term_line(l)
            rendered.append(r)
            if c is not None and c:
                cmds.append(c)
        host = re.sub(r"[#>(].*", "", hosts[0]) if hosts else "terminal"
        data = html.escape("\n".join(cmds), quote=True)
        return (f'<div class="term"><div class="term-bar"><i></i><i></i><i></i><span>{html.escape(host)}</span>'
                f'<button class="copy" type="button" data-copy="{data}" title="Copy the commands only (prompts and output removed)">Copy commands</button></div>'
                f'<pre><code>{chr(10).join(rendered)}</code></pre></div>')
    return re.sub(r"<pre><code( class=\"[^\"]*\")?>(.*?)</code></pre>", rep, h, flags=re.S)


# --------------------------------------------------------------------------- quizzes
Q_HEAD = re.compile(r"^### ([^\n]*(?:Practice questions|revision questions)[^\n]*)\n", re.M)
A_HEAD = re.compile(r"^### [^\n]*Answer key[^\n]*\n", re.M)
QSTART = re.compile(r"^\*\*(\d+)\.\s*(?:\(([^)]*)\))?\*\*\s*", re.M)
_MD = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])


def _md(text, inline=False):
    _MD.reset()
    out = _MD.convert(text)
    if inline:
        out = re.sub(r"^<p>(.*)</p>$", r"\1", out.strip(), flags=re.S)
    return out


def _split_options(block):
    lines = block.rstrip().split("\n")
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("A. "):
            optline = " ".join(l.strip() for l in lines[i:] if l.strip())
            parts = re.split(r"(?:^|\s{2,})([A-F])\.\s+", optline)
            opts = [(parts[j], parts[j + 1].strip()) for j in range(1, len(parts) - 1, 2)]
            if [o[0] for o in opts] == [chr(65 + k) for k in range(len(opts))] and len(opts) >= 2:
                return "\n".join(lines[:i]).rstrip(), opts
            break
    return block, []


def _answers(text):
    return {int(m.group(1)): m.group(2).strip()
            for m in re.finditer(r"^(\d+)\.\s+(.*?)(?=^\d+\.\s|\Z)", text, re.M | re.S)}


def _letters(a):
    m = re.match(r"\*\*([A-F](?:(?:\s*,\s*and\s+|\s*,\s*|\s+and\s+)[A-F])*)\.?\*\*", a)
    return re.findall(r"[A-F]", m.group(1)) if m else None


def extract_quiz(md):
    """Cut the practice questions + answer key out of a chapter. Returns (md_with_placeholder, quiz dict or None)."""
    qm, am = Q_HEAD.search(md), A_HEAD.search(md)
    if not qm or not am or am.start() < qm.start():
        return md, None
    nxt = re.search(r"^#{2,3} ", md[am.end():], re.M)
    a_end = am.end() + (nxt.start() if nxt else len(md) - am.end())
    qtext, answers = md[qm.end():am.start()], _answers(md[am.end():a_end])
    starts = list(QSTART.finditer(qtext))
    qs = []
    for i, s in enumerate(starts):
        body = qtext[s.end(): starts[i + 1].start() if i + 1 < len(starts) else len(qtext)].strip()
        n, kind = int(s.group(1)), (s.group(2) or "").strip()
        stem, opts = _split_options(body)
        a = answers.get(n, "")
        letters = _letters(a) if opts else None
        if not opts or not letters or any(l not in [o[0] for o in opts] for l in letters):
            stem, opts, letters = body, [], []
        qs.append({"n": n, "kind": kind, "stem": stem, "opts": opts, "correct": letters, "answer": a})
    quiz = {"title": qm.group(1), "pre": qtext[:starts[0].start()].strip() if starts else "", "qs": qs}
    placeholder = f"### {qm.group(1)}\n\n<div>QUIZ-PLACEHOLDER</div>\n\n"
    return md[:qm.start()] + placeholder + md[a_end:], quiz


def quiz_html(n, quiz):
    qs = quiz["qs"]
    graded = sum(1 for q in qs if q["opts"])
    rows = []
    for q in qs:
        kind = html.escape(q["kind"] or "Question")
        stem = _md(q["stem"])
        expl = _md(q["answer"])
        if q["opts"]:
            k = len(q["correct"])
            opts = "".join(f'<button class="opt" type="button" data-l="{l}"><span class="ol">{l}</span>'
                           f'<span class="ot">{_md(t, inline=True)}</span></button>' for l, t in q["opts"])
            multi = (f'<div class="qact"><span class="qhint">Choose {k}</span>'
                     f'<button class="btn small qcheck" type="button" disabled>Check answer</button></div>') if k > 1 else ""
            rows.append(f'<div class="q" data-q="{q["n"]}" data-correct="{"".join(q["correct"])}">'
                        f'<div class="qhead"><span class="qn">{q["n"]}</span><span class="qkind">{kind}</span><span class="qtag">auto-graded</span></div>'
                        f'<div class="qstem">{stem}</div><div class="opts">{opts}</div>{multi}'
                        f'<div class="qans" hidden><div class="qverdict"></div>{expl}</div></div>')
        else:
            rows.append(f'<div class="q open" data-q="{q["n"]}">'
                        f'<div class="qhead"><span class="qn">{q["n"]}</span><span class="qkind">{kind}</span><span class="qtag">think, then reveal</span></div>'
                        f'<div class="qstem">{stem}</div>'
                        f'<div class="qact"><button class="btn small qreveal" type="button">Show answer</button>'
                        f'<span class="qhint">Answer it in your head (or on paper) first.</span></div>'
                        f'<div class="qans" hidden><div class="qverdict"></div>{expl}'
                        f'<div class="selfmark"><span>Did you get it?</span><button class="btn small ok" type="button" data-m="1">✓ Got it</button>'
                        f'<button class="btn small no" type="button" data-m="0">✗ Not yet</button></div></div></div>')
    pre = f'<div class="qpre">{_md(quiz["pre"])}</div>' if quiz["pre"] else ""
    return (f'<section class="quiz" data-ch="{n}" data-total="{len(qs)}">'
            f'<div class="quiz-top"><div class="quiz-title"><span class="qicon">📝</span><div><b>Self-check quiz</b>'
            f'<small>{len(qs)} questions · {graded} auto-graded, {len(qs) - graded} to reveal and self-mark · your score is saved in this browser</small></div></div>'
            f'<div class="quiz-score"><span class="qs-num">0 / {len(qs)}</span><div class="bar"><i></i></div><span class="qs-sub">not started</span></div>'
            f'<button class="btn small qreset" type="button">Reset</button></div>'
            f'{pre}{"".join(rows)}'
            f'<div class="quiz-done" hidden></div></section>')

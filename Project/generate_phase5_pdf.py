"""
Generates the Phase 5 PDF — Networking explained from scratch.
Covers: why TCP, the CGNAT problem, the relay server, ngrok,
the phone-number-as-label scheme, and the connection to audio + encryption.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase5_Networking_Explained.pdf"

styles = getSampleStyleSheet()

title_style = ParagraphStyle('TitleBig', parent=styles['Title'],
    fontSize=20, leading=26, alignment=TA_CENTER,
    textColor=colors.HexColor('#0B3D91'), spaceAfter=10)

subtitle_style = ParagraphStyle('SubTitle', parent=styles['Normal'],
    fontSize=13, leading=17, alignment=TA_CENTER,
    textColor=colors.HexColor('#444444'), spaceAfter=20)

h1 = ParagraphStyle('H1', parent=styles['Heading1'],
    fontSize=16, leading=20, spaceBefore=16, spaceAfter=10,
    textColor=colors.HexColor('#0B3D91'))

h2 = ParagraphStyle('H2', parent=styles['Heading2'],
    fontSize=12, leading=16, spaceBefore=10, spaceAfter=5,
    textColor=colors.HexColor('#1F4E79'))

h3 = ParagraphStyle('H3', parent=styles['Heading3'],
    fontSize=11, leading=14, spaceBefore=8, spaceAfter=4,
    textColor=colors.HexColor('#2E75B6'))

body = ParagraphStyle('Body', parent=styles['Normal'],
    fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)

bullet = ParagraphStyle('Bullet', parent=body,
    leftIndent=14, bulletIndent=4, spaceAfter=3)

success_style = ParagraphStyle('Success', parent=body,
    fontSize=10, leading=14,
    textColor=colors.HexColor('#1B7A3F'),
    backColor=colors.HexColor('#E8F5EC'),
    borderColor=colors.HexColor('#1B7A3F'),
    borderWidth=0.5, borderPadding=6,
    spaceBefore=4, spaceAfter=8)

note_style = ParagraphStyle('Note', parent=body,
    fontSize=9, leading=12,
    textColor=colors.HexColor('#666666'),
    leftIndent=10, spaceAfter=6)

code_style = ParagraphStyle('Code', parent=styles['Code'],
    fontName='Courier', fontSize=8, leading=10,
    leftIndent=6, rightIndent=4,
    backColor=colors.HexColor('#F4F4F4'),
    borderColor=colors.HexColor('#CCCCCC'),
    borderWidth=0.5, borderPadding=4,
    spaceBefore=4, spaceAfter=8)

ascii_style = ParagraphStyle('Ascii', parent=styles['Code'],
    fontName='Courier', fontSize=8, leading=10,
    leftIndent=4, rightIndent=4,
    spaceBefore=4, spaceAfter=8)

cell_style = ParagraphStyle('CellBody', parent=styles['Normal'],
    fontName='Helvetica', fontSize=8.5, leading=11,
    spaceBefore=0, spaceAfter=0, alignment=0)

cell_header_style = ParagraphStyle('CellHeader', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=9, leading=11,
    textColor=colors.white,
    spaceBefore=0, spaceAfter=0, alignment=0)


def P(t, s=body):
    return Paragraph(t, s)


def code(t):
    return Preformatted(t, code_style)


def ascii_block(t):
    return Preformatted(t, ascii_style)


def wrap_cell(value, header_row=False):
    if isinstance(value, Paragraph):
        return value
    if value is None:
        value = ''
    text = str(value)
    return Paragraph(text, cell_header_style if header_row else cell_style)


def make_table(data, col_widths=None, header=True):
    wrapped = []
    for r, row in enumerate(data):
        is_header = (header and r == 0)
        wrapped.append([wrap_cell(c, is_header) for c in row])
    t = Table(wrapped, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#888888')),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    if header:
        cmds += [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B3D91'))]
    t.setStyle(TableStyle(cmds))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm,
                      "Secure Voice Project | Phase 5 — Networking Explained")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

# ======== Title ========
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 5<br/>Networking Explained", title_style))
story.append(P("From scratch: TCP, NAT, the relay server, ngrok, and how it all fits with audio + encryption",
               subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P("This document explains <b>why we need a relay server</b>, <b>what TCP is</b>, "
               "<b>why ngrok</b>, and <b>how phone numbers work</b> in this project — all from "
               "first principles, no networking background assumed. It also documents what was "
               "built in Phase 5.1 / 5.2 / 5.3, and what comes next.",
               body))
story.append(Spacer(1, 0.5 * cm))
story.append(P("<b>STATUS at end of Phase 5.3 (2026-04-28):</b> Vodafone LTE modem successfully "
               "registers with relay.py through ngrok over 4G. Path verified end-to-end manually "
               "via Arduino Serial Monitor. Phase 5.4 (STM32 takes over from manual typing) is "
               "the next sub-task.", success_style))
story.append(PageBreak())

# ======== 1 — Big picture ========
story.append(P("1. The Big Picture", h1))

story.append(P("The whole project goal is two devices that exchange encrypted voice over LTE. "
               "Each device has a microphone, a speaker, an STM32 (which captures, encrypts, "
               "decrypts, and plays back audio), and an LTE modem (which moves bytes between "
               "devices over the cellular network).",
               body))

story.append(ascii_block(r"""
   Person A speaks                                          Person B hears
        |                                                        ^
        v                                                        |
   Device A  ------ encrypted audio over the internet -------  Device B
   (Karim's house)                                             (friend's house)
""".strip()))

story.append(P("The challenge: <b>how do the two devices find each other and exchange bytes "
               "over the internet?</b>", body))

# ======== 2 — Networking problem ========
story.append(P("2. The Networking Problem", h1))

story.append(P("On the internet, every machine has an <b>IP address</b> — a numeric label like "
               "<code>8.8.8.8</code> or <code>192.168.1.5</code>. To send data to a machine, you "
               "specify its IP address.", body))

story.append(P("That sounds simple. But cellular networks have a problem.", body))

story.append(P("2.1 — IP addresses are scarce", h2))
story.append(P("There are only ~4 billion IPv4 addresses in the world, but there are billions "
               "of phones, computers, IoT devices. There aren't enough public addresses to give "
               "each phone its own.", body))

story.append(P("2.2 — Carriers use CGNAT", h2))
story.append(P("Carriers like Vodafone solve this with <b>Carrier-Grade NAT</b> (CGNAT). Many "
               "subscribers share a small pool of public IPs. Each phone gets a <b>private IP</b> "
               "(like <code>10.244.223.181</code>) that's only valid inside Vodafone's network.", body))

story.append(ascii_block(r"""
   Public internet           Vodafone CGNAT             Your modem
   (real public IPs)         (translation gate)         (private IP)

   Anyone can reach a        Hides millions of          10.244.223.181
   public IP                 phones behind a few         (only Vodafone's
                             public IPs                   internal routers
                                                          can find this)
""".strip()))

story.append(P("2.3 — What this means in practice", h2))
story.append(P("Your modem can <b>call out</b> to public servers (Google, YouTube, etc.) — that "
               "works fine. But <b>nothing on the public internet can call IN to your modem</b>, "
               "because your modem has no public address.<br/><br/>"
               "Your friend's modem has the exact same problem.<br/><br/>"
               "<b>Therefore:</b> the two modems cannot connect directly to each other. Both can "
               "go OUT, neither can be reached from the OUTSIDE.", body))

story.append(P("This isn't a Vodafone bug — every consumer cellular carrier in the world does "
               "this. Your home Wi-Fi router does the same thing for your laptop and phone. "
               "It's how the internet is run today.", body))

# ======== 3 — Solution ========
story.append(P("3. The Solution — A Relay Server in the Middle", h1))

story.append(P("Both modems can call OUT. So we put a server in the middle that has a public IP, "
               "and have both modems call it. The server then forwards messages between them.",
               body))

story.append(ascii_block(r"""
   Modem A  --- calls out --->  RELAY SERVER  <--- calls out --- Modem B
   (private IP)                 (PUBLIC IP)                      (private IP)
                                     |
                                     v
                           Forwards bytes between
                           registered devices
""".strip()))

story.append(P("The relay is just a small Python program (<code>relay.py</code>) that:"))
points = [
    "Accepts TCP connections from devices.",
    "Remembers each device's phone number (used as a label, not as actual cellular calling).",
    "When device A says &quot;CALL B&quot;, the relay finds B's connection and starts forwarding bytes.",
    "Doesn't read the bytes &mdash; just shovels them between A and B (preserves end-to-end encryption).",
]
for p in points:
    story.append(P("&bull; " + p, bullet))

story.append(P("This is exactly how WhatsApp, Signal, FaceTime, Zoom, and every modern voice/video "
               "app works. The marketing makes them sound peer-to-peer but they all run massive "
               "server infrastructures because direct device-to-device just doesn't work on "
               "consumer networks.", body))

story.append(PageBreak())

# ======== 4 — TCP ========
story.append(P("4. What is TCP?", h1))

story.append(P("TCP (Transmission Control Protocol) is the simplest possible thing two computers "
               "can do over the internet: <b>open a reliable byte-stream channel between them.</b>",
               body))

story.append(P("Think of it like a phone call:", body))
points = [
    "<b>Dial</b> — one side asks to connect to the other (TCP &laquo;handshake&raquo;).",
    "<b>Pickup</b> — the other side accepts.",
    "<b>Talk</b> — both sides can send bytes back and forth, in order, and nothing gets lost.",
    "<b>Hang up</b> — either side closes the connection.",
]
for p in points:
    story.append(P("&bull; " + p, bullet))

story.append(P("That's it. TCP doesn't care what the bytes mean &mdash; it just delivers them "
               "reliably, in order, with no duplicates, no gaps. Your application (our relay, "
               "your modem firmware) decides what those bytes mean.",
               body))

story.append(P("4.1 — TCP from the modem's side", h2))
story.append(P("The A7608 modem speaks TCP via these AT commands:"))
tcp_cmds = [
    ['Command', 'TCP equivalent'],
    ['AT+NETOPEN', 'Activate the IP/TCP stack inside the modem'],
    ['AT+CIPOPEN=0,"TCP","host",port', 'Dial — open a connection to host:port (link 0)'],
    ['AT+CIPSEND=0,N', 'Prepare to send N bytes on link 0'],
    ['(then type N bytes)', 'Talk — send the bytes'],
    ['+IPD N then bytes', 'Talk — receive N bytes from the other side'],
    ['AT+CIPCLOSE=0', 'Hang up link 0'],
]
story.append(make_table(tcp_cmds, col_widths=[5.5 * cm, 9 * cm]))

story.append(P("4.2 — Why TCP and not something else?", h2))
story.append(P("Two reasons we picked raw TCP for this project (instead of HTTP, MQTT, etc.):"))
points = [
    "<b>It's the simplest layer.</b> TCP is built into every operating system and every modem firmware. No protocol library needed.",
    "<b>It gives us total control.</b> Our relay server can define any custom protocol on top &mdash; we used a simple line-based ASCII protocol with commands like REG, CALL, ANS, GO, HUP.",
    "<b>It's efficient for streaming.</b> For continuous audio bytes during a call, raw TCP has the lowest overhead.",
]
for p in points:
    story.append(P("&bull; " + p, bullet))

# ======== 5 — ngrok ========
story.append(P("5. Why ngrok?", h1))

story.append(P("There's still one missing piece: your relay (<code>relay.py</code>) runs on your "
               "laptop. <b>Your laptop is also behind your home router's NAT</b>. So your laptop "
               "doesn't have a public address either &mdash; the same problem as the modems.",
               body))

story.append(P("ngrok is a service that gives you a temporary public address that forwards to "
               "your laptop:", body))

story.append(ascii_block(r"""
   Modem  ----- TCP ---->  ngrok server  <---- TCP ---- Your laptop
                          (HAS public IP)               (relay.py)
                                |                            ^
                                |                            |
                                +----- forwards bytes -------+
""".strip()))

story.append(P("So when you run <code>ngrok tcp 5555</code>, ngrok says: &laquo;OK, I have given "
               "you the public address <code>2.tcp.eu.ngrok.io:23515</code>. Anyone who connects "
               "there will be forwarded to your laptop's port 5555.&raquo; That's where "
               "<code>relay.py</code> is listening.", body))

story.append(P("The full path is:"))
story.append(ascii_block(r"""
   Modem  ---->  Vodafone 4G  ---->  ngrok server  ---->  Your laptop  ---->  relay.py
                                    (public IP/port)        (port 5555)
""".strip()))

story.append(P("ngrok is for development only. In a real product (or for the final demo if you "
               "want maximum reliability), you'd skip ngrok and run <code>relay.py</code> "
               "directly on a small public server (like a $4/month DigitalOcean droplet). The "
               "modem would connect to the droplet's public IP directly.", note_style))

story.append(PageBreak())

# ======== 6 — Phone numbers ========
story.append(P("6. How &laquo;Calling by Phone Number&raquo; Works", h1))

story.append(P("This was the question Karim asked early in the project. The answer: <b>phone "
               "numbers are just labels stored on the relay server</b>, NOT actual cellular voice "
               "calls.", body))

story.append(P("The relay maintains a table:"))
story.append(make_table([
    ['Phone number', 'TCP socket'],
    ['01000000001', "Device A's TCP connection"],
    ['01000000002', "Device B's TCP connection"],
], col_widths=[5 * cm, 9.5 * cm]))

story.append(P("When both devices register with their phone numbers, the relay knows which "
               "socket goes to which device. From then on, any device can &laquo;call&raquo; "
               "another by phone number.", body))

story.append(P("6.1 — The call flow", h2))
flow = [
    ['Step', 'Sender', 'Sends', 'What happens'],
    ['1', 'Device A', 'REG 01000000001', 'A registers its number'],
    ['2', 'Relay → A', 'OK', 'Confirmed'],
    ['3', 'Device B', 'REG 01000000002', 'B registers its number'],
    ['4', 'Relay → B', 'OK', 'Confirmed'],
    ['5', 'Device A', 'CALL 01000000002', "A wants to call B"],
    ['6', 'Relay → A', 'RING', "A: peer is ringing"],
    ['7', 'Relay → B', 'INC 01000000001', "B: A is calling you"],
    ['8', 'Device B', 'ANS', "B accepts"],
    ['9', 'Relay → A', 'GO', "Talk now"],
    ['10', 'Relay → B', 'GO', "Talk now"],
    ['11', 'Both', 'audio bytes', "Encrypted audio flows freely both ways"],
    ['12', 'Either', 'HUP', "Hang up"],
    ['13', 'Relay → other', 'PEER_HUP', "Peer hung up"],
]
story.append(make_table(flow, col_widths=[1 * cm, 2.5 * cm, 4 * cm, 7 * cm]))

story.append(P("6.2 — Why not use real cellular voice calls?", h2))
story.append(P("The A7608 modem can make real voice calls with <code>ATD&lt;number&gt;;</code>. "
               "But that conflicts with the project's encryption goal:",
               body))
story.append(ascii_block(r"""
   Real voice call:
       Mic ---> LTE modem PCM bus ---> Cellular voice channel ---> Speaker
                                          |
                                          v
                                   STM32 NEVER sees the audio
                                          |
                                          v
                                   No encryption possible

   This project (data + relay):
       Mic ---> STM32 ADC ---> RSA + AES encrypt ---> LTE modem TCP send
                                                              |
                                                              v
                                                    Encrypted bytes over LTE
                                                              |
                                                              v
                                                    Other STM32 decrypts
                                                              |
                                                              v
                                                              Speaker
""".strip()))

story.append(P("In the data path, every audio sample lives in the STM32's RAM at some point. "
               "That's what makes the encryption possible &mdash; the STM32 can transform the "
               "samples before they leave. Real voice calls bypass the STM32 entirely.", body))

story.append(PageBreak())

# ======== 7 — Phase 5 progress ========
story.append(P("7. Phase 5 Sub-tasks &mdash; What's Done", h1))

phase5 = [
    ['Sub-task', 'What', 'Status'],
    ['5.1', 'Run relay.py on laptop, listening on port 5555', '✓ Done'],
    ['5.2', 'Expose laptop port 5555 to public internet via ngrok TCP tunnel', '✓ Done'],
    ['5.3', 'Manually open TCP from LTE modem to ngrok address; send REG; relay confirms registration', '✓ Done — verified end-to-end on 2026-04-28'],
    ['5.4', 'STM32 takes over from manual Arduino Serial Monitor typing', 'NEXT'],
    ['5.5', 'Hardware: wire LTE module to STM32 USART1 (with ESP32 reprogrammed as bridge)', 'After 5.4'],
]
story.append(make_table(phase5, col_widths=[1.5 * cm, 8 * cm, 5 * cm]))

story.append(P("7.1 — Working AT command sequence (verified)", h2))
story.append(code('''AT
ATE0
AT+CPIN?           -> +CPIN: READY
AT+CSQ             -> +CSQ: 22,99   (signal >= 10 = good)
AT+CREG?           -> +CREG: 0,1    (registered home network)
AT+CGDCONT=1,"IP","internet.vodafone.net"
AT+CGACT=1,1
AT+NETOPEN         -> +NETOPEN: 0
AT+IPADDR          -> +IPADDR: 10.x.x.x
AT+CIPOPEN=0,"TCP","2.tcp.eu.ngrok.io",23515
                   -> +CIPOPEN: 0,0
AT+CIPSEND=0,17
                   -> > prompt
REG 01000000001<CR><LF>     (17 bytes total)
                   -> +CIPSEND: 0,17,17
                   -> +IPD 3
                   -> OK     (relay's reply travels back through ngrok)'''))

story.append(P("And on the relay terminal:"))
story.append(code('''+ conn ('127.0.0.1', xxxxx)
+ registered 01000000001'''))

# ======== 8 — Audio + encryption integration ========
story.append(P("8. How Phase 5 Connects to Audio + Encryption", h1))

story.append(P("Phase 5 is just the network plumbing. Once it works, the rest of the project "
               "fits on top:", body))

story.append(ascii_block(r"""
   Phase 3 (DONE):
       Mic -> MAX9814 -> STM32 ADC -> MCP4725 DAC -> LM386 -> Speaker

   Phase 5 (in progress):
       STM32 <----UART----> LTE modem  <-- 4G --> ngrok --> relay.py
       (transports any bytes both ways)

   Phase 7 (LATER):
       STM32 audio bytes ----encrypt----> bytes for Phase 5 transport
       Phase 5 transport <----decrypt---- STM32 audio bytes

   Putting it all together:

   Mic -> ADC -> ENCRYPT -> UART -> LTE -> 4G -> ngrok -> relay.py
                                                              |
                                                              v
                                                    other relay/socket
                                                              |
                                                              v
                                                    Other LTE -> Other UART
                                                              |
                                                              v
                                                    Other STM32 DECRYPT
                                                              |
                                                              v
                                                    DAC -> LM386 -> Speaker
""".strip()))

story.append(P("Phase 5 only delivers a generic byte pipe. The audio+encryption logic (Phases 6 "
               "and 7) decide what bytes get pushed in and what comes out.", body))

# ======== 9 — Phase 5.4 plan ========
story.append(P("9. Phase 5.4 &mdash; Putting STM32 in Charge", h1))

story.append(P("So far, the human (Karim, typing in Arduino Serial Monitor) is the brain. "
               "Phase 5.4 replaces the human typing with STM32 firmware.",
               body))

story.append(P("9.1 — The STM32 firmware approach", h2))
story.append(P("We <b>edit the existing MicDAC project</b> &mdash; do NOT start a new project. "
               "Reasons:", body))
points = [
    "MicDAC already has the audio path working (mic -> ADC -> DAC -> speaker, Phase 3).",
    "Phase 5.4 just <b>adds</b> LTE communication on top &mdash; doesn't replace anything.",
    "Starting a new project means redoing all the Phase 3 work, which would be wasteful.",
    "Audio code (TIM3 ISR, ADC DMA) keeps running in the background while LTE code drives the main loop.",
]
for p in points:
    story.append(P("&bull; " + p, bullet))

story.append(P("9.2 — What gets added to MicDAC", h2))
adds = [
    ['Item', 'Where', 'Purpose'],
    ['USART1 init (PA9 TX, PA10 RX)', 'CubeMX', 'Talk to LTE module (or to ESP32 bridge)'],
    ['UART RX buffer + IDLE interrupt', 'main.c, USART1 IRQ handler', 'Receive AT replies'],
    ['Function: send_at(cmd, expected, timeout)', 'main.c', 'Send an AT command and wait for response'],
    ['LTE bring-up state machine', 'main.c USER CODE 4', 'Run AT, ATE0, CPIN?, CSQ, CGDCONT, CGACT, NETOPEN, CIPOPEN automatically'],
    ['REG state machine', 'main.c USER CODE 4', 'Send REG <phone>, wait for OK, then idle'],
    ['Status LED logic', 'main.c WHILE loop', 'PC13 reflects LTE state (booting, registered, in-call)'],
]
story.append(make_table(adds, col_widths=[5 * cm, 4.5 * cm, 5 * cm]))

story.append(P("9.3 — Hardware swap", h2))
story.append(P("To put the STM32 in control of the LTE module, we need to either:"))
story.append(make_table([
    ['Option', 'How', 'Pros / Cons'],
    ['(a) Reprogram ESP32 as STM32 bridge', 'Modify ESP32 sketch: bridge between STM32 UART and modem UART (instead of bridging USB)', 'Easier — keeps the working power-on sequence in ESP32. STM32 just sees a UART that talks to the modem.'],
    ['(b) Bypass ESP32', 'Connect STM32 USART1 directly to the A7608 modem UART pins on the LilyGO board header', 'Cleaner — no ESP32 in the loop. Requires finding the A7608 UART pins on the specific LilyGO board.'],
], col_widths=[3.5 * cm, 6 * cm, 5 * cm]))

story.append(P("Option (a) recommended &mdash; the existing ESP32 sketch already powers on the "
               "modem reliably; we just change where it gets bytes from (UART instead of USB).", body))

story.append(PageBreak())

# ======== 10 — Concrete bytes table ========
story.append(P("10. Concrete &mdash; What Bytes Get Sent", h1))

story.append(P("During a full call, here is every byte that flows between Device A, the relay, "
               "and Device B. The bytes during &laquo;TALKING&raquo; are continuous; the rest "
               "are one-shot.", body))

bytes_flow = [
    ['Phase', 'Sender', 'Bytes', 'Length'],
    ['Setup', 'A → relay', 'REG 01000000001\\r\\n', '17'],
    ['Setup', 'relay → A', 'OK\\n', '3'],
    ['Setup', 'B → relay', 'REG 01000000002\\r\\n', '17'],
    ['Setup', 'relay → B', 'OK\\n', '3'],
    ['Call', 'A → relay', 'CALL 01000000002\\r\\n', '18'],
    ['Call', 'relay → A', 'RING\\n', '5'],
    ['Call', 'relay → B', 'INC 01000000001\\n', '16'],
    ['Answer', 'B → relay', 'ANS\\r\\n', '5'],
    ['Answer', 'relay → A', 'GO\\n', '3'],
    ['Answer', 'relay → B', 'GO\\n', '3'],
    ['Talking', 'A → relay → B', 'encrypted audio bytes (continuous)', 'variable'],
    ['Talking', 'B → relay → A', 'encrypted audio bytes (continuous)', 'variable'],
    ['Hangup', 'A or B → relay', 'HUP\\r\\n', '5'],
    ['Hangup', 'relay → other', 'PEER_HUP\\n', '9'],
]
story.append(make_table(bytes_flow, col_widths=[2.5 * cm, 3 * cm, 6.5 * cm, 2.5 * cm]))

story.append(P("During &laquo;Talking&raquo;, encrypted audio frames are pushed continuously. "
               "The exact frame size depends on the encryption design (Phase 7) but typically "
               "16–64 bytes per frame, ~125 frames per second at 8 kHz. Total bandwidth "
               "~10 KB/sec one-way (2 KB/sec for the encrypted overhead, 8 KB/sec for the audio "
               "samples).", body))

# ======== 11 — Summary ========
story.append(P("11. Summary &mdash; What's Now Possible", h1))
story.append(P("After Phase 5.3, this is the verified system:", body))
points = [
    "Two computer programs (relay.py + ngrok) running on the developer's laptop create a public TCP relay.",
    "Any device anywhere on the internet can connect to <code>2.tcp.eu.ngrok.io:NNNNN</code> (or whatever ngrok assigns).",
    "Once connected, devices register a phone number with the relay.",
    "Devices identified by phone number can later request to call each other (Phase 6).",
    "The cellular path Vodafone 4G ↔ ngrok ↔ laptop ↔ relay.py is verified end-to-end with the LTE modem.",
    "All steps so far were done by typing AT commands manually in Arduino Serial Monitor; Phase 5.4 replaces the human with STM32 firmware.",
]
for p in points:
    story.append(P("&bull; " + p, bullet))

story.append(P("Phase 5.4 next: STM32 firmware automates everything above so that on power-up, "
               "the device boots, brings up the LTE network, opens TCP to the relay, and "
               "registers its phone number &mdash; with no human intervention.", body))

story.append(Spacer(1, 0.5 * cm))
story.append(P("End of Phase 5 networking explanation.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 5 — Networking Explained",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")
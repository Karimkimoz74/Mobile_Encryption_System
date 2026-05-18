"""
Generates the Phase 4 PDF — LTE Module Manual AT-Command Bring-up.
Documents what was done, the bridge sketch, every AT command used,
the working sequence, and lessons learned.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase4_LTE_AT_Commands.pdf"

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

warn_style = ParagraphStyle('Warn', parent=body,
    fontSize=10, leading=14,
    textColor=colors.HexColor('#8A4500'),
    backColor=colors.HexColor('#FFF4E5'),
    borderColor=colors.HexColor('#E08810'),
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
                      "Secure Voice Project | Phase 4 — LTE AT Command Bring-up")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

# Title page
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 4<br/>LTE Module<br/>AT-Command Bring-up", title_style))
story.append(P("Manual cellular network connection &amp; TCP echo verification", subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P("<b>STATUS: COMPLETED on 2026-04-28.</b> The T-A7608 4G modem boots, attaches "
               "to Vodafone Egypt with excellent signal (CSQ 22/31), opens a TCP socket to "
               "tcpbin.com:4242 over 4G, and successfully sends/echoes data end-to-end.",
               success_style))
story.append(Spacer(1, 0.5 * cm))
story.append(P("This document covers what was built, every AT command used and what it means, "
               "the working sequence in order, and the lessons learned during debugging. "
               "Phase 4 is the foundation for Phase 5 (where the STM32 takes over from the PC "
               "and drives the LTE module automatically).", body))
story.append(PageBreak())

# ============== Section 1 — Goal ==============
story.append(P("1. Goal of Phase 4", h1))

story.append(P("Confirm that the T-A7608SA-H 4G LTE module can:", body))
goals = [
    "Power on, boot, and respond to basic AT commands.",
    "Detect the SIM card and read its status.",
    "Register on the Vodafone Egypt cellular network with adequate signal strength.",
    "Attach to the GPRS / packet data service.",
    "Open a TCP socket to a public internet server over 4G.",
    "Send bytes over that socket and receive an echo back.",
]
for g in goals:
    story.append(P("• " + g, bullet))

story.append(P("All of this is done <b>by typing AT commands manually</b> from the PC. The "
               "STM32 is NOT involved in Phase 4. We're just learning the modem's command set "
               "and verifying the network works before automating it in Phase 5.",
               body))

# ============== Section 2 — Hardware ==============
story.append(P("2. Hardware Architecture", h1))

story.append(P("2.1 LilyGO T-A7608 board internals", h2))
story.append(P("The user's LTE module is a LilyGO T-A7608 development board, which contains "
               "<b>two chips working together</b>:", body))
story.append(ascii_block(r"""
   PC                            LilyGO T-A7608 board
   ───                           ────────────────────
   USB-C   <----------> [USB-C bridge connector]
                               |
                               | USB
                               v
                        [ESP32 chip]
                        (runs Arduino bridge sketch)
                               |
                               | UART  (HardwareSerial 2,
                               |        pins 26 = TX, 27 = RX)
                               v
                        [SIMCom A7608SA-H modem chip]
                               |
                               | RF
                               v
                        [4G antenna]  ----- to cell tower
                               |
                        [SIM card slot]
""".strip()))

story.append(P("The ESP32 sits between the PC and the actual 4G modem. It handles the USB "
               "connection on one side and forwards bytes to/from the modem's UART on the "
               "other. Its job is just &laquo;translator&raquo; — it doesn't process the AT "
               "commands itself.", body))

story.append(P("2.2 ESP32 control pins for the modem", h2))
pins = [
    ['ESP32 GPIO', 'Modem signal', 'Purpose'],
    ['12', 'POWER_ON', 'Set HIGH to enable the 4G modem\'s power supply'],
    ['4', 'PWRKEY', 'Pulse low for ~1 second to virtually press the modem\'s power button'],
    ['5', 'RST', 'Hold HIGH to keep the modem out of reset'],
    ['26', 'MODEM_RX', 'ESP32 sends from this pin → goes into the modem\'s RX'],
    ['27', 'MODEM_TX', 'Modem sends from its TX → comes into the ESP32\'s pin 27'],
]
story.append(make_table(pins, col_widths=[2 * cm, 3 * cm, 9.5 * cm]))

story.append(P("Without the ESP32 driving these pins, the 4G modem stays off — even though "
               "the USB connection appears to work. This was one of the first issues the user "
               "hit (see Section 6 lessons learned).", body))

story.append(P("2.3 Power requirement", h2))
story.append(P("The 4G modem can draw bursts of up to 2 A during transmit. USB-C from a "
               "laptop typically only supplies 500 mA. For reliable operation, the LilyGO "
               "board needs additional power:", body))
power_opts = [
    ['Option', 'How', 'Status'],
    ['18650 Li-ion battery', 'Insert charged 18650 cell into the holder on the board', 'Best — recommended for production'],
    ['External 5 V supply', 'Feed 5 V to the board\'s VBUS pin', 'Works'],
    ['USB-C only', 'Plug board directly into laptop / phone charger', 'Works for AT testing, marginal for transmit bursts'],
]
story.append(make_table(power_opts, col_widths=[3.5 * cm, 7 * cm, 4 * cm]))

story.append(PageBreak())

# ============== Section 3 — Bridge Sketch ==============
story.append(P("3. Arduino Bridge Sketch", h1))

story.append(P("The ESP32 runs a small Arduino program that does two things at startup:<br/>"
               "(1) drives the modem power-on sequence using GPIO pins, and "
               "(2) becomes a transparent bridge that forwards every byte between "
               "USB Serial and the modem UART in both directions.",
               body))

story.append(P("3.1 Final working sketch", h2))
story.append(code('''#include <HardwareSerial.h>

HardwareSerial gsmSerial(2);

#define MODEM_RX_PIN      27
#define MODEM_TX_PIN      26
#define MODEM_PWRKEY_PIN  4
#define MODEM_POWERON_PIN 12
#define MODEM_RST_PIN     5
#define PC_BAUD           115200
#define MODEM_BAUD        115200

void setup() {
  Serial.begin(PC_BAUD);
  delay(500);
  Serial.println("\\n[ESP32] booting...");

  // Enable 4G modem power
  pinMode(MODEM_POWERON_PIN, OUTPUT);
  digitalWrite(MODEM_POWERON_PIN, HIGH);

  // Keep reset HIGH (not in reset)
  pinMode(MODEM_RST_PIN, OUTPUT);
  digitalWrite(MODEM_RST_PIN, HIGH);

  // Pulse PWRKEY to power on the modem
  pinMode(MODEM_PWRKEY_PIN, OUTPUT);
  digitalWrite(MODEM_PWRKEY_PIN, HIGH);
  delay(100);
  digitalWrite(MODEM_PWRKEY_PIN, LOW);
  delay(1000);
  digitalWrite(MODEM_PWRKEY_PIN, HIGH);

  Serial.println("[ESP32] PWRKEY pulsed, waiting for modem to boot...");
  delay(5000);

  gsmSerial.begin(MODEM_BAUD, SERIAL_8N1, MODEM_RX_PIN, MODEM_TX_PIN);

  Serial.println("[ESP32] Bridge ready. Type AT commands.");
}

void loop() {
  // PC -> modem (transparent passthrough)
  while (Serial.available() > 0) {
    gsmSerial.write((char)Serial.read());
  }

  // Modem -> PC (transparent passthrough)
  while (gsmSerial.available() > 0) {
    Serial.write((char)gsmSerial.read());
  }
}'''))

story.append(P("3.2 Arduino IDE settings", h2))
ide_settings = [
    ['Setting', 'Value'],
    ['Board', 'ESP32 Dev Module'],
    ['Upload Speed', '921600'],
    ['CPU Frequency', '240 MHz (WiFi/BT)'],
    ['Flash Frequency', '80 MHz'],
    ['Flash Mode', 'QIO'],
    ['Flash Size', '4MB (32Mb)'],
    ['Partition Scheme', 'Default 4MB with spiffs'],
    ['Port', 'whatever COM port the CH9102 driver assigns'],
]
story.append(make_table(ide_settings, col_widths=[5 * cm, 9.5 * cm]))

story.append(P("3.3 CH9102 driver", h2))
story.append(P("The LilyGO board's USB bridge uses a <b>CH9102</b> chip (similar to CH340). "
               "Windows does not always install the driver automatically. If the COM port does "
               "not appear in Device Manager, download the driver from <i>wch-ic.com</i> "
               "(search &laquo;CH9102 Windows driver&raquo;), install it, and replug the USB-C cable.",
               body))

story.append(P("3.4 Serial Monitor settings", h2))
sm = [
    ['Setting', 'Value'],
    ['Baud rate', '115200 (this is PC ↔ ESP32, not ESP32 ↔ modem)'],
    ['Line ending', 'Both NL &amp; CR (CRITICAL — modem ignores AT without proper line ending)'],
]
story.append(make_table(sm, col_widths=[4 * cm, 10.5 * cm]))

story.append(PageBreak())

# ============== Section 4 — AT Command Reference ==============
story.append(P("4. AT Command Reference", h1))

story.append(P("Every command typed during Phase 4, what it does, what reply to expect, and "
               "why it matters. Run them in the order shown in Section 5.",
               body))

story.append(P("4.1 — AT", h2))
story.append(P("<b>Definition:</b> The simplest possible AT command. Comes from the original "
               "Hayes modem standard from the 1980s. Just two letters and Enter — used to "
               "verify that the modem is alive and listening.<br/>"
               "<b>Reply:</b> <code>OK</code><br/>"
               "<b>Why we use it:</b> sanity check. If <code>AT</code> doesn't reply <code>OK</code>, "
               "no other command will work either. Always type this first.", body))

story.append(P("4.2 — ATE0", h2))
story.append(P("<b>Definition:</b> Echo Off. Tells the modem &laquo;don't echo my commands "
               "back to me&raquo;.<br/>"
               "<b>Reply:</b> <code>OK</code><br/>"
               "<b>Why we use it:</b> by default the modem echoes every character you type. "
               "When the responses come, your output looks like:<br/>"
               "<code>AT+CSQ &lt;-- echoed back<br/>+CSQ: 22,99 &lt;-- actual response<br/>OK</code><br/>"
               "After ATE0 the echo stops, so you only see the response &mdash; cleaner output.",
               body))

story.append(P("4.3 — AT+CPIN?", h2))
story.append(P("<b>Definition:</b> &laquo;PIN?&raquo; Query the SIM card's lock status. "
               "Asks: &laquo;Is the SIM card present and unlocked?&raquo;<br/>"
               "<b>Replies:</b><br/>"
               "<code>+CPIN: READY</code> &mdash; SIM is unlocked and ready (good)<br/>"
               "<code>+CPIN: SIM PIN</code> &mdash; SIM needs a PIN code (use AT+CPIN=&quot;1234&quot; to enter)<br/>"
               "<code>+CME ERROR: 10</code> &mdash; no SIM card inserted<br/>"
               "<b>Why we use it:</b> if SIM isn't ready, all later network commands will fail. "
               "Confirm READY before continuing.", body))

story.append(P("4.4 — AT+CSQ", h2))
story.append(P("<b>Definition:</b> &laquo;Cellular Signal Quality&raquo;. Asks the modem how "
               "strong the signal from the cell tower is.<br/>"
               "<b>Reply:</b> <code>+CSQ: &lt;rssi&gt;,&lt;ber&gt;</code><br/>"
               "<b>Interpretation:</b>", body))
csq = [
    ['rssi value', 'Signal quality'],
    ['0–9', 'Marginal — connection unstable'],
    ['10–14', 'OK — usable'],
    ['15–19', 'Good'],
    ['20–30', 'Excellent'],
    ['31', 'Maximum (rare)'],
    ['99', 'Unknown / not detectable'],
]
story.append(make_table(csq, col_widths=[3 * cm, 11.5 * cm]))
story.append(P("The second value (BER, Bit Error Rate) is usually 99 (unknown) on most modems. "
               "Ignore it. Only the first number matters. The user got <b>22,99</b> which is "
               "excellent.", body))

story.append(P("4.5 — AT+CREG?", h2))
story.append(P("<b>Definition:</b> &laquo;Cellular network REGistration&raquo;. Asks: &laquo;Am I "
               "registered with a cell tower right now?&raquo;<br/>"
               "<b>Reply:</b> <code>+CREG: &lt;n&gt;,&lt;stat&gt;</code><br/>"
               "<b>Interpretation of stat:</b>", body))
creg = [
    ['stat', 'Meaning'],
    ['0', 'Not registered, not searching'],
    ['1', 'Registered, on home network ✓'],
    ['2', 'Searching for a network'],
    ['3', 'Registration denied'],
    ['4', 'Unknown'],
    ['5', 'Registered, on roaming network ✓'],
]
story.append(make_table(creg, col_widths=[2 * cm, 12.5 * cm]))
story.append(P("Stat = 1 or 5 means you can use the network. Anything else and you cannot make "
               "data connections. The user got <b>0,1</b> = registered on home network "
               "(Vodafone Egypt) ✓.", body))

story.append(P("4.6 — AT+CGATT?", h2))
story.append(P("<b>Definition:</b> &laquo;Cellular GPRS ATtach status&raquo;. Asks: &laquo;Am I "
               "attached to the data (GPRS/4G) network, separate from voice?&raquo;<br/>"
               "<b>Replies:</b><br/>"
               "<code>+CGATT: 1</code> &mdash; attached to data network ✓<br/>"
               "<code>+CGATT: 0</code> &mdash; not attached. Use <code>AT+CGATT=1</code> to attach.<br/>"
               "<b>Why:</b> registration (CREG) is voice-side; GPRS attach (CGATT) is data-side. "
               "Both must be 1 before you can open TCP sockets.", body))

story.append(P("4.7 — AT+CGDCONT", h2))
story.append(P("<b>Definition:</b> &laquo;Cellular GPRS Define CONText&raquo;. Sets the APN "
               "(Access Point Name) — the gateway that lets your modem reach the public internet "
               "through the carrier.<br/>"
               "<b>Syntax:</b> <code>AT+CGDCONT=&lt;cid&gt;,&quot;&lt;type&gt;&quot;,&quot;&lt;apn&gt;&quot;</code><br/>"
               "<b>Example used:</b> <code>AT+CGDCONT=1,&quot;IP&quot;,&quot;internet.vodafone.net&quot;</code><br/>"
               "<b>Reply:</b> <code>OK</code><br/>"
               "<b>Parameters:</b><br/>"
               "&nbsp;&nbsp;<i>cid</i> = context ID, almost always 1<br/>"
               "&nbsp;&nbsp;<i>type</i> = &quot;IP&quot; for IPv4 (the standard choice)<br/>"
               "&nbsp;&nbsp;<i>apn</i> = the carrier's APN string", body))
apns = [
    ['Egyptian carrier', 'APN string'],
    ['Vodafone (the user\'s SIM)', 'internet.vodafone.net'],
    ['Orange', 'internet.orange'],
    ['Etisalat', 'etisalat'],
    ['WE', 'internet'],
]
story.append(make_table(apns, col_widths=[5 * cm, 9.5 * cm]))

story.append(P("4.8 — AT+CGACT", h2))
story.append(P("<b>Definition:</b> &laquo;Cellular GPRS ACTivate&raquo;. Activates the data "
               "session you defined with CGDCONT. After this command, the modem has an IP "
               "address from the carrier and can reach the internet.<br/>"
               "<b>Syntax:</b> <code>AT+CGACT=&lt;state&gt;,&lt;cid&gt;</code><br/>"
               "<b>Used:</b> <code>AT+CGACT=1,1</code> &mdash; state=1 (activate), cid=1 (context 1)<br/>"
               "<b>Reply:</b> <code>OK</code> (may take 5–10 seconds)<br/>"
               "<b>Why:</b> CGDCONT only DEFINES the parameters; CGACT actually ESTABLISHES the "
               "connection. Without CGACT the modem has the APN string saved but no IP.", body))

story.append(P("4.9 — AT+NETOPEN", h2))
story.append(P("<b>Definition:</b> Open the IP application stack inside the modem. Newer "
               "SIMCom firmware (A7608, A7670) uses this command set instead of the older "
               "<code>AT+CIPMUX</code> / <code>AT+CIPSTART</code> set found in SIM800 era.<br/>"
               "<b>Reply:</b> <code>OK</code> followed by <code>+NETOPEN: 0</code><br/>"
               "<b>Why:</b> after CGACT the modem has IP connectivity, but the IP stack inside "
               "the modem isn't running yet. NETOPEN starts it so you can open TCP/UDP sockets.", body))

story.append(P("4.10 — AT+CIPOPEN", h2))
story.append(P("<b>Definition:</b> Open a TCP or UDP socket. Equivalent to a programming "
               "<code>connect()</code> call.<br/>"
               "<b>Syntax:</b> <code>AT+CIPOPEN=&lt;link_id&gt;,&quot;TCP&quot;,&quot;&lt;host&gt;&quot;,&lt;port&gt;</code><br/>"
               "<b>Used:</b> <code>AT+CIPOPEN=0,&quot;TCP&quot;,&quot;tcpbin.com&quot;,4242</code><br/>"
               "<b>Reply:</b> <code>OK</code> followed by <code>+CIPOPEN: 0,0</code> (link 0, "
               "result 0 = success)<br/>"
               "<b>Why:</b> tcpbin.com:4242 is a public test server that echoes back anything "
               "you send to it. Useful for verifying TCP works without setting up your own "
               "server.<br/>"
               "<b>Other result codes:</b> 1=resolution fail (DNS), 2=connect fail (no route), "
               "3=connect fail (refused), 4=socket allocation fail.", body))

story.append(P("4.11 — AT+CIPSEND", h2))
story.append(P("<b>Definition:</b> Send bytes through an open socket.<br/>"
               "<b>Syntax:</b> <code>AT+CIPSEND=&lt;link_id&gt;,&lt;byte_count&gt;</code><br/>"
               "<b>Used:</b> <code>AT+CIPSEND=0,5</code> &mdash; send 5 bytes through link 0<br/>"
               "<b>Behaviour:</b><br/>"
               "&nbsp;&nbsp;1. Modem replies with a <code>&gt;</code> prompt<br/>"
               "&nbsp;&nbsp;2. You type exactly &lt;byte_count&gt; characters (no Enter)<br/>"
               "&nbsp;&nbsp;3. Modem replies <code>+CIPSEND: 0,5,5</code> (link, requested, actual)<br/>"
               "&nbsp;&nbsp;4. If the server echoes back, you'll see <code>+IPD &lt;n&gt;</code> "
               "followed by the data", body))

story.append(P("4.12 — Unsolicited Result Codes (URCs)", h2))
story.append(P("These are messages the modem sends without you asking. They appear at any time "
               "in the terminal:", body))
urcs = [
    ['URC', 'Meaning'],
    ['+CPIN: READY', 'SIM finished initializing (sent automatically at boot)'],
    ['SMS Ready', 'SMS subsystem is ready'],
    ['PB DONE', 'Phonebook service initialized'],
    ['+IPD &lt;n&gt;', 'Incoming &lt;n&gt; bytes of data on a socket — followed by the actual bytes'],
    ['+IPCLOSE: 0,1', 'Socket 0 was closed by the remote (1=closed by peer, 2=timeout)'],
    ['+CFUN: 1', 'Modem entered full functionality mode'],
]
story.append(make_table(urcs, col_widths=[3.5 * cm, 11 * cm]))

story.append(PageBreak())

# ============== Section 5 — Working Sequence ==============
story.append(P("5. Working Sequence — In Order", h1))

story.append(P("These are the exact commands the user typed and the actual responses "
               "received during the successful Phase 4 run. Type each one, wait for the "
               "response, then proceed to the next.", body))

story.append(P("5.1 — Verify modem is alive", h2))
story.append(code('''> AT
OK

> ATE0
OK'''))

story.append(P("5.2 — SIM and signal", h2))
story.append(code('''> AT+CPIN?
+CPIN: READY
OK

> AT+CSQ
+CSQ: 22,99
OK

> AT+CREG?
+CREG: 0,1
OK'''))
story.append(P("Signal of 22 is excellent. Stat = 1 = registered on Vodafone home network.", body))

story.append(P("5.3 — APN and data session activation", h2))
story.append(code('''> AT+CGDCONT=1,"IP","internet.vodafone.net"
OK

> AT+CGACT=1,1
OK'''))

story.append(P("5.4 — Open IP stack", h2))
story.append(code('''> AT+NETOPEN
OK
+NETOPEN: 0'''))

story.append(P("5.5 — Open TCP socket", h2))
story.append(code('''> AT+CIPOPEN=0,"TCP","tcpbin.com",4242
OK
+CIPOPEN: 0,0'''))
story.append(P("0,0 = link 0 opened successfully. The TCP connection is now live.", body))

story.append(P("5.6 — Send data", h2))
story.append(code('''> AT+CIPSEND=0,5
>
(now type the 5 characters with no Enter:)
hello

(modem replies:)
OK
+CIPSEND: 0,5,5

(then the server echoes back the 5 bytes:)
+IPD 5
hello

(eventually the test server closes the connection:)
+IPCLOSE: 0,1'''))

story.append(P("PHASE 4 COMPLETE. The full data path is verified end-to-end: PC &rarr; ESP32 "
               "bridge &rarr; A7608 modem &rarr; cell tower &rarr; 4G core &rarr; internet "
               "&rarr; tcpbin.com &rarr; back. The modem can connect to TCP services on the "
               "public internet.", success_style))

story.append(PageBreak())

# ============== Section 6 — Lessons Learned ==============
story.append(P("6. Lessons Learned (from the actual debug session)", h1))

story.append(P("Phase 4 hit several roadblocks that took an hour or more to solve. They are "
               "documented here so the same time isn't wasted next time.", body))

story.append(P("6.1 — &laquo;BRIDGE READY&raquo; appeared but AT got no response", h2))
story.append(P("<b>Symptom:</b> the ESP32 boot text printed &laquo;[*] BRIDGE READY&raquo;, "
               "but typing AT in PuTTY did nothing.<br/>"
               "<b>Cause:</b> &laquo;BRIDGE READY&raquo; only means the ESP32's bridge firmware "
               "started. The actual 4G modem chip is a separate IC and needs the ESP32 to "
               "drive its POWERON / PWRKEY pins to power on. The original sketch did not do "
               "this.<br/>"
               "<b>Fix:</b> add the power-on sequence in setup() &mdash; set MODEM_POWERON_PIN "
               "(GPIO 12) HIGH, set MODEM_RST_PIN (GPIO 5) HIGH, pulse MODEM_PWRKEY_PIN "
               "(GPIO 4) low for 1 second, then wait 5 seconds before opening the modem UART.",
               body))

story.append(P("6.2 — Garbled characters in Serial Monitor", h2))
story.append(P("<b>Symptom:</b> after fixing the power-on, the bridge produced unreadable "
               "&laquo;b'@$@bbA'`bb…&raquo; gibberish.<br/>"
               "<b>Cause:</b> baud rate mismatch between ESP32 and modem.<br/>"
               "<b>Fix:</b> the user's specific A7608 firmware uses 115200 baud (the standard "
               "default for SIMCom). Some boards report needing 921600 — try 115200 first, "
               "then 921600 if garbled.<br/>"
               "<b>Note:</b> the PC-to-ESP32 baud (Serial Monitor) is independent and stays "
               "at 115200 regardless.", body))

story.append(P("6.3 — Could not type in PuTTY", h2))
story.append(P("<b>Symptom:</b> keyboard input didn't appear in the terminal.<br/>"
               "<b>Cause:</b> default PuTTY has Local Echo off, so characters only appear "
               "after the modem echoes them. If the modem isn't answering, typing looks "
               "invisible.<br/>"
               "<b>Fix:</b> Right-click the PuTTY title bar &rarr; Change Settings &rarr; "
               "Terminal &rarr; <b>Local echo: Force on</b>, <b>Local line editing: Force on</b>. "
               "Or use the Arduino IDE Serial Monitor instead, which always shows your input.",
               body))

story.append(P("6.4 — &laquo;NO PORTS DISCOVERED&raquo; in Arduino IDE", h2))
story.append(P("<b>Symptom:</b> Arduino IDE didn't show the LilyGO board's COM port.<br/>"
               "<b>Cause:</b> the LilyGO board uses a CH9102 USB-serial chip (not the more "
               "common CH340 or CP2102). Windows doesn't have the driver built in.<br/>"
               "<b>Fix:</b> install the CH9102 driver from wch-ic.com, replug the cable.",
               body))

story.append(P("6.5 — AT+CIPMUX and AT+CIPSTART returned ERROR", h2))
story.append(P("<b>Symptom:</b> after CGACT succeeded, attempts to use the older IP commands "
               "(<code>AT+CIPMUX=0</code> then <code>AT+CIPSTART</code>) both returned ERROR.<br/>"
               "<b>Cause:</b> the A7608 firmware uses a newer IP command set that doesn't "
               "include CIPMUX/CIPSTART. The older syntax is from the SIM800/SIM900 era.<br/>"
               "<b>Fix:</b> use <code>AT+NETOPEN</code> followed by <code>AT+CIPOPEN=0,&quot;TCP&quot;,...</code> "
               "and <code>AT+CIPSEND=0,&lt;n&gt;</code>. The link ID parameter is always "
               "required (0 for the first connection).", body))

story.append(P("6.6 — One of the two T-A7608 modules didn't respond", h2))
story.append(P("<b>Symptom:</b> the second T-A7608 module didn't respond to AT even with the "
               "same cable and PC.<br/>"
               "<b>Cause:</b> likely a hardware defect or different firmware. Could not be "
               "diagnosed remotely without comparing the two boards side by side.<br/>"
               "<b>Action:</b> Phase 4 development continues on the working module. The broken "
               "one needs to be inspected (antenna connection, button labels, comparison "
               "with the working board) before Phase 6 (where two devices need to talk).", body))

story.append(P("6.7 — Common typos to watch for", h2))
typos = [
    ['Wrong', 'Right'],
    ['AT+CGADCONT', 'AT+CGDCONT (no extra A)'],
    ['AT+CSPN?', 'AT+CPIN? (P-I-N like the SIM PIN)'],
    ['AT+CIPMUX', 'AT+NETOPEN (CIPMUX is the old SIM800 command, A7608 uses NETOPEN)'],
    ['AT+CIPSTART', 'AT+CIPOPEN (same reason)'],
]
story.append(make_table(typos, col_widths=[5 * cm, 9.5 * cm]))

story.append(PageBreak())

# ============== Section 7 — What's Next ==============
story.append(P("7. What's Next", h1))

story.append(P("Phase 4 proved that a human can connect to the cellular network, attach to "
               "data, and open a TCP socket through manual AT commands. Phase 5 puts the "
               "STM32 in charge of doing the same thing automatically.", body))

story.append(P("7.1 — Phase 5: STM32 drives the LTE module", h2))
phase5 = [
    "Disconnect the LTE module from the ESP32 / USB-C bridge.",
    "Wire the LTE module's TXD/RXD pins directly to the STM32's USART1 (PA9, PA10).",
    "Power the LTE module from a stable 5 V supply (NOT the STM32's 3.3 V regulator).",
    "Common ground between LTE module, STM32, and any external supply.",
    "Write STM32 firmware that automates the AT sequence from Section 5: AT, ATE0, AT+CPIN?, AT+CSQ, AT+CREG?, AT+CGDCONT, AT+CGACT, AT+NETOPEN, AT+CIPOPEN to the relay server.",
    "Start running the small Python relay server on the developer's laptop with ngrok exposing it.",
    "Replace tcpbin.com:4242 with the ngrok-provided host:port.",
    "STM32 sends &quot;REG &lt;phone_number&gt;&quot; to the relay and waits for &quot;OK&quot;.",
]
for p in phase5:
    story.append(P("• " + p, bullet))

story.append(P("7.2 — Phase 6 onwards", h2))
later = [
    ['Phase', 'Adds'],
    ['6 — Two-node plain audio', 'Both devices connected. CALL/ANS protocol. Audio bytes flow through relay. No encryption yet.'],
    ['7 — Hybrid encryption', 'mbedTLS RSA-512 wraps an AES-128 key at session start; AES-CTR encrypts bulk audio.'],
    ['8 — Polish &amp; demo', 'Physical Call/Answer buttons, status LEDs (idle/ringing/in-call), video backup of the demo.'],
]
story.append(make_table(later, col_widths=[4.5 * cm, 10 * cm]))

story.append(P("Phase 4 is the gateway between &laquo;the device works alone on a desk&raquo; "
               "(Phases 1–3) and &laquo;two devices talk to each other over the internet&raquo; "
               "(Phase 5+). All the protocol learning happens here so Phase 5 firmware doesn't "
               "have to debug the modem in addition to its own logic.", body))

story.append(Spacer(1, 0.5 * cm))
story.append(P("End of Phase 4 document.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 4 — LTE AT Command Bring-up",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")
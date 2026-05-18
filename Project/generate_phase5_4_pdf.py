"""
Generates Phase 5.4 PDF — STM32 Takes Over (Option B1).
Full wiring, CubeMX changes, pin assignments for putting the STM32
in direct control of the LTE modem (no Arduino, no ESP32 in the loop).
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase5_4_STM32_LTE_Setup.pdf"

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
                      "Secure Voice Project | Phase 5.4 — STM32 Takes Over LTE Control")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

# Title
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 5.4<br/>STM32 Takes Over<br/>LTE Control", title_style))
story.append(P("Option B1: STM controls EVERYTHING — no Arduino in the toolchain",
               subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P("This document covers the wiring, CubeMX configuration, and pin assignments "
               "needed to put the STM32 in <b>direct control</b> of the T-A7608 modem on the "
               "LilyGO board. The ESP32 is held in reset and stays out of the way; STM32 handles "
               "modem power-on AND UART communication.",
               body))
story.append(Spacer(1, 0.5 * cm))
story.append(P("<b>Submission 1 scope (no encryption):</b> two devices register with the relay "
               "over LTE, exchange plain audio bytes both directions, identify each other by "
               "phone number. Encryption is added in Submission 2 (Phase 7).",
               success_style))
story.append(PageBreak())

# ============== Section 1 — Why this approach ==============
story.append(P("1. Why STM32 in Direct Control (Option B1)", h1))

story.append(P("In Phase 5.3 the LTE modem was driven by hand through Arduino IDE Serial "
               "Monitor. The ESP32 on the LilyGO board was acting as a USB &laquo;bridge&raquo; "
               "between the laptop and the modem. That works for testing but is not the final "
               "architecture &mdash; for the demo we need the STM32 to be the brain.",
               body))

story.append(P("There were two ways to get there:"))

story.append(P("Option B1 (this approach) &mdash; STM only", h2))
story.append(P("STM32 controls modem power-on AND UART. ESP32 is held in reset (its pins go to "
               "high-impedance) so it doesn't fight on the UART lines.",
               body))
points = [
    "<b>Pros:</b> No Arduino IDE in the toolchain. Cleaner. STM32 can power-cycle the modem from firmware if it gets stuck.",
    "<b>Cons:</b> 5 wires for control instead of 3. Slightly more CubeMX setup.",
]
for p in points:
    story.append(P("• " + p, bullet))

story.append(P("Option B2 &mdash; Arduino once, STM after", h2))
story.append(P("Flash the ESP32 once with a sketch that powers on the modem and goes to "
               "deep sleep. After that, only STM32 talks to the modem (3 wires).",
               body))
points = [
    "<b>Pros:</b> Only 3 wires.",
    "<b>Cons:</b> Need Arduino IDE for the one-time flash.",
]
for p in points:
    story.append(P("• " + p, bullet))

story.append(P("<b>Selected: Option B1.</b> The Arduino dependency is removed entirely. The "
               "5 extra wires are once-and-done.", success_style))

# ============== Section 2 — Architecture ==============
story.append(P("2. Architecture", h1))

story.append(ascii_block(r"""
   STM32 Black Pill                          LilyGO XY-A7608B v1.2
   ───────────────                           ──────────────────────
                                              ┌────────────────┐
   PA8 ──── ESP32_RST ───────HOLD LOW────────▶│ ESP32 (in reset│
                                              │  doesn't run)  │
                                              └────────────────┘

   PB1 ──── MODEM_POWERON ───HOLD HIGH───────▶ A7608 power supply enable
   PB2 ──── MODEM_PWRKEY  ───PULSE LOW 1s───▶ A7608 virtual power button

   PA9  (USART1_TX) ─────────data───────────▶ A7608 RXD (via IO26)
   PA10 (USART1_RX) ◀───────data───────────── A7608 TXD (via IO27)
   GND  ──────────── shared ground ──────────  GND

   Buttons:
   PA1  (input, pull-up) ◀──── push button ──▶ GND   (Call)
   PB0  (input, pull-up) ◀──── push button ──▶ GND   (Answer/Hangup)
""".strip()))

story.append(P("Every audio sample, every AT command, every byte — they all pass through the "
               "STM32. The ESP32 doesn't run any code; it sits in reset with its UART pins "
               "tristated so they don't conflict with the STM32's drive of those lines.",
               body))

# ============== Section 3 — Wiring ==============
story.append(P("3. Complete Wiring (8 wires + GND)", h1))

story.append(P("3.1 — Power-on / control wires (3)", h2))
ctl = [
    ['#', 'STM32 pin', 'LilyGO pin', 'Function'],
    ['1', 'PA8 (output)', 'RST (right header)', 'ESP32 reset hold — drive LOW always (keeps ESP32 stopped, pins go high-Z)'],
    ['2', 'PB1 (output)', 'IO12 (left header)', 'Modem POWERON — drive HIGH always (powers the A7608 chip)'],
    ['3', 'PB2 (output)', 'IO4 (left header)', 'Modem PWRKEY — initially HIGH; pulse LOW for 1 second at boot to power on the modem'],
]
story.append(make_table(ctl, col_widths=[1 * cm, 3 * cm, 3.5 * cm, 7 * cm]))

story.append(P("3.2 — UART to modem (2 wires + ground)", h2))
uart = [
    ['#', 'STM32 pin', 'LilyGO pin', 'Direction'],
    ['4', 'PA9 (USART1_TX)', 'IO26 (left header)', 'STM32 → modem (RX into modem)'],
    ['5', 'PA10 (USART1_RX)', 'IO27 (left header)', 'STM32 ← modem (TX from modem)'],
    ['6', 'GND', 'GND', 'Common ground (mandatory)'],
]
story.append(make_table(uart, col_widths=[1 * cm, 3 * cm, 3.5 * cm, 7 * cm]))

story.append(P("3.3 — User buttons (2)", h2))
btn = [
    ['#', 'STM32 pin', 'Connected to', 'Function'],
    ['7', 'PA1 (input, pull-up)', 'Call button → GND', 'Pressed → initiate a call to peer'],
    ['8', 'PB0 (input, pull-up)', 'Answer/Hangup button → GND', 'Pressed → answer incoming OR end ongoing call'],
]
story.append(make_table(btn, col_widths=[1 * cm, 3 * cm, 4.5 * cm, 6 * cm]))

story.append(P("Buttons use STM32's internal pull-up resistors. With the button NOT pressed, "
               "the pin reads HIGH. When pressed, the button connects the pin to GND, and the "
               "pin reads LOW. Software detects the falling edge as a button press.",
               note_style))

story.append(P("3.4 — Power for each board", h2))
power = [
    ['Board', 'Power source', 'Notes'],
    ['STM32 Black Pill', 'USB-C from PC', 'Same as before — for programming and runtime'],
    ['LilyGO LTE board', 'USB-C from phone charger OR 18650 battery OR VBUS pin', 'Needs separate ≥5V/2A supply (USB-C from laptop is OK for testing)'],
]
story.append(make_table(power, col_widths=[3.5 * cm, 5.5 * cm, 5.5 * cm]))

story.append(P("Both boards must share the same GND (covered by wire 6 above). All other "
               "wires use the same ground reference automatically.", body))

story.append(PageBreak())

# ============== Section 4 — Pin Map ==============
story.append(P("4. Complete STM32 Pin Map (after Phase 5.4)", h1))

pin_map = [
    ['Pin', 'Function', 'Connection', 'Phase added'],
    ['PA0', 'ADC1_IN0', 'MAX9814 OUT (mic)', '2'],
    ['PA1', 'GPIO input (pull-up)', 'Call button → GND', '5.4 (NEW)'],
    ['PA8', 'GPIO output (low)', 'LilyGO RST (ESP32 reset hold)', '5.4 (NEW)'],
    ['PA9', 'USART1_TX', 'LilyGO IO26 (modem RX)', '5.4 (NEW)'],
    ['PA10', 'USART1_RX', 'LilyGO IO27 (modem TX)', '5.4 (NEW)'],
    ['PA13', 'SWDIO', 'ST-Link', '1'],
    ['PA14', 'SWCLK', 'ST-Link', '1'],
    ['PB0', 'GPIO input (pull-up)', 'Answer/Hangup button → GND', '5.4 (NEW)'],
    ['PB1', 'GPIO output (high)', 'LilyGO IO12 (POWERON)', '5.4 (NEW)'],
    ['PB2', 'GPIO output (high, pulse low)', 'LilyGO IO4 (PWRKEY)', '5.4 (NEW)'],
    ['PB6', 'I2C1_SCL', 'MCP4725 SCL', '3'],
    ['PB7', 'I2C1_SDA', 'MCP4725 SDA', '3'],
    ['PC13', 'GPIO output (LED)', 'Onboard LED (status)', '2'],
    ['3V3 / GND', 'Power', 'MAX9814, MCP4725 (3V3); LM386 (5V)', '1+'],
]
story.append(make_table(pin_map, col_widths=[1.5 * cm, 4.5 * cm, 6 * cm, 2 * cm]))

# ============== Section 5 — CubeMX changes ==============
story.append(P("5. CubeMX Configuration Changes", h1))

story.append(P("Open <b>MicDAC.ioc</b> in CubeMX. Do NOT touch existing peripherals (ADC1, "
               "TIM2, TIM3, I2C1) — only ADD the items below.",
               warn_style))

story.append(P("5.1 — Enable USART1", h2))
points = [
    "Connectivity → <b>USART1</b> → Mode: <b>Asynchronous</b>.",
    "Parameter Settings → Baud Rate: <b>115200</b>; Word Length: 8 bits; Parity: None; Stop Bits: 1.",
    "Hardware Flow Control: None.",
    "<b>NVIC Settings</b> tab → tick <b>USART1 global interrupt</b>.",
    "PA9 (TX) and PA10 (RX) auto-assign on the chip diagram.",
]
for p in points:
    story.append(P("• " + p, bullet))

story.append(P("5.2 — Add 3 GPIO outputs (modem + ESP32 control)", h2))
story.append(P("On the chip diagram, left-click each pin and select <b>GPIO_Output</b>. Then "
               "in System Core → GPIO, click each pin row and configure:"))
gpio_out = [
    ['Pin', 'User Label', 'Output level (initial)', 'Mode', 'Speed', 'Pull'],
    ['PA8', 'ESP32_RST', 'Low', 'Push Pull', 'Low', 'No'],
    ['PB1', 'MODEM_POWERON', 'High', 'Push Pull', 'Low', 'No'],
    ['PB2', 'MODEM_PWRKEY', 'High', 'Push Pull', 'Low', 'No'],
]
story.append(make_table(gpio_out, col_widths=[1.5 * cm, 3.5 * cm, 3 * cm, 2 * cm, 1.5 * cm, 1 * cm]))

story.append(P("Initial levels: PA8=Low keeps the ESP32 in reset from the moment STM32 boots. "
               "PB1=High keeps modem power on. PB2=High is the idle state of PWRKEY (firmware "
               "pulses it LOW for 1 second once at boot to power on the modem chip).",
               body))

story.append(P("5.3 — Add 2 GPIO inputs (buttons)", h2))
story.append(P("Left-click each pin and select <b>GPIO_Input</b>. Then in GPIO config:"))
gpio_in = [
    ['Pin', 'User Label', 'Mode', 'Pull-up/Pull-down'],
    ['PA1', 'BTN_CALL', 'Input', 'Pull-up'],
    ['PB0', 'BTN_ANSWER', 'Input', 'Pull-up'],
]
story.append(make_table(gpio_in, col_widths=[2 * cm, 4 * cm, 3 * cm, 4 * cm]))

story.append(P("5.4 — Generate code", h2))
points = [
    "Project Manager → confirm Toolchain = CMake.",
    "Click <b>GENERATE CODE</b>.",
    "VS Code reloads the project automatically.",
]
for p in points:
    story.append(P("• " + p, bullet))

story.append(PageBreak())

# ============== Section 6 — Verification ==============
story.append(P("6. Verification Before Writing Firmware", h1))

story.append(P("After regenerating the CubeMX code, do these quick checks:"))

story.append(P("6.1 — Open Core/Src/gpio.c", h2))
story.append(P("Verify the <code>MX_GPIO_Init()</code> function configures all the new pins. "
               "Search for the lines that set GPIO_PIN_8 / GPIO_PIN_1 / GPIO_PIN_2 etc. and "
               "confirm initial output levels and pull settings.",
               body))

story.append(P("6.2 — Open Core/Src/usart.c", h2))
story.append(P("Should contain a <code>MX_USART1_UART_Init()</code> function with baud rate "
               "115200 and PA9/PA10 configured as alternate function (USART1 TX/RX).",
               body))

story.append(P("6.3 — Compile with no errors", h2))
points = [
    "Build (Ctrl+Shift+B in VS Code).",
    "Should report <b>0 errors, 0 warnings</b>.",
    "If there are errors, the CubeMX changes had a problem &mdash; re-check.",
]
for p in points:
    story.append(P("• " + p, bullet))

story.append(P("6.4 — Multimeter sanity check (optional)", h2))
mm = [
    ['Probe', 'Expected reading', 'Why'],
    ['STM32 PA8 vs GND', '~0 V', 'ESP32 hold is LOW'],
    ['STM32 PB1 vs GND', '~3.3 V', 'POWERON is HIGH (modem powered)'],
    ['STM32 PB2 vs GND (steady)', '~3.3 V', 'PWRKEY idle HIGH'],
    ['STM32 PA1 vs GND, button NOT pressed', '~3.3 V', 'pull-up active'],
    ['STM32 PA1 vs GND, button PRESSED', '~0 V', 'button shorts to GND'],
    ['STM32 PB0 same test', 'same as PA1', ''],
]
story.append(make_table(mm, col_widths=[5 * cm, 4 * cm, 5.5 * cm]))

# ============== Section 7 — what's next ==============
story.append(P("7. What's Next — Phase 5.4 Firmware", h1))

story.append(P("After wiring + CubeMX is done, the firmware additions to <code>main.c</code> "
               "will include:", body))

next_steps = [
    ['Block', 'What it does'],
    ['Modem power-on sequence at boot', 'Pulse PB2 (PWRKEY) low for 1 sec, wait 8 sec for boot'],
    ['UART RX interrupt handler', 'Buffers bytes received from the modem so the main loop can parse responses'],
    ['send_at(cmd, expected, timeout)', 'Helper that writes an AT command, waits for the expected response within a timeout'],
    ['LTE bring-up state machine', 'Runs AT, ATE0, AT+CPIN?, AT+CSQ, AT+CGDCONT, AT+CGACT, AT+NETOPEN, AT+CIPOPEN to relay'],
    ['REG sender', 'Sends "REG <phone>" through the open TCP socket, waits for "OK"'],
    ['Status LED logic', 'PC13: slow-blink = registered idle, fast-blink = ringing, solid = in call'],
    ['Button polling', 'Detects PA1 (Call) and PB0 (Answer/Hangup) presses with debouncing'],
]
story.append(make_table(next_steps, col_widths=[4.5 * cm, 10 * cm]))

story.append(P("All of this gets ADDED to the existing MicDAC project. The Phase 3 audio code "
               "(ADC sampling, DAC playback) keeps running unchanged in the background.",
               body))

# ============== Section 8 — Action items ==============
story.append(P("8. Action Items Before Continuing", h1))

action = [
    "Buy 4 push-buttons (4-leg tactile) if not already purchased &mdash; 2 per device.",
    "Wire the 8 connections per Section 3 on Device 1's breadboard.",
    "Power the LilyGO board separately from the STM32 (USB-C charger or 18650 battery for LilyGO; STM32 keeps its USB-C from PC).",
    "In CubeMX: open MicDAC.ioc, add USART1 + 3 GPIO outputs + 2 GPIO inputs as in Section 5.",
    "Generate code, build with 0 errors.",
    "Multimeter check the static GPIO levels (Section 6.4).",
    "Once everything verified &mdash; ready for the firmware code (Phase 5.4 part 2).",
]
for a in action:
    story.append(P("• " + a, bullet))

story.append(Spacer(1, 0.5 * cm))
story.append(P("End of Phase 5.4 hardware/CubeMX setup document. Firmware code will follow in "
               "Phase 5.4 Part 2.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 5.4 — STM32 LTE Setup",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")
"""
Generates the complete project documentation PDF for the
Secure Real-Time Voice Communication System project.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


OUT = "Secure_Voice_Project_Documentation.pdf"

# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'TitleBig', parent=styles['Title'],
    fontSize=22, leading=28, alignment=TA_CENTER,
    textColor=colors.HexColor('#0B3D91'), spaceAfter=12)

subtitle_style = ParagraphStyle(
    'SubTitle', parent=styles['Normal'],
    fontSize=14, leading=18, alignment=TA_CENTER,
    textColor=colors.HexColor('#444444'), spaceAfter=24)

h1 = ParagraphStyle('H1', parent=styles['Heading1'],
    fontSize=16, leading=20, spaceBefore=18, spaceAfter=10,
    textColor=colors.HexColor('#0B3D91'))

h2 = ParagraphStyle('H2', parent=styles['Heading2'],
    fontSize=13, leading=17, spaceBefore=12, spaceAfter=6,
    textColor=colors.HexColor('#1F4E79'))

h3 = ParagraphStyle('H3', parent=styles['Heading3'],
    fontSize=11, leading=14, spaceBefore=8, spaceAfter=4,
    textColor=colors.HexColor('#2E75B6'))

body = ParagraphStyle('Body', parent=styles['Normal'],
    fontSize=10, leading=14, alignment=TA_JUSTIFY,
    spaceAfter=6)

bullet = ParagraphStyle('Bullet', parent=body,
    leftIndent=14, bulletIndent=4, spaceAfter=3)

note = ParagraphStyle('Note', parent=body,
    fontSize=9, textColor=colors.HexColor('#666666'),
    leftIndent=10, spaceAfter=6)

code_style = ParagraphStyle('Code', parent=styles['Code'],
    fontName='Courier', fontSize=8, leading=10,
    leftIndent=8, rightIndent=4,
    backColor=colors.HexColor('#F4F4F4'),
    borderColor=colors.HexColor('#CCCCCC'),
    borderWidth=0.5, borderPadding=4,
    spaceBefore=4, spaceAfter=8)

ascii_style = ParagraphStyle('Ascii', parent=styles['Code'],
    fontName='Courier', fontSize=7.5, leading=9,
    leftIndent=4, rightIndent=4,
    spaceBefore=4, spaceAfter=8)


def P(text, style=body):
    return Paragraph(text, style)


def code(text):
    return Preformatted(text, code_style)


def ascii_block(text):
    return Preformatted(text, ascii_style)


def H1(t): return P(t, h1)
def H2(t): return P(t, h2)
def H3(t): return P(t, h3)


def make_table(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style_cmds = [
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#888888')),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    if header:
        style_cmds += [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B3D91')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ]
    t.setStyle(TableStyle(style_cmds))
    return t


# --------------------------------------------------------------------------
# Page header / footer
# --------------------------------------------------------------------------
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    # Header
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm,
                      "Secure Real-Time Voice Communication System using STM32 and LTE")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    # Footer
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems ECE5206 | Semester 8")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


# --------------------------------------------------------------------------
# Build content
# --------------------------------------------------------------------------
story = []

# ====================== Title page ======================
story.append(Spacer(1, 4 * cm))
story.append(P("Secure Real-Time Voice<br/>Communication System<br/>using STM32 and LTE", title_style))
story.append(Spacer(1, 0.3 * cm))
story.append(P("Project Documentation &amp; Implementation Plan", subtitle_style))
story.append(Spacer(1, 1.5 * cm))

team_data = [
    ['Team Members', 'College ID'],
    ['Rawan Mohamed Ismail', '221006089'],
    ['Malak Wael Ghabn', '221004011'],
    ['Karim Mohamed Ismail', '221004798'],
    ['Omar Mohamed Sayed El-Shafei', '221005236'],
]
story.append(make_table(team_data, col_widths=[10 * cm, 4 * cm]))
story.append(Spacer(1, 1.2 * cm))

meta_data = [
    ['Supervised By', 'Dr. Amr Fahmy'],
    ['Course', 'Embedded Systems ECE5206'],
    ['Semester', 'Semester 8'],
    ['Department', 'Computer Engineering'],
    ['Institution', 'Arab Academy for Science, Technology and Maritime Transport'],
]
story.append(make_table(meta_data, col_widths=[5 * cm, 9 * cm], header=False))

story.append(PageBreak())

# ====================== Section 1: Overview ======================
story.append(H1("1. Project Overview"))

story.append(H2("1.1 Problem Statement"))
story.append(P("Existing voice communication systems either lack hardware-level encryption "
               "or are too computationally expensive for resource-constrained microcontrollers. "
               "This project addresses the need for a low-cost, embedded solution that delivers "
               "real-time encrypted voice communication over LTE, integrating ADC/DAC signal "
               "processing with RSA cryptography on an STM32 microcontroller."))

story.append(H2("1.2 System Goal"))
story.append(P("Build two identical communication nodes (Device A and Device B). Each node "
               "captures voice from a microphone, encrypts it on the STM32, transmits it over "
               "the 4G LTE network to the peer node, where it is decrypted on the peer's STM32 "
               "and played back through a speaker. Both nodes operate in full-duplex mode. "
               "Calls are initiated by phone number through a small relay server, which forwards "
               "the encrypted bytes between the two nodes."))

story.append(H2("1.3 Objectives"))
objectives = [
    "Implement real-time voice capture, ADC conversion, and DAC reconstruction on STM32 with end-to-end latency under 200 ms (excluding network transit).",
    "Integrate RSA-512 + AES-128 hybrid encryption on the STM32 without external processing hardware.",
    "Establish bidirectional encrypted voice transmission over a 4G LTE network using two T-A7608SA-H modules.",
    "Achieve clear audio output with acceptable SNR using MAX9814 (capture) and LM386 (playback) amplification stages.",
]
for o in objectives:
    story.append(P("• " + o, bullet))

story.append(PageBreak())

# ====================== Section 2: BOM ======================
story.append(H1("2. Bill of Materials (BOM)"))
story.append(P("Components for two complete, identical nodes plus shared programming hardware."))

bom_data = [
    ['#', 'Component', 'Qty', 'Unit (LE)', 'Total (LE)'],
    ['1', 'STM32F401RCT6 Black Pill development board', '2', '270.00', '540.00'],
    ['2', 'MAX9814 Electret Microphone Amplifier (AGC)', '2', '230.00', '460.00'],
    ['3', 'MCP4725 12-bit Digital-to-Analog Converter (I²C)', '2', '195.00', '390.00'],
    ['4', 'TRRS 3.5 mm Audio Jack Female AUX Breakout V3.0', '4', '5.00', '20.00'],
    ['5', 'ST-LINK V2 Emulator/Programmer', '1', '140.00', '140.00'],
    ['6', 'LM386 Audio Amplifier Module (200× gain)', '2', '35.00', '70.00'],
    ['7', 'T-A7608SA-H 4G LTE Module', '2', '(supplied)', '—'],
    ['', 'Total Estimated Cost', '', '', '1,620.00 LE'],
]
story.append(make_table(bom_data,
    col_widths=[1 * cm, 7 * cm, 1.5 * cm, 2.5 * cm, 3 * cm]))

story.append(Spacer(1, 0.5 * cm))
story.append(H2("2.1 Component Roles"))
roles = [
    ("STM32F401RCT6 Black Pill (×2)", "Main microcontroller. Handles ADC capture, encryption, DAC playback, and UART communication with the LTE module. Runs at 84 MHz HCLK."),
    ("MAX9814 Microphone Amplifier (×2)", "Electret microphone preamplifier with auto gain control. Outputs an AC-coupled audio signal biased at ~1.25 V into the STM32 ADC."),
    ("MCP4725 DAC (×2)", "External 12-bit I²C DAC. Reconstructs the decrypted digital audio into an analog waveform at 8 kHz sample rate."),
    ("LM386 Audio Amplifier (×2)", "Low-voltage power amplifier. Drives the headphone output from the DAC's low-current signal."),
    ("TRRS 3.5 mm Audio Jacks (×4)", "Standard 4-conductor headphone jacks. Used to connect a TRRS headset (mic + speaker) to each node, providing one-cable audio I/O."),
    ("T-A7608SA-H 4G LTE Module (×2)", "4G LTE modem with TCP/IP stack. Driven over UART using AT commands. Carries encrypted voice packets between the two nodes via the relay server."),
    ("ST-LINK V2 (×1)", "SWD programmer/debugger. Used during development to flash firmware to both Black Pill boards and to debug via breakpoints."),
]
for name, desc in roles:
    story.append(P(f"<b>{name}</b> — {desc}", body))

story.append(PageBreak())

# ====================== Section 3: System Architecture ======================
story.append(H1("3. System Architecture"))

story.append(H2("3.1 High-Level Block Diagram"))
story.append(ascii_block(r"""
       DEVICE A                          [Relay Server]                         DEVICE B
                                          (laptop+ngrok)
   Headset MIC --> MAX9814                     |              MCP4725 -->LM386 --> Headset SPK
       |             |                         |                  ^
       |             v                         |                  |
       |         ADC (8kHz)                    |              DAC (8kHz)
       |             |                         |                  |
       |        RSA + AES Encrypt              |          Decrypt RSA + AES
       |             |                         |                  ^
       |             v                         |                  |
       |     T-A7608 LTE Module ---TCP-----,---+---,----TCP--- T-A7608 LTE Module
       |             |                     |       |                  |
       |             '------> 4G <---------+       +---------> 4G <---'
       |
       '--- the SAME pipeline runs in the OTHER direction at the same time (full-duplex) --->
""".strip()))

story.append(P("Both devices run identical firmware. Each device simultaneously captures and "
               "encrypts outgoing audio while receiving and decrypting incoming audio, producing "
               "full-duplex (two-way) communication."))

story.append(H2("3.2 Why a Relay Server?"))
story.append(P("Both T-A7608 LTE modules connect to the cellular network through carrier-grade "
               "NAT (CGNAT). They are assigned private IP addresses and have <b>no public "
               "address</b>, so they cannot reach each other directly. A small relay server with "
               "a public IP receives connections from both nodes and forwards encrypted bytes "
               "between them."))
story.append(P("<b>Critical:</b> the relay never sees plaintext audio. It only forwards "
               "ciphertext bytes. End-to-end encryption remains on the STM32 nodes, exactly as "
               "production voice apps (WhatsApp, Signal, FaceTime) operate."))

story.append(H2("3.3 Phone-Number-Based Calling Flow"))
flow = [
    "Both nodes boot, bring up LTE data, and connect TCP to the relay's public address.",
    "Each node sends <b>REG &lt;phone&gt;</b> to register its phone number with the relay.",
    "User on Device A presses the Call button → A sends <b>CALL &lt;B's phone&gt;</b>.",
    "Relay sends <b>INC &lt;A's phone&gt;</b> to Device B → B's status LED indicates ringing.",
    "User on Device B presses Answer → B sends <b>ANS</b> → relay sends <b>GO</b> to both ends.",
    "From this point, the TCP channel carries encrypted audio in both directions, transparently forwarded by the relay.",
    "Either side can send <b>HUP</b> to terminate the call.",
]
for i, step in enumerate(flow, 1):
    story.append(P(f"{i}. {step}", bullet))

story.append(PageBreak())

# ====================== Section 4: Hardware Configuration ======================
story.append(H1("4. Hardware Configuration"))

story.append(H2("4.1 STM32F401RCT6 Pin Assignment"))
story.append(P("Final pin map per node. All other pins are unused and can be ignored."))

pin_data = [
    ['Pin', 'Function', 'Connects to'],
    ['PA0', 'ADC1_IN0', 'MAX9814 OUT'],
    ['PA2', 'USART2_TX', 'USB-TTL adapter RX (optional debug log)'],
    ['PA3', 'USART2_RX', 'USB-TTL adapter TX (optional debug log)'],
    ['PA9', 'USART1_TX', 'T-A7608 LTE module RXD'],
    ['PA10', 'USART1_RX', 'T-A7608 LTE module TXD'],
    ['PB6', 'I2C1_SCL', 'MCP4725 SCL'],
    ['PB7', 'I2C1_SDA', 'MCP4725 SDA'],
    ['PA13', 'SWDIO', 'ST-LINK SWDIO (programming)'],
    ['PA14', 'SWCLK', 'ST-LINK SWCLK (programming)'],
    ['PC13', 'GPIO output', 'Onboard status LED'],
    ['PH0/PH1', 'HSE crystal', '25 MHz crystal (already on Black Pill)'],
    ['3V3 / GND', 'Power', '3.3 V devices: MAX9814, MCP4725'],
    ['5V (VBUS)', 'Power', 'LM386 module VCC'],
]
story.append(make_table(pin_data, col_widths=[2.5 * cm, 3 * cm, 9 * cm]))

story.append(H2("4.2 Power Distribution"))
story.append(P("<b>Critical rule:</b> the Black Pill's onboard 3.3 V regulator can supply only "
               "~300 mA — enough for the MAX9814 and MCP4725, but <b>not enough for the T-A7608 "
               "LTE module</b>, which can pull bursts of up to 2 A during transmission. The LTE "
               "module needs its own dedicated 5 V → 3.8 V supply (or a Li-ion battery with a "
               "buck regulator). All devices must share a common ground."))

story.append(ascii_block(r"""
   +--------------+     +-----------------+     +-----------------+
   | USB-PC (5V)  |     | USB-C charger   |     | 5V 2A regulator |
   |              |     | or 5V 2A PSU    |     | -> 3.8V to LTE  |
   +------+-------+     +--------+--------+     +--------+--------+
          |                      |                       |
          v                      v                       v
   +--------------+      [3.3V rail]                +-----------+
   | Black Pill   |---> MAX9814 VDD                 | T-A7608   |
   | onboard reg  |---> MCP4725 VDD                 | 4G module |
   +--------------+      |                          +-----+-----+
          |              |                                |
          |              | [5V VBUS rail] -> LM386 VCC    |
          |              |                                |
          +-------+------+--- COMMON GROUND ---+----------+
                  |
            (all GNDs physically tied together: STM32, MAX9814, MCP4725,
             LM386, T-A7608, all power supplies)
""".strip()))

story.append(P("<b>Decoupling:</b> place a 470 µF electrolytic capacitor in parallel with a "
               "100 nF ceramic capacitor across the LTE module's power input, as physically "
               "close to the module's VBAT pin as possible. This absorbs the inrush current "
               "during 4G transmit bursts and prevents brown-outs of the rest of the system."))

story.append(PageBreak())

# ====================== Section 4.3-4.5: Wiring details ======================
story.append(H2("4.3 Microphone Path (MAX9814 → STM32)"))
story.append(ascii_block(r"""
   MAX9814 module                  Black Pill
     VDD ---------------------->  3V3
     GND ---------------------->  GND
     OUT ---------------------->  PA0  (ADC1_IN0)
     GAIN -- floating (default 60 dB) or tie to VDD (40 dB) / GND (50 dB)
     A/R  -- floating (default attack/release timing)
""".strip()))
story.append(P("The MAX9814 OUT pin idles at approximately 1.25 V (its internal mid-rail bias). "
               "With ADC reference voltage of 3.3 V, the digital midpoint code is ≈ 96 (out of "
               "255 in 8-bit mode). Firmware subtracts this offset to get a signed audio sample."))

story.append(H2("4.4 Speaker Path (STM32 → MCP4725 → LM386 → Headset)"))
story.append(ascii_block(r"""
   MCP4725 module                  Black Pill
     VDD ---------------------->  3V3
     GND ---------------------->  GND
     SCL ---------------------->  PB6  (I2C1_SCL)
     SDA ---------------------->  PB7  (I2C1_SDA)
     A0  ---- tie to GND  (sets I2C address = 0x60)
     OUT ---------------------->  LM386 module IN

   LM386 module                    TRRS jack breakout
     VCC ----> 5V  (NOT 3.3V - LM386 needs >=4V)
     GND ----> GND
     IN  ----> from MCP4725 OUT
     +   ----> TRRS Tip   (Left audio)
     +   ----> TRRS Ring1 (Right audio)  -- tie L=R for mono
     GND ----> TRRS Sleeve (or Ring2, depending on wiring standard)
""".strip()))
story.append(P("<b>MCP4725 pull-ups:</b> most breakouts already include 4.7 kΩ pull-ups on SCL "
               "and SDA. Do not add additional pull-ups. If your specific module lacks them, add "
               "a single pair of 4.7 kΩ resistors from each line to 3.3 V."))
story.append(P("<b>LM386 gain:</b> if your LM386 module has a gain potentiometer, start with it "
               "fully down. The MCP4725 + LM386 combination is loud enough to clip badly at full "
               "gain."))

story.append(H2("4.5 LTE Module (T-A7608SA-H) Wiring"))
story.append(ascii_block(r"""
   T-A7608 module                  Black Pill
     VBAT (3.3-4.3V) ---------->  dedicated 5V->3.8V buck or Li-ion
     GND ---------------------->  GND  (common with STM32 GND)
     TXD ---------------------->  PA10 (USART1_RX)
     RXD ---------------------->  PA9  (USART1_TX)
     PWRKEY ------------------->  pulse low >=1s to power on (button or GPIO+transistor)
     GND ---------------------->  GND  (a second ground wire - redundant at 2A)
""".strip()))
story.append(P("<b>UART logic levels:</b> the T-A7608 UART operates at 1.8 V or 3.3 V depending "
               "on the breakout board. Verify before connecting. The STM32 outputs 3.3 V — if "
               "the LTE module requires 1.8 V, a level shifter is needed on the STM32 → LTE "
               "direction."))

story.append(H2("4.6 TRRS Headset Wiring (CTIA Standard)"))
story.append(P("A standard Android/iPhone TRRS headset uses the CTIA wiring standard:"))
trrs_data = [
    ['Plug Section', 'Signal', 'Wire to'],
    ['Tip', 'Left audio (output)', 'LM386 output'],
    ['Ring 1', 'Right audio (output)', 'LM386 output (same line, mono)'],
    ['Ring 2', 'Ground', 'Common GND'],
    ['Sleeve', 'Microphone (input)', 'MAX9814 input pad (or leave floating to use onboard mic)'],
]
story.append(make_table(trrs_data, col_widths=[3 * cm, 5 * cm, 6.5 * cm]))
story.append(P("<b>Note:</b> if you use the onboard electret microphone on the MAX9814 breakout "
               "for the first prototype, leave the TRRS Sleeve disconnected. You only need the "
               "Tip + Ring 1 + Ring 2 (GND) connections for headphone output. This is simpler "
               "for initial bring-up."))

story.append(PageBreak())

# ====================== Section 5: STM32CubeMX Configuration ======================
story.append(H1("5. STM32CubeMX Configuration"))
story.append(P("Step-by-step procedure to configure the project in STM32CubeMX (or via the "
               "STM32 VS Code Extension). Follow this top-to-bottom for a fresh project."))

story.append(H2("5.1 Project Creation"))
steps = [
    "Launch STM32CubeMX → File → New Project.",
    "Search <b>STM32F401RCTx</b> → select your row → Start Project.",
    "You land on the Pinout &amp; Configuration tab with a chip diagram.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(H2("5.2 Clock Source (RCC + SYS)"))
steps = [
    "System Core → RCC → High Speed Clock (HSE): <b>Crystal/Ceramic Resonator</b>.",
    "System Core → RCC → Low Speed Clock (LSE): <b>Disable</b>.",
    "System Core → SYS → Debug: <b>Serial Wire</b>. (Critical — without this, SWD programming fails after the first flash.)",
    "System Core → SYS → Timebase Source: <b>SysTick</b> (default).",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(H2("5.3 Clock Configuration Tab — 84 MHz HCLK"))
clock_data = [
    ['Field', 'Value'],
    ['Input Frequency', '25 MHz'],
    ['PLL Source Mux', 'HSE'],
    ['PLLM', '/25  (→ 1 MHz reference)'],
    ['PLLN', '×336 (→ 336 MHz VCO)'],
    ['PLLP', '/4   (→ 84 MHz SYSCLK)'],
    ['PLLQ', '/7   (don\'t care, no USB)'],
    ['System Clock Mux', 'PLLCLK'],
    ['AHB Prescaler', '/1  (HCLK = 84 MHz)'],
    ['APB1 Prescaler', '/2  (PCLK1 = 42 MHz, TIM clk = 84 MHz)'],
    ['APB2 Prescaler', '/1  (PCLK2 = 84 MHz, TIM clk = 84 MHz)'],
    ['Voltage Scaling', 'Scale 1'],
    ['Flash Latency', '2 WS  (auto-set)'],
]
story.append(make_table(clock_data, col_widths=[5 * cm, 9 * cm]))
story.append(P("<i>Shortcut: type 84 in the HCLK field and press Enter. CubeMX auto-solves the "
               "PLL chain.</i>", note))

story.append(H2("5.4 TIM2 — 8 kHz ADC Trigger"))
steps = [
    "Timers → TIM2 → Clock Source: <b>Internal Clock</b>.",
    "Parameter Settings → Prescaler (PSC): <b>83</b>.",
    "Parameter Settings → Counter Period (ARR): <b>124</b>.",
    "Parameter Settings → auto-reload preload: <b>Enable</b>.",
    "Trigger Output → Master/Slave Mode: <b>Disable</b>.",
    "Trigger Output → Trigger Event Selection TRGO: <b>Update Event</b>.",
    "Math: 84 MHz / ((83+1) × (124+1)) = 8000 Hz exactly.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(H2("5.5 TIM3 — 8 kHz DAC Playback Tick"))
steps = [
    "Timers → TIM3 → Clock Source: <b>Internal Clock</b>.",
    "Parameter Settings → Prescaler: <b>83</b>, Counter Period: <b>124</b>.",
    "NVIC Settings → enable <b>TIM3 global interrupt</b>.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(PageBreak())

story.append(H2("5.6 ADC1 — 8-bit, Timer-Triggered, DMA Circular"))
steps = [
    "Analog → ADC1 → check <b>IN0</b> (PA0 turns green).",
    "Parameter Settings → Clock Prescaler: <b>PCLK2 div 4</b> (21 MHz; ADC max is 36 MHz).",
    "Parameter Settings → Resolution: <b>8 bits</b>.",
    "Parameter Settings → Continuous Conversion Mode: <b>Disabled</b>.",
    "Parameter Settings → DMA Continuous Requests: <b>Enabled</b>.",
    "External Trigger Conversion Source: <b>Timer 2 Trigger Out event</b>.",
    "External Trigger Conversion Edge: <b>Rising edge</b>.",
    "Channel Sampling Time: 15 Cycles.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(P("<b>DMA Settings tab → Add → ADC1:</b>"))
dma_data = [
    ['Field', 'Value'],
    ['Stream', 'DMA2 Stream 0 (auto)'],
    ['Direction', 'Peripheral To Memory'],
    ['Mode', 'Circular'],
    ['Priority', 'High'],
    ['Use FIFO', 'Disabled (Direct mode)'],
    ['Increment Address — Peripheral', 'Unchecked'],
    ['Increment Address — Memory', 'Checked'],
    ['Peripheral Data Width', 'Byte'],
    ['Memory Data Width', 'Byte'],
]
story.append(make_table(dma_data, col_widths=[6.5 * cm, 7.5 * cm]))
story.append(P("<b>NVIC Settings tab:</b> enable <i>DMA2 stream0 global interrupt</i> and "
               "<i>ADC1 global interrupt</i>."))

story.append(H2("5.7 I2C1 — MCP4725 at 400 kHz Fast Mode"))
steps = [
    "Connectivity → I2C1 → Mode: <b>I2C</b>.",
    "Parameter Settings → I2C Speed Mode: <b>Fast Mode</b>.",
    "Parameter Settings → I2C Clock Speed (Hz): <b>400000</b>.",
    "Parameter Settings → Fast Mode Duty Cycle: 2.",
    "Pins auto-assign: PB6 = SCL, PB7 = SDA.",
    "(Optional) Add I2C1_TX DMA — Normal mode, Memory→Peripheral, byte width.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(H2("5.8 USART1 — LTE Module (115200 baud)"))
steps = [
    "Connectivity → USART1 → Mode: <b>Asynchronous</b>.",
    "Parameter Settings: Baud Rate <b>115200</b>, Word Length 8 bits, Parity None, Stop Bits 1.",
    "Hardware Flow Control: None (enable RTS/CTS only if your LTE module wiring uses them).",
    "NVIC Settings → enable <b>USART1 global interrupt</b>.",
    "Pins auto-assign: PA9 = TX, PA10 = RX.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(H2("5.9 USART2 — Optional Debug Console"))
steps = [
    "Connectivity → USART2 → Mode: <b>Asynchronous</b>, baud 115200, 8N1.",
    "NVIC: leave disabled (use blocking HAL_UART_Transmit for printf-style logging).",
    "Pins auto-assign: PA2 = TX, PA3 = RX. Wire PA2 to a USB-TTL adapter for live debug logs.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(H2("5.10 GPIO — Status LED on PC13"))
steps = [
    "On the chip diagram, click <b>PC13</b> → select <b>GPIO_Output</b>.",
    "GPIO config: output level High (LED is active-low on Black Pill), Push-Pull, Low speed, no pull.",
    "User Label: <b>LED</b>.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(H2("5.11 NVIC Priority Table"))
nvic_data = [
    ['Interrupt', 'Preempt Priority', 'Reason'],
    ['DMA2 Stream0 (ADC)', '0 (highest)', 'Audio capture must never be starved'],
    ['I2C1 EV / I2C1 ER', '1', 'Audio playback timing'],
    ['ADC1', '2', 'Conversion complete signaling'],
    ['TIM3', '2', 'Playback tick'],
    ['USART1', '3', 'LTE bytes — least time-critical'],
]
story.append(make_table(nvic_data, col_widths=[5 * cm, 4 * cm, 5 * cm]))

story.append(H2("5.12 Project Manager Settings"))
steps = [
    "Project Name: <b>SecureVoice</b>.",
    "Toolchain / IDE: <b>CMake</b> (for VS Code) or <b>STM32CubeIDE</b>.",
    "Linker Settings → Minimum Heap Size: <b>0x800</b>, Minimum Stack Size: <b>0x800</b>.",
    "Code Generator → tick <b>Generate peripheral initialization as a pair of '.c/.h' files per peripheral</b>.",
    "Click <b>GENERATE CODE</b>.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(PageBreak())

# ====================== Section 6: Software Architecture ======================
story.append(H1("6. Software Architecture"))

story.append(H2("6.1 Module Breakdown"))
modules = [
    ("ADC Driver", "Continuously samples PA0 at 8 kHz via TIM2-triggered ADC + DMA into a circular ping-pong buffer. Generates HalfCplt and FullCplt callbacks signaling buffer halves are ready for processing."),
    ("DAC Driver", "TIM3 ISR fires at 8 kHz and pushes the next playback sample to the MCP4725 over I²C using interrupt-driven transfers (HAL_I2C_Master_Transmit_IT)."),
    ("Crypto Module", "RSA-512 (PKCS#1 v1.5) for the initial session-key exchange. AES-128-CTR for bulk audio encryption using the exchanged key. RSA-only audio is not real-time feasible at 8 kHz on the F401."),
    ("LTE Driver", "AT-command state machine over USART1. Brings up GPRS, opens a TCP connection to the relay server, performs REG/CALL/ANS handshake, then enters streaming mode."),
    ("Audio Buffer Manager", "Coordinates the four producer/consumer flows: ADC→encrypt→TX, RX→decrypt→DAC. Uses ping-pong buffers to decouple sample timing from variable-latency processing."),
    ("Call State Machine", "Tracks IDLE → REGISTERED → CALLING/RINGING → TALKING → IDLE. Drives the status LED to indicate state to the user."),
]
for name, desc in modules:
    story.append(P(f"<b>{name}</b> — {desc}", body))

story.append(H2("6.2 Data Flow per Audio Frame"))
story.append(ascii_block(r"""
   [TX path]  Mic --> MAX9814 --> ADC@8kHz --> ping-pong half --> AES encrypt
              --> UART TX --> T-A7608 --> TCP --> Relay --> peer T-A7608
              --> peer UART RX --> peer AES decrypt --> peer ping-pong half
              --> MCP4725 @ 8kHz --> LM386 --> Speaker

   [RX path]  Symmetric, runs in parallel on the same hardware.
""".strip()))

story.append(H2("6.3 Hybrid Encryption Rationale"))
story.append(P("Pure RSA-512 on every audio block cannot keep up with 8 kHz audio on a "
               "Cortex-M4 at 84 MHz. Decryption alone takes 40–100 ms per 53-byte block; "
               "8 kHz audio requires processing roughly 150 blocks per second. The math "
               "simply does not work out."))
story.append(P("<b>Solution:</b> use RSA only for what it is designed for — exchanging a small "
               "secret key. At session start, Device A generates a random 16-byte AES-128 key, "
               "encrypts it with Device B's RSA public key, and sends it. Device B decrypts the "
               "key with its RSA private key. From then on, both sides use AES-128-CTR for the "
               "bulk audio stream — sub-millisecond per block on the M4."))
story.append(P("This is exactly how TLS, Signal, and every other production secure-comms system "
               "works (\"hybrid encryption\"). RSA = key exchange. AES = data."))

story.append(H2("6.4 Buffer Sizing"))
buf_data = [
    ['Parameter', 'Value', 'Notes'],
    ['Sample rate', '8 kHz', '8000 samples/sec mono, voice-grade'],
    ['Sample width', '8 bits', 'unsigned, mid-bias 0x60 due to MAX9814'],
    ['Audio frame size', '128 samples', '16 ms per frame — standard voice frame'],
    ['Ping-pong total', '256 bytes', 'two halves of 128 each'],
    ['AES block size', '16 bytes', 'AES-128 native block'],
    ['RSA modulus', '64 bytes', 'RSA-512 = 64 bytes ciphertext'],
    ['Frames per second', '~62.5', '8000 / 128'],
    ['LTE bandwidth', '~10 KB/s', '8 kHz × 1 byte + framing overhead'],
]
story.append(make_table(buf_data, col_widths=[4 * cm, 3 * cm, 7 * cm]))

story.append(PageBreak())

# ====================== Section 7: Relay Server ======================
story.append(H1("7. Relay Server (Laptop + ngrok)"))
story.append(P("The relay forwards encrypted bytes between the two devices. It runs on the "
               "developer's laptop during testing/demo and is exposed to the public internet via "
               "ngrok's free TCP tunnel."))

story.append(H2("7.1 Protocol Specification"))
story.append(P("All control messages are line-based ASCII terminated by '\\n'. After the GO "
               "message, the connection switches to raw byte forwarding mode."))
proto_data = [
    ['Direction', 'Message', 'Meaning'],
    ['Client → Server', 'REG <phone>', 'Register this connection with a phone number'],
    ['Server → Client', 'OK', 'Registration accepted'],
    ['Server → Client', 'ERR <reason>', 'Command failed'],
    ['Client → Server', 'CALL <peer_phone>', 'Initiate a call to peer'],
    ['Server → Client', 'RING', 'Your CALL was accepted, peer is ringing'],
    ['Server → Client', 'INC <caller>', '(unsolicited) Someone is calling you'],
    ['Client → Server', 'ANS', 'Pick up an incoming call'],
    ['Server → Client', 'GO', 'Both ends now in audio-streaming mode'],
    ['Client → Server', 'HUP', 'End the current call'],
    ['Server → Client', 'PEER_HUP', 'Peer ended the call'],
    ['Server → Client', 'PEER_GONE', 'Peer disconnected unexpectedly'],
]
story.append(make_table(proto_data, col_widths=[3.5 * cm, 4 * cm, 7 * cm]))

story.append(H2("7.2 Server Code (Python 3, asyncio)"))
story.append(P("Save as <b>relay.py</b> on the laptop. Run with <code>python relay.py</code>. "
               "Listens on TCP port 5555. No external dependencies."))

server_code = '''import asyncio

CLIENTS = {}   # phone_number -> Session

class Session:
    def __init__(self, r, w):
        self.r = r
        self.w = w
        self.phone = None
        self.peer = None
        self.state = "IDLE"
        self.kick = asyncio.Event()

    async def send(self, line):
        self.w.write((line + "\\n").encode())
        await self.w.drain()

async def handle_command(s, line):
    parts = line.split(maxsplit=1)
    if not parts: return
    verb = parts[0].upper()
    arg  = parts[1] if len(parts) > 1 else None

    if verb == "REG" and s.state == "IDLE":
        if not arg:           return await s.send("ERR no_phone")
        if arg in CLIENTS:    return await s.send("ERR taken")
        s.phone = arg; s.state = "REGD"; CLIENTS[arg] = s
        await s.send("OK")
        print(f"+ registered {arg}")

    elif verb == "CALL" and s.state == "REGD":
        peer = CLIENTS.get(arg)
        if not peer or peer.state != "REGD":
            return await s.send("ERR unavail")
        s.peer = peer; peer.peer = s
        s.state = "CALLING"; peer.state = "RINGING"
        await s.send("RING")
        await peer.send(f"INC {s.phone}")
        peer.kick.set()

    elif verb == "ANS" and s.state == "RINGING":
        s.state = "TALK"; s.peer.state = "TALK"
        await s.send("GO"); await s.peer.send("GO")
        s.peer.kick.set()

    elif verb == "HUP":
        if s.peer:
            await s.peer.send("PEER_HUP")
            s.peer.peer = None; s.peer.state = "REGD"; s.peer.kick.set()
        s.peer = None; s.state = "REGD"
        await s.send("OK")
    else:
        await s.send(f"ERR {verb}_in_{s.state}")

async def setup_phase(s):
    while s.state not in ("TALK", "GONE"):
        rt = asyncio.create_task(s.r.readline())
        kt = asyncio.create_task(s.kick.wait())
        done, pending = await asyncio.wait([rt, kt],
            return_when=asyncio.FIRST_COMPLETED)
        for p in pending: p.cancel()
        if kt in done:
            s.kick.clear(); continue
        line = rt.result()
        if not line:
            s.state = "GONE"; return
        await handle_command(s, line.decode(errors="replace").strip())

async def talk_phase(s):
    while s.state == "TALK" and s.peer and s.peer.state == "TALK":
        data = await s.r.read(256)
        if not data: break
        try:
            s.peer.w.write(data)
            await s.peer.w.drain()
        except (ConnectionResetError, BrokenPipeError):
            break

async def handle(r, w):
    s = Session(r, w)
    print(f"+ conn {w.get_extra_info('peername')}")
    try:
        await setup_phase(s)
        if s.state == "TALK":
            await talk_phase(s)
    finally:
        if s.phone in CLIENTS: del CLIENTS[s.phone]
        if s.peer:
            try: s.peer.w.write(b"PEER_GONE\\n"); await s.peer.w.drain()
            except: pass
            s.peer.peer = None; s.peer.state = "REGD"; s.peer.kick.set()
        try: w.close(); await w.wait_closed()
        except: pass

async def main():
    srv = await asyncio.start_server(handle, "0.0.0.0", 5555)
    print(f"relay listening on {srv.sockets[0].getsockname()}")
    async with srv:
        await srv.serve_forever()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\\nbye")
'''
story.append(code(server_code))

story.append(H2("7.3 Exposing the Relay via ngrok"))
ngrok_steps = [
    "Sign up at ngrok.com (free tier).",
    "Download the Windows zip → unzip → single ngrok.exe.",
    "Add your auth-token: <code>ngrok config add-authtoken &lt;your_token&gt;</code>",
    "Start the tunnel (separate terminal, with relay.py also running): <code>ngrok tcp 5555</code>",
    "ngrok prints a public address such as <b>2.tcp.ngrok.io:14732</b>. This is the host:port the LTE devices will connect to.",
    "<b>Note:</b> the free tier assigns a new address each restart. Leave the tunnel running from demo morning.",
]
for s in ngrok_steps:
    story.append(P("• " + s, bullet))

story.append(H2("7.4 Local Testing (no STM32 needed)"))
story.append(P("The relay can be fully validated before any embedded code exists. Open three "
               "terminals on the laptop:"))
test_steps = [
    "Terminal 1: <code>python relay.py</code>",
    "Terminal 2: <code>telnet localhost 5555</code> → type <code>REG 01000000001</code> → expect <code>OK</code>.",
    "Terminal 3: <code>telnet localhost 5555</code> → type <code>REG 01000000002</code> → expect <code>OK</code>.",
    "Terminal 2: <code>CALL 01000000002</code> → expect <code>RING</code>; Terminal 3 should see <code>INC 01000000001</code>.",
    "Terminal 3: <code>ANS</code> → both terminals see <code>GO</code>.",
    "Now anything typed in either terminal appears in the other — bytes are forwarded transparently.",
]
for s in test_steps:
    story.append(P("• " + s, bullet))

story.append(PageBreak())

# ====================== Section 8: Bring-up plan ======================
story.append(H1("8. Incremental Bring-up Plan (Milestones)"))
story.append(P("Build and verify the system in slices. Do <b>not</b> wire all subsystems and "
               "then attempt to debug the whole thing at once — the project will not converge "
               "that way. Each milestone is independently testable."))

milestones = [
    ("M1: LED Blink",
     "External LED on PA1 with 330 Ω resistor. Verifies the toolchain end-to-end (driver, IDE, ST-Link, board, GPIO config, clock tree).",
     "LED blinks at 1 Hz."),
    ("M2: ADC Visualizer",
     "MAX9814 → PA0 + USB-TTL adapter on USART2. Firmware streams ADC sample min/max to the PC terminal.",
     "Numbers on terminal change visibly when whistling/speaking into the mic."),
    ("M3: Local Audio Loopback",
     "Add MCP4725 + LM386 + TRRS jack. Mic samples are written directly to the DAC at 8 kHz with no encryption and no LTE.",
     "Hear yourself in the headset with ~32 ms delay. Proves the entire analog/digital audio chain."),
    ("M4: LTE Module AT Sanity",
     "Wire T-A7608 to USB-TTL adapter directly (not yet to STM32). Manually issue AT+CIPSTART to a public TCP echo server.",
     "Module powers on, registers on the network, opens TCP, echoes data."),
    ("M5: STM32-Driven TCP Echo",
     "Connect T-A7608 to STM32 USART1. Firmware automates the AT sequence and echoes 100 bytes/s of dummy data through the relay.",
     "Bytes loop back via the relay; first end-to-end network proof."),
    ("M6: Two-Node Plain Audio over LTE",
     "Both devices fully assembled. Audio flows mic→ADC→LTE→relay→LTE→DAC→speaker, no encryption yet.",
     "First two-way voice between the devices, even if quality is rough."),
    ("M7: Add RSA + AES Hybrid Encryption",
     "Drop in mbedTLS. Pre-share RSA keypairs, exchange AES session key at call setup, encrypt audio frames with AES-CTR.",
     "All voice traffic on the LTE link is unintelligible to a packet sniffer; decoded perfectly at the peer."),
    ("M8: Phone-Number Call Setup + Polish",
     "Add the REG/CALL/ANS state machine, status LED, push-button to initiate/answer calls.",
     "User experience matches a real phone call."),
]
for name, what, success in milestones:
    story.append(H3(name))
    story.append(P(f"<b>What:</b> {what}", body))
    story.append(P(f"<b>Success criteria:</b> {success}", body))

story.append(PageBreak())

# ====================== Section 9: Code skeleton ======================
story.append(H1("9. Firmware Code Skeleton"))
story.append(P("Reference snippets to drop into the CubeMX-generated <b>main.c</b> at the "
               "marked USER CODE regions. These are starting points — Milestones 2, 3, and 5 "
               "use progressively larger subsets."))

story.append(H2("9.1 Variables and Buffers"))
story.append(code('''/* USER CODE BEGIN PD */
#define AUDIO_BUFFER_SIZE   256        /* total ping-pong, samples */
#define HALF_BUFFER_SIZE    (AUDIO_BUFFER_SIZE / 2)
#define LTE_RX_BUFFER_SIZE  512
#define LTE_TX_BUFFER_SIZE  512
#define MCP4725_ADDR        (0x60 << 1)
/* USER CODE END PD */

/* USER CODE BEGIN PV */
uint8_t  adc_buffer[AUDIO_BUFFER_SIZE];   /* mic capture (DMA target) */
uint8_t  dac_buffer[AUDIO_BUFFER_SIZE];   /* speaker source           */

volatile uint8_t adc_half_ready = 0;
volatile uint8_t adc_full_ready = 0;
volatile uint16_t dac_play_idx  = 0;

uint8_t lte_rx_buffer[LTE_RX_BUFFER_SIZE];
uint8_t lte_tx_buffer[LTE_TX_BUFFER_SIZE];
volatile uint8_t lte_rx_ready = 0;
/* USER CODE END PV */'''))

story.append(H2("9.2 Peripheral Start-up"))
story.append(code('''/* USER CODE BEGIN 2 */
HAL_UART_Receive_IT(&huart1, lte_rx_buffer, LTE_RX_BUFFER_SIZE);
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, AUDIO_BUFFER_SIZE);
HAL_TIM_Base_Start(&htim2);
HAL_TIM_Base_Start_IT(&htim3);
/* USER CODE END 2 */'''))

story.append(H2("9.3 Callbacks"))
story.append(code('''/* USER CODE BEGIN 4 */
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *h) {
    if (h->Instance == ADC1) adc_half_ready = 1;
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *h) {
    if (h->Instance == ADC1) adc_full_ready = 1;
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *h) {
    if (h->Instance == USART1) {
        lte_rx_ready = 1;
        HAL_UART_Receive_IT(&huart1, lte_rx_buffer, LTE_RX_BUFFER_SIZE);
    }
}

/* TIM3 @ 8 kHz: push next sample to MCP4725 over I2C */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM3) {
        uint16_t v12 = ((uint16_t)dac_buffer[dac_play_idx]) << 4;
        uint8_t pkt[2] = {
            (uint8_t)((v12 >> 8) & 0x0F),
            (uint8_t)(v12 & 0xFF)
        };
        HAL_I2C_Master_Transmit_IT(&hi2c1, MCP4725_ADDR, pkt, 2);
        dac_play_idx = (dac_play_idx + 1) % AUDIO_BUFFER_SIZE;
    }
}
/* USER CODE END 4 */'''))

story.append(H2("9.4 Main Loop"))
story.append(code('''/* USER CODE BEGIN WHILE */
while (1)
{
    /* TX: encrypt completed half-buffer & ship to LTE */
    if (adc_half_ready) {
        adc_half_ready = 0;
        Encrypt_Frame(&adc_buffer[0], HALF_BUFFER_SIZE, lte_tx_buffer);
        LTE_Send(lte_tx_buffer, /*ciphertext_len*/);
    }
    if (adc_full_ready) {
        adc_full_ready = 0;
        Encrypt_Frame(&adc_buffer[HALF_BUFFER_SIZE], HALF_BUFFER_SIZE, lte_tx_buffer);
        LTE_Send(lte_tx_buffer, /*ciphertext_len*/);
    }

    /* RX: decrypt incoming frame & write into the playback half */
    if (lte_rx_ready) {
        lte_rx_ready = 0;
        Decrypt_Frame(lte_rx_buffer, /*len*/, dac_buffer + /*write_offset*/);
    }

    HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
}
/* USER CODE END WHILE */'''))

story.append(H2("9.5 LTE AT-Command Bring-up Sketch"))
story.append(code('''static void LTE_Init(void) {
    HAL_Delay(3000);  /* boot delay */

    LTE_AT("AT",                                      1000);
    LTE_AT("ATE0",                                    1000);
    LTE_AT("AT+CPIN?",                                2000);
    LTE_AT("AT+CSQ",                                  1000);
    LTE_AT("AT+CGATT=1",                             10000);
    LTE_AT("AT+CGDCONT=1,\\"IP\\",\\"<YOUR_APN>\\"",  2000);
    LTE_AT("AT+CGACT=1,1",                           15000);
    LTE_AT("AT+CIPMUX=0",                             2000);
    LTE_AT("AT+CIPSTART=\\"TCP\\",\\"<NGROK_HOST>\\","
           "<NGROK_PORT>",                           20000);
    /* Expect "CONNECT OK". Then: */
    LTE_Write("REG <YOUR_PHONE>\\r\\n");
    /* Wait for "OK" → ready for CALL / INC */
}'''))

story.append(PageBreak())

# ====================== Section 10: Timeline ======================
story.append(H1("10. Development Timeline"))
timeline_data = [
    ['Week', 'Phase', 'Deliverable'],
    ['9', 'Planning, procurement, environment setup',
     'Toolchain ready; all components in hand; LED blink working (M1)'],
    ['10', 'Hardware assembly & ADC capture',
     'MAX9814 wired; ADC visualizer working (M2); MCP4725+LM386 wired'],
    ['11', 'Audio pipeline & local loopback',
     'Mic→ADC→DAC→speaker loopback working (M3)'],
    ['12', 'LTE integration',
     'AT-command bring-up (M4); STM32-driven TCP echo (M5); plain audio over LTE (M6)'],
    ['13', 'Encryption layer',
     'mbedTLS integrated; RSA+AES hybrid encryption working (M7)'],
    ['14', 'Polish & call control',
     'Phone-number call setup, status LED, push buttons (M8)'],
    ['15', 'Final testing & demonstration',
     'Reliability testing, latency measurement, demo prep, video backup'],
]
story.append(make_table(timeline_data, col_widths=[1.5 * cm, 5 * cm, 7.5 * cm]))

story.append(H2("10.1 Latency Budget"))
lat_data = [
    ['Stage', 'Estimated Latency'],
    ['ADC fill (one half-buffer at 8 kHz × 128 samples)', '16 ms'],
    ['AES-128-CTR encrypt of 128 bytes', '< 1 ms'],
    ['UART → LTE module → 4G transmit', '50–150 ms (network)'],
    ['Relay forwarding', '< 5 ms'],
    ['4G receive → UART → STM32 RX', '50–150 ms (network)'],
    ['AES decrypt of 128 bytes', '< 1 ms'],
    ['DAC playback fill', '16 ms'],
    ['Estimated one-way mouth-to-ear', '~150–350 ms'],
]
story.append(make_table(lat_data, col_widths=[10 * cm, 4 * cm]))
story.append(P("The cellular network dominates the latency budget. The encryption objective "
               "(under 200 ms) refers to the on-device processing path, which is comfortably "
               "achieved by the hybrid scheme."))

story.append(PageBreak())

# ====================== Section 11: Risk register ======================
story.append(H1("11. Risk Register & Mitigations"))
risks = [
    ("LTE module brown-out during transmit",
     "T-A7608 pulls up to 2 A in bursts; weak supply causes the entire system to reset.",
     "Use a dedicated 5 V/2 A regulator for the LTE module. Add 470 µF + 100 nF decoupling at its power pin."),
    ("ADC offset / clipping",
     "MAX9814 output sits at ~1.25 V; ADC reads ~96/255 at silence. Naive playback sounds garbled.",
     "Subtract 96 from sample before playback or use signed audio internally."),
    ("Pure RSA cannot keep up with audio",
     "RSA-512 decrypt = 40-100 ms per block; voice needs 150 blocks/sec.",
     "Use hybrid: RSA for key exchange only, AES-128-CTR for bulk audio."),
    ("CGNAT prevents direct connection",
     "Two LTE modules cannot directly TCP-connect to each other.",
     "Relay server (laptop + ngrok). Architecturally identical to all real voice apps."),
    ("ngrok address changes on restart",
     "Free tier reassigns the public address each time the tunnel restarts.",
     "Start the tunnel once on demo morning and leave it running. Have the firmware accept host:port via UART or a config menu instead of hard-coding."),
    ("Demo failure on the day",
     "Live cellular and audio demos are notoriously fragile.",
     "Record a working video demo as backup. Have the milestone test apps available so individual subsystems can be shown if the full integrated demo fails."),
    ("RSA-512 is cryptographically weak",
     "RSA-512 is broken in practice; not suitable for real-world use.",
     "Acknowledge this explicitly in the report. The objective is to demonstrate the embedded encryption pipeline, not to provide production-grade security. The same code design extends to RSA-2048 by changing only key length constants."),
    ("Data plan exhaustion",
     "Continuous voice consumes ~36 MB/hour of data per node.",
     "Use a SIM with at least 1 GB/month data; estimate 10-30 hours of demo testing."),
]
risk_data = [['Risk', 'Cause', 'Mitigation']]
for r in risks:
    risk_data.append(list(r))
story.append(make_table(risk_data, col_widths=[3.5 * cm, 5 * cm, 5.5 * cm]))

story.append(PageBreak())

# ====================== Section 12: Glossary ======================
story.append(H1("12. Glossary"))
glossary = [
    ("ADC", "Analog-to-Digital Converter. Samples analog voltage into digital codes."),
    ("AES-128-CTR", "Advanced Encryption Standard with 128-bit key in Counter mode. Symmetric stream cipher; fast on Cortex-M4."),
    ("APN", "Access Point Name. The cellular gateway identifier required to attach a data session."),
    ("CGNAT", "Carrier-Grade NAT. Network address translation done by mobile carriers, hiding all subscribers behind shared public IPs."),
    ("DAC", "Digital-to-Analog Converter. Reconstructs an analog signal from digital samples."),
    ("DMA", "Direct Memory Access. Lets peripherals move data to/from RAM without CPU involvement."),
    ("Full-duplex", "Simultaneous two-way communication, like a real phone call (vs. half-duplex like a walkie-talkie)."),
    ("HAL", "Hardware Abstraction Layer. ST's C library that wraps STM32 peripheral registers in friendlier function calls."),
    ("HCLK", "AHB system bus clock; the main CPU clock on STM32."),
    ("Hybrid encryption", "Use asymmetric crypto (RSA) to exchange a symmetric key, then symmetric crypto (AES) for bulk data. Standard practice."),
    ("I²C", "Two-wire serial bus (SDA + SCL) used to talk to the MCP4725 DAC."),
    ("ngrok", "Free tunneling service that exposes a port on your laptop to the public internet via a forwarded address."),
    ("RSA-512", "Asymmetric (public-key) encryption with 512-bit modulus. Weak by modern standards but light enough for embedded demos."),
    ("SWD", "Serial Wire Debug. Two-wire programming/debug interface (SWDIO + SWCLK) used by the ST-Link."),
    ("TCP", "Transmission Control Protocol. Reliable, ordered byte-stream over IP — used for the relay link."),
    ("TRGO", "Trigger Output. STM32 timer feature that lets one peripheral (e.g., TIM2) trigger another (e.g., ADC)."),
    ("TRRS", "Tip-Ring-Ring-Sleeve. Four-conductor 3.5 mm jack standard, used by mic+headphone headsets."),
    ("VoLTE", "Voice over LTE. Carrier-managed voice call over the LTE data network — bypassed in this project."),
]
g_data = [['Term', 'Definition']]
for t, d in glossary:
    g_data.append([t, d])
story.append(make_table(g_data, col_widths=[3 * cm, 11 * cm]))

story.append(Spacer(1, 1 * cm))
story.append(P("End of document.", note))


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Secure Voice Project Documentation",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")

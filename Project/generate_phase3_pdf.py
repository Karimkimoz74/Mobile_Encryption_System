"""
Generates Phase 3 PDF — Digital Audio Loopback
(mic -> ADC -> RAM -> MCP4725 DAC -> LM386 -> headphones)
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase3_Digital_Loopback.pdf"

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
    fontSize=13, leading=17, spaceBefore=12, spaceAfter=6,
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
    fontName='Courier', fontSize=7.5, leading=10,
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
                      "Secure Voice Project | Phase 3 — Digital Audio Loopback")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

# ----- Title page -----
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 3<br/>Digital Audio Loopback", title_style))
story.append(P("Microphone &rarr; STM32 ADC &rarr; RAM &rarr; MCP4725 DAC &rarr; LM386 &rarr; Headphones",
               subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P("<b>Goal:</b> Build a real-time digital audio path through the STM32. The user speaks "
               "into the microphone and hears their own voice in the headphones, with every audio "
               "sample passing through the microcontroller as a digital number in RAM.",
               body))
story.append(Spacer(1, 0.5 * cm))
story.append(P("<b>Why this is the most important phase:</b> once it works, the entire local audio "
               "pipeline is verified. Every later phase (encryption, LTE transmission, decryption) "
               "just changes what happens to the digital samples between ADC and DAC — the hardware "
               "path stays the same.", body))
story.append(Spacer(1, 1 * cm))
story.append(P("<b>Prerequisites:</b> Phase 1 (analog chain) and Phase 2 (STM32 ADC + LED) "
               "must be complete and verified working.", success_style))
story.append(PageBreak())

# ----- Section 1: Overview -----
story.append(P("1. Phase 3 Overview", h1))

story.append(P("1.1 The Pipeline", h2))
story.append(ascii_block(r"""
   Phase 2 (just finished):
       mic ---> MAX9814 ---> STM32 ADC ---> [LED on/off]   (no audio output)

   Phase 3 (this phase):
       mic ---> MAX9814 ---> STM32 ADC ---> RAM buffer ---> MCP4725 DAC
                                                                 |
                                                                 v
                                                              LM386 amplifier
                                                                 |
                                                                 v
                                                              TRRS jack
                                                                 |
                                                                 v
                                                              Headphones
                                                                 |
                                                                 v
                                                              YOUR EARS
""".strip()))

story.append(P("1.2 What's New", h2))
new_things = [
    ['Item', 'Purpose'],
    ['MCP4725 DAC module', 'Converts digital audio samples back into an analog voltage'],
    ['I2C1 peripheral', 'STM32 communicates with the MCP4725 over a 2-wire bus (SDA + SCL)'],
    ['TIM3 timer', 'Generates an 8 kHz interrupt — every interrupt writes one sample to the DAC'],
    ['~15 lines of firmware', 'TIM3 ISR plus a small change to the main loop'],
]
story.append(make_table(new_things, col_widths=[5 * cm, 9 * cm]))

story.append(P("1.3 What Stays the Same", h2))
story.append(P("All the wiring from Phases 1 and 2 stays in place:"))
same = [
    "MAX9814 powered (3.3 V, GND) and connected to PA0 — unchanged from Phase 2.",
    "Headset (input) plugged into TRRS#1, with mic wired to MAX9814's empty pads.",
    "LM386 powered (5 V, GND) and wired to TRRS#2 (output). Same as Phase 1.",
    "Output headphones still in TRRS#2.",
    "Black Pill USB-C powering the breadboard rails.",
]
for s in same:
    story.append(P("• " + s, bullet))

story.append(P("The only signal-path change: the LM386's INPUT switches from <i>(formerly the "
               "MAX9814 OUT)</i> to <i>the MCP4725 OUT</i>. The MAX9814's output now goes to the "
               "STM32 instead of straight to the LM386.", body))

story.append(PageBreak())

# ----- Section 2: MCP4725 Background -----
story.append(P("2. About the MCP4725 DAC", h1))

story.append(P("2.1 What It Does", h2))
story.append(P("The MCP4725 is a tiny single-chip DAC (digital-to-analog converter) that turns "
               "12-bit digital values (0&ndash;4095) into an analog voltage between 0 V and VDD. "
               "It speaks over the I&sup2;C bus, so only two wires are needed for control plus "
               "VDD and GND for power."))

specs = [
    ['Spec', 'Value'],
    ['Resolution', '12 bits (4096 voltage levels between 0 V and VDD)'],
    ['Output range', '0 V to VDD (we use VDD = 3.3 V)'],
    ['Communication', 'I&sup2;C, 7-bit address 0x60 (when A0 pin is tied to GND)'],
    ['Maximum I&sup2;C speed', '3.4 MHz (we will use 400 kHz Fast Mode &mdash; plenty of margin)'],
    ['Output settling time', '~6 &mu;s &mdash; fast enough for 8 kHz audio (period = 125 &mu;s)'],
    ['Onboard pull-ups', 'Most breakouts already include 4.7 k&Omega; pull-ups on SDA and SCL'],
]
story.append(make_table(specs, col_widths=[5 * cm, 9 * cm]))

story.append(P("2.2 Address Selection", h2))
story.append(P("The MCP4725 has an A0 pin that selects between two possible I&sup2;C addresses. "
               "On most breakouts A0 is already tied to GND on the PCB, giving address <b>0x60</b>. "
               "If your breakout exposes A0 as a pin/pad, tie it to GND for address 0x60. "
               "(If tied to VDD, address would be 0x61 &mdash; we will use 0x60 in firmware.)"))

story.append(P("2.3 Fast-Write Frame Format", h2))
story.append(P("To save bandwidth we use the MCP4725's Fast Write mode &mdash; just 2 bytes per "
               "sample after the address byte:"))
story.append(ascii_block(r"""
   Byte 1:  C2 C1 PD1 PD0 D11 D10 D9 D8     (control bits + upper 4 data bits)
   Byte 2:  D7 D6 D5 D4 D3 D2 D1 D0          (lower 8 data bits)

   For normal operation we send C2=0, C1=0, PD1=0, PD0=0,
   followed by the 12-bit data value.

   At 400 kHz I2C, each 2-byte transfer takes ~25 us.
   With audio period = 125 us per sample at 8 kHz, we have plenty of headroom.
""".strip()))

story.append(P("2.4 Why a 12-bit DAC for 8-bit Audio?", h2))
story.append(P("The ADC samples are 8-bit (0&ndash;255), but the DAC accepts 12-bit values "
               "(0&ndash;4095). The firmware simply left-shifts the 8-bit value by 4 bits to "
               "scale it into the 12-bit range. This wastes some DAC resolution, but it works "
               "perfectly for voice quality and keeps the data path simple."))
story.append(code('''/* Convert 8-bit ADC sample to 12-bit DAC value */
uint16_t dac_value = ((uint16_t)adc_sample) << 4;
/* 0   -> 0
   128 -> 2048 (mid-rail)
   255 -> 4080 (close to full scale) */'''))

story.append(PageBreak())

# ----- Section 3: Wiring -----
story.append(P("3. Circuit &amp; Wiring", h1))

story.append(P("3.1 New Connections (4 wires to the MCP4725)", h2))
mcp_wires = [
    ['#', 'From', 'To', 'Notes'],
    ['1', 'MCP4725 VDD', '3.3 V rail (top + rail)', 'Powers the DAC chip'],
    ['2', 'MCP4725 GND', '&minus; rail', 'Common ground with everything'],
    ['3', 'MCP4725 SCL', 'STM32 PB6 (I2C1_SCL)', 'I&sup2;C clock'],
    ['4', 'MCP4725 SDA', 'STM32 PB7 (I2C1_SDA)', 'I&sup2;C data'],
    ['5', 'MCP4725 A0', '&minus; rail (GND)', 'Sets I&sup2;C address to 0x60'],
    ['6', 'MCP4725 OUT', 'LM386 IN (header pin)', 'Replaces the wire that previously came from MAX9814 OUT'],
]
story.append(make_table(mcp_wires, col_widths=[1 * cm, 3.5 * cm, 4.5 * cm, 5.5 * cm]))

story.append(P("3.2 Wire That Must Be Removed", h2))
story.append(P("In Phase 2 the MAX9814 OUT was already feeding the STM32 at PA0. In Phase 3 the "
               "<b>LM386 input source changes</b> from MAX9814 OUT to MCP4725 OUT:"))
removal = [
    ['Action', 'Wire', 'Reason'],
    ['REMOVE', 'Any direct wire from MAX9814 OUT to LM386 IN', 'Audio now goes through the STM32 first; LM386 input comes from the DAC'],
]
story.append(make_table(removal, col_widths=[2.5 * cm, 6 * cm, 6 * cm]))

story.append(P("3.3 What Stays Wired (do not touch)", h2))
keep = [
    "All 4 power rail wires (Black Pill 3V3, 5V, GND).",
    "MAX9814 power: VDD to 3.3 V rail, GND to &minus; rail.",
    "TRRS#1 Sleeve to MAX9814 MIC+ pad (the empty pad).",
    "TRRS#1 Ring 2 to &minus; rail.",
    "MAX9814 OUT to STM32 PA0 (added in Phase 2).",
    "LM386 power: VCC to 5 V rail, GND to &minus; rail.",
    "LM386 green terminal + to TRRS#2 Tip and Ring 1.",
    "LM386 green terminal &minus; to &minus; rail.",
]
for s in keep:
    story.append(P("• " + s, bullet))

story.append(P("3.4 Final Wiring Summary &mdash; All Sections", h2))
all_wires = [
    ['Section', '#', 'From', 'To'],
    ['Power', '1', 'Black Pill 3V3', 'Top + rail (3.3 V)'],
    ['', '2', 'Black Pill 5V', 'Bottom + rail (5 V)'],
    ['', '3', 'Black Pill GND', '&minus; rail'],
    ['', '4', 'Top &minus; rail', 'Bottom &minus; rail (common GND)'],
    ['MAX9814', '5', 'MAX9814 VDD', 'Top + rail'],
    ['', '6', 'MAX9814 GND', '&minus; rail'],
    ['', '7', 'TRRS#1 Sleeve', 'MAX9814 MIC+ empty pad'],
    ['', '8', 'TRRS#1 Ring 2', '&minus; rail'],
    ['', '9', 'MAX9814 OUT', 'STM32 PA0 (ADC1_IN0)'],
    ['MCP4725', '10', 'MCP4725 VDD', 'Top + rail (3.3 V)'],
    ['', '11', 'MCP4725 GND', '&minus; rail'],
    ['', '12', 'MCP4725 SCL', 'STM32 PB6'],
    ['', '13', 'MCP4725 SDA', 'STM32 PB7'],
    ['', '14', 'MCP4725 A0', '&minus; rail (selects address 0x60)'],
    ['', '15', 'MCP4725 OUT', 'LM386 IN (header pin)'],
    ['LM386', '16', 'LM386 VCC', 'Bottom + rail (5 V)'],
    ['', '17', 'LM386 GND', '&minus; rail'],
    ['', '18', 'LM386 + (green)', 'TRRS#2 Tip and Ring 1'],
    ['', '19', 'LM386 &minus; (green)', '&minus; rail'],
]
story.append(make_table(all_wires, col_widths=[2 * cm, 1 * cm, 5 * cm, 6.5 * cm]))

story.append(P("Total: <b>19 wires</b>. No extra capacitors, no extra resistors &mdash; the "
               "MAX9814 OUT now goes directly to PA0 (the STM32 ADC input has its own bias "
               "tolerance), and the MCP4725 OUT goes directly to LM386 IN (modern LM386 modules "
               "include their own input coupling capacitor).", note_style))

story.append(PageBreak())

# ----- Section 4: CubeMX -----
story.append(P("4. STM32CubeMX Configuration", h1))
story.append(P("Open your existing <b>MicLED</b> project's .ioc file in CubeMX. Add I2C1 and TIM3, "
               "then regenerate code."))

story.append(P("4.1 Add I2C1 (for the MCP4725)", h2))
i2c_steps = [
    "Connectivity &rarr; <b>I2C1</b> &rarr; Mode: <b>I2C</b>.",
    "PB6 turns yellow as SCL, PB7 turns yellow as SDA on the chip diagram.",
    "Parameter Settings &rarr; I2C Speed Mode: <b>Fast Mode</b>.",
    "Parameter Settings &rarr; I2C Clock Speed (Hz): <b>400000</b>.",
    "Parameter Settings &rarr; Fast Mode Duty Cycle: 2.",
    "Other defaults are fine.",
    "(Optional but recommended) DMA Settings &rarr; Add &rarr; <b>I2C1_TX</b>: Mode = Normal, Direction = Memory To Peripheral, Byte width.",
]
for s in i2c_steps:
    story.append(P("• " + s, bullet))

story.append(P("4.2 Add TIM3 (8 kHz Playback Tick)", h2))
tim3_steps = [
    "Timers &rarr; <b>TIM3</b> &rarr; Clock Source: <b>Internal Clock</b>.",
    "Parameter Settings &rarr; Prescaler: <b>83</b>.",
    "Parameter Settings &rarr; Counter Period: <b>124</b>.",
    "Parameter Settings &rarr; Auto-reload preload: <b>Enable</b>.",
    "<b>NVIC Settings tab</b> &rarr; enable <b>TIM3 global interrupt</b>.",
]
for s in tim3_steps:
    story.append(P("• " + s, bullet))
story.append(P("Math: TIM3 clock = 84 MHz / ((83+1) &times; (124+1)) = 8000 Hz exact &mdash; same "
               "as TIM2 already configured for the ADC.", note_style))

story.append(P("4.3 NVIC Priority Order", h2))
nvic_steps = [
    "System Core &rarr; NVIC &rarr; verify these enabled with the listed priorities:",
]
for s in nvic_steps:
    story.append(P("• " + s, bullet))
nvic_data = [
    ['Interrupt', 'Preempt Priority', 'Why'],
    ['DMA2 Stream0 (ADC)', '0 (highest)', 'Audio capture must never be starved'],
    ['I2C1 EV', '1', 'DAC writes must complete before next TIM3 tick'],
    ['I2C1 ER', '1', 'I&sup2;C error handling'],
    ['ADC1', '2', 'Conversion-complete signaling'],
    ['TIM3', '2', 'Playback tick'],
]
story.append(make_table(nvic_data, col_widths=[4 * cm, 4 * cm, 6.5 * cm]))

story.append(P("4.4 Generate Code", h2))
gen_steps = [
    "Click <b>Project Manager</b> tab &rarr; verify Toolchain is still <b>CMake</b>.",
    "Click <b>GENERATE CODE</b>.",
    "When done, return to VS Code &mdash; the new files (i2c.c, i2c.h, tim.h additions) appear in Core/Src and Core/Inc.",
]
for s in gen_steps:
    story.append(P("• " + s, bullet))

story.append(PageBreak())

# ----- Section 5: Firmware -----
story.append(P("5. Firmware Code", h1))
story.append(P("Open <b>Core/Src/main.c</b>. Add the snippets below at the marked USER CODE regions. "
               "Keep all the Phase 2 code that is already there &mdash; we are <b>adding</b>, not "
               "replacing."))

story.append(P("5.1 Add to USER CODE BEGIN PD (private defines)", h2))
story.append(code('''/* USER CODE BEGIN PD */
#define BUF_SIZE        256
#define HALF_SIZE       (BUF_SIZE / 2)
#define VOICE_THRESHOLD 20
#define MCP4725_ADDR    (0x60 << 1)   /* HAL expects shifted 8-bit address */
/* USER CODE END PD */'''))

story.append(P("5.2 Add to USER CODE BEGIN PV (private variables)", h2))
story.append(code('''/* USER CODE BEGIN PV */
uint8_t  adc_buffer[BUF_SIZE];
volatile uint8_t half_ready = 0;
volatile uint8_t full_ready = 0;
volatile uint16_t dac_play_idx = 0;     /* index into adc_buffer for next DAC sample */
/* USER CODE END PV */'''))

story.append(P("5.3 Add to USER CODE BEGIN 2 (after MX_*_Init() calls)", h2))
story.append(code('''/* USER CODE BEGIN 2 */
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, BUF_SIZE);
HAL_TIM_Base_Start(&htim2);             /* drives the 8 kHz ADC trigger */
HAL_TIM_Base_Start_IT(&htim3);          /* drives the 8 kHz DAC playback */
/* USER CODE END 2 */'''))

story.append(P("5.4 Replace the WHILE loop (USER CODE BEGIN WHILE)", h2))
story.append(P("In Phase 2 the loop drove the LED. In Phase 3 the loop just toggles the heartbeat "
               "LED &mdash; the audio playback runs entirely in interrupts."))
story.append(code('''/* USER CODE BEGIN WHILE */
while (1)
{
    /* Optional: heartbeat LED so we know firmware is alive */
    if (half_ready || full_ready) {
        half_ready = 0;
        full_ready = 0;
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
    }
}
/* USER CODE END WHILE */'''))

story.append(P("5.5 Add the TIM3 ISR &mdash; the heart of Phase 3", h2))
story.append(P("This callback runs 8000 times per second. Each call grabs the latest ADC sample "
               "from RAM and writes it to the MCP4725 over I&sup2;C."))
story.append(code('''/* In USER CODE BEGIN 4 (or extend it if Phase 2 already added callbacks) */
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) half_ready = 1;
}
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) full_ready = 1;
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM3) {
        /* Take the next ADC sample (8-bit) and scale it to 12-bit for MCP4725 */
        uint16_t v12 = ((uint16_t)adc_buffer[dac_play_idx]) << 4;

        /* MCP4725 Fast-Write packet (2 bytes) */
        uint8_t pkt[2] = {
            (uint8_t)((v12 >> 8) & 0x0F),   /* upper 4 bits */
            (uint8_t)(v12 & 0xFF)            /* lower 8 bits */
        };
        HAL_I2C_Master_Transmit_IT(&hi2c1, MCP4725_ADDR, pkt, 2);

        /* Advance the playback index, wrap at end of buffer */
        dac_play_idx = (dac_play_idx + 1) % BUF_SIZE;
    }
}'''))

story.append(P("Why <code>HAL_I2C_Master_Transmit_IT</code> (interrupt) and not the blocking "
               "version? At 400 kHz the 2-byte transfer takes ~25 &mu;s. Blocking inside a "
               "TIM3 ISR for that long would block other interrupts. The IT (interrupt) version "
               "starts the transfer and returns immediately; the I&sup2;C peripheral finishes "
               "in the background while the rest of the firmware runs.", note_style))

story.append(PageBreak())

# ----- Section 6: Build & Flash -----
story.append(P("6. Build, Flash &amp; Test", h1))

story.append(P("6.1 Build", h2))
build_steps = [
    "Press <b>Ctrl + S</b> in VS Code to save main.c.",
    "Press <b>Ctrl + Shift + B</b> &rarr; pick <b>Build</b>.",
    "Watch the terminal for the build output:",
]
for s in build_steps:
    story.append(P("• " + s, bullet))
story.append(code('''[16/16] Linking C executable MicLED.elf
   text    data     bss     dec     hex filename
  ...
Build finished. 0 errors, 0 warnings.'''))

story.append(P("6.2 Flash", h2))
flash_steps = [
    "Verify wiring: ST-Link SWDIO/SWCLK/GND to Black Pill, board powered via USB-C.",
    "Verify breadboard: all 19 wires from Section 3.4 in place, MCP4725 properly seated.",
    "In VS Code STM32 sidebar, click <b>Run</b>. Or use Run/Debug &rarr; green arrow.",
    "Terminal shows:",
]
for s in flash_steps:
    story.append(P("• " + s, bullet))
story.append(code('''Memory Programming ...
File download complete
Time elapsed during download operation: ~1s
Application is running, Reset device.'''))

story.append(P("6.3 Test Procedure", h2))
test_steps = [
    "Plug the input headset into TRRS#1 (with mic wired to MAX9814 MIC+ empty pad).",
    "Plug the output headphones into TRRS#2.",
    "Set LM386 gain knob to <b>minimum</b> (fully counter-clockwise).",
    "Hold the input headset and output headphones <b>physically apart</b> from each other (acoustic feedback prevention).",
    "Place one earbud loosely near the ear &mdash; do not insert.",
    "Slowly turn the LM386 gain clockwise while speaking softly into the input headset's mic.",
    "When the voice becomes audible at low gain, the loop is working.",
]
for s in test_steps:
    story.append(P("• " + s, bullet))

story.append(P("6.4 Expected Results", h2))
expected = [
    ['Stimulus', 'Expected Result'],
    ['Silence', 'Quiet hiss in earbud (background noise of the analog chain)'],
    ['Speaking normally', 'Your own voice reproduced in the earbud, with imperceptible delay (~30 ms)'],
    ['Whistling', 'Whistle reproduced clearly'],
    ['Sharp clap', 'Clap reproduced as a short impulse'],
    ['Tap the input mic with finger', 'Each tap reproduced as a "thump"'],
    ['PC13 onboard LED', 'Toggles every 16 ms when audio frames arrive (looks like steady glow at low brightness)'],
]
story.append(make_table(expected, col_widths=[5 * cm, 9.5 * cm]))

story.append(P("<b>Pass criterion:</b> Voice audible in the headphones, with the audio passing "
               "through the STM32 (you can confirm this by simply removing power to the Black "
               "Pill &mdash; the audio cuts out, proving the path goes through the microcontroller).",
               success_style))

story.append(PageBreak())

# ----- Section 7: Troubleshooting -----
story.append(P("7. Troubleshooting", h1))

trouble = [
    ['Symptom', 'Likely Cause', 'Fix'],
    ['Build error: hi2c1 undeclared',
     'I2C1 not added in CubeMX or code not regenerated',
     'Re-open .ioc, ensure I2C1 enabled, click Generate Code'],
    ['Build error: htim3 undeclared',
     'TIM3 not added in CubeMX',
     'Re-open .ioc, enable TIM3 internal clock, regenerate'],
    ['Total silence in headphones',
     '(a) MCP4725 not powered, (b) wrong I&sup2;C address, (c) MCP4725 OUT not connected to LM386 IN',
     'Multimeter: 3.3V on MCP4725 VDD; verify A0 to GND; verify wire 15 from Section 3.4'],
    ['Distorted / harsh / clipping sound',
     'LM386 gain too high; or DAC saturating because input audio is louder than 8-bit range',
     'Lower LM386 gain; speak softer; if still bad, divide ADC sample by 2 in firmware'],
    ['Steady tone instead of voice',
     'TIM3 firing too fast or I&sup2;C transactions colliding',
     'Verify TIM3 PSC=83, ARR=124; verify I2C1 at 400 kHz Fast Mode'],
    ['Audio crackles / drops out',
     'I&sup2;C not finishing in time (busy too long)',
     'Verify I2C1 at 400 kHz; verify NVIC priority of TIM3 lower than I2C1'],
    ['Audio plays but sounds robotic / aliased',
     'ADC offset (~96/255) being treated as audio',
     'Subtract 96 from sample before scaling: v12 = ((adc_buffer[i] - 96 + 128) & 0xFF) << 4'],
    ['HAL_I2C_Master_Transmit_IT returns BUSY',
     'Previous transfer still in progress',
     'Check that NVIC priorities are correct (I2C IRQ above TIM3); add a small skip-if-busy guard'],
    ['LED on PC13 stays off forever',
     'Heartbeat code not running &mdash; main loop blocked',
     'ADC DMA may be misconfigured (Circular mode? NVIC enabled?)'],
]
story.append(make_table(trouble, col_widths=[4 * cm, 5 * cm, 5.5 * cm]))

story.append(P("7.1 Quick Diagnostic Sequence", h2))
diag = [
    "<b>Power check:</b> multimeter on MCP4725 VDD&mdash;GND should read 3.3 V.",
    "<b>I&sup2;C check:</b> add a simple I2C device scan loop in firmware that walks addresses 1&ndash;127 and prints anything found over USART2 / debug. Should report 0x60.",
    "<b>DC test:</b> temporarily replace the TIM3 ISR body with two alternating writes (one to 0x000, one to 0xFFF, with a 1-second HAL_Delay between). Multimeter on MCP4725 OUT should toggle between ~0 V and ~3.3 V.",
    "<b>Tone test:</b> generate a 500 Hz square wave on the DAC. You should hear a clean low-pitched beep.",
    "<b>Loopback test:</b> only after all of the above pass, run the full firmware and expect to hear yourself.",
]
for d in diag:
    story.append(P("• " + d, bullet))

story.append(P("7.2 What This Phase Proves", h2))
proves = [
    "I&sup2;C peripheral is correctly configured at 400 kHz.",
    "The MCP4725 DAC is responding at address 0x60.",
    "TIM3 fires at exactly 8 kHz, locked to the same clock as TIM2 (the ADC trigger).",
    "Interrupt-driven I&sup2;C transmission completes within the 125 &mu;s budget every cycle.",
    "ADC and DAC sample rates are synchronised &mdash; samples are produced and consumed at the same rate, so the buffer never overruns or underruns.",
    "The full real-time digital audio loop closes: every sample passes through the STM32's RAM.",
    "The system has 4 ms of buffer latency (256 samples / 8 kHz / 2 halves) plus the ADC + I&sup2;C processing time.",
]
for p in proves:
    story.append(P("• " + p, bullet))

story.append(P("These are exactly the primitives every later phase will build on. Phase 4 (LTE "
               "manual AT commands) and beyond add a network in the middle of the loop, but the "
               "audio path itself stays identical.", body))

story.append(PageBreak())

# ----- Section 8: Phase 3 Roadmap -----
story.append(P("8. After Phase 3", h1))
story.append(P("Once you can hear yourself reliably through the digital loopback, the upcoming "
               "phases are:"))
roadmap = [
    ['Phase', 'Description', 'New Hardware', 'New Firmware Concept'],
    ['Phase 4', 'LTE module bring-up &mdash; manual AT commands via USB-TTL',
     'T-A7608 LTE module + USB-TTL adapter',
     'None &mdash; you type AT commands by hand to verify the modem'],
    ['Phase 5', 'STM32 drives the LTE module',
     'Wire LTE module to STM32 USART1',
     'AT-command state machine + relay TCP connection'],
    ['Phase 6', 'Two-node plain audio over LTE',
     'Both devices fully assembled',
     'Send the encrypted-audio bytes over the TCP channel (no encryption yet)'],
    ['Phase 7', 'Add hybrid encryption',
     'No new hardware',
     'mbedTLS RSA + AES-128-CTR; key exchange at session start'],
    ['Phase 8', 'Polish &mdash; phone-number-based call setup, status LEDs, push buttons',
     '2 push buttons per device',
     'Call/Answer/Hangup state machine, blinking-LED state indicator'],
]
story.append(make_table(roadmap, col_widths=[2 * cm, 4 * cm, 4 * cm, 4.5 * cm]))

story.append(Spacer(1, 0.5 * cm))
story.append(P("End of Phase 3 document.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 3 — Digital Audio Loopback",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")

"""
Generates the Phase 3 step-by-step PDF — complete from-scratch walkthrough
from hardware wiring through CubeMX, firmware, build, flash, and test.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase3_Steps_From_Scratch.pdf"

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
                      "Secure Voice Project | Phase 3 Step-by-Step (From Scratch)")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

# Title page
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 3<br/>Complete Steps From Scratch", title_style))
story.append(P("Hardware &rarr; CubeMX &rarr; Firmware &rarr; Build &rarr; Flash &rarr; Test",
               subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P("<b>Phase 3 — Digital Audio Loopback.</b> A new STM32CubeMX project (named "
               "<b>MicDAC</b>) is created from scratch. The user speaks into the headset "
               "microphone, the audio passes through the STM32 (ADC &rarr; RAM &rarr; DAC), "
               "and is heard in the output headphones via the LM386 amplifier.",
               body))
story.append(Spacer(1, 0.3 * cm))
story.append(P("<b>STATUS:</b> COMPLETED on 2026-04-27. Voice is reproduced cleanly through the "
               "STM32 with only mild background hiss. This document reflects the final working "
               "configuration after the lessons listed in Section 16.",
               success_style))
story.append(Spacer(1, 0.3 * cm))
story.append(P("Project name: <b>MicDAC</b><br/>"
               "MCU: <b>STM32F401RCT6</b><br/>"
               "HCLK: <b>84 MHz</b> from HSE 25 MHz crystal<br/>"
               "Sample rate: <b>8 kHz</b> for both ADC capture and DAC playback<br/>"
               "ADC resolution: <b>12-bit</b> (upgraded from 8-bit during testing — see Section 16)<br/>"
               "I&sup2;C transfer: <b>blocking</b> (HAL_I2C_Master_Transmit, NOT the _IT variant)",
               body))
story.append(PageBreak())

# ----- STEP 1: Hardware -----
story.append(P("STEP 1 — Hardware Wiring", h1))
story.append(P("Build the entire breadboard before any code is written. Total of 19 wires.", body))

story.append(P("Power Rails (4 wires)", h2))
story.append(make_table([
    ['#', 'From', 'To'],
    ['1', 'Black Pill 3V3', 'Top + rail'],
    ['2', 'Black Pill 5V', 'Bottom + rail'],
    ['3', 'Black Pill GND', 'Top &minus; rail'],
    ['4', 'Top &minus; rail', 'Bottom &minus; rail (common GND)'],
], col_widths=[1 * cm, 5 * cm, 8.5 * cm]))

story.append(P("MAX9814 — modified board with onboard mic removed (5 wires)", h2))
story.append(make_table([
    ['#', 'From', 'To'],
    ['5', 'MAX9814 VDD', 'Top + rail (3.3 V)'],
    ['6', 'MAX9814 GND', '&minus; rail'],
    ['7', 'TRRS#1 Sleeve pad', 'MAX9814 MIC+ empty pad'],
    ['8', 'TRRS#1 Ring 2 pad', '&minus; rail'],
    ['9', 'MAX9814 OUT', 'STM32 PA0 (ADC1_IN0)'],
], col_widths=[1 * cm, 5 * cm, 8.5 * cm]))
story.append(P("IMPORTANT: leave the MAX9814 GAIN pin floating (no wire). On this user's clone "
               "board, tying GAIN to VDD silences the mic entirely. Default 60 dB gain (floating) "
               "works fine when the headset mic sits at the user's mouth.",
               warn_style))

story.append(P("MCP4725 DAC (6 wires + 1 capacitor)", h2))
story.append(make_table([
    ['#', 'From', 'To'],
    ['10', 'MCP4725 VDD (or VCC)', 'Top + rail (3.3 V)'],
    ['11', 'MCP4725 GND (one of two)', '&minus; rail'],
    ['12', 'MCP4725 GND (other)', '&minus; rail (both GND pins go to ground)'],
    ['13', 'MCP4725 SCL', 'STM32 PB6 (I2C1_SCL)'],
    ['14', 'MCP4725 SDA', 'STM32 PB7 (I2C1_SDA)'],
    ['15', 'MCP4725 A0', 'On many clone boards A0 is not exposed and is hardwired to GND on the PCB &mdash; address 0x60. If your board has the pin, tie it to the &minus; rail.'],
    ['16', 'MCP4725 OUT', 'one leg of 1 &mu;F capacitor'],
    ['16b', 'other leg of 1 &mu;F capacitor', 'LM386 IN (header pin)'],
], col_widths=[1 * cm, 5 * cm, 8.5 * cm]))
story.append(P("MANDATORY: the 1 &mu;F capacitor between MCP4725 OUT and LM386 IN. The MCP4725 "
               "output sits at ~1.6 V DC (mid-rail). Without the cap to block this DC bias, the "
               "LM386 input is DC-coupled to a permanent offset and audio cannot pass through &mdash; "
               "you will hear only hiss. With the cap in place, only the AC audio is coupled in.",
               warn_style))

story.append(P("LM386 + TRRS#2 Output (4 wires)", h2))
story.append(make_table([
    ['#', 'From', 'To'],
    ['16', 'LM386 VCC (header)', 'Bottom + rail (5 V)'],
    ['17', 'LM386 GND (header)', '&minus; rail'],
    ['18', 'LM386 + (green terminal)', 'TRRS#2 Tip AND Ring 1 pads'],
    ['19', 'LM386 &minus; (green terminal)', '&minus; rail'],
], col_widths=[1 * cm, 5 * cm, 8.5 * cm]))

story.append(P("Plug the input headset (with mic) into <b>TRRS#1</b>. Plug the output headphones "
               "into <b>TRRS#2</b>. Set the LM386 gain knob fully counter-clockwise (minimum) "
               "before powering on.", body))

story.append(PageBreak())

# ----- STEP 2: Create CubeMX -----
story.append(P("STEP 2 — Create New CubeMX Project", h1))
steps = [
    "Open <b>STM32CubeMX</b>.",
    "<b>File &rarr; New Project</b>.",
    "In the search box, type <b>STM32F401RCTx</b>.",
    "Click your row in the result list &rarr; click <b>Start Project</b>.",
    "The Pinout &amp; Configuration tab opens with the chip diagram.",
]
for s in steps:
    story.append(P("• " + s, bullet))

# ----- STEP 3: RCC + SYS -----
story.append(P("STEP 3 — RCC and SYS", h1))
steps = [
    "Left tree &rarr; <b>System Core &rarr; RCC</b>.",
    "Set <b>High Speed Clock (HSE)</b> = <b>Crystal/Ceramic Resonator</b>.",
    "Leave Low Speed Clock (LSE) = Disable.",
    "Left tree &rarr; <b>System Core &rarr; SYS</b>.",
    "Set <b>Debug</b> = <b>Serial Wire</b>. (Critical &mdash; without this, SWD programming will fail after first flash.)",
]
for s in steps:
    story.append(P("• " + s, bullet))

# ----- STEP 4: Clock -----
story.append(P("STEP 4 — Clock Configuration @ 84 MHz", h1))
steps = [
    "Click <b>Clock Configuration</b> tab at the top.",
    "Click <b>PLL Source Mux</b> dropdown &rarr; select <b>HSE</b>.",
    "In the <b>HCLK (MHz)</b> field, type <b>84</b> and press Enter.",
    "CubeMX shows a dialog about auto-solving the PLL &mdash; click OK.",
    "Verify HCLK shows 84 MHz in green and Flash Latency = 2 WS auto-set.",
]
for s in steps:
    story.append(P("• " + s, bullet))

# ----- STEP 5: TIM2 -----
story.append(P("STEP 5 — TIM2 (8 kHz ADC trigger)", h1))
story.append(P("Back to Pinout &amp; Configuration tab."))
steps = [
    "Left tree &rarr; <b>Timers &rarr; TIM2</b>.",
    "Mode &rarr; Clock Source = <b>Internal Clock</b>.",
    "Parameter Settings &rarr; Prescaler = <b>83</b>.",
    "Parameter Settings &rarr; Counter Period (ARR) = <b>124</b>.",
    "Parameter Settings &rarr; Auto-reload preload = <b>Enable</b>.",
    "Trigger Output &rarr; Master/Slave Mode = <b>Disable</b>.",
    "Trigger Output &rarr; Trigger Event Selection TRGO = <b>Update Event</b>.",
    "NVIC: leave TIM2 IRQ disabled (we only need TRGO, not the interrupt).",
]
for s in steps:
    story.append(P("• " + s, bullet))
story.append(P("Math: TIM2 clk = 84 MHz / ((83+1) &times; (124+1)) = 8000 Hz exactly.", note_style))

# ----- STEP 6: TIM3 -----
story.append(P("STEP 6 — TIM3 (8 kHz DAC playback tick)", h1))
steps = [
    "Left tree &rarr; <b>Timers &rarr; TIM3</b>.",
    "Mode &rarr; Clock Source = <b>Internal Clock</b>.",
    "Parameter Settings &rarr; Prescaler = <b>83</b>.",
    "Parameter Settings &rarr; Counter Period (ARR) = <b>124</b>.",
    "Parameter Settings &rarr; Auto-reload preload = <b>Enable</b>.",
    "<b>NVIC Settings tab</b> &rarr; <b>enable TIM3 global interrupt</b>.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(PageBreak())

# ----- STEP 7: ADC1 -----
story.append(P("STEP 7 — ADC1 (8-bit, TIM2-triggered, DMA)", h1))
story.append(P("CubeMX gotcha: do the DMA Settings BEFORE the Parameter Settings, otherwise "
               "<i>DMA Continuous Requests</i> stays grayed out.", warn_style))

story.append(P("7a — Enable channel", h2))
steps = [
    "Left tree &rarr; <b>Analog &rarr; ADC1</b>.",
    "Check <b>IN0</b> in the Mode pane &mdash; PA0 turns green on the chip diagram.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(P("7b — DMA Settings tab (do this FIRST)", h2))
steps = [
    "Click the <b>DMA Settings</b> tab in the ADC1 configuration pane.",
    "Click <b>Add</b> &rarr; in the new row, DMA Request = <b>ADC1</b>.",
]
for s in steps:
    story.append(P("• " + s, bullet))
story.append(make_table([
    ['Field', 'Value'],
    ['Stream', 'DMA2 Stream 0 (auto)'],
    ['Direction', 'Peripheral To Memory'],
    ['Mode', 'Circular  (NOT Normal — continuous sampling)'],
    ['Priority', 'High'],
    ['Use FIFO', 'Disabled (Direct mode)'],
    ['Increment Address — Peripheral', 'Unchecked'],
    ['Increment Address — Memory', 'Checked'],
    ['Peripheral Data Width', 'Half Word  (matches 12-bit ADC)'],
    ['Memory Data Width', 'Half Word  (matches uint16_t buffer)'],
], col_widths=[6.5 * cm, 8 * cm]))
story.append(P("Mode = <b>Circular</b> is critical. CubeMX defaults to Normal mode which "
               "transfers BUF_SIZE samples once and stops &mdash; the half/full callbacks fire "
               "exactly twice and never again. Audio appears to never start.",
               warn_style))

story.append(P("7c — Parameter Settings tab (now go back)", h2))
story.append(make_table([
    ['Field', 'Value'],
    ['Clock Prescaler', 'PCLK2 div 4'],
    ['Resolution', '12 bits  (NOT 8 — see Section 16 lessons learned)'],
    ['Continuous Conversion Mode', 'Disabled'],
    ['DMA Continuous Requests', 'Enabled (becomes selectable only AFTER the DMA is added in 7b)'],
    ['External Trigger Conversion Source', 'Timer 2 Trigger Out event'],
    ['External Trigger Conversion Edge', 'Trigger detection on the rising edge'],
    ['ADC_Regular_ConversionMode &rarr; Number Of Conversion', '1'],
    ['Rank 1 (expand the triangle) &rarr; Channel', 'Channel 0'],
    ['Rank 1 &rarr; Sampling Time', '15 Cycles'],
], col_widths=[7.5 * cm, 7 * cm]))

story.append(P("7d — NVIC Settings tab", h2))
steps = [
    "Enable <b>DMA2 stream0 global interrupt</b>.",
    "Enable <b>ADC1 global interrupt</b> (or <b>ADC1, ADC2 and ADC3 global interrupts</b>).",
]
for s in steps:
    story.append(P("• " + s, bullet))

# ----- STEP 8: I2C1 -----
story.append(P("STEP 8 — I2C1 (for MCP4725)", h1))
steps = [
    "Left tree &rarr; <b>Connectivity &rarr; I2C1</b>.",
    "Mode = <b>I2C</b>.",
    "PB6 turns yellow as SCL, PB7 turns yellow as SDA on the chip diagram.",
    "Parameter Settings &rarr; I2C Speed Mode = <b>Fast Mode</b>.",
    "Parameter Settings &rarr; I2C Clock Speed (Hz) = <b>400000</b>.",
    "Parameter Settings &rarr; Fast Mode Duty Cycle = <b>2</b>.",
]
for s in steps:
    story.append(P("• " + s, bullet))

# ----- STEP 9: GPIO -----
story.append(P("STEP 9 — GPIO PC13 (LED Heartbeat)", h1))
steps = [
    "On the chip diagram, click <b>PC13</b> &rarr; select <b>GPIO_Output</b>.",
    "Left tree &rarr; <b>System Core &rarr; GPIO</b> &rarr; click the PC13 row.",
    "Set: GPIO output level = <b>High</b>, GPIO mode = <b>Output Push Pull</b>, no pull-up/down, low speed.",
    "User Label = <b>LED</b>.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(PageBreak())

# ----- STEP 10: Project Manager -----
story.append(P("STEP 10 — Project Manager and Generate Code", h1))
story.append(make_table([
    ['Field', 'Value'],
    ['Project Name', 'MicDAC'],
    ['Project Location', 'C:\\STM32\\  (or any easy path)'],
    ['Toolchain / IDE', 'CMake'],
    ['Linker — Min Heap Size', '0x800'],
    ['Linker — Min Stack Size', '0x800'],
], col_widths=[5 * cm, 9.5 * cm]))
story.append(P("Code Generator sub-tab:", h2))
steps = [
    "Tick <b>Generate peripheral initialization as a pair of '.c/.h' files per peripheral</b>.",
    "Tick <b>Keep User Code when re-generating</b>.",
    "Click <b>GENERATE CODE</b> (top right).",
    "Close STM32CubeMX once the dialog finishes.",
]
for s in steps:
    story.append(P("• " + s, bullet))

# ----- STEP 11: VS Code -----
story.append(P("STEP 11 — Open in VS Code", h1))
steps = [
    "Open VS Code.",
    "<b>File &rarr; Open Folder</b> &rarr; browse to <b>C:\\STM32\\MicDAC</b> &rarr; Select Folder.",
    "When prompted, click &laquo;Yes, I trust the authors&raquo;.",
    "Click the STM32 icon in the left sidebar.",
    "Click <b>Setup STM32Cube project(s)</b> when it activates.",
    "Wait for the CMake configuration to finish (status bar at the bottom).",
]
for s in steps:
    story.append(P("• " + s, bullet))

# ----- STEP 12: Edit main.c -----
story.append(P("STEP 12 — Edit Core/Src/main.c", h1))
story.append(P("Add the snippets to the marked USER CODE regions. Save (Ctrl+S) when done.", body))

story.append(P("12a &mdash; USER CODE BEGIN PD (private defines)", h2))
story.append(code('''/* USER CODE BEGIN PD */
#define BUF_SIZE      256
#define HALF_SIZE     (BUF_SIZE / 2)
#define MCP4725_ADDR  (0x60 << 1)
/* USER CODE END PD */'''))

story.append(P("12b &mdash; USER CODE BEGIN PV (private variables)", h2))
story.append(code('''/* USER CODE BEGIN PV */
uint16_t adc_buffer[BUF_SIZE];   /* 12-bit samples -> uint16_t, NOT uint8_t */
volatile uint8_t  half_ready = 0;
volatile uint8_t  full_ready = 0;
volatile uint16_t dac_play_idx = 0;
/* USER CODE END PV */'''))

story.append(P("12c &mdash; USER CODE BEGIN 2 (inside main(), after MX_*_Init)", h2))
story.append(code('''  /* USER CODE BEGIN 2 */
  HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, BUF_SIZE);
  HAL_TIM_Base_Start(&htim2);
  HAL_TIM_Base_Start_IT(&htim3);
  /* USER CODE END 2 */'''))

story.append(P("12d &mdash; Main while-loop (USER CODE BEGIN WHILE)", h2))
story.append(P("Make sure both closing braces are present &mdash; one for while(1), one for main(). "
               "This is the most common build error in this phase.", warn_style))
story.append(code('''  /* USER CODE BEGIN WHILE */
  while (1)
  {
    if (half_ready || full_ready) {
        half_ready = 0;
        full_ready = 0;
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);   /* heartbeat */
    }
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }   /* <-- closes while(1)  */
  /* USER CODE END 3 */
}     /* <-- closes main()    */'''))

story.append(P("12e &mdash; USER CODE BEGIN 4 (callbacks at end of main.c)", h2))
story.append(code('''/* USER CODE BEGIN 4 */
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) half_ready = 1;
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) full_ready = 1;
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM3) {
        /* ADC sample is now 12-bit (0..4095). DAC accepts 12-bit directly,
           no shifting required. Direct passthrough. */
        uint16_t v12 = adc_buffer[dac_play_idx];

        /* MCP4725 Fast-Write packet: top 4 bits + low 8 bits */
        uint8_t pkt[2] = {
            (uint8_t)((v12 >> 8) & 0x0F),
            (uint8_t)(v12 & 0xFF)
        };

        /* BLOCKING I2C, NOT _IT.  HAL_I2C_Master_Transmit_IT requires
           the I2C event interrupt to be enabled in NVIC; the default
           CubeMX config does NOT enable it.  Blocking version polls the
           I2C status register itself and works without that NVIC flag.
           At 400 kHz Fast Mode, 2 bytes take ~75 us, fits in 125 us tick. */
        HAL_I2C_Master_Transmit(&hi2c1, MCP4725_ADDR, pkt, 2, 1);

        dac_play_idx = (dac_play_idx + 1) % BUF_SIZE;
    }
}
/* USER CODE END 4 */'''))

story.append(PageBreak())

# ----- STEP 13: Build -----
story.append(P("STEP 13 — Build", h1))
steps = [
    "Press <b>Ctrl + S</b> to save main.c.",
    "Press <b>Ctrl + Shift + B</b> &rarr; pick <b>Build</b> from the dropdown.",
    "Watch the terminal panel at the bottom of VS Code for the build output.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(P("Expected output:", h2))
story.append(code('''[16/16] Linking C executable MicDAC.elf
   text    data     bss     dec     hex filename
   ...
Build finished. 0 errors, 0 warnings.'''))
story.append(P("If there are errors, do not flash. Read the error message and verify the USER CODE "
               "regions are correctly closed (Step 12d). The most common issue is a missing closing "
               "brace at the end of main().", body))

# ----- STEP 14: Flash -----
story.append(P("STEP 14 — Flash", h1))
steps = [
    "Verify ST-Link wiring: SWDIO &harr; DIO, SWCLK &harr; CLK, GND &harr; GND.",
    "Power the Black Pill via USB-C (do NOT also wire the ST-Link 3.3 V to the board).",
    "Plug the input headset into TRRS#1 and the output headphones into TRRS#2.",
    "Click the <b>Run</b> button in VS Code's Run/Debug view (or in the STM32 sidebar).",
    "The first time, an &laquo;Edit Configuration&raquo; dialog appears &mdash; accept defaults.",
]
for s in steps:
    story.append(P("• " + s, bullet))
story.append(P("Expected console output:", h2))
story.append(code('''Memory Programming ...
File download complete
Time elapsed during download operation: ~1s
Application is running, Reset device.'''))

# ----- STEP 15: Test -----
story.append(P("STEP 15 — Test", h1))
steps = [
    "Confirm the LM386 gain knob is at minimum (fully counter-clockwise).",
    "Hold the input headset and the output headphones <b>physically apart</b> &mdash; do not put either on the head yet (acoustic feedback prevention).",
    "Place one earbud loosely near the ear, do not insert.",
    "Speak softly into the input headset's mic.",
    "Slowly turn the LM386 gain knob clockwise while listening.",
    "When the voice becomes audible, the loop is closed.",
]
for s in steps:
    story.append(P("• " + s, bullet))

story.append(P("Expected behavior", h2))
story.append(make_table([
    ['Stimulus', 'Expected Result'],
    ['Silence', 'Quiet hiss in earbud'],
    ['Speaking normally', 'Your own voice reproduced with imperceptible delay (~30 ms)'],
    ['Whistling', 'Whistle reproduced clearly'],
    ['Clap or tap on mic', 'Reproduced as a short impulse'],
    ['PC13 onboard LED', 'Toggles many times per second &mdash; appears as a steady dim glow'],
], col_widths=[5 * cm, 9.5 * cm]))

story.append(P("Pass criterion: voice is clearly audible in the headphones, and removing power to "
               "the Black Pill makes the audio cut out (proves the audio path goes through the "
               "STM32, not directly through the analog hardware).",
               success_style))

story.append(PageBreak())

# ----- Lessons Learned -----
story.append(P("Section 16 — Lessons Learned (from the actual build)", h1))
story.append(P("This section documents every issue encountered during the live build of Phase 3, "
               "in the order they were discovered and fixed. Earlier versions of this document "
               "had the wrong configuration for several of these and were corrected only after "
               "live debugging.", body))

story.append(P("16.1 — DMA Continuous Requests was grayed out", h2))
story.append(P("<b>Symptom:</b> the DMA Continuous Requests field in ADC1 Parameter Settings "
               "could not be enabled (greyed out / not selectable).<br/>"
               "<b>Cause:</b> CubeMX requires the DMA channel to be added FIRST in the DMA "
               "Settings tab before that checkbox becomes selectable.<br/>"
               "<b>Fix:</b> always configure ADC1 in this order: enable channel &rarr; DMA Settings "
               "tab (Add ADC1, set Circular + Half Word) &rarr; THEN go back to Parameter Settings "
               "and toggle DMA Continuous Requests = Enabled.", body))

story.append(P("16.2 — Sampling Time field was missing", h2))
story.append(P("<b>Symptom:</b> Could not find Sampling Time in the Parameter Settings list, "
               "only ADC_Injected_ConversionMode was visible.<br/>"
               "<b>Cause:</b> Sampling Time lives inside the expandable <b>Rank 1</b> entry of "
               "ADC_Regular_ConversionMode (a different section from Injected). It only appears "
               "after Number Of Conversion is set to 1.<br/>"
               "<b>Fix:</b> set ADC_Regular_ConversionMode &rarr; Number Of Conversion = 1, then "
               "click the small triangle next to Rank 1 to expand it, then set Channel and "
               "Sampling Time inside.", body))

story.append(P("16.3 — DMA Mode was Normal instead of Circular", h2))
story.append(P("<b>Symptom:</b> the PC13 heartbeat LED never glowed; main loop never saw "
               "half_ready/full_ready set.<br/>"
               "<b>Cause:</b> in CubeMX DMA Settings, Mode defaulted to Normal. With Normal mode "
               "the DMA stops after one full transfer (~32 ms in our config) and never restarts. "
               "The half-complete and full-complete callbacks fire exactly twice on boot, then "
               "never again, which is invisible to the user.<br/>"
               "<b>Fix:</b> change DMA Mode &rarr; Circular and regenerate code.", body))

story.append(P("16.4 — Tying GAIN pin of MAX9814 to VDD silenced the mic", h2))
story.append(P("<b>Symptom:</b> after wiring MAX9814 GAIN pad to the 3.3 V rail (per datasheet "
               "this should set 40 dB gain), the mic produced no signal at all.<br/>"
               "<b>Cause:</b> on the user's specific MAX9814 clone breakout, the GAIN pin "
               "appears to be wired in a way that conflicts with an external pull-up. Setting "
               "GAIN externally disabled the chip's input.<br/>"
               "<b>Fix:</b> leave the GAIN pin floating. Default 60 dB gain is more amplification "
               "than ideal but works reliably.", body))

story.append(P("16.5 — HAL_I2C_Master_Transmit_IT did not transfer", h2))
story.append(P("<b>Symptom:</b> MCP4725 OUT showed exactly one DC value (~1.6 V) regardless of "
               "audio. DAC was not updating per sample. User heard hiss but no voice.<br/>"
               "<b>Cause:</b> the _IT (interrupt-driven) HAL function requires the I&sup2;C event "
               "interrupt to be enabled in NVIC. CubeMX's default I&sup2;C generation in this "
               "project did NOT add HAL_NVIC_EnableIRQ(I2C1_EV_IRQn). The first byte of the "
               "first transfer went out, then the I&sup2;C peripheral got stuck waiting for an "
               "event interrupt that never fired. All subsequent calls returned HAL_BUSY.<br/>"
               "<b>Fix:</b> use the blocking variant <b>HAL_I2C_Master_Transmit</b> "
               "(without the _IT suffix) in the TIM3 ISR. Blocking transfers poll the status "
               "register and complete in ~75 &mu;s at 400 kHz, well within the 125 &mu;s tick "
               "period. Alternative fix would have been to enable I&sup2;C event/error interrupts "
               "in CubeMX NVIC Settings, but the code change is simpler and equally effective.", body))

story.append(P("16.6 — Missing 1 &mu;F cap between DAC and LM386 caused silence", h2))
story.append(P("<b>Symptom:</b> after fixing the I&sup2;C transfer issue (16.5), the DAC was "
               "updating but the user still heard only hiss. The LM386 finger-touch test still "
               "produced hum, so the amplifier itself was fine.<br/>"
               "<b>Cause:</b> the MCP4725 OUT sits at ~1.6 V DC (mid-rail with the boosted code). "
               "Without a series capacitor, this DC offset is fed straight into the LM386 input, "
               "which DC-couples to it and prevents AC audio from being amplified.<br/>"
               "<b>Fix:</b> add a 1 &mu;F capacitor in series between MCP4725 OUT and LM386 IN. "
               "The cap blocks DC, passes AC. With this in place voice came through.", body))

story.append(P("16.7 — Robotic-sounding voice with 8-bit ADC", h2))
story.append(P("<b>Symptom:</b> after all the above fixes, voice was finally audible, but it "
               "sounded heavily robotic / digital / quantized.<br/>"
               "<b>Cause:</b> 8-bit ADC has only 256 levels = ~48 dB SNR theoretical. The audible "
               "stepping between values produces a robotic timbre on voice.<br/>"
               "<b>Fix:</b> upgrade to 12-bit ADC (4096 levels = 72 dB SNR, 16x cleaner). In "
               "CubeMX: ADC1 Resolution = 12 bits, DMA data widths Peripheral and Memory both = "
               "Half Word. In code: change buffer type from uint8_t to uint16_t and remove the "
               "&lt;&lt; 4 shift in the TIM3 ISR (ADC and DAC are now both 12-bit native, direct "
               "passthrough). Voice immediately sounded natural.", body))

story.append(PageBreak())

# ----- Troubleshooting -----
story.append(P("Troubleshooting", h1))
story.append(make_table([
    ['Symptom', 'Likely Cause', 'Fix'],
    ['Total silence',
     'MCP4725 not powered, A0 floating, OUT not connected to LM386 IN',
     'Multimeter on MCP4725 VDD = 3.3V; verify A0 to GND; verify wire 15'],
    ['Distorted / clipping',
     'LM386 gain too high, or DC bias not subtracted',
     'Lower LM386 gain; or apply bias correction in firmware (subtract ~96)'],
    ['LED PC13 not flickering',
     'ADC DMA not running &mdash; main loop never sees half_ready/full_ready',
     'Re-check Step 7: DMA Continuous Requests = Enabled, NVIC for DMA2 Stream0 enabled'],
    ['Build error: hi2c1 undeclared',
     'I2C1 not enabled in CubeMX',
     'Re-do Step 8, regenerate code'],
    ['Build error: htim3 undeclared',
     'TIM3 not configured in CubeMX',
     'Re-do Step 6, regenerate code'],
    ['Build error: expected declaration at end of input',
     'Missing closing brace in main.c',
     'Re-check Step 12d &mdash; both } at the end (one for while, one for main)'],
    ['Audio is just a steady tone, no voice',
     'TIM3 firing too fast or HAL_I2C_Master_Transmit_IT returning busy',
     'Verify TIM3 PSC=83, ARR=124; verify NVIC priorities (I2C above TIM3)'],
    ['Audio crackles / drops out',
     'I&sup2;C transfers not finishing in time',
     'Verify I2C1 at 400 kHz, NVIC priorities correct'],
    ['Flash error: target locked',
     'SWD disabled in CubeMX (SYS &rarr; Debug = None instead of Serial Wire)',
     'Recovery: hold BOOT0, reset, mass-erase via STM32CubeProgrammer; then fix Step 3'],
    ['Squealing feedback',
     'Input mic too close to output earbuds',
     'Hold them apart, lower LM386 gain'],
], col_widths=[4 * cm, 5 * cm, 5.5 * cm]))

story.append(P("Diagnostic Sequence (if the loopback is silent)", h2))
diag = [
    "<b>Power check.</b> Multimeter on MCP4725 VDD vs GND &mdash; should be 3.3 V.",
    "<b>I&sup2;C scan.</b> Add a temporary loop in firmware that calls "
    "HAL_I2C_IsDeviceReady on addresses 1..127 and toggles the LED for each one found. "
    "You should detect 0x60.",
    "<b>DC test.</b> Replace the TIM3 ISR body with two alternating writes "
    "(0x000 and 0xFFF) with HAL_Delay between them. Multimeter on MCP4725 OUT should "
    "toggle between 0 V and 3.3 V every second.",
    "<b>Tone test.</b> Generate a 500 Hz square wave on the DAC. You should hear a "
    "clean low-pitched beep in the headphones.",
    "<b>Loopback test.</b> Only after all of the above pass, run the full firmware "
    "and you should hear yourself.",
]
for d in diag:
    story.append(P("• " + d, bullet))

story.append(P("What This Phase Proves", h1))
proves = [
    "I&sup2;C peripheral is correctly configured at 400 kHz.",
    "MCP4725 DAC is responding at address 0x60.",
    "TIM3 fires at exactly 8 kHz, locked to the same clock as TIM2.",
    "Interrupt-driven I&sup2;C completes within the 125 &mu;s budget every cycle.",
    "ADC and DAC sample rates are synchronised &mdash; no buffer overruns or underruns.",
    "The full real-time digital audio loop closes &mdash; every sample lives briefly in the STM32's RAM.",
    "Total system latency is approximately 32 ms (one half-buffer at 8 kHz) plus negligible processing time.",
]
for p in proves:
    story.append(P("• " + p, bullet))

story.append(P("After this phase passes, the next milestones are: <b>Phase 4</b> &mdash; LTE module "
               "manual AT-command bring-up, <b>Phase 5</b> &mdash; STM32 drives the LTE module, "
               "<b>Phase 6</b> &mdash; two-node plain audio over LTE, <b>Phase 7</b> &mdash; add "
               "RSA + AES hybrid encryption, <b>Phase 8</b> &mdash; phone-number call setup &amp; demo polish.",
               body))

story.append(Spacer(1, 0.5 * cm))
story.append(P("End of Phase 3 step-by-step document.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 3 — Steps From Scratch",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")
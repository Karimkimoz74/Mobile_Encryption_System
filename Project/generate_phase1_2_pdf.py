"""
Generates a PDF documenting Phase 1 (completed) and Phase 2 (next step)
of the Secure Voice Communication System project.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase1_and_Phase2_Plan.pdf"

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'TitleBig', parent=styles['Title'],
    fontSize=20, leading=26, alignment=TA_CENTER,
    textColor=colors.HexColor('#0B3D91'), spaceAfter=10)

subtitle_style = ParagraphStyle(
    'SubTitle', parent=styles['Normal'],
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
    fontSize=10, leading=14, alignment=TA_JUSTIFY,
    spaceAfter=6)

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


def P(t, s=body):
    return Paragraph(t, s)


def code(t):
    return Preformatted(t, code_style)


def ascii_block(t):
    return Preformatted(t, ascii_style)


cell_style = ParagraphStyle('CellBody', parent=styles['Normal'],
    fontName='Helvetica', fontSize=8.5, leading=11,
    spaceBefore=0, spaceAfter=0, alignment=0)

cell_header_style = ParagraphStyle('CellHeader', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=9, leading=11,
    textColor=colors.white,
    spaceBefore=0, spaceAfter=0, alignment=0)


def wrap_cell(value, header_row=False):
    """Wrap any string cell in a Paragraph so it word-wraps within the column."""
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
        cmds += [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B3D91')),
        ]
    t.setStyle(TableStyle(cmds))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm,
                      "Secure Voice Project | Phase 1 Report & Phase 2 Plan")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ---------------- BUILD STORY ----------------
story = []

# Title
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 1 Completion Report<br/>&amp; Phase 2 Plan", title_style))
story.append(P("Secure Real-Time Voice Communication System using STM32 and LTE", subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P(
    "<b>Phase 1:</b> Analog Talkback Verification with Modified MAX9814 + Headset Microphone &nbsp;&nbsp;<b>STATUS: COMPLETED</b>",
    success_style))
story.append(P(
    "<b>Phase 2 (next):</b> STM32 ADC Voice Detection with Onboard LED Indicator",
    body))
story.append(PageBreak())

# ============== PHASE 1 ==============
story.append(H1 := P("PHASE 1 — Analog Talkback Verification (COMPLETED)", h1))

story.append(P("Goal", h2))
story.append(P("Verify that all analog audio components — microphone, amplifier, jacks, and headphones — "
               "work end-to-end as a continuous signal chain, before introducing any microcontroller. "
               "If a person can speak into the microphone and hear themselves in the headphones, all "
               "analog hardware is proven good and the project can move on to digital processing."))

story.append(P("Approach", h2))
story.append(P("Build a pure analog circuit (no STM32 firmware needed) in which the microphone signal "
               "is amplified by the MAX9814, AC-coupled through a 1 µF capacitor into the LM386 power "
               "amplifier, and routed through a TRRS jack to standard headphones. The Black Pill is "
               "used as a power source only — its 3.3 V and 5 V rails feed the boards."))

story.append(P("Components Used", h2))
parts = [
    ['#', 'Component', 'Role'],
    ['1', 'STM32F401 Black Pill', 'Power source (3.3 V and 5 V rails). No firmware required.'],
    ['2', 'MAX9814 (modified)', 'Microphone preamplifier with AGC. Onboard electret mic was physically removed.'],
    ['3', '1 µF capacitor', 'AC coupling between MAX9814 OUT and LM386 IN to block DC bias.'],
    ['4', 'LM386 module', 'Power amplifier. Drives the headphones from the MAX9814 audio signal.'],
    ['5', 'TRRS jack breakout', 'Female 3.5 mm socket. Provides access to all 4 conductors of the headset plug.'],
    ['6', 'TRRS headset', 'Provides BOTH the microphone (from the headset cable) and the speakers (earbuds).'],
    ['7', 'Breadboard + jumpers', 'Mechanical connection of the above components.'],
]
story.append(make_table(parts, col_widths=[1 * cm, 4.5 * cm, 9 * cm]))

story.append(P("Critical Modification — Onboard Mic Removal", h2))
story.append(P("The MAX9814 breakout ships with a small electret microphone soldered to its PCB. "
               "On a breadboard, this onboard mic picks up significant environmental noise (50/60 Hz "
               "hum, breadboard noise, RF). To improve signal quality, the onboard mic was physically "
               "removed and replaced with the higher-quality microphone built into the TRRS headset."))

story.append(P("Removal procedure:", h3))
removal = [
    "Located the small cylindrical electret microphone on the MAX9814 board.",
    "Cut the two leads connecting the mic to the PCB (or desoldered for non-destructive removal).",
    "Two empty solder pads remained on the PCB where the mic used to sit.",
    "Identified the two pads using PCB trace inspection AND multimeter continuity:",
]
for r in removal:
    story.append(P("• " + r, bullet))
sub = [
    "<b>MIC+ pad</b> — the empty pad whose trace runs toward the MAX9814 chip body. This is the analog input to the chip's internal amplifier.",
    "<b>GND pad</b> — the empty pad whose trace joins the wider ground copper. Used as the return path.",
]
for s in sub:
    story.append(P("&nbsp;&nbsp;&nbsp;&nbsp;◦ " + s, bullet))

story.append(P("Headset Microphone Wiring (CTIA standard)", h2))
story.append(P("A standard Android/iPhone TRRS headset uses the CTIA pinout. The microphone signal "
               "is on the <b>Sleeve</b> conductor of the plug, with the microphone's ground return on "
               "<b>Ring 2</b>. The TRRS jack breakout exposes these as labeled pads:"))
trrs = [
    ['Plug Section', 'Carries (CTIA)', 'Wired to'],
    ['Tip', 'Left audio (output)', 'LM386 + (speaker output, both ears get same signal)'],
    ['Ring 1', 'Right audio (output)', 'LM386 + (same wire as Tip)'],
    ['Ring 2', 'Ground', 'Common GND rail (also serves as headphone return)'],
    ['Sleeve', 'Microphone (input)', 'MAX9814 MIC+ pad (the empty pad after mic removal)'],
]
story.append(make_table(trrs, col_widths=[3 * cm, 5 * cm, 6.5 * cm]))

story.append(P("Final Circuit — Block Diagram", h2))
story.append(ascii_block(r"""
   YOUR VOICE                                                        YOUR EARS
       v                                                                ^
       v                                                                |
   ┌─────────┐    ┌─────────────┐  1uF  ┌────────┐         ┌─────────┐  |
   │ headset │    │  MAX9814    │ cap   │ LM386  │         │ headset │  |
   │  (mic)  │----│ (mic chip   │--||---│  amp   │--------→│ speaker │--+
   │         │    │  removed)   │       │        │         │         │
   └─────────┘    └─────────────┘       └────────┘         └─────────┘
        |              ^                                       ^
        |              |                                       |
   TRRS Sleeve     MIC+ pad                                LM386 +
   TRRS Ring2      GND pad                                LM386 GND
""".strip()))

story.append(P("Final Circuit — Complete Wire List (14 wires + 1 capacitor)", h2))
wires = [
    ['Section', '#', 'From', 'To'],
    ['Power rails', '1', 'Black Pill 3V3 pin', 'Top + rail of breadboard'],
    ['', '2', 'Black Pill 5V pin', 'Bottom + rail of breadboard'],
    ['', '3', 'Black Pill GND pin', 'Top − rail of breadboard'],
    ['', '4', 'Top − rail', 'Bottom − rail (so all GND is one)'],
    ['MAX9814 power', '5', 'MAX9814 VDD', 'Top + rail (3.3 V)'],
    ['', '6', 'MAX9814 GND', '− rail (GND)'],
    ['Headset mic in', '7', 'TRRS Sleeve pad', 'MAX9814 MIC+ empty pad'],
    ['', '8', 'TRRS Ring 2 pad', '− rail (GND)'],
    ['Audio coupling', '9', 'MAX9814 OUT pin', '1 µF cap → LM386 IN (header pin)'],
    ['LM386 power', '10', 'LM386 VCC (header)', 'Bottom + rail (5 V)'],
    ['', '11', 'LM386 GND (header)', '− rail (GND)'],
    ['Speaker output', '12', 'LM386 green terminal +', 'TRRS Tip pad'],
    ['', '13', 'LM386 green terminal +', 'TRRS Ring 1 pad'],
    ['', '14', 'LM386 green terminal −', '− rail (GND)'],
]
story.append(make_table(wires, col_widths=[3 * cm, 1 * cm, 5 * cm, 5.5 * cm]))

story.append(PageBreak())

story.append(P("Test Procedure", h2))
test = [
    "Plug Black Pill into PC via USB-C. Red power LED lights up.",
    "Multimeter check: 3.30 V between top + rail and GND, 4.7–5.1 V between bottom + rail and GND.",
    "Plug TRRS headset into the TRRS jack breakout.",
    "Turn LM386 gain potentiometer fully counter-clockwise (minimum gain).",
    "Hold the headset in the hand — DO NOT put it on the head (mic and earbuds too close → acoustic feedback).",
    "Hold the headset's mic near the mouth, earbuds at arm's length away from the face.",
    "Place one earbud loosely near the ear.",
    "Slowly rotate the LM386 gain knob clockwise while speaking softly.",
    "When voice becomes audible in the earbud, gain is correctly set.",
]
for s in test:
    story.append(P("• " + s, bullet))

story.append(P("Result", h2))
story.append(P("✓ Clear, clean voice reproduction in the earbuds.<br/>"
               "✓ Significantly lower noise floor compared to the un-modified MAX9814 (with onboard mic).<br/>"
               "✓ All analog components verified working end-to-end.<br/>"
               "✓ TRRS pinout confirmed as CTIA standard for the available headset.",
               success_style))

story.append(P("Lessons Learned", h2))
lessons = [
    "<b>Modular testing pays off.</b> Verifying the entire analog chain before introducing the microcontroller eliminated several debugging variables for later phases.",
    "<b>Onboard mics on breadboards are noisy.</b> The MAX9814's onboard electret was the dominant noise source; replacing it with the headset mic (which sits at the mouth, far from breadboard noise) dramatically improved SNR.",
    "<b>The MAX9814's bias circuit is universal.</b> Once the onboard mic is removed, the breakout can power any electret microphone connected to its empty pads — no external bias resistor required.",
    "<b>Acoustic feedback is unavoidable</b> when input mic and output speakers share the same headset. The workaround is to hold them physically apart during testing; in the final project the two devices are physically separated.",
    "<b>The TRRS jack is purely a connector</b> — no electronics inside. The 4 pads on the breakout are direct passthroughs to the 4 conductors on the plug (Tip, Ring 1, Ring 2, Sleeve).",
]
for l in lessons:
    story.append(P("• " + l, bullet))

story.append(PageBreak())

# ============== PHASE 2 ==============
story.append(P("PHASE 2 — STM32 ADC Voice Detection (NEXT)", h1))

story.append(P("Goal", h2))
story.append(P("Prove that the STM32F401 microcontroller can read audio samples from the microphone "
               "via its built-in ADC. Provide visual confirmation by lighting the onboard PC13 LED "
               "whenever sound is detected by the mic. This bridges the project from pure analog to "
               "digital firmware and lays the foundation for all subsequent phases (DAC playback, "
               "encryption, LTE transmission)."))

story.append(P("Why this approach (Option A — LED indicator)", h2))
story.append(P("Three options were considered for visualizing the ADC output:"))
opts = [
    ['Option', 'Method', 'Extra Hardware', 'Pros', 'Cons'],
    ['A (chosen)', 'Onboard PC13 LED reacts to audio', 'None', 'Simplest, no extra parts, immediate visual feedback', 'No numeric data, only ON/OFF'],
    ['B', 'USB-TTL adapter to PC terminal', 'USB-TTL adapter (CH340/CP2102)', 'See actual sample values', 'Requires extra ~15 LE adapter'],
    ['C', 'USB CDC virtual COM via Black Pill USB-C', 'None', 'No extra parts', 'Significantly more CubeMX setup, USB middleware required'],
]
story.append(make_table(opts, col_widths=[2 * cm, 3.5 * cm, 2.5 * cm, 3.5 * cm, 3.5 * cm]))
story.append(P("<b>Option A is selected for Phase 2</b> because it gives immediate, unambiguous "
               "confirmation that the ADC is functioning, with zero additional hardware. Once Phase 2 "
               "passes, Phase 2.5 or Phase 3 can upgrade to Option B or C for full visualization."))

story.append(P("Wiring Changes from Phase 1", h2))
story.append(P("The audio signal currently flowing into the LM386 needs to be redirected into the "
               "STM32's ADC pin (PA0). The LM386 / output speaker portion of the circuit can be "
               "physically left in place but is not used in Phase 2."))
story.append(ascii_block(r"""
   PHASE 1 (was):
        MAX9814 OUT --[1uF cap]--> LM386 IN --> headphones

   PHASE 2 (new):
        MAX9814 OUT -------------> PA0 (STM32 ADC input)
                                    |
                                    v
                              process samples
                                    |
                                    v
                          if (loud) -> turn ON PC13 LED
                          if (quiet) -> turn OFF PC13 LED
""".strip()))

story.append(P("Wires to change", h3))
chg = [
    ['Action', 'Wire', 'Notes'],
    ['REMOVE', '1 µF cap between MAX9814 OUT and LM386 IN', 'No longer needed; STM32 ADC accepts the DC-biased signal directly.'],
    ['REMOVE (optional)', 'LM386 power and output wires', 'Can leave in place — they will be re-used in later phases.'],
    ['ADD', 'MAX9814 OUT → STM32 PA0', 'Direct wire. PA0 is ADC1 channel 0.'],
    ['KEEP', 'MAX9814 power (VDD/GND), TRRS Sleeve → MAX9814 MIC+ pad, TRRS Ring2 → GND', 'These confirm the headset mic is feeding the MAX9814 just like Phase 1.'],
]
story.append(make_table(chg, col_widths=[3 * cm, 6 * cm, 5.5 * cm]))

story.append(P("CubeMX Configuration", h2))
story.append(P("Use the existing SecureVoice CubeMX project (from project documentation), or create a "
               "fresh minimal project with only the peripherals needed for Phase 2. The minimum set is:"))

cubemx_min = [
    ['Peripheral', 'Setting', 'Value'],
    ['RCC', 'High Speed Clock (HSE)', 'Crystal/Ceramic Resonator'],
    ['SYS', 'Debug', 'Serial Wire (critical — prevents bricking after first flash)'],
    ['Clock', 'HCLK', '84 MHz (PLL: M=25, N=336, P=4)'],
    ['ADC1', 'IN0 channel', 'Enabled (PA0)'],
    ['ADC1', 'Resolution', '8 bits'],
    ['ADC1', 'Continuous Conversion', 'Disabled'],
    ['ADC1', 'DMA Continuous Requests', 'Enabled'],
    ['ADC1', 'External Trigger Source', 'Timer 2 Trigger Out event, Rising edge'],
    ['ADC1', 'Sampling Time', '15 cycles'],
    ['ADC1 DMA', 'Mode', 'Circular, Peripheral→Memory, Byte/Byte, Memory increment ON'],
    ['TIM2', 'Prescaler', '83'],
    ['TIM2', 'Counter Period', '124'],
    ['TIM2', 'Trigger Event Selection TRGO', 'Update Event'],
    ['GPIO PC13', 'Mode', 'Output Push-Pull, Low speed, no pull-up/down, label "LED"'],
    ['NVIC', 'Enabled', 'DMA2 Stream0 IRQ, ADC1 IRQ'],
]
story.append(make_table(cubemx_min, col_widths=[3 * cm, 5 * cm, 6.5 * cm]))
story.append(P("8 kHz sampling math: TIM2 clock = 84 MHz / ((83+1) × (124+1)) = 8000 Hz exactly.", note_style))

story.append(P("Firmware (paste into main.c)", h2))
story.append(P("Place each block in the correct USER CODE region. The CubeMX-generated init code "
               "(HAL_Init, SystemClock_Config, MX_GPIO_Init, MX_DMA_Init, MX_ADC1_Init, MX_TIM2_Init) "
               "stays untouched."))

story.append(P("Variables and buffers (USER CODE BEGIN PV)", h3))
story.append(code('''/* USER CODE BEGIN PD */
#define BUF_SIZE        256        /* total ping-pong buffer (samples) */
#define HALF_SIZE       (BUF_SIZE / 2)
#define VOICE_THRESHOLD 20         /* peak-to-peak threshold for "voice detected" */
/* USER CODE END PD */

/* USER CODE BEGIN PV */
uint8_t  adc_buffer[BUF_SIZE];
volatile uint8_t half_ready = 0;
volatile uint8_t full_ready = 0;
/* USER CODE END PV */'''))

story.append(P("Peripheral start (USER CODE BEGIN 2, inside main())", h3))
story.append(code('''/* USER CODE BEGIN 2 */
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, BUF_SIZE);
HAL_TIM_Base_Start(&htim2);
/* USER CODE END 2 */'''))

story.append(P("Main loop (USER CODE BEGIN WHILE)", h3))
story.append(code('''/* USER CODE BEGIN WHILE */
while (1)
{
    if (half_ready || full_ready) {
        uint8_t *chunk = half_ready ? &adc_buffer[0]
                                    : &adc_buffer[HALF_SIZE];
        half_ready = 0;
        full_ready = 0;

        /* Compute peak-to-peak amplitude of this chunk */
        uint8_t lo = 255, hi = 0;
        for (int i = 0; i < HALF_SIZE; i++) {
            if (chunk[i] < lo) lo = chunk[i];
            if (chunk[i] > hi) hi = chunk[i];
        }
        uint8_t amp = hi - lo;

        /* Drive PC13 LED — active LOW on the Black Pill */
        if (amp > VOICE_THRESHOLD) {
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);  /* LED ON */
        } else {
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);    /* LED OFF */
        }
    }
}
/* USER CODE END WHILE */'''))

story.append(P("ADC callbacks (USER CODE BEGIN 4)", h3))
story.append(code('''/* USER CODE BEGIN 4 */
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) half_ready = 1;
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) full_ready = 1;
}
/* USER CODE END 4 */'''))

story.append(PageBreak())

story.append(P("Test Procedure", h2))
proc = [
    "Modify the wiring as described in the 'Wires to change' table above.",
    "Open the CubeMX project, verify ADC1 + TIM2 + DMA + GPIO PC13 are configured. Generate code.",
    "Open the project in VS Code (STM32 extension) or STM32CubeIDE.",
    "Paste the firmware blocks into main.c at the indicated USER CODE regions.",
    "Build (Ctrl+Shift+B). Confirm 0 errors in the terminal/console.",
    "Connect ST-Link V2 to the Black Pill (SWDIO ↔ DIO, SWCLK ↔ CLK, GND ↔ GND).",
    "Power the board via USB-C (do NOT also power from the ST-Link's 3.3 V pin).",
    "Plug the headset into the TRRS jack — same as Phase 1.",
    "Click Run/Flash in the IDE. Wait for 'Download verified successfully'.",
]
for s in proc:
    story.append(P("• " + s, bullet))

story.append(P("Expected Results", h2))
results = [
    ['Stimulus', 'Expected LED behavior'],
    ['Silence (no sound)', 'PC13 LED is OFF'],
    ['Speaking normally into the headset mic', 'PC13 LED is ON while speaking, OFF in pauses'],
    ['Whistling continuously', 'PC13 LED stays ON'],
    ['Single sharp clap', 'PC13 LED briefly flashes'],
    ['Tapping the headset mic with finger', 'PC13 LED flickers with each tap'],
]
story.append(make_table(results, col_widths=[6 * cm, 8.5 * cm]))

story.append(P("Pass criterion: <b>the LED reliably reflects voice activity</b>. The exact threshold "
               "value (currently 20) can be tuned: lower for higher sensitivity, higher to reject "
               "background noise. If the LED is always on or always off, adjust VOICE_THRESHOLD in "
               "the firmware and re-flash.", body))

story.append(P("Troubleshooting", h2))
trouble = [
    ['Symptom', 'Likely Cause', 'Fix'],
    ['LED always ON, never reacts', 'ADC reads constant noise above threshold; or ADC stuck', 'Increase VOICE_THRESHOLD; verify TIM2 is started; check ADC DMA NVIC enabled'],
    ['LED always OFF, never reacts', 'ADC not converting; or PA0 not connected to MAX9814 OUT', 'Verify PA0 wire; verify ADC1 IN0 is enabled; verify HAL_ADC_Start_DMA was called'],
    ['LED responds but only to very loud sound', 'Threshold too high', 'Lower VOICE_THRESHOLD (try 10)'],
    ['LED responds to anything, even silence', 'Threshold too low; or noisy ground', 'Raise VOICE_THRESHOLD; verify common ground'],
    ['Build error: HAL_ADC_Start_DMA undefined', 'CubeMX did not generate ADC code', 'Re-open .ioc, ensure ADC1 is enabled, regenerate'],
    ['Compile OK but flash fails: target locked', 'SWD was disabled in CubeMX', 'Set SYS → Debug = Serial Wire, regenerate. If already flashed: hold BOOT0 + reset, mass-erase via STM32CubeProgrammer'],
]
story.append(make_table(trouble, col_widths=[4 * cm, 5 * cm, 5.5 * cm]))

story.append(P("What This Phase Proves", h2))
proves = [
    "The TIM2 timer is generating a precise 8 kHz trigger.",
    "The ADC is sampling PA0 at exactly 8 kHz, triggered by TIM2.",
    "DMA is moving samples from the ADC into RAM in circular mode without CPU intervention.",
    "Half-complete and full-complete callbacks are firing correctly.",
    "Main-loop processing of audio frames is running fast enough to handle the data rate.",
    "GPIO output (PC13 LED) responds correctly to firmware control.",
]
for p in proves:
    story.append(P("• " + p, bullet))
story.append(P("These are exactly the same primitives that will be used in every later phase, just with "
               "different actions in the main loop (encryption, transmission, etc.). Once Phase 2 passes, "
               "the digital input pipeline is verified."))

story.append(P("After Phase 2", h2))
story.append(P("Once the LED reliably reacts to voice, the next milestones are:"))
nxt = [
    "<b>Phase 2.5</b> — Upgrade to PC visualization (Option B or C) so actual sample values can be inspected.",
    "<b>Phase 3</b> — Add the MCP4725 DAC: ADC samples are written to the DAC at 8 kHz, producing a digital-domain mic-to-speaker loopback (full audio path running through the STM32).",
    "<b>Phase 4</b> — LTE module bring-up with manual AT commands.",
    "<b>Phase 5</b> — STM32 drives the LTE module, connects to the relay server, performs phone-number-based call setup.",
    "<b>Phase 6</b> — Plain audio over LTE between two devices (no encryption).",
    "<b>Phase 7</b> — Add RSA + AES hybrid encryption to the audio stream.",
    "<b>Phase 8</b> — Polish: physical buttons for call/answer, LED status states, demo prep.",
]
for n in nxt:
    story.append(P("• " + n, bullet))

story.append(Spacer(1, 0.5 * cm))
story.append(P("End of Phase 1 / Phase 2 document.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 1 & 2 Report",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")

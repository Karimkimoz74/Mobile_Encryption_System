"""
Generates Phase 6 PDF — Two-Device Voice Call (Submission 1).
Covers: buttons, CALL/INC/ANS/GO/HUP protocol, two-device setup,
LED states, audio streaming, full firmware additions, demo script.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase6_Two_Device_Voice_Call.pdf"

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
    fontName='Courier', fontSize=7.5, leading=9.5,
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
    return Paragraph(str(value), cell_header_style if header_row else cell_style)


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
                      "Secure Voice Project | Phase 6 — Two-Device Voice Call (Submission 1)")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

# ============== TITLE PAGE ==============
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 6<br/>Two-Device Voice Call", title_style))
story.append(P("Submission 1: Full-duplex voice between two devices over LTE — no encryption yet",
               subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P("<b>Goal:</b> Two physically separate devices identify each other by phone number "
               "through the relay, dial each other with a Call button, accept with an Answer "
               "button, and exchange voice in BOTH directions simultaneously over the cellular "
               "network. The Submission 1 deliverable to the supervisor.",
               body))
story.append(Spacer(1, 0.5 * cm))
story.append(P("<b>Builds on:</b> Phase 5.4 (one device auto-registering with the relay).<br/>"
               "<b>What's added:</b> Second physical device + push-buttons + call setup state "
               "machine + audio streaming through the relay.<br/>"
               "<b>Status:</b> In progress.<br/><br/>"
               "<b>Next after this:</b> Phase 7 (encryption — Submission 2).",
               success_style))
story.append(PageBreak())

# ============== Section 1 — Big Picture ==============
story.append(P("1. The Big Picture", h1))

story.append(P("Two physically separate devices, each with mic + speaker + STM32 + LTE modem, "
               "exchange voice through your relay server.", body))

story.append(ascii_block(r"""
   DEVICE A (Karim's home)                                   DEVICE B (friend's home)
   ───────────────────────                                   ───────────────────────────

   Headset mic ──> MAX9814 ──> ADC                ADC <── MAX9814 <── Headset mic
                              │                  ▲
                              │                  │
                          UART/TCP            UART/TCP
                              │                  │
                              ▼                  │
                       LTE modem            LTE modem
                              │                  ▲
                              │                  │
                              ▼                  │
                          4G ── Vodafone Egypt ── 4G
                              │                  │
                              └──── ngrok ───────┘
                                       │
                                       ▼
                                 relay.py (Karim's laptop)
                                       │
                                  forwards bytes
                                  between A and B

   Speaker <── LM386 <── DAC                       DAC ──> LM386 ──> Speaker
""".strip()))

story.append(P("During a call, every byte of voice flows: A's mic → A's STM32 → 4G → relay → "
               "4G → B's STM32 → B's speaker. Same in reverse. <b>Both at the same time</b> = "
               "full-duplex.", body))

# ============== Section 2 — What's NEW vs Phase 5.4 ==============
story.append(P("2. What's New Compared to Phase 5.4", h1))

newstuff = [
    ['Item', 'Phase 5.4', 'Phase 6 (new)'],
    ['Number of devices', '1 (Karim only)', '2 (Karim + friend)'],
    ['Phone numbers', '01000000001 only', '01000000001 + 01000000002'],
    ['Call setup', 'Just REG and idle', 'CALL → INC → ANS → GO state machine'],
    ['Buttons used', 'Wired but not used', 'PA1=Call, PB0=Answer/Hangup — actively used'],
    ['Audio streaming', 'Disabled (TIM3 commented)', 'Re-enabled — bytes flow during TALK state'],
    ['LED states', '2 (off / slow blink)', '4 (off / slow / fast / solid)'],
    ['Firmware complexity', 'Linear bring-up + idle', 'Full state machine'],
]
story.append(make_table(newstuff, col_widths=[3.5 * cm, 5 * cm, 6 * cm]))

# ============== Section 3 — Hardware ==============
story.append(P("3. Hardware Setup (per device)", h1))

story.append(P("3.1 — Both devices are identical", h2))
story.append(P("Each device needs the SAME hardware: STM32 Black Pill + LilyGO XY-A7608B + "
               "MAX9814 + MCP4725 + LM386 + 2 TRRS jacks + 2 push-buttons + headphones with "
               "mic. Both run the SAME firmware with only the phone number different.",
               body))

story.append(P("3.2 — Wires between STM32 and LilyGO (6 wires, same as Phase 5.4)", h2))
ww = [
    ['#', 'STM32', 'LilyGO', 'Function'],
    ['1', 'PA8', 'RST', 'ESP32 reset hold (LOW)'],
    ['2', 'PB1', 'IO12', 'Modem POWERON (HIGH)'],
    ['3', 'PB2', 'IO4', 'Modem PWRKEY (idle HIGH)'],
    ['4', 'PA9', 'IO26 (TX label)', 'STM32 → modem'],
    ['5', 'PA10', 'IO27 (RX label)', 'STM32 ← modem'],
    ['6', 'GND', 'GND', 'Common ground'],
]
story.append(make_table(ww, col_widths=[1 * cm, 2.5 * cm, 4 * cm, 7 * cm]))

story.append(P("3.3 — Audio chain (re-enabled in Phase 6, was Phase 3)", h2))
audio = [
    ['#', 'STM32', 'Connection', 'Purpose'],
    ['7', 'PA0', 'MAX9814 OUT', 'ADC sampling at 8 kHz, 12-bit'],
    ['8', 'PB6', 'MCP4725 SCL', 'I2C clock to DAC'],
    ['9', 'PB7', 'MCP4725 SDA', 'I2C data to DAC'],
    ['10', 'MCP4725 OUT', '1 µF cap → LM386 IN', 'AC-coupled audio to amplifier'],
    ['11', 'LM386 + → TRRS Tip+Ring1', 'Headphones', 'Output speakers'],
    ['12', 'TRRS Sleeve', 'MAX9814 MIC+ pad', 'Headset microphone'],
]
story.append(make_table(audio, col_widths=[1 * cm, 2.5 * cm, 5 * cm, 6 * cm]))

story.append(P("3.4 — Buttons (NEW — actively used in Phase 6)", h2))
btn = [
    ['#', 'STM32', 'Connection', 'Function'],
    ['13', 'PA1 (input pull-up)', 'Top leg of Call button; bottom leg → GND', 'Initiate a call to the peer'],
    ['14', 'PB0 (input pull-up)', 'Top leg of Answer button; bottom leg → GND', 'Accept incoming call OR hang up active call'],
]
story.append(make_table(btn, col_widths=[1 * cm, 3.5 * cm, 5.5 * cm, 4.5 * cm]))

story.append(P("Buttons read HIGH when not pressed (internal pull-up), LOW when pressed. "
               "Firmware detects HIGH→LOW transition with debouncing.",
               note_style))

story.append(P("3.5 — Power", h2))
story.append(P("Each device has its own:"))
power = [
    ['Item', 'Purpose'],
    ['STM32 Black Pill USB-C → PC (or charger)', 'Powers STM32; for programming via ST-Link'],
    ['LilyGO USB-C → phone charger or 18650', 'Powers LTE modem (needs 2 A burst capability)'],
    ['LM386 powered from STM32 5V (VBUS)', 'Audio output amplifier'],
    ['MAX9814, MCP4725 powered from STM32 3V3', 'Audio capture and DAC'],
]
story.append(make_table(power, col_widths=[6 * cm, 8.5 * cm]))

story.append(PageBreak())

# ============== Section 4 — Call Protocol ==============
story.append(P("4. Call Setup Protocol", h1))

story.append(P("All messages between device and relay are line-based ASCII terminated by "
               "<code>\\r\\n</code>. After the GO message, the connection switches to raw byte "
               "audio streaming.",
               body))

story.append(P("4.1 — Message reference", h2))
msgs = [
    ['Message', 'Direction', 'Meaning'],
    ['REG &lt;phone&gt;', 'device → relay', 'Register this device with this phone number'],
    ['OK', 'relay → device', 'Registration accepted'],
    ['CALL &lt;peer_phone&gt;', 'device → relay', 'Initiate call to peer'],
    ['RING', 'relay → caller', 'Your call is being delivered, peer is ringing'],
    ['INC &lt;caller_phone&gt;', 'relay → callee', 'Someone is calling you'],
    ['ANS', 'callee → relay', 'I accept the incoming call'],
    ['GO', 'relay → both', 'Both ends now in audio mode'],
    ['HUP', 'either side → relay', 'End the current call'],
    ['PEER_HUP', 'relay → other side', 'The other side hung up'],
    ['PEER_GONE', 'relay → other side', 'The other side disconnected unexpectedly'],
    ['ERR &lt;reason&gt;', 'relay → device', 'Command rejected (offline / busy / etc.)'],
]
story.append(make_table(msgs, col_widths=[4 * cm, 3 * cm, 7.5 * cm]))

story.append(P("4.2 — Full call flow (sequence diagram)", h2))
story.append(ascii_block(r"""
   Device A          relay             Device B
   ────────          ─────             ────────

   REG 01000000001 ───────►
                  ◄─────── OK
                                       REG 01000000002 ───────►
                                                      ◄─────── OK

   [user A presses Call button]
   CALL 01000000002 ──────►
                  ◄──── RING               INC 01000000001 ───►

                                       [user B presses Answer button]
                                                ANS ─────►
                  ◄────── GO                    GO ◄─────

   [TALK STATE — full-duplex audio bytes flow continuously]
   <encrypted? no — Phase 7> audio bytes ────────────────►
                                       ◄──────────────── audio bytes

   [user A presses Hangup]
   HUP ─────────────────►
                  ◄── OK              PEER_HUP ────────►

   [Both back to REGISTERED state, ready for next call]
""".strip()))

story.append(P("4.3 — Byte counts (for AT+CIPSEND)", h2))
counts = [
    ['Message', 'Bytes (incl. \\r\\n)'],
    ['REG 01000000001\\r\\n', '17'],
    ['REG 01000000002\\r\\n', '17'],
    ['CALL 01000000001\\r\\n', '18'],
    ['CALL 01000000002\\r\\n', '18'],
    ['ANS\\r\\n', '5'],
    ['HUP\\r\\n', '5'],
]
story.append(make_table(counts, col_widths=[6 * cm, 8.5 * cm]))

# ============== Section 5 — State Machine ==============
story.append(P("5. Device State Machine", h1))

story.append(P("Each device runs the same simple state machine:"))

story.append(ascii_block(r"""
                  ┌────────────────┐
                  │   BOOTING      │
                  │ (LED off)       │
                  └────────┬───────┘
                           │  bring-up + REG OK
                           ▼
                  ┌────────────────────┐
                  │   IDLE              │  ◄────────────────┐
                  │ (slow 1 Hz blink)   │                   │
                  └─┬────────────────┬─┘                   │
                    │                │                       │
       Call btn     │                │   INC <peer> arrives │   HUP / PEER_HUP
       pressed      ▼                ▼                       │
                ┌──────────┐    ┌──────────┐                │
                │ CALLING   │    │ RINGING   │                │
                │ (fast    │    │ (fast    │                │
                │  blink)   │    │  blink)   │                │
                └─┬─────┬──┘    └─┬──────┬─┘                │
                  │     │         │      │                    │
           GO arrives  HUP   Answer btn  HUP                 │
                  │     │         │      │                    │
                  ▼     │         ▼      │                    │
                ┌──────────────────┐    │                    │
                │   IN_CALL         │    │                    │
                │ (LED solid ON)    │ ───┴────────────────────┘
                │ Audio streams     │
                │ both directions   │
                └──────────────────┘
""".strip()))

story.append(P("5.1 — LED states map to call state", h2))
leds = [
    ['State', 'LED behavior', 'What it means'],
    ['BOOTING', 'Off → 2-sec ON → off → quick blinks 1..10', 'Modem boot + AT progress'],
    ['IDLE', 'Slow 1 Hz blink', 'Registered, waiting'],
    ['CALLING', 'Fast 5 Hz blink', 'Outgoing call ringing'],
    ['RINGING', 'Fast 5 Hz blink', 'Incoming call — answer it'],
    ['IN_CALL', 'Solid ON', 'Active conversation'],
    ['ERROR', 'Off forever', 'Bring-up failed (see Phase 5.4 troubleshooting)'],
]
story.append(make_table(leds, col_widths=[2.5 * cm, 5 * cm, 7 * cm]))

story.append(PageBreak())

# ============== Section 6 — Firmware ==============
story.append(P("6. Firmware Additions", h1))

story.append(P("Added on top of the Phase 5.4 firmware. The Phase 5.4 code stays exactly the "
               "same except: (1) re-enable the audio peripherals, (2) add state variables, "
               "(3) add button polling, (4) add audio streaming, (5) add incoming-message "
               "parser.", body))

story.append(P("6.1 — New defines and variables", h2))
story.append(code('''/* USER CODE BEGIN PD */
#define BUF_SIZE      256
#define HALF_SIZE     (BUF_SIZE / 2)
#define MCP4725_ADDR  (0x60 << 1)

#define PHONE_NUMBER       "01000000001"   /* CHANGE on Device 2 to "01000000002" */
#define PEER_PHONE         "01000000002"   /* CHANGE on Device 2 to "01000000001" */
#define NGROK_HOST         "<your_ngrok_host>"
#define NGROK_PORT         <your_ngrok_port>
#define APN                "internet.vodafone.net"

#define LTE_RX_BUF_SIZE    512
#define BTN_DEBOUNCE_MS    50
/* USER CODE END PD */

/* USER CODE BEGIN PV */
/* Audio buffers (ping-pong) */
uint16_t adc_buffer[BUF_SIZE];
uint16_t dac_buffer[BUF_SIZE];     /* what we play OUT */
volatile uint8_t  half_ready = 0, full_ready = 0;
volatile uint16_t dac_play_idx = 0;
volatile uint16_t dac_write_idx = 0;

/* LTE / call state */
volatile uint8_t  lte_rx_byte;
volatile char     lte_rx_buf[LTE_RX_BUF_SIZE];
volatile uint16_t lte_rx_idx = 0;

typedef enum {
    ST_BOOTING,
    ST_IDLE,
    ST_CALLING,
    ST_RINGING,
    ST_IN_CALL
} call_state_t;

volatile call_state_t state = ST_BOOTING;
/* USER CODE END PV */'''))

story.append(P("6.2 — Re-enable audio in main()", h2))
story.append(code('''/* USER CODE BEGIN 2 */
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, BUF_SIZE);
HAL_TIM_Base_Start(&htim2);
HAL_TIM_Base_Start_IT(&htim3);

lte_bring_up();        /* same as Phase 5.4 */
if (lte_registered) state = ST_IDLE;
/* USER CODE END 2 */'''))

story.append(P("6.3 — Send a custom message through the open TCP socket", h2))
story.append(code('''/* Send a line through the existing TCP socket via AT+CIPSEND */
static bool tcp_send_line(const char* line) {
    char cmd[64];
    int len = strlen(line) + 2;   /* +2 for \\r\\n */
    snprintf(cmd, sizeof cmd, "AT+CIPSEND=0,%d", len);
    if (!lte_send_at(cmd, ">", 3000)) return false;

    lte_clear_rx();
    HAL_UART_Transmit(&huart1, (uint8_t*)line, strlen(line), 1000);
    HAL_UART_Transmit(&huart1, (uint8_t*)"\\r\\n", 2, 1000);
    return true;
}'''))

story.append(P("6.4 — Button polling with debounce", h2))
story.append(code('''static bool btn_call_was_pressed = false;
static bool btn_ans_was_pressed  = false;
static uint32_t last_btn_time = 0;

static bool btn_pressed_edge(GPIO_TypeDef* port, uint16_t pin, bool* prev_state) {
    bool now_pressed = (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_RESET);
    bool edge = (now_pressed && !*prev_state &&
                 (HAL_GetTick() - last_btn_time) > BTN_DEBOUNCE_MS);
    if (edge) last_btn_time = HAL_GetTick();
    *prev_state = now_pressed;
    return edge;
}'''))

story.append(P("6.5 — Main loop with state machine", h2))
story.append(code('''/* USER CODE BEGIN WHILE */
while (1)
{
    /* 1. Update LED based on state */
    static uint32_t last_blink = 0;
    uint32_t blink_period = 0;
    switch (state) {
        case ST_BOOTING:  blink_period = 0;   break;  /* off */
        case ST_IDLE:     blink_period = 500; break;  /* 1 Hz slow */
        case ST_CALLING:
        case ST_RINGING:  blink_period = 100; break;  /* 5 Hz fast */
        case ST_IN_CALL:  blink_period = 0;   break;  /* solid */
    }
    if (blink_period > 0 && (HAL_GetTick() - last_blink) >= blink_period) {
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
        last_blink = HAL_GetTick();
    } else if (blink_period == 0 && state == ST_IN_CALL) {
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);  /* solid ON */
    } else if (blink_period == 0 && state == ST_BOOTING) {
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);    /* off */
    }

    /* 2. Buttons */
    if (btn_pressed_edge(BTN_CALL_GPIO_Port, BTN_CALL_Pin, &btn_call_was_pressed)) {
        if (state == ST_IDLE) {
            char cmd[32];
            snprintf(cmd, sizeof cmd, "CALL %s", PEER_PHONE);
            tcp_send_line(cmd);
            state = ST_CALLING;
        }
    }
    if (btn_pressed_edge(BTN_ANSWER_GPIO_Port, BTN_ANSWER_Pin, &btn_ans_was_pressed)) {
        if (state == ST_RINGING) {
            tcp_send_line("ANS");
        } else if (state == ST_IN_CALL) {
            tcp_send_line("HUP");
            state = ST_IDLE;
        }
    }

    /* 3. Parse incoming relay messages from lte_rx_buf */
    if (strstr((char*)lte_rx_buf, "INC ") && state == ST_IDLE) {
        state = ST_RINGING;
        lte_clear_rx();
    }
    if (strstr((char*)lte_rx_buf, "GO\\n")) {
        state = ST_IN_CALL;
        lte_clear_rx();
    }
    if (strstr((char*)lte_rx_buf, "PEER_HUP") || strstr((char*)lte_rx_buf, "PEER_GONE")) {
        state = ST_IDLE;
        lte_clear_rx();
    }

    /* 4. During TALK state, push audio bytes (Phase 6.2) */
    if (state == ST_IN_CALL && (half_ready || full_ready)) {
        uint16_t *chunk = half_ready ? &adc_buffer[0] : &adc_buffer[HALF_SIZE];
        half_ready = full_ready = 0;
        /* Pack 12-bit samples into bytes and send via AT+CIPSEND */
        /* (For simplicity, send 1 byte per sample = the upper 8 bits) */
        char hdr[16];
        snprintf(hdr, sizeof hdr, "AT+CIPSEND=0,%d", HALF_SIZE);
        if (lte_send_at(hdr, ">", 1000)) {
            uint8_t pkt[HALF_SIZE];
            for (int i = 0; i < HALF_SIZE; i++) {
                pkt[i] = (uint8_t)(chunk[i] >> 4);   /* take top 8 bits of 12-bit */
            }
            HAL_UART_Transmit(&huart1, pkt, HALF_SIZE, 1000);
        }
    }
}
/* USER CODE END WHILE */'''))

story.append(P("6.6 — DAC playback in TIM3 ISR (re-enabled from Phase 3)", h2))
story.append(code('''void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM3) {
        uint16_t v12 = dac_buffer[dac_play_idx];   /* 12-bit DAC value */
        uint8_t pkt[2] = {
            (uint8_t)((v12 >> 8) & 0x0F),
            (uint8_t)(v12 & 0xFF)
        };
        HAL_I2C_Master_Transmit(&hi2c1, MCP4725_ADDR, pkt, 2, 1);
        dac_play_idx = (dac_play_idx + 1) % BUF_SIZE;
    }
}'''))

story.append(P("6.7 — Receiving audio bytes from peer (extending UART RX callback)", h2))
story.append(code('''/* When in IN_CALL state, treat incoming +IPD bytes as audio for DAC */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        char c = (char)lte_rx_byte;

        if (state == ST_IN_CALL) {
            /* Naive: assume any byte during TALK is audio. Skip the +IPD header. */
            /* (Production code needs proper +IPD parsing.) */
            dac_buffer[dac_write_idx] = ((uint16_t)c) << 4;  /* expand 8→12 bits */
            dac_write_idx = (dac_write_idx + 1) % BUF_SIZE;
        } else {
            /* Outside calls, accumulate for protocol parsing */
            if (lte_rx_idx < LTE_RX_BUF_SIZE - 1) {
                lte_rx_buf[lte_rx_idx++] = c;
                lte_rx_buf[lte_rx_idx]   = 0;
            } else {
                lte_rx_idx = 0;
                lte_rx_buf[0] = 0;
            }
        }
        HAL_UART_Receive_IT(&huart1, (uint8_t*)&lte_rx_byte, 1);
    }
}'''))

story.append(P("This is a simplified streaming approach. A production implementation would "
               "properly parse <code>+IPD &lt;n&gt;</code> URCs to know exactly how many "
               "audio bytes to consume vs treating them as control. For Submission 1 demo "
               "purposes the simplified version is acceptable.",
               note_style))

story.append(PageBreak())

# ============== Section 7 — Two-Device Coordination ==============
story.append(P("7. Two-Device Coordination", h1))

story.append(P("7.1 — Phone numbers", h2))
phones = [
    ['Device', 'PHONE_NUMBER', 'PEER_PHONE'],
    ['Karim\'s device', '01000000001', '01000000002'],
    ['Friend\'s device', '01000000002', '01000000001'],
]
story.append(make_table(phones, col_widths=[5 * cm, 4.5 * cm, 5 * cm]))

story.append(P("Both devices flash the SAME firmware, just with these two #defines swapped.",
               body))

story.append(P("7.2 — Relay hosting", h2))
story.append(P("ONLY ONE relay runs — on Karim's laptop. Both devices connect to it via "
               "ngrok.", body))
host = [
    ['Component', 'Where it runs', 'Notes'],
    ['relay.py', 'Karim\'s laptop', 'Listens on port 5555, single instance'],
    ['ngrok tcp 5555', 'Karim\'s laptop', 'Exposes port 5555 to the public internet'],
    ['ngrok address (e.g., 2.tcp.eu.ngrok.io:20919)', 'public', 'Same address baked into BOTH devices\' firmware'],
]
story.append(make_table(host, col_widths=[4 * cm, 4 * cm, 6.5 * cm]))

story.append(P("7.3 — Coordinating with the friend remotely", h2))
coord = [
    "Karim starts <code>python relay.py</code> on his laptop.",
    "Karim starts <code>ngrok tcp 5555</code>, notes the new public address.",
    "Karim shares the address with the friend (WhatsApp, etc.).",
    "Karim updates NGROK_HOST/PORT in his firmware, builds, flashes Device 1.",
    "Friend updates NGROK_HOST/PORT in her copy of the firmware (same address as Karim's), sets PHONE_NUMBER=01000000002, builds, flashes Device 2.",
    "Both devices boot. Karim watches the relay terminal — should see both registrations:",
]
for c in coord:
    story.append(P("• " + c, bullet))
story.append(code('''+ conn (1.2.3.4, xxxxx)
+ registered 01000000001
+ conn (5.6.7.8, xxxxx)
+ registered 01000000002'''))

story.append(P("Both LEDs slow-blink → both devices ready. Now Karim presses Call on his "
               "device → friend's device LED goes fast-blink (ringing). Friend presses "
               "Answer → both LEDs go solid → audio streams.",
               body))

# ============== Section 8 — Demo procedure ==============
story.append(P("8. Demo Script (for the supervisor)", h1))

demo = [
    "Show the relay terminal on the laptop, displaying \"relay listening on (...)\".",
    "Plug both devices into power. After ~25 seconds, BOTH PC13 LEDs slow-blink.",
    "Show the relay terminal logging two registrations with phone numbers.",
    "Press Call on Device A. Show that A's LED goes fast-blink (calling).",
    "Show that B's LED also goes fast-blink (ringing) — relay forwarded the INC.",
    "Press Answer on Device B. Both LEDs go solid ON (in call).",
    "Speak into Device A's headset mic — voice plays in Device B's headphones.",
    "Speak into Device B's headset mic — voice plays in Device A's headphones.",
    "Both at the same time = full-duplex.",
    "Press Hangup on either device. Both LEDs return to slow-blink (idle).",
    "Repeat call in opposite direction: Device B presses Call → Device A rings → Device A presses Answer → audio resumes.",
    "Total demo time: ~3 minutes including narration.",
]
for d in demo:
    story.append(P("• " + d, bullet))

story.append(P("8.1 — Backup plan", h2))
backup = [
    "Record a video of the working system the day BEFORE the demo, in case something fails on demo day.",
    "Have the relay terminal output captured so you can show registrations even if audio fails.",
    "Have spare USB cables, jumper wires, and an extra SIM in case one fails.",
    "Test the full flow once just before the demo (within the same ngrok session).",
]
for b in backup:
    story.append(P("• " + b, bullet))

# ============== Section 9 — Known issues / next ==============
story.append(P("9. Known Issues &amp; What's Next", h1))

issues = [
    ['Issue', 'Workaround / Fix'],
    ['Audio quality is poor — bytes are not properly framed as +IPD URCs', 'For Submission 1, sound will be choppy. Phase 7 will add proper frame delimiters along with encryption.'],
    ['8 kHz mono 8-bit audio is the absolute minimum quality', 'Acceptable for project demo. A future improvement would be 16 kHz 12-bit.'],
    ['ngrok address changes on each restart', 'For demo, start ngrok once and don\'t restart it. Long-term: $4/month VPS.'],
    ['No echo cancellation', 'If both users wear headphones, this is not an issue. With speakers, can cause feedback loops.'],
    ['No proper +IPD parser yet', 'Audio bytes during TALK are treated naively. Works for single continuous stream but breaks if relay sends control messages mid-call.'],
]
story.append(make_table(issues, col_widths=[6.5 * cm, 8 * cm]))

story.append(P("After Submission 1 (this phase) is delivered, Phase 7 adds the encryption "
               "layer for Submission 2:", body))

next_p = [
    "Phase 7.1 — Pre-share RSA-512 keypairs between the two devices (one keypair per device).",
    "Phase 7.2 — At call setup, Device A generates a random AES-128 key, encrypts it with B's RSA public key, sends the encrypted key. B decrypts with its RSA private key.",
    "Phase 7.3 — From then on, both sides encrypt audio bytes with AES-128-CTR using the shared session key.",
    "Phase 7.4 — Verify with a packet sniffer that audio bytes on the LTE link are unintelligible without the key.",
]
for n in next_p:
    story.append(P("• " + n, bullet))

story.append(Spacer(1, 0.5 * cm))
story.append(P("End of Phase 6 — Two-Device Voice Call documentation.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 6 — Two-Device Voice Call",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")
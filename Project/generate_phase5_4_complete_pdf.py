"""
Generates the COMPLETED Phase 5.4 PDF — STM32 takes over LTE auto-registration.
Documents the working configuration, full wiring, ESP32 sleep sketch,
STM32 firmware, and all the gotchas hit during debugging.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase5_4_Complete.pdf"

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
                      "Secure Voice Project | Phase 5.4 — STM32 Drives LTE Auto-Registration")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

# ============== TITLE PAGE ==============
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 5.4<br/>STM32 Takes Over<br/>LTE Auto-Registration", title_style))
story.append(P("Submission 1: STM32 firmware connects to the relay over 4G with no human intervention",
               subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P("<b>STATUS: COMPLETED on 2026-04-29.</b><br/><br/>"
               "STM32 firmware boots, automatically powers up the LTE network connection, opens "
               "TCP through ngrok to the relay server, registers its phone number, and waits "
               "in idle. No manual AT commands. The relay log on the laptop confirms: "
               "<code>+ registered 01000000001</code>.",
               success_style))
story.append(Spacer(1, 0.5 * cm))
story.append(P("This document captures the working hardware configuration, the firmware code, "
               "the two Arduino sketches that prepare the LilyGO board, and every gotcha that "
               "had to be solved along the way.", body))
story.append(PageBreak())

# ============== Section 1 — Goal ==============
story.append(P("1. Goal of Phase 5.4", h1))

story.append(P("In Phase 5.3 the human was typing AT commands into Arduino Serial Monitor to "
               "register the device with the relay. Phase 5.4 puts the STM32 in charge of doing "
               "the same thing automatically.", body))

story.append(ascii_block(r"""
   Phase 5.3 (manual):
       Human  ───►  Arduino Serial Monitor  ───►  ESP32 bridge  ───►  A7608 modem
                    (typing AT commands)

   Phase 5.4 (automated):
       STM32 firmware  ───►  USART1  ───►  A7608 modem  ───►  4G  ───►  ngrok  ───►  relay.py
       (sends AT sequence
        and REG automatically
        on every boot)
""".strip()))

story.append(P("End result: power on the device, wait ~25 seconds, and it's registered with the "
               "relay and ready to receive incoming calls. Status LED slow-blinks at 1 Hz when "
               "registered.", body))

# ============== Section 2 — Architecture ==============
story.append(P("2. Architecture", h1))

story.append(ascii_block(r"""
   STM32 Black Pill                          LilyGO XY-A7608B v1.2
   ────────────────                          ──────────────────────
                                              ┌─────────────────────┐
   PA8 ──── ESP32_RST ───────HOLD LOW────────▶│ ESP32 (in deep sleep│
                                              │  after one-time     │
                                              │  power-on sketch)   │
                                              └─────────────────────┘

   PB1 ──── MODEM_POWERON ──────HIGH──────────▶ A7608 power supply enable
   PB2 ──── MODEM_PWRKEY  ─────(idle HIGH)────▶ A7608 virtual power button

   PA9  (USART1 TX, 115200) ────────data──────▶ A7608 RXD (LilyGO IO26 / TX label)
   PA10 (USART1 RX, 115200) ◀──────data─────── A7608 TXD (LilyGO IO27 / RX label)
   GND  ──────────── shared ground ─────────── GND

   Status LED: PC13 (onboard, active LOW)
   Buttons:    PA1 = Call,  PB0 = Answer/Hangup  (input pull-up to GND)
""".strip()))

story.append(P("The ESP32 on the LilyGO board does the modem's hardware power-on sequence "
               "ONCE (via a small Arduino sketch flashed to it), then enters deep sleep. From "
               "that point on, the ESP32 is electrically silent and the STM32 has clean access "
               "to the modem's UART through GPIO pins 26 and 27.",
               body))

# ============== Section 3 — Hardware ==============
story.append(P("3. Hardware Setup", h1))

story.append(P("3.1 — Components per device", h2))
parts = [
    ['Component', 'Purpose'],
    ['STM32F401RCT6 Black Pill', 'Microcontroller running the application firmware'],
    ['LilyGO XY-A7608B v1.2', 'LTE modem board (ESP32 + A7608 SIMCom 4G modem)'],
    ['ST-LINK V2', 'For programming + debugging the STM32'],
    ['Vodafone Egypt SIM', 'Cellular subscription with active data plan'],
    ['Push-buttons (×2)', 'Call (PA1) and Answer/Hangup (PB0)'],
    ['USB-C cable to PC', 'Powers the STM32 and is the SWD link via ST-Link'],
    ['USB-C cable to phone charger', 'Powers the LilyGO board separately'],
    ['Jumper wires', 'Six wires between STM32 and LilyGO (+ button wires)'],
]
story.append(make_table(parts, col_widths=[5 * cm, 9.5 * cm]))

story.append(P("3.2 — The 6 wires between STM32 and LilyGO", h2))
ww = [
    ['#', 'STM32 pin', 'LilyGO pin', 'Function'],
    ['1', 'PA8 (output, LOW)', 'RST (right header)', 'Holds ESP32 in reset (defensive — ESP32 is also asleep from sketch)'],
    ['2', 'PB1 (output, HIGH)', 'IO12 (left header)', 'Modem POWERON enable — keeps the A7608 chip powered'],
    ['3', 'PB2 (output, HIGH idle)', 'IO4 (left header)', 'Modem PWRKEY — pulsed by ESP32 sketch at boot, then idle HIGH'],
    ['4', 'PA9 (USART1 TX)', 'IO26 / "TX" label', 'Data: STM32 → modem'],
    ['5', 'PA10 (USART1 RX)', 'IO27 / "RX" label', 'Data: modem → STM32'],
    ['6', 'GND', 'GND', 'Common ground (mandatory for any UART)'],
]
story.append(make_table(ww, col_widths=[1 * cm, 3.5 * cm, 4 * cm, 6 * cm]))

story.append(P("3.3 — Buttons (2 wires + GND each)", h2))
btn = [
    ['#', 'STM32 pin', 'Other side'],
    ['7', 'PA1 (input, pull-up)', 'Call button → GND rail'],
    ['8', 'PB0 (input, pull-up)', 'Answer/Hangup button → GND rail'],
]
story.append(make_table(btn, col_widths=[1 * cm, 5 * cm, 8.5 * cm]))

story.append(P("3.4 — Power", h2))
story.append(P("<b>Each board has its own power source.</b> They share only one wire: ground.", body))
pw = [
    ['Board', 'Powered by'],
    ['STM32 Black Pill', 'USB-C cable to PC (also used for SWD via ST-Link)'],
    ['LilyGO LTE board', 'USB-C cable to phone charger (5 V/2 A) OR 18650 Li-ion battery'],
]
story.append(make_table(pw, col_widths=[5 * cm, 9.5 * cm]))

story.append(P("Critical: The LilyGO board CANNOT be powered from the STM32. The 4G modem can "
               "draw 2 A bursts during transmit, while the STM32's regulator only provides "
               "300 mA.", warn_style))

story.append(PageBreak())

# ============== Section 4 — Pin Map ==============
story.append(P("4. Complete STM32 Pin Map (after Phase 5.4)", h1))

pin_map = [
    ['Pin', 'Function', 'Connection'],
    ['PA0', 'ADC1_IN0', 'MAX9814 OUT (audio — disabled in 5.4)'],
    ['PA1', 'GPIO input pull-up', 'Call button → GND'],
    ['PA8', 'GPIO output (LOW)', 'LilyGO RST (ESP32 reset hold)'],
    ['PA9', 'USART1 TX', 'LilyGO IO26 (modem RX line)'],
    ['PA10', 'USART1 RX', 'LilyGO IO27 (modem TX line)'],
    ['PA13', 'SWDIO', 'ST-Link'],
    ['PA14', 'SWCLK', 'ST-Link'],
    ['PB0', 'GPIO input pull-up', 'Answer/Hangup button → GND'],
    ['PB1', 'GPIO output (HIGH)', 'LilyGO IO12 (POWERON)'],
    ['PB2', 'GPIO output (HIGH idle)', 'LilyGO IO4 (PWRKEY)'],
    ['PB6', 'I2C1_SCL', 'MCP4725 SCL (audio — disabled in 5.4)'],
    ['PB7', 'I2C1_SDA', 'MCP4725 SDA (audio — disabled in 5.4)'],
    ['PC13', 'GPIO output', 'Onboard status LED'],
]
story.append(make_table(pin_map, col_widths=[2 * cm, 4.5 * cm, 8 * cm]))

# ============== Section 5 — ESP32 sketches ==============
story.append(P("5. Two Arduino Sketches Used Once on the LilyGO", h1))

story.append(P("Both sketches are uploaded to the ESP32 chip on the LilyGO board (not to the "
               "STM32). The first locks the modem baud permanently. The second hands control "
               "to the STM32. After both are run, you never need Arduino IDE again.", body))

story.append(P("5.1 — Factory Reset Utility (lock baud at 115200 forever)", h2))
story.append(P("Many SIMCom A7608 modems ship with auto-baud or a non-115200 default. The "
               "STM32 firmware expects 115200, so we lock the modem permanently using BOTH "
               "<code>AT+IPR=115200</code> (current session) AND <code>AT+IPREX=115200</code> "
               "(boot baud, non-volatile).", body))
story.append(code('''#include <HardwareSerial.h>

HardwareSerial gsmSerial(2);

#define MODEM_RX_PIN  27
#define MODEM_TX_PIN  26
#define MODEM_PWRKEY_PIN  4
#define MODEM_POWERON_PIN 12
#define MODEM_RST_PIN  5
#define PC_BAUD        115200

const long BAUDS[]  = {115200, 9600, 921600, 460800, 230400, 57600, 38400, 19200};
const int  NUM_BAUDS = 8;

bool sendAndWaitForOK(const char* cmd, unsigned long timeout_ms) {
    while (gsmSerial.available()) gsmSerial.read();
    gsmSerial.print(cmd); gsmSerial.print("\\r\\n");
    String resp;
    unsigned long start = millis();
    while (millis() - start < timeout_ms) {
        while (gsmSerial.available()) {
            char c = (char)gsmSerial.read(); resp += c; Serial.write(c);
            if (resp.indexOf("OK") >= 0) return true;
            if (resp.indexOf("ERROR") >= 0) return false;
        }
    }
    return false;
}

void setup() {
    Serial.begin(PC_BAUD); delay(500);
    Serial.println("\\n[ESP32] Modem Baud Lock to 115200");
    pinMode(MODEM_POWERON_PIN, OUTPUT);  digitalWrite(MODEM_POWERON_PIN, HIGH);
    pinMode(MODEM_RST_PIN, OUTPUT);       digitalWrite(MODEM_RST_PIN, HIGH);
    pinMode(MODEM_PWRKEY_PIN, OUTPUT);
    digitalWrite(MODEM_PWRKEY_PIN, HIGH); delay(100);
    digitalWrite(MODEM_PWRKEY_PIN, LOW);  delay(1000);
    digitalWrite(MODEM_PWRKEY_PIN, HIGH);
    delay(10000);

    long workingBaud = 0;
    for (int i = 0; i < NUM_BAUDS; i++) {
        gsmSerial.begin(BAUDS[i], SERIAL_8N1, MODEM_RX_PIN, MODEM_TX_PIN);
        delay(500);
        if (sendAndWaitForOK("AT", 1500)) { workingBaud = BAUDS[i]; break; }
        gsmSerial.end();
    }
    if (!workingBaud) { Serial.println("FAILED"); return; }

    sendAndWaitForOK("AT+IPR=115200",   2000);
    sendAndWaitForOK("AT+IPREX=115200", 2000);   /* CRITICAL — survives power cycle */
    sendAndWaitForOK("AT&W",            2000);

    Serial.println("DONE. Power-cycle the modem.");
    gsmSerial.begin(115200, SERIAL_8N1, MODEM_RX_PIN, MODEM_TX_PIN);
}

void loop() {
    if (Serial.available())   gsmSerial.write((char)Serial.read());
    if (gsmSerial.available()) Serial.write((char)gsmSerial.read());
}'''))

story.append(P("5.2 — ESP32 deep-sleep sketch (release UART pins to STM32)", h2))
story.append(P("Once the baud is locked, this second sketch powers on the modem and then puts "
               "the ESP32 into deep sleep. After this, the ESP32 stops driving GPIO 26/27 and "
               "the STM32 can use those pins to talk to the modem directly.",
               body))
story.append(code('''#include <esp_sleep.h>
#include <Arduino.h>

#define MODEM_PWRKEY_PIN  4
#define MODEM_POWERON_PIN 12
#define MODEM_RST_PIN     5
#define MODEM_RX_PIN      27
#define MODEM_TX_PIN      26

void setup() {
  Serial.begin(115200);
  Serial.println("\\n[ESP32] Power-on then sleep");

  pinMode(MODEM_POWERON_PIN, OUTPUT); digitalWrite(MODEM_POWERON_PIN, HIGH);
  pinMode(MODEM_RST_PIN, OUTPUT);     digitalWrite(MODEM_RST_PIN, HIGH);
  pinMode(MODEM_PWRKEY_PIN, OUTPUT);
  digitalWrite(MODEM_PWRKEY_PIN, HIGH); delay(100);
  digitalWrite(MODEM_PWRKEY_PIN, LOW);  delay(1000);
  digitalWrite(MODEM_PWRKEY_PIN, HIGH);

  Serial.println("[ESP32] Modem powered on. Waiting 8 sec for boot...");
  delay(8000);

  /* Release UART pins so STM32 can drive them */
  pinMode(MODEM_RX_PIN, INPUT);
  pinMode(MODEM_TX_PIN, INPUT);

  Serial.println("[ESP32] Going to deep sleep — STM32 takes over");
  Serial.flush();
  esp_deep_sleep_start();
}

void loop() {} /* never reached */'''))

story.append(P("Order of use: First flash the Factory Reset utility, run it once, then power-cycle. "
               "Then flash the deep-sleep sketch. Watch Serial Monitor until you see &laquo;Going "
               "to deep sleep&raquo;, then close Arduino IDE. From this point on, never use "
               "Arduino IDE again — STM32 owns the modem.",
               note_style))

story.append(PageBreak())

# ============== Section 6 — STM32 firmware ==============
story.append(P("6. STM32 Firmware (added to MicDAC project)", h1))

story.append(P("All additions live in the existing <code>MicDAC</code> project. The audio code "
               "from Phase 3 stays in place but is COMMENTED OUT for Phase 5.4 testing because "
               "TIM3+I2C blocking can hang the CPU when the MCP4725 is not in the circuit.",
               body))

story.append(P("6.1 — Includes and defines", h2))
story.append(code('''/* USER CODE BEGIN Includes */
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
/* USER CODE END Includes */

/* USER CODE BEGIN PD */
#define BUF_SIZE      256
#define HALF_SIZE     (BUF_SIZE / 2)
#define MCP4725_ADDR  (0x60 << 1)

/* LTE config — UPDATE these to match the current ngrok session */
#define PHONE_NUMBER       "01000000001"
#define NGROK_HOST         "0.tcp.eu.ngrok.io"
#define NGROK_PORT         12930
#define APN                "internet.vodafone.net"

#define LTE_RX_BUF_SIZE    512
/* USER CODE END PD */'''))

story.append(P("6.2 — Variables and prototypes", h2))
story.append(code('''/* USER CODE BEGIN PV */
uint16_t adc_buffer[BUF_SIZE];
volatile uint8_t  half_ready = 0;
volatile uint8_t  full_ready = 0;
volatile uint16_t dac_play_idx = 0;

volatile uint8_t  lte_rx_byte;            /* 1-byte slot for UART RX IT */
volatile char     lte_rx_buf[LTE_RX_BUF_SIZE];
volatile uint16_t lte_rx_idx = 0;
volatile uint8_t  lte_registered = 0;
/* USER CODE END PV */

/* USER CODE BEGIN PFP */
void lte_clear_rx(void);
bool lte_wait_for(const char* expected, uint32_t timeout_ms);
bool lte_send_at(const char* cmd, const char* expected, uint32_t timeout_ms);
void lte_bring_up(void);
/* USER CODE END PFP */'''))

story.append(P("6.3 — main() initialization (USER CODE BEGIN 2)", h2))
story.append(code('''/* USER CODE BEGIN 2 */
/* Audio disabled during Phase 5.4 LTE testing.  Re-enable in Phase 6
   when MCP4725 is back in the circuit. */
// HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, BUF_SIZE);
// HAL_TIM_Base_Start(&htim2);
// HAL_TIM_Base_Start_IT(&htim3);

/* ESP32 already powered on the modem. Now do AT bring-up + REG to relay. */
lte_bring_up();
/* USER CODE END 2 */'''))

story.append(P("6.4 — Main while-loop (LED status)", h2))
story.append(code('''/* USER CODE BEGIN WHILE */
while (1)
{
    static uint32_t last_led_toggle = 0;

    if (lte_registered) {
        /* Slow blink at 1 Hz — registered idle */
        if (HAL_GetTick() - last_led_toggle >= 500) {
            HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
            last_led_toggle = HAL_GetTick();
        }
    } else {
        /* Not registered — LED off */
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
    }
}
/* USER CODE END WHILE */'''))

story.append(P("6.5 — Helper functions (USER CODE BEGIN 4)", h2))
story.append(code('''/* Clear the LTE RX buffer */
void lte_clear_rx(void) {
    __disable_irq();
    lte_rx_idx = 0;
    lte_rx_buf[0] = 0;
    __enable_irq();
}

/* Wait for substring in RX buffer, or timeout */
bool lte_wait_for(const char* expected, uint32_t timeout_ms) {
    uint32_t start = HAL_GetTick();
    while ((HAL_GetTick() - start) < timeout_ms) {
        if (strstr((const char*)lte_rx_buf, expected) != NULL) return true;
        HAL_Delay(10);
    }
    return false;
}

/* Send AT command and wait for expected response */
bool lte_send_at(const char* cmd, const char* expected, uint32_t timeout_ms) {
    lte_clear_rx();
    HAL_UART_Transmit(&huart1, (uint8_t*)cmd, strlen(cmd), 1000);
    HAL_UART_Transmit(&huart1, (uint8_t*)"\\r\\n", 2, 1000);
    return lte_wait_for(expected, timeout_ms);
}

/* UART RX interrupt callback — append byte to buffer */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        if (lte_rx_idx < LTE_RX_BUF_SIZE - 1) {
            lte_rx_buf[lte_rx_idx++] = (char)lte_rx_byte;
            lte_rx_buf[lte_rx_idx]   = 0;
        } else {
            lte_rx_idx = 0;
            lte_rx_buf[0] = 0;
        }
        HAL_UART_Receive_IT(&huart1, (uint8_t*)&lte_rx_byte, 1);
    }
}'''))

story.append(P("6.6 — The bring-up sequence", h2))
story.append(P("This is the heart of Phase 5.4. It runs once at boot and either succeeds "
               "(<code>lte_registered = 1</code>) or fails silently (registered stays 0). "
               "Each successful step blinks the LED N times for visual debugging.",
               body))
story.append(code('''static void debug_blink(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) {
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);  /* ON */
        HAL_Delay(150);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);    /* OFF */
        HAL_Delay(150);
    }
    HAL_Delay(500);
}

void lte_bring_up(void) {
    char cmd[128];

    /* Step 0: boot indicator */
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
    HAL_Delay(2000);
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);

    /* Start UART RX */
    HAL_UART_Receive_IT(&huart1, (uint8_t*)&lte_rx_byte, 1);

    /* ESP32 already powered the modem; wait briefly */
    HAL_Delay(2000);

    if (!lte_send_at("AT", "OK", 2000)) return;            debug_blink(1);
    if (!lte_send_at("ATE0", "OK", 2000)) return;          debug_blink(2);
    if (!lte_send_at("AT+CPIN?", "READY", 5000)) return;   debug_blink(3);
    if (!lte_send_at("AT+CSQ", "OK", 2000)) return;        debug_blink(4);

    snprintf(cmd, sizeof cmd, "AT+CGDCONT=1,\\"IP\\",\\"%s\\"", APN);
    if (!lte_send_at(cmd, "OK", 2000)) return;             debug_blink(5);

    if (!lte_send_at("AT+CGACT=1,1", "OK", 10000)) return; debug_blink(6);
    lte_send_at("AT+NETOPEN", "OK", 5000);                 debug_blink(7);

    snprintf(cmd, sizeof cmd, "AT+CIPOPEN=0,\\"TCP\\",\\"%s\\",%d", NGROK_HOST, NGROK_PORT);
    if (!lte_send_at(cmd, "+CIPOPEN: 0,0", 15000)) return; debug_blink(8);

    char reg_payload[32];
    int  reg_len = snprintf(reg_payload, sizeof reg_payload, "REG %s\\r\\n", PHONE_NUMBER);

    snprintf(cmd, sizeof cmd, "AT+CIPSEND=0,%d", reg_len);
    if (!lte_send_at(cmd, ">", 3000)) return;              debug_blink(9);

    lte_clear_rx();
    HAL_UART_Transmit(&huart1, (uint8_t*)reg_payload, reg_len, 1000);

    if (lte_wait_for("OK", 5000)) {
        lte_registered = 1;
        debug_blink(10);   /* SUCCESS */
    }
}'''))

story.append(PageBreak())

# ============== Section 7 — Operating Procedure ==============
story.append(P("7. Operating Procedure", h1))

story.append(P("7.1 — One-time setup (per device)", h2))
once = [
    "Wire up everything per Section 3 (6 STM32-LilyGO wires + 4 button wires).",
    "Power both boards (STM32 on USB-C to PC, LilyGO on USB-C to phone charger).",
    "Connect LilyGO USB-C briefly to PC for ESP32 programming.",
    "Open Arduino IDE. Upload the Factory Reset Utility (Section 5.1). Wait for &laquo;DONE&raquo;.",
    "Power-cycle the LilyGO (unplug USB-C, wait 10s, plug back in).",
    "Upload the ESP32 deep-sleep sketch (Section 5.2). Wait for &laquo;Going to deep sleep&raquo;.",
    "Disconnect LilyGO from PC. Plug it back into the phone charger.",
    "Re-attach STM32 wires to LilyGO if you removed them.",
    "Build and flash the STM32 firmware in VS Code.",
]
for s in once:
    story.append(P("• " + s, bullet))

story.append(P("7.2 — Normal startup (every boot)", h2))
boot = [
    "Start <code>relay.py</code> on laptop.",
    "Start ngrok: <code>ngrok tcp 5555</code>. Note the new public address.",
    "Update <code>NGROK_HOST</code> and <code>NGROK_PORT</code> in main.c if changed.",
    "Build &amp; flash STM32.",
    "Power on the LilyGO board (USB-C charger).",
    "Power on the STM32 (USB-C to PC).",
    "Wait ~25 seconds for the LED to start slow-blinking.",
]
for s in boot:
    story.append(P("• " + s, bullet))

story.append(P("7.3 — LED state legend", h2))
states = [
    ['LED state', 'Meaning'],
    ['Off (right after reset)', 'Code starting'],
    ['Solid ON for 2 seconds', 'Boot indicator (start of lte_bring_up)'],
    ['1 quick blink', 'AT command OK'],
    ['2 quick blinks', 'ATE0 OK (echo off)'],
    ['3 quick blinks', 'SIM card READY'],
    ['4 quick blinks', 'Signal strength check OK'],
    ['5 quick blinks', 'APN configured'],
    ['6 quick blinks', 'Data session activated'],
    ['7 quick blinks', 'IP stack opened (NETOPEN)'],
    ['8 quick blinks', 'TCP socket to relay opened'],
    ['9 quick blinks', 'Got &gt; prompt for sending REG'],
    ['10 quick blinks', '✓ REGISTERED with relay (success!)'],
    ['Slow 1 Hz blink (forever)', 'Registered, idle, ready for incoming calls'],
    ['LED stops at N blinks', 'Step N+1 failed — see Section 8'],
]
story.append(make_table(states, col_widths=[5 * cm, 9.5 * cm]))

# ============== Section 8 — Lessons learned ==============
story.append(P("8. Lessons Learned (the hard way)", h1))

story.append(P("Phase 5.4 was the hardest phase by far. Seven distinct issues were hit and "
               "solved over the debugging session. Each is documented here so the same time "
               "isn't wasted next time.", body))

lessons = [
    ("8.1 — Modem silent garbled output at 115200",
     "Symptom: Arduino bridge sketch printed unreadable bytes from the modem.<br/>"
     "Cause: SIMCom A7608 default baud is not always 115200. The second LilyGO board's modem "
     "shipped at a different rate (likely 9600 or 921600).<br/>"
     "Fix: Auto-baud detect by trying multiple rates, then permanently lock with both "
     "<code>AT+IPR=115200</code> AND <code>AT+IPREX=115200</code> followed by "
     "<code>AT&amp;W</code>. Without IPREX, the modem reverts on next power-cycle."),

    ("8.2 — TIM3 ISR hung the CPU",
     "Symptom: After flashing the LTE firmware, the LED stayed solid ON forever; nothing else ran.<br/>"
     "Cause: TIM3 ISR fires every 125&micro;s and calls <code>HAL_I2C_Master_Transmit</code> to "
     "the MCP4725. With the MCP4725 NOT in the circuit (Phase 5.4 only tests LTE), the I&sup2;C "
     "transmit blocks until timeout. The blocking call uses HAL_GetTick() which depends on "
     "SysTick — but SysTick is at lower priority than TIM3, so it can't fire to advance the timeout. CPU hangs forever.<br/>"
     "Fix: Comment out <code>HAL_TIM_Base_Start_IT(&amp;htim3)</code> during Phase 5.4 testing. "
     "Re-enable in Phase 6 when audio + LTE are integrated and the MCP4725 is connected."),

    ("8.3 — STM32 PA8 alone did not reliably hold ESP32 in reset",
     "Symptom: Even with PA8 driven LOW, the ESP32 was still partially active and seemed to be driving the UART pins, conflicting with STM32.<br/>"
     "Cause: The LilyGO board's CH9102 USB-serial chip has its own DTR/RTS connections to the ESP32's EN pin. When USB-C is connected (even just for power), CH9102 can interfere.<br/>"
     "Fix: Don't rely solely on PA8. Flash the ESP32 with a one-time &laquo;power-on then deep-sleep&raquo; sketch. After this, the ESP32 is in true low-power state with all pins released."),

    ("8.4 — PuTTY was not sending \\r\\n on Enter",
     "Symptom: REG command sent the right bytes, but the relay never recognized a complete line.<br/>"
     "Cause: PuTTY by default sends only carriage return (\\r) on Enter. The relay's <code>readline()</code> waits for newline (\\n).<br/>"
     "Fix: Use Arduino IDE Serial Monitor with line ending set to &laquo;Both NL &amp; CR&raquo;. It always sends \\r\\n correctly."),

    ("8.5 — STM32 firmware byte count mismatch for REG",
     "Symptom: <code>AT+CIPSEND=0,18</code> followed by &laquo;REG 01000000001&raquo; produced \\<code>+CIPSEND: 0,18,18</code\\> but relay never registered.<br/>"
     "Cause: &laquo;REG 01000000001&raquo; is 15 chars; with \\r\\n that's 17 bytes, not 18. Sending CIPSEND=0,18 made the modem buffer 18 bytes including a stray byte that broke the line.<br/>"
     "Fix: Compute byte count carefully: 3 (REG) + 1 (space) + 11 (phone) + 2 (\\r\\n) = 17."),

    ("8.6 — ngrok free tier requires credit-card verification for TCP",
     "Symptom: <code>ngrok tcp 5555</code> errored with &laquo;You must add a credit or debit card&raquo;.<br/>"
     "Cause: ngrok recently restricted TCP tunnels to verified accounts to prevent abuse.<br/>"
     "Fix: Add a card on the ngrok dashboard. ngrok performs a $0 verification charge only — does not actually charge. For long-term hosting, switch to a paid VPS (~$4/month) where the address never changes."),

    ("8.7 — ngrok address changes per session (free tier)",
     "Symptom: After restarting ngrok, the public address (host + port) is different.<br/>"
     "Cause: Free tier dynamic addresses.<br/>"
     "Fix for development: Update <code>NGROK_HOST</code> and <code>NGROK_PORT</code> in STM32 firmware before each test session. For demo day: start ngrok, note address, flash STM32 with that address, demo within the session."),
]
for title, body_text in lessons:
    story.append(P(title, h2))
    story.append(P(body_text, body))

story.append(PageBreak())

# ============== Section 9 — what's next ==============
story.append(P("9. What's Next", h1))

story.append(P("Phase 5.4 is the foundation for everything in Submission 1. Now that one device "
               "can register with the relay automatically, the remaining work is:", body))

next_phases = [
    ['Phase', 'Description', 'Time'],
    ['5.5', 'Build Device 2 — same hardware as Device 1, but PHONE_NUMBER = "01000000002". Run through Sections 5.1, 5.2, 7.1, 7.2 again on the second LilyGO + STM32.', '~2 hrs'],
    ['6.1', 'Add CALL / INC / ANS / GO / HUP state machine to STM32 firmware. User pushes Call → STM sends "CALL <peer_phone>". Other side gets "INC <caller>". User pushes Answer → STM sends "ANS". Both end up in TALK state.', '~3 hrs'],
    ['6.2', 'Stream audio bytes between devices: re-enable TIM3, mic samples → packed bytes → CIPSEND → received bytes → DAC playback buffer. Both directions simultaneously.', '~6 hrs'],
    ['8', 'Demo polish: status LED states for ringing/in-call, debounced button reading, video backup, latency measurement.', '~3 hrs'],
]
story.append(make_table(next_phases, col_widths=[1.5 * cm, 11 * cm, 2 * cm]))

story.append(P("After Phase 8, Submission 1 is demonstrated. Submission 2 (encryption with "
               "RSA + AES) gets layered on top later.",
               body))

story.append(Spacer(1, 0.5 * cm))
story.append(P("End of Phase 5.4 documentation.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 5.4 — STM32 Drives LTE Auto-Registration",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")
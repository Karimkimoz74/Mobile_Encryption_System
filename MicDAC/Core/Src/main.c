/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "adc.h"
#include "dma.h"
#include "i2c.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define BUF_SIZE      1024
#define HALF_SIZE     (BUF_SIZE / 2)
#define MCP4725_ADDR  (0x60 << 1)

/* LTE config — CHANGE these to match your setup */
#define PHONE_NUMBER       "01000000001"      /* this devBice */
#define PEER_PHONE         "01000000002"      /* friend's device */
#define NGROK_HOST         "4.tcp.eu.ngrok.io"
#define NGROK_PORT         23257
#define APN                "internet.vodafone.net"

#define LTE_RX_BUF_SIZE   2048   /* doubled: SEND OK responses accumulate at 16 Hz */
#define MODEM_BOOT_DELAY_MS 8000
#define BTN_DEBOUNCE_MS    50

/* DIAGNOSTIC: when 1, sends a clean sawtooth tone instead of mic audio.
   Used to isolate whether the noise is from mic capture or from
   the transmission path. Set to 0 for live mic. */
#define SEND_TEST_TONE     0

/* DIAGNOSTIC: when 1, route mic samples STRAIGHT to local DAC (no LTE).
   You hear yourself in your own headphones. Use this to PROVE the mic is
   actually capturing your voice. Set to 0 for normal (peer plays your mic). */
#define LOCAL_LOOPBACK     0
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
uint16_t adc_buffer[BUF_SIZE];
volatile uint8_t half_ready = 0;
volatile uint8_t full_ready = 0;
volatile uint16_t dac_play_idx = 0;
/* LTE state */
volatile uint8_t  lte_rx_byte;            /* single byte buffer for UART RX IT */
volatile char     lte_rx_buf[LTE_RX_BUF_SIZE];
volatile uint16_t lte_rx_idx = 0;
volatile uint8_t  lte_registered = 0;

/* Phase 6 — call state machine */
typedef enum {
    ST_BOOTING = 0,
    ST_IDLE,        /* registered, waiting */
    ST_CALLING,     /* outgoing call ringing */
    ST_RINGING,     /* incoming call */
    ST_IN_CALL      /* both ends connected */
} call_state_t;

volatile call_state_t state = ST_BOOTING;

/* Phase 6.2.5 — incoming audio play buffer.
   When state == ST_IN_CALL, every UART RX byte is written here instead of
   lte_rx_buf. TIM3 ISR drains it into the MCP4725. */
#define PLAY_BUF_SIZE 8192        /* 1 second of audio */
#define PLAY_THRESH   1200        /* ~150 ms — moderate startup delay */
#define PLAY_MAX_OCC  7000        /* ~875 ms — only drop oldest when truly overflowing */
volatile uint8_t  play_buf[PLAY_BUF_SIZE];
volatile uint16_t play_write_idx = 0;
volatile uint16_t play_read_idx  = 0;

/* +IPD URC parser state — extracts only the audio payload from the modem
   stream so AT-response bytes don't pollute the play buffer.
   Handles three SIMCom A7608 formats:
       +IPD,<N>\r\n<data>
       +IPD,<N>:<data>
       +IPD<N>:<data>            (CIPHEAD form)
*/
volatile char     ipd_tail[5]      = {0,0,0,0,0};   /* rolling last-5 bytes */
volatile bool     ipd_after_d      = false;         /* just saw "+IPD", deciding form */
volatile bool     ipd_collect_len  = false;
volatile uint16_t ipd_pending_len  = 0;
volatile uint16_t ipd_remaining    = 0;             /* audio bytes still to consume */
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
void lte_clear_rx(void);
bool lte_wait_for(const char* expected, uint32_t timeout_ms);
bool lte_send_at(const char* cmd, const char* expected, uint32_t timeout_ms);
void modem_power_on_pulse(void);
void lte_bring_up(void);
bool tcp_send_line(const char* line);
bool tcp_send_audio(const uint8_t* buf, int len);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_TIM2_Init();
  MX_TIM3_Init();
  MX_I2C1_Init();
  MX_USART1_UART_Init();
  /* USER CODE BEGIN 2 */
  /* CRITICAL: MCP4725 must be wired on I2C1 (SDA=PB7, SCL=PB6).
     If not connected, TIM3 ISR hangs in HAL_I2C_Master_Transmit and CPU stalls. */

  /* NVIC priority fix — CubeMX sets TIM3 and USART1 both to priority 0.
     At equal priority, neither ISR can preempt the other.
     Problem: TIM3 ISR calls HAL_I2C_Master_Transmit which busy-polls for
     ~75 μs (400 kHz I2C, 2 data bytes). USART1 at 115200 baud delivers a
     byte every 86.8 μs. While TIM3 holds the CPU for 75 μs, USART1 IRQ is
     frozen — only 11 μs of margin before UART overrun drops an audio byte.
     Fix: USART1 = priority 0 (preempts everything),
          TIM3   = priority 1 (preemptable by USART1),
          DMA2   = priority 2 (lowest, only fires every 64 ms anyway).
     NVIC_PRIORITYGROUP_4 is set by CubeMX: 4 bits preemption, 0 sub-priority. */
  HAL_NVIC_SetPriority(USART1_IRQn,      0, 0);
  HAL_NVIC_SetPriority(TIM3_IRQn,        1, 0);
  HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 2, 0);

  HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, BUF_SIZE);
  HAL_TIM_Base_Start(&htim2);
  HAL_TIM_Base_Start_IT(&htim3);

  /* ESP32 already powered on the modem. Now do AT bring-up + REG to relay. */
  lte_bring_up();
  if (lte_registered) state = ST_IDLE;

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    static uint32_t last_led_toggle = 0;
    static uint32_t last_btn_time   = 0;
    static bool     btn_call_prev   = false;
    static bool     btn_ans_prev    = false;

    /* === 1. LED state machine — full duplex: solid ON during call. */
    uint32_t period = 0;
    switch (state) {
      case ST_BOOTING:  period = 0;   break;
      case ST_IDLE:     period = 500; break;
      case ST_CALLING:
      case ST_RINGING:  period = 100; break;
      case ST_IN_CALL:  period = 0;   break;   /* solid ON full-duplex */
    }
    if (period > 0 && (HAL_GetTick() - last_led_toggle) >= period) {
      HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
      last_led_toggle = HAL_GetTick();
    } else if (state == ST_IN_CALL) {
      HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET); /* solid ON */
    } else if (state == ST_BOOTING) {
      HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);   /* off */
    }

    /* === 2. Buttons (with debounce) === */
    bool now_call = (HAL_GPIO_ReadPin(BTN_CALL_GPIO_Port, BTN_CALL_Pin) == GPIO_PIN_RESET);
    bool now_ans  = (HAL_GPIO_ReadPin(BTN_ANSWER_GPIO_Port, BTN_ANSWER_Pin) == GPIO_PIN_RESET);

    /* During a call, PA1 is the PTT (handled level-based above). Skip the
       edge handler entirely so the LED flash + DBG line don't gap the audio. */
    if (now_call && !btn_call_prev && (HAL_GetTick() - last_btn_time) > BTN_DEBOUNCE_MS
        && state != ST_IN_CALL) {
      last_btn_time = HAL_GetTick();
      /* DEBUG: local LED flash so you can see the press is detected */
      for (int i = 0; i < 3; i++) {
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
        HAL_Delay(80);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
        HAL_Delay(80);
      }
      /* DEBUG: tell the server the button was pressed + current state */
      {
        char dbg[32];
        snprintf(dbg, sizeof dbg, "DBG CALL_BTN state=%d", (int)state);
        tcp_send_line(dbg);
      }
      if (state == ST_IDLE) {
        char cmd[32];
        snprintf(cmd, sizeof cmd, "CALL %s", PEER_PHONE);
        if (tcp_send_line(cmd)) {
          state = ST_CALLING;
          tcp_send_line("DBG CALL_SENT_OK");
        } else {
          tcp_send_line("DBG CALL_SEND_FAIL");
        }
      } else {
        tcp_send_line("DBG CALL_IGNORED_NOT_IDLE");
      }
    }
    btn_call_prev = now_call;

    if (now_ans && !btn_ans_prev && (HAL_GetTick() - last_btn_time) > BTN_DEBOUNCE_MS) {
      last_btn_time = HAL_GetTick();
      /* DEBUG: local LED flash */
      for (int i = 0; i < 2; i++) {
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
        HAL_Delay(80);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
        HAL_Delay(80);
      }
      tcp_send_line("DBG ANS_BTN");
      if (state == ST_RINGING) {
        if (tcp_send_line("ANS")) {
          tcp_send_line("DBG ANS_SENT_OK");
          /* state will move to IN_CALL when GO arrives */
        } else {
          tcp_send_line("DBG ANS_SEND_FAIL");
        }
      } else if (state == ST_IN_CALL) {
        /* Phase 6.2: relay is in byte-forward mode, so "HUP" can't be a line
           command anymore. Close the TCP socket — relay sees EOF and notifies
           the peer with PEER_GONE. We then re-bring-up so we're ready again. */
        lte_send_at("AT+CIPCLOSE=0", "OK", 3000);
        lte_registered = 0;
        state = ST_BOOTING;
        lte_bring_up();
        if (lte_registered) state = ST_IDLE;
      } else if (state == ST_CALLING) {
        /* Outgoing call not yet answered: still in line mode, normal HUP works. */
        if (tcp_send_line("HUP")) {
          state = ST_IDLE;
          tcp_send_line("DBG HUP_SENT_OK");
        } else {
          tcp_send_line("DBG HUP_SEND_FAIL");
        }
      } else {
        tcp_send_line("DBG ANS_IGNORED_NOT_RINGING");
      }
    }
    btn_ans_prev = now_ans;

    /* === 3. Parse incoming relay messages from lte_rx_buf === */
    if (state == ST_IDLE && strstr((const char*)lte_rx_buf, "INC ")) {
      state = ST_RINGING;
      lte_clear_rx();
    }
    if ((state == ST_CALLING || state == ST_RINGING) &&
        strstr((const char*)lte_rx_buf, "GO\n")) {
      state = ST_IN_CALL;
      lte_clear_rx();
    }
    if (strstr((const char*)lte_rx_buf, "PEER_HUP") ||
        strstr((const char*)lte_rx_buf, "PEER_GONE")) {
      state = ST_IDLE;
      lte_clear_rx();
    }
    if (state == ST_CALLING && strstr((const char*)lte_rx_buf, "ERR ")) {
      state = ST_IDLE;
      lte_clear_rx();
    }

    /* === 3.5. Walkie-talkie: stream audio while PA1 is held during the call.
       Half-duplex — only one side talks at a time, the other listens.
       Sticky PTT: once held, we keep transmitting for 200 ms after release.
       audio_fail_count tracks consecutive tcp_send_audio failures; if the
       modem's TCP buffer is dead we reconnect rather than hanging forever. */
    static uint8_t  test_phase     = 0;
    static int      audio_fail_cnt = 0;
    static uint32_t last_voice_ms  = 0;

    if (state == ST_IN_CALL) {
      /* AUTO-VOX (works as before for transmission) + noise reduction:
           1. VOX threshold blocks ambient/idle noise.
           2. Noise gate kills small ADC noise within a packet.
           3. 2-sample averaging = low-pass filter, removes high-frequency
              ADC noise without affecting voice (voice is below ~3 kHz). */

      const int32_t VOX_THRESH = 300;   /* original: lets normal voice trigger */
      const int32_t NOISE_GATE = 50;    /* slightly stronger than the working 40 */

      if (half_ready) {
        half_ready = 0;
        int32_t peak = 0;
        for (int i = 0; i < HALF_SIZE; i++) {
          int32_t s = (int32_t)adc_buffer[i] - 2048;
          if (s < 0) s = -s;
          if (s > peak) peak = s;
        }
        if (peak > VOX_THRESH) last_voice_ms = HAL_GetTick();
        bool tx = (HAL_GetTick() - last_voice_ms) < 600;

        if (tx) {
          uint8_t out[HALF_SIZE];
          for (int i = 0; i < HALF_SIZE; i++) {
#if SEND_TEST_TONE
            out[i] = test_phase;
            test_phase += 8;
#else
            /* 2-sample average smoothes high-frequency ADC noise */
            uint16_t a = adc_buffer[i];
            uint16_t b = (i == 0) ? a : adc_buffer[i - 1];
            uint16_t avg = (uint16_t)(((uint32_t)a + b) >> 1);
            int32_t s = (int32_t)avg - 2048;
            if (s > -NOISE_GATE && s < NOISE_GATE) {
              out[i] = 128;                     /* gate small noise to silence */
            } else {
              out[i] = (uint8_t)(avg >> 4);     /* pass voice through */
            }
#endif
          }
          bool ok = tcp_send_audio(out, HALF_SIZE);
          audio_fail_cnt = ok ? 0 : audio_fail_cnt + 1;
        }
      }

      if (full_ready) {
        full_ready = 0;
        int32_t peak = 0;
        for (int i = 0; i < HALF_SIZE; i++) {
          int32_t s = (int32_t)adc_buffer[HALF_SIZE + i] - 2048;
          if (s < 0) s = -s;
          if (s > peak) peak = s;
        }
        if (peak > VOX_THRESH) last_voice_ms = HAL_GetTick();
        bool tx = (HAL_GetTick() - last_voice_ms) < 600;

        if (tx) {
          uint8_t out[HALF_SIZE];
          for (int i = 0; i < HALF_SIZE; i++) {
#if SEND_TEST_TONE
            out[i] = test_phase;
            test_phase += 8;
#else
            uint16_t a = adc_buffer[HALF_SIZE + i];
            uint16_t b = adc_buffer[HALF_SIZE + i - 1];
            uint16_t avg = (uint16_t)(((uint32_t)a + b) >> 1);
            int32_t s = (int32_t)avg - 2048;
            if (s > -NOISE_GATE && s < NOISE_GATE) {
              out[i] = 128;
            } else {
              out[i] = (uint8_t)(avg >> 4);
            }
#endif
          }
          bool ok = tcp_send_audio(out, HALF_SIZE);
          audio_fail_cnt = ok ? 0 : audio_fail_cnt + 1;
        }
      }

      /* Full duplex stresses the modem — be lenient.
         50 consecutive failures (~3 sec) before we give up and reconnect. */
      if (audio_fail_cnt >= 50) {
        audio_fail_cnt = 0;
        lte_registered = 0;
        state = ST_BOOTING;
        lte_bring_up();
        if (lte_registered) state = ST_IDLE;
      }
    }

    /* === 4. Heartbeat — keep TCP socket alive against ngrok/NAT idle timeout.
       Send a PING every 10 sec when idle. The PING also embeds the live raw
       pin levels of PA1 (Call) and PB0 (Answer) so we can see in the relay
       log whether the STM32 is even reading the buttons. === */
    static uint32_t last_ping = 0;
    if (state == ST_IDLE && (HAL_GetTick() - last_ping) >= 10000) {
      last_ping = HAL_GetTick();
      char ping_msg[32];
      int raw_pa1 = (HAL_GPIO_ReadPin(BTN_CALL_GPIO_Port,   BTN_CALL_Pin)   == GPIO_PIN_SET) ? 1 : 0;
      int raw_pb0 = (HAL_GPIO_ReadPin(BTN_ANSWER_GPIO_Port, BTN_ANSWER_Pin) == GPIO_PIN_SET) ? 1 : 0;
      snprintf(ping_msg, sizeof ping_msg, "PING PA1=%d PB0=%d", raw_pa1, raw_pb0);
      if (!tcp_send_line(ping_msg)) {
        /* Socket died — try full reconnect */
        lte_registered = 0;
        state = ST_BOOTING;
        lte_bring_up();
        if (lte_registered) state = ST_IDLE;
      }
    }

    /* Detect modem-reported close (+IPCLOSE URC) — drop to BOOTING and reconnect.
       Previously excluded during ST_IN_CALL to avoid "phantom disconnect", but
       audio bytes are routed to play_buf by the ISR and never reach lte_rx_buf,
       so there is no way for audio content to accidentally contain "+IPCLOSE".
       Re-enabling here is the only way to detect a real socket death mid-call. */
    if (strstr((const char*)lte_rx_buf, "+IPCLOSE")) {
      lte_clear_rx();
      lte_registered = 0;
      state = ST_BOOTING;
      lte_bring_up();
      if (lte_registered) state = ST_IDLE;
    }
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 84;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) half_ready = 1;
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) full_ready = 1;
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM3) {
        /* last_v12 persists between ISR calls for the fade-to-silence logic. */
        static uint16_t last_v12 = 2048;
        uint16_t v12;

#if LOCAL_LOOPBACK
        /* DIAGNOSTIC: play own mic to own DAC (no LTE involved at all). */
        v12 = adc_buffer[dac_play_idx];
        dac_play_idx = (dac_play_idx + 1) % BUF_SIZE;
#else
        if (state == ST_IN_CALL) {
            uint16_t available =
                (play_write_idx + PLAY_BUF_SIZE - play_read_idx) % PLAY_BUF_SIZE;
            if (available > PLAY_THRESH) {
                uint8_t v8 = play_buf[play_read_idx];
                play_read_idx = (play_read_idx + 1) % PLAY_BUF_SIZE;
                v12 = ((uint16_t)v8) << 4;
                last_v12 = v12;
            } else {
                /* Jitter-buffer underrun: fade exponentially toward mid-scale
                   instead of snapping hard to 2048. This eliminates the click
                   that was audible every time the buffer emptied out.
                   Rate: ~7 dB per ms decay toward 2048 at 8 kHz. */
                last_v12 = (uint16_t)(((uint32_t)last_v12 * 253 + 2048 * 3) >> 8);
                v12 = last_v12;
            }
        } else {
            /* Outside a call: silent mid-scale, reset fade state. */
            last_v12 = 2048;
            v12 = 2048;
        }
#endif

        uint8_t pkt[2] = {
            (uint8_t)((v12 >> 8) & 0x0F),
            (uint8_t)(v12 & 0xFF)
        };
        HAL_I2C_Master_Transmit(&hi2c1, MCP4725_ADDR, pkt, 2, 1);
    }
}
/* Clear the LTE RX buffer */
void lte_clear_rx(void) {
    __disable_irq();
    lte_rx_idx = 0;
    lte_rx_buf[0] = 0;
    __enable_irq();
}

/* Wait for a substring to appear in the RX buffer, or until timeout */
bool lte_wait_for(const char* expected, uint32_t timeout_ms) {
    uint32_t start = HAL_GetTick();
    while ((HAL_GetTick() - start) < timeout_ms) {
        if (strstr((const char*)lte_rx_buf, expected) != NULL) {
            return true;
        }
        HAL_Delay(10);
    }
    return false;
}

/* Send an AT command + CRLF, then wait for expected response */
bool lte_send_at(const char* cmd, const char* expected, uint32_t timeout_ms) {
    lte_clear_rx();
    HAL_UART_Transmit(&huart1, (uint8_t*)cmd, strlen(cmd), 1000);
    HAL_UART_Transmit(&huart1, (uint8_t*)"\r\n", 2, 1000);
    return lte_wait_for(expected, timeout_ms);
}

/* Send a relay protocol line over TCP via AT+CIPSEND on link 0.
   Appends CRLF. Returns true if the modem accepted the payload. */
bool tcp_send_line(const char* line) {
    char cmd[64];
    int payload_len = (int)strlen(line) + 2;   /* +2 for \r\n */
    snprintf(cmd, sizeof cmd, "AT+CIPSEND=0,%d", payload_len);
    if (!lte_send_at(cmd, ">", 3000)) return false;
    lte_clear_rx();
    HAL_UART_Transmit(&huart1, (uint8_t*)line, strlen(line), 1000);
    HAL_UART_Transmit(&huart1, (uint8_t*)"\r\n", 2, 1000);
    /* Modem replies "+CIPSEND: 0,<n>,<n>" then "OK" on success */
    return lte_wait_for("OK", 5000);
}

/* Send raw binary audio bytes over TCP.
   Returns false if the modem rejected the data (buffer full, socket dead, ERROR).
   Caller counts consecutive failures and reconnects after a threshold. */
bool tcp_send_audio(const uint8_t* buf, int len) {
    char cmd[32];
    lte_clear_rx();
    int n = snprintf(cmd, sizeof cmd, "AT+CIPSEND=0,%d\r\n", len);
    HAL_UART_Transmit(&huart1, (uint8_t*)cmd, n, 100);

    /* Wait for '>' prompt. 500 ms gives the modem room even when
       its TCP queue is nearly full; ERROR means queue overflow or dead socket. */
    uint32_t start = HAL_GetTick();
    bool got_prompt = false;
    while ((HAL_GetTick() - start) < 500) {
        if (strchr((const char*)lte_rx_buf, '>') != NULL) { got_prompt = true; break; }
        if (strstr((const char*)lte_rx_buf, "ERROR") != NULL) return false;
    }
    if (!got_prompt) return false;

    lte_clear_rx();
    HAL_UART_Transmit(&huart1, (uint8_t*)buf, len, 500);

    /* Wait for OK/DATA ACCEPT (CIPQSEND=1 delivers this quickly, ~5-10 ms).
       This acts as back-pressure: if the modem is full it goes silent or sends
       ERROR, which we catch here instead of pipelining into a dead socket.
       60 ms timeout: safe within the 64 ms ADC half-buffer window. */
    start = HAL_GetTick();
    while ((HAL_GetTick() - start) < 60) {
        if (strstr((const char*)lte_rx_buf, "OK") != NULL)    return true;
        if (strstr((const char*)lte_rx_buf, "ERROR") != NULL) return false;
    }
    /* OK timeout: assume success — persistent timeouts will be caught by
       the consecutive-failure counter in the main loop. */
    return true;
}

/* Pulse PWRKEY low for 1 second to power on the modem */
void modem_power_on_pulse(void) {
    HAL_GPIO_WritePin(MODEM_PWRKEY_GPIO_Port, MODEM_PWRKEY_Pin, GPIO_PIN_RESET);
    HAL_Delay(1000);
    HAL_GPIO_WritePin(MODEM_PWRKEY_GPIO_Port, MODEM_PWRKEY_Pin, GPIO_PIN_SET);
}

/* DEBUG: Blink LED N times to show progress step */
static void debug_blink(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) {
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);  /* ON */
        HAL_Delay(150);
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);    /* OFF */
        HAL_Delay(150);
    }
    HAL_Delay(500);  /* pause between groups */
}

/* LTE bring-up: AT sequence, TCP open, REG.
   ESP32 already did modem power-on, so we skip that. */
void lte_bring_up(void) {
    char cmd[128];

    /* Step 0: indicate boot started — LED solid for 2 seconds */
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
    HAL_Delay(2000);
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);

    /* Start UART RX */
    HAL_UART_Receive_IT(&huart1, (uint8_t*)&lte_rx_byte, 1);

    /* Modem already powered by ESP32 — just give it a moment */
    HAL_Delay(2000);

    if (!lte_send_at("AT", "OK", 2000)) return;
    debug_blink(1);

    if (!lte_send_at("ATE0", "OK", 2000)) return;
    debug_blink(2);

    /* Suppress "RECV FROM:" prefix on incoming TCP data — reduces overhead
       so audio +IPD packets arrive faster during a call. */
    lte_send_at("AT+CIPSRIP=0", "OK", 2000);

    /* Quick-send mode: modem batches TCP ACKs internally instead of waiting
       per packet. Cuts CIPSEND latency and prevents the socket from drowning
       in continuous walkie-talkie traffic. */
    lte_send_at("AT+CIPQSEND=1", "OK", 2000);

    if (!lte_send_at("AT+CPIN?", "READY", 5000)) return;
    debug_blink(3);

    if (!lte_send_at("AT+CSQ", "OK", 2000)) return;
    debug_blink(4);

    snprintf(cmd, sizeof cmd, "AT+CGDCONT=1,\"IP\",\"%s\"", APN);
    if (!lte_send_at(cmd, "OK", 2000)) return;
    debug_blink(5);

    if (!lte_send_at("AT+CGACT=1,1", "OK", 10000)) return;
    debug_blink(6);

    lte_send_at("AT+NETOPEN", "OK", 5000);  /* may already be open */
    debug_blink(7);

    snprintf(cmd, sizeof cmd, "AT+CIPOPEN=0,\"TCP\",\"%s\",%d", NGROK_HOST, NGROK_PORT);
    if (!lte_send_at(cmd, "+CIPOPEN: 0,0", 15000)) return;
    debug_blink(8);

    char reg_payload[32];
    int  reg_len = snprintf(reg_payload, sizeof reg_payload, "REG %s\r\n", PHONE_NUMBER);

    snprintf(cmd, sizeof cmd, "AT+CIPSEND=0,%d", reg_len);
    if (!lte_send_at(cmd, ">", 3000)) return;
    debug_blink(9);

    lte_clear_rx();
    HAL_UART_Transmit(&huart1, (uint8_t*)reg_payload, reg_len, 1000);

    if (lte_wait_for("OK", 5000)) {
        lte_registered = 1;
        debug_blink(10);
    }
}
/* Called every time the LTE modem sends a byte to STM32 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance != USART1) {
        return;
    }
    char b = (char)lte_rx_byte;

    if (ipd_remaining > 0) {
        /* Inside a +IPD payload.
           If we're in a call, treat as audio -> play_buf.
           Otherwise the payload is control data (INC, GO, PEER_HUP, etc.)
           that the state machine needs to see in lte_rx_buf. */
        if (state == ST_IN_CALL) {
            play_buf[play_write_idx] = (uint8_t)b;
            play_write_idx = (play_write_idx + 1) % PLAY_BUF_SIZE;
            /* Latency cap: if the buffer is filling faster than we drain
               (network burst), drop the oldest sample. Better small audio
               loss than half a second of growing delay. */
            uint16_t occ =
                (play_write_idx + PLAY_BUF_SIZE - play_read_idx) % PLAY_BUF_SIZE;
            if (occ > PLAY_MAX_OCC) {
                play_read_idx = (play_read_idx + 1) % PLAY_BUF_SIZE;
            }
        } else {
            if (lte_rx_idx < LTE_RX_BUF_SIZE - 1) {
                lte_rx_buf[lte_rx_idx++] = b;
                lte_rx_buf[lte_rx_idx]   = 0;
            } else {
                lte_rx_idx = 0;
                lte_rx_buf[0] = 0;
            }
        }
        ipd_remaining--;
    } else if (ipd_after_d) {
        /* Just saw "+IPD" — next byte tells us the form */
        ipd_after_d = false;
        if (b == ',') {
            /* "+IPD," form — start collecting digits */
            ipd_collect_len = true;
            ipd_pending_len = 0;
        } else if (b >= '0' && b <= '9') {
            /* "+IPDN..." form (no comma) — first digit is here */
            ipd_collect_len = true;
            ipd_pending_len = (uint16_t)(b - '0');
        }
        /* anything else: abort, the "+IPD" was a false positive */
    } else if (ipd_collect_len) {
        /* Collecting ASCII digits, terminated by \r\n or ':' */
        if (b >= '0' && b <= '9') {
            ipd_pending_len = ipd_pending_len * 10 + (uint16_t)(b - '0');
        } else if (b == '\n' || b == ':') {
            ipd_remaining     = ipd_pending_len;
            ipd_pending_len   = 0;
            ipd_collect_len   = false;
        } else if (b != '\r') {
            ipd_collect_len = false;
            ipd_pending_len = 0;
        }
    } else {
        /* Normal byte: write to lte_rx_buf for AT command parsing */
        if (lte_rx_idx < LTE_RX_BUF_SIZE - 1) {
            lte_rx_buf[lte_rx_idx++] = b;
            lte_rx_buf[lte_rx_idx]   = 0;
        } else {
            lte_rx_idx = 0;
            lte_rx_buf[0] = 0;
        }
        /* Update rolling 5-byte tail and check for "+IPD" (4 chars only) */
        ipd_tail[0] = ipd_tail[1];
        ipd_tail[1] = ipd_tail[2];
        ipd_tail[2] = ipd_tail[3];
        ipd_tail[3] = ipd_tail[4];
        ipd_tail[4] = b;
        if (ipd_tail[1] == '+' && ipd_tail[2] == 'I' &&
            ipd_tail[3] == 'P' && ipd_tail[4] == 'D') {
            /* Strip "+IPD" from lte_rx_buf */
            if (lte_rx_idx >= 4) {
                lte_rx_idx -= 4;
                lte_rx_buf[lte_rx_idx] = 0;
            }
            ipd_after_d = true;
        }
    }

    HAL_UART_Receive_IT(&huart1, (uint8_t*)&lte_rx_byte, 1);
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */